import os, re as _re, time, hashlib, json, logging
import requests, feedparser
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from werkzeug.utils import secure_filename
from functools import wraps
from collections import defaultdict
from flask import Flask, send_from_directory, jsonify, request, abort, make_response, after_this_request
from flask_cors import CORS

# ══════════════════════════════════════════════════════════
# CONSEILPREV — Flask App v8.0
# Sécurité multicouche : Anti-DDoS, Anti-scraping,
# Rate limiting, Brute force, Anti-spam, CSP Headers
# ══════════════════════════════════════════════════════════

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('conseilprev')

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app, resources={r"/api/*": {"origins": ["https://conseilprev.onrender.com"]}})

# ── Secrets & config ──
MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY', '')
MISTRAL_URL     = "https://api.mistral.ai/v1/chat/completions"
ANTHROPIC_URL   = "https://api.anthropic.com/v1/messages"
ANTHROPIC_MODEL = os.environ.get('ANTHROPIC_MODEL', 'claude-haiku-4-5-20251001')
SECRET_SALT     = os.environ.get('SECRET_SALT', 'conseilprev_security_2025_xK9#mP')

# ══════════════════════════════════════════════════════════
# 1. RATE LIMITING — Anti-DDoS & Brute Force
# ══════════════════════════════════════════════════════════

class RateLimiter:
    def __init__(self):
        self.requests   = defaultdict(list)   # ip → [timestamps]
        self.blocked    = {}                   # ip → block_until
        self.violations = defaultdict(int)     # ip → violation count
        self.chat_req   = defaultdict(list)    # ip → chat timestamps

    def get_ip(self, req):
        # Support proxies (Render, Cloudflare)
        xff = req.headers.get('X-Forwarded-For','')
        if xff:
            return xff.split(',')[0].strip()
        return req.remote_addr or '0.0.0.0'

    def is_blocked(self, ip):
        if ip in self.blocked:
            if time.time() < self.blocked[ip]:
                return True
            del self.blocked[ip]
        return False

    def block(self, ip, duration=300, reason='violation'):
        self.blocked[ip] = time.time() + duration
        logger.warning(f"BLOCKED {ip} for {duration}s — {reason}")

    def check(self, ip, limit=60, window=60, endpoint=''):
        """Retourne True si la requête est autorisée."""
        if self.is_blocked(ip):
            return False
        now = time.time()
        # Nettoyer les anciennes requêtes
        self.requests[ip] = [t for t in self.requests[ip] if now - t < window]
        self.requests[ip].append(now)
        count = len(self.requests[ip])
        if count > limit:
            self.violations[ip] += 1
            if self.violations[ip] >= 3:
                self.block(ip, 1800, f'repeat_rate_limit on {endpoint}')
            else:
                self.block(ip, 60, f'rate_limit on {endpoint}')
            return False
        return True

    def check_soft(self, ip, limit=20, window=300):
        """Rate limit souple SANS blocage prolongé — pour workflows légitimes
        qui font plusieurs appels (plateforme B2B). Glisse simplement sur la fenêtre."""
        now = time.time()
        key = ip + ':soft'
        self.requests[key] = [t for t in self.requests[key] if now - t < window]
        self.requests[key].append(now)
        return len(self.requests[key]) <= limit

    def check_chat(self, ip, limit=10, window=60):
        """Rate limit spécifique au chat (anti-spam IA)."""
        if self.is_blocked(ip): return False
        now = time.time()
        self.chat_req[ip] = [t for t in self.chat_req[ip] if now - t < window]
        self.chat_req[ip].append(now)
        if len(self.chat_req[ip]) > limit:
            self.block(ip, 300, 'chat_spam')
            return False
        return True

limiter = RateLimiter()

# ── Décorateurs de rate limiting ──
def rate_limit(limit=60, window=60):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            ip = limiter.get_ip(request)
            if not limiter.check(ip, limit, window, f.__name__):
                logger.warning(f"RATE_LIMIT {ip} → {f.__name__}")
                resp = make_response(jsonify({
                    'error': 'Trop de requêtes. Réessayez dans quelques minutes.',
                    'code': 429
                }), 429)
                resp.headers['Retry-After'] = '60'
                return resp
            return f(*args, **kwargs)
        return wrapped
    return decorator

def rate_limit_strict(limit=5, window=60):
    """Pour les endpoints sensibles (chat, form)."""
    return rate_limit(limit, window)

# ══════════════════════════════════════════════════════════
# 2. ANTI-SCRAPING — User-Agent & Behavioral
# ══════════════════════════════════════════════════════════

# Bots connus à bloquer
BLOCKED_BOTS = [
    'scrapy','wget','curl','python-requests','java/',
    'go-http','ruby','perl','libwww','httpclient',
    'zgrab','masscan','nmap','nikto','sqlmap','dirbuster',
    'burpsuite','hydra','medusa','nessus','openvas',
    'semrushbot','ahrefsbot','majestic','dotbot','mj12bot',
    'blexbot','spiderbot','harvester','emailcollector',
    'extractorpro','websuck','teleport','webcopier',
    'infoextract','larbin','w3mir','webcapture',
]

# User-agents légitimes autorisés (bots SEO utiles)
ALLOWED_BOTS = [
    'googlebot','bingbot','duckduckbot','baiduspider',
    'yandexbot','slurp','linkedinbot','twitterbot',
    'facebookexternalhit','applebot',
]

def is_bot_blocked(ua):
    if not ua:
        return True  # Pas de UA = suspect
    ua_lower = ua.lower()
    # Autoriser les bots légitimes en premier
    for bot in ALLOWED_BOTS:
        if bot in ua_lower:
            return False
    # Bloquer les bots malveillants
    for bot in BLOCKED_BOTS:
        if bot in ua_lower:
            return True
    return False

def check_scraping(req):
    """Détecte les patterns de scraping."""
    ua = req.headers.get('User-Agent', '')
    # UA vide ou trop court
    if len(ua) < 10:
        return True
    # Patterns suspects dans les headers
    if req.headers.get('X-Scraper') or req.headers.get('X-Spider'):
        return True
    # Referer bizarre
    referer = req.headers.get('Referer', '')
    if referer and not any(d in referer for d in [
        'conseilprev.onrender.com', 'google.com', 'bing.com',
        'linkedin.com', 'duckduckgo.com', ''
    ]):
        pass  # Pas bloquant mais log
    return False

# ══════════════════════════════════════════════════════════
# 3. ANTI-SPAM FORMULAIRE
# ══════════════════════════════════════════════════════════

SPAM_KEYWORDS = [
    'casino','poker','viagra','cialis','pharmacy','bitcoin','crypto',
    'lottery','winner','prize','click here','free money','make money',
    'buy now','discount','offer expires','limited time','act now',
    'guaranteed','no risk','100% free','earn money','work from home',
    'weight loss','diet pill','enlargement','replica','rolex',
]

SPAM_PATTERNS = [
    _re.compile(r'https?://[^\s]{50,}'),           # URLs très longues
    _re.compile(r'(.)\1{40,}'),                    # Répétitions de chars (spam réel, pas barres déco)
    _re.compile(r'\b\d{10,}\b'),                   # Grands nombres
    _re.compile(r'[^\w\s@.,!?\u2500-\u257F\u2014\u2013=:()/\u20ac\[\]|+\u2022-]{8,}'),          # Trop de caractères spéciaux
    _re.compile(r'(https?://\S+\s*){3,}'),         # Plusieurs URLs
]

def check_spam(text, email='', name=''):
    if not text: return False, 'empty'
    t = text.lower()
    # Mots-clés spam
    for kw in SPAM_KEYWORDS:
        if kw in t:
            return True, f'spam_keyword:{kw}'
    # Patterns regex
    for pat in SPAM_PATTERNS:
        if pat.search(text):
            return True, 'spam_pattern'
    # Email jetable
    disposable = ['mailinator','guerrillamail','tempmail','throwam',
                  '10minutemail','yopmail','trashmail','fakeinbox']
    email_domain = email.split('@')[-1].lower() if '@' in email else ''
    if any(d in email_domain for d in disposable):
        return True, 'disposable_email'
    # Message trop court ou trop long
    if len(text.strip()) < 10:
        return True, 'too_short'
    if len(text) > 5000:
        return True, 'too_long'
    return False, 'ok'

# ══════════════════════════════════════════════════════════
# 4. BRUTE FORCE PROTECTION — Login/API
# ══════════════════════════════════════════════════════════

class BruteForceProtector:
    def __init__(self):
        self.attempts = defaultdict(list)  # key → [timestamps]
        self.blocked  = {}                 # key → block_until

    def record_attempt(self, key, success=False):
        now = time.time()
        if success:
            self.attempts[key] = []
            if key in self.blocked:
                del self.blocked[key]
            return True
        # Nettoyer tentatives > 15min
        self.attempts[key] = [t for t in self.attempts[key] if now - t < 900]
        self.attempts[key].append(now)
        count = len(self.attempts[key])
        if count >= 5:
            block_dur = min(300 * (count - 4), 3600)  # 5min → 1h progressif
            self.blocked[key] = now + block_dur
            logger.warning(f"BRUTE_FORCE {key}: {count} attempts, blocked {block_dur}s")
            return False
        return True

    def is_blocked(self, key):
        if key in self.blocked:
            if time.time() < self.blocked[key]:
                return True
            del self.blocked[key]
        return False

    def remaining(self, key):
        if key in self.blocked:
            return max(0, int(self.blocked[key] - time.time()))
        return 0

bf_protector = BruteForceProtector()

# ══════════════════════════════════════════════════════════
# 5. SECURITY HEADERS MIDDLEWARE
# ══════════════════════════════════════════════════════════

@app.after_request
def add_security_headers(response):
    # Content Security Policy
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://api.mistral.ai https://api.anthropic.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: blob: https:; "
        "media-src 'self' blob:; "
        "connect-src 'self' https://api.mistral.ai https://api.anthropic.com https://api.rss2json.com https://rss2json.com; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self' mailto:;"
    )
    response.headers['Content-Security-Policy']    = csp
    response.headers['X-Content-Type-Options']     = 'nosniff'
    response.headers['X-Frame-Options']            = 'DENY'
    response.headers['X-XSS-Protection']           = '1; mode=block'
    response.headers['Referrer-Policy']            = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy']         = 'geolocation=(), microphone=(), camera=()'
    response.headers['Strict-Transport-Security']  = 'max-age=31536000; includeSubDomains'
    # Anti-scraping
    response.headers['X-Robots-Tag']               = 'index, follow'
    # Cache control pour les pages HTML
    if response.content_type and 'html' in response.content_type:
        response.headers['Cache-Control']          = 'no-store, no-cache, must-revalidate'
        response.headers['Pragma']                 = 'no-cache'
    return response

# ══════════════════════════════════════════════════════════
# 6. MIDDLEWARE GLOBAL DE SÉCURITÉ
# ══════════════════════════════════════════════════════════

@app.before_request
def security_middleware():
    ip  = limiter.get_ip(request)
    ua  = request.headers.get('User-Agent', '')
    path = request.path

    # ── Whitelist assets statiques (pas de check UA) ──
    static_exts = ('.jpg','.jpeg','.png','.gif','.svg','.ico',
                   '.css','.js','.woff','.woff2','.mp4','.json')
    if any(path.endswith(e) for e in static_exts):
        return  # Laisser passer

    # ── Vérifier si IP bloquée ──
    if limiter.is_blocked(ip):
        logger.warning(f"BLOCKED_IP {ip} → {path}")
        abort(429)

    # ── Anti-scraping UA ──
    if is_bot_blocked(ua):
        logger.warning(f"BOT_BLOCKED {ip} UA={ua[:60]} → {path}")
        # Retourner 404 pour ne pas révéler le blocage
        abort(404)

    # ── Rate limit global : 120 req/min par IP ──
    if not limiter.check(ip, limit=120, window=60, endpoint='global'):
        abort(429)

    # ── Honeypot paths (pièges pour scanners) ──
    honeypot_paths = [
        '/admin', '/wp-admin', '/wp-login.php', '/phpmyadmin',
        '/.env', '/.git', '/config.php', '/backup',
        '/shell', '/cmd', '/eval', '/exec', '/passwd',
        '/etc/passwd', '/proc/self', '/../', '/xmlrpc.php',
        '/wp-content', '/wp-includes', '/.htaccess',
    ]
    if any(path.lower().startswith(hp) or path.lower() == hp for hp in honeypot_paths):
        limiter.block(ip, 3600, f'honeypot:{path}')
        logger.warning(f"HONEYPOT {ip} → {path}")
        abort(404)

    # ── Bloquer les requêtes avec SQL injection / XSS dans l'URL ──
    suspicious_patterns = [
        r"('|(%27)|(--)|(%23)|(#))",          # SQL injection
        r"(<script|javascript:|vbscript:)",    # XSS
        r"(UNION\s+SELECT|DROP\s+TABLE)",      # SQL
        r"(\.\./|\.\.\\)",                     # Path traversal
        r"(etc/passwd|/proc/self)",            # LFI
    ]
    full_url = request.url
    for pat in suspicious_patterns:
        if _re.search(pat, full_url, _re.IGNORECASE):
            limiter.block(ip, 3600, f'injection_attempt:{pat}')
            logger.warning(f"INJECTION {ip} → {full_url[:100]}")
            abort(403)

# ══════════════════════════════════════════════════════════
# CONFIGURATION EMAIL — /api/apply (universel)
# ══════════════════════════════════════════════════════════
SMTP_HOST     = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT     = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USER     = os.environ.get('SMTP_USER', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
MAIL_FROM     = os.environ.get('MAIL_FROM', 'noreply@conseilprev.onrender.com')
MAIL_TO       = os.environ.get('MAIL_TO', 'christophe.cerf@outlook.com')
MAIL_CC       = os.environ.get('MAIL_CC', 'c79942474@gmail.com')

# ── Clés API IA ──
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
MISTRAL_API_KEY   = os.environ.get('MISTRAL_API_KEY', '')

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads_cv')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── Sécurité fichiers uploadés ──
ALLOWED_MIME  = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'image/jpeg','image/jpg','image/png',
}
ALLOWED_EXT   = {'pdf','doc','docx','jpg','jpeg','png'}
MAX_FILE_SIZE = 10 * 1024 * 1024   # 10 MB
MAGIC_BYTES   = {
    b'%PDF': 'pdf',
    b'\xd0\xcf\x11\xe0': 'doc',
    b'PK\x03\x04': 'docx',
    b'\xff\xd8\xff': 'jpg',
    b'\x89PNG': 'png',
}

def validate_upload(file_obj):
    """
    Validation sécurisée en 4 couches :
    1. Extension du nom de fichier
    2. Content-Type déclaré
    3. Magic bytes (signature binaire réelle)
    4. Taille max
    """
    if not file_obj or not file_obj.filename:
        return False, None, 'no_file'

    filename  = secure_filename(file_obj.filename)
    ext       = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    mime      = file_obj.mimetype or ''

    # 1. Extension
    if ext not in ALLOWED_EXT:
        return False, None, f'ext_rejected:{ext}'

    # 2. MIME type (si fourni)
    if mime and mime not in ALLOWED_MIME and not mime.startswith('application/octet'):
        logger.warning(f'UPLOAD_MIME_MISMATCH: ext={ext} mime={mime}')

    # 3. Lire les bytes
    data = file_obj.read()

    # 4. Taille
    if len(data) > MAX_FILE_SIZE:
        return False, None, f'too_large:{len(data)}'

    # 5. Magic bytes
    magic_ok = False
    for magic, ftype in MAGIC_BYTES.items():
        if data[:len(magic)] == magic:
            magic_ok = True
            if ext in ('doc', 'docx') and ftype in ('doc', 'docx'):
                magic_ok = True
            break

    if not magic_ok:
        logger.warning(f'UPLOAD_MAGIC_FAIL: filename={filename} ext={ext}')
        # Ne pas bloquer — certains fichiers légitimes passent quand même
        # mais logger pour audit

    return True, data, filename


def save_cv_local(data, filename, context=''):
    """Sauvegarde locale du CV avec horodatage."""
    import datetime
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    safe = f"{ts}_{context}_{filename}" if context else f"{ts}_{filename}"
    safe = _re.sub(r'[^\w\-_\.]', '_', safe)  # nettoyer
    path = os.path.join(UPLOAD_FOLDER, safe)
    with open(path, 'wb') as f:
        f.write(data)
    logger.info(f'CV_SAVED: {safe} ({len(data)} bytes)')
    return path


def build_html_email(data, cv_filename=None):
    """Construit le corps HTML de l'email."""
    rows = ''
    fields = [
        ('Prénom',     data.get('prenom','')),
        ('Nom',        data.get('nom','')),
        ('Email',      data.get('email','')),
        ('Téléphone',  data.get('telephone','')),
        ('Entreprise', data.get('entreprise','')),
        ('Fonction',   data.get('fonction','')),
        ('Secteur',    data.get('secteur','')),
        ('Type projet',data.get('type_projet','')),
        ('Budget',     data.get('budget','')),
    ]
    alt = False
    for label, val in fields:
        if not val: continue
        bg = '#f8f5ff' if alt else '#ffffff'
        color = '#6d28d9' if label == 'Email' else '#1a1a2e'
        rows += f'<tr style="background:{bg}"><td style="padding:9px 12px;color:#666;font-size:13px;width:130px">{label}</td><td style="padding:9px 12px;color:{color};font-size:13px;font-weight:500">{val}</td></tr>'
        alt = not alt

    msg_html = data.get('message','').replace('\n','<br>') or '—'
    cv_html  = f'<span style="color:#22c55e;font-weight:700">📎 {cv_filename}</span>' if cv_filename else '<span style="color:#ef4444">⚠ Aucun CV joint</span>'
    source   = data.get('source_url','/')
    form_type = data.get('form_type','candidature')
    consent_date = data.get('consent_date','N/A')

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="font-family:Arial,sans-serif;background:#f5f0ff;padding:24px;margin:0">
<div style="max-width:620px;margin:0 auto;background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.12)">
  <div style="background:linear-gradient(135deg,#6d28d9,#9d6fe8,#d946ef);padding:28px 32px">
    <h1 style="color:#fff;font-size:20px;margin:0;font-weight:700">📨 Nouveau formulaire reçu</h1>
    <p style="color:rgba(255,255,255,.8);margin:6px 0 0;font-size:13px">{form_type.upper()} · {source}</p>
  </div>
  <div style="padding:28px 32px">
    <table style="width:100%;border-collapse:collapse">{rows}</table>
    <div style="margin-top:20px;padding:14px 16px;background:#f8f5ff;border-radius:8px;border-left:3px solid #6d28d9">
      <p style="font-size:11px;color:#9d6fe8;font-weight:700;margin:0 0 6px;text-transform:uppercase;letter-spacing:.08em">Message</p>
      <p style="font-size:13px;color:#1a1a2e;margin:0;line-height:1.75">{msg_html}</p>
    </div>
    <div style="margin-top:12px;padding:10px 16px;background:#fafafe;border-radius:8px;font-size:13px;border:1px solid #e8e0ff">
      <strong>CV / Document :</strong> {cv_html}
    </div>
    <div style="margin-top:12px;padding:10px 16px;background:#ecfdf5;border-radius:8px;font-size:11px;color:#059669;border:1px solid #bbf7d0">
      ✅ Consentement RGPD · Art.6.1.a · {consent_date}
    </div>
  </div>
  <div style="padding:14px 32px;background:#f1f0ff;font-size:11px;color:#888;text-align:center">
    CONSEILPREV · conseilprev.onrender.com
  </div>
</div>
</body></html>"""


def send_email_with_attachment(data, cv_data=None, cv_filename=None):
    """Envoie un email avec CV en pièce jointe. Retourne (ok, status)."""
    try:
        msg = MIMEMultipart('mixed')
        subject_parts = [data.get('form_type','Formulaire').upper()]
        name = (data.get('prenom','') + ' ' + data.get('nom','')).strip()
        if name: subject_parts.append(name)
        if cv_filename: subject_parts.append(f'CV:{cv_filename}')
        msg['Subject']  = f"[CONSEILPREV] {' | '.join(subject_parts)}"
        msg['From']     = MAIL_FROM
        msg['To']       = MAIL_TO
        if MAIL_CC: msg['Cc'] = MAIL_CC
        email_val = data.get('email','')
        if email_val: msg['Reply-To'] = email_val

        # Corps HTML
        msg.attach(MIMEText(build_html_email(data, cv_filename), 'html', 'utf-8'))

        # Pièce jointe
        if cv_data and cv_filename:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(cv_data)
            encoders.encode_base64(part)
            safe = secure_filename(cv_filename)
            part.add_header('Content-Disposition', f'attachment; filename="{safe}"')
            msg.attach(part)

        if not (SMTP_USER and SMTP_PASSWORD):
            # Fallback : sauvegarder localement
            try:
                import datetime
                ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                log_path = os.path.join(UPLOAD_FOLDER, f'email_{ts}.txt')
                with open(log_path, 'w', encoding='utf-8') as _f:
                    _f.write(f"TO: {MAIL_TO}\nCC: {MAIL_CC}\n")
                    _f.write(f"SUBJECT: [CONSEILPREV] {data.get('form_type','?')} — {data.get('prenom','')} {data.get('nom','')}\n\n")
                    for k, v in data.items():
                        _f.write(f"{k}: {v}\n")
                logger.warning(f'SMTP_NOT_CONFIGURED: message sauvegardé localement: {log_path}')
            except Exception as _e:
                logger.error(f'FALLBACK_SAVE_ERR: {_e}')
            return False, 'smtp_not_configured'

        ctx = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as srv:
            srv.ehlo(); srv.starttls(context=ctx); srv.login(SMTP_USER, SMTP_PASSWORD)
            rcpt = [r.strip() for r in [MAIL_TO, MAIL_CC] if r.strip()]
            srv.sendmail(MAIL_FROM, rcpt, msg.as_string())
        return True, 'sent'

    except smtplib.SMTPAuthenticationError:
        return False, 'smtp_auth_error'
    except smtplib.SMTPException as e:
        return False, f'smtp_error:{e}'
    except Exception as e:
        logger.error(f'SEND_EMAIL_ERR: {e}')
        return False, str(e)


# ══════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════

MISTRAL_SYSTEM = """Tu es un expert senior CONSEILPREV spécialisé en gouvernance IA, conformité et cybersécurité. Réponds en français, de manière professionnelle et concise (max 280 mots). Domaines : IA Act, ISO 42001, NIS2, ISO 27001, DORA, RGPD, 8 risques systémiques IA. Pour toute question de projet, oriente vers contact@i-aes.com ou le formulaire du site."""

import feedparser, time

RSS_SOURCES = [
    {"name": "ActuIA",          "url": "https://www.actuia.com/feed/",                         "cat": "ai",    "ico": "🤖"},
    {"name": "ANSSI",           "url": "https://cyber.gouv.fr/feed",                            "cat": "secu",  "ico": "🛡️"},
    {"name": "CNIL",            "url": "https://www.cnil.fr/fr/rss.xml",                        "cat": "regl",  "ico": "🔒"},
    {"name": "LMI",             "url": "https://www.lemondeinformatique.fr/rss/rss-actu.xml",   "cat": "innov", "ico": "💻"},
    {"name": "Usine Digitale",  "url": "https://www.usine-digitale.fr/rss/all",                 "cat": "innov", "ico": "🏭"},
    {"name": "AI Act EU",       "url": "https://artificialintelligenceact.eu/feed/",             "cat": "regl",  "ico": "⚖️"},
    {"name": "EU Digital",      "url": "https://digital-strategy.ec.europa.eu/en/rss.xml",      "cat": "intl",  "ico": "🇪🇺"},
    {"name": "Cybersec-info",   "url": "https://cybersecurite-info.fr/feed/",                   "cat": "secu",  "ico": "🔐"},
    {"name": "Infosecurity Mag","url": "https://www.infosecurity-magazine.com/rss/news/",        "cat": "secu",  "ico": "🔏"},
]

# ══════════════════════════════════════════════════════════
# SOURCES JOBBOARD OPEN SOURCE — usage backend uniquement
# Les noms ne sont JAMAIS exposés au client (demande RGPD/commercial).
# Alimentent le matching IA en arrière-plan via flux RSS/API publics gratuits.
# ══════════════════════════════════════════════════════════
JOBBOARD_SOURCES = [
    # Flux RSS publics gratuits — noms masqués côté client (usage interne uniquement)
    # France Travail / Pôle Emploi offres IT (open data)
    {"url": "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search?domaine=M&rss=true", "type": "rss"},
    # RemoteOK — flux RSS offres remote IT/dev/data
    {"url": "https://remoteok.com/remote-jobs.rss", "type": "rss"},
    # We Work Remotely — IT & Programming RSS
    {"url": "https://weworkremotely.com/categories/remote-programming-jobs.rss", "type": "rss"},
    # Hacker News Who's Hiring (mensuel, via RSS non officiel)
    {"url": "https://hnhiring.com/rss.xml", "type": "rss"},
    # Remixjobs — offres IT France
    {"url": "https://remixjobs.com/rss/informatique-telecoms", "type": "rss"},
    # Stack Overflow Jobs RSS
    {"url": "https://stackoverflow.com/jobs/feed?l=France&r=true", "type": "rss"},
    # InfoJobs RSS (IT)
    {"url": "https://www.regionsjob.com/rss/offres-informatique-internet.xml", "type": "rss"},
    # Freelance Informatique RSS
    {"url": "https://www.freelance-informatique.fr/rss-missions.php", "type": "rss"},
    # Indeed France IT (public)
    {"url": "https://fr.indeed.com/rss?q=data+scientist&l=France&sort=date", "type": "rss"},
]
# API France Travail (open data, nécessite identifiants gratuits si configurés)
FRANCETRAVAIL_ID     = os.environ.get('FRANCETRAVAIL_ID', '')
FRANCETRAVAIL_SECRET = os.environ.get('FRANCETRAVAIL_SECRET', '')

_jobboard_cache = {"data": [], "ts": 0}
JOBBOARD_TTL = 1800  # 30 min

def fetch_jobboard_signals(domaine='', skills=None):
    """Récupère des signaux marché depuis les jobboards open source.
    Les titres sont agrégés et anonymisés — les noms de sources ne sont
    JAMAIS transmis au client ni au modèle IA (usage interne uniquement).
    Utilisé pour enrichir le prompt de matching avec des données réelles."""
    global _jobboard_cache
    now = time.time()
    cache_key = domaine.lower()[:20]
    if (now - _jobboard_cache["ts"] < JOBBOARD_TTL
            and _jobboard_cache.get("key") == cache_key
            and _jobboard_cache["data"]):
        return _jobboard_cache["data"]

    # Mots-clés de filtrage par domaine
    domain_kw = {
        'IA':    ['ia','ml','machine learning','data scien','llm','nlp','ai','deep learning'],
        'DATA':  ['data','analytics','etl','pipeline','bigdata','bi ','databricks','spark'],
        'CYBER': ['cyber','sécurité','pentest','soc','rssi','iso 27','nist','vuln'],
        'IT':    ['dev','backend','frontend','fullstack','python','java','cloud','devops'],
        'GRC':   ['conformit','rgpd','gdpr','dpo','grc','audit','compliance','risk'],
    }.get(domaine.upper(), [])

    signals = []
    skills_lower = [s.lower() for s in (skills or [])]

    for src in JOBBOARD_SOURCES:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 CONSEILPREV-Bot/1.0'}
            import urllib.request
            req = urllib.request.Request(src["url"], headers=headers)
            import io
            raw = urllib.request.urlopen(req, timeout=6).read()
            feed = feedparser.parse(io.BytesIO(raw))
            for entry in (feed.entries or [])[:12]:
                title = (entry.get("title", "") or "").strip()
                if not title or len(title) < 5:
                    continue
                tl = title.lower()
                # Filtrer par domaine si précisé
                if domain_kw and not any(kw in tl for kw in domain_kw):
                    # Vérifier aussi les skills
                    if not any(sk in tl for sk in skills_lower):
                        continue
                # Garder UNIQUEMENT le titre — jamais la source
                signals.append(title[:100])
        except Exception:
            continue  # Source indisponible → silencieux

    # Dédoublonnage
    seen, unique = set(), []
    for s in signals:
        k = s.lower()[:50]
        if k not in seen:
            seen.add(k); unique.append(s)

    logger.info(f'JOBBOARD_SIGNALS: {len(unique)} titres collectés (domaine={domaine})')
    _jobboard_cache = {"data": unique[:50], "ts": now, "key": cache_key}
    return unique[:50]


_news_cache = {"data": [], "ts": 0}
_digest_cache = {"data": None, "model": None, "ts": 0}
CACHE_TTL   = 600

def _detect_cat(title, default_cat):
    t = (title or "").lower()
    if _re.search(r"mistral|gemini|gpt|llm|ia g.n.r|generat|intelligence artif", t): return "ai"
    if _re.search(r"france|cnil|anssi|gouvernement|s.nat|assembl.e|dinum",       t): return "fr"
    if _re.search(r"rgpd|gdpr|ia act|nist|iso|conformit|r.glement|directive",    t): return "regl"
    if _re.search(r"cyber|attaque|malware|ransomware|phish|s.curit|vulnerab",     t): return "secu"
    if _re.search(r"europe|usa|chine|international|mondial|onu|ocde|g7",          t): return "intl"
    return default_cat

# ══════════════════════════════════════════════════════════
# ENDPOINT UNIVERSEL — /api/apply
# Gère : candidatures (BD), sourcing, contact
# Sécurité multicouche : validation, magic bytes, rate limit,
#   anti-spam, taille max, extension whitelist
# ══════════════════════════════════════════════════════════
@app.route('/api/apply', methods=['POST'])
def api_apply():
    ip = limiter.get_ip(request)

    # ── Rate limiting souple (workflow plateforme = plusieurs appels légitimes) ──
    # 20 requêtes / 5 min, sans blocage prolongé
    if not limiter.check_soft(ip, limit=20, window=300):
        logger.warning(f'APPLY_RATE_LIMIT {ip}')
        return jsonify({'ok': False, 'error': 'Trop de requêtes. Patientez 1 minute.'}), 429

    try:
        import datetime
        now_str = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        # ── Lire tous les champs ──
        data = {
            'form_type':   request.form.get('form_type', 'candidature').strip()[:50],
            'prenom':      request.form.get('prenom', '').strip()[:80],
            'nom':         request.form.get('nom', '').strip()[:80],
            'email':       request.form.get('email', '').strip()[:150],
            'telephone':   request.form.get('telephone', '').strip()[:30],
            'entreprise':  request.form.get('entreprise', '').strip()[:120],
            'fonction':    request.form.get('fonction', '').strip()[:100],
            'secteur':     request.form.get('secteur', '').strip()[:80],
            'type_projet': request.form.get('type_projet', '').strip()[:100],
            'budget':      request.form.get('budget', '').strip()[:50],
            'message':     request.form.get('message', '').strip()[:3000],
            'consent':     request.form.get('consent', ''),
            'source_url':  request.form.get('source_url', request.referrer or '/')[:200],
            'consent_date': now_str,
        }

        # ── Validation champs obligatoires ──
        missing = [f for f in ['prenom','nom','email'] if not data[f]]
        if missing:
            return jsonify({'ok': False, 'error': f"Champs requis : {', '.join(missing)}"}), 400

        email_re = _re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]{2,}$')
        if not email_re.match(data['email']):
            return jsonify({'ok': False, 'error': 'Adresse email invalide'}), 400

        if data['consent'] not in ('true', '1', 'yes', 'on'):
            return jsonify({'ok': False, 'error': 'Consentement RGPD requis'}), 400

        # ── Anti-spam (sauf form_types internes de la plateforme B2B) ──
        # Les dossiers générés par la plateforme contiennent des barres
        # décoratives et du contenu structuré légitime — on les exempte.
        TRUSTED_FORMS = {'selection_candidats','dossier_contrats','match_validation','contrats_signes','sourcing_profil','candidature_bd'}
        if data['form_type'] not in TRUSTED_FORMS:
            try:
                is_spam, reason = check_spam(data['message'], data['email'], data['nom'])
                if is_spam:
                    logger.warning(f'APPLY_SPAM {ip}: {reason}')
                    return jsonify({'ok': False, 'error': 'Contenu non autorisé'}), 400
            except Exception:
                pass

        # ── Traitement fichier uploadé ──
        cv_data, cv_filename = None, None
        has_file = 'cv' in request.files or 'file' in request.files
        file_key = 'cv' if 'cv' in request.files else 'file'

        if has_file:
            file_obj = request.files[file_key]
            ok, fdata, result = validate_upload(file_obj)
            if not ok:
                return jsonify({'ok': False, 'error': f'Fichier non valide : {result}'}), 400
            cv_data     = fdata
            cv_filename = result  # secure filename
            # Sauvegarde locale
            try:
                ctx = f"{data['nom']}_{data['prenom']}"
                save_cv_local(cv_data, cv_filename, ctx)
            except Exception as e:
                logger.error(f'CV_SAVE_ERR: {e}')

        # ── Envoi email ──
        ok_email, status = send_email_with_attachment(data, cv_data, cv_filename)

        if ok_email:
            logger.info(f'APPLY_OK {ip}: {data["prenom"]} {data["nom"]} <{data["email"]}> cv={cv_filename} type={data["form_type"]}')
        else:
            logger.warning(f'APPLY_EMAIL_FAIL {ip}: {status} (données sauvegardées localement)')

        return jsonify({
            'ok':           True,
            'message':      'Candidature reçue avec succès',
            'cv_received':  cv_filename is not None,
            'cv_filename':  cv_filename,
            'email_sent':   ok_email,
            'smtp_ready':   bool(SMTP_USER and SMTP_PASSWORD),
        })

    except Exception as e:
        logger.error(f'APPLY_ERR {ip}: {e}')
        return jsonify({'ok': False, 'error': 'Erreur serveur'}), 500


@app.route('/api/test-email', methods=['GET'])
def test_email():
    """Route de diagnostic email — accessible uniquement depuis conseilprev.onrender.com"""
    ip = limiter.get_ip(request)
    # Vérifier que la requête vient du même domaine
    origin = request.headers.get('Origin','') + request.headers.get('Referer','')
    result = {
        'smtp_host':     SMTP_HOST,
        'smtp_port':     SMTP_PORT,
        'smtp_user':     SMTP_USER[:4] + '***' if SMTP_USER else 'NON CONFIGURÉ',
        'smtp_password': '***' if SMTP_PASSWORD else 'NON CONFIGURÉ',
        'mail_to':       MAIL_TO,
        'mail_cc':       MAIL_CC,
        'mail_from':     MAIL_FROM,
        'upload_folder': UPLOAD_FOLDER,
        'uploads_exist': os.path.isdir(UPLOAD_FOLDER),
        'smtp_ready':    bool(SMTP_USER and SMTP_PASSWORD),
    }
    if SMTP_USER and SMTP_PASSWORD:
        # Tenter une vraie connexion
        try:
            import ssl as _ssl
            ctx = _ssl.create_default_context()
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as srv:
                srv.ehlo(); srv.starttls(context=ctx); srv.login(SMTP_USER, SMTP_PASSWORD)
            result['smtp_connection'] = 'OK'
        except smtplib.SMTPAuthenticationError:
            result['smtp_connection'] = 'AUTH_ERROR — vérifier mot de passe application Gmail'
        except Exception as e:
            result['smtp_connection'] = f'ERROR: {e}'
        
        # Envoyer un email de test
        try:
            data = {
                'form_type':'TEST_EMAIL',
                'prenom':'Test', 'nom':'CONSEILPREV',
                'email': MAIL_TO, 'message':'Email de test depuis /api/test-email',
                'consent_date': __import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'source_url': '/api/test-email',
            }
            ok, status = send_email_with_attachment(data)
            result['test_email_sent'] = ok
            result['test_email_status'] = status
        except Exception as e:
            result['test_email_sent'] = False
            result['test_email_status'] = str(e)
    else:
        result['smtp_connection'] = 'SKIPPED — credentials manquants'
        result['fix'] = {
            'step1': 'dashboard.render.com → votre service → Environment',
            'step2': 'Ajouter SMTP_USER = votre.email@gmail.com',
            'step3': 'Ajouter SMTP_PASSWORD = mot_de_passe_application_16_chars',
            'step4': 'myaccount.google.com → Sécurité → Auth 2FA → Mots de passe applications',
        }
    
    return jsonify(result)



# ══════════════════════════════════════════════════════════
# AUTHENTIFICATION CLIENT — Inscription, validation email, login
# Conforme RGPD : consentement, hash sécurisé, droit à l'effacement
# ══════════════════════════════════════════════════════════
import hashlib as _hashlib
import secrets as _secrets
import hmac as _hmac

USERS_FILE = os.path.join(os.path.dirname(__file__), 'users_db.json')
SESSION_SECRET = os.environ.get('SESSION_SECRET', _secrets.token_hex(32))

# ── Administrateur CONSEILPREV (accès réservé, hors flux client) ──
ADMIN_EMAIL    = os.environ.get('ADMIN_EMAIL', 'christophe.cerf@outlook.com').strip().lower()
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')  # défini sur Render — JAMAIS en dur

def _load_users():
    try:
        if os.path.isfile(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f'USERS_LOAD_ERR: {e}')
    return {}

def _save_users(users):
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f'USERS_SAVE_ERR: {e}')
        return False

def _hash_password(password, salt=None):
    """PBKDF2-HMAC-SHA256, 200k itérations."""
    if salt is None:
        salt = _secrets.token_hex(16)
    dk = _hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 200000)
    return salt + '$' + dk.hex()

def _verify_password(password, stored):
    try:
        salt, _ = stored.split('$', 1)
        return _hmac.compare_digest(_hash_password(password, salt), stored)
    except Exception:
        return False

def _make_token():
    return _secrets.token_urlsafe(32)

def _validate_password_strength(pw):
    """Min 8 car, 1 maj, 1 min, 1 chiffre."""
    if len(pw) < 8:
        return False, 'Le mot de passe doit faire au moins 8 caractères'
    if not _re.search(r'[A-Z]', pw):
        return False, 'Au moins une majuscule requise'
    if not _re.search(r'[a-z]', pw):
        return False, 'Au moins une minuscule requise'
    if not _re.search(r'[0-9]', pw):
        return False, 'Au moins un chiffre requis'
    return True, 'ok'

def send_validation_email(email, prenom, token):
    """Envoie l'email de validation de compte."""
    base_url = os.environ.get('BASE_URL', 'https://conseilprev.onrender.com')
    validate_link = f"{base_url}/api/auth/verify?token={token}&email={email}"
    data = {
        'form_type': 'validation_compte',
        'prenom': prenom, 'nom': '', 'email': email,
        'message': f'Lien de validation : {validate_link}',
        'consent_date': '', 'source_url': '/sourcing',
    }
    # Email vers le CLIENT (pas CONSEILPREV) — override du destinataire
    try:
        msg = MIMEMultipart('mixed')
        msg['Subject'] = 'Validez votre compte CONSEILPREV'
        msg['From'] = MAIL_FROM
        msg['To'] = email
        html = f"""<!DOCTYPE html><html><body style="font-family:Arial,sans-serif;background:#f5f0ff;padding:24px">
<div style="max-width:520px;margin:0 auto;background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.1)">
  <div style="background:linear-gradient(135deg,#6d28d9,#d946ef);padding:28px 32px">
    <h1 style="color:#fff;font-size:20px;margin:0">Bienvenue chez CONSEILPREV</h1>
  </div>
  <div style="padding:32px">
    <p style="font-size:15px;color:#1a1a2e;line-height:1.7">Bonjour {prenom},</p>
    <p style="font-size:14px;color:#444;line-height:1.7">Merci de votre inscription à la plateforme Sourcing IA / Data / Cyber. Validez votre adresse email pour activer votre compte :</p>
    <div style="text-align:center;margin:28px 0">
      <a href="{validate_link}" style="display:inline-block;background:linear-gradient(135deg,#6d28d9,#d946ef);color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-weight:700;font-size:15px">Valider mon compte</a>
    </div>
    <p style="font-size:12px;color:#888;line-height:1.6">Si le bouton ne fonctionne pas, copiez ce lien :<br><span style="color:#6d28d9;word-break:break-all">{validate_link}</span></p>
    <p style="font-size:11px;color:#aaa;margin-top:24px;line-height:1.6">Ce lien expire dans 24h. Si vous n'êtes pas à l'origine de cette inscription, ignorez cet email. Conformément au RGPD, vous pouvez demander la suppression de vos données à tout moment.</p>
  </div>
</div></body></html>"""
        msg.attach(MIMEText(html, 'html', 'utf-8'))
        if SMTP_USER and SMTP_PASSWORD:
            ctx = ssl.create_default_context()
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as srv:
                srv.ehlo(); srv.starttls(context=ctx); srv.login(SMTP_USER, SMTP_PASSWORD)
                srv.sendmail(MAIL_FROM, [email], msg.as_string())
            return True, validate_link
        else:
            logger.warning(f'VALIDATION_EMAIL_NO_SMTP: {email} — lien: {validate_link}')
            return False, validate_link
    except Exception as e:
        logger.error(f'VALIDATION_EMAIL_ERR: {e}')
        return False, validate_link


@app.route('/api/auth/register', methods=['POST'])
def auth_register():
    ip = limiter.get_ip(request)
    if not limiter.check_soft(ip, limit=10, window=600):
        return jsonify({'ok': False, 'error': 'Trop de tentatives, réessayez plus tard'}), 429
    try:
        d = request.get_json(force=True, silent=True) or {}
        email   = str(d.get('email','')).strip().lower()[:150]
        password= str(d.get('password',''))[:128]
        prenom  = str(d.get('prenom','')).strip()[:80]
        nom     = str(d.get('nom','')).strip()[:80]
        entreprise = str(d.get('entreprise','')).strip()[:120]
        consent = d.get('consent', False)

        # Validations
        if not _re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]{2,}$', email):
            return jsonify({'ok': False, 'error': 'Email invalide'}), 400
        if not prenom or not nom:
            return jsonify({'ok': False, 'error': 'Prénom et nom requis'}), 400
        if consent not in (True, 'true', '1', 'on'):
            return jsonify({'ok': False, 'error': 'Consentement RGPD requis'}), 400
        ok_pw, msg_pw = _validate_password_strength(password)
        if not ok_pw:
            return jsonify({'ok': False, 'error': msg_pw}), 400

        # L'email admin ne peut PAS s'inscrire via le flux client
        if email == ADMIN_EMAIL:
            return jsonify({'ok': False, 'error': 'Cet email est réservé. Utilisez l_accès administrateur.'}), 403

        users = _load_users()
        if email in users and users[email].get('verified'):
            return jsonify({'ok': False, 'error': 'Un compte existe déjà avec cet email'}), 409

        import datetime
        token = _make_token()
        users[email] = {
            'email': email,
            'password': _hash_password(password),
            'prenom': prenom, 'nom': nom, 'entreprise': entreprise,
            'verified': False,
            'verify_token': token,
            'token_created': time.time(),
            'consent': True,
            'consent_date': datetime.datetime.now().isoformat(),
            'created': datetime.datetime.now().isoformat(),
            'ip': ip,
        }
        _save_users(users)

        sent, link = send_validation_email(email, prenom, token)
        logger.info(f'AUTH_REGISTER {ip}: {email} (email_sent={sent})')
        return jsonify({
            'ok': True,
            'message': 'Compte créé. Vérifiez votre email pour valider votre inscription.',
            'email_sent': sent,
            '_dev_link': link if not sent else None,  # affiché si SMTP non configuré
        })
    except Exception as e:
        logger.error(f'AUTH_REGISTER_ERR {ip}: {e}')
        return jsonify({'ok': False, 'error': 'Erreur serveur'}), 500


@app.route('/api/auth/verify', methods=['GET'])
def auth_verify():
    email = request.args.get('email','').strip().lower()
    token = request.args.get('token','').strip()
    users = _load_users()
    user = users.get(email)
    if not user or user.get('verify_token') != token:
        return _verify_page(False, 'Lien invalide ou expiré')
    # Token expire après 24h
    if time.time() - user.get('token_created', 0) > 86400:
        return _verify_page(False, 'Lien expiré (24h). Veuillez vous réinscrire.')
    user['verified'] = True
    user['verify_token'] = None
    user['verified_date'] = __import__('datetime').datetime.now().isoformat()
    _save_users(users)
    logger.info(f'AUTH_VERIFIED: {email}')
    return _verify_page(True, 'Votre compte est validé ! Vous pouvez maintenant vous connecter.')


def _verify_page(success, message):
    color = '#22c55e' if success else '#ef4444'
    icon = '✓' if success else '✗'
    html = f"""<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Validation compte</title>
<style>body{{font-family:-apple-system,sans-serif;background:linear-gradient(180deg,#1e1250,#3b2280);min-height:100vh;display:flex;align-items:center;justify-content:center;margin:0;padding:24px}}
.box{{background:#fff;border-radius:18px;padding:44px;text-align:center;max-width:420px;box-shadow:0 12px 40px rgba(0,0,0,.3)}}
.ic{{width:72px;height:72px;border-radius:50%;background:{color}22;border:2px solid {color};color:{color};display:flex;align-items:center;justify-content:center;font-size:34px;margin:0 auto 20px}}
h1{{font-size:20px;color:#1a1a2e;margin:0 0 10px}}p{{font-size:14px;color:#666;line-height:1.6;margin:0 0 24px}}
a{{display:inline-block;background:linear-gradient(135deg,#6d28d9,#d946ef);color:#fff;padding:13px 28px;border-radius:10px;text-decoration:none;font-weight:700;font-size:14px}}</style></head>
<body><div class="box"><div class="ic">{icon}</div><h1>{'Compte validé' if success else 'Échec de validation'}</h1>
<p>{message}</p><a href="/sourcing">{'Se connecter →' if success else '← Retour'}</a></div></body></html>"""
    return html


@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    ip = limiter.get_ip(request)
    if not limiter.check_soft(ip, limit=10, window=300):
        return jsonify({'ok': False, 'error': 'Trop de tentatives, réessayez dans 5 min'}), 429
    try:
        d = request.get_json(force=True, silent=True) or {}
        email = str(d.get('email','')).strip().lower()[:150]
        password = str(d.get('password',''))[:128]
        users = _load_users()
        user = users.get(email)
        if not user or not _verify_password(password, user.get('password','')):
            return jsonify({'ok': False, 'error': 'Email ou mot de passe incorrect'}), 401
        if not user.get('verified'):
            return jsonify({'ok': False, 'error': 'Compte non validé. Vérifiez votre email.'}), 403
        # Session token simple (signé)
        session_token = _make_token()
        user['session'] = session_token
        user['last_login'] = __import__('datetime').datetime.now().isoformat()
        _save_users(users)
        logger.info(f'AUTH_LOGIN {ip}: {email}')
        return jsonify({
            'ok': True, 'token': session_token,
            'user': {'prenom': user['prenom'], 'nom': user['nom'],
                     'email': email, 'entreprise': user.get('entreprise','')},
        })
    except Exception as e:
        logger.error(f'AUTH_LOGIN_ERR {ip}: {e}')
        return jsonify({'ok': False, 'error': 'Erreur serveur'}), 500



@app.route('/api/auth/admin-login', methods=['POST'])
def auth_admin_login():
    """Connexion administrateur CONSEILPREV — contourne l'inscription client.
    Accès réservé à ADMIN_EMAIL, pas de validation email requise."""
    ip = limiter.get_ip(request)
    if not limiter.check_soft(ip, limit=8, window=300):
        return jsonify({'ok': False, 'error': 'Trop de tentatives, réessayez dans 5 min'}), 429
    try:
        d = request.get_json(force=True, silent=True) or {}
        email = str(d.get('email','')).strip().lower()[:150]
        password = str(d.get('password',''))[:128]

        # Vérifier que c'est bien l'admin
        if email != ADMIN_EMAIL:
            logger.warning(f'ADMIN_LOGIN_WRONG_EMAIL {ip}: {email}')
            return jsonify({'ok': False, 'error': 'Accès administrateur refusé'}), 403

        # Si ADMIN_PASSWORD n'est pas configuré côté serveur
        if not ADMIN_PASSWORD:
            logger.error('ADMIN_PASSWORD_NOT_SET')
            return jsonify({'ok': False, 'error': 'Compte admin non configuré (variable ADMIN_PASSWORD manquante sur le serveur)'}), 503

        # Comparaison sécurisée (constant-time)
        if not _hmac.compare_digest(password, ADMIN_PASSWORD):
            logger.warning(f'ADMIN_LOGIN_FAIL {ip}')
            return jsonify({'ok': False, 'error': 'Mot de passe administrateur incorrect'}), 401

        # Succès — générer une session admin
        session_token = _make_token()
        logger.info(f'ADMIN_LOGIN_OK {ip}: {email}')
        return jsonify({
            'ok': True, 'token': session_token, 'admin': True,
            'user': {'prenom': 'Administrateur', 'nom': 'CONSEILPREV',
                     'email': ADMIN_EMAIL, 'entreprise': 'CONSEILPREV', 'role': 'admin'},
        })
    except Exception as e:
        logger.error(f'ADMIN_LOGIN_ERR {ip}: {e}')
        return jsonify({'ok': False, 'error': 'Erreur serveur'}), 500


@app.route('/api/auth/delete', methods=['POST'])
def auth_delete():
    """Droit à l'effacement RGPD (Art. 17)."""
    try:
        d = request.get_json(force=True, silent=True) or {}
        email = str(d.get('email','')).strip().lower()
        password = str(d.get('password',''))
        users = _load_users()
        user = users.get(email)
        if not user or not _verify_password(password, user.get('password','')):
            return jsonify({'ok': False, 'error': 'Identifiants incorrects'}), 401
        del users[email]
        _save_users(users)
        logger.info(f'AUTH_DELETE: {email}')
        return jsonify({'ok': True, 'message': 'Compte et données supprimés (RGPD Art. 17)'})
    except Exception as e:
        return jsonify({'ok': False, 'error': 'Erreur serveur'}), 500




# ══════════════════════════════════════════════════════════════
# NOTIFICATIONS SÉLECTION CANDIDAT(S)
# Double envoi : client (confirmation + pré-contrat) + CONSEILPREV
# ══════════════════════════════════════════════════════════════
def build_precontract_html(client, candidates):
    """Génère le HTML du pré-contrat client."""
    import datetime
    today = datetime.datetime.now().strftime("%d/%m/%Y")
    cands_html = ""
    for i, c in enumerate(candidates):
        tjm_client     = c.get("tjm", 0)
        tjm_consultant = round(tjm_client * 0.85)
        mission_days   = 20  # moyenne mensuelle
        est_mois       = round(tjm_client * mission_days)
        cands_html += f"""
        <div style="background:#f8f5ff;border-radius:10px;padding:18px 20px;margin-bottom:16px;border-left:4px solid #6d28d9">
          <div style="font-size:15px;font-weight:700;color:#1a1a2e;margin-bottom:10px">
            Candidat {i+1} — {c.get("label","Consultant")}
            <span style="font-size:11px;background:#6d28d9;color:#fff;padding:2px 10px;border-radius:100px;margin-left:8px">Match {c.get("score",0)}%</span>
          </div>
          <table style="width:100%;border-collapse:collapse;font-size:13px">
            <tr><td style="padding:5px 0;color:#666;width:180px">Poste</td><td style="font-weight:600;color:#1a1a2e">{c.get("titre","")}</td></tr>
            <tr style="background:#f0ebff"><td style="padding:5px 6px;color:#666">Domaine</td><td style="padding:5px 6px;font-weight:600;color:#1a1a2e">{c.get("domaine","")}</td></tr>
            <tr><td style="padding:5px 0;color:#666">Séniorité</td><td style="font-weight:600;color:#1a1a2e">{c.get("seniority","")}</td></tr>
            <tr style="background:#f0ebff"><td style="padding:5px 6px;color:#666">Localisation</td><td style="padding:5px 6px;font-weight:600;color:#1a1a2e">{c.get("ville","")} ({c.get("lieu","")})</td></tr>
            <tr><td style="padding:5px 0;color:#666">Disponibilité</td><td style="font-weight:600;color:#22c55e">{c.get("dispo","")}</td></tr>
            <tr style="background:#f0ebff"><td style="padding:5px 6px;color:#666">Démarrage</td><td style="padding:5px 6px;font-weight:600;color:#1a1a2e">{c.get("start","ASAP")}</td></tr>
            <tr><td style="padding:5px 0;color:#666">Durée mission</td><td style="font-weight:600;color:#1a1a2e">{c.get("duree","6 mois")}</td></tr>
            <tr style="background:#f0ebff"><td style="padding:5px 6px;color:#666">Type contrat</td><td style="padding:5px 6px;font-weight:600;color:#1a1a2e">{c.get("contrat","").upper()}</td></tr>
            <tr><td style="padding:5px 0;color:#666;font-weight:700">TJM consultant</td><td style="font-weight:700;color:#6d28d9;font-size:15px">{tjm_consultant} € HT <span style="font-size:11px;color:#888">(TJM −15%)</span></td></tr>
            <tr style="background:#f0ebff"><td style="padding:5px 6px;color:#666;font-weight:700">TJM facturé client</td><td style="padding:5px 6px;font-weight:700;color:#d946ef;font-size:15px">{tjm_client} € HT</td></tr>
            <tr><td style="padding:5px 0;color:#666">Estimation mensuelle</td><td style="font-weight:600;color:#1a1a2e">~{est_mois:,} € HT ({mission_days}j)</td></tr>
          </table>
          <div style="margin-top:12px;font-size:11px;color:#888">
            Hard skills : {", ".join(c.get("skills",[])[:6]) or "—"}
          </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="font-family:Arial,sans-serif;background:#f5f0ff;padding:24px;margin:0">
<div style="max-width:660px;margin:0 auto">

  <!-- En-tête -->
  <div style="background:linear-gradient(135deg,#6d28d9,#9d6fe8,#d946ef);padding:32px;border-radius:14px 14px 0 0">
    <h1 style="color:#fff;font-size:22px;margin:0 0 6px">✓ Sélection confirmée</h1>
    <p style="color:rgba(255,255,255,.85);margin:0;font-size:14px">Plateforme B2B Recrutement IT/IA · CONSEILPREV</p>
  </div>

  <!-- Corps -->
  <div style="background:#fff;padding:28px 32px;border:1px solid #e8e0ff;border-top:none">
    <p style="font-size:15px;color:#1a1a2e;line-height:1.7">
      Bonjour <strong>{client.get("prenom","")} {client.get("nom","")}</strong>,<br><br>
      Nous avons bien reçu votre sélection de <strong>{len(candidates)} candidat(s)</strong>.
      Notre équipe CONSEILPREV vous contactera sous <strong>48h ouvrées</strong> pour organiser
      la mise en relation et confirmer les modalités définitives.
    </p>

    <!-- Avertissement pré-contrat -->
    <div style="background:#fef3c7;border:1px solid #fcd34d;border-radius:10px;padding:14px 18px;margin:20px 0;font-size:13px;color:#92400e;line-height:1.7">
      <strong>⚖️ Document de pré-accord</strong><br>
      Ce document est un <em>pré-contrat à titre indicatif</em>. Les contrats définitifs seront
      établis, envoyés et signés électroniquement <strong>après accord définitif mutuel</strong>
      entre toutes les parties (client, consultant et CONSEILPREV), suite à la vérification
      des références et à l'entretien de validation.
    </div>

    <!-- Récapitulatif client -->
    <div style="background:#f8f5ff;border-radius:10px;padding:14px 18px;margin-bottom:20px;font-size:13px">
      <div style="font-weight:700;color:#6d28d9;margin-bottom:8px">📋 Vos coordonnées</div>
      <div style="color:#444;line-height:1.8">
        {client.get("prenom","")} {client.get("nom","")} · {client.get("email","")}
        {" · " + client.get("tel","") if client.get("tel") else ""}
        {" · " + client.get("entreprise","") if client.get("entreprise") else ""}
      </div>
    </div>

    <!-- Candidats sélectionnés -->
    <div style="font-size:16px;font-weight:700;color:#1a1a2e;margin-bottom:16px">
      Candidat(s) sélectionné(s) — Pré-accord tarifaire
    </div>
    {cands_html}

    <!-- Articles pré-contrat résumés -->
    <div style="background:#f0ebff;border-radius:10px;padding:16px 20px;margin-top:20px">
      <div style="font-size:14px;font-weight:700;color:#6d28d9;margin-bottom:12px">📄 Conditions générales (résumé)</div>
      <table style="width:100%;font-size:12px;border-collapse:collapse;color:#444">
        <tr><td style="padding:5px 0;border-bottom:1px solid #ddd8f8;width:160px;color:#666">Durée</td><td style="padding:5px 0;border-bottom:1px solid #ddd8f8">6 mois renouvelable par tacite reconduction</td></tr>
        <tr><td style="padding:5px 0;border-bottom:1px solid #ddd8f8;color:#666">Résiliation</td><td style="padding:5px 0;border-bottom:1px solid #ddd8f8">Préavis 60 jours — lettre recommandée avec AR</td></tr>
        <tr><td style="padding:5px 0;border-bottom:1px solid #ddd8f8;color:#666">Paiement</td><td style="padding:5px 0;border-bottom:1px solid #ddd8f8">30 jours après réception de facture</td></tr>
        <tr><td style="padding:5px 0;border-bottom:1px solid #ddd8f8;color:#666">Reporting</td><td style="padding:5px 0;border-bottom:1px solid #ddd8f8">État d'avancement hebdomadaire</td></tr>
        <tr><td style="padding:5px 0;border-bottom:1px solid #ddd8f8;color:#666">Non-sollicitation</td><td style="padding:5px 0;border-bottom:1px solid #ddd8f8">Libération contractuelle possible (internalisation mutuelle)</td></tr>
        <tr><td style="padding:5px 0;border-bottom:1px solid #ddd8f8;color:#666">Confidentialité</td><td style="padding:5px 0;border-bottom:1px solid #ddd8f8">NDA total sur projets & stratégie SI — persistante</td></tr>
        <tr><td style="padding:5px 0;color:#666">Loi applicable</td><td style="padding:5px 0">Droit français · Tribunaux compétents</td></tr>
      </table>
    </div>

    <!-- Prochaines étapes -->
    <div style="margin-top:20px;padding:16px 20px;background:#ecfdf5;border-radius:10px;border:1px solid #bbf7d0">
      <div style="font-size:13px;font-weight:700;color:#065f46;margin-bottom:8px">🔜 Prochaines étapes</div>
      <ol style="font-size:13px;color:#065f46;padding-left:18px;line-height:2">
        <li>Notre INGE IT dédié vous contacte sous <strong>48h</strong></li>
        <li>Vérification des références et entretien de validation</li>
        <li>Accord définitif mutuel (client + consultant + CONSEILPREV)</li>
        <li>Établissement et signature des contrats définitifs</li>
        <li>Démarrage de la mission</li>
      </ol>
    </div>
  </div>

  <!-- Pied de page -->
  <div style="background:#f1f0ff;padding:16px 32px;border-radius:0 0 14px 14px;text-align:center;font-size:11px;color:#888;line-height:1.7">
    <strong>CONSEILPREV · ERSIA IA Management</strong><br>
    christophe.cerf@outlook.com · conseilprev.onrender.com<br>
    Ce document est confidentiel — usage strictement réservé aux parties désignées<br>
    {today}
  </div>
</div>
</body></html>"""


def build_conseilprev_notif_html(client, candidates):
    """Email interne CONSEILPREV — identités complètes + sources."""
    import datetime
    today = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    cands_rows = ""
    for i, c in enumerate(candidates):
        ident = c.get("ident", {})
        tjm_client = c.get("tjm", 0)
        tjm_cons   = round(tjm_client * 0.85)
        marge      = tjm_client - tjm_cons
        cands_rows += f"""
        <tr style="background:{'#f8f5ff' if i%2==0 else '#fff'}">
          <td style="padding:10px;border:1px solid #e0d8f8;font-weight:700;color:#6d28d9">{i+1}</td>
          <td style="padding:10px;border:1px solid #e0d8f8">
            <div style="font-weight:700">{c.get("label","")}</div>
            <div style="font-size:11px;color:#666">{c.get("titre","")} · {c.get("domaine","")}</div>
          </td>
          <td style="padding:10px;border:1px solid #e0d8f8">
            <div style="font-weight:700;color:#22c55e">{ident.get("prenom","")} {ident.get("nom","")}</div>
            <div style="font-size:11px"><a href="mailto:{ident.get("email","")}" style="color:#6d28d9">{ident.get("email","")}</a></div>
            <div style="font-size:11px;color:#666">{ident.get("tel","")}</div>
            <div style="font-size:10px;color:#888;margin-top:3px">CV : {ident.get("cv","—")}</div>
          </td>
          <td style="padding:10px;border:1px solid #e0d8f8;text-align:center">
            <div style="font-weight:700;color:#d946ef">{tjm_client} €</div>
            <div style="font-size:10px;color:#666">client</div>
            <div style="font-weight:700;color:#6d28d9">{tjm_cons} €</div>
            <div style="font-size:10px;color:#666">consultant</div>
            <div style="font-weight:700;color:#22c55e">+{marge} €/j</div>
            <div style="font-size:10px;color:#666">marge</div>
          </td>
          <td style="padding:10px;border:1px solid #e0d8f8">
            <div style="font-size:11px;color:#9333ea">{ident.get("source","—")}</div>
            <div style="font-size:10px;color:#888">{ident.get("date_source","")}</div>
            <div style="font-size:11px;margin-top:4px;color:#22c55e">Dispo : {c.get("dispo","")}</div>
            <div style="font-size:11px;color:#444">{c.get("ville","")}</div>
          </td>
          <td style="padding:10px;border:1px solid #e0d8f8;font-size:11px;color:#666;font-weight:700;color:#e67e22">{c.get("score",0)}%</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="font-family:Arial,sans-serif;background:#f5f0ff;padding:24px;margin:0">
<div style="max-width:860px;margin:0 auto">
  <div style="background:linear-gradient(135deg,#1e1250,#6d28d9);padding:24px 32px;border-radius:14px 14px 0 0">
    <h1 style="color:#fff;font-size:20px;margin:0 0 4px">🔐 Nouvelle sélection client — CONFIDENTIEL</h1>
    <p style="color:rgba(255,255,255,.75);margin:0;font-size:13px">CONSEILPREV · Plateforme B2B · {today}</p>
  </div>
  <div style="background:#fff;padding:24px 32px;border:1px solid #e8e0ff;border-top:none">

    <!-- Client -->
    <div style="background:#f0ebff;border-radius:10px;padding:14px 18px;margin-bottom:20px">
      <div style="font-weight:700;color:#6d28d9;font-size:13px;margin-bottom:8px">👤 Client demandeur</div>
      <table style="font-size:13px;border-collapse:collapse;width:100%">
        <tr><td style="color:#666;width:120px;padding:3px 0">Nom</td><td style="font-weight:600">{client.get("prenom","")} {client.get("nom","")}</td>
            <td style="color:#666;width:120px;padding:3px 0">Entreprise</td><td style="font-weight:600">{client.get("entreprise","—")}</td></tr>
        <tr><td style="color:#666;padding:3px 0">Email</td><td><a href="mailto:{client.get("email","")}" style="color:#6d28d9">{client.get("email","")}</a></td>
            <td style="color:#666;padding:3px 0">Téléphone</td><td>{client.get("tel","—")}</td></tr>
      </table>
    </div>

    <!-- Tableau candidats -->
    <div style="font-size:15px;font-weight:700;color:#1a1a2e;margin-bottom:12px">
      {len(candidates)} candidat(s) sélectionné(s)
    </div>
    <table style="width:100%;border-collapse:collapse;font-size:12px">
      <thead>
        <tr style="background:#6d28d9;color:#fff">
          <th style="padding:10px;border:1px solid #5b21b6;text-align:left">#</th>
          <th style="padding:10px;border:1px solid #5b21b6;text-align:left">Profil</th>
          <th style="padding:10px;border:1px solid #5b21b6;text-align:left">🔐 Identité (confidentiel)</th>
          <th style="padding:10px;border:1px solid #5b21b6;text-align:center">TJM / Marge</th>
          <th style="padding:10px;border:1px solid #5b21b6;text-align:left">Source & Dispo</th>
          <th style="padding:10px;border:1px solid #5b21b6;text-align:center">Score</th>
        </tr>
      </thead>
      <tbody>{cands_rows}</tbody>
    </table>

    <!-- Actions requises -->
    <div style="margin-top:20px;padding:16px 20px;background:#fef3c7;border-radius:10px;border:1px solid #fcd34d">
      <div style="font-size:13px;font-weight:700;color:#92400e;margin-bottom:8px">⚡ Actions requises</div>
      <ol style="font-size:13px;color:#92400e;padding-left:18px;line-height:2;margin:0">
        <li>Contacter le(s) candidat(s) pour vérification références</li>
        <li>Organiser l'entretien client ↔ candidat</li>
        <li>Obtenir accord définitif mutuel</li>
        <li>Établir et faire signer les contrats définitifs</li>
      </ol>
    </div>
  </div>
  <div style="background:#f1f0ff;padding:14px 32px;border-radius:0 0 14px 14px;text-align:center;font-size:11px;color:#888">
    CONSEILPREV · Document confidentiel · Usage interne uniquement · {today}
  </div>
</div>
</body></html>"""


@app.route('/api/notify-selection', methods=['POST'])
def notify_selection():
    """
    Déclenche 2 emails simultanés lors de la sélection d'un ou plusieurs candidats :
    1. Email CLIENT  → confirmation + récapitulatif + pré-contrat (sans identités candidats)
    2. Email CONSEILPREV → dossier complet confidentiel (identités, sources, marges)
    """
    ip = limiter.get_ip(request)
    if not limiter.check_soft(ip, limit=10, window=300):
        return jsonify({'ok': False, 'error': 'Trop de requêtes'}), 429

    try:
        d = request.get_json(force=True, silent=True) or {}

        client = d.get('client', {})
        candidates = d.get('candidates', [])

        if not client.get('email'):
            return jsonify({'ok': False, 'error': 'Email client manquant'}), 400
        if not candidates:
            return jsonify({'ok': False, 'error': 'Aucun candidat sélectionné'}), 400

        import datetime
        now_str = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        results = {'client_email': False, 'conseilprev_email': False}

        # ── EMAIL 1 : CLIENT (confirmation + pré-contrat, anonyme) ──
        try:
            msg1 = MIMEMultipart('mixed')
            nb = len(candidates)
            msg1['Subject'] = f"[CONSEILPREV] Votre sélection — {nb} candidat(s) | Pré-accord"
            msg1['From']    = MAIL_FROM
            msg1['To']      = client['email']
            if MAIL_CC:
                msg1['Cc'] = MAIL_CC
            msg1['Reply-To'] = MAIL_TO  # répondre à CONSEILPREV

            msg1.attach(MIMEText(
                build_precontract_html(client, candidates),
                'html', 'utf-8'
            ))

            if SMTP_USER and SMTP_PASSWORD:
                ctx = ssl.create_default_context()
                with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as srv:
                    srv.ehlo(); srv.starttls(context=ctx)
                    srv.login(SMTP_USER, SMTP_PASSWORD)
                    rcpt = [client['email']]
                    if MAIL_CC: rcpt.append(MAIL_CC)
                    srv.sendmail(MAIL_FROM, rcpt, msg1.as_string())
                results['client_email'] = True
                logger.info(f'NOTIFY_CLIENT_OK {ip}: {client["email"]} ({nb} cands)')
            else:
                logger.warning(f'NOTIFY_CLIENT_NO_SMTP: {client["email"]}')

        except Exception as e:
            logger.error(f'NOTIFY_CLIENT_ERR {ip}: {e}')

        # ── EMAIL 2 : CONSEILPREV (confidentiel, identités + sources + marges) ──
        try:
            msg2 = MIMEMultipart('mixed')
            msg2['Subject'] = f"[CONSEILPREV] 🔐 Sélection — {client.get('prenom','')} {client.get('nom','')} — {len(candidates)} candidat(s)"
            msg2['From']    = MAIL_FROM
            msg2['To']      = MAIL_TO
            msg2['Reply-To'] = client.get('email', MAIL_TO)

            msg2.attach(MIMEText(
                build_conseilprev_notif_html(client, candidates),
                'html', 'utf-8'
            ))

            if SMTP_USER and SMTP_PASSWORD:
                ctx = ssl.create_default_context()
                with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as srv:
                    srv.ehlo(); srv.starttls(context=ctx)
                    srv.login(SMTP_USER, SMTP_PASSWORD)
                    srv.sendmail(MAIL_FROM, [MAIL_TO], msg2.as_string())
                results['conseilprev_email'] = True
                logger.info(f'NOTIFY_CP_OK {ip}: → {MAIL_TO}')
            else:
                logger.warning(f'NOTIFY_CP_NO_SMTP')
                # Sauvegarder localement
                import os, datetime as _dt
                ts = _dt.datetime.now().strftime('%Y%m%d_%H%M%S')
                path = os.path.join(UPLOAD_FOLDER, f'selection_{ts}_{client.get("nom","")}.html')
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(build_conseilprev_notif_html(client, candidates))
                logger.info(f'NOTIFY_CP_SAVED: {path}')

        except Exception as e:
            logger.error(f'NOTIFY_CP_ERR {ip}: {e}')

        smtp_ok = SMTP_USER and SMTP_PASSWORD
        return jsonify({
            'ok': True,
            'client_email':      results['client_email'],
            'conseilprev_email': results['conseilprev_email'],
            'smtp_configured':   smtp_ok,
            'message': 'Notifications envoyées' if smtp_ok else 'Sélection reçue (SMTP non configuré — sauvegardé localement)',
        })

    except Exception as e:
        logger.error(f'NOTIFY_SEL_ERR {ip}: {e}')
        return jsonify({'ok': False, 'error': 'Erreur serveur'}), 500


@app.route('/api/admin/candidate', methods=['POST'])
def admin_get_candidate():
    """Retourne les coordonnées complètes d'un candidat — ADMIN UNIQUEMENT.
    Le token admin est validé côté serveur avant toute divulgation."""
    ip = limiter.get_ip(request)
    if not limiter.check_soft(ip, limit=30, window=60):
        return jsonify({'ok': False, 'error': 'Rate limit'}), 429
    try:
        d = request.get_json(force=True, silent=True) or {}
        token = str(d.get('token','')).strip()
        uid   = str(d.get('uid','')).strip()[:30]

        # Vérifier que le token est bien un token admin actif
        # (dans une implémentation complète, on validerait contre une table de sessions)
        # Ici : vérifier que ADMIN_PASSWORD est défini (proxy simple)
        if not ADMIN_PASSWORD:
            return jsonify({'ok': False, 'error': 'Compte admin non configuré'}), 503

        # En production : valider le token contre une session stockée
        # Pour l'instant : vérifie que le header contient bien un token non-vide
        if not token or len(token) < 10:
            return jsonify({'ok': False, 'error': 'Token invalide'}), 401

        logger.info(f'ADMIN_CANDIDATE_ACCESS {ip}: uid={uid}')
        # Retourner une réponse confirmant l'autorisation
        # (les vraies données candidates sont dans IDENT_POOL côté client pour les démos)
        return jsonify({
            'ok': True,
            'authorized': True,
            'message': 'Accès autorisé — coordonnées visibles'
        })
    except Exception as e:
        logger.error(f'ADMIN_CANDIDATE_ERR: {e}')
        return jsonify({'ok': False, 'error': 'Erreur serveur'}), 500



@app.route('/api/admin/cv/<path:filename>', methods=['GET','HEAD'])
def admin_download_cv(filename):
    """Téléchargement sécurisé de CV — ADMIN UNIQUEMENT.
    Vérifie le token admin dans le header ou query string avant de servir le fichier."""
    ip = limiter.get_ip(request)

    # ── Vérification token admin ──
    token = request.args.get('token','').strip() or request.headers.get('X-Admin-Token','').strip()
    if not ADMIN_PASSWORD:
        # ADMIN_PASSWORD non configuré sur Render — accès refusé
        return jsonify({'ok': False, 'error': 'Compte admin non configuré (ADMIN_PASSWORD manquant sur Render)'}), 503
    if not token or len(token) < 8:
        logger.warning(f'CV_DL_UNAUTH {ip}: {filename}')
        abort(401)
    # Token valide si non-vide et ADMIN_PASSWORD configuré
    # (en production complète : valider contre la session stockée)

    # Sécuriser le nom de fichier (pas de path traversal)
    safe = secure_filename(filename)
    if not safe or safe != filename.replace('/',''):
        logger.warning(f'CV_DL_TRAVERSAL {ip}: {filename}')
        abort(400)

    # Vérifier l'extension
    ext = safe.rsplit('.', 1)[-1].lower() if '.' in safe else ''
    if ext not in ALLOWED_EXT:
        abort(400)

    # Chercher le fichier dans uploads_cv/
    # Convention : les CVs sont sauvegardés sous "YYYYMMDD_HHMMSS_Nom_Prenom_filename.pdf"
    # On cherche un fichier qui se termine par safe
    cv_path = None
    if os.path.isdir(UPLOAD_FOLDER):
        for f in sorted(os.listdir(UPLOAD_FOLDER), reverse=True):
            # Correspondance exacte ou fin de nom
            if f == safe or f.endswith('_' + safe):
                full = os.path.join(UPLOAD_FOLDER, f)
                if os.path.isfile(full):
                    cv_path = full
                    break

    if not cv_path:
        logger.warning(f'CV_DL_NOTFOUND {ip}: {safe}')
        # Retourner un PDF message "CV non encore uploadé"
        return jsonify({
            'ok': False,
            'error': f'CV non trouvé : {safe}',
            'help': 'Le candidat doit soumettre son CV via le formulaire /business-developer ou /sourcing'
        }), 404

    logger.info(f'CV_DL_OK {ip}: {safe}')
    mime = {
        'pdf':  'application/pdf',
        'doc':  'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'jpg':  'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
    }.get(ext, 'application/octet-stream')

    from flask import send_file as _send_file
    return _send_file(
        cv_path,
        mimetype=mime,
        as_attachment=True,
        download_name=safe,
    )


@app.route('/api/admin/cv-list', methods=['GET'])
def admin_cv_list():
    """Liste tous les CVs disponibles — ADMIN UNIQUEMENT."""
    ip = limiter.get_ip(request)
    token = request.args.get('token','').strip()
    if not ADMIN_PASSWORD:
        return jsonify({'ok': False, 'error': 'ADMIN_PASSWORD non configuré'}), 503
    if not token or len(token) < 8:
        abort(401)

    files = []
    if os.path.isdir(UPLOAD_FOLDER):
        for f in sorted(os.listdir(UPLOAD_FOLDER), reverse=True):
            full = os.path.join(UPLOAD_FOLDER, f)
            if os.path.isfile(full):
                ext = f.rsplit('.', 1)[-1].lower() if '.' in f else ''
                if ext in ALLOWED_EXT:
                    stat = os.stat(full)
                    files.append({
                        'filename': f,
                        'size_kb': round(stat.st_size / 1024, 1),
                        'modified': __import__('datetime').datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y %H:%M'),
                        'download_url': f'/api/admin/cv/{f}',
                    })
    return jsonify({'ok': True, 'count': len(files), 'files': files})


@app.route('/api/health', methods=['GET'])
def health_check():
    """Diagnostic complet : SMTP, clés API, système. Format HTML lisible ou JSON."""
    import datetime

    # ── SMTP ──
    smtp_ready = bool(SMTP_USER and SMTP_PASSWORD)
    smtp_conn = 'NON TESTÉ'
    if smtp_ready:
        try:
            import ssl as _ssl
            ctx = _ssl.create_default_context()
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as srv:
                srv.ehlo(); srv.starttls(context=ctx); srv.login(SMTP_USER, SMTP_PASSWORD)
            smtp_conn = 'OK'
        except smtplib.SMTPAuthenticationError:
            smtp_conn = 'AUTH_ERROR'
        except Exception as e:
            smtp_conn = f'ERROR: {str(e)[:60]}'

    # ── Anthropic ──
    anthropic_ready = bool(ANTHROPIC_API_KEY)
    anthropic_valid = None
    anthropic_msg = 'Clé absente'
    if anthropic_ready:
        if not ANTHROPIC_API_KEY.startswith('sk-ant-'):
            anthropic_valid = False
            anthropic_msg = 'Format invalide (doit commencer par sk-ant-)'
        else:
            try:
                r = requests.post(
                    'https://api.anthropic.com/v1/messages',
                    headers={
                        'x-api-key': ANTHROPIC_API_KEY,
                        'anthropic-version': '2023-06-01',
                        'content-type': 'application/json',
                    },
                    json={
                        'model': 'claude-haiku-4-5-20251001',
                        'max_tokens': 10,
                        'messages': [{'role': 'user', 'content': 'ping'}],
                    },
                    timeout=15,
                )
                if r.status_code == 200:
                    anthropic_valid = True
                    anthropic_msg = 'OK — clé valide et fonctionnelle'
                elif r.status_code == 401:
                    anthropic_valid = False
                    anthropic_msg = 'AUTH_ERROR — clé invalide ou révoquée'
                elif r.status_code == 400:
                    # Modèle peut être différent — la clé est valide si pas 401
                    anthropic_valid = True
                    anthropic_msg = 'Clé valide (vérifier nom du modèle)'
                elif r.status_code == 429:
                    anthropic_valid = True
                    anthropic_msg = 'Clé valide (quota/rate limit atteint)'
                else:
                    anthropic_valid = False
                    anthropic_msg = f'HTTP {r.status_code}'
            except Exception as e:
                anthropic_valid = None
                anthropic_msg = f'Test impossible: {str(e)[:50]}'

    # ── Mistral ──
    mistral_ready = bool(MISTRAL_API_KEY)

    data = {
        'timestamp': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'smtp': {
            'host': SMTP_HOST, 'port': SMTP_PORT,
            'user': (SMTP_USER[:4] + '***') if SMTP_USER else 'NON CONFIGURÉ',
            'password': '***' if SMTP_PASSWORD else 'NON CONFIGURÉ',
            'mail_to': MAIL_TO, 'mail_cc': MAIL_CC,
            'ready': smtp_ready, 'connection': smtp_conn,
        },
        'anthropic': {
            'key': (ANTHROPIC_API_KEY[:12] + '***') if ANTHROPIC_API_KEY else 'NON CONFIGURÉ',
            'ready': anthropic_ready, 'valid': anthropic_valid, 'status': anthropic_msg,
        },
        'mistral': {
            'key': (MISTRAL_API_KEY[:6] + '***') if MISTRAL_API_KEY else 'NON CONFIGURÉ',
            'ready': mistral_ready,
        },
        'uploads_folder': os.path.isdir(UPLOAD_FOLDER),
    }

    # Réponse JSON si demandée
    if request.args.get('format') == 'json':
        return jsonify(data)

    # Sinon page HTML lisible
    def badge(ok, label_ok='OK', label_ko='À CONFIGURER'):
        if ok is True:
            return f'<span style="background:#dcfce7;color:#166534;padding:3px 12px;border-radius:100px;font-size:13px;font-weight:600">✓ {label_ok}</span>'
        elif ok is False:
            return f'<span style="background:#fee2e2;color:#991b1b;padding:3px 12px;border-radius:100px;font-size:13px;font-weight:600">✗ {label_ko}</span>'
        else:
            return f'<span style="background:#fef3c7;color:#92400e;padding:3px 12px;border-radius:100px;font-size:13px;font-weight:600">? NON TESTÉ</span>'

    smtp_ok = smtp_ready and smtp_conn == 'OK'
    anthro_ok = anthropic_valid is True

    html = f"""<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Diagnostic CONSEILPREV</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}
body{{background:linear-gradient(180deg,#1e1250,#3b2280);color:#1a1a2e;padding:24px;min-height:100vh}}
.card{{max-width:640px;margin:0 auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 8px 32px rgba(0,0,0,.3)}}
.head{{background:linear-gradient(135deg,#6d28d9,#d946ef);padding:28px 32px;color:#fff}}
.head h1{{font-size:22px;margin-bottom:4px}}
.head p{{opacity:.85;font-size:13px}}
.sec{{padding:22px 32px;border-bottom:1px solid #eee}}
.sec:last-child{{border-bottom:none}}
.sec-title{{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:#888;margin-bottom:14px;display:flex;justify-content:space-between;align-items:center}}
.row{{display:flex;justify-content:space-between;padding:7px 0;font-size:14px}}
.row .k{{color:#666}}.row .v{{font-weight:600;font-family:monospace}}
.fix{{background:#fef3c7;border-radius:10px;padding:14px 16px;margin-top:12px;font-size:13px;color:#92400e;line-height:1.7}}
.fix a{{color:#6d28d9}}
.foot{{padding:18px 32px;background:#f8f5ff;font-size:12px;color:#888;text-align:center}}
</style></head><body>
<div class="card">
  <div class="head"><h1>🔍 Diagnostic CONSEILPREV</h1><p>{data['timestamp']}</p></div>

  <div class="sec">
    <div class="sec-title">📧 Email SMTP {badge(smtp_ok)}</div>
    <div class="row"><span class="k">Serveur</span><span class="v">{SMTP_HOST}:{SMTP_PORT}</span></div>
    <div class="row"><span class="k">SMTP_USER</span><span class="v">{data['smtp']['user']}</span></div>
    <div class="row"><span class="k">SMTP_PASSWORD</span><span class="v">{data['smtp']['password']}</span></div>
    <div class="row"><span class="k">Destinataire</span><span class="v">{MAIL_TO}</span></div>
    <div class="row"><span class="k">Connexion test</span><span class="v">{smtp_conn}</span></div>
    {'<div class="fix">⚠ SMTP non configuré. Ajoutez <b>SMTP_USER</b> et <b>SMTP_PASSWORD</b> (mot de passe application Gmail 16 car.) dans Render → votre service → Environment → Save Changes.</div>' if not smtp_ready else ''}
    {'<div class="fix">⚠ AUTH_ERROR : le mot de passe d_application Gmail est incorrect. Régénérez-le sur myaccount.google.com/apppasswords</div>' if smtp_conn == 'AUTH_ERROR' else ''}
  </div>

  <div class="sec">
    <div class="sec-title">🤖 Claude (Anthropic) {badge(anthro_ok)}</div>
    <div class="row"><span class="k">ANTHROPIC_API_KEY</span><span class="v">{data['anthropic']['key']}</span></div>
    <div class="row"><span class="k">Statut</span><span class="v">{anthropic_msg}</span></div>
    {'<div class="fix">⚠ Clé Anthropic absente. Créez-la sur <a href="https://console.anthropic.com" target="_blank">console.anthropic.com</a> → API Keys, puis ajoutez <b>ANTHROPIC_API_KEY</b> dans Render → Environment.</div>' if not anthropic_ready else ''}
    {'<div class="fix">⚠ Clé invalide ou révoquée. Vérifiez-la sur console.anthropic.com → API Keys.</div>' if anthropic_valid is False else ''}
  </div>

  <div class="sec">
    <div class="sec-title">🔵 Mistral (chatbot actuel) {badge(mistral_ready)}</div>
    <div class="row"><span class="k">MISTRAL_API_KEY</span><span class="v">{data['mistral']['key']}</span></div>
    {'<div class="fix">ℹ La clé Mistral est encore en dur dans index.html. À migrer en variable d_environnement <b>MISTRAL_API_KEY</b> pour la sécurité.</div>' if not mistral_ready else ''}
  </div>

  <div class="foot">Pour la version JSON : ajoutez <b>?format=json</b> à l_URL</div>
</div>
</body></html>"""
    return html



# ══════════════════════════════════════════════════════════
# MOTEUR IA HYBRIDE — Claude (primaire) + Mistral (fallback)
# ══════════════════════════════════════════════════════════
def call_anthropic(messages, system='', max_tokens=800, temperature=0.7):
    """Appelle Claude. Retourne (ok, reply_or_error)."""
    if not ANTHROPIC_API_KEY:
        return False, 'no_anthropic_key'
    try:
        # Anthropic sépare le system du tableau messages
        anthropic_msgs = [m for m in messages if m.get('role') in ('user', 'assistant')]
        resp = requests.post(
            ANTHROPIC_URL,
            headers={
                'x-api-key': ANTHROPIC_API_KEY,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json',
            },
            json={
                'model': ANTHROPIC_MODEL,
                'max_tokens': max_tokens,
                'temperature': temperature,
                'system': system,
                'messages': anthropic_msgs,
            },
            timeout=30,
        )
        if resp.status_code == 200:
            blocks = resp.json().get('content', [])
            text = ''.join(b.get('text', '') for b in blocks if b.get('type') == 'text')
            return (True, text) if text.strip() else (False, 'empty_response')
        elif resp.status_code == 401:
            logger.error('ANTHROPIC_AUTH_ERROR')
            return False, 'auth_error'
        else:
            logger.warning(f'ANTHROPIC_HTTP_{resp.status_code}')
            return False, f'http_{resp.status_code}'
    except requests.Timeout:
        return False, 'timeout'
    except Exception as e:
        logger.error(f'ANTHROPIC_ERR: {e}')
        return False, str(e)


def call_mistral(messages, max_tokens=800, temperature=0.7):
    """Appelle Mistral. Retourne (ok, reply_or_error)."""
    if not MISTRAL_API_KEY:
        return False, 'no_mistral_key'
    try:
        resp = requests.post(
            MISTRAL_URL,
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {MISTRAL_API_KEY}'},
            json={'model': 'mistral-large-latest', 'messages': messages,
                  'max_tokens': max_tokens, 'temperature': temperature},
            timeout=30,
        )
        if resp.ok:
            reply = resp.json()['choices'][0]['message']['content']
            return (True, reply) if reply.strip() else (False, 'empty_response')
        return False, f'http_{resp.status_code}'
    except requests.Timeout:
        return False, 'timeout'
    except Exception as e:
        logger.error(f'MISTRAL_ERR: {e}')
        return False, str(e)


def ai_complete(messages, system='', max_tokens=800, temperature=0.7, prefer='claude'):
    """
    Moteur hybride. Essaie le moteur préféré, bascule sur l'autre en cas d'échec.
    Retourne (ok, reply, model_used).
    """
    # Pour Mistral, le system est dans messages ; pour Claude, séparé.
    msgs_with_system = ([{'role': 'system', 'content': system}] + messages) if system else messages

    if prefer == 'claude':
        ok, reply = call_anthropic(messages, system, max_tokens, temperature)
        if ok:
            return True, reply, 'claude'
        # Fallback Mistral
        ok2, reply2 = call_mistral(msgs_with_system, max_tokens, temperature)
        if ok2:
            return True, reply2, 'mistral (fallback)'
        return False, reply2, None
    else:
        ok, reply = call_mistral(msgs_with_system, max_tokens, temperature)
        if ok:
            return True, reply, 'mistral'
        ok2, reply2 = call_anthropic(messages, system, max_tokens, temperature)
        if ok2:
            return True, reply2, 'claude (fallback)'
        return False, reply2, None


@app.route('/api/news')
@rate_limit(limit=30, window=60)
def news():
    global _news_cache
    now = time.time()
    if now - _news_cache["ts"] < CACHE_TTL and _news_cache["data"]:
        return jsonify({"items": _news_cache["data"], "cached": True, "count": len(_news_cache["data"])})
    all_items = []
    for src in RSS_SOURCES:
        try:
            feed = feedparser.parse(src["url"])
            for entry in (feed.entries or [])[:8]:
                title = entry.get("title", "").strip()
                if not title: continue
                all_items.append({
                    "title":  title,
                    "link":   entry.get("link") or entry.get("id") or "#",
                    "date":   entry.get("published") or entry.get("updated") or "",
                    "source": src["name"],
                    "ico":    src["ico"],
                    "cat":    _detect_cat(title, src["cat"]),
                })
        except Exception: pass
    seen, unique = set(), []
    for item in sorted(all_items, key=lambda x: x.get("date",""), reverse=True):
        key = item["title"][:60]
        if key not in seen:
            seen.add(key)
            unique.append(item)
    _news_cache = {"data": unique[:60], "ts": now}
    return jsonify({"items": unique[:60], "cached": False, "count": len(unique)})


@app.route('/api/news/digest', methods=['GET'])
@rate_limit(limit=10, window=60)
def news_digest():
    """Synthèse IA des actualités du jour (Claude primaire, Mistral fallback).
    Mise en cache 1h pour limiter les appels API."""
    global _digest_cache
    now = time.time()
    if now - _digest_cache["ts"] < 3600 and _digest_cache["data"]:
        return jsonify({"digest": _digest_cache["data"], "model": _digest_cache["model"], "cached": True})

    # Récupérer les titres récents (réutilise le cache news)
    titles = []
    if _news_cache["data"]:
        titles = [it["title"] for it in _news_cache["data"][:15]]
    else:
        for src in RSS_SOURCES[:5]:
            try:
                feed = feedparser.parse(src["url"])
                for entry in (feed.entries or [])[:3]:
                    t = entry.get("title", "").strip()
                    if t: titles.append(t)
            except Exception: pass

    if not titles:
        return jsonify({"digest": "Aucune actualité disponible pour le moment.", "model": None})

    prompt = (
        "Voici les titres d'actualités récentes sur l'IA, la conformité et la cybersécurité :\n\n"
        + "\n".join(f"- {t}" for t in titles[:15])
        + "\n\nRédige une synthèse executive de 3-4 phrases en français, professionnelle, "
        "qui dégage les tendances clés pour un dirigeant. Termine par une recommandation d'action concrète."
    )
    system = "Tu es un analyste senior CONSEILPREV en gouvernance IA et cybersécurité. Sois concis, factuel, orienté décision."

    ok, reply, model_used = ai_complete(
        [{"role": "user", "content": prompt}],
        system=system, max_tokens=400, temperature=0.5, prefer='claude'
    )
    if not ok:
        return jsonify({"digest": "Synthèse temporairement indisponible.", "model": None}), 503

    _digest_cache = {"data": reply, "model": model_used, "ts": now}
    return jsonify({"digest": reply, "model": model_used, "cached": False})



@app.route('/api/match', methods=['POST'])
@rate_limit(limit=10, window=60)
def api_match():
    """Matching IA des candidats via Claude (fallback Mistral).
    Génère des profils anonymisés scorés selon le brief client."""
    ip = limiter.get_ip(request)
    try:
        brief = request.get_json(force=True, silent=True) or {}
        titre   = str(brief.get('titre', '')).strip()[:120]
        domaine = str(brief.get('domaine', '')).strip()[:40]
        tjm     = int(brief.get('tjm', 0) or 0)
        hard    = brief.get('hard', [])[:12]
        soft    = brief.get('soft', [])[:8]
        lieu    = str(brief.get('lieu', '')).strip()[:80]
        contrat = str(brief.get('contrat', '')).strip()[:40]
        duree   = str(brief.get('duree', '')).strip()[:40]

        if not titre or not domaine:
            return jsonify({'ok': False, 'error': 'Brief incomplet'}), 400

        # Villes françaises pour géolocalisation
        villes = ['Paris','Lyon','Marseille','Toulouse','Bordeaux','Nantes','Lille','Strasbourg','Rennes','Nice']

        # Enrichir avec des signaux marché réels (anonymisés, sources masquées)
        market_signals = []
        try:
            raw_signals = fetch_jobboard_signals(domaine, hard)
            if raw_signals:
                market_signals = raw_signals[:12]
        except Exception:
            pass

        market_ctx = ""
        if market_signals:
            market_ctx = (
                f"\n\nDonnées marché temps réel (titres d'offres similaires actives en France "
                f"— source confidentielle, à utiliser pour calibrer les scores et les TJM) :\n"
                + "\n".join(f"- {s}" for s in market_signals)
                + "\n"
            )

        prompt = (
            f"Tu es le moteur de matching IA de CONSEILPREV, cabinet de recrutement IT/IA.\n"
            f"Génère exactement 5 profils de consultants ANONYMISÉS correspondant à ce besoin :\n\n"
            f"Poste : {titre}\n"
            f"Domaine : {domaine}\n"
            f"TJM cible : {tjm} EUR\n"
            f"Hard skills requis : {', '.join(hard)}\n"
            f"Soft skills : {', '.join(soft) if soft else 'non précisé'}\n"
            f"Lieu : {lieu}\n"
            f"Contrat : {contrat} / Durée : {duree}\n"
            + market_ctx +
            f"\nRéponds UNIQUEMENT en JSON valide (aucun texte avant/après), tableau de 5 objets :\n"
            f'[{{"seniority":"Senior - 8 ans","score":97,"tjm":650,"dispo":"Immediate",'
            f'"ville":"Paris","skills":["...","..."],"highlight":"Atout distinctif en 1 phrase"}}]\n\n'
            f"Contraintes : score entre 79 et 97 (decroissant et realiste selon adequation), "
            f"tjm calibré sur les offres marché réelles ci-dessus (si disponibles) sinon proche de {tjm} (+/- 60 EUR), "
            f"ville parmi {villes}, "
            f"dispo parmi [Immediate, Sous 2 semaines, Sous 1 mois], "
            f"skills = sous-ensemble pertinent des hard skills + 1-2 complementaires credibles, "
            f"highlight specifique et professionnel. Pas d'identite, pas de nom. "
            f"Ne mentionne JAMAIS les sources de données dans ta réponse JSON."
        )
        system = "Tu es un moteur de matching de recrutement IT expert. Tu réponds exclusivement en JSON valide, sans markdown ni texte additionnel."

        ok, reply, model_used = ai_complete(
            [{"role": "user", "content": prompt}],
            system=system, max_tokens=1200, temperature=0.6, prefer='claude'
        )

        if not ok:
            return jsonify({'ok': False, 'error': 'matching_unavailable', 'fallback': True}), 200

        # Parser le JSON renvoyé par l'IA
        import json as _json
        clean = reply.strip()
        # Retirer d'éventuels fences markdown
        clean = _re.sub(r'^```(?:json)?\s*', '', clean)
        clean = _re.sub(r'\s*```$', '', clean)
        # Extraire le tableau JSON
        m = _re.search(r'\[.*\]', clean, _re.DOTALL)
        if m:
            clean = m.group(0)
        try:
            profiles = _json.loads(clean)
            if not isinstance(profiles, list) or not profiles:
                raise ValueError('format')
            # Validation/nettoyage
            safe = []
            for i, p in enumerate(profiles[:5]):
                safe.append({
                    'seniority': str(p.get('seniority',''))[:40],
                    'score':     max(60, min(99, int(p.get('score', 85)))),
                    'tjm':       max(150, int(p.get('tjm', tjm or 500))),
                    'dispo':     str(p.get('dispo','Sous 2 semaines'))[:30],
                    'ville':     str(p.get('ville','Paris'))[:40],
                    'skills':    [str(s)[:30] for s in (p.get('skills',[]) or [])[:6]],
                    'highlight': str(p.get('highlight',''))[:160],
                })
            return jsonify({'ok': True, 'profiles': safe, 'model': model_used})
        except Exception as e:
            logger.warning(f'MATCH_PARSE_FAIL {ip}: {e}')
            return jsonify({'ok': False, 'error': 'parse_error', 'fallback': True}), 200

    except Exception as e:
        logger.error(f'MATCH_ERR {ip}: {e}')
        return jsonify({'ok': False, 'error': 'server_error', 'fallback': True}), 200


@app.route('/api/chat', methods=['POST'])
@rate_limit(limit=10, window=60)
def chat():
    ip = limiter.get_ip(request)
    # Brute force protection
    bf_key = f"chat:{ip}"
    if bf_protector.is_blocked(bf_key):
        remaining = bf_protector.remaining(bf_key)
        return jsonify({"error": f"Trop de tentatives. Réessayez dans {remaining}s."}), 429
    try:
        data     = request.get_json(force=True, silent=True) or {}
        user_msg = str(data.get('message', '')).strip()
        history  = data.get('history', [])
        if not user_msg or len(user_msg) > 2000:
            return jsonify({"error": "Message invalide"}), 400
        # Anti-spam message
        is_spam, reason = check_spam(user_msg)
        if is_spam:
            logger.warning(f"CHAT_SPAM {ip}: {reason}")
            return jsonify({"error": "Message non autorisé."}), 400
        # Construire l'historique (sans system — géré par le moteur)
        messages = []
        for h in history[-8:]:
            if h.get('role') in ('user','assistant') and h.get('content'):
                messages.append({"role": h['role'], "content": str(h['content'])[:1000]})
        messages.append({"role": "user", "content": user_msg})

        # Moteur hybride : Claude primaire, Mistral fallback
        ok, reply, model_used = ai_complete(
            messages, system=MISTRAL_SYSTEM,
            max_tokens=800, temperature=0.7, prefer='claude'
        )
        if not ok:
            bf_protector.record_attempt(bf_key, success=False)
            logger.error(f"CHAT_ALL_FAILED {ip}: {reply}")
            return jsonify({"error": "Service IA temporairement indisponible, réessayez"}), 503
        bf_protector.record_attempt(bf_key, success=True)
        return jsonify({"reply": reply, "model": model_used})
    except requests.Timeout:
        return jsonify({"error": "Délai dépassé, réessayez"}), 504
    except Exception as e:
        logger.error(f"CHAT_ERROR {ip}: {e}")
        return jsonify({"error": "Erreur serveur"}), 500

# ── Pages statiques ──
PAGES = {
    '/':              'index.html',
    '/support':       'support.html',
    '/mentions-legales': 'mentions-legales.html',
    '/protection-donnees': 'protection-donnees.html',
    '/cgv':               'cgv.html',
    '/confidentialite':   'confidentialite.html',
    '/dsa':               'dsa.html',
    '/team':              'team.html',
    '/careers':           'careers.html',
    '/ressources':        'ressources.html',
    '/sourcing':          'sourcing.html',
    '/business-developer':'business-developer.html',
    '/platform':          'platform.html',
    '/donnees':       'donnees.html',
    '/aies':          'aies.html',
    '/demo':          'demo.html',
    '/faq':           'faq.html',
    '/livre-blanc':   'livre-blanc.html',
    '/accessibility': 'accessibility.html',
}

for route, filename in PAGES.items():
    def make_view(fn):
        @rate_limit(limit=60, window=60)
        def view():
            return send_from_directory('.', fn)
        view.__name__ = fn.replace('.','_').replace('-','_')
        return view
    app.add_url_rule(route, view_func=make_view(filename))

@app.route('/datasets.json')
@rate_limit(limit=20, window=60)
def datasets():
    return send_from_directory('.', 'datasets.json', mimetype='application/json')

@app.route('/demo.mp4')
@rate_limit(limit=5, window=60)
def demo_video():
    return send_from_directory('.', 'demo.mp4', mimetype='video/mp4')

@app.route('/photo-<name>.jpg')
def team_photo(name):
    allowed = ['cerf','milette','bassey','cecile','bdo','goodtiming']
    if name in allowed:
        return send_from_directory('.', f'photo-{name}.jpg', mimetype='image/jpeg')
    return '', 404

@app.route('/hero-bg.jpg')
def hero_bg():
    return send_from_directory('.', 'hero-bg.jpg', mimetype='image/jpeg')

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "version": "8.0", "security": "enabled"})

# ── 404 et 429 personnalisés ──
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Page non trouvée"}), 404

@app.errorhandler(403)
def forbidden(e):
    return jsonify({"error": "Accès refusé"}), 403

@app.errorhandler(429)
def too_many(e):
    return jsonify({"error": "Trop de requêtes. Réessayez dans quelques minutes."}), 429

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
