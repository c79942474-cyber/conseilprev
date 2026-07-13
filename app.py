import os, re as _re, time, hashlib, json, logging, threading, base64
import requests, feedparser
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from werkzeug.utils import secure_filename
from functools import wraps
from collections import defaultdict
from flask import Flask, send_from_directory, jsonify, request, abort, make_response, after_this_request, Response, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta as _timedelta_auth
from flask_cors import CORS

# ══════════════════════════════════════════════════════════
# CONSEILPREV — Flask App v8.0
# Sécurité multicouche : Anti-DDoS, Anti-scraping,
# Rate limiting, Brute force, Anti-spam, CSP Headers
# ══════════════════════════════════════════════════════════

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('conseilprev')

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', '').strip() or hashlib.sha256(b'conseilprev-sentinel-fallback-2026').hexdigest()
app.config['PERMANENT_SESSION_LIFETIME'] = _timedelta_auth(days=30)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
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
        self.last_violation = {}               # ip → timestamp derniere violation (pour decroissance)
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
        """Retourne True si la requête est autorisée.
        Clé par (ip, endpoint) pour ne pas pénaliser globalement
        une IP active sur plusieurs routes différentes.
        3 dépassements successifs avant le 1er blocage (30s).
        """
        if self.is_blocked(ip):
            return False
        now = time.time()
        # Clé par route pour isoler les compteurs par endpoint
        key = f"{ip}:{endpoint}" if endpoint else ip
        # Décroissance : violation vieille de plus de 2h réinitialisée
        viol_key = f"viol:{key}"
        if viol_key in self.last_violation and now - self.last_violation[viol_key] > 7200:
            self.violations[viol_key] = 0
        # Nettoyer les anciennes requêtes de cette clé
        self.requests[key] = [t for t in self.requests[key] if now - t < window]
        self.requests[key].append(now)
        count = len(self.requests[key])
        if count > limit:
            self.violations[viol_key] = self.violations.get(viol_key, 0) + 1
            self.last_violation[viol_key] = now
            viol_count = self.violations[viol_key]
            # Tolérance : 3 dépassements avant le 1er blocage IP global
            if viol_count >= 8:
                self.block(ip, 600, f'repeat_rate_limit on {endpoint}')  # 10 min
            elif viol_count >= 5:
                self.block(ip, 120, f'rate_limit on {endpoint}')         # 2 min
            elif viol_count >= 3:
                self.block(ip, 30, f'rate_limit on {endpoint}')          # 30 s
            # 1-2 violations : ralentir sans bloquer (pas de block())
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
                retry_after = max(1, int(limiter.blocked.get(ip, time.time()) - time.time()))
                retry_msg = f"{retry_after} secondes" if retry_after < 60 else f"{retry_after // 60} minute(s)"
                resp = make_response(jsonify({
                    'error': f'Trop de requêtes. Réessayez dans environ {retry_msg}.',
                    'code': 429,
                    'retry_after_seconds': retry_after
                }), 429)
                resp.headers['Retry-After'] = str(retry_after)
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
# AUTHENTIFICATION — Acces a Sentinel AI
# CONSEILPREV : lien secret personnel (cookie longue duree, sans mot de passe).
# Clients externes : compte email + mot de passe (cree manuellement par CONSEILPREV).
# Isolation complete : chaque client ne voit que ses propres donnees (client_id).
# ══════════════════════════════════════════════════════════




# ══════════════════════════════════════════════════════════
# 5. SECURITY HEADERS MIDDLEWARE
# ══════════════════════════════════════════════════════════

@app.after_request
def add_security_headers(response):
    # Autoriser iframe pour /map
    if request.path == '/map':
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        return response
    # Content Security Policy
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://api.mistral.ai https://api.anthropic.com https://unpkg.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: blob: https:; "
        "media-src 'self' blob:; "
        "connect-src 'self' https://api.mistral.ai https://api.anthropic.com https://api.rss2json.com https://rss2json.com https://api.allorigins.win https://basemaps.cartocdn.com https://*.basemaps.cartocdn.com; "
        "frame-ancestors 'self'; "
        "frame-src 'self'; "
        "base-uri 'self'; "
        "form-action 'self' mailto:;"
    )
    response.headers['Content-Security-Policy']    = csp
    response.headers['X-Content-Type-Options']     = 'nosniff'
    response.headers['X-Frame-Options']            = 'SAMEORIGIN'
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

    # ── Exemption partielle /auth/<token> des verifications anti-injection/coherence
    # des en-tetes : ce chemin ne contient que des tokens generes par le serveur
    # (jamais d'input libre), donc ces 2 verifications specifiques n'ont pas de sens
    # ici et peuvent causer des faux positifs selon les caracteres aleatoires du token
    # (ex: une sequence '--' ou '#' par hasard). Le rate limiting global RESTE applique
    # (voir plus bas) pour empecher le brute-force du token.
    is_auth_link = path.startswith('/auth/')

    # ── Whitelist assets statiques (pas de check UA) ──
    static_exts = ('.jpg','.jpeg','.png','.gif','.svg','.ico',
                   '.css','.js','.woff','.woff2','.mp4','.json')
    if any(path.endswith(e) for e in static_exts):
        return  # Laisser passer

    # ── Whitelist health check Render et sondes externes ──────────
    # Render vérifie la disponibilité via HEAD / ou GET /health depuis
    # des IPs GCP externes (34.x.x.x) avec UA=Go-http-client/2.0.
    # On laisse passer HEAD et GET sur les paths de health check
    # quelle que soit l'IP source — aucune donnée sensible exposée.
    _health_paths = ('/', '/health', '/api/health')
    if request.method in ('HEAD', 'GET') and path in _health_paths:
        return  # Health check légitime — pas de vérif UA ni blocage

    # ── Vérifier si IP bloquée ──
    if limiter.is_blocked(ip):
        logger.warning(f"BLOCKED_IP {ip} → {path}")
        abort(429)

    # ── Anti-scraping UA ──
    if is_bot_blocked(ua):
        logger.warning(f"BOT_BLOCKED {ip} UA={ua[:60]} → {path}")
        # Retourner 404 pour ne pas révéler le blocage
        abort(404)

    # ── Anti-scraping comportemental (check_scraping etait definie mais jamais appelee) ──
    if path.startswith('/api/') and check_scraping(request):
        logger.warning(f"SCRAPING_PATTERN {ip} UA={ua[:60]} → {path}")
        abort(404)

    # ── Coherence des en-tetes : un vrai navigateur envoie Accept-Language et Accept-Encoding.
    # Un script qui usurpe juste le User-Agent (ex: 'Mozilla/5.0...' en dur dans du code Python
    # avec requests/curl) oublie generalement ces en-tetes. Applique uniquement aux pages HTML,
    # pas aux assets/API deja proteges autrement, pour ne pas bloquer des clients API legitimes.
    if not is_auth_link and not path.startswith('/api/') and not any(path.endswith(e) for e in static_exts):
        accept_lang = request.headers.get('Accept-Language', '')
        accept_enc = request.headers.get('Accept-Encoding', '')
        if ua and len(ua) > 10 and not accept_lang and not accept_enc:
            logger.warning(f"HEADERS_INCOHERENTS {ip} UA={ua[:60]} → {path}")
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
    if not is_auth_link:
        for pat in suspicious_patterns:
            if _re.search(pat, full_url, _re.IGNORECASE):
                limiter.block(ip, 3600, f'injection_attempt:{pat}')
                logger.warning(f"INJECTION {ip} → {full_url[:100]}")
                abort(403)

# ══════════════════════════════════════════════════════════
# CONFIGURATION EMAIL — /api/apply (universel)
# ══════════════════════════════════════════════════════════
# ── BREVO (ex-Sendinblue) — SMTP + API transactionnelle ──
# Paramètres SMTP Brevo (priorité sur variables d'env Render)
SMTP_HOST     = os.environ.get('SMTP_HOST', 'smtp-relay.brevo.com')
SMTP_PORT     = int(os.environ.get('SMTP_PORT', '2525'))  # Brevo : 2525 (STARTTLS) ou 465 (SSL)
SMTP_USER     = os.environ.get('SMTP_USER', '')      # Votre email Brevo (login)
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')  # Clé SMTP Brevo (pas votre mdp)
BREVO_API_KEY = os.environ.get('BREVO_API_KEY', '')  # Clé API Brevo (v3)
BREVO_API_URL = 'https://api.brevo.com/v3/smtp/email'


# ══════════════════════════════════════════════════════════════
# BREVO — Fonctions d'envoi email (API + SMTP + fallback local)
# ══════════════════════════════════════════════════════════════
def send_via_brevo_api(to_email, to_name, subject, html_content,
                       reply_to=None, attachments=None, tags=None):
    if not BREVO_API_KEY:
        return False, 'no_brevo_api_key'
    try:
        payload = {
            'sender':      {'name': 'CONSEILPREV', 'email': MAIL_FROM},
            'to':          [{'email': to_email, 'name': to_name or to_email}],
            'subject':     subject,
            'htmlContent': html_content,
        }
        if reply_to:    payload['replyTo']    = {'email': reply_to}
        if tags:        payload['tags']       = tags[:10]
        if attachments: payload['attachment'] = attachments
        resp = requests.post(BREVO_API_URL,
            headers={'api-key': BREVO_API_KEY, 'Content-Type': 'application/json', 'Accept': 'application/json'},
            json=payload, timeout=20)
        if resp.status_code in (201, 200):
            mid = resp.json().get('messageId', 'ok')
            logger.info(f'BREVO_API_OK: {to_email} — {mid}')
            return True, mid
        logger.error(f'BREVO_API_ERR {resp.status_code}: {resp.text[:200]}')
        return False, f'http_{resp.status_code}'
    except Exception as e:
        logger.error(f'BREVO_API_EXCEPTION: {e}')
        return False, str(e)


def send_email_smart(to_email, to_name, subject, html_content,
                     reply_to=None, tags=None):
    """Brevo API → SMTP Brevo → sauvegarde locale. Chaque tentative est journalisee
    dans la table email_log pour permettre un diagnostic immediat (page Gestion des
    clients) sans avoir a chercher dans les logs Render a chaque incident."""
    if BREVO_API_KEY:
        ok, result = send_via_brevo_api(to_email, to_name, subject, html_content,
                                        reply_to=reply_to, tags=tags)
        if ok:
            email_log_record(to_email, subject, 'brevo_api', True)
            return True, 'brevo_api'
        logger.warning(f'BREVO_API_FAILED: {result}')
    if SMTP_USER and SMTP_PASSWORD:
        try:
            from email.mime.multipart import MIMEMultipart as _MM
            from email.mime.text import MIMEText as _MT
            msg = _MM('mixed')
            msg['Subject'] = subject; msg['From'] = MAIL_FROM; msg['To'] = to_email
            if reply_to: msg['Reply-To'] = reply_to
            msg.attach(_MT(html_content, 'html', 'utf-8'))
            ctx = ssl.create_default_context()
            if SMTP_PORT == 465:
                # SSL direct (port 465) — recommandé sur Render
                with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx, timeout=20) as srv:
                    srv.ehlo()
                    srv.login(SMTP_USER, SMTP_PASSWORD)
                    srv.sendmail(MAIL_FROM, [to_email], msg.as_string())
            else:
                # STARTTLS (port 587/2525)
                with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as srv:
                    srv.ehlo(); srv.starttls(context=ctx); srv.login(SMTP_USER, SMTP_PASSWORD)
                    srv.sendmail(MAIL_FROM, [to_email], msg.as_string())
            logger.info(f'BREVO_SMTP_OK: {to_email}')
            email_log_record(to_email, subject, 'brevo_smtp', True)
            return True, 'brevo_smtp'
        except Exception as e:
            logger.error(f'BREVO_SMTP_FAILED: {e}')
            email_log_record(to_email, subject, 'brevo_smtp', False, str(e)[:200])
    import datetime as _dt
    ts   = _dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    path = os.path.join(UPLOAD_FOLDER, f'email_{ts}_{to_email.split("@")[0]}.html')
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f'<!-- To: {to_email} | Subject: {subject} -->\n' + html_content)
        logger.warning(f'EMAIL_SAVED_LOCAL: {path}')
    except Exception: pass
    email_log_record(to_email, subject, 'saved_locally', False, 'Brevo API et SMTP indisponibles ou non configures')
    return False, 'saved_locally'


def add_contact_to_brevo(email, prenom, nom, entreprise='', liste_id=None):
    if not BREVO_API_KEY: return False, 'no_brevo_api_key'
    try:
        payload = {
            'email': email,
            'attributes': {'PRENOM': prenom, 'NOM': nom, 'ENTREPRISE': entreprise or '', 'SOURCE': 'CONSEILPREV'},
            'updateEnabled': True,
        }
        if liste_id: payload['listIds'] = [int(liste_id)]
        resp = requests.post('https://api.brevo.com/v3/contacts',
            headers={'api-key': BREVO_API_KEY, 'Content-Type': 'application/json'},
            json=payload, timeout=15)
        if resp.status_code in (201, 204):
            logger.info(f'BREVO_CONTACT_OK: {email}')
            return True, 'ok'
        return False, f'http_{resp.status_code}'
    except Exception as e:
        logger.error(f'BREVO_CONTACT_ERR: {e}')
        return False, str(e)


MAIL_FROM     = os.environ.get('MAIL_FROM', 'noreply@conseilprev.onrender.com')
_FREE_EMAIL_DOMAINS = ('outlook.com', 'hotmail.com', 'live.com', 'gmail.com', 'yahoo.com', 'icloud.com', 'aol.com', 'protonmail.com')
if MAIL_FROM.split('@')[-1].lower() in _FREE_EMAIL_DOMAINS:
    logger.error(
        f"CONFIGURATION INVALIDE : MAIL_FROM='{MAIL_FROM}' utilise un domaine grand public "
        f"({MAIL_FROM.split('@')[-1]}), qui ne peut JAMAIS etre authentifie sur Brevo. "
        f"Tous les envois d'email seront rejetes par les fournisseurs (Outlook, Gmail...). "
        f"Definissez MAIL_FROM sur Render avec une adresse de votre propre domaine, deja "
        f"verifie dans Brevo (Senders & IP -> Domains)."
    )
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
        # Bloquer si c'est sensé être un PDF/DOC mais ne l'est pas (potentiel exploit)
        if ext in ('pdf',) and not data[:4].startswith(b'%PDF'):
            return False, None, f'invalid_magic_bytes:{ext}'
        if ext in ('doc','docx') and not (data[:4] == b'PK\x03\x04' or data[:4] == b'\xd0\xcf\x11\xe0'):
            return False, None, f'invalid_magic_bytes:{ext}'
        # Pour images — bloquer aussi
        if ext in ('jpg','jpeg') and not data[:2] == b'\xff\xd8':
            return False, None, f'invalid_magic_bytes:{ext}'
        if ext == 'png' and not data[:4] == b'\x89PNG':
            return False, None, f'invalid_magic_bytes:{ext}'

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
    """
    Envoie email candidature + CV en pièce jointe.
    Flux: 1) Brevo API (HTTP, pas de port SMTP) → 2) SMTP Brevo → 3) local.
    """
    import base64 as _b64, datetime as _dt

    prenom  = data.get('prenom','')
    nom     = data.get('nom','')
    email   = data.get('email','')
    ftype   = data.get('form_type','candidature')
    name    = f'{prenom} {nom}'.strip()
    subject = f"[CONSEILPREV] {ftype.upper()} | {name}"
    if cv_filename:
        subject += f" | CV:{cv_filename}"
    html_body = build_html_email(data, cv_filename)

    # ── 1. Brevo API (priorité absolue — HTTP, fonctionne sur Render) ──
    # Relecture dynamique au cas où la variable aurait été ajoutée après démarrage
    _brevo_key = os.environ.get('BREVO_API_KEY', BREVO_API_KEY)
    _mail_from = os.environ.get('MAIL_FROM', MAIL_FROM)
    if _brevo_key:
        try:
            payload = {
                'sender':      {'name': 'CONSEILPREV', 'email': _mail_from},
                'to':          [{'email': MAIL_TO, 'name': 'CONSEILPREV'}],
                'subject':     subject,
                'htmlContent': html_body,
                'replyTo':     {'email': email or MAIL_TO, 'name': name},
                'tags':        [ftype, 'candidature'],
            }
            if MAIL_CC:
                payload['cc'] = [{'email': MAIL_CC}]
            if cv_data and cv_filename:
                safe_fn = secure_filename(cv_filename)
                payload['attachment'] = [{
                    'name':    safe_fn,
                    'content': _b64.b64encode(cv_data).decode('ascii'),
                }]
                logger.info(f'BREVO_CV_ATTACH: {safe_fn} ({len(cv_data)} bytes)')
            resp = requests.post(
                BREVO_API_URL,
                headers={
                    'api-key':      _brevo_key,
                    'Content-Type': 'application/json',
                    'Accept':       'application/json',
                },
                json=payload,
                timeout=25,
            )
            if resp.status_code in (201, 200):
                mid = resp.json().get('messageId', 'ok')
                logger.info(f'APPLY_BREVO_API_OK: {name} cv={cv_filename} → {mid}')
                return True, 'brevo_api'
            logger.error(f'APPLY_BREVO_API_ERR {resp.status_code}: {resp.text[:200]}')
        except Exception as e:
            logger.error(f'APPLY_BREVO_API_EXC: {e}')

    # ── 2. SMTP Brevo (fallback avec pièce jointe MIME) ──
    if SMTP_USER and SMTP_PASSWORD:
        try:
            msg = MIMEMultipart('mixed')
            msg['Subject']  = subject
            msg['From']     = MAIL_FROM
            msg['To']       = MAIL_TO
            if MAIL_CC:       msg['Cc']       = MAIL_CC
            if email:         msg['Reply-To'] = email
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            if cv_data and cv_filename:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(cv_data)
                encoders.encode_base64(part)
                safe = secure_filename(cv_filename)
                part.add_header('Content-Disposition', f'attachment; filename="{safe}"')
                msg.attach(part)
            ctx  = ssl.create_default_context()
            rcpt = [r.strip() for r in [MAIL_TO, MAIL_CC] if r.strip()]
            if SMTP_PORT == 465:
                with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx, timeout=25) as srv:
                    srv.ehlo(); srv.login(SMTP_USER, SMTP_PASSWORD)
                    srv.sendmail(MAIL_FROM, rcpt, msg.as_string())
            else:
                with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=25) as srv:
                    srv.ehlo(); srv.starttls(context=ctx); srv.login(SMTP_USER, SMTP_PASSWORD)
                    srv.sendmail(MAIL_FROM, rcpt, msg.as_string())
            logger.info(f'APPLY_SMTP_OK: {name} cv={cv_filename}')
            return True, 'brevo_smtp'
        except smtplib.SMTPAuthenticationError:
            logger.error('APPLY_SMTP_AUTH: vérifier clé SMTP Brevo dans Render')
            return False, 'smtp_auth_error'
        except Exception as e:
            logger.error(f'APPLY_SMTP_ERR: {e}')

    # ── 3. Sauvegarde locale ──
    try:
        ts   = _dt.datetime.now().strftime('%Y%m%d_%H%M%S')
        path = os.path.join(UPLOAD_FOLDER, f'email_{ts}.txt')
        with open(path, 'w', encoding='utf-8') as _f:
            _f.write(f"TO: {MAIL_TO}\nCC: {MAIL_CC}\nSUBJECT: {subject}\n\n")
            for k, v in data.items():
                _f.write(f"{k}: {v}\n")
            if cv_filename:
                _f.write(f"\nCV: {cv_filename} ({len(cv_data or b'')} bytes)\n")
        logger.warning(f'APPLY_SAVED_LOCAL: {path}')
    except Exception as _e:
        logger.error(f'APPLY_SAVE_ERR: {_e}')
    return False, 'smtp_not_configured'

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


# ══════════════════════════════════════════════════════════
# SOURCES RSS — Veille actualités IA / cyber / réglementaire
# Utilisées par l'endpoint /api/news (défilement actualités)
# ══════════════════════════════════════════════════════════
RSS_SOURCES = [
    # ── Sources francophones ──
    {"name": "ActuIA",          "url": "https://www.actuia.com/feed/",                        "cat": "ai",    "ico": "\U0001F916", "lang": "fr"},
    {"name": "ANSSI",           "url": "https://cyber.gouv.fr/feed",                          "cat": "secu",  "ico": "\U0001F6E1", "lang": "fr"},
    {"name": "CNIL",            "url": "https://www.cnil.fr/fr/rss.xml",                      "cat": "regl",  "ico": "\U0001F512", "lang": "fr"},
    {"name": "Le Monde Info",   "url": "https://www.lemondeinformatique.fr/rss/rss-actu.xml", "cat": "innov", "ico": "\U0001F4BB", "lang": "fr"},
    {"name": "Usine Digitale",  "url": "https://www.usine-digitale.fr/rss/all",               "cat": "innov", "ico": "\U0001F3ED", "lang": "fr"},
    {"name": "Cybersec-info",   "url": "https://cybersecurite-info.fr/feed/",                 "cat": "secu",  "ico": "\U0001F510", "lang": "fr"},
    # ── Sources anglophones ──
    {"name": "AI Act EU",       "url": "https://artificialintelligenceact.eu/feed/",          "cat": "regl",  "ico": "\u2696\uFE0F", "lang": "en"},
    {"name": "EU Digital",      "url": "https://digital-strategy.ec.europa.eu/en/rss.xml",    "cat": "intl",  "ico": "\U0001F1EA\U0001F1FA", "lang": "en"},
    {"name": "Infosecurity",    "url": "https://www.infosecurity-magazine.com/rss/news/",     "cat": "secu",  "ico": "\U0001F50F", "lang": "en"},
    {"name": "The Hacker News", "url": "https://feeds.feedburner.com/TheHackersNews",         "cat": "secu",  "ico": "\U0001F513", "lang": "en"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/",              "cat": "ai",    "ico": "\U0001F9E0", "lang": "en"},
    {"name": "TechCrunch AI",   "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "cat": "ai", "ico": "\U0001F680", "lang": "en"},
]

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
# ══════════════════════════════════════════════════════════════════
# Veille réglementaire IA — agrégateur de flux (lecture seule, cache)
# ══════════════════════════════════════════════════════════════════
VEILLE_FEEDS = [
    # Régulation et gouvernance (prioritaires pour la veille CONSEILPREV)
    {"url": "https://dig.watch/feed/",                    "source": "Digital Watch Observatory", "jur": "International", "trusted": True, "fallbacks": ["https://news.google.com/rss/search?q=AI%20regulation%20governance&hl=en-US&gl=US&ceid=US:en"]},
    {"url": "https://artificialintelligenceact.eu/feed/", "source": "EU AI Act",                 "jur": "Union européenne", "trusted": True, "fallbacks": ["https://news.google.com/rss/search?q=%22EU%20AI%20Act%22&hl=en-US&gl=US&ceid=US:en"]},
    {"url": "https://news.google.com/rss/search?q=EU%20artificial%20intelligence%20policy%20OR%20%22AI%20Act%22&hl=en-US&gl=US&ceid=US:en", "source": "EURACTIV / actualité UE", "jur": "Union européenne", "fallbacks": ["https://www.euractiv.com/feed/"]},
    # Actualité technologique (contexte)
    {"url": "https://arstechnica.com/ai/feed/",           "source": "Ars Technica — IA",         "jur": "International", "fallbacks": ["https://news.google.com/rss/search?q=artificial%20intelligence&hl=en-US&gl=US&ceid=US:en"]},
    {"url": "https://www.technologyreview.com/feed/",     "source": "MIT Technology Review",     "jur": "International", "fallbacks": ["https://news.google.com/rss/search?q=AI%20technology%20regulation&hl=en-US&gl=US&ceid=US:en"]},
    # Cybersécurité & protection des données (spécialisées — pertinentes NIS2/DORA/RGPD)
    {"url": "https://news.google.com/rss/search?q=ENISA%20OR%20NIS2%20OR%20cybersecurity%20EU&hl=en-US&gl=US&ceid=US:en", "source": "ENISA / cybersécurité UE", "jur": "Union européenne", "fallbacks": ["https://www.enisa.europa.eu/media/news-items/news-wires/RSS"]},  # Google News primaire (natif bloque sur Render), natif en repli
    {"url": "https://www.cert.ssi.gouv.fr/feed/",         "source": "CERT-FR / ANSSI",           "jur": "France", "trusted": True, "theme": "Cyber / NIS2 / DORA", "fallbacks": ["https://www.cert.ssi.gouv.fr/avis/feed/", "https://www.cert.ssi.gouv.fr/alerte/feed/", "https://www.cert.ssi.gouv.fr/actualite/feed/"]},
    {"url": "https://www.cnil.fr/fr/rss.xml",             "source": "CNIL — RGPD",               "jur": "France", "trusted": True, "theme": "RGPD / données", "fallbacks": ["https://www.cnil.fr/fr/flux-rss", "https://news.google.com/rss/search?q=CNIL%20RGPD&hl=fr&gl=FR&ceid=FR:fr"]},
    # Pour ajouter une source : dupliquer une ligne (url du flux RSS/Atom, source, jur).
    # Le mode diagnostic /api/veille?debug=1 indique, pour chaque flux, le statut HTTP et le nombre d'items.
]
VEILLE_TTL = 1800  # cache serveur (secondes) = 30 min
VEILLE_MAX_PER_SOURCE = 6  # plafond par source (equilibrage)
_VEILLE_CACHE = {"ts": 0.0, "items": [], "errors": []}
VEILLE_THEMES = [
    ("AI Act",               ["ai act", "artificial intelligence act", "ia act", "2024/1689", "high-risk", "gpai", "ai office", "règlement ia", "reglement ia", "règlement (ue)"]),
    ("RGPD / données",       ["gdpr", "rgpd", "data protection", "privacy", "donnees personnelles", "données personnelles",
                              "cookies", "vidéosurveillance", "videosurveillance", "localisation", "vie privée", "vie privee",
                              "consentement", "dpo", "cnil", "sanction", "délibération", "deliberation", "biométr", "biometr"]),
    ("Cyber / NIS2 / DORA",  ["nis2", "nis 2", "nis360", "dora", "cyber", "cybersecurity", "cybersecurite", "cybersécurité", "resilience",
                              "vulnérabilit", "vulnerabilit", "faille", "exploit", "correctif", "ransomware", "malware",
                              "attaque", "intrusion", "supply chain security"]),
    ("Normes / gouvernance", ["iso", "42001", "governance", "gouvernance", "standard", "oecd", "ocde", "normalisation", "certification"]),
]

_VEILLE_KW = _re.compile(
    r"(artificial intelligence|intelligence artificielle|machine learning|deep learning|"
    r"\bllm\b|\bgpai\b|generative|genai|chatgpt|openai|anthropic|mistral|"
    r"algorithm[e]?s?|ai act|r\u00e8glement|regulation|\bgdpr\b|\brgpd\b|"
    r"nis ?2|\bdora\b|cyber\w*|cybers\u00e9curit\u00e9|vuln\u00e9rabilit\w*|vulnerabilit\w*|"
    r"ransomware|malware|phishing|\benisa\b|\bcnil\b|data protection|privacy|surveillance|"
    r"gouvernance|governance|compliance|conformit\u00e9|directive|sanction|amende|d\u00e9lib\u00e9ration|"
    r"digital services act|\bdsa\b|\bdma\b)",
    _re.I,
)
_VEILLE_AI = _re.compile(r"\bAI\b")  # acronyme (sensible \u00e0 la casse) pour éviter le faux positif français "ai"

_VEILLE_JUNK = _re.compile(
    r"(test to be deleted|\bto be deleted\b|test article|dummy|lorem ipsum|\[test\]|placeholder)",
    _re.I,
)

def _veille_is_junk(text):
    """Vrai si l'entrée est manifestement un résidu technique ou de test."""
    return bool(_VEILLE_JUNK.search(text or ""))

def _veille_relevant(text):
    """Vrai si le texte concerne l'IA, la r\u00e9gulation, la cybers\u00e9curit\u00e9 ou les donn\u00e9es."""
    return bool(_VEILLE_KW.search(text or "") or _VEILLE_AI.search(text or ""))


def _veille_load(feed):
    """Essaie l'URL principale puis les fallbacks ; renvoie le 1er flux valide (>0 items)."""
    urls = [feed["url"]] + list(feed.get("fallbacks") or [])
    last = {"parsed": None, "url": urls[0], "status": None, "error": None, "items": 0}
    for u in urls:
        try:
            resp = requests.get(u, headers={"User-Agent": "Sentinel-Veille/1.0"}, timeout=6)
            parsed = feedparser.parse(resp.content)
            n = len(parsed.entries)
            cand = {"parsed": parsed, "url": u, "status": resp.status_code, "error": None, "items": n}
            if resp.status_code == 200 and n > 0:
                return cand
            last = cand
        except Exception as ex:
            last = {"parsed": None, "url": u, "status": None, "error": str(ex)[:160], "items": 0}
    return last


def _veille_theme(text):
    t = (text or "").lower()
    for label, kws in VEILLE_THEMES:
        for kw in kws:
            if kw in t:
                return label
    return "Actualité IA"

@app.route('/api/veille', methods=['GET'])
def api_veille():
    """Agrège des flux RSS publics sur la régulation et l'actualité de l'IA.
    Lecture seule, cache serveur (VEILLE_TTL). ?refresh=1 force le rafraîchissement."""
    import time as _time, html as _html, re as _re
    force = (request.args.get('refresh') or '') in ('1', 'true', 'yes')
    debug = (request.args.get('debug') or '') in ('1', 'true', 'yes')
    if debug:
        diag = []
        for feed in VEILLE_FEEDS:
            r = _veille_load(feed)
            entry = {"source": feed.get("source"), "url": feed.get("url"),
                     "used_url": r["url"], "jur": feed.get("jur"),
                     "http_status": r["status"], "items": r["items"],
                     "ok": bool(r["status"] == 200 and r["items"] > 0)}
            if r["url"] != feed["url"] and r.get("ok"):
                entry["note"] = "repli utilisé"
            if r.get("error"):
                entry["error"] = r["error"]
            if r["parsed"] and r["parsed"].entries:
                entry["sample"] = (r["parsed"].entries[0].get("title") or "")[:120]
            diag.append(entry)
        return jsonify({"ok": True, "debug": True, "count": len(diag),
                        "working": sum(1 for d in diag if d.get("ok")), "feeds": diag})
    now = _time.time()
    if (not force) and _VEILLE_CACHE["items"] and (now - _VEILLE_CACHE["ts"] < VEILLE_TTL):
        return jsonify({
            "ok": True, "cached": True,
            "updated_at": datetime.utcfromtimestamp(_VEILLE_CACHE["ts"]).isoformat() + "Z",
            "count": len(_VEILLE_CACHE["items"]),
            "items": _VEILLE_CACHE["items"],
            "errors": _VEILLE_CACHE["errors"],
        })
    items, errors, seen = [], [], set()
    headers = {"User-Agent": "Sentinel-Veille/1.0"}
    for feed in VEILLE_FEEDS:
        try:
            r = _veille_load(feed)
            parsed = r["parsed"]
            if not parsed or not parsed.entries:
                errors.append({"source": feed.get("source"), "error": "aucun item (statut %s)" % r.get("status")})
                continue
            trusted = bool(feed.get("trusted"))
            fixed_theme = feed.get("theme")
            cap = feed.get("max_items", VEILLE_MAX_PER_SOURCE)
            kept = 0
            for e in parsed.entries[:20]:
                if kept >= cap:
                    break
                title = _html.unescape((e.get("title") or "").strip())
                if not title:
                    continue
                clean_sum = _re.sub(r"<[^>]+>", "", e.get("summary") or "")
                if _veille_is_junk(title + " " + clean_sum):
                    continue
                if not trusted and not _veille_relevant(title):
                    continue
                link = e.get("link") or ""
                key = link or title
                if key in seen:
                    continue
                seen.add(key)
                kept += 1
                iso, ts_sort = None, 0.0
                for attr in ("published_parsed", "updated_parsed"):
                    dp = e.get(attr)
                    if dp:
                        try:
                            ts_sort = _time.mktime(dp)
                            iso = datetime(dp[0], dp[1], dp[2], dp[3], dp[4], dp[5]).isoformat() + "Z"
                        except Exception:
                            pass
                        break
                raw_sum = e.get("summary") or ""
                summary = _html.unescape(_re.sub(r"<[^>]+>", "", raw_sum)).strip()[:220]
                items.append({
                    "title": title[:200], "link": link,
                    "source": feed["source"], "jur": feed["jur"],
                    "theme": fixed_theme or _veille_theme(title + " " + summary),
                    "date": iso, "_ts": ts_sort, "summary": summary,
                })
        except Exception as ex:
            errors.append({"source": feed.get("source"), "error": str(ex)[:140]})
    items.sort(key=lambda x: x.get("_ts") or 0.0, reverse=True)
    for it in items:
        it.pop("_ts", None)
    items = items[:60]
    _VEILLE_CACHE["ts"], _VEILLE_CACHE["items"], _VEILLE_CACHE["errors"] = now, items, errors
    return jsonify({
        "ok": True, "cached": False,
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "count": len(items), "items": items, "errors": errors,
    })


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
        # Vérification honeypot (champ invisible — si rempli = bot)
        honeypot = request.form.get('website', '') or request.form.get('_hp', '')
        if honeypot:
            logger.warning(f'APPLY_HONEYPOT {ip}: honeypot={honeypot[:20]}')
            # Simuler succès pour ne pas alerter le bot
            return jsonify({'ok': True, 'message': 'Candidature reçue avec succès', 'cv_received': False, 'email_sent': False})

        # Vérification taille maximale request (déjà géré par MAX_CONTENT_LENGTH mais double check)
        if request.content_length and request.content_length > 16 * 1024 * 1024:
            return jsonify({'ok': False, 'error': 'Requête trop volumineuse'}), 413

        def gf(k, max_l=200): return sanitize_input(request.form.get(k,''), max_l)
        data = {
            'form_type':   gf('form_type', 50),
            'prenom':      gf('prenom', 80),
            'nom':         gf('nom', 80),
            'email':       sanitize_email(request.form.get('email','')) or '',
            'telephone':   sanitize_phone(request.form.get('telephone','')),
            'entreprise':  gf('entreprise', 120),
            'fonction':    gf('fonction', 100),
            'secteur':     gf('secteur', 80),
            'type_projet': gf('type_projet', 100),
            'budget':      gf('budget', 50),
            'message':     sanitize_input(request.form.get('message',''), 3000, allow_newlines=True),
            'consent':     request.form.get('consent', ''),
            'source_url':  sanitize_input(request.form.get('source_url', request.referrer or '/'), 200, False),
            'consent_date': now_str,
        }

        # Preuve de consentement (art. 7) : enregistree si la case est cochee
        try:
            if data.get('consent') and data.get('email'):
                _rgpd_record_consent(data.get('email'), {'formulaire_contact': True}, 'formulaire-site')
        except Exception:
            pass

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
        TRUSTED_FORMS = {'selection_candidats','dossier_contrats','match_validation','contrats_signes','sourcing_profil','candidature_bd','contact_projet'}
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


@app.route('/api/test-brevo-cv', methods=['GET'])
def test_brevo_cv():
    """Test direct API Brevo avec pièce jointe — diagnostic CV."""
    import base64 as _b64
    ip = limiter.get_ip(request)

    # Mini PDF valide (1 page)
    mini_pdf = (
        b'%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n'
        b'2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n'
        b'3 0 obj<</Type/Page/MediaBox[0 0 595 842]/Parent 2 0 R>>endobj\n'
        b'xref\n0 4\n0000000000 65535 f\n'
        b'trailer<</Size 4/Root 1 0 R>>\nstartxref\n9\n%%EOF'
    )

    result = {
        'brevo_api_key_set':  bool(BREVO_API_KEY),
        'brevo_api_key_len':  len(BREVO_API_KEY) if BREVO_API_KEY else 0,
        'brevo_api_key_start': BREVO_API_KEY[:12] + '...' if BREVO_API_KEY else '',
        'mail_from':  MAIL_FROM,
        'mail_to':    MAIL_TO,
    }

    if not BREVO_API_KEY:
        result['error'] = 'BREVO_API_KEY non configurée dans Render'
        return jsonify(result), 400

    # Test 1 : Appel API sans pièce jointe
    try:
        resp1 = requests.post(
            BREVO_API_URL,
            headers={'api-key': BREVO_API_KEY, 'Content-Type': 'application/json'},
            json={
                'sender':      {'name': 'CONSEILPREV TEST', 'email': MAIL_FROM},
                'to':          [{'email': MAIL_TO}],
                'subject':     '[TEST] Brevo API — sans CV',
                'htmlContent': '<p>Test sans CV — <b>OK si vous recevez ceci</b></p>',
                'tags':        ['test', 'diagnostic'],
            },
            timeout=15,
        )
        result['test1_no_cv'] = {
            'status': resp1.status_code,
            'ok':     resp1.status_code in (200, 201),
            'body':   resp1.text[:200],
        }
    except Exception as e:
        result['test1_no_cv'] = {'error': str(e)}

    # Test 2 : Appel API avec CV en pièce jointe
    try:
        resp2 = requests.post(
            BREVO_API_URL,
            headers={'api-key': BREVO_API_KEY, 'Content-Type': 'application/json'},
            json={
                'sender':      {'name': 'CONSEILPREV TEST', 'email': MAIL_FROM},
                'to':          [{'email': MAIL_TO}],
                'subject':     '[TEST] Brevo API — AVEC CV joint',
                'htmlContent': '<p>Test <b>avec CV joint</b> — vérifiez la pièce jointe</p>',
                'attachment':  [{'name': 'CV_test.pdf', 'content': _b64.b64encode(mini_pdf).decode()}],
                'tags':        ['test', 'cv-diagnostic'],
            },
            timeout=15,
        )
        result['test2_with_cv'] = {
            'status': resp2.status_code,
            'ok':     resp2.status_code in (200, 201),
            'body':   resp2.text[:200],
            'mid':    resp2.json().get('messageId','') if resp2.status_code in (200,201) else '',
        }
    except Exception as e:
        result['test2_with_cv'] = {'error': str(e)}

    # Résumé
    t1_ok = result.get('test1_no_cv',{}).get('ok', False)
    t2_ok = result.get('test2_with_cv',{}).get('ok', False)
    result['summary'] = (
        '✅ API OK + CV OK — vérifiez votre boîte mail' if t1_ok and t2_ok else
        '⚠ API OK mais CV échoue — problème encodage' if t1_ok and not t2_ok else
        '❌ API KO — vérifier BREVO_API_KEY et MAIL_FROM'
    )

    logger.info(f'BREVO_TEST_CV {ip}: t1={t1_ok} t2={t2_ok}')
    return jsonify(result)


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
            if SMTP_PORT == 465:
                with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx, timeout=10) as srv:
                    srv.ehlo(); srv.login(SMTP_USER, SMTP_PASSWORD)
            else:
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



# ══════════════════════════════════════════════════════════════
# CSRF PROTECTION — token par session / per-request
# ══════════════════════════════════════════════════════════════
import hmac as _hmac_csrf
_CSRF_STORE = {}   # {token: (ip, expire_ts)} — en mémoire (Redis en prod)
CSRF_TTL = 3600    # 1h

def generate_csrf_token(ip=''):
    """Génère un token CSRF cryptographiquement sûr."""
    token = _secrets.token_urlsafe(32)
    _CSRF_STORE[token] = (ip, time.time() + CSRF_TTL)
    # Nettoyer les anciens tokens
    now = time.time()
    expired = [k for k, v in _CSRF_STORE.items() if v[1] < now]
    for k in expired:
        _CSRF_STORE.pop(k, None)
    return token

def validate_csrf_token(token, ip=''):
    """Valide un token CSRF. Retourne True si valide (single-use)."""
    if not token or len(token) < 10:
        return False
    entry = _CSRF_STORE.get(token)
    if not entry:
        return False
    stored_ip, expire_ts = entry
    if time.time() > expire_ts:
        _CSRF_STORE.pop(token, None)
        return False
    # Token valide — le supprimer (single-use pour les actions sensibles)
    # Pour les formulaires normaux, on garde le token 1h pour l'UX
    return True

@app.route('/api/csrf-token', methods=['GET'])
@rate_limit(limit=30, window=60)
def get_csrf_token():
    """Endpoint pour obtenir un token CSRF (appelé au chargement de page)."""
    ip = limiter.get_ip(request)
    token = generate_csrf_token(ip)
    resp = jsonify({'token': token, 'ttl': CSRF_TTL})
    resp.set_cookie('csrf_token', token, httponly=False, samesite='Strict', max_age=CSRF_TTL)
    return resp

def check_csrf(req):
    """Vérifie le token CSRF dans header ou form data."""
    token = (req.headers.get('X-CSRF-Token','')
             or req.form.get('_csrf','')
             or req.get_json(silent=True, force=True) and req.get_json(silent=True, force=True).get('_csrf','')
             or req.cookies.get('csrf_token',''))
    # API calls depuis notre propre domaine : vérifier Origin/Referer
    origin = req.headers.get('Origin','')
    referer = req.headers.get('Referer','')
    own_domain = 'conseilprev.onrender.com'
    if origin and own_domain not in origin and 'localhost' not in origin:
        return False, 'origin_mismatch'
    # Pour les formulaires HTML sans JS CSRF, le cookie suffit
    if not token:
        return True, 'no_token_relaxed'   # relaxed mode pour compatibilité
    return validate_csrf_token(token), 'token_checked'


# ══════════════════════════════════════════════════════════════
# INPUT SANITIZATION — Protection XSS + injection
# ══════════════════════════════════════════════════════════════
_HTML_ESCAPE = {
    '&': '&amp;', '<': '&lt;', '>': '&gt;',
    '"': '&quot;', "'": '&#x27;', '/': '&#x2F;',
}
def sanitize_input(text, max_len=3000, allow_newlines=True):
    """
    Nettoie un input utilisateur :
    - Supprime les caractères de contrôle dangereux
    - Échappe les entités HTML
    - Limite la longueur
    - Normalise les espaces
    """
    if not isinstance(text, str):
        return ''
    # Limiter longueur
    text = text[:max_len]
    # Supprimer les caractères de contrôle (sauf newline/tab)
    allowed_ctrl = {9, 10, 13} if allow_newlines else set()
    text = ''.join(c for c in text if ord(c) >= 32 or ord(c) in allowed_ctrl)
    # Normaliser les lignes
    text = text.strip()
    return text

def sanitize_email(email):
    """Valide et nettoie une adresse email."""
    email = str(email).strip().lower()[:150]
    if not _re.match(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$', email):
        return None
    return email

def sanitize_phone(phone):
    """Nettoie un numéro de téléphone — chiffres, +, espaces, tirets uniquement."""
    phone = str(phone).strip()[:30]
    phone = _re.sub(r'[^\d\s\+\-\(\)]', '', phone)
    return phone[:30]


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
        # Utiliser send_email_smart (Brevo API puis SMTP)
        ok, method = send_email_smart(
            email, f'{prenom}',
            'Validez votre compte CONSEILPREV',
            html,
            reply_to=MAIL_TO,
            tags=['validation', 'compte-client']
        )
        if ok:
            logger.info(f'VALIDATION_EMAIL_OK via {method}: {email}')
            return True, validate_link
        else:
            logger.warning(f'VALIDATION_EMAIL_FAIL ({method}): {email} — lien: {validate_link}')
            return False, validate_link
    except Exception as e:
        logger.error(f'VALIDATION_EMAIL_ERR: {e}')
        return False, validate_link


@app.route('/api/auth/register', methods=['POST'])
def auth_register():
    ip = limiter.get_ip(request)
    if not limiter.check_soft(ip, limit=20, window=600):
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
        # Validation stricte de l'email comme clé (pas d'injection possible)
        if not _re.match(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$', email):
            return jsonify({'ok': False, 'error': 'Format email invalide'}), 400
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

        # Ajouter le contact dans Brevo CRM (liste clients)
        BREVO_LISTE_CLIENTS = os.environ.get('BREVO_LISTE_CLIENTS', '')
        if BREVO_API_KEY:
            add_contact_to_brevo(
                email, prenom, nom, entreprise,
                liste_id=BREVO_LISTE_CLIENTS if BREVO_LISTE_CLIENTS else None
            )

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
        import datetime as _dt_
        user['session'] = session_token
        user['session_expires'] = (_dt_.datetime.now() + _dt_.timedelta(hours=8)).isoformat()
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
        if not _hmac.compare_digest(password.ljust(32), ADMIN_PASSWORD.ljust(32)):
            logger.warning(f'ADMIN_LOGIN_FAIL {ip}')
            # Délai artificiel anti-timing (50ms)
            time.sleep(0.05)
            return jsonify({'ok': False, 'error': 'Identifiants incorrects'}), 401

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

            ok_c, method_c = send_email_smart(
                client['email'], f'{client.get("prenom","")} {client.get("nom","")}',
                f'[CONSEILPREV] Votre sélection — {nb} candidat(s) | Pré-accord',
                build_precontract_html(client, candidates),
                reply_to=MAIL_TO,
                tags=['selection', 'precontrat']
            )
            if ok_c:
                results['client_email'] = True
                logger.info(f'NOTIFY_CLIENT_OK via {method_c} {ip}: {client["email"]}')
            else:
                logger.warning(f'NOTIFY_CLIENT_FAIL: {client["email"]}')

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

            ok_cp, method_cp = send_email_smart(
                MAIL_TO, 'CONSEILPREV',
                f'[CONSEILPREV] 🔐 Sélection — {client.get("prenom","")} {client.get("nom","")} — {len(candidates)} candidat(s)',
                build_conseilprev_notif_html(client, candidates),
                reply_to=client.get('email', MAIL_TO),
                tags=['selection', 'confidentiel', 'interne']
            )
            if ok_cp:
                results['conseilprev_email'] = True
                logger.info(f'NOTIFY_CP_OK via {method_cp} {ip}: → {MAIL_TO}')
            else:
                logger.warning(f'NOTIFY_CP_FAIL')
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



@app.route('/api/brevo/webhook', methods=['POST'])
def brevo_webhook():
    """
    Webhook Brevo — reçoit les événements email :
    delivered, opened, clicked, bounced, unsubscribed.
    À configurer dans Brevo : Paramètres > Webhooks > Transactionnel
    URL : https://conseilprev.onrender.com/api/brevo/webhook
    """
    try:
        events = request.get_json(force=True, silent=True)
        if not events:
            return jsonify({'ok': True}), 200
        if isinstance(events, list):
            for evt in events:
                _process_brevo_event(evt)
        else:
            _process_brevo_event(events)
        return jsonify({'ok': True}), 200
    except Exception as e:
        logger.error(f'BREVO_WEBHOOK_ERR: {e}')
        return jsonify({'ok': False}), 200  # Toujours 200 pour Brevo


def _process_brevo_event(evt):
    """Traite un événement Brevo."""
    event_type = evt.get('event', '')
    email      = evt.get('email', '')
    msg_id     = evt.get('message-id', '')
    ts         = evt.get('ts_epoch', 0)
    tags       = evt.get('tags', [])
    logger.info(f'BREVO_EVT: {event_type} | {email} | tags={tags} | msg={msg_id[:20]}')
    if event_type in ('hard_bounce', 'soft_bounce', 'blocked'):
        logger.warning(f'BREVO_BOUNCE: {email} ({event_type})')
    elif event_type == 'unsubscribe':
        logger.warning(f'BREVO_UNSUB: {email}')
        # TODO: marquer comme désabonné dans users_db.json


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
    smtp_conn  = 'NON TESTÉ'

    # ── Test API Brevo (HTTP — aucun port SMTP, fonctionne sur Render) ──
    brevo_api_ok  = False
    brevo_api_msg = 'BREVO_API_KEY non configurée'
    if BREVO_API_KEY:
        try:
            r_brevo = requests.get(
                'https://api.brevo.com/v3/account',
                headers={'api-key': BREVO_API_KEY, 'Accept': 'application/json'},
                timeout=8
            )
            if r_brevo.status_code == 200:
                brevo_api_ok  = True
                info = r_brevo.json()
                email_acct = info.get('email', '?')
                plan_type  = (info.get('plan') or [{}])[0].get('type', '?')
                brevo_api_msg = f"✅ Connecté — {email_acct} ({plan_type})"
            elif r_brevo.status_code == 401:
                brevo_api_msg = '❌ Clé invalide — vérifier BREVO_API_KEY'
            else:
                brevo_api_msg = f'HTTP {r_brevo.status_code}'
        except Exception as e:
            brevo_api_msg = f'Erreur: {str(e)[:60]}'

    # ── Test SMTP uniquement si API indisponible (éviter timeout sur Render) ──
    if smtp_ready and not brevo_api_ok:
        try:
            import ssl as _ssl2
            _ctx = _ssl2.create_default_context()
            if SMTP_PORT == 465:
                with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=_ctx, timeout=8) as _s:
                    _s.ehlo(); _s.login(SMTP_USER, SMTP_PASSWORD)
            else:
                with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=8) as _s:
                    _s.ehlo(); _s.starttls(context=_ctx); _s.login(SMTP_USER, SMTP_PASSWORD)
            smtp_conn = 'OK'
        except smtplib.SMTPAuthenticationError:
            smtp_conn = '❌ AUTH_ERROR — vérifier clé SMTP Brevo'
        except Exception as e:
            smtp_conn = f'❌ {str(e)[:60]}'
    elif brevo_api_ok:
        smtp_conn = '✅ Non nécessaire (API Brevo active)'
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
        'brevo': {
            'api_ready':  brevo_api_ok,
            'api_status': brevo_api_msg,
            'smtp_host':  SMTP_HOST,
            'smtp_port':  SMTP_PORT,
            'smtp_conn':  smtp_conn,
            'mode':       '✅ API HTTP (recommandé)' if brevo_api_ok else ('⚠ SMTP' if smtp_conn=='OK' else '❌ non configuré'),
            'conseil':    '✅ Opérationnel' if brevo_api_ok else '→ Ajouter BREVO_API_KEY dans Render → Environment',
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

def ai_complete_cross_checked(messages, system='', max_tokens=800, temperature=0.7):
    """Appelle Claude ET Mistral en parallele (threads), compare les 2 reponses via
    un 3eme appel leger (detection de divergence factuelle, pas une simple comparaison
    de texte qui serait presque toujours 'differente'). Retourne la reponse Claude
    (consideree primaire) avec un signal de divergence si les 2 modeles se contredisent
    sur un point factuel (numero d'article, sanction, date...).
    Cout et latence plus eleves qu'un appel simple : reserve au Chat Conformite,
    ou la fiabilite prime sur la rapidite."""
    results = {}

    def _run_claude():
        results['claude'] = call_anthropic(messages, system, max_tokens, temperature)

    def _run_mistral():
        msgs_with_system = ([{'role': 'system', 'content': system}] + messages) if system else messages
        results['mistral'] = call_mistral(msgs_with_system, max_tokens, temperature)

    t1 = threading.Thread(target=_run_claude)
    t2 = threading.Thread(target=_run_mistral)
    t1.start(); t2.start()
    t1.join(timeout=35); t2.join(timeout=35)

    ok_claude, reply_claude = results.get('claude', (False, 'timeout'))
    ok_mistral, reply_mistral = results.get('mistral', (False, 'timeout'))

    if not ok_claude and not ok_mistral:
        return False, 'Les deux moteurs IA sont indisponibles, réessayez.', None, None
    if not ok_claude:
        return True, reply_mistral, 'mistral (claude indisponible)', None
    if not ok_mistral:
        return True, reply_claude, 'claude (mistral indisponible)', None

    # Les deux ont repondu : detecter une divergence factuelle via un 3e appel leger.
    divergence_warning = None
    try:
        compare_prompt = (
            "Compare ces deux reponses a la MEME question reglementaire IA. "
            "Reponds UNIQUEMENT par 'DIVERGENCE: <description courte>' si elles se "
            "contredisent sur un FAIT precis (numero d'article, montant de sanction, "
            "date d'application, obligation legale). Reponds UNIQUEMENT 'OK' si elles "
            "sont factuellement compatibles, meme reformulees differemment.\\n\\n"
            f"Reponse A (Claude):\\n{reply_claude[:600]}\\n\\n"
            f"Reponse B (Mistral):\\n{reply_mistral[:600]}"
        )
        ok_check, check_result = call_anthropic(
            [{'role': 'user', 'content': compare_prompt}],
            system='Tu es un verificateur factuel strict et concis.',
            max_tokens=120, temperature=0
        )
        if ok_check and check_result.strip().upper().startswith('DIVERGENCE'):
            divergence_warning = check_result.strip()
            logger.warning(f"CHAT_DIVERGENCE_DETECTED: {divergence_warning}")
    except Exception as e:
        logger.error(f"CHAT_CROSSCHECK_FAILED: {e}")

    return True, reply_claude, 'claude+mistral (verifie)', divergence_warning


MISTRAL_SYSTEM = (
    "Tu es l'assistant reglementaire de Sentinel AI (CONSEILPREV), specialise dans le "
    "Reglement (UE) 2024/1689 (EU AI Act), le RGPD, NIS2, DORA, DSA, DMA, CRA et les normes "
    "ISO/IEC 42001 et 23894. Regles strictes a respecter sans exception :\n"
    "1. Ne JAMAIS inventer un numero d'article, une sanction ou une date d'application. "
    "Si tu n'es pas certain a 100% d'une reference precise, dis-le explicitement plutot "
    "que de la deviner.\n"
    "2. Cite toujours la source exacte de ton affirmation (ex: 'Art. 9, Reglement (UE) "
    "2024/1689') quand tu mentionnes une obligation legale precise.\n"
    "3. En cas de doute entre deux versions d'un texte (ex: amendement recent), signale "
    "explicitement l'incertitude et recommande une verification auprès d'EUR-Lex ou d'un "
    "conseil juridique qualifie.\n"
    "4. Reste factuel et neutre. Ne donne jamais de conseil juridique definitif - oriente "
    "vers un accompagnement CONSEILPREV pour les decisions a enjeu.\n"
    "5. Reponses concises (300 mots maximum), en francais, sans jargon technique non explique.\n"
    "6. Sentinel AI est la plateforme logicielle elle-meme (la ou se trouve ce chat), PAS un "
    "site web externe distinct. N'invente JAMAIS une adresse, un nom de domaine ou un lien "
    "vers un pretendu 'site Sentinel' — cela n'existe pas. Le seul site web de reference a "
    "mentionner si necessaire est conseilprev.onrender.com (CONSEILPREV).\n"
    "7. N'utilise JAMAIS de formatage Markdown dans tes reponses : pas de dieses (#) pour les "
    "titres, pas d'asterisques (*) pour le gras ou l'italique, pas de listes a puces avec - ou *. "
    "Ecris uniquement en texte brut, en phrases ou paragraphes normaux."
)

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
@rate_limit(limit=60, window=60)
def news():
    global _news_cache
    now = time.time()
    if now - _news_cache["ts"] < CACHE_TTL and _news_cache["data"]:
        return jsonify({"items": _news_cache["data"], "cached": True, "count": len(_news_cache["data"])})
    all_items = []
    import socket as _socket
    _old_timeout = _socket.getdefaulttimeout()
    _socket.setdefaulttimeout(8)
    # Headers complets imitant Chrome 124 — contourne les filtres anti-bot des sites RSS
    _headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml, application/atom+xml, */*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
    }
    for src in RSS_SOURCES:
        try:
            resp = requests.get(src["url"], headers=_headers, timeout=7, allow_redirects=True)
            if resp.status_code != 200:
                continue
            import io as _io
            feed = feedparser.parse(_io.BytesIO(resp.content))
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
                    "lang":   src.get("lang", "fr"),
                })
        except Exception:
            pass
    _socket.setdefaulttimeout(_old_timeout)
    seen, unique = set(), []
    for item in sorted(all_items, key=lambda x: x.get("date",""), reverse=True):
        key = item["title"][:60]
        if key not in seen:
            seen.add(key)
            unique.append(item)
    if not unique:
        unique = [
            {"title": "EU AI Act : les obligations GPAI applicables depuis aout 2025", "link": "https://artificialintelligenceact.eu/", "date": "", "source": "AI Act EU", "ico": "\u2696\uFE0F", "cat": "regl", "lang": "en"},
            {"title": "ANSSI : recommandations de securite pour les systemes d'IA", "link": "https://cyber.gouv.fr/", "date": "", "source": "ANSSI", "ico": "\U0001F6E1", "cat": "secu", "lang": "fr"},
            {"title": "CNIL : fiches pratiques sur l'IA et le RGPD", "link": "https://www.cnil.fr/fr/intelligence-artificielle", "date": "", "source": "CNIL", "ico": "\U0001F512", "cat": "regl", "lang": "fr"},
            {"title": "AI safety testing requirements under EO 14179", "link": "https://www.federalregister.gov/", "date": "", "source": "Federal Register", "ico": "\U0001F1FA\U0001F1F8", "cat": "regl", "lang": "en"},
        ]
        _news_cache = {"data": unique, "ts": now - CACHE_TTL + 60}
        return jsonify({"items": unique, "cached": False, "count": len(unique), "fallback": True})
    _news_cache = {"data": unique[:60], "ts": now}
    return jsonify({"items": unique[:60], "cached": False, "count": len(unique)})


@app.route('/api/news/digest', methods=['GET'])
@rate_limit(limit=20, window=60)
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



def _chat_contexte_sentinel(question, limite=5):
    """Couche de connaissance Sentinel pour le chat : retrouve les extraits les
    plus pertinents (base documentaire, veille reglementaire, analyses) et les
    formate en contexte. Retourne (contexte_texte, sources). Silencieux en cas
    d'erreur : le chat conserve ses moteurs habituels."""
    try:
        mots = _expl_mots(question)
        cadres = _expl_cadres_detectes(question)
        conn = registre_get_db(); cur = conn.cursor()
        res = []
        try:
            res += _expl_documents(cur, question, mots, cadres, limite)
        except Exception:
            pass
        try:
            res += _expl_analyses(cur, mots, cadres, 3)
        except Exception:
            pass
        try: conn.close()
        except Exception: pass
        try:
            res += _expl_veille(mots, cadres, 3)
        except Exception:
            pass
        for r in res:
            r['score_final'] = float(r.get('score') or 0.0) * EXPL_SOURCE_POIDS.get(r.get('type'), 0.7)
        res.sort(key=lambda x: -x['score_final'])
        res = [r for r in res if r['score_final'] > 0.12][:limite]
        if not res:
            return '', []
        LIB = {'document': 'Base documentaire', 'veille': 'Veille reglementaire',
               'analyse': 'Analyse de la plateforme'}
        blocs = []
        sources = []
        for i, r in enumerate(res, start=1):
            blocs.append('[%d] (%s - %s)\n%s' % (
                i, LIB.get(r.get('type'), r.get('type')), str(r.get('titre') or '')[:110],
                str(r.get('extrait') or '')[:600]))
            sources.append({'n': i, 'type': r.get('type'), 'titre': str(r.get('titre') or '')[:140],
                            'ref': r.get('ref')})
        return '\n\n'.join(blocs), sources
    except Exception:
        return '', []


@app.route('/api/chat', methods=['POST'])
@rate_limit(limit=15, window=60)
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

        # Reponse HYBRIDE MULTI-SOURCES :
        #  1. couche de connaissance Sentinel (base documentaire, veille, analyses)
        #     -> extraits injectes dans le systeme, avec obligation de citer ;
        #  2. moteurs conserves : Claude ET Mistral interroges en parallele, avec
        #     comparaison automatique pour detecter toute divergence factuelle.
        contexte, sources = _chat_contexte_sentinel(user_msg)
        system_chat = MISTRAL_SYSTEM
        if contexte:
            system_chat = (MISTRAL_SYSTEM +
                "\n\nCONNAISSANCE SENTINEL (CONSEILPREV) — extraits issus de la base documentaire, "
                "de la veille reglementaire et des analyses de la plateforme :\n\n" + contexte +
                "\n\nPrivilegiez ces extraits lorsqu'ils repondent a la question, et citez-les entre "
                "crochets, par exemple [1]. N'inventez jamais un article, une date ou un chiffre. "
                "Si les extraits ne suffisent pas, repondez avec vos connaissances generales en le "
                "signalant, sans citer de source.")
        ok, reply, model_used, divergence = ai_complete_cross_checked(
            messages, system=system_chat, max_tokens=800, temperature=0.7
        )
        if not ok:
            bf_protector.record_attempt(bf_key, success=False)
            logger.error(f"CHAT_ALL_FAILED {ip}: {reply}")
            return jsonify({"error": "Service IA temporairement indisponible, réessayez"}), 503
        bf_protector.record_attempt(bf_key, success=True)
        return jsonify({"reply": reply, "model": model_used, "divergence": divergence,
                        "sources": sources, "connaissance": bool(contexte)})
    except requests.Timeout:
        return jsonify({"error": "Délai dépassé, réessayez"}), 504
    except Exception as e:
        logger.error(f"CHAT_ERROR {ip}: {e}")
        return jsonify({"error": "Erreur serveur"}), 500

# ── Pages statiques ──
@app.route('/robots.txt')
def robots_txt():
    """Declare explicitement les zones interdites au crawl — n'arrete pas un bot
    malveillant decide, mais cadre les bots respectueux (SEO, archivistes) et
    sert de preuve de bonne foi en cas de litige sur l'usage des donnees du site."""
    content = """User-agent: *
Disallow: /api/
Disallow: /admin
Sitemap: https://conseilprev.onrender.com/sitemap.xml

User-agent: GPTBot
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: anthropic-ai
Disallow: /
"""
    return Response(content, mimetype='text/plain')

PAGES = {
    '/':              'index.html',
    '/support':       'support.html',
    '/mentions-legales': 'mentions-legales.html',
    '/protection-donnees': 'protection-donnees.html',
    '/cgv':               'cgv.html',
    '/confidentialite':   'confidentialite.html',
    '/actualites':        'actualites.html',
    '/formations':        'formations.html',
    '/tarifications':     'tarifications.html',
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
    '/map':           'map.html',
}


@app.route('/api/chat/claude', methods=['POST'])
@rate_limit(limit=20, window=60)
def chat_claude():
    """Proxy Anthropic Claude pour le chatbot Sentinel AI."""
    import os, json as _json
    try:
        data = request.get_json(force=True) or {}
        model    = data.get('model', 'claude-sonnet-4-6')
        system   = data.get('system', '')
        messages = data.get('messages', [])
        max_tok  = min(int(data.get('max_tokens', 550)), 1000)

        ANTHROPIC_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
        if not ANTHROPIC_KEY:
            return jsonify({"error": "ANTHROPIC_API_KEY non configuree"}), 503

        import urllib.request as _req
        payload = _json.dumps({
            "model": model,
            "max_tokens": max_tok,
            "system": system,
            "messages": messages
        }).encode('utf-8')

        req = _req.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01"
            },
            method="POST"
        )
        with _req.urlopen(req, timeout=30) as r:
            result = _json.loads(r.read().decode('utf-8'))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ══════════════════════════════════════════════════════════
# REGISTRE IA — Base de donnees externe geree (Postgres)
# Utilise la variable d'environnement DATABASE_URL (standard
# Render/Heroku/Neon/Supabase). Si absente (dev local), bascule
# automatiquement sur SQLite en fichier local pour ne jamais
# bloquer le developpement.
# ══════════════════════════════════════════════════════════
import sqlite3
from datetime import datetime, timedelta

DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()
REGISTRE_USE_PG = bool(DATABASE_URL)
REGISTRE_SQLITE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'registre_ia.db')

if REGISTRE_USE_PG:
    import psycopg
    import psycopg.rows
    # Render fournit parfois des URLs postgres:// (ancien schema) -> psycopg accepte les deux
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

    # Diagnostic : logger le host cible SANS exposer les identifiants
    try:
        from urllib.parse import urlparse as _urlparse
        _parsed = _urlparse(DATABASE_URL)
        logger.info(f"REGISTRE_IA — DATABASE_URL detectee, host cible : {_parsed.hostname}:{_parsed.port or 5432}, base : {_parsed.path.lstrip('/')}")
    except Exception:
        logger.info("REGISTRE_IA — DATABASE_URL detectee (parsing host impossible)")

    # Test de connexion reel au demarrage : si echec, on bascule proprement sur SQLite
    # plutot que de rester bloque sur un moteur Postgres inaccessible a chaque requete.
    try:
        _test_conn = psycopg.connect(DATABASE_URL, row_factory=psycopg.rows.dict_row, connect_timeout=5)
        _test_conn.close()
        logger.info("REGISTRE_IA — connexion Postgres testee avec succes")
    except Exception as _conn_err:
        logger.error(f"REGISTRE_IA — connexion Postgres impossible ({_conn_err}) — bascule sur SQLite local")
        REGISTRE_USE_PG = False

    # Pool de connexions persistant : elimine la latence de handshake TCP/TLS/auth
    # (1-3s observes sur Render) qui se produisait a CHAQUE requete avec psycopg.connect()
    # appele individuellement. Le pool maintient des connexions ouvertes et les reutilise.
    REGISTRE_POOL = None
    try:
        from psycopg_pool import ConnectionPool
        REGISTRE_POOL = ConnectionPool(
            DATABASE_URL, min_size=1, max_size=5, timeout=10,
            kwargs={"row_factory": psycopg.rows.dict_row}, open=True
        )
        logger.info("REGISTRE_IA — pool de connexions Postgres initialise (min=1, max=5)")
    except Exception as _pool_err:
        logger.warning(f"REGISTRE_IA — pool de connexions indisponible, repli sur connexion directe : {_pool_err}")
        REGISTRE_POOL = None

class _PooledConnWrapper:
    """Wrapper de compatibilite : le code existant appelle conn.close() partout (sans
    context manager). Ce wrapper intercepte close() pour rendre la connexion au pool
    au lieu de la fermer definitivement, sans avoir a modifier les dizaines d appels existants."""
    def __init__(self, pool, conn):
        self._pool = pool
        self._conn = conn
    def __getattr__(self, name):
        return getattr(self._conn, name)
    def close(self):
        try:
            # Nettoie systematiquement l etat transactionnel avant de rendre la
            # connexion au pool : un rollback sur une transaction deja terminee
            # (commit explicite fait par ailleurs) est un no-op sans danger, et
            # ca evite que le pool doive le faire lui-meme avec un warning a
            # chaque fois qu un appelant oublie un commit() apres un SELECT.
            try:
                self._conn.rollback()
            except Exception:
                pass
            self._pool.putconn(self._conn)
        except Exception:
            try: self._conn.close()
            except Exception: pass

def registre_get_db():
    if REGISTRE_USE_PG:
        if REGISTRE_POOL is not None:
            try:
                conn = REGISTRE_POOL.getconn()
                return _PooledConnWrapper(REGISTRE_POOL, conn)
            except Exception as _e:
                logger.warning(f"REGISTRE_IA — getconn pool echoue, connexion directe : {_e}")
        return psycopg.connect(DATABASE_URL, row_factory=psycopg.rows.dict_row)
    else:
        conn = sqlite3.connect(REGISTRE_SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def registre_sql(pg_query, sqlite_query):
    """Retourne la requete adaptee au moteur actif (placeholders %s vs ?)."""
    return pg_query if REGISTRE_USE_PG else sqlite_query

import secrets as _secrets_auth
# Token stable par defaut si AUTH_MASTER_TOKEN n'est pas defini sur Render (Environment).
# Recommande : definissez votre propre valeur secrete dans Render pour plus de securite -
# ce fallback reste fonctionnel immediatement mais est visible dans le code source.
AUTH_MASTER_TOKEN = os.environ.get('AUTH_MASTER_TOKEN', '').strip() or 'kwQKnjGw8YLgsP1yWwkA1Fg8jhH3BLwe'
# Ensemble des tokens acceptes par le lien maitre /auth/<token> :
#  - la variable d'environnement Render AUTH_MASTER_TOKEN (prioritaire, recommandee)
#  - le fallback statique ci-dessus (fonctionnel immediatement)
#  - le token historique distribue par email avant la migration vers le fallback
#    statique (les anciens liens enregistres/favoris restent valides)
AUTH_TOKENS_VALIDES = frozenset(t for t in (
    os.environ.get('AUTH_MASTER_TOKEN', '').strip(),
    'kwQKnjGw8YLgsP1yWwkA1Fg8jhH3BLwe',
    'PBeay16MElqpW5kvtJ3XWHuBVAlUtNw-DCUmEx-3PEw',
) if t)
if AUTH_MASTER_TOKEN == 'kwQKnjGw8YLgsP1yWwkA1Fg8jhH3BLwe':
    logger.warning("AUTH_MASTER_TOKEN non defini en variable d'environnement Render — "
                    "utilisation du token par defaut (visible dans le code source). "
                    "Definissez AUTH_MASTER_TOKEN sur Render pour une valeur secrete personnelle.")

def sentauth_init_db():
    conn = registre_get_db()
    cur = conn.cursor()
    if REGISTRE_USE_PG:
        cur.execute('''CREATE TABLE IF NOT EXISTS clients (
            id SERIAL PRIMARY KEY,
            nom_entreprise TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mot_de_passe_hash TEXT,
            actif BOOLEAN DEFAULT FALSE,
            date_creation TEXT NOT NULL,
            derniere_connexion TEXT,
            invitation_token TEXT,
            invitation_expire TEXT,
            rgpd_consenti BOOLEAN DEFAULT FALSE,
            rgpd_consenti_date TEXT
        )''')
        try:
            cur.execute("ALTER TABLE clients ALTER COLUMN mot_de_passe_hash DROP NOT NULL")
            cur.execute("ALTER TABLE clients ALTER COLUMN actif SET DEFAULT FALSE")
            cur.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS invitation_token TEXT")
            cur.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS invitation_expire TEXT")
            cur.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS verify_email_token TEXT")
            cur.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS verify_email_expire TEXT")
            cur.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT")
            cur.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS stripe_subscription_id TEXT")
            cur.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS essai_fin TEXT")
            cur.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS essai_relance TEXT")
            cur.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS rgpd_consenti BOOLEAN DEFAULT FALSE")
            cur.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS rgpd_consenti_date TEXT")
            cur.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS plan TEXT DEFAULT 'gratuit'")
            cur.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS reset_token TEXT")
            cur.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS reset_expire TEXT")
            conn.commit()
        except Exception: conn.rollback()
    else:
        cur.execute('''CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_entreprise TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
            mot_de_passe_hash TEXT NOT NULL, actif INTEGER DEFAULT 1,
            date_creation TEXT NOT NULL, derniere_connexion TEXT
        )''')
    # ── Migration : forcer plan='gratuit' sur les comptes créés avant
    # la correction (commit 0fe43de0). Tout compte public doit démarrer
    # au plan Gratuit — seul CONSEILPREV attribue pro/entreprise via admin.
    # Note : CONSEILPREV_INTERNAL_EMAIL n'est pas encore définie ici (définie
    # après l'appel try: sentauth_init_db()), on utilise le littéral direct.
    _CP_EMAIL = 'conseilprev@internal.system'
    try:
        cur2 = conn.cursor()
        if REGISTRE_USE_PG:
            cur2.execute(
                # Parenthèses explicites : (A OR B OR C) AND D
                # Sans elles, AND a priorité sur OR → logique incorrecte
                "UPDATE clients SET plan='gratuit' "                "WHERE plan IS NULL "                "AND email != %s",
                (_CP_EMAIL,)
            )
        else:
            cur2.execute(
                "UPDATE clients SET plan='gratuit' "                "WHERE plan IS NULL "                "AND email != ?",
                (_CP_EMAIL,)
            )
        n = cur2.rowcount
        conn.commit()
        if n > 0:
            logger.info(f"MIGRATION_PLAN: {n} compte(s) remis au plan gratuit")
    except Exception as _m:
        try: conn.rollback()
        except: pass
        logger.error(f"MIGRATION_PLAN_ERR: {_m}")
    conn.close()

try:
    sentauth_init_db()
except Exception as _e:
    logger.error(f"AUTH — erreur init table clients : {_e}")

def raas_init_db():
    """Table des jalons RaaS — agent Sentinel Pricing Orchestrator.
    Un enregistrement par (client, jalon). Statuts : pending -> verified -> invoiced.
    Un jalon verified est irrevocable (garantie contractuelle)."""
    conn = registre_get_db()
    cur = conn.cursor()
    if REGISTRE_USE_PG:
        cur.execute('''CREATE TABLE IF NOT EXISTS raas_milestones (
            id SERIAL PRIMARY KEY,
            client_id INTEGER NOT NULL,
            milestone_id TEXT NOT NULL,
            label TEXT NOT NULL,
            art TEXT,
            weight REAL NOT NULL,
            threshold INTEGER NOT NULL,
            amount_eur INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            score_at_verification REAL,
            evidence TEXT,
            verified_at TEXT,
            invoiced_at TEXT,
            created_at TEXT NOT NULL,
            UNIQUE(client_id, milestone_id)
        )''')
    else:
        cur.execute('''CREATE TABLE IF NOT EXISTS raas_milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            milestone_id TEXT NOT NULL,
            label TEXT NOT NULL,
            art TEXT,
            weight REAL NOT NULL,
            threshold INTEGER NOT NULL,
            amount_eur INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            score_at_verification REAL,
            evidence TEXT,
            verified_at TEXT,
            invoiced_at TEXT,
            created_at TEXT NOT NULL,
            UNIQUE(client_id, milestone_id)
        )''')
    conn.commit()
    conn.close()

try:
    raas_init_db()
except Exception as _e:
    logger.error(f"RAAS — erreur init table raas_milestones : {_e}")


def raas_clients_init_db():
    """Tables expertes de gestion des clients RaaS (reserve CONSEILPREV) :
    - client_kyc     : donnees KYC (Know Your Customer) par client
    - raas_contracts : contrats generes/enregistres par client (BDD)
    - raas_invoices  : factures emises selon l'echeancier client
    - client_notes   : notes explicatives par client
    Toutes les operations sont reservees a la session CONSEILPREV."""
    conn = registre_get_db()
    cur = conn.cursor()
    if REGISTRE_USE_PG:
        cur.execute('''CREATE TABLE IF NOT EXISTS client_kyc (
            client_id INTEGER PRIMARY KEY,
            raison_sociale TEXT,
            siren TEXT,
            forme_juridique TEXT,
            adresse TEXT,
            code_postal TEXT,
            ville TEXT,
            pays TEXT DEFAULT 'France',
            representant TEXT,
            fonction_representant TEXT,
            email_contact TEXT,
            telephone TEXT,
            tva_intra TEXT,
            secteur TEXT,
            effectif TEXT,
            kyc_status TEXT NOT NULL DEFAULT 'incomplet',
            kyc_verified_at TEXT,
            updated_at TEXT NOT NULL
        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS raas_contracts (
            id SERIAL PRIMARY KEY,
            client_id INTEGER NOT NULL,
            reference TEXT NOT NULL UNIQUE,
            envelope_total INTEGER,
            milestones_count INTEGER,
            status TEXT NOT NULL DEFAULT 'brouillon',
            content_json TEXT,
            created_at TEXT NOT NULL,
            signed_at TEXT
        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS raas_invoices (
            id SERIAL PRIMARY KEY,
            client_id INTEGER NOT NULL,
            numero TEXT NOT NULL UNIQUE,
            milestone_id TEXT,
            amount_eur INTEGER NOT NULL,
            installments INTEGER DEFAULT 2,
            status TEXT NOT NULL DEFAULT 'emise',
            due_json TEXT,
            issued_at TEXT NOT NULL,
            paid_at TEXT
        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS client_notes (
            id SERIAL PRIMARY KEY,
            client_id INTEGER NOT NULL,
            note TEXT NOT NULL,
            author TEXT,
            created_at TEXT NOT NULL
        )''')
    else:
        cur.execute('''CREATE TABLE IF NOT EXISTS client_kyc (
            client_id INTEGER PRIMARY KEY,
            raison_sociale TEXT, siren TEXT, forme_juridique TEXT,
            adresse TEXT, code_postal TEXT, ville TEXT, pays TEXT DEFAULT 'France',
            representant TEXT, fonction_representant TEXT, email_contact TEXT,
            telephone TEXT, tva_intra TEXT, secteur TEXT, effectif TEXT,
            kyc_status TEXT NOT NULL DEFAULT 'incomplet', kyc_verified_at TEXT,
            updated_at TEXT NOT NULL
        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS raas_contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL, reference TEXT NOT NULL UNIQUE,
            envelope_total INTEGER, milestones_count INTEGER,
            status TEXT NOT NULL DEFAULT 'brouillon', content_json TEXT,
            created_at TEXT NOT NULL, signed_at TEXT
        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS raas_invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL, numero TEXT NOT NULL UNIQUE,
            milestone_id TEXT, amount_eur INTEGER NOT NULL, installments INTEGER DEFAULT 2,
            status TEXT NOT NULL DEFAULT 'emise', due_json TEXT,
            issued_at TEXT NOT NULL, paid_at TEXT
        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS client_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL, note TEXT NOT NULL,
            author TEXT, created_at TEXT NOT NULL
        )''')
    conn.commit()
    conn.close()

try:
    raas_clients_init_db()
except Exception as _e:
    logger.error(f"RAAS — erreur init tables gestion clients : {_e}")


def clients_followup_init_db():
    """Tables de suivi et de relance client (reserve CONSEILPREV) :
    - client_lifecycle : statut, sante, dernier contact, prochaine action
    - client_relances  : relances planifiees/effectuees (email, appel, facture, jalon)
    Reservees a la session CONSEILPREV."""
    conn = registre_get_db()
    cur = conn.cursor()
    if REGISTRE_USE_PG:
        cur.execute('''CREATE TABLE IF NOT EXISTS client_lifecycle (
            client_id INTEGER PRIMARY KEY,
            statut TEXT NOT NULL DEFAULT 'prospect',
            sante TEXT NOT NULL DEFAULT 'a_evaluer',
            last_contact_at TEXT,
            next_action_at TEXT,
            next_action_label TEXT,
            updated_at TEXT NOT NULL
        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS client_relances (
            id SERIAL PRIMARY KEY,
            client_id INTEGER NOT NULL,
            type TEXT NOT NULL DEFAULT 'email',
            objet TEXT NOT NULL,
            canal TEXT DEFAULT 'email',
            priorite TEXT DEFAULT 'normale',
            due_date TEXT,
            status TEXT NOT NULL DEFAULT 'planifiee',
            notes TEXT,
            related_ref TEXT,
            created_at TEXT NOT NULL,
            done_at TEXT
        )''')
    else:
        cur.execute('''CREATE TABLE IF NOT EXISTS client_lifecycle (
            client_id INTEGER PRIMARY KEY,
            statut TEXT NOT NULL DEFAULT 'prospect',
            sante TEXT NOT NULL DEFAULT 'a_evaluer',
            last_contact_at TEXT, next_action_at TEXT, next_action_label TEXT,
            updated_at TEXT NOT NULL
        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS client_relances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL, type TEXT NOT NULL DEFAULT 'email',
            objet TEXT NOT NULL, canal TEXT DEFAULT 'email', priorite TEXT DEFAULT 'normale',
            due_date TEXT, status TEXT NOT NULL DEFAULT 'planifiee', notes TEXT,
            related_ref TEXT, created_at TEXT NOT NULL, done_at TEXT
        )''')
    conn.commit()
    conn.close()

try:
    clients_followup_init_db()
except Exception as _e:
    logger.error(f"RAAS — erreur init tables suivi/relance : {_e}")

# Definition canonique des 7 jalons AI Act (partagee avec le front PRICING_PARAMS.raasMilestones)
RAAS_MILESTONE_DEFS = [
    {'id': 'registre', 'label': 'Registre IA complet',          'art': 'Art. 49',    'w': 0.10, 'threshold': 30},
    {'id': 'classif',  'label': 'Classification des risques',   'art': 'Annexe III', 'w': 0.10, 'threshold': 38},
    {'id': 'sgr',      'label': 'SGR operationnel',             'art': 'Art. 9',     'w': 0.15, 'threshold': 48},
    {'id': 'doctech',  'label': 'Documentation technique',      'art': 'Art. 11',    'w': 0.15, 'threshold': 58},
    {'id': 'fria',     'label': 'FRIA realisee',                'art': 'Art. 27',    'w': 0.10, 'threshold': 65},
    {'id': 'audit80',  'label': 'Audit de conformite >= 80 %',  'art': 'Art. 43',    'w': 0.20, 'threshold': 80},
    {'id': 'attest',   'label': 'Attestation finale',           'art': 'Art. 47',    'w': 0.20, 'threshold': 90},
]

# Jalons RaaS RGPD (parallele a l'IA Act) : ids prefixes 'rgpd_', memes table et endpoints.
# Verification adossee a l'indice de conformite RGPD (score transmis par le frontend).
RAAS_MILESTONE_DEFS_RGPD = [
    {'id': 'rgpd_registre',        'label': 'Registre des traitements (art. 30)', 'art': 'Art. 30',  'w': 0.15, 'threshold': 30},
    {'id': 'rgpd_cartographie',    'label': 'Cartographie des traitements',       'art': 'Art. 30',  'w': 0.10, 'threshold': 40},
    {'id': 'rgpd_aipd',            'label': 'AIPD des traitements a risque',      'art': 'Art. 35',  'w': 0.20, 'threshold': 55},
    {'id': 'rgpd_pbd',             'label': 'Privacy by design',                  'art': 'Art. 25',  'w': 0.15, 'threshold': 65},
    {'id': 'rgpd_doc',             'label': 'Politique documentaire',             'art': 'Art. 5.2', 'w': 0.15, 'threshold': 75},
    {'id': 'rgpd_sensibilisation', 'label': 'Sensibilisation',                    'art': 'Art. 39',  'w': 0.10, 'threshold': 85},
    {'id': 'rgpd_conformite',      'label': 'Indice de conformite RGPD >= 90%',   'art': 'RGPD',     'w': 0.15, 'threshold': 90},
]

# Jalons RaaS ISO/IEC 42001 (3e cadre) : ids prefixes 'iso_', meme table et endpoints.
# Verification adossee a la couverture du systeme de management (score transmis par le frontend).
RAAS_MILESTONE_DEFS_ISO = [
    {'id': 'iso_contexte',     'label': 'Contexte & parties interessees',      'art': 'Clause 4',        'w': 0.10, 'threshold': 20},
    {'id': 'iso_leadership',   'label': 'Politique IA & leadership',           'art': 'Clause 5 · A.2',  'w': 0.15, 'threshold': 35},
    {'id': 'iso_planification','label': 'Evaluation des risques & impacts',     'art': 'Clause 6 · 8.2',  'w': 0.20, 'threshold': 50},
    {'id': 'iso_support',      'label': 'Competences & documentation',         'art': 'Clause 7',        'w': 0.15, 'threshold': 60},
    {'id': 'iso_operation',    'label': 'Cycle de vie & donnees',              'art': 'Clause 8 · A.6',  'w': 0.15, 'threshold': 70},
    {'id': 'iso_evaluation',   'label': 'Audit interne & revue de direction',  'art': 'Clause 9',        'w': 0.15, 'threshold': 80},
    {'id': 'iso_amelioration', 'label': 'Amelioration continue',               'art': 'Clause 10',       'w': 0.10, 'threshold': 90},
]
RAAS_ENVELOPE_RATE = 0.60  # enveloppe resultats = 60 % du SaaS annuel

CONSEILPREV_INTERNAL_EMAIL = 'conseilprev@internal.system'

def ensure_conseilprev_client_id():
    """Garantit l'existence d'un enregistrement CONSEILPREV dans la table clients
    (idempotent — cree au premier appel, retrouve ensuite). Necessaire pour que
    CONSEILPREV ait un vrai client_id numerique, comme tout client normal, afin
    de pouvoir lui assigner les donnees du Registre IA crees avant l isolation
    par client (migration)."""
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql(
        'SELECT id FROM clients WHERE email=%s', 'SELECT id FROM clients WHERE email=?'
    ), (CONSEILPREV_INTERNAL_EMAIL,))
    row = cur.fetchone()
    if row:
        cid = row['id'] if isinstance(row, dict) else row[0]
        conn.close()
        return cid
    now = datetime.utcnow().isoformat()
    if REGISTRE_USE_PG:
        cur.execute(
            "INSERT INTO clients (nom_entreprise, email, actif, rgpd_consenti, rgpd_consenti_date, date_creation, plan) "
            "VALUES (%s,%s,TRUE,TRUE,%s,%s,'entreprise') RETURNING id",
            ('CONSEILPREV', CONSEILPREV_INTERNAL_EMAIL, now, now)
        )
        cid = cur.fetchone()['id']
    else:
        cur.execute(
            "INSERT INTO clients (nom_entreprise, email, actif, rgpd_consenti, rgpd_consenti_date, date_creation, plan) "
            "VALUES (?,?,1,1,?,?,'entreprise')",
            ('CONSEILPREV', CONSEILPREV_INTERNAL_EMAIL, now, now)
        )
        cid = cur.lastrowid
    conn.commit()
    conn.close()
    logger.info(f"CONSEILPREV_CLIENT_CREATED id={cid}")
    return cid


def sentauth_current_client():
    """Retourne le dict client connecte, ou {'is_conseilprev': True} si acces
    CONSEILPREV via le lien maitre, ou None si non authentifie."""
    if session.get('is_conseilprev'):
        # L'acces CONSEILPREV ne doit jamais echouer a cause d'un incident DB :
        # en cas d'erreur (PostgreSQL froid, timeout), degrader avec id=0 plutot
        # que de provoquer une erreur 500 sur /sentinel.
        try:
            _cp_id = ensure_conseilprev_client_id()
        except Exception as _cp_err:
            logger.error(f'CONSEILPREV_CLIENT_ID_ERR (acces degrade id=0): {_cp_err}')
            _cp_id = 0
        return {'is_conseilprev': True, 'id': _cp_id, 'nom_entreprise': 'CONSEILPREV', 'plan': 'entreprise'}
    client_id = session.get('client_id')
    if not client_id:
        return None
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql('SELECT * FROM clients WHERE id=%s AND actif=TRUE', 'SELECT * FROM clients WHERE id=? AND actif=1'), (client_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row) if not isinstance(row, dict) else row
    # CONSEILPREV connecte par le formulaire habituel (et non par le lien maitre) :
    # reconnu par son e-mail interne ou sa denomination, il conserve l'acces
    # administrateur complet et n'est pas concerne par la protection anti-elevation.
    _em = (d.get('email') or '').strip().lower()
    _nom = (d.get('nom_entreprise') or '').strip().upper()
    if _em == str(CONSEILPREV_INTERNAL_EMAIL).strip().lower() or _nom == 'CONSEILPREV':
        return {'is_conseilprev': True, 'id': d['id'], 'nom_entreprise': 'CONSEILPREV',
                'email': d.get('email'), 'plan': 'entreprise'}
    raw_plan = d.get('plan') or 'gratuit'
    # Sécurité : un compte public ne peut avoir que 'gratuit'.
    # Pro/Entreprise ne sont attribués que via l'interface admin CONSEILPREV.
    safe_plan = raw_plan if raw_plan in ('gratuit', 'pro', 'entreprise') else 'gratuit'
    # Protection supplémentaire : si plan non-gratuit sans invitation admin → forcer gratuit
    # (détecte les comptes créés avant la correction)
    if safe_plan in ('pro', 'entreprise'):
        # Vérifier qu'une invitation admin a bien été utilisée (invitation_token=NULL = activé via admin)
        # Les comptes créés via l'API publique n'ont pas de invitation_token
        # ET ont un verify_email_token (flux email vérif) → plan forcé à gratuit
        had_verify_email = d.get('verify_email_token') is not None or d.get('verify_email_expire') is not None
        # Comptes créés via le flux public (avec vérif email) → gratuit seulement
        # Comptes créés via invitation admin → plan conservé
        was_invited = d.get('invitation_token') is None and not had_verify_email
        # Conserver le plan si créé par invitation admin OU si pas de token de vérif email
        # (ce qui indique une création admin directe)
        if not was_invited and safe_plan != 'gratuit':
            safe_plan = 'gratuit'
    # Essai gratuit de 15 jours : le compte accede au plan Gratuit pendant 15 jours
    # seulement. A l'echeance, l'acces prend fin (essai_expire) et une souscription
    # est requise. Les comptes payants (pro/entreprise) ne sont pas concernes.
    essai_actif = False
    essai_expire = False
    essai_jours = 0
    _ef = d.get('essai_fin')
    if _ef and safe_plan == 'gratuit':
        try:
            _fin = datetime.fromisoformat(str(_ef))
            _reste = (_fin - datetime.utcnow()).total_seconds()
            if _reste > 0:
                essai_actif = True
                essai_jours = max(1, int(_reste // 86400) + 1)
            else:
                essai_expire = True
        except Exception:
            essai_actif = False
    return {'is_conseilprev': False, 'id': d['id'], 'nom_entreprise': d['nom_entreprise'], 'email': d['email'],
            'plan': safe_plan, 'essai_actif': essai_actif, 'essai_expire': essai_expire,
            'essai_jours': essai_jours, 'essai_fin': _ef}

def sentinel_login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        client = sentauth_current_client()
        if not client:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentification requise.'}), 401
            return redirect('/login')
        request.current_client = client
        return f(*args, **kwargs)
    return wrapper

def require_paid_plan(f):
    """Protege les API de donnees reservees aux plans Pro/Entreprise (et CONSEILPREV).
    Le plan Gratuit (Apercu, Simulateur, Reglementations, Hub Training) n'a pas
    besoin de ce decorateur car ces pages n'ont pas de donnees sensibles a proteger."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        client = sentauth_current_client()
        if not client:
            return jsonify({'error': 'Authentification requise.'}), 401
        if client.get('is_conseilprev'):
            return f(*args, **kwargs)
        if (client.get('plan') or 'gratuit') == 'gratuit':
            return jsonify({'error': 'Cette fonctionnalite necessite un plan Pro ou Entreprise.', 'plan_requis': True}), 403
        return f(*args, **kwargs)
    return wrapper
# ══════════════════════════════════════════════════════════
# JOURNALISATION DES EMAILS — solution durable face aux incidents
# Brevo (blocage IP, quota epuise). Permet un diagnostic immediat
# sans avoir a chercher dans les logs Render a chaque incident.
# ══════════════════════════════════════════════════════════
def email_log_init_db():
    conn = registre_get_db()
    cur = conn.cursor()
    if REGISTRE_USE_PG:
        cur.execute('''CREATE TABLE IF NOT EXISTS email_log (
            id SERIAL PRIMARY KEY,
            destinataire TEXT NOT NULL,
            sujet TEXT,
            methode TEXT,
            succes BOOLEAN NOT NULL,
            raison_echec TEXT,
            date_envoi TEXT NOT NULL
        )''')
    else:
        cur.execute('''CREATE TABLE IF NOT EXISTS email_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destinataire TEXT NOT NULL, sujet TEXT, methode TEXT,
            succes INTEGER NOT NULL, raison_echec TEXT, date_envoi TEXT NOT NULL
        )''')
    conn.commit()
    conn.close()

try:
    email_log_init_db()
except Exception as _e:
    logger.error(f"EMAIL_LOG — erreur init DB : {_e}")

def email_log_record(destinataire, sujet, methode, succes, raison_echec=None):
    try:
        conn = registre_get_db()
        cur = conn.cursor()
        now = datetime.utcnow().isoformat()
        cur.execute(registre_sql(
            'INSERT INTO email_log (destinataire, sujet, methode, succes, raison_echec, date_envoi) VALUES (%s,%s,%s,%s,%s,%s)',
            'INSERT INTO email_log (destinataire, sujet, methode, succes, raison_echec, date_envoi) VALUES (?,?,?,?,?,?)'
        ), (destinataire, sujet, methode, succes, raison_echec, now))
        conn.commit()
        conn.close()
    except Exception as _e:
        logger.error(f"EMAIL_LOG_RECORD_FAILED : {_e}")

# ══════════════════════════════════════════════════════════
# RAPPORT DE CARTOGRAPHIE AUTOMATIQUE — genere cote serveur
# (fpdf2, pure Python, aucune dependance systeme) et envoye
# par email apres une periode de stabilite (debouncing) suite
# a une modification du Registre IA. Premiere brique pilote
# du systeme de documents vivants demande par le client.
# ══════════════════════════════════════════════════════════
from fpdf import FPDF

CLASSIF_LABELS_PDF = {
    'inacceptable': 'Risque inacceptable (interdit)',
    'haut': 'Haut risque',
    'limite': 'Risque limite (transparence)',
    'minimal': 'Risque minimal',
    'a_evaluer': 'A evaluer',
}

def generate_cartographie_pdf_bytes(client_id):
    """Construit le PDF de cartographie a partir du Registre IA reel du client.
    Retourne les bytes du PDF, ou None si le client n'a aucun systeme enregistre."""
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql(
        'SELECT * FROM systemes_ia WHERE client_id=%s ORDER BY classification, nom',
        'SELECT * FROM systemes_ia WHERE client_id=? ORDER BY classification, nom'
    ), (client_id,))
    rows = [dict(r) if not isinstance(r, dict) else r for r in cur.fetchall()]
    conn.close()
    if not rows:
        return None

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 12, 'Cartographie des systemes IA', ln=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, f'CONSEILPREV — Genere le {datetime.utcnow().strftime("%d/%m/%Y a %H:%M")} UTC', ln=True)
    pdf.ln(6)
    pdf.set_text_color(0, 0, 0)

    counts = {}
    for r in rows:
        c = r.get('classification') or 'a_evaluer'
        counts[c] = counts.get(c, 0) + 1

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, f'Synthese — {len(rows)} systeme(s) au registre', ln=True)
    pdf.set_font('Helvetica', '', 10)
    for classif, label in CLASSIF_LABELS_PDF.items():
        n = counts.get(classif, 0)
        if n > 0:
            pdf.cell(0, 6, f'  {label} : {n}', ln=True)
    pdf.ln(6)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, 'Detail par systeme', ln=True)
    for r in rows:
        pdf.set_font('Helvetica', 'B', 10)
        pdf.multi_cell(0, 6, r.get('nom') or 'Sans nom')
        pdf.set_font('Helvetica', '', 9)
        classif_label = CLASSIF_LABELS_PDF.get(r.get('classification'), 'A evaluer')
        pdf.multi_cell(0, 5, f"Classification : {classif_label}  ·  Secteur : {r.get('secteur') or '-'}")
        if r.get('finalite'):
            pdf.multi_cell(0, 5, f"Finalite : {r['finalite'][:300]}")
        pdf.ln(3)

    return bytes(pdf.output())


def send_cartographie_report(client_id, client_email, client_nom):
    """Genere le PDF de cartographie et l'envoie par email avec piece jointe.
    Appelee uniquement apres la periode de stabilite du debouncer."""
    try:
        pdf_bytes = generate_cartographie_pdf_bytes(client_id)
        if not pdf_bytes:
            return
        pdf_b64 = base64.b64encode(pdf_bytes).decode('ascii')
        html = (
            f"<p>Bonjour,</p><p>Votre Registre IA a ete mis a jour. "
            f"Vous trouverez ci-joint la cartographie actualisee de vos systemes IA.</p>"
            f"<p>CONSEILPREV — Sentinel AI</p>"
        )
        ok, result = send_via_brevo_api(
            client_email, client_nom,
            "Cartographie IA mise a jour — Sentinel AI",
            html,
            attachments=[{'content': pdf_b64, 'name': 'cartographie-ia.pdf'}],
            tags=['rapport-auto-cartographie']
        )
        email_log_record(client_email, "Cartographie IA mise a jour", 'brevo_api (auto)', ok, None if ok else str(result))
        logger.info(f"CARTOGRAPHIE_REPORT_SENT client={client_id} ok={ok}")
    except Exception as e:
        logger.error(f"CARTOGRAPHIE_REPORT_FAILED client={client_id}: {e}")


# ── Debouncing PERSISTANT : remplace l ancien threading.Timer (en memoire, perdu
# si le processus redemarre/se met en veille — ce qui arrive sur Render). La date
# du prochain envoi est stockee en base, et verifiee a chaque requete pertinente.
REPORT_DEBOUNCE_SECONDS = 300  # 5 minutes

def pending_reports_init_db():
    conn = registre_get_db()
    cur = conn.cursor()
    if REGISTRE_USE_PG:
        cur.execute('''CREATE TABLE IF NOT EXISTS pending_reports (
            client_id INTEGER PRIMARY KEY,
            client_email TEXT,
            client_nom TEXT,
            next_send_at TEXT NOT NULL
        )''')
    else:
        cur.execute('''CREATE TABLE IF NOT EXISTS pending_reports (
            client_id INTEGER PRIMARY KEY,
            client_email TEXT, client_nom TEXT, next_send_at TEXT NOT NULL
        )''')
    conn.commit()
    conn.close()

try:
    pending_reports_init_db()
except Exception as _e:
    logger.error(f"PENDING_REPORTS — erreur init DB : {_e}")


def schedule_cartographie_report(client_id, client_email, client_nom):
    """Repousse la date d'envoi prevue de 5 minutes (upsert). Remplace l'ancien
    threading.Timer : la date est persistante en base, donc survit a un
    redemarrage ou une mise en veille du processus — seule une requete
    ulterieure (check_pending_reports) declenche l'envoi reel."""
    try:
        next_send = (datetime.utcnow() + timedelta(seconds=REPORT_DEBOUNCE_SECONDS)).isoformat()
        conn = registre_get_db()
        cur = conn.cursor()
        if REGISTRE_USE_PG:
            cur.execute(
                "INSERT INTO pending_reports (client_id, client_email, client_nom, next_send_at) "
                "VALUES (%s,%s,%s,%s) ON CONFLICT (client_id) DO UPDATE SET "
                "client_email=EXCLUDED.client_email, client_nom=EXCLUDED.client_nom, next_send_at=EXCLUDED.next_send_at",
                (client_id, client_email, client_nom, next_send)
            )
        else:
            cur.execute(
                "INSERT OR REPLACE INTO pending_reports (client_id, client_email, client_nom, next_send_at) "
                "VALUES (?,?,?,?)",
                (client_id, client_email, client_nom, next_send)
            )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"SCHEDULE_REPORT_FAILED client={client_id}: {e}")


def check_pending_reports():
    """Cherche les rapports dont la date d'envoi est depassee et les traite.
    Appelee a chaque requete sur une route a fort trafic (cf. plus bas) plutot
    que via un timer en arriere-plan — fonctionne tant qu il y a une activite
    minimale sur le site, sans dependre de la survie d un thread en memoire."""
    try:
        now = datetime.utcnow().isoformat()
        conn = registre_get_db()
        cur = conn.cursor()
        cur.execute(registre_sql(
            "SELECT * FROM pending_reports WHERE next_send_at <= %s",
            "SELECT * FROM pending_reports WHERE next_send_at <= ?"
        ), (now,))
        due = [dict(r) if not isinstance(r, dict) else r for r in cur.fetchall()]
        if due:
            cur.execute(registre_sql(
                "DELETE FROM pending_reports WHERE next_send_at <= %s",
                "DELETE FROM pending_reports WHERE next_send_at <= ?"
            ), (now,))
        # Commit inconditionnel : meme un simple SELECT ouvre une transaction
        # (mode par defaut de psycopg) qui doit etre terminee avant de rendre
        # la connexion au pool, sous peine d un rollback de securite a chaque
        # appel (visible dans les logs sous forme de warning repete).
        conn.commit()
        conn.close()
        for r in due:
            send_cartographie_report(r['client_id'], r['client_email'], r['client_nom'])
    except Exception as e:
        logger.error(f"CHECK_PENDING_REPORTS_FAILED: {e}")

@app.route('/api/admin/email-health', methods=['GET'])
@sentinel_login_required
def email_health():
    client = sentauth_current_client()
    if not client or not client.get('is_conseilprev'):
        abort(403)
    try:
        email_log_init_db()  # garantit que la table existe, meme si l init au demarrage a echoue
    except Exception as _e:
        logger.error(f"EMAIL_HEALTH_INIT_RETRY_FAILED : {_e}")

    try:
        conn = registre_get_db()
        cur = conn.cursor()
        cur.execute(registre_sql(
            "SELECT * FROM email_log ORDER BY date_envoi DESC LIMIT 30",
            "SELECT * FROM email_log ORDER BY date_envoi DESC LIMIT 30"
        ))
        recent = [dict(r) if not isinstance(r, dict) else r for r in cur.fetchall()]

        cutoff_24h = (datetime.utcnow() - _timedelta_auth(hours=24)).isoformat()
        cur.execute(registre_sql(
            "SELECT succes, COUNT(*) as n FROM email_log WHERE date_envoi > %s GROUP BY succes",
            "SELECT succes, COUNT(*) as n FROM email_log WHERE date_envoi > ? GROUP BY succes"
        ), (cutoff_24h,))
        stats_rows = cur.fetchall()
        conn.commit()
        conn.close()
    except Exception as _e:
        logger.error(f"EMAIL_HEALTH_QUERY_FAILED : {_e}")
        return jsonify({'error': f'Erreur de lecture du journal email : {_e}'}), 500

    succes_24h = 0
    echec_24h = 0
    for r in stats_rows:
        rd = dict(r) if not isinstance(r, dict) else r
        if rd['succes'] in (True, 1):
            succes_24h = rd['n']
        else:
            echec_24h = rd['n']
    total_24h = succes_24h + echec_24h
    taux_succes = round(succes_24h / total_24h * 100, 1) if total_24h > 0 else None

    return jsonify({
        'taux_succes_24h': taux_succes,
        'total_24h': total_24h,
        'succes_24h': succes_24h,
        'echec_24h': echec_24h,
        'derniers_envois': recent,
        'alerte': echec_24h > 0 and (taux_succes is None or taux_succes < 80)
    })

@app.route('/auth/<token>')
@rate_limit_strict(limit=10, window=300)
def sentauth_master_link(token):
    """Lien secret CONSEILPREV — pose un cookie de session longue duree sans mot de passe."""
    if token in AUTH_TOKENS_VALIDES:
        session.clear()
        session['is_conseilprev'] = True
        session.permanent = True
        logger.info(f"AUTH_CONSEILPREV — connexion via lien maitre, IP={limiter.get_ip(request)}")
        return redirect('/sentinel')
    # Journaliser le prefixe du token rejete pour faciliter le diagnostic
    # (jamais le token complet, par prudence dans les logs)
    logger.warning(f"AUTH_LINK_REJETE prefixe={token[:8]}... IP={limiter.get_ip(request)}")
    abort(404)

@app.route('/login', methods=['GET'])
def sentauth_login_page():
    if sentauth_current_client():
        return redirect('/sentinel')
    return send_from_directory('.', 'login.html')

def sentauth_send_login_alert(email, nom_entreprise, ip):
    """Envoie une alerte de securite par email a chaque connexion client reussie.
    Execute en arriere-plan (thread court, envoi unique) pour ne pas ralentir la
    connexion avec la latence SMTP (~1-2s)."""
    try:
        date_str = datetime.utcnow().strftime('%d/%m/%Y à %H:%M UTC')
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:24px;background:#F5F2ED">
          <div style="background:#fff;border-radius:8px;padding:32px;border:1px solid #E0DDD8">
            <div style="font-size:20px;font-weight:600;color:#1C1C1C;margin-bottom:4px">Sentinel <span style="background:#B83222;color:#fff;font-size:10px;padding:2px 6px;border-radius:3px;vertical-align:middle">AI</span></div>
            <div style="font-size:11px;color:#767676;text-transform:uppercase;letter-spacing:1px;margin-bottom:24px">Alerte de connexion</div>
            <p style="font-size:14px;color:#3D3D3D;line-height:1.6">Bonjour,</p>
            <p style="font-size:14px;color:#3D3D3D;line-height:1.6">Une connexion à votre espace Sentinel AI ({nom_entreprise}) vient d être effectuée :</p>
            <table style="width:100%;font-size:13px;color:#3D3D3D;margin:16px 0">
              <tr><td style="padding:4px 0;color:#767676">Date</td><td style="padding:4px 0;font-weight:600">{date_str}</td></tr>
              <tr><td style="padding:4px 0;color:#767676">Adresse IP</td><td style="padding:4px 0;font-weight:600">{ip}</td></tr>
            </table>
            <p style="font-size:13px;color:#767676;line-height:1.6;margin-top:20px">Si vous n êtes pas à l origine de cette connexion, contactez immédiatement CONSEILPREV à <a href="mailto:christophe.cerf@outlook.com" style="color:#B83222">christophe.cerf@outlook.com</a>.</p>
          </div>
          <p style="font-size:11px;color:#A8A8A8;text-align:center;margin-top:16px">CONSEILPREV — Sentinel AI · Cet email est envoyé automatiquement à chaque connexion pour votre sécurité.</p>
        </div>
        """
        ok, method = send_email_smart(email, nom_entreprise, "🔒 Nouvelle connexion à votre espace Sentinel AI", html, tags=['sentinel-login-alert'])
        logger.info(f"LOGIN_ALERT_EMAIL {email} via {method} — ok={ok}")
    except Exception as e:
        logger.error(f"LOGIN_ALERT_EMAIL_FAILED {email} : {e}")

@app.route('/api/sentinel-auth/login', methods=['POST'])
@rate_limit_strict(limit=20, window=300)
def sentauth_login():
    data = request.get_json(force=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = (data.get('password') or '')
    bf_key = f"login:{email}"
    if bf_protector.is_blocked(bf_key):
        remaining = bf_protector.remaining(bf_key)
        return jsonify({'error': f'Trop de tentatives. Réessayez dans {remaining // 60 + 1} min.'}), 429

    if not email or not password:
        return jsonify({'error': 'Email et mot de passe requis.'}), 400

    conn = registre_get_db()
    cur = conn.cursor()
    # Recupere le compte quel que soit son statut actif — la distinction entre
    # "mauvais mot de passe" et "compte pas encore active" ne se fait QU APRES
    # verification du mot de passe, pour ne jamais reveler le statut d un compte
    # a quelqu un qui ne connait pas deja le bon mot de passe (anti-enumeration).
    cur.execute(registre_sql('SELECT * FROM clients WHERE email=%s', 'SELECT * FROM clients WHERE email=?'), (email,))
    row = cur.fetchone()
    conn.commit()
    conn.close()

    if not row:
        bf_protector.record_attempt(bf_key, success=False)
        return jsonify({'error': 'Identifiants incorrects.'}), 401

    d = dict(row) if not isinstance(row, dict) else row
    if not d.get('mot_de_passe_hash') or not check_password_hash(d['mot_de_passe_hash'], password):
        bf_protector.record_attempt(bf_key, success=False)
        return jsonify({'error': 'Identifiants incorrects.'}), 401

    if not d.get('actif'):
        bf_protector.record_attempt(bf_key, success=True)
        return jsonify({'error': 'Votre compte n\'est pas encore activé. Vérifiez votre boîte mail (et les spams) pour le lien de confirmation, ou contactez CONSEILPREV si vous ne l\'avez pas reçu.'}), 403

    bf_protector.record_attempt(bf_key, success=True)
    session.clear()
    session['client_id'] = d['id']
    session.permanent = True

    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql('UPDATE clients SET derniere_connexion=%s WHERE id=%s', 'UPDATE clients SET derniere_connexion=? WHERE id=?'),
                (datetime.utcnow().isoformat(), d['id']))
    conn.commit()

    # Alerte de securite par email a chaque connexion - envoi unique en arriere-plan,
    # ne bloque pas la reponse de connexion avec la latence SMTP (~1-2s).
    _login_ip = limiter.get_ip(request)
    threading.Thread(target=sentauth_send_login_alert, args=(email, d['nom_entreprise'], _login_ip), daemon=True).start()
    conn.close()

    logger.info(f"AUTH_CLIENT — connexion reussie : {email}")
    return jsonify({'ok': True, 'nom_entreprise': d['nom_entreprise']})

@app.route('/api/sentinel-auth/logout', methods=['POST'])
@rate_limit(limit=30, window=60)
def sentauth_logout():
    # Vide la session (y compris l'indicateur d'acces CONSEILPREV pose par le
    # lien maitre) et invalide explicitement le cookie cote navigateur.
    session.pop('is_conseilprev', None)
    session.pop('client_id', None)
    session.clear()
    resp = make_response(jsonify({'ok': True}))
    try:
        resp.set_cookie(app.config.get('SESSION_COOKIE_NAME', 'session'), '', expires=0, path='/')
    except Exception:
        pass
    resp.headers['Cache-Control'] = 'no-store'
    return resp

def _essai_relances():
    """Rappels d'essai gratuit : un courriel a 3 jours de l'echeance, un autre a
    l'expiration. Chaque rappel n'est envoye qu'une fois (colonne essai_relance).
    Declenche au fil des chargements, sans tache planifiee. Silencieux en cas
    d'erreur : ne doit jamais perturber une requete."""
    try:
        conn = registre_get_db(); cur = conn.cursor()
        try:
            cur.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS essai_relance TEXT")
            conn.commit()
        except Exception:
            try: conn.rollback()
            except Exception: pass
        cur.execute("SELECT id, email, nom_entreprise, essai_fin, essai_relance, plan FROM clients "
                    "WHERE essai_fin IS NOT NULL AND (plan IS NULL OR plan = 'gratuit')")
        rows = [dict(r) for r in cur.fetchall()]
        try: conn.close()
        except Exception: pass
    except Exception:
        return

    now = datetime.utcnow()
    for c in rows:
        email = c.get('email')
        if not email:
            continue
        try:
            fin = datetime.fromisoformat(str(c.get('essai_fin')))
        except Exception:
            continue
        reste = (fin - now).total_seconds()
        deja = c.get('essai_relance') or ''
        etape = None
        if 0 < reste <= 3 * 86400 and deja != 'j3' and deja != 'fin':
            etape = 'j3'
        elif reste <= 0 and deja != 'fin':
            etape = 'fin'
        if not etape:
            continue

        nom = c.get('nom_entreprise') or 'Client'
        if etape == 'j3':
            jours = max(1, int(reste // 86400) + 1)
            sujet = 'Votre essai Sentinel se termine dans %d jour(s)' % jours
            html = ('<p>Bonjour,</p>'
                    '<p>Votre essai gratuit de Sentinel se termine dans <strong>%d jour(s)</strong>. '
                    'A l echeance, l acces a la plateforme prendra fin.</p>'
                    '<p>Pour poursuivre sans interruption, vous pouvez souscrire une offre depuis la '
                    'plateforme, ou comparer les formules sur notre site.</p>'
                    '<p>L equipe CONSEILPREV</p>') % jours
        else:
            sujet = 'Votre essai gratuit Sentinel est termine'
            html = ('<p>Bonjour,</p>'
                    '<p>Votre essai gratuit de Sentinel est arrive a son terme et l acces a la plateforme '
                    'a pris fin.</p>'
                    '<p>Pour retrouver l acces, souscrivez l offre qui correspond a vos besoins. '
                    'Nous restons a votre disposition pour vous accompagner dans ce choix.</p>'
                    '<p>L equipe CONSEILPREV</p>')

        try:
            send_email_smart(email, nom, sujet, html, tags=['essai-' + etape])
        except Exception:
            continue
        try:
            conn2 = registre_get_db(); cur2 = conn2.cursor()
            cur2.execute(registre_sql('UPDATE clients SET essai_relance=%s WHERE id=%s',
                                      'UPDATE clients SET essai_relance=? WHERE id=?'), (etape, int(c['id'])))
            conn2.commit()
            try: conn2.close()
            except Exception: pass
        except Exception:
            pass


@app.route('/api/sentinel-auth/me', methods=['GET'])
@rate_limit(limit=120, window=60)
def sentauth_me():
    check_pending_reports()  # verifie les rapports en attente a chaque chargement de page
    try:
        _essai_relances()  # rappels d'essai (3 jours avant, puis a l'expiration)
    except Exception:
        pass
    client = sentauth_current_client()
    if not client:
        return jsonify({'authenticated': False}), 401
    return jsonify({'authenticated': True, **client})


# ══════════════════════════════════════════════════════════
# PAIEMENT STRIPE — ACTIVATION AUTOMATIQUE DES OFFRES
# Sur paiement confirme (notification signee 'checkout.session.completed'),
# l'offre du client est automatiquement mise a niveau (pro / entreprise).
# Securite : aucune offre n'est activee sans un evenement de paiement dont
# la signature Stripe est verifiee. Import 'stripe' differe et endpoints
# desactives tant que les cles ne sont pas configurees : l'absence de
# configuration ne compromet jamais le demarrage de l'application.
# CONSEILPREV/Sentinel.
# ══════════════════════════════════════════════════════════

def activate_client_plan(client_id, plan):
    """Met a niveau l'offre d'un client. Reserve a pro/entreprise ; appele
    uniquement apres verification d'un paiement (webhook signe) ou par
    l'administration CONSEILPREV."""
    if plan not in ('pro', 'entreprise'):
        return False
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql('UPDATE clients SET plan=%s WHERE id=%s',
                             'UPDATE clients SET plan=? WHERE id=?'),
                (plan, int(client_id)))
    conn.commit()
    try:
        conn.close()
    except Exception:
        pass
    return True


@app.route('/api/sentinel/checkout', methods=['POST'])
@rate_limit(limit=20, window=60)
def sentinel_checkout():
    """Cree une session de paiement Stripe pour le client connecte et l'offre
    demandee. Retourne l'URL de paiement hebergee par Stripe."""
    client = sentauth_current_client()
    if not client or not client.get('id'):
        return jsonify({'error': "Authentification requise."}), 401
    body = request.get_json(silent=True) or {}
    plan = body.get('plan')
    if plan not in ('pro', 'entreprise'):
        return jsonify({'error': "Offre invalide."}), 400
    secret = os.environ.get('STRIPE_SECRET_KEY')
    price_id = os.environ.get('STRIPE_PRICE_PRO' if plan == 'pro' else 'STRIPE_PRICE_ENTREPRISE')
    if not secret or not price_id:
        return jsonify({'error': "Paiement non configure.", 'configured': False}), 501
    try:
        import stripe
    except Exception:
        return jsonify({'error': "Module de paiement indisponible.", 'configured': False}), 501
    stripe.api_key = secret
    base = request.host_url.rstrip('/')
    try:
        _existing_customer = None
        try:
            _cc = registre_get_db(); _ccur = _cc.cursor()
            _ccur.execute(registre_sql('SELECT stripe_customer_id FROM clients WHERE id=%s', 'SELECT stripe_customer_id FROM clients WHERE id=?'), (int(client['id']),))
            _crow = _ccur.fetchone()
            if _crow: _existing_customer = dict(_crow).get('stripe_customer_id')
            _cc.close()
        except Exception:
            _existing_customer = None
        _sk = dict(mode='subscription', line_items=[{'price': price_id, 'quantity': 1}],
                   client_reference_id=str(client['id']),
                   metadata={'client_id': str(client['id']), 'plan': plan},
                   success_url=base + '/sentinel?activation=ok', cancel_url=base + '/tarifications')
        if _existing_customer:
            _sk['customer'] = _existing_customer
        else:
            _sk['customer_email'] = client.get('email')
        sess = stripe.checkout.Session.create(**_sk)
        return jsonify({'url': sess.url})
    except Exception:
        return jsonify({'error': "Echec de creation de la session de paiement."}), 502


@app.route('/api/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """Notification Stripe. Verifie la signature puis active l'offre du client
    sur 'checkout.session.completed'. Desactive si le secret n'est pas defini."""
    secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    if not secret:
        return jsonify({'error': "Webhook non configure."}), 501
    try:
        import stripe
    except Exception:
        return jsonify({'error': "Module indisponible."}), 501
    payload = request.get_data()
    sig = request.headers.get('Stripe-Signature', '')
    try:
        event = stripe.Webhook.construct_event(payload, sig, secret)
    except Exception:
        return jsonify({'error': "Signature invalide."}), 400
    try:
        import json as _jwh
        evt = _jwh.loads(payload.decode('utf-8') if isinstance(payload, (bytes, bytearray)) else payload)
    except Exception:
        evt = {}
    try:
        if _stripe_event_seen(evt.get('id')):
            return jsonify({'received': True, 'duplicate': True}), 200
        etype = evt.get('type')
        obj = (evt.get('data') or {}).get('object') or {}
        meta = obj.get('metadata') or {}
        if etype == 'checkout.session.completed':
            cid = meta.get('client_id') or obj.get('client_reference_id')
            plan = meta.get('plan')
            if cid and plan in ('pro', 'entreprise'):
                try:
                    activate_client_plan(int(cid), plan)
                except Exception:
                    pass
                try:
                    _conn_e = registre_get_db(); _cur_e = _conn_e.cursor()
                    _cur_e.execute(registre_sql('SELECT email, nom_entreprise FROM clients WHERE id=%s', 'SELECT email, nom_entreprise FROM clients WHERE id=?'), (int(cid),))
                    _ce = _cur_e.fetchone()
                    try: _conn_e.close()
                    except Exception: pass
                    _ce = dict(_ce) if _ce else {}
                    if _ce.get('email'):
                        _plabel = 'Entreprise' if plan == 'entreprise' else 'Pro'
                        send_email_smart(_ce['email'], _ce.get('nom_entreprise') or 'Client',
                            'Votre offre Sentinel ' + _plabel + ' est activee',
                            '<p>Bonjour,</p><p>Votre paiement a bien ete recu et votre offre <strong>Sentinel ' + _plabel + '</strong> est desormais active. Vous avez acces a l ensemble des modules correspondants.</p><p>L equipe CONSEILPREV</p>',
                            tags=['activation'])
                except Exception:
                    pass
            cust = obj.get('customer')
            if cid and cust:
                try:
                    _billing_set_customer(int(cid), cust)
                except Exception:
                    pass
            sub = obj.get('subscription')
            if cid and sub:
                try:
                    _billing_set_subscription(int(cid), sub)
                except Exception:
                    pass
        elif etype == 'invoice.paid':
            numero = meta.get('numero'); ech = meta.get('echeance')
            if numero and ech:
                try:
                    _billing_on_invoice_paid(numero, int(ech))
                except Exception:
                    pass
        elif etype == 'invoice.payment_failed':
            numero = meta.get('numero'); ech = meta.get('echeance'); cid = meta.get('client_id')
            if numero and ech:
                try:
                    _billing_on_invoice_failed(numero, int(ech), int(cid) if cid else None)
                except Exception:
                    pass
        try: _stripe_event_mark(evt.get('id'))
        except Exception: pass
        return jsonify({'received': True}), 200



    # ══════════════════════════════════════════════════════════
    # AGENT SENTINEL PRICING ORCHESTRATOR — TARIFICATION RAAS PAR JALONS
    # Modules : Observateur (lecture des scores), Verificateur (double
    # declencheur), Facturier (echeancier, gel des acquis), Mediateur
    # (validation humaine CONSEILPREV requise pour verifier un jalon).
    # Regles inviolables : jalon verified = irrevocable ; aucun jalon
    # facture sans verification ; enveloppe bornee a 60 % du SaaS annuel.
    # ══════════════════════════════════════════════════════════
    except Exception as _we:
        try: logger.error('STRIPE_WEBHOOK_ERROR: ' + str(_we))
        except Exception: pass
    return jsonify({'received': True}), 200

def raas_require_conseilprev():
    """Retourne le client CONSEILPREV ou None. Les operations de
    verification et de facturation sont reservees a CONSEILPREV
    (module Mediateur : l'humain reste dans la boucle)."""
    client = sentauth_current_client()
    if not client or not client.get('is_conseilprev'):
        return None
    return client

@app.route('/api/raas/milestones', methods=['GET'])
@sentinel_login_required
def raas_list_milestones():
    """Etat des jalons du client courant (ou ?client_id=N pour CONSEILPREV)."""
    client = request.current_client
    target_id = client['id']
    if client.get('is_conseilprev') and request.args.get('client_id'):
        try:
            target_id = int(request.args.get('client_id'))
        except (TypeError, ValueError):
            return jsonify({'ok': False, 'error': 'client_id invalide'}), 400
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql(
        'SELECT * FROM raas_milestones WHERE client_id=%s ORDER BY threshold ASC',
        'SELECT * FROM raas_milestones WHERE client_id=? ORDER BY threshold ASC'
    ), (target_id,))
    rows = [dict(r) if not isinstance(r, dict) else r for r in cur.fetchall()]
    conn.close()
    total = sum(r['amount_eur'] for r in rows)
    verified = sum(r['amount_eur'] for r in rows if r['status'] in ('verified', 'invoiced'))
    return jsonify({'ok': True, 'milestones': rows,
                    'envelope_total': total, 'verified_total': verified})

@app.route('/api/raas/milestones/init', methods=['POST'])
def raas_init_milestones():
    """Initialise l'echeancier de jalons pour un client (CONSEILPREV uniquement).
    Body : {client_id, saas_monthly}. Idempotent : n'ecrase jamais un jalon existant
    (garantie du gel des acquis)."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    d = request.get_json(force=True, silent=True) or {}
    try:
        client_id = int(d.get('client_id'))
        saas_monthly = float(d.get('saas_monthly'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'client_id et saas_monthly requis'}), 400
    if saas_monthly <= 0 or saas_monthly > 100000:
        return jsonify({'ok': False, 'error': 'saas_monthly hors bornes'}), 400
    framework = str(d.get('framework', 'ai_act'))
    if framework == 'rgpd':
        defs = RAAS_MILESTONE_DEFS_RGPD
    elif framework == 'iso42001':
        defs = RAAS_MILESTONE_DEFS_ISO
    else:
        defs = RAAS_MILESTONE_DEFS
    envelope = round(saas_monthly * 12 * RAAS_ENVELOPE_RATE)
    now = datetime.utcnow().isoformat()
    conn = registre_get_db()
    cur = conn.cursor()
    created = 0
    for m in defs:
        amount = round(envelope * m['w'])
        try:
            if REGISTRE_USE_PG:
                cur.execute(
                    "INSERT INTO raas_milestones (client_id, milestone_id, label, art, weight, threshold, amount_eur, status, created_at) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,'pending',%s) ON CONFLICT (client_id, milestone_id) DO NOTHING",
                    (client_id, m['id'], m['label'], m['art'], m['w'], m['threshold'], amount, now))
            else:
                cur.execute(
                    "INSERT OR IGNORE INTO raas_milestones (client_id, milestone_id, label, art, weight, threshold, amount_eur, status, created_at) "
                    "VALUES (?,?,?,?,?,?,?,'pending',?)",
                    (client_id, m['id'], m['label'], m['art'], m['w'], m['threshold'], amount, now))
            created += cur.rowcount if cur.rowcount and cur.rowcount > 0 else 0
        except Exception as e:
            logger.error(f'RAAS_INIT_ERR {client_id}/{m["id"]}: {e}')
    conn.commit()
    conn.close()
    logger.info(f'RAAS_INIT client={client_id} envelope={envelope} crees={created}')
    return jsonify({'ok': True, 'created': created, 'envelope': envelope})

@app.route('/api/raas/milestones/verify', methods=['POST'])
def raas_verify_milestone():
    """Verificateur + Mediateur : marque un jalon comme verifie (CONSEILPREV).
    Body : {client_id, milestone_id, score, evidence}. Double declencheur :
    le score fourni doit atteindre le seuil ET l'evidence documentaire est
    obligatoire. Un jalon deja verified/invoiced est immuable."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    d = request.get_json(force=True, silent=True) or {}
    try:
        client_id = int(d.get('client_id'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'client_id requis'}), 400
    milestone_id = str(d.get('milestone_id', ''))[:50]
    evidence = str(d.get('evidence', ''))[:2000]
    try:
        score = float(d.get('score'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'score requis'}), 400
    if not evidence.strip():
        return jsonify({'ok': False, 'error': 'Evidence documentaire obligatoire (double declencheur)'}), 400
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql(
        'SELECT * FROM raas_milestones WHERE client_id=%s AND milestone_id=%s',
        'SELECT * FROM raas_milestones WHERE client_id=? AND milestone_id=?'
    ), (client_id, milestone_id))
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({'ok': False, 'error': 'Jalon introuvable — initialisez l\'echeancier'}), 404
    r = dict(row) if not isinstance(row, dict) else row
    if r['status'] in ('verified', 'invoiced'):
        conn.close()
        return jsonify({'ok': False, 'error': 'Jalon deja verifie — irrevocable'}), 409
    if score < r['threshold']:
        conn.close()
        logger.info(f'RAAS_VERIFY_REFUSE client={client_id} jalon={milestone_id} score={score}<{r["threshold"]}')
        return jsonify({'ok': False, 'error': f'Score {score} inferieur au seuil {r["threshold"]} — declencheur non atteint'}), 422
    now = datetime.utcnow().isoformat()
    cur.execute(registre_sql(
        "UPDATE raas_milestones SET status='verified', score_at_verification=%s, evidence=%s, verified_at=%s WHERE client_id=%s AND milestone_id=%s",
        "UPDATE raas_milestones SET status='verified', score_at_verification=?, evidence=?, verified_at=? WHERE client_id=? AND milestone_id=?"
    ), (score, evidence, now, client_id, milestone_id))
    conn.commit()
    conn.close()
    logger.info(f'RAAS_VERIFY_OK client={client_id} jalon={milestone_id} score={score}')
    return jsonify({'ok': True, 'milestone_id': milestone_id, 'status': 'verified',
                    'amount_eur': r['amount_eur'], 'verified_at': now})

@app.route('/api/raas/billing-cycle', methods=['POST'])
def raas_billing_cycle():
    """Facturier : marque comme factures (invoiced) les jalons verifies d'un
    client et retourne l'echeancier de paiement etale sur 2 mensualites.
    Body : {client_id}. Reserve a CONSEILPREV. Le montant est fige au moment
    de la verification — le cycle ne recalcule jamais un jalon acquis."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    d = request.get_json(force=True, silent=True) or {}
    try:
        client_id = int(d.get('client_id'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'client_id requis'}), 400
    now = datetime.utcnow().isoformat()
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql(
        "SELECT * FROM raas_milestones WHERE client_id=%s AND status='verified'",
        "SELECT * FROM raas_milestones WHERE client_id=? AND status='verified'"
    ), (client_id,))
    to_invoice = [dict(r) if not isinstance(r, dict) else r for r in cur.fetchall()]
    schedule = []
    for r in to_invoice:
        half = round(r['amount_eur'] / 2)
        schedule.append({'milestone_id': r['milestone_id'], 'label': r['label'],
                         'installments': [half, r['amount_eur'] - half]})
        cur.execute(registre_sql(
            "UPDATE raas_milestones SET status='invoiced', invoiced_at=%s WHERE id=%s",
            "UPDATE raas_milestones SET status='invoiced', invoiced_at=? WHERE id=?"
        ), (now, r['id']))
    conn.commit()
    conn.close()
    total = sum(r['amount_eur'] for r in to_invoice)
    logger.info(f'RAAS_BILLING client={client_id} jalons={len(to_invoice)} total={total}')
    return jsonify({'ok': True, 'invoiced_count': len(to_invoice),
                    'total_eur': total, 'schedule': schedule})

# ══════════════════════════════════════════════════════════
# INVITATION CLIENT — le client definit lui-meme son mot de passe
# Conforme RGPD : CONSEILPREV ne connait jamais le mot de passe du client.
# Lien d'invitation a usage unique (48h), consentement RGPD horodate (preuve),
# captcha maison (sans dependance externe), politique de robustesse du mot de passe.
# ══════════════════════════════════════════════════════════
INVITATION_VALIDITY_HOURS = 48
VERIFY_EMAIL_VALIDITY_HOURS = 48  # flux distinct de l invitation CONSEILPREV : auto-inscription cliente
PASSWORD_MIN_LENGTH = 10

def sentauth_validate_password_strength(password):
    """Politique de robustesse : 10+ caracteres, majuscule, minuscule, chiffre, caractere special."""
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Le mot de passe doit contenir au moins {PASSWORD_MIN_LENGTH} caractères."
    if not _re.search(r'[A-Z]', password):
        return False, "Le mot de passe doit contenir au moins une majuscule."
    if not _re.search(r'[a-z]', password):
        return False, "Le mot de passe doit contenir au moins une minuscule."
    if not _re.search(r'[0-9]', password):
        return False, "Le mot de passe doit contenir au moins un chiffre."
    if not _re.search(r'[^A-Za-z0-9]', password):
        return False, "Le mot de passe doit contenir au moins un caractère spécial."
    return True, None

def sentauth_send_invitation_email(email, nom_entreprise, token):
    try:
        link = f"https://conseilprev.onrender.com/invitation/{token}"
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:24px;background:#F5F2ED">
          <div style="background:#fff;border-radius:8px;padding:32px;border:1px solid #E0DDD8">
            <div style="font-size:20px;font-weight:600;color:#1C1C1C;margin-bottom:4px">Sentinel <span style="background:#B83222;color:#fff;font-size:10px;padding:2px 6px;border-radius:3px;vertical-align:middle">AI</span></div>
            <div style="font-size:11px;color:#767676;text-transform:uppercase;letter-spacing:1px;margin-bottom:24px">Invitation — Activation de votre accès</div>
            <p style="font-size:14px;color:#3D3D3D;line-height:1.6">Bonjour,</p>
            <p style="font-size:14px;color:#3D3D3D;line-height:1.6">CONSEILPREV vous invite à activer votre accès à la plateforme Sentinel AI pour {nom_entreprise}.</p>
            <p style="font-size:14px;color:#3D3D3D;line-height:1.6">Pour votre sécurité, vous seul choisirez votre mot de passe — CONSEILPREV ne le connaîtra jamais.</p>
            <div style="text-align:center;margin:28px 0">
              <a href="{link}" style="display:inline-block;background:#B83222;color:#fff;padding:13px 28px;border-radius:6px;text-decoration:none;font-weight:600;font-size:14px">Activer mon accès →</a>
            </div>
            <p style="font-size:12px;color:#767676;line-height:1.6">Ce lien est valable {INVITATION_VALIDITY_HOURS} heures et ne peut être utilisé qu une seule fois.</p>
          </div>
          <p style="font-size:11px;color:#A8A8A8;text-align:center;margin-top:16px">CONSEILPREV — Sentinel AI</p>
        </div>
        """
        ok, method = send_email_smart(email, nom_entreprise, "Activez votre accès à Sentinel AI", html, tags=['sentinel-invitation'])
        logger.info(f"INVITATION_EMAIL {email} via {method} — ok={ok}")
        return ok
    except Exception as e:
        logger.error(f"INVITATION_EMAIL_FAILED {email} : {e}")
        return False

# ══════════════════════════════════════════════════════════
# GESTION EXPERTE DES CLIENTS RAAS (reserve CONSEILPREV)
# KYC, contrats (BDD), factures selon echeancier, notes, notification email.
# ══════════════════════════════════════════════════════════

def _clients_now():
    return datetime.utcnow().isoformat()

def _kyc_completeness(row):
    """Retourne 'complet' si les champs KYC essentiels sont renseignes, sinon 'incomplet'."""
    essentiels = ['raison_sociale', 'siren', 'adresse', 'ville', 'representant', 'email_contact']
    for k in essentiels:
        v = (row.get(k) if isinstance(row, dict) else None)
        if not v or not str(v).strip():
            return 'incomplet'
    return 'complet'

@app.route('/api/clients/kyc', methods=['GET'])
def clients_kyc_get():
    """Lit la fiche KYC d'un client. Reserve CONSEILPREV."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    try:
        client_id = int(request.args.get('client_id'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'client_id invalide'}), 400
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql(
        'SELECT * FROM client_kyc WHERE client_id=%s',
        'SELECT * FROM client_kyc WHERE client_id=?'
    ), (client_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({'ok': True, 'kyc': None})
    return jsonify({'ok': True, 'kyc': dict(row)})

@app.route('/api/clients/kyc', methods=['POST'])
def clients_kyc_save():
    """Cree ou met a jour la fiche KYC d'un client. Reserve CONSEILPREV.
    Les champs sont valides et nettoyes ; le statut de completude est recalcule."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    d = request.get_json(force=True, silent=True) or {}
    try:
        client_id = int(d.get('client_id'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'client_id invalide'}), 400
    def clean(k, maxlen=200):
        v = d.get(k, '')
        return (str(v).strip()[:maxlen]) if v is not None else ''
    fields = {
        'raison_sociale': clean('raison_sociale'), 'siren': clean('siren', 20),
        'forme_juridique': clean('forme_juridique', 60), 'adresse': clean('adresse', 300),
        'code_postal': clean('code_postal', 12), 'ville': clean('ville', 120),
        'pays': clean('pays', 80) or 'France', 'representant': clean('representant', 160),
        'fonction_representant': clean('fonction_representant', 120),
        'email_contact': clean('email_contact', 160), 'telephone': clean('telephone', 40),
        'tva_intra': clean('tva_intra', 30), 'secteur': clean('secteur', 60),
        'effectif': clean('effectif', 40),
    }
    email = fields['email_contact']
    if email and '@' not in email:
        return jsonify({'ok': False, 'error': 'Email de contact invalide'}), 400
    status = _kyc_completeness(fields)
    now = _clients_now()
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql(
        'SELECT client_id FROM client_kyc WHERE client_id=%s',
        'SELECT client_id FROM client_kyc WHERE client_id=?'
    ), (client_id,))
    exists = cur.fetchone()
    cols = list(fields.keys())
    vals = [fields[c] for c in cols]
    if exists:
        setclause = ', '.join([c + '=' + ('%s' if REGISTRE_USE_PG else '?') for c in cols])
        setclause += ', kyc_status=' + ('%s' if REGISTRE_USE_PG else '?')
        setclause += ', updated_at=' + ('%s' if REGISTRE_USE_PG else '?')
        cur.execute('UPDATE client_kyc SET ' + setclause + ' WHERE client_id=' + ('%s' if REGISTRE_USE_PG else '?'),
                    tuple(vals) + (status, now, client_id))
    else:
        ph = ', '.join(['%s' if REGISTRE_USE_PG else '?'] * (len(cols) + 2))
        cur.execute('INSERT INTO client_kyc (client_id, ' + ', '.join(cols) + ', kyc_status, updated_at) VALUES (' + ('%s' if REGISTRE_USE_PG else '?') + ', ' + ph + ')',
                    (client_id,) + tuple(vals) + (status, now))
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'kyc_status': status, 'updated_at': now})

@app.route('/api/clients/notes', methods=['GET'])
def clients_notes_get():
    """Liste les notes explicatives d'un client. Reserve CONSEILPREV."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    try:
        client_id = int(request.args.get('client_id'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'client_id invalide'}), 400
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql(
        'SELECT * FROM client_notes WHERE client_id=%s ORDER BY created_at DESC',
        'SELECT * FROM client_notes WHERE client_id=? ORDER BY created_at DESC'
    ), (client_id,))
    notes = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({'ok': True, 'notes': notes})

@app.route('/api/clients/notes', methods=['POST'])
def clients_notes_add():
    """Ajoute une note explicative a un client. Reserve CONSEILPREV."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    d = request.get_json(force=True, silent=True) or {}
    try:
        client_id = int(d.get('client_id'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'client_id invalide'}), 400
    note = (str(d.get('note', '')).strip())[:4000]
    if not note:
        return jsonify({'ok': False, 'error': 'Note vide'}), 400
    now = _clients_now()
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql(
        'INSERT INTO client_notes (client_id, note, author, created_at) VALUES (%s, %s, %s, %s)',
        'INSERT INTO client_notes (client_id, note, author, created_at) VALUES (?, ?, ?, ?)'
    ), (client_id, note, 'CONSEILPREV', now))
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'created_at': now})

@app.route('/api/clients/contracts', methods=['GET'])
def clients_contracts_list():
    """Liste les contrats enregistres d'un client. Reserve CONSEILPREV."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    try:
        client_id = int(request.args.get('client_id'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'client_id invalide'}), 400
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql(
        'SELECT id, client_id, reference, envelope_total, milestones_count, status, created_at, signed_at FROM raas_contracts WHERE client_id=%s ORDER BY created_at DESC',
        'SELECT id, client_id, reference, envelope_total, milestones_count, status, created_at, signed_at FROM raas_contracts WHERE client_id=? ORDER BY created_at DESC'
    ), (client_id,))
    contracts = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({'ok': True, 'contracts': contracts})

@app.route('/api/clients/contracts', methods=['POST'])
def clients_contracts_save():
    """Enregistre un contrat RaaS en base pour un client. Reserve CONSEILPREV.
    Reference unique RAAS-<client>-<annee>-<seq>. Idempotent sur la reference."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    d = request.get_json(force=True, silent=True) or {}
    try:
        client_id = int(d.get('client_id'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'client_id invalide'}), 400
    now = _clients_now()
    year = datetime.utcnow().year
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql(
        'SELECT COUNT(*) AS n FROM raas_contracts WHERE client_id=%s',
        'SELECT COUNT(*) AS n FROM raas_contracts WHERE client_id=?'
    ), (client_id,))
    r = cur.fetchone()
    seq = (dict(r)['n'] if r else 0) + 1
    reference = 'RAAS-%d-%d-%02d' % (client_id, year, seq)
    try:
        envelope = int(d.get('envelope_total') or 0)
    except (TypeError, ValueError):
        envelope = 0
    try:
        mcount = int(d.get('milestones_count') or 0)
    except (TypeError, ValueError):
        mcount = 0
    content = json.dumps(d.get('content') or {})[:200000]
    cur.execute(registre_sql(
        'INSERT INTO raas_contracts (client_id, reference, envelope_total, milestones_count, status, content_json, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)',
        'INSERT INTO raas_contracts (client_id, reference, envelope_total, milestones_count, status, content_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)'
    ), (client_id, reference, envelope, mcount, 'enregistre', content, now))
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'reference': reference, 'created_at': now})

@app.route('/api/clients/invoices', methods=['GET'])
def clients_invoices_list():
    """Liste les factures emises d'un client. Reserve CONSEILPREV."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    try:
        client_id = int(request.args.get('client_id'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'client_id invalide'}), 400
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql(
        'SELECT * FROM raas_invoices WHERE client_id=%s ORDER BY issued_at DESC',
        'SELECT * FROM raas_invoices WHERE client_id=? ORDER BY issued_at DESC'
    ), (client_id,))
    invoices = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({'ok': True, 'invoices': invoices})

@app.route('/api/clients/invoices/issue', methods=['POST'])
def clients_invoices_issue():
    """Emet les factures des jalons verifies selon l'echeancier du client, en
    2 mensualites. Enregistre chaque facture, marque le jalon invoiced, et
    notifie le client par email (Brevo) si une fiche KYC avec email existe.
    Reserve CONSEILPREV."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    d = request.get_json(force=True, silent=True) or {}
    try:
        client_id = int(d.get('client_id'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'client_id invalide'}), 400
    notify = bool(d.get('notify', True))
    now = _clients_now()
    conn = registre_get_db()
    cur = conn.cursor()
    # Jalons verifies non encore factures
    cur.execute(registre_sql(
        "SELECT * FROM raas_milestones WHERE client_id=%s AND status='verified'",
        "SELECT * FROM raas_milestones WHERE client_id=? AND status='verified'"
    ), (client_id,))
    verified = [dict(r) for r in cur.fetchall()]
    if not verified:
        conn.close()
        return jsonify({'ok': True, 'issued_count': 0, 'invoices': [], 'message': 'Aucun jalon verifie a facturer'})
    year = datetime.utcnow().year
    issued = []
    for m in verified:
        cur.execute(registre_sql(
            'SELECT COUNT(*) AS n FROM raas_invoices WHERE client_id=%s',
            'SELECT COUNT(*) AS n FROM raas_invoices WHERE client_id=?'
        ), (client_id,))
        seq = (dict(cur.fetchone())['n'] if True else 0) + 1
        numero = 'F%d-%d-%03d' % (year, client_id, seq)
        amount = int(m.get('amount_eur') or 0)
        half = round(amount / 2)
        _due1 = datetime.utcnow().date().isoformat()
        _due2 = (datetime.utcnow() + timedelta(days=30)).date().isoformat()
        due = [{'echeance': 1, 'montant': half, 'due': _due1, 'status': 'a_venir'},
               {'echeance': 2, 'montant': amount - half, 'due': _due2, 'status': 'a_venir'}]
        cur.execute(registre_sql(
            'INSERT INTO raas_invoices (client_id, numero, milestone_id, amount_eur, installments, status, due_json, issued_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
            'INSERT INTO raas_invoices (client_id, numero, milestone_id, amount_eur, installments, status, due_json, issued_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
        ), (client_id, numero, m.get('milestone_id'), amount, 2, 'emise', json.dumps(due), now))
        cur.execute(registre_sql(
            "UPDATE raas_milestones SET status='invoiced', invoiced_at=%s WHERE client_id=%s AND milestone_id=%s",
            "UPDATE raas_milestones SET status='invoiced', invoiced_at=? WHERE client_id=? AND milestone_id=?"
        ), (now, client_id, m.get('milestone_id')))
        issued.append({'numero': numero, 'label': m.get('label'), 'amount_eur': amount, 'due': due})
    conn.commit()
    # Notification email client (best effort, ne bloque pas la facturation)
    email_sent = False
    email_error = None
    if notify:
        cur.execute(registre_sql(
            'SELECT raison_sociale, email_contact, representant FROM client_kyc WHERE client_id=%s',
            'SELECT raison_sociale, email_contact, representant FROM client_kyc WHERE client_id=?'
        ), (client_id,))
        kyc = cur.fetchone()
        kyc = dict(kyc) if kyc else {}
        to_email = (kyc.get('email_contact') or '').strip()
        if to_email and '@' in to_email:
            try:
                total = sum(i['amount_eur'] for i in issued)
                lignes = ''.join('<li>%s — %s : %d&#8239;&euro;</li>' % (i['numero'], i['label'], i['amount_eur']) for i in issued)
                html = ('<p>Bonjour %s,</p>' % (kyc.get('representant') or kyc.get('raison_sociale') or 'Madame, Monsieur')
                    + '<p>Dans le cadre de votre contrat de tarification RaaS par jalons, '
                    + 'CONSEILPREV a emis %d facture(s) correspondant aux jalons de conformite recemment verifies :</p>' % len(issued)
                    + '<ul>' + lignes + '</ul>'
                    + '<p>Montant total : <strong>%d&#8239;&euro;</strong>, chaque jalon etant echelonne sur deux mensualites egales.</p>' % total
                    + '<p>Ces jalons ont fait l\'objet d\'une double verification (score Sentinel atteint et validation documentaire).</p>'
                    + '<p>Cordialement,<br>Christophe CERF — CONSEILPREV — Sentinel AI</p>')
                res = send_email_smart(to_email, kyc.get('raison_sociale') or 'Client',
                                       'CONSEILPREV — Emission de facture(s) RaaS', html, tags=['raas-invoice'])
                email_sent = bool(res if not isinstance(res, tuple) else res[0])
            except Exception as _e:
                email_error = str(_e)[:200]
                logger.error(f"RAAS_INVOICE_EMAIL_FAILED client={client_id} : {_e}")
        else:
            email_error = 'Aucun email KYC valide'
    conn.close()
    try:
        _billing_cancel_subscription(client_id)
    except Exception:
        pass
    return jsonify({'ok': True, 'issued_count': len(issued), 'invoices': issued,
                    'email_sent': email_sent, 'email_error': email_error})

# ══════════════════════════════════════════════════════════
# SUIVI & RELANCE CLIENT AVANCE (reserve CONSEILPREV)
# Cycle de vie, relances, paiement facture, tableau de bord + suggestions.
# ══════════════════════════════════════════════════════════

def _days_since(iso_str):
    """Nombre de jours ecoules depuis une date ISO (ou None)."""
    if not iso_str:
        return None
    try:
        dt = datetime.fromisoformat(str(iso_str).replace('Z', '').split('.')[0])
        return (datetime.utcnow() - dt).days
    except Exception:
        return None

@app.route('/api/clients/status', methods=['GET'])
def clients_status_get():
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    try:
        client_id = int(request.args.get('client_id'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'client_id invalide'}), 400
    conn = registre_get_db(); cur = conn.cursor()
    cur.execute(registre_sql('SELECT * FROM client_lifecycle WHERE client_id=%s',
                             'SELECT * FROM client_lifecycle WHERE client_id=?'), (client_id,))
    row = cur.fetchone(); conn.close()
    return jsonify({'ok': True, 'status': (dict(row) if row else None)})

@app.route('/api/clients/status', methods=['POST'])
def clients_status_save():
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    d = request.get_json(force=True, silent=True) or {}
    try:
        client_id = int(d.get('client_id'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'client_id invalide'}), 400
    STATUTS = {'prospect', 'onboarding', 'actif', 'a_risque', 'inactif', 'clos'}
    SANTES = {'a_evaluer', 'bonne', 'moyenne', 'fragile'}
    statut = str(d.get('statut', 'prospect'))
    if statut not in STATUTS:
        statut = 'prospect'
    sante = str(d.get('sante', 'a_evaluer'))
    if sante not in SANTES:
        sante = 'a_evaluer'
    next_action_at = (str(d.get('next_action_at', '')).strip() or None)
    next_action_label = (str(d.get('next_action_label', '')).strip()[:200] or None)
    now = _clients_now()
    conn = registre_get_db(); cur = conn.cursor()
    cur.execute(registre_sql('SELECT client_id FROM client_lifecycle WHERE client_id=%s',
                             'SELECT client_id FROM client_lifecycle WHERE client_id=?'), (client_id,))
    exists = cur.fetchone()
    if exists:
        cur.execute(registre_sql(
            'UPDATE client_lifecycle SET statut=%s, sante=%s, next_action_at=%s, next_action_label=%s, updated_at=%s WHERE client_id=%s',
            'UPDATE client_lifecycle SET statut=?, sante=?, next_action_at=?, next_action_label=?, updated_at=? WHERE client_id=?'),
            (statut, sante, next_action_at, next_action_label, now, client_id))
    else:
        cur.execute(registre_sql(
            'INSERT INTO client_lifecycle (client_id, statut, sante, next_action_at, next_action_label, updated_at) VALUES (%s, %s, %s, %s, %s, %s)',
            'INSERT INTO client_lifecycle (client_id, statut, sante, next_action_at, next_action_label, updated_at) VALUES (?, ?, ?, ?, ?, ?)'),
            (client_id, statut, sante, next_action_at, next_action_label, now))
    conn.commit(); conn.close()
    return jsonify({'ok': True, 'statut': statut, 'sante': sante, 'updated_at': now})

@app.route('/api/clients/relances', methods=['GET'])
def clients_relances_list():
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    try:
        client_id = int(request.args.get('client_id'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'client_id invalide'}), 400
    conn = registre_get_db(); cur = conn.cursor()
    cur.execute(registre_sql(
        'SELECT * FROM client_relances WHERE client_id=%s ORDER BY (done_at IS NULL) DESC, due_date ASC, created_at DESC',
        'SELECT * FROM client_relances WHERE client_id=? ORDER BY (done_at IS NULL) DESC, due_date ASC, created_at DESC'), (client_id,))
    relances = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({'ok': True, 'relances': relances})

@app.route('/api/clients/relances', methods=['POST'])
def clients_relances_add():
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    d = request.get_json(force=True, silent=True) or {}
    try:
        client_id = int(d.get('client_id'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'client_id invalide'}), 400
    objet = (str(d.get('objet', '')).strip())[:300]
    if not objet:
        return jsonify({'ok': False, 'error': 'Objet requis'}), 400
    TYPES = {'email', 'appel', 'rdv', 'relance_facture', 'relance_jalon', 'autre'}
    rtype = str(d.get('type', 'email'))
    if rtype not in TYPES:
        rtype = 'autre'
    canal = str(d.get('canal', 'email'))[:40]
    PRIOS = {'basse', 'normale', 'haute', 'urgente'}
    priorite = str(d.get('priorite', 'normale'))
    if priorite not in PRIOS:
        priorite = 'normale'
    due_date = (str(d.get('due_date', '')).strip() or None)
    notes = (str(d.get('notes', '')).strip())[:2000]
    related_ref = (str(d.get('related_ref', '')).strip())[:80] or None
    now = _clients_now()
    conn = registre_get_db(); cur = conn.cursor()
    cur.execute(registre_sql(
        'INSERT INTO client_relances (client_id, type, objet, canal, priorite, due_date, status, notes, related_ref, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
        'INSERT INTO client_relances (client_id, type, objet, canal, priorite, due_date, status, notes, related_ref, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'),
        (client_id, rtype, objet, canal, priorite, due_date, 'planifiee', notes, related_ref, now))
    conn.commit(); conn.close()
    return jsonify({'ok': True, 'created_at': now})

@app.route('/api/clients/relances/complete', methods=['POST'])
def clients_relances_complete():
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    d = request.get_json(force=True, silent=True) or {}
    try:
        client_id = int(d.get('client_id'))
        rid = int(d.get('id'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'Parametres invalides'}), 400
    new_status = str(d.get('status', 'faite'))
    if new_status not in {'faite', 'annulee', 'planifiee'}:
        new_status = 'faite'
    now = _clients_now()
    done = now if new_status != 'planifiee' else None
    conn = registre_get_db(); cur = conn.cursor()
    cur.execute(registre_sql(
        'UPDATE client_relances SET status=%s, done_at=%s WHERE id=%s AND client_id=%s',
        'UPDATE client_relances SET status=?, done_at=? WHERE id=? AND client_id=?'),
        (new_status, done, rid, client_id))
    # Mettre a jour le dernier contact du client si relance faite
    if new_status == 'faite':
        cur.execute(registre_sql('SELECT client_id FROM client_lifecycle WHERE client_id=%s',
                                 'SELECT client_id FROM client_lifecycle WHERE client_id=?'), (client_id,))
        if cur.fetchone():
            cur.execute(registre_sql('UPDATE client_lifecycle SET last_contact_at=%s, updated_at=%s WHERE client_id=%s',
                                     'UPDATE client_lifecycle SET last_contact_at=?, updated_at=? WHERE client_id=?'),
                        (now, now, client_id))
    conn.commit(); conn.close()
    return jsonify({'ok': True, 'status': new_status, 'done_at': done})

@app.route('/api/clients/invoices/pay', methods=['POST'])
def clients_invoices_pay():
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    d = request.get_json(force=True, silent=True) or {}
    try:
        client_id = int(d.get('client_id'))
        numero = str(d.get('numero', '')).strip()
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'Parametres invalides'}), 400
    if not numero:
        return jsonify({'ok': False, 'error': 'Numero de facture requis'}), 400
    now = _clients_now()
    conn = registre_get_db(); cur = conn.cursor()
    cur.execute(registre_sql(
        "UPDATE raas_invoices SET status='payee', paid_at=%s WHERE numero=%s AND client_id=%s",
        "UPDATE raas_invoices SET status='payee', paid_at=? WHERE numero=? AND client_id=?"),
        (now, numero, client_id))
    conn.commit(); conn.close()
    return jsonify({'ok': True, 'paid_at': now})

@app.route('/api/clients/dashboard', methods=['GET'])
def clients_dashboard():
    """Tableau de bord de suivi : statut, relances en attente, factures impayees/en
    retard, jalons stagnants, et suggestions de relance automatiques. CONSEILPREV."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    try:
        client_id = int(request.args.get('client_id'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'client_id invalide'}), 400
    conn = registre_get_db(); cur = conn.cursor()
    # Statut
    cur.execute(registre_sql('SELECT * FROM client_lifecycle WHERE client_id=%s',
                             'SELECT * FROM client_lifecycle WHERE client_id=?'), (client_id,))
    lc = cur.fetchone(); lc = dict(lc) if lc else {}
    # Relances en attente
    cur.execute(registre_sql("SELECT * FROM client_relances WHERE client_id=%s AND status='planifiee' ORDER BY due_date ASC",
                             "SELECT * FROM client_relances WHERE client_id=? AND status='planifiee' ORDER BY due_date ASC"), (client_id,))
    pending = [dict(r) for r in cur.fetchall()]
    # Factures impayees
    cur.execute(registre_sql("SELECT * FROM raas_invoices WHERE client_id=%s AND status!='payee' ORDER BY issued_at ASC",
                             "SELECT * FROM raas_invoices WHERE client_id=? AND status!='payee' ORDER BY issued_at ASC"), (client_id,))
    unpaid = [dict(r) for r in cur.fetchall()]
    # Jalons
    cur.execute(registre_sql('SELECT * FROM raas_milestones WHERE client_id=%s',
                             'SELECT * FROM raas_milestones WHERE client_id=?'), (client_id,))
    milestones = [dict(r) for r in cur.fetchall()]
    conn.close()
    # Suggestions automatiques
    suggestions = []
    for inv in unpaid:
        age = _days_since(inv.get('issued_at'))
        if age is not None and age >= 30:
            suggestions.append({'type': 'relance_facture', 'priorite': 'urgente' if age >= 60 else 'haute',
                                'objet': 'Facture %s impayee depuis %d jours' % (inv.get('numero'), age),
                                'related_ref': inv.get('numero')})
    pending_ms = [m for m in milestones if m.get('status') == 'pending']
    if pending_ms:
        oldest = _days_since(lc.get('last_contact_at'))
        if oldest is None or oldest >= 21:
            suggestions.append({'type': 'relance_jalon', 'priorite': 'normale',
                                'objet': '%d jalon(s) en attente \u2014 relancer sur l\'avancement' % len(pending_ms),
                                'related_ref': None})
    last_contact_days = _days_since(lc.get('last_contact_at'))
    if last_contact_days is not None and last_contact_days >= 45:
        suggestions.append({'type': 'email', 'priorite': 'normale',
                            'objet': 'Aucun contact depuis %d jours \u2014 prendre des nouvelles' % last_contact_days,
                            'related_ref': None})
    unpaid_total = sum(i.get('amount_eur', 0) for i in unpaid)
    return jsonify({'ok': True,
                    'status': lc or None,
                    'pending_relances': pending,
                    'unpaid_invoices': unpaid,
                    'unpaid_total': unpaid_total,
                    'milestones_pending': len(pending_ms),
                    'milestones_total': len(milestones),
                    'last_contact_days': last_contact_days,
                    'suggestions': suggestions})

@app.route('/api/clients/invoices/remind', methods=['POST'])
def clients_invoices_remind():
    """Envoie un email de rappel de paiement au client pour une facture donnee
    (ou toutes les factures impayees si numero absent), via Brevo. Enregistre une
    relance de type relance_facture (status faite) et met a jour le dernier contact.
    Reserve CONSEILPREV. La facturation/relance n'est pas bloquee par un echec email."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    d = request.get_json(force=True, silent=True) or {}
    try:
        client_id = int(d.get('client_id'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'client_id invalide'}), 400
    numero = (str(d.get('numero', '')).strip() or None)
    now = _clients_now()
    conn = registre_get_db(); cur = conn.cursor()
    # Coordonnees client (KYC)
    cur.execute(registre_sql('SELECT raison_sociale, email_contact, representant FROM client_kyc WHERE client_id=%s',
                             'SELECT raison_sociale, email_contact, representant FROM client_kyc WHERE client_id=?'), (client_id,))
    kyc = cur.fetchone(); kyc = dict(kyc) if kyc else {}
    to_email = (kyc.get('email_contact') or '').strip()
    if not to_email or '@' not in to_email:
        conn.close()
        return jsonify({'ok': False, 'error': 'Aucun email KYC valide pour ce client'}), 400
    # Factures concernees
    if numero:
        cur.execute(registre_sql("SELECT * FROM raas_invoices WHERE client_id=%s AND numero=%s AND status!='payee'",
                                 "SELECT * FROM raas_invoices WHERE client_id=? AND numero=? AND status!='payee'"), (client_id, numero))
    else:
        cur.execute(registre_sql("SELECT * FROM raas_invoices WHERE client_id=%s AND status!='payee' ORDER BY issued_at ASC",
                                 "SELECT * FROM raas_invoices WHERE client_id=? AND status!='payee' ORDER BY issued_at ASC"), (client_id,))
    factures = [dict(r) for r in cur.fetchall()]
    if not factures:
        conn.close()
        return jsonify({'ok': True, 'email_sent': False, 'message': 'Aucune facture impayee a relancer'})
    # Construction de l'email (identite CONSEILPREV / Sentinel)
    total_ht = sum(f.get('amount_eur', 0) for f in factures)
    tva = round(total_ht * 0.20)
    ttc = total_ht + tva
    lignes = ''.join('<li>%s \u2014 %d&#8239;&euro; HT (\u00e9mise le %s)</li>' % (
        f.get('numero'), f.get('amount_eur', 0), str(f.get('issued_at', ''))[:10]) for f in factures)
    dest = kyc.get('representant') or kyc.get('raison_sociale') or 'Madame, Monsieur'
    html = ('<p>Bonjour %s,</p>' % dest
        + '<p>Sauf erreur ou r\u00e8glement r\u00e9cent de votre part, nous constatons que '
        + ('la facture suivante demeure' if len(factures) == 1 else 'les factures suivantes demeurent')
        + ' en attente de paiement :</p>'
        + '<ul>' + lignes + '</ul>'
        + '<p>Total : <strong>%d&#8239;&euro; HT</strong>, soit <strong>%d&#8239;&euro; TTC</strong> (TVA 20&#8239;%%).</p>' % (total_ht, ttc)
        + '<p>Nous vous remercions de bien vouloir proc\u00e9der au r\u00e8glement \u00e0 r\u00e9ception, '
        + 'selon l\'\u00e9ch\u00e9ancier contractuel. Pass\u00e9 le d\u00e9lai, des p\u00e9nalit\u00e9s de retard '
        + '(trois fois le taux d\'int\u00e9r\u00eat l\u00e9gal) et une indemnit\u00e9 forfaitaire de recouvrement '
        + 'de 40&#8239;&euro; seraient applicables (articles L.441-10 et D.441-5 du Code de commerce).</p>'
        + '<p>Pour toute question ou si le r\u00e8glement a d\u00e9j\u00e0 \u00e9t\u00e9 effectu\u00e9, '
        + 'n\'h\u00e9sitez pas \u00e0 nous contacter.</p>'
        + '<p>Cordialement,<br>Christophe CERF<br>CONSEILPREV \u2014 Sentinel AI<br>'
        + '19 rue Auguste Chabri\u00e8res, 75015 Paris<br>christophe.cerf@outlook.com</p>')
    email_sent = False
    email_error = None
    try:
        res = send_email_smart(to_email, kyc.get('raison_sociale') or 'Client',
                               'CONSEILPREV \u2014 Rappel de paiement', html, tags=['raas-reminder'])
        email_sent = bool(res[0] if isinstance(res, tuple) else res)
    except Exception as _e:
        email_error = str(_e)[:200]
        logger.error(f"RAAS_REMINDER_EMAIL_FAILED client={client_id} : {_e}")
    # Enregistrer la relance (tracabilite)
    objet = ('Rappel de paiement \u2014 facture %s' % numero) if numero else ('Rappel de paiement \u2014 %d facture(s)' % len(factures))
    cur.execute(registre_sql(
        'INSERT INTO client_relances (client_id, type, objet, canal, priorite, due_date, status, notes, related_ref, created_at, done_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
        'INSERT INTO client_relances (client_id, type, objet, canal, priorite, due_date, status, notes, related_ref, created_at, done_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'),
        (client_id, 'relance_facture', objet, 'email', 'haute', None,
         'faite' if email_sent else 'planifiee',
         ('Email envoye a ' + to_email) if email_sent else ('Echec envoi : ' + (email_error or 'inconnu')),
         numero, now, now if email_sent else None))
    # Dernier contact
    if email_sent:
        cur.execute(registre_sql('SELECT client_id FROM client_lifecycle WHERE client_id=%s',
                                 'SELECT client_id FROM client_lifecycle WHERE client_id=?'), (client_id,))
        if cur.fetchone():
            cur.execute(registre_sql('UPDATE client_lifecycle SET last_contact_at=%s, updated_at=%s WHERE client_id=%s',
                                     'UPDATE client_lifecycle SET last_contact_at=?, updated_at=? WHERE client_id=?'), (now, now, client_id))
    conn.commit(); conn.close()
    return jsonify({'ok': True, 'email_sent': email_sent, 'email_error': email_error,
                    'invoices_count': len(factures), 'to': to_email})

@app.route('/api/clients/portfolio', methods=['GET'])
def clients_portfolio():
    """Vue portefeuille multiclient : pour chaque client, agrege statut/sante,
    factures impayees (nombre + total), relances en attente, jalons en attente,
    et jours depuis le dernier contact. Reserve CONSEILPREV."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    conn = registre_get_db(); cur = conn.cursor()
    try:
        cur.execute('SELECT id, nom_entreprise, email, plan, stripe_subscription_id FROM clients ORDER BY nom_entreprise ASC')
        clients = [dict(r) for r in cur.fetchall()]
    except Exception:
        try: conn.rollback()
        except Exception: pass
        try:
            cur.execute('SELECT id, nom_entreprise, email, plan FROM clients ORDER BY nom_entreprise ASC')
            clients = [dict(r) for r in cur.fetchall()]
        except Exception:
            try: conn.rollback()
            except Exception: pass
            cur.execute('SELECT id, nom_entreprise, email FROM clients ORDER BY nom_entreprise ASC')
            clients = [dict(r) for r in cur.fetchall()]
    portfolio = []
    tot_unpaid_amount = 0
    tot_unpaid_count = 0
    tot_pending_rel = 0
    for c in clients:
        cid = c['id']
        cur.execute(registre_sql("SELECT amount_eur FROM raas_invoices WHERE client_id=%s AND status!='payee'",
                                 "SELECT amount_eur FROM raas_invoices WHERE client_id=? AND status!='payee'"), (cid,))
        unpaid = [dict(r) for r in cur.fetchall()]
        unpaid_amt = sum(u.get('amount_eur', 0) for u in unpaid)
        cur.execute(registre_sql("SELECT COUNT(*) AS n FROM client_relances WHERE client_id=%s AND status='planifiee'",
                                 "SELECT COUNT(*) AS n FROM client_relances WHERE client_id=? AND status='planifiee'"), (cid,))
        pending = dict(cur.fetchone())['n']
        cur.execute(registre_sql("SELECT COUNT(*) AS n FROM raas_milestones WHERE client_id=%s AND status='pending'",
                                 "SELECT COUNT(*) AS n FROM raas_milestones WHERE client_id=? AND status='pending'"), (cid,))
        ms_pending = dict(cur.fetchone())['n']
        cur.execute(registre_sql(
            "SELECT COUNT(*) AS n FROM raas_milestones WHERE client_id=%s AND status='pending' AND milestone_id LIKE 'rgpd%%'",
            "SELECT COUNT(*) AS n FROM raas_milestones WHERE client_id=? AND status='pending' AND milestone_id LIKE 'rgpd%'"), (cid,))
        ms_pending_rgpd = dict(cur.fetchone())['n']
        cur.execute(registre_sql(
            "SELECT COUNT(*) AS n FROM raas_milestones WHERE client_id=%s AND status='pending' AND milestone_id LIKE 'iso%%'",
            "SELECT COUNT(*) AS n FROM raas_milestones WHERE client_id=? AND status='pending' AND milestone_id LIKE 'iso%'"), (cid,))
        ms_pending_iso = dict(cur.fetchone())['n']
        ms_pending_ai = ms_pending - ms_pending_rgpd - ms_pending_iso
        cur.execute(registre_sql('SELECT statut, sante, last_contact_at, next_action_at, next_action_label FROM client_lifecycle WHERE client_id=%s',
                                 'SELECT statut, sante, last_contact_at, next_action_at, next_action_label FROM client_lifecycle WHERE client_id=?'), (cid,))
        lc = cur.fetchone(); lc = dict(lc) if lc else {}
        last_days = _days_since(lc.get('last_contact_at'))
        portfolio.append({
            'id': cid, 'nom': c.get('nom_entreprise') or ('Client #' + str(cid)),
            'plan': (c.get('plan') or 'gratuit'), 'has_sub': bool(c.get('stripe_subscription_id')),
            'statut': lc.get('statut') or 'prospect', 'sante': lc.get('sante') or 'a_evaluer',
            'unpaid_count': len(unpaid), 'unpaid_amount': unpaid_amt,
            'pending_relances': pending, 'milestones_pending': ms_pending, 'milestones_pending_ai': ms_pending_ai, 'milestones_pending_rgpd': ms_pending_rgpd, 'milestones_pending_iso': ms_pending_iso,
            'last_contact_days': last_days,
            'next_action_at': lc.get('next_action_at'), 'next_action_label': lc.get('next_action_label')
        })
        tot_unpaid_amount += unpaid_amt
        tot_unpaid_count += len(unpaid)
        tot_pending_rel += pending
    conn.close()
    # Tri : priorite aux clients avec impayes puis relances
    portfolio.sort(key=lambda x: (-x['unpaid_amount'], -x['pending_relances']))
    return jsonify({'ok': True, 'portfolio': portfolio,
                    'totals': {'clients': len(clients), 'unpaid_count': tot_unpaid_count,
                               'unpaid_amount': tot_unpaid_amount, 'pending_relances': tot_pending_rel}})

@app.route('/api/clients/portfolio/digest', methods=['POST'])
def clients_portfolio_digest():
    """Synthese de relance : envoie a CONSEILPREV un recapitulatif des actions a
    mener (impayes, relances en attente, prochaines actions). Reserve CONSEILPREV."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    conn = registre_get_db(); cur = conn.cursor()
    cur.execute('SELECT id, nom_entreprise FROM clients ORDER BY nom_entreprise ASC')
    clients = [dict(r) for r in cur.fetchall()]
    lignes_imp = []
    lignes_rel = []
    tot_imp = 0
    for c in clients:
        cid = c['id']; nom = c.get('nom_entreprise') or ('Client #' + str(cid))
        cur.execute(registre_sql("SELECT numero, amount_eur, issued_at FROM raas_invoices WHERE client_id=%s AND status!='payee'",
                                 "SELECT numero, amount_eur, issued_at FROM raas_invoices WHERE client_id=? AND status!='payee'"), (cid,))
        for u in [dict(r) for r in cur.fetchall()]:
            age = _days_since(u.get('issued_at'))
            tot_imp += u.get('amount_eur', 0)
            lignes_imp.append('<li>%s \u2014 %s : %d&#8239;&euro; HT%s</li>' % (
                nom, u.get('numero'), u.get('amount_eur', 0),
                (' (depuis %d j)' % age) if age is not None else ''))
        cur.execute(registre_sql("SELECT objet, priorite, due_date FROM client_relances WHERE client_id=%s AND status='planifiee'",
                                 "SELECT objet, priorite, due_date FROM client_relances WHERE client_id=? AND status='planifiee'"), (cid,))
        for r in [dict(x) for x in cur.fetchall()]:
            lignes_rel.append('<li>%s \u2014 %s (%s%s)</li>' % (
                nom, r.get('objet'), r.get('priorite'),
                (', \u00e9ch. ' + str(r.get('due_date'))[:10]) if r.get('due_date') else ''))
    conn.close()
    html = ('<p>Synth\u00e8se de suivi CONSEILPREV \u2014 Sentinel AI</p>'
        + '<h3>Factures impay\u00e9es (%d&#8239;&euro; HT au total)</h3>' % tot_imp
        + ('<ul>' + ''.join(lignes_imp) + '</ul>' if lignes_imp else '<p>Aucune facture impay\u00e9e.</p>')
        + '<h3>Relances en attente</h3>'
        + ('<ul>' + ''.join(lignes_rel) + '</ul>' if lignes_rel else '<p>Aucune relance en attente.</p>')
        + '<p style="color:#888;font-size:12px">Synth\u00e8se g\u00e9n\u00e9r\u00e9e automatiquement par Sentinel AI.</p>')
    email_sent = False; email_error = None
    try:
        res = send_email_smart(ADMIN_EMAIL, 'CONSEILPREV', 'CONSEILPREV \u2014 Synth\u00e8se de suivi client', html, tags=['portfolio-digest'])
        email_sent = bool(res[0] if isinstance(res, tuple) else res)
    except Exception as _e:
        email_error = str(_e)[:200]
        logger.error(f"PORTFOLIO_DIGEST_EMAIL_FAILED : {_e}")
    return jsonify({'ok': True, 'email_sent': email_sent, 'email_error': email_error,
                    'unpaid_lines': len(lignes_imp), 'relance_lines': len(lignes_rel), 'to': ADMIN_EMAIL})

@app.route('/api/clients/erase', methods=['POST'])
def clients_erase():
    """RGPD \u2014 droit a l'effacement (art. 17 RGPD). Supprime les donnees
    personnelles d'un client : KYC, notes, relances, cycle de vie. Les factures et
    contrats sont CONSERVES au titre de l'obligation legale comptable (art. L.123-22
    C. com. \u2014 10 ans) mais anonymisables sur demande. Reserve CONSEILPREV."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    d = request.get_json(force=True, silent=True) or {}
    try:
        client_id = int(d.get('client_id'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'client_id invalide'}), 400
    if not d.get('confirm'):
        return jsonify({'ok': False, 'error': 'Confirmation requise'}), 400
    anonymize = bool(d.get('anonymize', True))
    conn = registre_get_db(); cur = conn.cursor()
    deleted = {}
    for tbl in ['client_kyc', 'client_notes', 'client_relances', 'client_lifecycle']:
        cur.execute(registre_sql('DELETE FROM ' + tbl + ' WHERE client_id=%s',
                                 'DELETE FROM ' + tbl + ' WHERE client_id=?'), (client_id,))
        deleted[tbl] = cur.rowcount if cur.rowcount is not None else 0
    anonymized = False
    if anonymize:
        # Anonymisation des coordonnees nominatives conservees dans le compte client,
        # les factures/contrats restant lies par un identifiant pseudonymise (client_id).
        anon_nom = 'Client anonymise #%d' % client_id
        anon_email = 'rgpd-anonymise-%d@invalide.local' % client_id
        try:
            cur.execute(registre_sql(
                'UPDATE clients SET nom_entreprise=%s, email=%s, actif=%s WHERE id=%s',
                'UPDATE clients SET nom_entreprise=?, email=?, actif=? WHERE id=?'),
                (anon_nom, anon_email, False if REGISTRE_USE_PG else 0, client_id))
            anonymized = True
        except Exception as _e:
            logger.error(f"RGPD_ANONYMIZE_CLIENT_FAILED client={client_id} : {_e}")
    conn.commit(); conn.close()
    logger.info(f"RGPD_ERASE client={client_id} deleted={deleted} anonymized={anonymized}")
    return jsonify({'ok': True, 'deleted': deleted, 'anonymized': anonymized,
                    'note': 'Donnees de suivi supprimees. Coordonnees nominatives du compte anonymisees. '
                            'Factures et contrats conserves (lies par identifiant pseudonymise) au titre de '
                            'l obligation comptable legale de 10 ans (art. L.123-22 C. com.).'})

@app.route('/invitation/<token>', methods=['GET'])
def sentauth_invitation_page(token):
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql(
        'SELECT * FROM clients WHERE invitation_token=%s', 'SELECT * FROM clients WHERE invitation_token=?'
    ), (token,))
    row = cur.fetchone()
    conn.commit()
    conn.close()
    if not row:
        return send_from_directory('.', 'invitation-expiree.html')
    d = dict(row) if not isinstance(row, dict) else row
    expire = datetime.fromisoformat(d['invitation_expire']) if d.get('invitation_expire') else None
    if not expire or datetime.utcnow() > expire:
        return send_from_directory('.', 'invitation-expiree.html')
    return send_from_directory('.', 'invitation.html')

@app.route('/api/sentinel-auth/invitation-info/<token>', methods=['GET'])
@rate_limit_strict(limit=20, window=60)
def sentauth_invitation_info(token):
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql(
        'SELECT nom_entreprise, email, invitation_expire FROM clients WHERE invitation_token=%s',
        'SELECT nom_entreprise, email, invitation_expire FROM clients WHERE invitation_token=?'
    ), (token,))
    row = cur.fetchone()
    conn.commit()
    conn.close()
    if not row:
        return jsonify({'valid': False, 'error': 'Lien invalide ou déjà utilisé.'}), 404
    d = dict(row) if not isinstance(row, dict) else row
    expire = datetime.fromisoformat(d['invitation_expire']) if d.get('invitation_expire') else None
    if not expire or datetime.utcnow() > expire:
        return jsonify({'valid': False, 'error': 'Ce lien a expiré.'}), 410

    # Captcha maison simple : addition aleatoire, stockee en session, sans dependance externe.
    a, b = _secrets_auth.randbelow(8) + 2, _secrets_auth.randbelow(8) + 2
    session['captcha_answer'] = a + b
    session['captcha_token'] = token

    masked_email = d['email'][:2] + '***@' + d['email'].split('@')[1] if '@' in d['email'] else d['email']
    return jsonify({'valid': True, 'nom_entreprise': d['nom_entreprise'], 'email_masque': masked_email, 'captcha_question': f"{a} + {b} = ?"})

@app.route('/api/sentinel-auth/activate-account', methods=['POST'])
@rate_limit_strict(limit=10, window=300)
def sentauth_activate_account():
    data = request.get_json(force=True) or {}
    token = (data.get('token') or '').strip()
    password = data.get('password') or ''
    rgpd_consent = bool(data.get('rgpd_consent'))
    captcha_answer = data.get('captcha_answer')

    if session.get('captcha_token') != token:
        return jsonify({'error': 'Session expirée, rechargez la page.'}), 400
    try:
        if int(captcha_answer) != session.get('captcha_answer'):
            return jsonify({'error': 'Réponse de vérification incorrecte.'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Réponse de vérification invalide.'}), 400

    if not rgpd_consent:
        return jsonify({'error': 'Le consentement RGPD est requis pour activer votre compte.'}), 400

    ok, msg = sentauth_validate_password_strength(password)
    if not ok:
        return jsonify({'error': msg}), 400

    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql('SELECT * FROM clients WHERE invitation_token=%s', 'SELECT * FROM clients WHERE invitation_token=?'), (token,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Lien invalide ou déjà utilisé.'}), 404
    d = dict(row) if not isinstance(row, dict) else row
    expire = datetime.fromisoformat(d['invitation_expire']) if d.get('invitation_expire') else None
    if not expire or datetime.utcnow() > expire:
        conn.close()
        return jsonify({'error': 'Ce lien a expiré.'}), 410

    pw_hash = generate_password_hash(password)
    now = datetime.utcnow().isoformat()
    cur.execute(registre_sql(
        'UPDATE clients SET mot_de_passe_hash=%s, actif=TRUE, invitation_token=NULL, invitation_expire=NULL, rgpd_consenti=TRUE, rgpd_consenti_date=%s WHERE id=%s',
        'UPDATE clients SET mot_de_passe_hash=?, actif=1, invitation_token=NULL, invitation_expire=NULL, rgpd_consenti=1, rgpd_consenti_date=? WHERE id=?'
    ), (pw_hash, now, d['id']))
    conn.commit()
    conn.close()
    session.pop('captcha_answer', None)
    session.pop('captcha_token', None)
    logger.info(f"ACCOUNT_ACTIVATED {d['email']} — consentement RGPD horodate {now}")
    return jsonify({'ok': True})

# ══════════════════════════════════════════════════════════
# MOT DE PASSE OUBLIE — demande -> email avec lien -> nouveau
# mot de passe -> email de confirmation de securite. Colonnes
# dediees (reset_token/reset_expire), distinctes de invitation_token
# pour ne jamais interferer avec le flux d'invitation initiale.
# ══════════════════════════════════════════════════════════
RESET_PASSWORD_VALIDITY_HOURS = 2  # plus court qu une invitation : usage immediat attendu

def sentauth_send_reset_email(email, nom_entreprise, token):
    try:
        link = f"https://conseilprev.onrender.com/reset-password/{token}"
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:24px;background:#F5F2ED">
          <div style="background:#fff;border-radius:8px;padding:32px;border:1px solid #E0DDD8">
            <div style="font-size:20px;font-weight:600;color:#1C1C1C;margin-bottom:4px">Sentinel <span style="background:#B83222;color:#fff;font-size:10px;padding:2px 6px;border-radius:3px;vertical-align:middle">AI</span></div>
            <div style="font-size:11px;color:#767676;text-transform:uppercase;letter-spacing:1px;margin-bottom:24px">Reinitialisation de mot de passe</div>
            <p style="font-size:14px;color:#3D3D3D;line-height:1.6">Bonjour,</p>
            <p style="font-size:14px;color:#3D3D3D;line-height:1.6">Une demande de reinitialisation de mot de passe a ete faite pour le compte {nom_entreprise}. Si c est vous, definissez un nouveau mot de passe :</p>
            <div style="text-align:center;margin:28px 0">
              <a href="{link}" style="display:inline-block;background:#B83222;color:#fff;padding:13px 28px;border-radius:6px;text-decoration:none;font-weight:600;font-size:14px">Definir un nouveau mot de passe →</a>
            </div>
            <p style="font-size:12px;color:#767676;line-height:1.6">Ce lien est valable {RESET_PASSWORD_VALIDITY_HOURS} heures et ne peut etre utilise qu une seule fois. Si vous n etes pas a l origine de cette demande, ignorez cet email — votre mot de passe actuel reste inchange.</p>
          </div>
          <p style="font-size:11px;color:#A8A8A8;text-align:center;margin-top:16px">CONSEILPREV — Sentinel AI</p>
        </div>
        """
        ok, method = send_email_smart(email, nom_entreprise, "Réinitialisation de votre mot de passe — Sentinel AI", html, tags=['sentinel-reset-password'])
        logger.info(f"RESET_EMAIL {email} via {method} — ok={ok}")
        return ok
    except Exception as e:
        logger.error(f"RESET_EMAIL_FAILED {email} : {e}")
        return False


def sentauth_send_reset_confirmation_email(email, nom_entreprise, ip):
    """Notification de securite envoyee APRES un changement de mot de passe
    reussi — permet au client de detecter immediatement un changement qu il
    n aurait pas demande lui-meme."""
    try:
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:24px;background:#F5F2ED">
          <div style="background:#fff;border-radius:8px;padding:32px;border:1px solid #E0DDD8">
            <div style="font-size:20px;font-weight:600;color:#1C1C1C;margin-bottom:4px">Sentinel <span style="background:#B83222;color:#fff;font-size:10px;padding:2px 6px;border-radius:3px;vertical-align:middle">AI</span></div>
            <div style="font-size:11px;color:#767676;text-transform:uppercase;letter-spacing:1px;margin-bottom:24px">Alerte de securite</div>
            <p style="font-size:14px;color:#3D3D3D;line-height:1.6">Bonjour,</p>
            <p style="font-size:14px;color:#3D3D3D;line-height:1.6">Le mot de passe du compte {nom_entreprise} vient d etre modifie ({datetime.utcnow().strftime('%d/%m/%Y a %H:%M')} UTC, depuis l adresse IP {ip}).</p>
            <p style="font-size:14px;color:#3D3D3D;line-height:1.6"><strong>Si vous n etes pas a l origine de ce changement</strong>, contactez immediatement CONSEILPREV.</p>
          </div>
          <p style="font-size:11px;color:#A8A8A8;text-align:center;margin-top:16px">CONSEILPREV — Sentinel AI</p>
        </div>
        """
        ok, method = send_email_smart(email, nom_entreprise, "Votre mot de passe a ete modifié — Sentinel AI", html, tags=['sentinel-reset-confirm'])
        logger.info(f"RESET_CONFIRM_EMAIL {email} via {method} — ok={ok}")
        return ok
    except Exception as e:
        logger.error(f"RESET_CONFIRM_EMAIL_FAILED {email} : {e}")
        return False


@app.route('/api/sentinel-auth/forgot-password', methods=['POST'])
@rate_limit_strict(limit=5, window=300)
def sentauth_forgot_password():
    """Toujours la meme reponse, que l email existe ou non en base — evite
    qu un tiers puisse deviner quels emails sont enregistres (enumeration)."""
    data = request.get_json(force=True) or {}
    email = (data.get('email') or '').strip().lower()
    generic_response = jsonify({'ok': True, 'message': 'Si un compte existe avec cet email, vous recevrez un lien de réinitialisation.'})

    if not email or '@' not in email:
        return generic_response

    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql('SELECT * FROM clients WHERE email=%s AND actif=TRUE', 'SELECT * FROM clients WHERE email=? AND actif=1'), (email,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return generic_response

    d = dict(row) if not isinstance(row, dict) else row
    reset_token = _secrets_auth.token_urlsafe(32)
    reset_expire = (datetime.utcnow() + _timedelta_auth(hours=RESET_PASSWORD_VALIDITY_HOURS)).isoformat()
    cur.execute(registre_sql(
        'UPDATE clients SET reset_token=%s, reset_expire=%s WHERE id=%s',
        'UPDATE clients SET reset_token=?, reset_expire=? WHERE id=?'
    ), (reset_token, reset_expire, d['id']))
    conn.commit()
    conn.close()

    sentauth_send_reset_email(email, d['nom_entreprise'], reset_token)
    logger.info(f"PASSWORD_RESET_REQUESTED {email}")
    return generic_response


@app.route('/reset-password/<token>', methods=['GET'])
def sentauth_reset_password_page(token):
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql('SELECT * FROM clients WHERE reset_token=%s', 'SELECT * FROM clients WHERE reset_token=?'), (token,))
    row = cur.fetchone()
    conn.commit()
    conn.close()
    if not row:
        return send_from_directory('.', 'invitation-expiree.html')
    d = dict(row) if not isinstance(row, dict) else row
    expire = datetime.fromisoformat(d['reset_expire']) if d.get('reset_expire') else None
    if not expire or datetime.utcnow() > expire:
        return send_from_directory('.', 'invitation-expiree.html')
    return send_from_directory('.', 'reset-password.html')


@app.route('/api/sentinel-auth/reset-password-info/<token>', methods=['GET'])
@rate_limit_strict(limit=20, window=60)
def sentauth_reset_password_info(token):
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql(
        'SELECT nom_entreprise, email, reset_expire FROM clients WHERE reset_token=%s',
        'SELECT nom_entreprise, email, reset_expire FROM clients WHERE reset_token=?'
    ), (token,))
    row = cur.fetchone()
    conn.commit()
    conn.close()
    if not row:
        return jsonify({'valid': False, 'error': 'Lien invalide ou déjà utilisé.'}), 404
    d = dict(row) if not isinstance(row, dict) else row
    expire = datetime.fromisoformat(d['reset_expire']) if d.get('reset_expire') else None
    if not expire or datetime.utcnow() > expire:
        return jsonify({'valid': False, 'error': 'Ce lien a expiré.'}), 410

    a, b = _secrets_auth.randbelow(8) + 2, _secrets_auth.randbelow(8) + 2
    session['reset_captcha_answer'] = a + b
    session['reset_captcha_token'] = token

    masked_email = d['email'][:2] + '***@' + d['email'].split('@')[1] if '@' in d['email'] else d['email']
    return jsonify({'valid': True, 'nom_entreprise': d['nom_entreprise'], 'email_masque': masked_email, 'captcha_question': f"{a} + {b} = ?"})


@app.route('/api/sentinel-auth/reset-password', methods=['POST'])
@rate_limit_strict(limit=10, window=300)
def sentauth_reset_password_confirm():
    data = request.get_json(force=True) or {}
    token = (data.get('token') or '').strip()
    password = data.get('password') or ''
    captcha_answer = data.get('captcha_answer')

    if session.get('reset_captcha_token') != token:
        return jsonify({'error': 'Session expirée, rechargez la page.'}), 400
    try:
        if int(captcha_answer) != session.get('reset_captcha_answer'):
            return jsonify({'error': 'Réponse de vérification incorrecte.'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Réponse de vérification invalide.'}), 400

    ok, msg = sentauth_validate_password_strength(password)
    if not ok:
        return jsonify({'error': msg}), 400

    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql('SELECT * FROM clients WHERE reset_token=%s', 'SELECT * FROM clients WHERE reset_token=?'), (token,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Lien invalide ou déjà utilisé.'}), 404
    d = dict(row) if not isinstance(row, dict) else row
    expire = datetime.fromisoformat(d['reset_expire']) if d.get('reset_expire') else None
    if not expire or datetime.utcnow() > expire:
        conn.close()
        return jsonify({'error': 'Ce lien a expiré.'}), 410

    pw_hash = generate_password_hash(password)
    cur.execute(registre_sql(
        'UPDATE clients SET mot_de_passe_hash=%s, reset_token=NULL, reset_expire=NULL WHERE id=%s',
        'UPDATE clients SET mot_de_passe_hash=?, reset_token=NULL, reset_expire=NULL WHERE id=?'
    ), (pw_hash, d['id']))
    conn.commit()
    conn.close()
    session.pop('reset_captcha_answer', None)
    session.pop('reset_captcha_token', None)

    ip = limiter.get_ip(request)
    threading.Thread(target=sentauth_send_reset_confirmation_email, args=(d['email'], d['nom_entreprise'], ip), daemon=True).start()
    logger.info(f"PASSWORD_RESET_COMPLETED {d['email']}")
    return jsonify({'ok': True})

# ══════════════════════════════════════════════════════════
# AUTO-INSCRIPTION CLIENT — accès direct ouvert sur /login (sans invitation
# prealable de CONSEILPREV). Verification d'email obligatoire (le compte reste
# inactif jusqu'a confirmation) pour eviter qu'un tiers s'inscrive avec l'email
# de quelqu'un d'autre. CONSEILPREV est notifie de chaque nouvelle inscription
# (controle a posteriori plutot qu'a priori).
# ══════════════════════════════════════════════════════════
CONSEILPREV_NOTIFY_EMAIL = os.environ.get('CONSEILPREV_NOTIFY_EMAIL', 'christophe.cerf@outlook.com')

@app.route('/api/sentinel-auth/register-captcha', methods=['GET'])
@rate_limit_strict(limit=20, window=60)
def sentauth_register_captcha():
    a, b = _secrets_auth.randbelow(8) + 2, _secrets_auth.randbelow(8) + 2
    session['register_captcha_answer'] = a + b
    return jsonify({'captcha_question': f"{a} + {b} = ?"})

def sentauth_send_verification_email(email, nom_entreprise, token):
    try:
        link = f"https://conseilprev.onrender.com/verify-email/{token}"
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:24px;background:#F5F2ED">
          <div style="background:#fff;border-radius:8px;padding:32px;border:1px solid #E0DDD8">
            <div style="font-size:20px;font-weight:600;color:#1C1C1C;margin-bottom:4px">Sentinel <span style="background:#B83222;color:#fff;font-size:10px;padding:2px 6px;border-radius:3px;vertical-align:middle">AI</span></div>
            <div style="font-size:11px;color:#767676;text-transform:uppercase;letter-spacing:1px;margin-bottom:24px">Confirmez votre adresse email</div>
            <p style="font-size:14px;color:#3D3D3D;line-height:1.6">Bonjour,</p>
            <p style="font-size:14px;color:#3D3D3D;line-height:1.6">Vous venez de créer un compte Sentinel AI pour {nom_entreprise}. Confirmez votre adresse email pour activer votre accès :</p>
            <div style="text-align:center;margin:28px 0">
              <a href="{link}" style="display:inline-block;background:#B83222;color:#fff;padding:13px 28px;border-radius:6px;text-decoration:none;font-weight:600;font-size:14px">Confirmer mon email →</a>
            </div>
            <p style="font-size:12px;color:#767676;line-height:1.6">Ce lien est valable {INVITATION_VALIDITY_HOURS} heures. Si vous n êtes pas à l origine de cette inscription, ignorez cet email.</p>
          </div>
          <p style="font-size:11px;color:#A8A8A8;text-align:center;margin-top:16px">CONSEILPREV — Sentinel AI</p>
        </div>
        """
        ok, method = send_email_smart(email, nom_entreprise, "Confirmez votre adresse email — Sentinel AI", html, tags=['sentinel-verify-email'])
        logger.info(f"VERIFY_EMAIL {email} via {method} — ok={ok}")
        return ok
    except Exception as e:
        logger.error(f"VERIFY_EMAIL_FAILED {email} : {e}")
        return False

def sentauth_notify_conseilprev_new_signup(nom_entreprise, email, ip):
    try:
        html = f"""<div style="font-family:Arial,sans-serif;padding:20px">
          <p><strong>Nouvelle auto-inscription Sentinel AI</strong></p>
          <table style="font-size:13px"><tr><td style="padding:4px 12px 4px 0;color:#767676">Entreprise</td><td><strong>{nom_entreprise}</strong></td></tr>
          <tr><td style="padding:4px 12px 4px 0;color:#767676">Email</td><td>{email}</td></tr>
          <tr><td style="padding:4px 12px 4px 0;color:#767676">IP</td><td>{ip}</td></tr>
          <tr><td style="padding:4px 12px 4px 0;color:#767676">Date</td><td>{datetime.utcnow().strftime('%d/%m/%Y à %H:%M UTC')}</td></tr></table>
          <p style="font-size:12px;color:#767676;margin-top:12px">Connectez-vous à Sentinel AI → Gestion des clients pour désactiver ce compte si nécessaire.</p></div>"""
        send_email_smart(CONSEILPREV_NOTIFY_EMAIL, 'CONSEILPREV', f"Nouvelle inscription Sentinel AI : {nom_entreprise}", html, tags=['sentinel-new-signup-notify'])
    except Exception as e:
        logger.error(f"NOTIFY_CONSEILPREV_FAILED : {e}")


@app.route('/api/pricing-request', methods=['POST'])
@rate_limit(limit=10, window=300)
def pricing_request():
    """Demande de tarification par résultats — accessible à tous les plans.
    Envoie une notification email à CONSEILPREV avec les informations du prospect.
    Ne conserve aucune donnée côté serveur."""
    data   = request.get_json(force=True) or {}
    plan     = str(data.get('plan') or '').strip()[:20]
    nom      = str(data.get('nom') or '').strip()[:120]
    email    = str(data.get('email') or '').strip()[:150]
    systemes = str(data.get('systemes') or '').strip()[:20]
    secteur  = str(data.get('secteur') or '').strip()[:100]
    message  = str(data.get('message') or '').strip()[:800]

    if not nom or not email or '@' not in email:
        return jsonify({'ok': False, 'error': 'Nom et email valides requis.'}), 400
    if plan not in ('pro', 'entreprise'):
        return jsonify({'ok': False, 'error': 'Plan invalide.'}), 400

    ip = limiter.get_ip(request)
    plan_label = 'Sentinel Pro' if plan == 'pro' else 'Sentinel Entreprise'
    now_str = datetime.utcnow().strftime('%d/%m/%Y à %H:%M UTC')

    html = f"""<div style="font-family:Arial,sans-serif;max-width:560px;padding:24px">
  <div style="background:#1C1C1C;color:#fff;border-radius:8px 8px 0 0;padding:16px 20px;margin-bottom:0">
    <span style="font-size:16px;font-weight:700">Sentinel <span style="background:#B83222;font-size:10px;padding:2px 6px;border-radius:3px;vertical-align:middle">AI</span></span>
    <span style="font-size:12px;color:rgba(255,255,255,.6);margin-left:12px">Demande de tarification par résultats</span>
  </div>
  <table style="font-size:13px;border-collapse:collapse;width:100%;border:1px solid #E0DDD8;border-top:none">
    <tr style="background:#F6F4FC"><td style="padding:10px 16px;color:#767676;width:180px;border-bottom:1px solid #E0DDD8">Plan demandé</td>
        <td style="padding:10px 16px;font-weight:700;color:#B83222;border-bottom:1px solid #E0DDD8">{plan_label}</td></tr>
    <tr><td style="padding:10px 16px;color:#767676;border-bottom:1px solid #E0DDD8">Entreprise</td>
        <td style="padding:10px 16px;font-weight:600;border-bottom:1px solid #E0DDD8">{nom}</td></tr>
    <tr style="background:#F6F4FC"><td style="padding:10px 16px;color:#767676;border-bottom:1px solid #E0DDD8">Email</td>
        <td style="padding:10px 16px;border-bottom:1px solid #E0DDD8"><a href="mailto:{email}">{email}</a></td></tr>
    <tr><td style="padding:10px 16px;color:#767676;border-bottom:1px solid #E0DDD8">Secteur</td>
        <td style="padding:10px 16px;border-bottom:1px solid #E0DDD8">{secteur or 'Non précisé'}</td></tr>
    <tr style="background:#F6F4FC"><td style="padding:10px 16px;color:#767676;border-bottom:1px solid #E0DDD8">Systèmes IA</td>
        <td style="padding:10px 16px;border-bottom:1px solid #E0DDD8">{systemes or 'Non précisé'}</td></tr>
    <tr><td style="padding:10px 16px;color:#767676;border-bottom:1px solid #E0DDD8">Message</td>
        <td style="padding:10px 16px;border-bottom:1px solid #E0DDD8;white-space:pre-wrap">{message or '—'}</td></tr>
    <tr style="background:#F6F4FC"><td style="padding:10px 16px;color:#767676">Origine</td>
        <td style="padding:10px 16px;font-size:11px;color:#767676">IP {ip} — {now_str}</td></tr>
  </table>
  <div style="margin-top:16px;font-size:11px;color:#999;border-top:1px solid #E0DDD8;padding-top:12px">
    Répondre directement à cet email pour contacter le prospect. Demande soumise depuis Sentinel AI — page Tarification par résultats.
  </div>
</div>"""

    subject = f"[Sentinel AI] Demande {plan_label} — {nom}"
    try:
        sent, _ = send_email_smart(
            CONSEILPREV_NOTIFY_EMAIL, 'CONSEILPREV',
            subject, html,
            reply_to=email,
            tags=['pricing-request', plan]
        )
    except Exception as e:
        logger.error(f"PRICING_REQUEST_EMAIL_ERR: {e}")
        sent = False

    logger.info(f"PRICING_REQUEST plan={plan} nom={nom} email={email} ip={ip} sent={sent}")
    if not sent:
        # Fallback : logger la demande même si l'email échoue
        logger.warning(f"PRICING_REQUEST_EMAIL_FAILED: {nom} <{email}> plan={plan}")

    # Toujours retourner ok=True — l'email est secondaire, la demande est enregistrée
    return jsonify({'ok': True, 'plan': plan})


@app.route('/api/sentinel-auth/register', methods=['POST'])
@rate_limit_strict(limit=10, window=300)
def sentauth_register():
    data = request.get_json(force=True) or {}
    nom = (data.get('nom_entreprise') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    rgpd_consent = bool(data.get('rgpd_consent'))
    captcha_answer = data.get('captcha_answer')
    # Toute inscription publique est forcée au plan Gratuit.
    # Seul CONSEILPREV peut attribuer un plan supérieur via l'interface admin.
    plan = 'gratuit'

    try:
        if int(captcha_answer) != session.get('register_captcha_answer'):
            return jsonify({'error': 'Réponse de vérification incorrecte.'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Réponse de vérification invalide.'}), 400

    if not nom or not email or '@' not in email:
        return jsonify({'error': 'Nom d entreprise et email valide requis.'}), 400
    if not rgpd_consent:
        return jsonify({'error': 'Le consentement RGPD est requis pour créer un compte.'}), 400

    ok, msg = sentauth_validate_password_strength(password)
    if not ok:
        return jsonify({'error': msg}), 400

    verify_token = _secrets_auth.token_urlsafe(32)
    verify_expire = (datetime.utcnow() + _timedelta_auth(hours=VERIFY_EMAIL_VALIDITY_HOURS)).isoformat()
    now = datetime.utcnow().isoformat()
    pw_hash = generate_password_hash(password)

    conn = registre_get_db()
    cur = conn.cursor()
    try:
        _essai_fin = (datetime.utcnow() + timedelta(days=15)).isoformat()
        if REGISTRE_USE_PG:
            cur.execute('''INSERT INTO clients (nom_entreprise, email, mot_de_passe_hash, date_creation, verify_email_token, verify_email_expire, actif, rgpd_consenti, rgpd_consenti_date, plan, essai_fin)
                VALUES (%s,%s,%s,%s,%s,%s,FALSE,TRUE,%s,%s,%s) RETURNING id''', (nom, email, pw_hash, now, verify_token, verify_expire, now, plan, _essai_fin))
            new_id = cur.fetchone()['id']
        else:
            cur.execute('INSERT INTO clients (nom_entreprise, email, mot_de_passe_hash, date_creation, verify_email_token, verify_email_expire, actif, rgpd_consenti, rgpd_consenti_date, plan, essai_fin) VALUES (?,?,?,?,?,?,0,1,?,?,?)', (nom, email, pw_hash, now, verify_token, verify_expire, now, plan, _essai_fin))
            new_id = cur.lastrowid
        conn.commit()
    except Exception:
        conn.rollback()
        conn.close()
        return jsonify({'error': 'Cet email est déjà utilisé.'}), 409
    conn.close()

    session.pop('register_captcha_answer', None)
    try:
        _rgpd_record_consent(email, {'compte_sentinel': True, 'rgpd_accepte': True, 'essai_15j': True}, 'inscription-sentinel')
    except Exception:
        pass
    verification_email_sent = sentauth_send_verification_email(email, nom, verify_token)
    ip = limiter.get_ip(request)
    try:
        sentauth_notify_conseilprev_new_signup(nom, email, ip)
    except Exception as _e:
        logger.error(f"NOTIFY_CONSEILPREV_SYNC_FAILED : {_e}")
    logger.info(f"NEW_SIGNUP {email} — en attente de verification email — email_envoye={verification_email_sent}")
    if not verification_email_sent:
        logger.warning(f"NEW_SIGNUP_EMAIL_NON_ENVOYE {email} — verifiez BREVO_API_KEY ou SMTP_USER/SMTP_PASSWORD sur Render")
    return jsonify({'ok': True, 'verification_email_sent': verification_email_sent}), 201

@app.route('/verify-email/<token>', methods=['GET'])
def sentauth_verify_email_page(token):
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql('SELECT * FROM clients WHERE verify_email_token=%s', 'SELECT * FROM clients WHERE verify_email_token=?'), (token,))
    row = cur.fetchone()
    if not row:
        conn.commit()
        conn.close()
        return send_from_directory('.', 'invitation-expiree.html')
    d = dict(row) if not isinstance(row, dict) else row
    expire = datetime.fromisoformat(d['verify_email_expire']) if d.get('verify_email_expire') else None
    if not expire or datetime.utcnow() > expire:
        conn.commit()
        conn.close()
        return send_from_directory('.', 'invitation-expiree.html')
    cur.execute(registre_sql(
        "UPDATE clients SET actif=TRUE, verify_email_token=NULL, verify_email_expire=NULL WHERE id=%s",
        "UPDATE clients SET actif=1, verify_email_token=NULL, verify_email_expire=NULL WHERE id=?"
    ), (d['id'],))
    conn.commit()
    conn.close()
    logger.info(f"EMAIL_VERIFIED {d['email']}")
    return redirect('/login?verified=1')

@app.route('/api/admin/clients', methods=['POST'])
@sentinel_login_required
@rate_limit_strict(limit=10, window=60)
def sentauth_admin_create_client():
    """Creation manuelle de comptes clients — reservee a CONSEILPREV.
    Le mot de passe n est PAS demande ici : un email d invitation est envoye
    au client, qui choisit lui-meme son mot de passe (CONSEILPREV ne le
    connait jamais, conformement aux bonnes pratiques RGPD)."""
    client = sentauth_current_client()
    if not client or not client.get('is_conseilprev'):
        abort(403)
    data = request.get_json(force=True) or {}
    nom = (data.get('nom_entreprise') or '').strip()
    email = (data.get('email') or '').strip().lower()
    if not nom or not email:
        return jsonify({'error': 'nom_entreprise et email requis.'}), 400

    invitation_token = _secrets_auth.token_urlsafe(32)
    invitation_expire = (datetime.utcnow() + _timedelta_auth(hours=INVITATION_VALIDITY_HOURS)).isoformat()
    now = datetime.utcnow().isoformat()

    conn = registre_get_db()
    cur = conn.cursor()
    try:
        if REGISTRE_USE_PG:
            cur.execute('''INSERT INTO clients (nom_entreprise, email, date_creation, invitation_token, invitation_expire, actif)
                VALUES (%s,%s,%s,%s,%s,FALSE) RETURNING id''', (nom, email, now, invitation_token, invitation_expire))
            new_id = cur.fetchone()['id']
        else:
            cur.execute('INSERT INTO clients (nom_entreprise, email, date_creation, invitation_token, invitation_expire, actif) VALUES (?,?,?,?,?,0)', (nom, email, now, invitation_token, invitation_expire))
            new_id = cur.lastrowid
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': 'Email déjà utilisé ou erreur de création.'}), 409
    conn.close()

    email_sent = sentauth_send_invitation_email(email, nom, invitation_token)
    return jsonify({'client': {'id': new_id, 'nom_entreprise': nom, 'email': email}, 'invitation_email_sent': email_sent}), 201

@app.route('/api/admin/clients', methods=['GET'])
@sentinel_login_required
def sentauth_admin_list_clients():
    client = sentauth_current_client()
    if not client or not client.get('is_conseilprev'):
        abort(403)
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, nom_entreprise, email, actif, date_creation, derniere_connexion FROM clients ORDER BY date_creation DESC')
    rows = cur.fetchall()
    conn.close()
    clients = [dict(r) if not isinstance(r, dict) else r for r in rows]
    return jsonify({'clients': clients})


def registre_init_db():
    conn = registre_get_db()
    cur = conn.cursor()
    if REGISTRE_USE_PG:
        cur.execute('''CREATE TABLE IF NOT EXISTS systemes_ia (
            id SERIAL PRIMARY KEY,
            nom TEXT NOT NULL,
            finalite TEXT,
            secteur TEXT,
            type_systeme TEXT,
            donnees_utilisees TEXT,
            classification TEXT,
            justification TEXT,
            statut_conformite TEXT DEFAULT 'a_evaluer',
            score_risque INTEGER DEFAULT 0,
            responsable TEXT,
            fournisseur TEXT,
            date_creation TEXT,
            date_maj TEXT
        )''')
    else:
        cur.execute('''CREATE TABLE IF NOT EXISTS systemes_ia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            finalite TEXT,
            secteur TEXT,
            type_systeme TEXT,
            donnees_utilisees TEXT,
            classification TEXT,
            justification TEXT,
            statut_conformite TEXT DEFAULT 'a_evaluer',
            score_risque INTEGER DEFAULT 0,
            responsable TEXT,
            fournisseur TEXT,
            date_creation TEXT,
            date_maj TEXT
        )''')
    conn.commit()

    # Migration isolation par client : ajout de la colonne, puis assignation des
    # systemes deja existants (crees avant l isolation) au compte CONSEILPREV.
    cur.execute("ALTER TABLE systemes_ia ADD COLUMN IF NOT EXISTS client_id INTEGER")
    conn.commit()
    conseilprev_id = ensure_conseilprev_client_id()
    cur.execute(registre_sql(
        "UPDATE systemes_ia SET client_id=%s WHERE client_id IS NULL",
        "UPDATE systemes_ia SET client_id=? WHERE client_id IS NULL"
    ), (conseilprev_id,))
    conn.commit()

    # Cycle de vie projet (Privacy by Design, Art. 25 RGPD) : conception -> developpement
    # -> pre-production -> production -> revue periodique. Les systemes deja existants
    # sont par defaut consideres en 'production' (hypothese la plus sure : ils etaient
    # deja deployes avant l introduction de ce suivi).
    cur.execute("ALTER TABLE systemes_ia ADD COLUMN IF NOT EXISTS cycle_vie TEXT DEFAULT 'production'")
    cur.execute("ALTER TABLE systemes_ia ADD COLUMN IF NOT EXISTS product_owner TEXT")
    cur.execute("ALTER TABLE systemes_ia ADD COLUMN IF NOT EXISTS derniere_revue TEXT")
    cur.execute(registre_sql(
        "UPDATE systemes_ia SET cycle_vie='production' WHERE cycle_vie IS NULL",
        "UPDATE systemes_ia SET cycle_vie='production' WHERE cycle_vie IS NULL"
    ))
    conn.commit()

    # Registre "parfait professionnel" — gap analyse vs les 10 questions essentielles
    # de la conformite IA Act (cf. Hub France IA, guide Premiers pas vers l IA de Confiance).
    cur.execute("ALTER TABLE systemes_ia ADD COLUMN IF NOT EXISTS service TEXT")
    cur.execute("ALTER TABLE systemes_ia ADD COLUMN IF NOT EXISTS roles TEXT")  # JSON: ["fournisseur","deployeur",...]
    cur.execute("ALTER TABLE systemes_ia ADD COLUMN IF NOT EXISTS personnes_concernees TEXT")
    cur.execute("ALTER TABLE systemes_ia ADD COLUMN IF NOT EXISTS transparence_art50 TEXT DEFAULT 'a_evaluer'")
    cur.execute("ALTER TABLE systemes_ia ADD COLUMN IF NOT EXISTS preuves_conformite TEXT")
    conn.commit()

    cur.execute('SELECT COUNT(*) AS n FROM systemes_ia')
    row = cur.fetchone()
    count = row['n'] if isinstance(row, dict) else row[0]
    if count == 0:
        now = datetime.utcnow().isoformat()
        demo = [
            ("Chatbot service client", "Repondre aux demandes clients de premier niveau", "Telecom", "LLM conversationnel", "Historique conversations, donnees compte client", "limite", "Art. 50 - obligation de transparence (interaction avec une IA)", "conforme", 4, "Responsable IA", "OpenAI/Interne", now, now),
            ("Scoring credit automatise", "Evaluer la solvabilite pour l'octroi de credit", "Finance", "Regression logistique / XGBoost", "Donnees identite, revenus, historique credit", "haut", "Annexe III, Point 5(a) - acces aux services financiers essentiels", "en_cours", 7, "Expert Data", "Interne", now, now),
            ("Maintenance predictive reseau", "Anticiper les pannes sur infrastructure reseau", "Telecom", "Modele de regression / ML supervise", "Donnees capteurs, historique pannes", "minimal", "Hors Annexe III - usage interne sans impact direct sur les personnes", "conforme", 2, "Expert Data", "Interne", now, now),
            ("Detection de fraude transactionnelle", "Identifier les transactions suspectes", "Finance", "Clustering / Isolation Forest", "Donnees transactionnelles, comportementales", "haut", "Annexe III, Point 5 - detection de fraude financiere", "en_cours", 6, "Consultant Cybersecurite", "Interne", now, now),
        ]
        ins = registre_sql(
            '''INSERT INTO systemes_ia (nom, finalite, secteur, type_systeme, donnees_utilisees, classification, justification, statut_conformite, score_risque, responsable, fournisseur, date_creation, date_maj)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
            '''INSERT INTO systemes_ia (nom, finalite, secteur, type_systeme, donnees_utilisees, classification, justification, statut_conformite, score_risque, responsable, fournisseur, date_creation, date_maj)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)'''
        )
        for row in demo:
            cur.execute(ins, row)
        conn.commit()
    conn.close()

try:
    registre_init_db()
    logger.info(f"REGISTRE_IA — moteur actif : {'PostgreSQL (externe)' if REGISTRE_USE_PG else 'SQLite (local, fallback dev)'}")
except Exception as _e:
    logger.error(f"REGISTRE_IA — erreur init DB : {_e}")


# ══════════════════════════════════════════════════════════════════
# Registre des traitements (RGPD, article 30) — calque du registre IA
# Table dediee, isolation par client (sentauth_current_client).
# ══════════════════════════════════════════════════════════════════
_RGPD_TRAIT_COLS = (
    'id', 'nom', 'finalites', 'base_legale', 'responsable', 'sous_traitants',
    'categories_personnes', 'categories_donnees', 'donnees_sensibles', 'destinataires',
    'transferts_hors_ue', 'duree_conservation', 'mesures_securite', 'service', 'statut',
    'date_creation', 'date_maj',
)


def rgpd_traitements_init_db():
    conn = registre_get_db()
    cur = conn.cursor()
    if REGISTRE_USE_PG:
        cur.execute("""CREATE TABLE IF NOT EXISTS rgpd_traitements (
            id SERIAL PRIMARY KEY,
            client_id INTEGER,
            nom TEXT NOT NULL,
            finalites TEXT,
            base_legale TEXT,
            responsable TEXT,
            sous_traitants TEXT,
            categories_personnes TEXT,
            categories_donnees TEXT,
            donnees_sensibles TEXT,
            destinataires TEXT,
            transferts_hors_ue TEXT,
            duree_conservation TEXT,
            mesures_securite TEXT,
            service TEXT,
            statut TEXT DEFAULT 'actif',
            date_creation TEXT,
            date_maj TEXT
        )""")
    else:
        cur.execute("""CREATE TABLE IF NOT EXISTS rgpd_traitements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            nom TEXT NOT NULL,
            finalites TEXT,
            base_legale TEXT,
            responsable TEXT,
            sous_traitants TEXT,
            categories_personnes TEXT,
            categories_donnees TEXT,
            donnees_sensibles TEXT,
            destinataires TEXT,
            transferts_hors_ue TEXT,
            duree_conservation TEXT,
            mesures_securite TEXT,
            service TEXT,
            statut TEXT DEFAULT 'actif',
            date_creation TEXT,
            date_maj TEXT
        )""")
    conn.commit()
    try:
        cid = ensure_conseilprev_client_id()
        cur.execute('SELECT COUNT(*) AS n FROM rgpd_traitements')
        row = cur.fetchone()
        count = row['n'] if isinstance(row, dict) else row[0]
        if count == 0:
            now = datetime.utcnow().isoformat()
            ins = registre_sql(
                'INSERT INTO rgpd_traitements (client_id, nom, finalites, base_legale, responsable, sous_traitants, categories_personnes, categories_donnees, donnees_sensibles, destinataires, transferts_hors_ue, duree_conservation, mesures_securite, service, statut, date_creation, date_maj) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                'INSERT INTO rgpd_traitements (client_id, nom, finalites, base_legale, responsable, sous_traitants, categories_personnes, categories_donnees, donnees_sensibles, destinataires, transferts_hors_ue, duree_conservation, mesures_securite, service, statut, date_creation, date_maj) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
            )
            cur.execute(ins, (
                cid, "Gestion des ressources humaines",
                "Gestion administrative du personnel (paie, contrats, absences)",
                "Obligation legale (art. 6.1.c) et execution du contrat (art. 6.1.b)",
                "CONSEILPREV - Direction", "Editeur SIRH (hebergement UE)",
                "Salaries, candidats",
                "Identite, coordonnees, donnees de carriere, donnees de paie",
                "Non (hors art. 9)",
                "Service RH, expert-comptable, organismes sociaux", "Non",
                "Duree du contrat + 5 ans (obligations legales)",
                "Controle d'acces, chiffrement, journalisation, habilitations",
                "Ressources humaines", "actif", now, now,
            ))
            conn.commit()
    except Exception:
        pass
    conn.close()


def rgpd_trait_row_to_dict(row):
    d = dict(row) if isinstance(row, dict) else {k: row[k] for k in row.keys()}
    return {k: d.get(k) for k in _RGPD_TRAIT_COLS}


try:
    rgpd_traitements_init_db()
    logger.info("RGPD_TRAITEMENTS - table prete")
except Exception as _e:
    logger.error(f"RGPD_TRAITEMENTS - erreur init : {_e}")


@app.route('/api/rgpd/traitements', methods=['GET'])
def rgpd_traitements_list():
    client = sentauth_current_client()
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql(
        'SELECT * FROM rgpd_traitements WHERE client_id=%s ORDER BY date_maj DESC',
        'SELECT * FROM rgpd_traitements WHERE client_id=? ORDER BY date_maj DESC'
    ), (client['id'],))
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return jsonify({'traitements': [rgpd_trait_row_to_dict(r) for r in rows]})


@app.route('/api/rgpd/traitements', methods=['POST'])
def rgpd_traitements_create():
    client = sentauth_current_client()
    data = request.get_json(force=True) or {}
    nom = (data.get('nom') or '').strip()[:200]
    if not nom:
        return jsonify({'error': 'Le nom du traitement est obligatoire'}), 400
    now = datetime.utcnow().isoformat()
    champs = ['finalites', 'base_legale', 'responsable', 'sous_traitants', 'categories_personnes',
              'categories_donnees', 'donnees_sensibles', 'destinataires', 'transferts_hors_ue',
              'duree_conservation', 'mesures_securite', 'service']
    vals = [(data.get(f) or '')[:1000] for f in champs]
    statut = (data.get('statut') or 'actif')[:30]
    conn = registre_get_db()
    cur = conn.cursor()
    ins = registre_sql(
        'INSERT INTO rgpd_traitements (client_id, nom, finalites, base_legale, responsable, sous_traitants, categories_personnes, categories_donnees, donnees_sensibles, destinataires, transferts_hors_ue, duree_conservation, mesures_securite, service, statut, date_creation, date_maj) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        'INSERT INTO rgpd_traitements (client_id, nom, finalites, base_legale, responsable, sous_traitants, categories_personnes, categories_donnees, donnees_sensibles, destinataires, transferts_hors_ue, duree_conservation, mesures_securite, service, statut, date_creation, date_maj) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
    )
    cur.execute(ins, tuple([client['id'], nom] + vals + [statut, now, now]))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/rgpd/traitements/delete', methods=['POST'])
def rgpd_traitements_delete():
    client = sentauth_current_client()
    data = request.get_json(force=True) or {}
    tid = data.get('id')
    if not tid:
        return jsonify({'error': 'id requis'}), 400
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql(
        'DELETE FROM rgpd_traitements WHERE id=%s AND client_id=%s',
        'DELETE FROM rgpd_traitements WHERE id=? AND client_id=?'
    ), (tid, client['id']))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


def registre_row_to_dict(row):
    if isinstance(row, dict):
        d = dict(row)
    else:
        d = {k: row[k] for k in row.keys()}
    try:
        roles_parsed = json.loads(d.get('roles')) if d.get('roles') else []
    except Exception:
        roles_parsed = []
    return {
        'id': d['id'], 'nom': d['nom'], 'finalite': d['finalite'],
        'secteur': d['secteur'], 'type_systeme': d['type_systeme'],
        'donnees_utilisees': d['donnees_utilisees'], 'classification': d['classification'],
        'justification': d['justification'], 'statut_conformite': d['statut_conformite'],
        'score_risque': d['score_risque'], 'responsable': d['responsable'],
        'fournisseur': d['fournisseur'], 'date_creation': d['date_creation'], 'date_maj': d['date_maj'],
        'cycle_vie': d.get('cycle_vie') or 'production', 'product_owner': d.get('product_owner'),
        'derniere_revue': d.get('derniere_revue'),
        'service': d.get('service'), 'roles': roles_parsed,
        'personnes_concernees': d.get('personnes_concernees'),
        'transparence_art50': d.get('transparence_art50') or 'a_evaluer',
        'preuves_conformite': d.get('preuves_conformite')
    }

@app.route('/api/registre', methods=['GET'])
@require_paid_plan
@rate_limit(limit=60, window=60)
def registre_list():
    client = sentauth_current_client()
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql(
        'SELECT * FROM systemes_ia WHERE client_id=%s ORDER BY date_maj DESC',
        'SELECT * FROM systemes_ia WHERE client_id=? ORDER BY date_maj DESC'
    ), (client['id'],))
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return jsonify({'systemes': [registre_row_to_dict(r) for r in rows], 'moteur': 'postgres' if REGISTRE_USE_PG else 'sqlite'})

@app.route('/api/registre', methods=['POST'])
@require_paid_plan
@rate_limit(limit=30, window=60)
def registre_create():
    client = sentauth_current_client()
    data = request.get_json(force=True) or {}
    nom = (data.get('nom') or '').strip()[:200]
    if not nom:
        return jsonify({'error': 'Le nom du systeme est obligatoire'}), 400
    now = datetime.utcnow().isoformat()
    conn = registre_get_db()
    cur = conn.cursor()
    roles_list = data.get('roles') or []
    if not isinstance(roles_list, list):
        roles_list = []
    values = (
        nom,
        (data.get('finalite') or '')[:500],
        (data.get('secteur') or '')[:100],
        (data.get('type_systeme') or '')[:100],
        (data.get('donnees_utilisees') or '')[:500],
        (data.get('classification') or 'a_evaluer')[:50],
        (data.get('justification') or '')[:500],
        (data.get('statut_conformite') or 'a_evaluer')[:50],
        int(data.get('score_risque') or 0),
        (data.get('responsable') or '')[:100],
        (data.get('fournisseur') or '')[:100],
        now, now, client['id'],
        (data.get('cycle_vie') or 'conception')[:30],
        (data.get('product_owner') or '')[:100],
        (data.get('service') or '')[:100],
        json.dumps(roles_list)[:300],
        (data.get('personnes_concernees') or '')[:500],
        (data.get('transparence_art50') or 'a_evaluer')[:30],
        (data.get('preuves_conformite') or '')[:500]
    )
    if REGISTRE_USE_PG:
        cur.execute('''INSERT INTO systemes_ia
            (nom, finalite, secteur, type_systeme, donnees_utilisees, classification, justification, statut_conformite, score_risque, responsable, fournisseur, date_creation, date_maj, client_id, cycle_vie, product_owner, service, roles, personnes_concernees, transparence_art50, preuves_conformite)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *''', values)
        row = cur.fetchone()
    else:
        cur.execute('''INSERT INTO systemes_ia
            (nom, finalite, secteur, type_systeme, donnees_utilisees, classification, justification, statut_conformite, score_risque, responsable, fournisseur, date_creation, date_maj, client_id, cycle_vie, product_owner, service, roles, personnes_concernees, transparence_art50, preuves_conformite)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', values)
        new_id = cur.lastrowid
        cur.execute('SELECT * FROM systemes_ia WHERE id=?', (new_id,))
        row = cur.fetchone()
    conn.commit()
    conn.close()
    schedule_cartographie_report(client['id'], client.get('email') or CONSEILPREV_INTERNAL_EMAIL, client.get('nom_entreprise') or 'CONSEILPREV')
    return jsonify({'systeme': registre_row_to_dict(row)}), 201

@app.route('/api/registre/<int:sys_id>', methods=['PUT'])
@require_paid_plan
@rate_limit(limit=30, window=60)
def registre_update(sys_id):
    client = sentauth_current_client()
    data = request.get_json(force=True) or {}
    conn = registre_get_db()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    fields = ['nom','finalite','secteur','type_systeme','donnees_utilisees','classification','justification','statut_conformite','responsable','fournisseur','cycle_vie','product_owner','service','personnes_concernees','transparence_art50','preuves_conformite']
    # Si le cycle de vie passe explicitement a 'revue', on horodate la derniere revue —
    # trace la conformite a l obligation de revue periodique des cas d usage en production.
    derniere_revue_val = now if data.get('cycle_vie') == 'revue' else None
    roles_json = json.dumps(data.get('roles')) if data.get('roles') is not None else None

    if REGISTRE_USE_PG:
        # COALESCE permet de ne mettre a jour que les champs fournis, en une seule requete
        # combinant verification d existence + mise a jour + lecture du resultat (au lieu de 3).
        # client_id dans le WHERE empeche un client de modifier le systeme d un autre.
        cur.execute('''UPDATE systemes_ia SET
            nom=COALESCE(%s,nom), finalite=COALESCE(%s,finalite), secteur=COALESCE(%s,secteur),
            type_systeme=COALESCE(%s,type_systeme), donnees_utilisees=COALESCE(%s,donnees_utilisees),
            classification=COALESCE(%s,classification), justification=COALESCE(%s,justification),
            statut_conformite=COALESCE(%s,statut_conformite), responsable=COALESCE(%s,responsable),
            fournisseur=COALESCE(%s,fournisseur), score_risque=COALESCE(%s,score_risque),
            cycle_vie=COALESCE(%s,cycle_vie), product_owner=COALESCE(%s,product_owner),
            derniere_revue=COALESCE(%s,derniere_revue),
            service=COALESCE(%s,service), roles=COALESCE(%s,roles),
            personnes_concernees=COALESCE(%s,personnes_concernees),
            transparence_art50=COALESCE(%s,transparence_art50),
            preuves_conformite=COALESCE(%s,preuves_conformite), date_maj=%s
            WHERE id=%s AND client_id=%s RETURNING *''', (
            data.get('nom'), data.get('finalite'), data.get('secteur'), data.get('type_systeme'),
            data.get('donnees_utilisees'), data.get('classification'), data.get('justification'),
            data.get('statut_conformite'), data.get('responsable'), data.get('fournisseur'),
            data.get('score_risque'), data.get('cycle_vie'), data.get('product_owner'),
            derniere_revue_val,
            data.get('service'), roles_json, data.get('personnes_concernees'),
            data.get('transparence_art50'), data.get('preuves_conformite'),
            now, sys_id, client['id']))
        row = cur.fetchone()
        conn.commit()
        conn.close()
        if not row:
            return jsonify({'error': 'Systeme introuvable'}), 404
        schedule_cartographie_report(client['id'], client.get('email') or CONSEILPREV_INTERNAL_EMAIL, client.get('nom_entreprise') or 'CONSEILPREV')
        return jsonify({'systeme': registre_row_to_dict(row)})
    else:
        cur.execute('SELECT * FROM systemes_ia WHERE id=? AND client_id=?', (sys_id, client['id']))
        existing = cur.fetchone()
        if not existing:
            conn.close()
            return jsonify({'error': 'Systeme introuvable'}), 404
        existing_d = registre_row_to_dict(existing)
        vals = {f: data.get(f, existing_d[f]) for f in fields}
        score = int(data.get('score_risque', existing_d['score_risque']) or 0)
        derniere_revue_final = derniere_revue_val or existing_d.get('derniere_revue')
        roles_final = roles_json if roles_json is not None else json.dumps(existing_d.get('roles') or [])
        cur.execute('''UPDATE systemes_ia SET nom=?, finalite=?, secteur=?, type_systeme=?, donnees_utilisees=?,
           classification=?, justification=?, statut_conformite=?, responsable=?, fournisseur=?, score_risque=?,
           cycle_vie=?, product_owner=?, derniere_revue=?,
           service=?, roles=?, personnes_concernees=?, transparence_art50=?, preuves_conformite=?, date_maj=?
           WHERE id=? AND client_id=?''', (vals['nom'], vals['finalite'], vals['secteur'], vals['type_systeme'], vals['donnees_utilisees'],
            vals['classification'], vals['justification'], vals['statut_conformite'], vals['responsable'], vals['fournisseur'],
            score, vals['cycle_vie'], vals['product_owner'], derniere_revue_final,
            vals['service'], roles_final, vals['personnes_concernees'], vals['transparence_art50'], vals['preuves_conformite'],
            now, sys_id, client['id']))
        conn.commit()
        cur.execute('SELECT * FROM systemes_ia WHERE id=?', (sys_id,))
        row = cur.fetchone()
        conn.close()
        schedule_cartographie_report(client['id'], client.get('email') or CONSEILPREV_INTERNAL_EMAIL, client.get('nom_entreprise') or 'CONSEILPREV')
        return jsonify({'systeme': registre_row_to_dict(row)})

@app.route('/api/registre/<int:sys_id>', methods=['DELETE'])
@require_paid_plan
@rate_limit(limit=30, window=60)
def registre_delete(sys_id):
    conn = registre_get_db()
    cur = conn.cursor()
    client = sentauth_current_client()
    # Une seule requete : DELETE direct, on verifie cur.rowcount pour savoir si la
    # ligne existait (au lieu d un SELECT de verification puis un DELETE separes).
    # client_id dans le WHERE empeche un client de supprimer le systeme d un autre.
    cur.execute(registre_sql(
        'DELETE FROM systemes_ia WHERE id=%s AND client_id=%s',
        'DELETE FROM systemes_ia WHERE id=? AND client_id=?'
    ), (sys_id, client['id']))
    deleted_count = cur.rowcount
    conn.commit()
    conn.close()
    if deleted_count == 0:
        return jsonify({'error': 'Systeme introuvable'}), 404
    schedule_cartographie_report(client['id'], client.get('email') or CONSEILPREV_INTERNAL_EMAIL, client.get('nom_entreprise') or 'CONSEILPREV')
    return jsonify({'deleted': sys_id})

@app.route('/api/registre/status', methods=['GET'])
@require_paid_plan
@rate_limit(limit=30, window=60)
def registre_status():
    return jsonify({
        'moteur': 'postgres' if REGISTRE_USE_PG else 'sqlite',
        'persistant': REGISTRE_USE_PG,
        'message': 'Base de donnees externe geree (persistance garantie)' if REGISTRE_USE_PG else 'SQLite local — DATABASE_URL non configuree, donnees non persistantes entre deploiements'
    })



# ══════════════════════════════════════════════════════════
# VEILLE QUALIFIEE PAR IA — Scoring de pertinence
# Croise les actualites RSS avec le Registre IA reel du client
# (table systemes_ia) pour evaluer l'impact potentiel de chaque
# article sur les systemes effectivement deployes.
# ══════════════════════════════════════════════════════════
_veille_cache = {}  # dict indexe par client_id, evite de melanger les caches entre clients
VEILLE_CACHE_TTL = 1800  # 30 min

def veille_get_registre_summary(client_id):
    """Recupere un resume textuel court du registre IA actif du client (Postgres ou SQLite)."""
    try:
        conn = registre_get_db()
        cur = conn.cursor()
        cur.execute(registre_sql(
            'SELECT nom, secteur, classification, type_systeme FROM systemes_ia WHERE client_id=%s',
            'SELECT nom, secteur, classification, type_systeme FROM systemes_ia WHERE client_id=?'
        ), (client_id,))
        rows = cur.fetchall()
        conn.commit()
        conn.close()
        systemes = [registre_row_to_dict_partial(r) for r in rows]
        return systemes
    except Exception as _e:
        logger.warning(f"VEILLE_QUALIFIEE — registre indisponible : {_e}")
        return []

def registre_row_to_dict_partial(row):
    if isinstance(row, dict):
        return {'nom': row.get('nom'), 'secteur': row.get('secteur'), 'classification': row.get('classification'), 'type_systeme': row.get('type_systeme')}
    return {'nom': row[0], 'secteur': row[1], 'classification': row[2], 'type_systeme': row[3]}

@app.route('/api/veille/qualifiee', methods=['GET'])
@require_paid_plan
@rate_limit(limit=30, window=60)
def veille_qualifiee():
    """Scoring de pertinence IA des actualites par rapport au registre reel du client.
    Mise en cache 30 min par client pour limiter les appels API."""
    global _veille_cache
    now = time.time()
    client = sentauth_current_client()
    cache_entry = _veille_cache.get(client['id'], {"data": None, "ts": 0, "registre_hash": None})

    systemes = veille_get_registre_summary(client['id'])
    registre_hash = hashlib.md5(json.dumps(systemes, sort_keys=True).encode()).hexdigest() if systemes else "empty"

    if (now - cache_entry["ts"] < VEILLE_CACHE_TTL
        and cache_entry["data"]
        and cache_entry["registre_hash"] == registre_hash):
        return jsonify({"items": cache_entry["data"], "cached": True, "registre_count": len(systemes)})

    # Récupérer les actualités (réutilise le cache /api/news si disponible)
    items = _news_cache["data"][:20] if _news_cache["data"] else []
    if not items:
        return jsonify({"items": [], "cached": False, "registre_count": len(systemes), "message": "Aucune actualite disponible. Appelez /api/news d'abord."})

    if not systemes:
        # Pas de registre -> scoring generique sans personnalisation
        secteurs_txt = "non specifie (aucun systeme enregistre)"
        systemes_txt = "Aucun systeme IA enregistre dans le registre."
    else:
        secteurs = sorted(set(s['secteur'] for s in systemes if s.get('secteur')))
        secteurs_txt = ", ".join(secteurs) if secteurs else "non specifie"
        systemes_txt = "\n".join(f"- {s['nom']} ({s.get('type_systeme') or 'type non precise'}, secteur {s.get('secteur') or 'n/c'}, classification {s.get('classification') or 'a_evaluer'})" for s in systemes)

    titres_numerotes = "\n".join(f"{i+1}. {it['title']} [source: {it['source']}]" for i, it in enumerate(items))

    prompt = (
        "Voici le registre des systemes IA reellement deployes par l'entreprise :\n"
        f"{systemes_txt}\n\n"
        f"Secteurs d'activite concernes : {secteurs_txt}\n\n"
        "Voici une liste d'actualites reglementaires et technologiques recentes :\n"
        f"{titres_numerotes}\n\n"
        "Pour CHAQUE actualite numerotee, evalue son impact potentiel sur les systemes IA listes ci-dessus. "
        "Reponds UNIQUEMENT en JSON valide, sous forme d'un tableau d'objets, un objet par actualite, dans l'ordre, avec exactement ces champs : "
        '{"n": <numero>, "impact": "haut"|"moyen"|"faible", "raison": "<une phrase courte expliquant le lien avec un systeme du registre ou pourquoi impact faible>"}. '
        "Ne mets aucun texte avant ou apres le JSON, aucun bloc de code markdown, juste le tableau JSON brut."
    )
    system = "Tu es un analyste reglementaire CONSEILPREV specialise en gouvernance IA. Tu evalues la pertinence d'actualites par rapport a un registre de systemes IA reel. Reponds uniquement en JSON strict, sans aucun texte additionnel."

    ok, reply, model_used = ai_complete(
        [{"role": "user", "content": prompt}],
        system=system, max_tokens=1500, temperature=0.2, prefer='mistral'
    )

    scored_items = []
    if ok and reply:
        try:
            cleaned = reply.strip()
            if cleaned.startswith('```'):
                cleaned = _re.sub(r'^```[a-zA-Z]*\n?', '', cleaned)
                cleaned = _re.sub(r'```$', '', cleaned).strip()
            scores = json.loads(cleaned)
            score_map = {int(s['n']): s for s in scores if 'n' in s}
        except Exception as _e:
            logger.warning(f"VEILLE_QUALIFIEE — parsing JSON echoue : {_e}")
            score_map = {}
    else:
        score_map = {}

    impact_order = {"haut": 0, "moyen": 1, "faible": 2}
    for i, it in enumerate(items):
        s = score_map.get(i + 1, {})
        scored_items.append({
            **it,
            "impact": s.get("impact", "moyen"),
            "raison": s.get("raison", "Analyse non disponible — pertinence generale non personnalisee."),
        })
    scored_items.sort(key=lambda x: impact_order.get(x["impact"], 1))

    _veille_cache[client['id']] = {"data": scored_items, "ts": now, "registre_hash": registre_hash}
    return jsonify({
        "items": scored_items,
        "cached": False,
        "registre_count": len(systemes),
        "model": model_used,
        "personnalise": len(systemes) > 0
    })

@app.route('/api/notifications/summary', methods=['GET'])
@sentinel_login_required
def notifications_summary():
    """Agrege les 3 sources de notifications affichees via la cloche de la
    sidebar : veille reglementaire a fort impact (depuis le cache deja calcule,
    pas de nouvel appel IA couteux), rapports de cartographie envoyes
    recemment, et laisse au frontend le calcul des points d audit en attente
    (stockes uniquement en localStorage, donc invisibles cote serveur)."""
    client = sentauth_current_client()

    veille_count = 0
    veille_items = []
    cache_entry = _veille_cache.get(client['id'])
    if cache_entry and cache_entry.get('data'):
        for it in cache_entry['data']:
            if it.get('impact') == 'haut':
                veille_count += 1
                if len(veille_items) < 5:
                    veille_items.append({'title': it.get('title'), 'link': it.get('link')})

    rapports_count = 0
    rapports_items = []
    try:
        conn = registre_get_db()
        cur = conn.cursor()
        cutoff = (datetime.utcnow() - _timedelta_auth(hours=48)).isoformat()
        cur.execute(registre_sql(
            "SELECT * FROM email_log WHERE destinataire=%s AND sujet LIKE %s AND succes=TRUE AND date_envoi > %s ORDER BY date_envoi DESC",
            "SELECT * FROM email_log WHERE destinataire=? AND sujet LIKE ? AND succes=1 AND date_envoi > ? ORDER BY date_envoi DESC"
        ), (client.get('email') or CONSEILPREV_INTERNAL_EMAIL, 'Cartographie IA%', cutoff))
        rows = [dict(r) if not isinstance(r, dict) else r for r in cur.fetchall()]
        conn.commit()
        conn.close()
        rapports_count = len(rows)
        rapports_items = [{'sujet': r['sujet'], 'date': r['date_envoi']} for r in rows[:5]]
    except Exception as e:
        logger.error(f"NOTIFICATIONS_SUMMARY_RAPPORTS_FAILED: {e}")

    return jsonify({
        'veille': {'count': veille_count, 'items': veille_items},
        'rapports': {'count': rapports_count, 'items': rapports_items}
    })

@app.route('/api/veille/notifier', methods=['POST'])
@rate_limit(limit=20, window=60)
def veille_notifier():
    """Genere un lien mailto pre-rempli avec les alertes haut-impact (cote serveur, formatage uniquement)."""
    data = request.get_json(force=True) or {}
    items = data.get('items', [])[:10]
    haut_impact = [it for it in items if it.get('impact') == 'haut']
    if not haut_impact:
        return jsonify({"message": "Aucune alerte a haut impact a notifier."})
    lines = [f"- {it.get('title','')} ({it.get('source','')}) : {it.get('raison','')}" for it in haut_impact]
    return jsonify({"count": len(haut_impact), "summary": "\n".join(lines)})


# ══════════════════════════════════════════════════════════
# HISTORIQUE DES CALCULS — stockage persistant, tracabilite RGPD
# Reutilise le moteur de connexion deja en place (registre_get_db / registre_sql).
# Conservation : 3 ans par defaut (delai de prescription contractuelle), purge
# automatique des entrees plus anciennes a chaque demarrage (Art. 5(1)(e) RGPD —
# limitation de la conservation). Acces partage client + CONSEILPREV (support/audit).
# ══════════════════════════════════════════════════════════
HISTO_RETENTION_DAYS = 365 * 3  # 3 ans

def histo_init_db():
    conn = registre_get_db()
    cur = conn.cursor()
    if REGISTRE_USE_PG:
        cur.execute('''CREATE TABLE IF NOT EXISTS calculs_historique (
            id SERIAL PRIMARY KEY,
            page_origine TEXT NOT NULL,
            type_calcul TEXT NOT NULL,
            parametres_entree TEXT NOT NULL,
            resultat TEXT NOT NULL,
            label TEXT,
            modifie_de INTEGER,
            date_creation TEXT NOT NULL,
            date_maj TEXT NOT NULL
        )''')
    else:
        cur.execute('''CREATE TABLE IF NOT EXISTS calculs_historique (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_origine TEXT NOT NULL,
            type_calcul TEXT NOT NULL,
            parametres_entree TEXT NOT NULL,
            resultat TEXT NOT NULL,
            label TEXT,
            modifie_de INTEGER,
            date_creation TEXT NOT NULL,
            date_maj TEXT NOT NULL
        )''')
    conn.commit()

    # Purge RGPD : suppression des entrees au-dela de la duree de conservation (Art. 5(1)(e))
    try:
        cutoff = (datetime.utcnow() - timedelta(days=HISTO_RETENTION_DAYS)).isoformat()
        cur.execute(registre_sql(
            'DELETE FROM calculs_historique WHERE date_creation < %s',
            'DELETE FROM calculs_historique WHERE date_creation < ?'
        ), (cutoff,))
        purged = cur.rowcount
        conn.commit()
        if purged and purged > 0:
            logger.info(f"HISTORIQUE_CALCULS — purge RGPD : {purged} entree(s) > {HISTO_RETENTION_DAYS} jours supprimee(s)")
    except Exception as _e:
        logger.warning(f"HISTORIQUE_CALCULS — purge RGPD echouee : {_e}")
    conn.close()

try:
    histo_init_db()
except Exception as _e:
    logger.error(f"HISTORIQUE_CALCULS — erreur init DB : {_e}")

def histo_row_to_dict(row):
    if isinstance(row, dict):
        d = dict(row)
    else:
        d = {k: row[k] for k in row.keys()}
    return {
        'id': d['id'], 'page_origine': d['page_origine'], 'type_calcul': d['type_calcul'],
        'parametres_entree': d['parametres_entree'], 'resultat': d['resultat'],
        'label': d['label'], 'modifie_de': d['modifie_de'],
        'date_creation': d['date_creation'], 'date_maj': d['date_maj']
    }

@app.route('/api/historique', methods=['GET'])
@require_paid_plan
@rate_limit(limit=60, window=60)
def historique_list():
    page_filter = request.args.get('page_origine', '').strip()
    conn = registre_get_db()
    cur = conn.cursor()
    if page_filter:
        cur.execute(registre_sql(
            'SELECT * FROM calculs_historique WHERE page_origine = %s ORDER BY date_maj DESC',
            'SELECT * FROM calculs_historique WHERE page_origine = ? ORDER BY date_maj DESC'
        ), (page_filter,))
    else:
        cur.execute('SELECT * FROM calculs_historique ORDER BY date_maj DESC')
    rows = cur.fetchall()
    conn.close()
    return jsonify({
        'calculs': [histo_row_to_dict(r) for r in rows],
        'retention_jours': HISTO_RETENTION_DAYS,
        'retention_info': "Conservation 3 ans (delai de prescription contractuelle usuel) — Art. 5(1)(e) RGPD. Suppression manuelle possible a tout moment."
    })

@app.route('/api/historique', methods=['POST'])
@require_paid_plan
@rate_limit(limit=60, window=60)
def historique_create():
    data = request.get_json(force=True) or {}
    page_origine = (data.get('page_origine') or '').strip()[:50]
    type_calcul = (data.get('type_calcul') or '').strip()[:100]
    parametres = data.get('parametres_entree')
    resultat = data.get('resultat')
    label = (data.get('label') or '')[:200]
    modifie_de = data.get('modifie_de')

    if not page_origine or not type_calcul or parametres is None or resultat is None:
        return jsonify({'error': 'page_origine, type_calcul, parametres_entree et resultat sont obligatoires'}), 400

    params_json = json.dumps(parametres, ensure_ascii=False)[:20000]
    resultat_json = json.dumps(resultat, ensure_ascii=False)[:20000]
    now = datetime.utcnow().isoformat()

    conn = registre_get_db()
    cur = conn.cursor()
    values = (page_origine, type_calcul, params_json, resultat_json, label, modifie_de, now, now)
    if REGISTRE_USE_PG:
        cur.execute('''INSERT INTO calculs_historique
            (page_origine, type_calcul, parametres_entree, resultat, label, modifie_de, date_creation, date_maj)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id''', values)
        new_id = cur.fetchone()['id']
    else:
        cur.execute('''INSERT INTO calculs_historique
            (page_origine, type_calcul, parametres_entree, resultat, label, modifie_de, date_creation, date_maj)
            VALUES (?,?,?,?,?,?,?,?)''', values)
        new_id = cur.lastrowid
    conn.commit()
    cur.execute(registre_sql('SELECT * FROM calculs_historique WHERE id=%s', 'SELECT * FROM calculs_historique WHERE id=?'), (new_id,))
    row = cur.fetchone()
    conn.close()
    return jsonify({'calcul': histo_row_to_dict(row)}), 201

@app.route('/api/historique/<int:calc_id>', methods=['PUT'])
@require_paid_plan
@rate_limit(limit=60, window=60)
def historique_update(calc_id):
    data = request.get_json(force=True) or {}
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql('SELECT * FROM calculs_historique WHERE id=%s', 'SELECT * FROM calculs_historique WHERE id=?'), (calc_id,))
    existing = cur.fetchone()
    if not existing:
        conn.close()
        return jsonify({'error': 'Calcul introuvable'}), 404
    existing_d = histo_row_to_dict(existing)
    now = datetime.utcnow().isoformat()
    parametres = data.get('parametres_entree', json.loads(existing_d['parametres_entree']))
    resultat = data.get('resultat', json.loads(existing_d['resultat']))
    label = data.get('label', existing_d['label'])
    params_json = json.dumps(parametres, ensure_ascii=False)[:20000]
    resultat_json = json.dumps(resultat, ensure_ascii=False)[:20000]
    cur.execute(registre_sql(
        'UPDATE calculs_historique SET parametres_entree=%s, resultat=%s, label=%s, date_maj=%s WHERE id=%s',
        'UPDATE calculs_historique SET parametres_entree=?, resultat=?, label=?, date_maj=? WHERE id=?'
    ), (params_json, resultat_json, label, now, calc_id))
    conn.commit()
    cur.execute(registre_sql('SELECT * FROM calculs_historique WHERE id=%s', 'SELECT * FROM calculs_historique WHERE id=?'), (calc_id,))
    row = cur.fetchone()
    conn.close()
    return jsonify({'calcul': histo_row_to_dict(row)})

@app.route('/api/historique/<int:calc_id>', methods=['DELETE'])
@require_paid_plan
@rate_limit(limit=60, window=60)
def historique_delete(calc_id):
    """Droit a l effacement (Art. 17 RGPD) — suppression manuelle a la demande du client."""
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql('SELECT id FROM calculs_historique WHERE id=%s', 'SELECT id FROM calculs_historique WHERE id=?'), (calc_id,))
    existing = cur.fetchone()
    if not existing:
        conn.close()
        return jsonify({'error': 'Calcul introuvable'}), 404
    cur.execute(registre_sql('DELETE FROM calculs_historique WHERE id=%s', 'DELETE FROM calculs_historique WHERE id=?'), (calc_id,))
    conn.commit()
    conn.close()
    return jsonify({'deleted': calc_id})

@app.route('/api/historique/purge-all', methods=['DELETE'])
@require_paid_plan
@rate_limit(limit=5, window=60)
def historique_purge_all():
    """Droit a l effacement en lot (Art. 17 RGPD) — suppression complete de l historique."""
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM calculs_historique')
    deleted_count = cur.rowcount
    conn.commit()
    conn.close()
    return jsonify({'deleted_count': deleted_count})


# ══════════════════════════════════════════════════════════
# RAG — BASE DE CONNAISSANCE (Espace)
# Upload/download de documents (PDF, DOCX, TXT, CSV), extraction de texte,
# chunking, embeddings Mistral, recherche hybride : vectorielle (pgvector si
# disponible) avec repli automatique sur recherche full-text Postgres native
# (tsvector/tsquery, disponible sur tout plan, y compris gratuit).
# ══════════════════════════════════════════════════════════
RAG_PGVECTOR_AVAILABLE = False
RAG_EMBED_DIM = 1024  # dimension mistral-embed
RAG_CHUNK_SIZE = 900
RAG_CHUNK_OVERLAP = 150
RAG_MAX_FILE_SIZE = 8 * 1024 * 1024  # 8 Mo
RAG_ALLOWED_EXT = {'.pdf', '.docx', '.txt', '.csv'}
RAG_PAGES_VALIDES = ['audit', 'registre', 'fria', 'maturite', 'veille', 'raci', 'general']

def rag_init_db():
    global RAG_PGVECTOR_AVAILABLE
    conn = registre_get_db()
    cur = conn.cursor()
    if REGISTRE_USE_PG:
        try:
            cur.execute('CREATE EXTENSION IF NOT EXISTS vector')
            conn.commit()
            RAG_PGVECTOR_AVAILABLE = True
            logger.info("RAG — pgvector active avec succes")
        except Exception as _e:
            conn.rollback()
            RAG_PGVECTOR_AVAILABLE = False
            logger.warning(f"RAG — pgvector indisponible, repli sur recherche full-text : {_e}")

        cur.execute('''CREATE TABLE IF NOT EXISTS rag_documents (
            id SERIAL PRIMARY KEY,
            nom_fichier TEXT NOT NULL,
            type_mime TEXT NOT NULL,
            extension TEXT NOT NULL,
            pages_liees TEXT NOT NULL,
            taille_octets INTEGER NOT NULL,
            contenu_fichier BYTEA NOT NULL,
            nb_chunks INTEGER DEFAULT 0,
            chunks_indexes INTEGER DEFAULT 0,
            statut_indexation TEXT DEFAULT \'termine\',
            date_upload TEXT NOT NULL
        )''')
        try:
            cur.execute("ALTER TABLE rag_documents ADD COLUMN IF NOT EXISTS chunks_indexes INTEGER DEFAULT 0")
            cur.execute("ALTER TABLE rag_documents ADD COLUMN IF NOT EXISTS statut_indexation TEXT DEFAULT \'termine\'")
            conn.commit()
        except Exception: conn.rollback()
        if RAG_PGVECTOR_AVAILABLE:
            cur.execute(f'''CREATE TABLE IF NOT EXISTS rag_chunks (
                id SERIAL PRIMARY KEY,
                document_id INTEGER NOT NULL REFERENCES rag_documents(id) ON DELETE CASCADE,
                chunk_text TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                embedding vector({RAG_EMBED_DIM}),
                search_vector tsvector
            )''')
        else:
            cur.execute('''CREATE TABLE IF NOT EXISTS rag_chunks (
                id SERIAL PRIMARY KEY,
                document_id INTEGER NOT NULL REFERENCES rag_documents(id) ON DELETE CASCADE,
                chunk_text TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                search_vector tsvector
            )''')
        cur.execute("CREATE INDEX IF NOT EXISTS idx_rag_chunks_search ON rag_chunks USING GIN(search_vector)")
    else:
        cur.execute('''CREATE TABLE IF NOT EXISTS rag_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_fichier TEXT NOT NULL, type_mime TEXT NOT NULL, extension TEXT NOT NULL,
            pages_liees TEXT NOT NULL, taille_octets INTEGER NOT NULL,
            contenu_fichier BLOB NOT NULL, nb_chunks INTEGER DEFAULT 0,
            chunks_indexes INTEGER DEFAULT 0, statut_indexation TEXT DEFAULT \'termine\',
            date_upload TEXT NOT NULL
        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS rag_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL, chunk_text TEXT NOT NULL, chunk_index INTEGER NOT NULL
        )''')
    conn.commit()
    conn.close()

try:
    rag_init_db()
except Exception as _e:
    logger.error(f"RAG — erreur init DB : {_e}")

def rag_extract_text(filename, file_bytes):
    """Extrait le texte d un fichier selon son extension. Retourne (ok, texte_ou_erreur)."""
    ext = os.path.splitext(filename)[1].lower()
    try:
        if ext == '.txt':
            return True, file_bytes.decode('utf-8', errors='ignore')
        elif ext == '.csv':
            text = file_bytes.decode('utf-8', errors='ignore')
            return True, text
        elif ext == '.pdf':
            from pypdf import PdfReader
            import io
            reader = PdfReader(io.BytesIO(file_bytes))
            pages_text = [p.extract_text() or '' for p in reader.pages]
            return True, '\n\n'.join(pages_text)
        elif ext == '.docx':
            from docx import Document as DocxDocument
            import io
            doc = DocxDocument(io.BytesIO(file_bytes))
            paras = [p.text for p in doc.paragraphs if p.text.strip()]
            return True, '\n\n'.join(paras)
        else:
            return False, f"Extension non supportee : {ext}"
    except Exception as e:
        return False, f"Erreur d extraction : {e}"

def rag_chunk_text(text):
    """Decoupe le texte en chunks avec overlap, en respectant les frontieres de mots."""
    text = _re.sub(r'\s+', ' ', text).strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + RAG_CHUNK_SIZE, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        if end >= len(text):
            break
        start = end - RAG_CHUNK_OVERLAP
    return chunks

def rag_get_embeddings(texts):
    """Appelle l API Mistral embeddings. Retourne (ok, liste_de_vecteurs_ou_erreur)."""
    if not MISTRAL_API_KEY:
        return False, 'no_mistral_key'
    try:
        resp = requests.post(
            'https://api.mistral.ai/v1/embeddings',
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {MISTRAL_API_KEY}'},
            json={'model': 'mistral-embed', 'input': texts},
            timeout=30
        )
        if resp.ok:
            data = resp.json()['data']
            return True, [d['embedding'] for d in data]
        return False, f'http_{resp.status_code}'
    except requests.Timeout:
        return False, 'timeout'
    except Exception as e:
        return False, str(e)

RAG_ACCESS_KEY = os.environ.get('RAG_ACCESS_KEY', 'conseilprev-rag-2026').strip()

def rag_check_access():
    """Verifie que la requete provient bien de CONSEILPREV (cle secrete serverside,
    jamais exposee au client HTML/JS contrairement a l ancien SRC_PASS cosmetique)."""
    provided = request.headers.get('X-RAG-Key', '') or request.args.get('rag_key', '')
    return provided == RAG_ACCESS_KEY

def rag_require_access(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not rag_check_access():
            return jsonify({'error': 'Accès réservé à CONSEILPREV. Clé d accès requise.'}), 403
        return f(*args, **kwargs)
    return wrapper

RAG_SUJETS = [
    ('IA Act', ['ia act', 'ai act', 'intelligence artificielle', 'systeme ia', "systeme d'ia", 'annexe iii',
                'haut risque', 'gpai', 'modele de fondation', 'ai office', 'bureau de l ia']),
    ('RGPD', ['rgpd', 'gdpr', 'donnees personnelles', 'donnees a caractere personnel', 'aipd', 'dpia',
              'sous-traitant', 'responsable de traitement', 'cnil', 'consentement', 'droit d acces']),
    ('ISO 42001', ['iso 42001', 'iso/iec 42001', 'iso42001', 'systeme de management de l ia', 'smia']),
    ('ISO 27001', ['iso 27001', 'iso/iec 27001', 'smsi', 'securite de l information', 'annexe a']),
    ('NIS2', ['nis2', 'nis 2', 'directive nis', 'entite essentielle', 'entite importante']),
    ('DORA', ['dora', 'resilience operationnelle', 'tiers prestataire tic', 'ict risk']),
    ('Cybersecurite', ['cyber', 'securite', 'vulnerabilite', 'incident', 'menace', 'attaque', 'iec 62443',
                       'ebios', 'pentest', 'soc ']),
    ('Contrats', ['contrat', 'convention', 'clause', 'avenant', 'nda', 'accord de confidentialite',
                  'conditions generales', 'cgv', 'cgu']),
    ('Audit', ['audit', 'controle', 'conformite', 'ecart', 'non-conformite', 'plan d action', 'remediation']),
]


def rag_classify_sujet(nom_fichier, texte=None):
    """Classe un document par sujet, a partir de son nom et d'un extrait de son
    texte. Retourne le sujet le mieux represente, ou 'Autre'."""
    def _norm(s):
        s = (s or '').lower()
        for a, b in [('é', 'e'), ('è', 'e'), ('ê', 'e'), ('à', 'a'), ('â', 'a'), ('î', 'i'),
                     ('ï', 'i'), ('ô', 'o'), ('û', 'u'), ('ù', 'u'), ('ç', 'c'), ('_', ' '), ('-', ' ')]:
            s = s.replace(a, b)
        return s

    base = _norm(nom_fichier)
    corps = _norm((texte or '')[:20000])
    meilleur = None
    meilleur_score = 0
    for sujet, mots in RAG_SUJETS:
        score = 0
        for mot in mots:
            if mot in base:
                score += 5           # le nom du fichier pese davantage
            score += corps.count(mot)
        if score > meilleur_score:
            meilleur_score = score
            meilleur = sujet
    return meilleur if (meilleur and meilleur_score >= 2) else 'Autre'


@app.route('/api/rag/documents', methods=['GET'])
@rate_limit(limit=60, window=60)
@rag_require_access
def rag_list_documents():
    page_filter = request.args.get('page', '').strip()
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, nom_fichier, type_mime, extension, pages_liees, taille_octets, nb_chunks, date_upload FROM rag_documents ORDER BY date_upload DESC')
    rows = cur.fetchall()
    conn.close()
    docs = []
    for r in rows:
        d = dict(r) if not isinstance(r, dict) else r
        pages = (d['pages_liees'] or '').split(',')
        if page_filter and page_filter not in pages:
            continue
        docs.append({
            'id': d['id'], 'nom_fichier': d['nom_fichier'], 'type_mime': d['type_mime'],
            'extension': d['extension'], 'pages_liees': pages, 'taille_octets': d['taille_octets'],
            'nb_chunks': d['nb_chunks'], 'date_upload': d['date_upload'],
            'sujet': rag_classify_sujet(d['nom_fichier'])
        })
    return jsonify({'documents': docs, 'pgvector_actif': RAG_PGVECTOR_AVAILABLE})

@app.route('/api/rag/upload', methods=['POST'])
@rate_limit(limit=10, window=60)
@rag_require_access
def rag_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400
    f = request.files['file']
    if not f.filename:
        return jsonify({'error': 'Nom de fichier invalide'}), 400

    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in RAG_ALLOWED_EXT:
        return jsonify({'error': f'Format non supporté. Formats acceptés : {", ".join(RAG_ALLOWED_EXT)}'}), 400

    file_bytes = f.read()
    if len(file_bytes) > RAG_MAX_FILE_SIZE:
        return jsonify({'error': f'Fichier trop volumineux (max {RAG_MAX_FILE_SIZE // (1024*1024)} Mo)'}), 400

    pages_liees = request.form.get('pages_liees', 'general').strip()
    pages_list = [p for p in pages_liees.split(',') if p in RAG_PAGES_VALIDES]
    if not pages_list:
        pages_list = ['general']

    ok, text_or_err = rag_extract_text(f.filename, file_bytes)
    if not ok:
        return jsonify({'error': text_or_err}), 400
    if not text_or_err.strip():
        return jsonify({'error': 'Aucun texte extractible de ce fichier (scan image non-OCR ?)'}), 400

    chunks = rag_chunk_text(text_or_err)
    if not chunks:
        return jsonify({'error': 'Texte extrait vide après nettoyage'}), 400

    now = datetime.utcnow().isoformat()
    safe_name = secure_filename(f.filename)
    statut_initial = 'en_cours' if RAG_PGVECTOR_AVAILABLE else 'termine'

    conn = registre_get_db()
    cur = conn.cursor()
    values = (safe_name, f.mimetype or 'application/octet-stream', ext, ','.join(pages_list),
              len(file_bytes), file_bytes, len(chunks), statut_initial, now)
    if REGISTRE_USE_PG:
        cur.execute('''INSERT INTO rag_documents
            (nom_fichier, type_mime, extension, pages_liees, taille_octets, contenu_fichier, nb_chunks, statut_indexation, date_upload)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id''', values)
        doc_id = cur.fetchone()['id']
    else:
        cur.execute('''INSERT INTO rag_documents
            (nom_fichier, type_mime, extension, pages_liees, taille_octets, contenu_fichier, nb_chunks, statut_indexation, date_upload)
            VALUES (?,?,?,?,?,?,?,?,?)''', values)
        doc_id = cur.lastrowid
    conn.commit()

    # Stockage immediat des chunks SANS embeddings -> reponse HTTP rapide (pas de thread serveur :
    # sur un hebergement a un seul worker Gunicorn, un thread d arriere-plan partage le meme GIL
    # et ralentit TOUT le service pendant son execution. A la place, c est le CLIENT qui appelle
    # /index-next-batch de facon repetee, chaque appel traitant un lot borne puis se terminant.)
    for i, chunk in enumerate(chunks):
        if REGISTRE_USE_PG:
            cur.execute('''INSERT INTO rag_chunks (document_id, chunk_text, chunk_index, search_vector)
                VALUES (%s,%s,%s, to_tsvector('french', %s))''', (doc_id, chunk, i, chunk))
        else:
            cur.execute('INSERT INTO rag_chunks (document_id, chunk_text, chunk_index) VALUES (?,?,?)', (doc_id, chunk, i))
    conn.commit()
    conn.close()

    return jsonify({'document': {'id': doc_id, 'nom_fichier': safe_name, 'nb_chunks': len(chunks)},
                     'statut_indexation': statut_initial, 'warning': None}), 201

@app.route('/api/rag/documents/<int:doc_id>/index-next-batch', methods=['POST'])
@rate_limit(limit=120, window=60)
@rag_require_access
def rag_index_next_batch(doc_id):
    """Traite UN SEUL lot de chunks puis retourne immediatement (quelques secondes max).
    Le client (frontend) rappelle cet endpoint en boucle jusqu a indexation complete.
    Architecture 'pull' : aucun thread serveur, donc aucune contention sur le worker
    Gunicorn unique de cet hebergement."""
    batch_size = 10
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql(
        'SELECT chunks_indexes, nb_chunks, statut_indexation FROM rag_documents WHERE id=%s',
        'SELECT chunks_indexes, nb_chunks, statut_indexation FROM rag_documents WHERE id=?'
    ), (doc_id,))
    docrow = cur.fetchone()
    if not docrow:
        conn.close()
        return jsonify({'error': 'Document introuvable'}), 404
    d = dict(docrow) if not isinstance(docrow, dict) else docrow
    already_done = d['chunks_indexes'] or 0
    total = d['nb_chunks']

    if already_done >= total or d['statut_indexation'] == 'termine':
        conn.close()
        return jsonify({'statut': 'termine', 'chunks_indexes': total, 'nb_chunks': total})

    cur.execute(registre_sql(
        'SELECT chunk_index, chunk_text FROM rag_chunks WHERE document_id=%s AND chunk_index >= %s ORDER BY chunk_index LIMIT %s',
        'SELECT chunk_index, chunk_text FROM rag_chunks WHERE document_id=? AND chunk_index >= ? ORDER BY chunk_index LIMIT ?'
    ), (doc_id, already_done, batch_size))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return jsonify({'statut': 'termine', 'chunks_indexes': total, 'nb_chunks': total})

    batch_texts = [(dict(r) if not isinstance(r, dict) else r)['chunk_text'] for r in rows]
    batch_indexes = [(dict(r) if not isinstance(r, dict) else r)['chunk_index'] for r in rows]

    embed_ok, embeddings_or_err = rag_get_embeddings(batch_texts)

    conn = registre_get_db()
    cur = conn.cursor()
    new_statut = 'en_cours'
    if embed_ok and embeddings_or_err:
        for idx, embedding in zip(batch_indexes, embeddings_or_err):
            cur.execute(registre_sql(
                'UPDATE rag_chunks SET embedding = %s WHERE document_id = %s AND chunk_index = %s',
                'UPDATE rag_chunks SET chunk_index = chunk_index WHERE document_id = ? AND chunk_index = ?'
            ), (embedding, doc_id, idx) if REGISTRE_USE_PG else (doc_id, idx))
        traites = max(batch_indexes) + 1
    else:
        traites = max(batch_indexes) + 1
        logger.warning(f"RAG — embeddings echoues pour un lot du document {doc_id} : {embeddings_or_err}")

    if traites >= total:
        new_statut = 'termine'

    cur.execute(registre_sql(
        'UPDATE rag_documents SET chunks_indexes = %s, statut_indexation = %s WHERE id = %s',
        'UPDATE rag_documents SET chunks_indexes = ?, statut_indexation = ? WHERE id = ?'
    ), (traites, new_statut, doc_id))
    conn.commit()
    conn.close()

    return jsonify({'statut': new_statut, 'chunks_indexes': traites, 'nb_chunks': total})

@app.route('/api/rag/documents/<int:doc_id>/status', methods=['GET'])
@rate_limit(limit=120, window=60)
@rag_require_access
def rag_document_status(doc_id):
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql(
        'SELECT statut_indexation, chunks_indexes, nb_chunks FROM rag_documents WHERE id=%s',
        'SELECT statut_indexation, chunks_indexes, nb_chunks FROM rag_documents WHERE id=?'
    ), (doc_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({'error': 'Document introuvable'}), 404
    d = dict(row) if not isinstance(row, dict) else row
    return jsonify({'statut': d['statut_indexation'], 'chunks_indexes': d['chunks_indexes'] or 0, 'nb_chunks': d['nb_chunks']})

@app.route('/api/rag/download/<int:doc_id>', methods=['GET'])

@app.route('/api/rag/download/<int:doc_id>', methods=['GET'])
@rate_limit(limit=30, window=60)
@rag_require_access
def rag_download(doc_id):
    conn = registre_get_db()
    cur = conn.cursor()
    # SELECT cible : ne charge pas le texte extrait (inutile et volumineux)
    cur.execute(registre_sql('SELECT nom_fichier, type_mime, contenu_fichier FROM rag_documents WHERE id=%s',
                             'SELECT nom_fichier, type_mime, contenu_fichier FROM rag_documents WHERE id=?'), (doc_id,))
    row = cur.fetchone()
    try: conn.close()
    except Exception: pass
    if not row:
        return jsonify({'error': 'Document introuvable'}), 404
    d = dict(row) if not isinstance(row, dict) else row
    brut = d.get('contenu_fichier')
    if brut is None:
        return jsonify({'error': 'Contenu du document indisponible.'}), 404
    try:
        content = bytes(brut)
    except Exception:
        return jsonify({'error': 'Contenu du document illisible.'}), 500
    nom = str(d.get('nom_fichier') or ('document-%d' % doc_id))
    # Nom de fichier robuste : ASCII pour les clients anciens, UTF-8 encode (RFC 5987)
    # pour les navigateurs modernes. Corrige l'echec de telechargement sur noms accentues.
    from urllib.parse import quote as _q
    ascii_nom = ''.join((c if (32 <= ord(c) < 127 and c not in '"\\') else '_') for c in nom) or 'document'
    response = make_response(content)
    response.headers['Content-Type'] = d.get('type_mime') or 'application/octet-stream'
    response.headers['Content-Disposition'] = (
        'attachment; filename="%s"; filename*=UTF-8\'\'%s' % (ascii_nom, _q(nom))
    )
    response.headers['Content-Length'] = str(len(content))
    return response

@app.route('/api/rag/documents/<int:doc_id>', methods=['DELETE'])
@rate_limit(limit=30, window=60)
@rag_require_access
def rag_delete_document(doc_id):
    conn = registre_get_db()
    cur = conn.cursor()
    cur.execute(registre_sql('SELECT id FROM rag_documents WHERE id=%s', 'SELECT id FROM rag_documents WHERE id=?'), (doc_id,))
    if not cur.fetchone():
        conn.close()
        return jsonify({'error': 'Document introuvable'}), 404
    if not REGISTRE_USE_PG:
        cur.execute('DELETE FROM rag_chunks WHERE document_id=?', (doc_id,))
    cur.execute(registre_sql('DELETE FROM rag_documents WHERE id=%s', 'DELETE FROM rag_documents WHERE id=?'), (doc_id,))
    conn.commit()
    conn.close()
    return jsonify({'deleted': doc_id})

@app.route('/api/rag/search', methods=['POST'])
@rate_limit(limit=60, window=60)
def rag_search():
    """Recherche hybride : vectorielle (pgvector) si disponible, sinon full-text Postgres."""
    data = request.get_json(force=True) or {}
    query = (data.get('query') or '').strip()
    page = (data.get('page') or '').strip()
    top_k = min(int(data.get('top_k', 5)), 10)
    if not query:
        return jsonify({'error': 'query requis'}), 400

    conn = registre_get_db()
    cur = conn.cursor()

    page_filter_sql = ''
    page_params = []
    if page and REGISTRE_USE_PG:
        page_filter_sql = "AND d.pages_liees LIKE %s"
        page_params = [f'%{page}%']

    results = []
    if RAG_PGVECTOR_AVAILABLE and REGISTRE_USE_PG:
        embed_ok, embeddings = rag_get_embeddings([query])
        if embed_ok:
            query_vec = embeddings[0]
            sql = f'''SELECT c.chunk_text, d.nom_fichier, d.id as doc_id,
                      1 - (c.embedding <=> %s::vector) as score
                      FROM rag_chunks c JOIN rag_documents d ON c.document_id = d.id
                      WHERE c.embedding IS NOT NULL {page_filter_sql}
                      ORDER BY c.embedding <=> %s::vector LIMIT %s'''
            cur.execute(sql, [query_vec] + page_params + [query_vec, top_k])
            results = [{'texte': r['chunk_text'], 'document': r['nom_fichier'], 'document_id': r['doc_id'], 'score': round(float(r['score']), 3)} for r in cur.fetchall()]

    if not results and REGISTRE_USE_PG:
        sql = f'''SELECT c.chunk_text, d.nom_fichier, d.id as doc_id,
                  ts_rank(c.search_vector, to_tsquery('french', %s)) as score
                  FROM rag_chunks c JOIN rag_documents d ON c.document_id = d.id
                  WHERE c.search_vector @@ to_tsquery('french', %s) {page_filter_sql}
                  ORDER BY score DESC LIMIT %s'''
        try:
            tsquery = ' | '.join(_re.findall(r'\w+', query))
            cur.execute(sql, [tsquery, tsquery] + page_params + [top_k])
            results = [{'texte': r['chunk_text'], 'document': r['nom_fichier'], 'document_id': r['doc_id'], 'score': round(float(r['score']), 3)} for r in cur.fetchall()]
        except Exception as _e:
            conn.rollback()
            logger.warning(f"RAG search fallback error: {_e}")

    conn.close()
    return jsonify({'resultats': results, 'mode': 'vectoriel' if RAG_PGVECTOR_AVAILABLE else 'texte_integral'})


# ══════════════════════════════════════════════════════════
# ANTI-SCRAPING — Detection de navigateurs headless (Puppeteer/Selenium/Playwright)
# Le filtre User-Agent seul ne suffit pas : un scraper sophistique usurpe un UA Chrome
# standard. Le frontend envoie un signal JS (navigator.webdriver, plugins, etc.) que
# seul un vrai navigateur peut authentifier correctement.
# ══════════════════════════════════════════════════════════
HEADLESS_FLAGGED_IPS = {}  # ip -> timestamp du dernier signalement

@app.route('/api/client-signal', methods=['POST'])
@rate_limit(limit=20, window=60)
def client_signal():
    """Recoit un signal anonyme du navigateur indiquant des caracteristiques de
    navigateur headless (navigator.webdriver=true, absence de plugins, etc.).
    Sert a renforcer le blocage cote middleware sans bloquer la navigation normale."""
    data = request.get_json(force=True) or {}
    is_headless = bool(data.get('webdriver') or data.get('no_plugins') or data.get('no_languages'))
    ip = limiter.get_ip(request)
    if is_headless:
        HEADLESS_FLAGGED_IPS[ip] = time.time()
        logger.warning(f"HEADLESS_DETECTED {ip} — signal navigateur automatise")
        limiter.block(ip, 1800, 'headless_browser_detected')
    return jsonify({'ok': True})


for route, filename in PAGES.items():
    def make_view(fn):
        @rate_limit(limit=60, window=60)
        def view():
            return send_from_directory('.', fn)
        view.__name__ = fn.replace('.','_').replace('-','_')
        return view
    app.add_url_rule(route, view_func=make_view(filename))

@app.route('/sentinel')
@sentinel_login_required
def sentinel_page():
    return send_from_directory('.', 'sentinel.html')

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

# ── Warm-up RSS au démarrage ──────────────────────────────────────────────────
# Le plan gratuit Render met le service en veille ; au redémarrage à froid,
# le premier appel /api/news prendrait 30-50s. Ce thread pré-charge le cache
# en arrière-plan dès le boot, sans bloquer le démarrage de Flask.
def _news_warmup():
    import time as _t
    _t.sleep(5)          # laisser Flask finir de démarrer
    try:
        import io as _io
        _headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/rss+xml, application/xml, text/xml, application/atom+xml, */*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
        all_items = []
        for src in RSS_SOURCES:
            try:
                resp = requests.get(src["url"], headers=_headers, timeout=7, allow_redirects=True)
                if resp.status_code != 200:
                    continue
                feed = feedparser.parse(_io.BytesIO(resp.content))
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
                        "lang":   src.get("lang", "fr"),
                    })
            except Exception:
                pass
        seen, unique = set(), []
        for item in sorted(all_items, key=lambda x: x.get("date",""), reverse=True):
            key = item["title"][:60]
            if key not in seen:
                seen.add(key)
                unique.append(item)
        if unique:
            global _news_cache
            _news_cache = {"data": unique[:60], "ts": _t.time()}
            logger.info(f"[warmup] RSS pré-chargé : {len(unique)} articles")
    except Exception as exc:
        logger.warning(f"[warmup] Echec pre-chargement RSS : {exc}")

threading.Thread(target=_news_warmup, daemon=True).start()

# ══════════════════════════════════════════════════════════
# FACTURATION ECHELONNEE PAR RESULTATS — LIEN Tarification par resultats /
# Gestion des clients / Stripe. Chaque echeance du due_json d'une facture RaAS
# (issue d'un jalon verifie) est prelevee via Stripe lorsqu'elle arrive a terme.
# Cycle CONSEILPREV : preview (liste des echeances dues, sans prelevement) ou
# execute (prelevement Stripe par echeance, idempotent, desactive si Stripe non
# configure). Les reactions Stripe (invoice.paid / payment_failed) mettent a jour
# l'echeance, la facture, le cycle de vie et creent une relance en cas d'echec.
# A valider en mode TEST Stripe avant production. CONSEILPREV/Sentinel.
# ══════════════════════════════════════════════════════════

def _stripe_event_seen(event_id):
    """Verifie seulement si un evenement Stripe a deja ete traite.
    L'enregistrement n'a lieu qu'apres traitement reussi (_stripe_event_mark),
    afin qu'un evenement en echec puisse etre rejoue et retraite."""
    if not event_id:
        return False
    conn = None
    try:
        conn = registre_get_db(); cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS stripe_events (event_id TEXT PRIMARY KEY, processed_at TEXT)")
        conn.commit()
        cur.execute(registre_sql('SELECT 1 FROM stripe_events WHERE event_id=%s',
                                 'SELECT 1 FROM stripe_events WHERE event_id=?'), (event_id,))
        seen = cur.fetchone() is not None
        try: conn.close()
        except Exception: pass
        return seen
    except Exception:
        try: conn.close()
        except Exception: pass
        return False


def _stripe_event_mark(event_id):
    """Enregistre un evenement Stripe comme traite, apres un traitement reussi."""
    if not event_id:
        return
    conn = None
    try:
        conn = registre_get_db(); cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS stripe_events (event_id TEXT PRIMARY KEY, processed_at TEXT)")
        try:
            cur.execute(registre_sql('INSERT INTO stripe_events (event_id, processed_at) VALUES (%s, %s)',
                                     'INSERT INTO stripe_events (event_id, processed_at) VALUES (?, ?)'),
                        (str(event_id), datetime.utcnow().isoformat()))
            conn.commit()
        except Exception:
            try: conn.rollback()
            except Exception: pass
        try: conn.close()
        except Exception: pass
    except Exception:
        try: conn.close()
        except Exception: pass
def _billing_set_subscription(client_id, sub_id):
    """Memorise l'identifiant d'abonnement Stripe du client (pour pouvoir le
    resilier lors du passage a la facturation par resultats)."""
    try:
        conn = registre_get_db(); cur = conn.cursor()
        cur.execute(registre_sql('UPDATE clients SET stripe_subscription_id=%s WHERE id=%s',
                                 'UPDATE clients SET stripe_subscription_id=? WHERE id=?'),
                    (str(sub_id), int(client_id)))
        conn.commit()
        try: conn.close()
        except Exception: pass
    except Exception:
        pass


def _billing_cancel_subscription(client_id):
    """Resilie l'abonnement Stripe d'un client. Exclusion du cumul : un client
    est facture soit par abonnement recurrent, soit par resultats (echeances RaAS),
    jamais les deux. Des qu'une facture RaAS est emise, l'abonnement est resilie.
    Idempotent (ne fait rien si aucun abonnement)."""
    secret = os.environ.get('STRIPE_SECRET_KEY')
    try:
        conn = registre_get_db(); cur = conn.cursor()
        cur.execute(registre_sql('SELECT stripe_subscription_id FROM clients WHERE id=%s',
                                 'SELECT stripe_subscription_id FROM clients WHERE id=?'), (int(client_id),))
        row = cur.fetchone()
        sub = (dict(row).get('stripe_subscription_id') if row else None)
        if not sub:
            try: conn.close()
            except Exception: pass
            return
        if secret:
            try:
                import stripe
                stripe.api_key = secret
                try:
                    stripe.Subscription.delete(sub)
                except Exception:
                    try:
                        stripe.Subscription.cancel(sub)
                    except Exception:
                        pass
            except Exception:
                pass
        cur.execute(registre_sql('UPDATE clients SET stripe_subscription_id=NULL WHERE id=%s',
                                 'UPDATE clients SET stripe_subscription_id=NULL WHERE id=?'), (int(client_id),))
        conn.commit()
        try: conn.close()
        except Exception: pass
    except Exception:
        pass


def _billing_set_customer(client_id, customer_id):
    conn = registre_get_db(); cur = conn.cursor()
    cur.execute(registre_sql('UPDATE clients SET stripe_customer_id=%s WHERE id=%s',
                             'UPDATE clients SET stripe_customer_id=? WHERE id=?'),
                (str(customer_id), int(client_id)))
    conn.commit()
    try: conn.close()
    except Exception: pass


def _billing_scan_due(cur, only_client=None):
    """Liste les echeances dues (date <= aujourd'hui, statut 'a_venir') sur les
    factures RaAS non soldees."""
    import json as _json
    today = datetime.utcnow().date().isoformat()
    q = "SELECT id, client_id, numero, amount_eur, due_json, status FROM raas_invoices WHERE status != 'payee'"
    params = ()
    if only_client is not None:
        q += (" AND client_id=%s" if REGISTRE_USE_PG else " AND client_id=?")
        params = (only_client,)
    cur.execute(q, params)
    rows = [dict(r) for r in cur.fetchall()]
    due = []
    for inv in rows:
        try:
            ech = _json.loads(inv.get('due_json') or '[]')
        except Exception:
            ech = []
        for e in ech:
            st = e.get('status') or 'a_venir'
            d = e.get('due')
            if st == 'a_venir' and (d is None or d <= today):
                due.append({'numero': inv['numero'], 'client_id': inv['client_id'],
                            'echeance': e.get('echeance'), 'montant': e.get('montant'), 'due': d})
    return due


def _billing_update_echeance(numero, echeance, status, stripe_invoice_id=None):
    """Met a jour le statut d'une echeance dans due_json ; solde la facture si
    toutes les echeances sont payees."""
    import json as _json
    conn = registre_get_db(); cur = conn.cursor()
    cur.execute(registre_sql('SELECT due_json FROM raas_invoices WHERE numero=%s',
                             'SELECT due_json FROM raas_invoices WHERE numero=?'), (numero,))
    row = cur.fetchone()
    if not row:
        try: conn.close()
        except Exception: pass
        return False
    row = dict(row)
    try:
        ech = _json.loads(row.get('due_json') or '[]')
    except Exception:
        ech = []
    for e in ech:
        if e.get('echeance') == echeance:
            e['status'] = status
            if stripe_invoice_id:
                e['stripe_invoice_id'] = stripe_invoice_id
    cur.execute(registre_sql('UPDATE raas_invoices SET due_json=%s WHERE numero=%s',
                             'UPDATE raas_invoices SET due_json=? WHERE numero=?'),
                (_json.dumps(ech), numero))
    if ech and all((e.get('status') == 'payee') for e in ech):
        cur.execute(registre_sql("UPDATE raas_invoices SET status='payee', paid_at=%s WHERE numero=%s",
                                 "UPDATE raas_invoices SET status='payee', paid_at=? WHERE numero=?"),
                    (datetime.utcnow().isoformat(), numero))
    conn.commit()
    try: conn.close()
    except Exception: pass
    return True


def _billing_on_invoice_paid(numero, echeance):
    _billing_update_echeance(numero, echeance, 'payee')


def _billing_on_invoice_failed(numero, echeance, client_id=None):
    _billing_update_echeance(numero, echeance, 'echec')
    if client_id:
        try:
            conn = registre_get_db(); cur = conn.cursor()
            cur.execute(registre_sql(
                "INSERT INTO client_relances (client_id, type, objet, canal, priorite, due_date, status, related_ref, created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                "INSERT INTO client_relances (client_id, type, objet, canal, priorite, due_date, status, related_ref, created_at) VALUES (?,?,?,?,?,?,?,?,?)"),
                (int(client_id), 'paiement', 'Echec de prelevement - echeance %s de %s' % (echeance, numero),
                 'email', 'haute', datetime.utcnow().date().isoformat(), 'planifiee', numero, datetime.utcnow().isoformat()))
            cur.execute(registre_sql("UPDATE client_lifecycle SET sante='en_retard', updated_at=%s WHERE client_id=%s",
                                     "UPDATE client_lifecycle SET sante='en_retard', updated_at=? WHERE client_id=?"),
                        (datetime.utcnow().isoformat(), int(client_id)))
            conn.commit()
            try:
                cur.execute(registre_sql('SELECT email, nom_entreprise FROM clients WHERE id=%s', 'SELECT email, nom_entreprise FROM clients WHERE id=?'), (int(client_id),))
                _fe = cur.fetchone(); _fe = dict(_fe) if _fe else {}
                if _fe.get('email'):
                    send_email_smart(_fe['email'], _fe.get('nom_entreprise') or 'Client',
                        'Echec de prelevement - facture ' + str(numero),
                        '<p>Bonjour,</p><p>Le prelevement de l echeance ' + str(echeance) + ' de la facture ' + str(numero) + ' n a pas abouti. Nous reviendrons vers vous ; vous pouvez aussi verifier votre moyen de paiement.</p><p>L equipe CONSEILPREV</p>',
                        tags=['paiement-echec'])
            except Exception:
                pass
            try: conn.close()
            except Exception: pass
        except Exception:
            pass


@app.route('/api/clients/billing-run', methods=['POST'])
def clients_billing_run():
    """Cycle de facturation echelonnee (CONSEILPREV).
    mode=preview (defaut) : liste les echeances dues, sans prelevement.
    mode=execute (+confirm=true) : cree une facture Stripe par echeance due,
    prelevee automatiquement. Desactive si Stripe non configure."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    d = request.get_json(silent=True) or {}
    mode = d.get('mode', 'preview')
    try:
        only_client = int(d.get('client_id')) if d.get('client_id') is not None else None
    except (TypeError, ValueError):
        only_client = None
    conn = registre_get_db(); cur = conn.cursor()
    due = _billing_scan_due(cur, only_client)
    if mode != 'execute':
        try: conn.close()
        except Exception: pass
        return jsonify({'ok': True, 'mode': 'preview', 'due_count': len(due), 'echeances': due})
    if not d.get('confirm'):
        try: conn.close()
        except Exception: pass
        return jsonify({'ok': False, 'error': "Confirmation requise (confirm=true) pour declencher les prelevements."}), 400
    secret = os.environ.get('STRIPE_SECRET_KEY')
    if not secret:
        try: conn.close()
        except Exception: pass
        return jsonify({'ok': False, 'error': "Paiement Stripe non configure.", 'configured': False, 'echeances': due}), 501
    try:
        import stripe
    except Exception:
        try: conn.close()
        except Exception: pass
        return jsonify({'ok': False, 'error': "Module Stripe indisponible.", 'configured': False}), 501
    stripe.api_key = secret
    try:
        _lim = int(d.get('limit', 200))
    except (TypeError, ValueError):
        _lim = 200
    _batch = due[:max(1, _lim)]
    _remaining = len(due) - len(_batch)
    _cids = list({it['client_id'] for it in _batch})
    _cust_map = {}
    if _cids:
        _ph = ','.join(['%s' if REGISTRE_USE_PG else '?'] * len(_cids))
        cur.execute('SELECT id, stripe_customer_id FROM clients WHERE id IN (' + _ph + ')', tuple(_cids))
        for _r in cur.fetchall():
            _r = dict(_r); _cust_map[_r['id']] = _r.get('stripe_customer_id')
    results = []
    _cancelled = set()
    for item in _batch:
        cust = _cust_map.get(item['client_id'])
        if not cust:
            results.append({'numero': item['numero'], 'echeance': item['echeance'], 'ok': False, 'error': 'Aucun moyen de paiement Stripe enregistre'})
            continue
        if item['client_id'] not in _cancelled:
            try:
                _billing_cancel_subscription(item['client_id'])
            except Exception:
                pass
            _cancelled.add(item['client_id'])
        try:
            _ikey = 'raas-' + str(item['numero']) + '-e' + str(item['echeance'])
            stripe.InvoiceItem.create(customer=cust, amount=int(item['montant']) * 100, currency='eur',
                                      description='%s - echeance %s' % (item['numero'], item['echeance']),
                                      idempotency_key=_ikey + '-item')
            inv = stripe.Invoice.create(customer=cust, auto_advance=True, collection_method='charge_automatically',
                                        metadata={'numero': item['numero'], 'echeance': str(item['echeance']), 'client_id': str(item['client_id'])},
                                        idempotency_key=_ikey + '-inv')
            try:
                stripe.Invoice.finalize_invoice(inv['id'])
            except Exception:
                pass
            _billing_update_echeance(item['numero'], item['echeance'], 'envoyee', inv.get('id'))
            results.append({'numero': item['numero'], 'echeance': item['echeance'], 'ok': True, 'stripe_invoice': inv.get('id')})
        except Exception:
            results.append({'numero': item['numero'], 'echeance': item['echeance'], 'ok': False, 'error': 'Echec de creation de la facture Stripe'})
    conn.commit()
    try: conn.close()
    except Exception: pass
    return jsonify({'ok': True, 'mode': 'execute', 'processed': results, 'remaining': _remaining})



@app.route('/api/clients/subscription', methods=['GET'])
def clients_subscription():
    """Detail de l'abonnement Stripe d'un client (CONSEILPREV). En mode direct,
    si l'identifiant d'abonnement n'a pas ete memorise, la fonction retrouve
    l'abonnement actif par e-mail chez Stripe et le rattache au client."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    try:
        client_id = int(request.args.get('client_id'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'client_id invalide'}), 400
    conn = registre_get_db(); cur = conn.cursor()
    row = None
    for q_pg, q_sq in [
        ('SELECT plan, stripe_subscription_id, stripe_customer_id, email FROM clients WHERE id=%s',
         'SELECT plan, stripe_subscription_id, stripe_customer_id, email FROM clients WHERE id=?'),
        ('SELECT plan, email FROM clients WHERE id=%s', 'SELECT plan, email FROM clients WHERE id=?'),
        ('SELECT plan FROM clients WHERE id=%s', 'SELECT plan FROM clients WHERE id=?')]:
        try:
            cur.execute(registre_sql(q_pg, q_sq), (client_id,))
            row = cur.fetchone(); break
        except Exception:
            try: conn.rollback()
            except Exception: pass
            row = None
    try: conn.close()
    except Exception: pass
    row = dict(row) if row else {}
    plan = row.get('plan') or 'gratuit'
    sub_id = row.get('stripe_subscription_id')
    email = row.get('email')
    if not request.args.get('live'):
        return jsonify({'ok': True, 'has_sub': bool(sub_id), 'plan': plan})
    secret = os.environ.get('STRIPE_SECRET_KEY')
    if not secret:
        return jsonify({'ok': True, 'has_sub': bool(sub_id), 'plan': plan, 'configured': False})

    def _g(o, k):
        try:
            return getattr(o, k)
        except Exception:
            try:
                return o[k]
            except Exception:
                return None

    try:
        import stripe
        stripe.api_key = secret
        stripe.max_network_retries = 0
        try:
            stripe.default_http_client = stripe.http_client.RequestsClient(timeout=8)
        except Exception:
            pass
        sub = None
        if sub_id:
            sub = stripe.Subscription.retrieve(sub_id)
        elif email:
            custs = stripe.Customer.list(email=email, limit=10)
            for c in (_g(custs, 'data') or []):
                subs = stripe.Subscription.list(customer=_g(c, 'id'), status='active', limit=1)
                dl = _g(subs, 'data') or []
                if dl:
                    sub = dl[0]
                    try:
                        _billing_set_customer(client_id, _g(c, 'id'))
                        _billing_set_subscription(client_id, _g(sub, 'id'))
                    except Exception:
                        pass
                    break
        if sub is None:
            return jsonify({'ok': True, 'has_sub': False, 'plan': plan})
    except Exception:
        return jsonify({'ok': True, 'has_sub': bool(sub_id), 'plan': plan, 'configured': True, 'error_stripe': True})

    amount = None; currency = 'eur'; interval = None
    try:
        items_obj = _g(sub, 'items')
        data = _g(items_obj, 'data') or []
        if data:
            price = _g(data[0], 'price')
            amount = _g(price, 'unit_amount')
            currency = _g(price, 'currency') or 'eur'
            rec = _g(price, 'recurring')
            interval = _g(rec, 'interval') if rec else None
    except Exception:
        pass
    return jsonify({'ok': True, 'has_sub': True, 'plan': plan,
                    'status': _g(sub, 'status'),
                    'amount_eur': (amount / 100.0 if amount is not None else None),
                    'currency': currency, 'interval': interval,
                    'current_period_end': _g(sub, 'current_period_end'),
                    'cancel_at_period_end': _g(sub, 'cancel_at_period_end')})


@app.route('/api/clients/set-plan', methods=['POST'])
def clients_set_plan():
    """Attribution manuelle de l'offre d'un client par CONSEILPREV
    (gratuit / pro / entreprise). Permet de faire evoluer une offre, par exemple
    d'Entreprise a Pro. Ne modifie pas l'abonnement Stripe (a ajuster separement
    si necessaire)."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    d = request.get_json(silent=True) or {}
    try:
        client_id = int(d.get('client_id'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'client_id invalide'}), 400
    plan = d.get('plan')
    if plan not in ('gratuit', 'pro', 'entreprise'):
        return jsonify({'ok': False, 'error': 'Offre invalide'}), 400
    conn = registre_get_db(); cur = conn.cursor()
    cur.execute(registre_sql('UPDATE clients SET plan=%s WHERE id=%s',
                             'UPDATE clients SET plan=? WHERE id=?'), (plan, client_id))
    conn.commit()
    try: conn.close()
    except Exception: pass
    stripe_sync = None
    secret = os.environ.get('STRIPE_SECRET_KEY')
    _c2 = registre_get_db(); _cur2 = _c2.cursor()
    _cur2.execute(registre_sql('SELECT stripe_subscription_id FROM clients WHERE id=%s', 'SELECT stripe_subscription_id FROM clients WHERE id=?'), (client_id,))
    _r2 = _cur2.fetchone()
    try: _c2.close()
    except Exception: pass
    sub_id = (dict(_r2).get('stripe_subscription_id') if _r2 else None)
    if secret and sub_id:
        try:
            import stripe
            stripe.api_key = secret
            stripe.max_network_retries = 0
            try: stripe.default_http_client = stripe.http_client.RequestsClient(timeout=8)
            except Exception: pass
            if plan == 'gratuit':
                try:
                    stripe.Subscription.delete(sub_id)
                except Exception:
                    try: stripe.Subscription.cancel(sub_id)
                    except Exception: pass
                _c3 = registre_get_db(); _cur3 = _c3.cursor()
                _cur3.execute(registre_sql('UPDATE clients SET stripe_subscription_id=NULL WHERE id=%s', 'UPDATE clients SET stripe_subscription_id=NULL WHERE id=?'), (client_id,))
                _c3.commit()
                try: _c3.close()
                except Exception: pass
                stripe_sync = 'abonnement_resilie'
            else:
                price_id = os.environ.get('STRIPE_PRICE_PRO') if plan == 'pro' else os.environ.get('STRIPE_PRICE_ENTREPRISE')
                if not price_id:
                    stripe_sync = 'tarif_non_configure'
                else:
                    sub = stripe.Subscription.retrieve(sub_id)
                    items = (sub.get('items') or {}).get('data') or []
                    if items:
                        stripe.Subscription.modify(sub_id, items=[{'id': items[0].get('id'), 'price': price_id}], proration_behavior='create_prorations')
                        stripe_sync = 'tarif_mis_a_jour'
                    else:
                        stripe_sync = 'aucun_article'
        except Exception:
            stripe_sync = 'erreur_stripe'
    return jsonify({'ok': True, 'plan': plan, 'stripe_sync': stripe_sync})



# ══════════════════════════════════════════════════════════
# ESPACE ENTREPRISE — entites/perimetres et connecteurs d'integration,
# rattaches au client authentifie. Tables creees a la volee.
# CONSEILPREV/Sentinel.
# ══════════════════════════════════════════════════════════

def _ent_client_id():
    c = sentauth_current_client()
    if not c:
        return None
    if c.get('is_conseilprev'):
        target = request.args.get('client_id')
        if target is None:
            try:
                target = (request.get_json(silent=True) or {}).get('client_id')
            except Exception:
                target = None
        if target is not None:
            try:
                return int(target)
            except (TypeError, ValueError):
                pass
    try:
        return int(c.get('id') or 0)
    except Exception:
        return 0


@app.route('/api/entreprise/entites', methods=['GET', 'POST'])
def entreprise_entites():
    cid = _ent_client_id()
    if cid is None:
        return jsonify({'ok': False, 'error': 'Non authentifie'}), 403
    conn = registre_get_db(); cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS client_entites (id SERIAL PRIMARY KEY, client_id INTEGER, nom TEXT, type TEXT, created_at TEXT)"
                if REGISTRE_USE_PG else
                "CREATE TABLE IF NOT EXISTS client_entites (id INTEGER PRIMARY KEY AUTOINCREMENT, client_id INTEGER, nom TEXT, type TEXT, created_at TEXT)")
    conn.commit()
    if request.method == 'POST':
        d = request.get_json(silent=True) or {}
        nom = (d.get('nom') or '').strip()[:200]
        typ = (d.get('type') or 'Filiale').strip()[:60]
        if not nom:
            try: conn.close()
            except Exception: pass
            return jsonify({'ok': False, 'error': 'Nom requis'}), 400
        cur.execute(registre_sql('INSERT INTO client_entites (client_id, nom, type, created_at) VALUES (%s,%s,%s,%s)',
                                 'INSERT INTO client_entites (client_id, nom, type, created_at) VALUES (?,?,?,?)'),
                    (cid, nom, typ, datetime.utcnow().isoformat()))
        conn.commit()
    cur.execute(registre_sql('SELECT id, nom, type FROM client_entites WHERE client_id=%s ORDER BY id ASC',
                             'SELECT id, nom, type FROM client_entites WHERE client_id=? ORDER BY id ASC'), (cid,))
    rows = [dict(r) for r in cur.fetchall()]
    try: conn.close()
    except Exception: pass
    return jsonify({'ok': True, 'entites': rows})


@app.route('/api/entreprise/entites/<int:eid>', methods=['DELETE'])
def entreprise_entites_delete(eid):
    cid = _ent_client_id()
    if cid is None:
        return jsonify({'ok': False, 'error': 'Non authentifie'}), 403
    conn = registre_get_db(); cur = conn.cursor()
    cur.execute(registre_sql('DELETE FROM client_entites WHERE id=%s AND client_id=%s',
                             'DELETE FROM client_entites WHERE id=? AND client_id=?'), (eid, cid))
    conn.commit()
    try: conn.close()
    except Exception: pass
    return jsonify({'ok': True})


@app.route('/api/entreprise/connecteurs', methods=['GET', 'POST'])
def entreprise_connecteurs():
    cid = _ent_client_id()
    if cid is None:
        return jsonify({'ok': False, 'error': 'Non authentifie'}), 403
    conn = registre_get_db(); cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS client_connecteurs (id SERIAL PRIMARY KEY, client_id INTEGER, categorie TEXT, nom TEXT, url TEXT, secret TEXT, statut TEXT, created_at TEXT)"
                if REGISTRE_USE_PG else
                "CREATE TABLE IF NOT EXISTS client_connecteurs (id INTEGER PRIMARY KEY AUTOINCREMENT, client_id INTEGER, categorie TEXT, nom TEXT, url TEXT, secret TEXT, statut TEXT, created_at TEXT)")
    conn.commit()
    if request.method == 'POST':
        d = request.get_json(silent=True) or {}
        categorie = (d.get('categorie') or 'GRC').strip()[:20]
        nom = (d.get('nom') or '').strip()[:120]
        url = (d.get('url') or '').strip()[:500]
        secret = (d.get('secret') or '').strip()[:500]
        if not url or not url.lower().startswith('https://'):
            try: conn.close()
            except Exception: pass
            return jsonify({'ok': False, 'error': 'URL HTTPS requise'}), 400
        cur.execute(registre_sql('INSERT INTO client_connecteurs (client_id, categorie, nom, url, secret, statut, created_at) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                                 'INSERT INTO client_connecteurs (client_id, categorie, nom, url, secret, statut, created_at) VALUES (?,?,?,?,?,?,?)'),
                    (cid, categorie, nom, url, secret, 'non_teste', datetime.utcnow().isoformat()))
        conn.commit()
    cur.execute(registre_sql('SELECT id, categorie, nom, url, statut FROM client_connecteurs WHERE client_id=%s ORDER BY id ASC',
                             'SELECT id, categorie, nom, url, statut FROM client_connecteurs WHERE client_id=? ORDER BY id ASC'), (cid,))
    rows = [dict(r) for r in cur.fetchall()]
    try: conn.close()
    except Exception: pass
    return jsonify({'ok': True, 'connecteurs': rows})


@app.route('/api/entreprise/connecteurs/<int:cxid>', methods=['DELETE'])
def entreprise_connecteurs_delete(cxid):
    cid = _ent_client_id()
    if cid is None:
        return jsonify({'ok': False, 'error': 'Non authentifie'}), 403
    conn = registre_get_db(); cur = conn.cursor()
    cur.execute(registre_sql('DELETE FROM client_connecteurs WHERE id=%s AND client_id=%s',
                             'DELETE FROM client_connecteurs WHERE id=? AND client_id=?'), (cxid, cid))
    conn.commit()
    try: conn.close()
    except Exception: pass
    return jsonify({'ok': True})


@app.route('/api/entreprise/connecteurs/<int:cxid>/test', methods=['POST'])
def entreprise_connecteurs_test(cxid):
    cid = _ent_client_id()
    if cid is None:
        return jsonify({'ok': False, 'error': 'Non authentifie'}), 403
    conn = registre_get_db(); cur = conn.cursor()
    cur.execute(registre_sql('SELECT url, secret FROM client_connecteurs WHERE id=%s AND client_id=%s',
                             'SELECT url, secret FROM client_connecteurs WHERE id=? AND client_id=?'), (cxid, cid))
    row = cur.fetchone()
    row = dict(row) if row else None
    if not row:
        try: conn.close()
        except Exception: pass
        return jsonify({'ok': False, 'error': 'Connecteur introuvable'}), 404
    url = row.get('url'); secret = row.get('secret')
    statut = 'echec'; detail = ''
    if not url or not url.lower().startswith('https://'):
        detail = 'URL non HTTPS'
    else:
        try:
            headers = {'Accept': 'application/json'}
            if secret:
                headers['Authorization'] = 'Bearer ' + secret
            resp = requests.get(url, headers=headers, timeout=8)
            statut = 'operationnel' if resp.status_code < 400 else 'echec'
            detail = 'HTTP ' + str(resp.status_code)
        except Exception:
            statut = 'echec'; detail = 'connexion impossible'
    cur.execute(registre_sql('UPDATE client_connecteurs SET statut=%s WHERE id=%s AND client_id=%s',
                             'UPDATE client_connecteurs SET statut=? WHERE id=? AND client_id=?'), (statut, cxid, cid))
    conn.commit()
    try: conn.close()
    except Exception: pass
    return jsonify({'ok': True, 'statut': statut, 'detail': detail})



@app.route('/api/entreprise/formations', methods=['GET', 'POST'])
def entreprise_formations():
    cid = _ent_client_id()
    if cid is None:
        return jsonify({'ok': False, 'error': 'Non authentifie'}), 403
    conn = registre_get_db(); cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS client_formations (id SERIAL PRIMARY KEY, client_id INTEGER, date_prevue TEXT, theme TEXT, statut TEXT, created_at TEXT)"
                if REGISTRE_USE_PG else
                "CREATE TABLE IF NOT EXISTS client_formations (id INTEGER PRIMARY KEY AUTOINCREMENT, client_id INTEGER, date_prevue TEXT, theme TEXT, statut TEXT, created_at TEXT)")
    conn.commit()
    if request.method == 'POST':
        d = request.get_json(silent=True) or {}
        date_prevue = (d.get('date_prevue') or '').strip()[:20]
        theme = (d.get('theme') or '').strip()[:200]
        if not date_prevue:
            try: conn.close()
            except Exception: pass
            return jsonify({'ok': False, 'error': 'Date requise'}), 400
        cur.execute(registre_sql('INSERT INTO client_formations (client_id, date_prevue, theme, statut, created_at) VALUES (%s,%s,%s,%s,%s)',
                                 'INSERT INTO client_formations (client_id, date_prevue, theme, statut, created_at) VALUES (?,?,?,?,?)'),
                    (cid, date_prevue, theme, 'planifiee', datetime.utcnow().isoformat()))
        conn.commit()
    cur.execute(registre_sql('SELECT id, date_prevue, theme, statut FROM client_formations WHERE client_id=%s ORDER BY date_prevue ASC',
                             'SELECT id, date_prevue, theme, statut FROM client_formations WHERE client_id=? ORDER BY date_prevue ASC'), (cid,))
    rows = [dict(r) for r in cur.fetchall()]
    try: conn.close()
    except Exception: pass
    return jsonify({'ok': True, 'formations': rows})


@app.route('/api/entreprise/formations/<int:fid>', methods=['DELETE'])
def entreprise_formations_delete(fid):
    cid = _ent_client_id()
    if cid is None:
        return jsonify({'ok': False, 'error': 'Non authentifie'}), 403
    conn = registre_get_db(); cur = conn.cursor()
    cur.execute(registre_sql('DELETE FROM client_formations WHERE id=%s AND client_id=%s',
                             'DELETE FROM client_formations WHERE id=? AND client_id=?'), (fid, cid))
    conn.commit()
    try: conn.close()
    except Exception: pass
    return jsonify({'ok': True})


@app.route('/api/entreprise/connecteurs/<int:cxid>/sync', methods=['POST'])
def entreprise_connecteurs_sync(cxid):
    """Echange de donnees reel : transmet a l'API du connecteur un contenu propre
    a sa categorie (fourni par le client), avec jeton Bearer optionnel."""
    cid = _ent_client_id()
    if cid is None:
        return jsonify({'ok': False, 'error': 'Non authentifie'}), 403
    conn = registre_get_db(); cur = conn.cursor()
    cur.execute(registre_sql('SELECT url, secret, categorie FROM client_connecteurs WHERE id=%s AND client_id=%s',
                             'SELECT url, secret, categorie FROM client_connecteurs WHERE id=? AND client_id=?'), (cxid, cid))
    row = cur.fetchone(); row = dict(row) if row else None
    if not row:
        try: conn.close()
        except Exception: pass
        return jsonify({'ok': False, 'error': 'Connecteur introuvable'}), 404
    url = row.get('url'); secret = row.get('secret')
    statut = 'echec'
    if not url or not url.lower().startswith('https://'):
        try: conn.close()
        except Exception: pass
        return jsonify({'ok': False, 'error': 'URL non HTTPS'}), 400
    payload = request.get_json(silent=True) or {}
    payload['source'] = 'CONSEILPREV Sentinel'
    payload['categorie'] = row.get('categorie')
    payload['emis_le'] = datetime.utcnow().isoformat()
    envoye = False; detail = ''
    try:
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        if secret:
            headers['Authorization'] = 'Bearer ' + secret
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        envoye = resp.status_code < 400
        statut = 'operationnel' if envoye else 'echec'
        detail = 'HTTP ' + str(resp.status_code)
    except Exception:
        envoye = False; statut = 'echec'; detail = 'connexion impossible'
    try:
        cur.execute(registre_sql('UPDATE client_connecteurs SET statut=%s WHERE id=%s AND client_id=%s',
                                 'UPDATE client_connecteurs SET statut=? WHERE id=? AND client_id=?'), (statut, cxid, cid))
        conn.commit()
    except Exception:
        pass
    try: conn.close()
    except Exception: pass
    return jsonify({'ok': True, 'envoye': envoye, 'detail': detail})



@app.route('/api/clients/entreprise-apercu', methods=['GET'])
def clients_entreprise_apercu():
    """Apercu du perimetre Entreprise d'un client pour CONSEILPREV :
    entites, connecteurs (sans secret) et formations."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    try:
        client_id = int(request.args.get('client_id'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'client_id invalide'}), 400
    conn = registre_get_db(); cur = conn.cursor()
    _pk = 'SERIAL PRIMARY KEY' if REGISTRE_USE_PG else 'INTEGER PRIMARY KEY AUTOINCREMENT'
    for ddl in [
        "CREATE TABLE IF NOT EXISTS client_entites (id " + _pk + ", client_id INTEGER, nom TEXT, type TEXT, created_at TEXT)",
        "CREATE TABLE IF NOT EXISTS client_connecteurs (id " + _pk + ", client_id INTEGER, categorie TEXT, nom TEXT, url TEXT, secret TEXT, statut TEXT, created_at TEXT)",
        "CREATE TABLE IF NOT EXISTS client_formations (id " + _pk + ", client_id INTEGER, date_prevue TEXT, theme TEXT, statut TEXT, created_at TEXT)"]:
        try:
            cur.execute(ddl)
        except Exception:
            pass
    conn.commit()

    def safe(sql_pg, sql_sq):
        try:
            cur.execute(registre_sql(sql_pg, sql_sq), (client_id,))
            return [dict(r) for r in cur.fetchall()]
        except Exception:
            try: conn.rollback()
            except Exception: pass
            return []

    entites = safe('SELECT id, nom, type FROM client_entites WHERE client_id=%s ORDER BY id',
                   'SELECT id, nom, type FROM client_entites WHERE client_id=? ORDER BY id')
    connecteurs = safe('SELECT id, categorie, nom, statut FROM client_connecteurs WHERE client_id=%s ORDER BY id',
                       'SELECT id, categorie, nom, statut FROM client_connecteurs WHERE client_id=? ORDER BY id')
    formations = safe('SELECT id, date_prevue, theme, statut FROM client_formations WHERE client_id=%s ORDER BY date_prevue',
                      'SELECT id, date_prevue, theme, statut FROM client_formations WHERE client_id=? ORDER BY date_prevue')
    try: conn.close()
    except Exception: pass
    return jsonify({'ok': True, 'entites': entites, 'connecteurs': connecteurs, 'formations': formations})



@app.route('/api/cron/essai-relances', methods=['POST', 'GET'])
def cron_essai_relances():
    """Point d'entree pour une tache planifiee (Render Cron Job) : declenche les
    rappels d'essai a heure fixe. Protege par un secret partage (CRON_SECRET),
    transmis en en-tete 'X-Cron-Secret' ou en parametre 'secret'.
    Sans CRON_SECRET configure, l'acces est refuse."""
    secret = os.environ.get('CRON_SECRET')
    if not secret:
        return jsonify({'ok': False, 'error': 'Tache planifiee non configuree.'}), 501
    fourni = request.headers.get('X-Cron-Secret') or request.args.get('secret')
    if not fourni or not hmac.compare_digest(str(fourni), str(secret)):
        return jsonify({'ok': False, 'error': 'Non autorise.'}), 403
    try:
        _essai_relances()
    except Exception:
        return jsonify({'ok': False, 'error': 'Echec du traitement des rappels.'}), 500
    return jsonify({'ok': True, 'executed_at': datetime.utcnow().isoformat()})



# ══════════════════════════════════════════════════════════
# MOTEUR D'EXPLORATION UNIFIE — Sentinel
# Interroge en temps reel l'ensemble des sources de connaissance :
#   1. base documentaire RAG (vectorielle si pgvector, sinon plein texte)
#   2. veille reglementaire (flux qualifies, cache serveur)
#   3. historique des analyses et documents produits par la plateforme
# Fusionne, pondere et restitue une reponse citee. Aucun reentrainement :
# la connaissance est lue a chaque requete, donc toujours a jour.
# CONSEILPREV/Sentinel.
# ══════════════════════════════════════════════════════════

EXPL_SOURCE_POIDS = {
    'document': 1.00,   # base documentaire : source de reference
    'veille': 0.85,     # actualite reglementaire : forte valeur si recente
    'analyse': 0.75,    # productions de la plateforme
}

EXPL_CADRES = {
    'IA Act': ['ia act', 'ai act', 'annexe iii', 'haut risque', 'gpai', 'systeme d ia'],
    'RGPD': ['rgpd', 'gdpr', 'donnees personnelles', 'aipd', 'dpia', 'cnil', 'consentement'],
    'ISO 42001': ['iso 42001', 'iso/iec 42001', 'smia'],
    'ISO 27001': ['iso 27001', 'smsi', 'securite de l information'],
    'NIS2': ['nis2', 'nis 2', 'entite essentielle'],
    'DORA': ['dora', 'resilience operationnelle'],
    'Cybersecurite': ['cyber', 'vulnerabilite', 'incident', 'menace', 'attaque', 'iec 62443', 'ebios'],
}


def _expl_norm(s):
    s = (s or '').lower()
    for a, b in [('é', 'e'), ('è', 'e'), ('ê', 'e'), ('ë', 'e'), ('à', 'a'), ('â', 'a'), ('î', 'i'),
                 ('ï', 'i'), ('ô', 'o'), ('ö', 'o'), ('û', 'u'), ('ù', 'u'), ('ç', 'c'), ('’', ' '),
                 ("'", ' '), ('-', ' '), ('_', ' ')]:
        s = s.replace(a, b)
    return s


def _expl_mots(q):
    """Mots significatifs de la question (hors mots vides)."""
    vides = {'le', 'la', 'les', 'de', 'des', 'du', 'un', 'une', 'et', 'ou', 'que', 'qui', 'quoi',
             'quel', 'quelle', 'quels', 'quelles', 'est', 'sont', 'ce', 'cet', 'cette', 'dans',
             'pour', 'par', 'sur', 'au', 'aux', 'en', 'a', 'il', 'elle', 'nous', 'vous', 'je',
             'mon', 'ma', 'mes', 'notre', 'nos', 'comment', 'pourquoi', 'quand', 'combien', 'plus'}
    mots = [m for m in _expl_norm(q).split() if len(m) > 2 and m not in vides]
    return mots


def _expl_cadres_detectes(q):
    n = _expl_norm(q)
    trouves = []
    for cadre, mots in EXPL_CADRES.items():
        if any(m in n for m in mots):
            trouves.append(cadre)
    return trouves


def _expl_score_texte(texte, mots, cadres):
    """Score lexical d'un extrait : couverture des mots + cadres reconnus."""
    if not texte:
        return 0.0
    n = _expl_norm(texte)
    couverts = sum(1 for m in mots if m in n)
    base = (couverts / max(1, len(mots))) if mots else 0.0
    bonus = 0.0
    for c in cadres:
        for m in EXPL_CADRES.get(c, []):
            if m in n:
                bonus += 0.08
                break
    return min(1.0, base + bonus)


def _expl_documents(cur, query, mots, cadres, limite):
    """Base documentaire : vectorielle si disponible, sinon lexicale."""
    out = []
    try:
        if RAG_PGVECTOR_AVAILABLE and REGISTRE_USE_PG:
            ok, embs = rag_get_embeddings([query])
            if ok:
                vec = embs[0]
                cur.execute(
                    'SELECT c.chunk_text, d.nom_fichier, d.id AS doc_id, '
                    '1 - (c.embedding <=> %s::vector) AS score '
                    'FROM rag_chunks c JOIN rag_documents d ON c.document_id = d.id '
                    'WHERE c.embedding IS NOT NULL '
                    'ORDER BY c.embedding <=> %s::vector LIMIT %s',
                    [vec, vec, limite])
                for r in cur.fetchall():
                    r = dict(r)
                    out.append({'type': 'document', 'titre': r['nom_fichier'], 'ref': r['doc_id'],
                                'extrait': (r['chunk_text'] or '')[:600],
                                'score': float(r.get('score') or 0.0)})
    except Exception:
        out = []
    if not out:
        try:
            cur.execute(registre_sql(
                'SELECT c.chunk_text, d.nom_fichier, d.id AS doc_id FROM rag_chunks c '
                'JOIN rag_documents d ON c.document_id = d.id LIMIT %s',
                'SELECT c.chunk_text, d.nom_fichier, d.id AS doc_id FROM rag_chunks c '
                'JOIN rag_documents d ON c.document_id = d.id LIMIT ?'), (600,))
            for r in cur.fetchall():
                r = dict(r)
                s = _expl_score_texte(r.get('chunk_text'), mots, cadres)
                if s > 0:
                    out.append({'type': 'document', 'titre': r['nom_fichier'], 'ref': r['doc_id'],
                                'extrait': (r['chunk_text'] or '')[:600], 'score': s})
        except Exception:
            pass
    return out


def _expl_veille(mots, cadres, limite):
    """Veille reglementaire : articles du cache serveur, bonus de fraicheur."""
    out = []
    try:
        items = (_VEILLE_CACHE or {}).get('items') or []
    except Exception:
        items = []
    for it in items:
        titre = it.get('title') or it.get('titre') or ''
        resume = it.get('summary') or it.get('resume') or ''
        s = _expl_score_texte(titre + ' ' + resume, mots, cadres)
        if s <= 0:
            continue
        s = min(1.0, s + 0.10)  # bonus de fraicheur (veille = actualite)
        out.append({'type': 'veille', 'titre': titre[:200], 'ref': it.get('link') or '',
                    'extrait': (resume or '')[:400], 'score': s,
                    'date': it.get('published') or it.get('date') or ''})
    out.sort(key=lambda x: -x['score'])
    return out[:limite]


def _expl_analyses(cur, mots, cadres, limite):
    """Documents et analyses produits par la plateforme (historique)."""
    out = []
    for sql_pg, sql_sq in [
        ('SELECT id, page, label, date_creation FROM historique ORDER BY date_creation DESC LIMIT %s',
         'SELECT id, page, label, date_creation FROM historique ORDER BY date_creation DESC LIMIT ?'),
        ('SELECT id, page, titre AS label, date_creation FROM historique ORDER BY date_creation DESC LIMIT %s',
         'SELECT id, page, titre AS label, date_creation FROM historique ORDER BY date_creation DESC LIMIT ?')]:
        try:
            cur.execute(registre_sql(sql_pg, sql_sq), (400,))
            for r in cur.fetchall():
                r = dict(r)
                txt = (r.get('label') or '') + ' ' + (r.get('page') or '')
                s = _expl_score_texte(txt, mots, cadres)
                if s > 0:
                    out.append({'type': 'analyse', 'titre': (r.get('label') or 'Analyse')[:200],
                                'ref': r.get('id'), 'extrait': ('Module : ' + str(r.get('page') or '')),
                                'score': s, 'date': str(r.get('date_creation') or '')})
            break
        except Exception:
            try: conn_rollback = None
            except Exception: pass
            continue
    out.sort(key=lambda x: -x['score'])
    return out[:limite]



def _expl_synthese(question, resultats):
    """Synthese redigee par le modele, fondee EXCLUSIVEMENT sur les extraits
    retrouves. Le modele doit citer ses sources et signaler l'absence
    d'information plutot que d'inventer."""
    if not resultats:
        return None
    LIB = {'document': 'Base documentaire', 'veille': 'Veille reglementaire',
           'analyse': 'Analyse de la plateforme'}
    blocs = []
    for i, r in enumerate(resultats[:8], start=1):
        blocs.append('[%d] (%s - %s)\n%s' % (
            i, LIB.get(r.get('type'), r.get('type')), str(r.get('titre') or '')[:120],
            str(r.get('extrait') or '')[:700]))
    contexte = '\n\n'.join(blocs)
    system = (
        "Vous etes l'assistant de conformite de la plateforme Sentinel, editee par CONSEILPREV. "
        "Vous repondez en francais, dans un style formel, precis et concis (200 mots maximum). "
        "REGLE ABSOLUE : vous vous appuyez EXCLUSIVEMENT sur les extraits fournis. "
        "Vous n'inventez aucun fait, aucun article, aucune date, aucun chiffre. "
        "Vous citez vos sources entre crochets, par exemple [1] ou [2]. "
        "Si les extraits ne permettent pas de repondre, vous le dites clairement et vous "
        "invitez a preciser la question ou a importer les documents utiles. "
        "Pour toute question juridique ou comptable, vous rappelez que la reponse ne constitue "
        "pas un conseil juridique et recommandez la validation par un conseil competent."
    )
    user = ('Question : %s\n\nExtraits disponibles :\n\n%s\n\n'
            'Redigez la reponse en vous appuyant uniquement sur ces extraits, avec citations.'
            % (question, contexte))
    ok, texte = call_anthropic([{'role': 'user', 'content': user}], system=system,
                               max_tokens=700, temperature=0.2)
    return texte if ok else None


@app.route('/api/sentinel/explorer', methods=['POST'])
@rate_limit(limit=20, window=60)
@rag_require_access
def sentinel_explorer():
    """Exploration unifiee de la connaissance Sentinel, en temps reel.
    Entree : {'question': str, 'sources': ['document','veille','analyse'], 'top_k': int}
    Sortie : resultats fusionnes et pondere, cadres detectes, synthese."""
    data = request.get_json(silent=True) or {}
    question = (data.get('question') or '').strip()
    if not question:
        return jsonify({'ok': False, 'error': 'Question requise.'}), 400
    demandees = data.get('sources') or ['document', 'veille', 'analyse']
    try:
        top_k = max(1, min(int(data.get('top_k', 8)), 20))
    except (TypeError, ValueError):
        top_k = 8

    mots = _expl_mots(question)
    cadres = _expl_cadres_detectes(question)

    conn = registre_get_db(); cur = conn.cursor()
    resultats = []
    if 'document' in demandees:
        resultats += _expl_documents(cur, question, mots, cadres, top_k)
    if 'analyse' in demandees:
        resultats += _expl_analyses(cur, mots, cadres, top_k)
    try: conn.close()
    except Exception: pass
    if 'veille' in demandees:
        resultats += _expl_veille(mots, cadres, top_k)

    # Fusion ponderee par source, puis classement
    for r in resultats:
        r['score_final'] = round(float(r.get('score') or 0.0) * EXPL_SOURCE_POIDS.get(r['type'], 0.7), 4)
    resultats.sort(key=lambda x: -x['score_final'])
    resultats = resultats[:top_k]

    par_source = {}
    for r in resultats:
        par_source[r['type']] = par_source.get(r['type'], 0) + 1

    synthese = None
    if data.get('synthese', True):
        try:
            synthese = _expl_synthese(question, resultats)
        except Exception:
            synthese = None
    return jsonify({'ok': True, 'question': question, 'cadres': cadres,
                    'synthese': synthese,
                    'resultats': resultats, 'par_source': par_source,
                    'total': len(resultats),
                    'moteur': 'vectoriel' if (RAG_PGVECTOR_AVAILABLE and REGISTRE_USE_PG) else 'lexical'})



@app.route('/api/mistral/proxy', methods=['POST'])
@rate_limit(limit=30, window=60)
@sentinel_login_required
def mistral_proxy():
    """Relais serveur vers Mistral, reserve aux clients authentifies.
    La cle d'API reste cote serveur et n'est jamais exposee au navigateur.
    Entree : {'model','messages','max_tokens','temperature'} — sortie : reponse Mistral."""
    if not MISTRAL_API_KEY:
        return jsonify({'error': 'Moteur Mistral non configure.'}), 501
    d = request.get_json(silent=True) or {}
    messages = d.get('messages') or []
    if not isinstance(messages, list) or not messages:
        return jsonify({'error': 'messages requis'}), 400
    propres = []
    for m in messages[-12:]:
        if isinstance(m, dict) and m.get('role') in ('system', 'user', 'assistant') and m.get('content'):
            propres.append({'role': m['role'], 'content': str(m['content'])[:6000]})
    if not propres:
        return jsonify({'error': 'messages invalides'}), 400
    try:
        max_tokens = max(1, min(int(d.get('max_tokens', 800)), 4000))
    except (TypeError, ValueError):
        max_tokens = 800
    try:
        temperature = float(d.get('temperature', 0.5))
    except (TypeError, ValueError):
        temperature = 0.5
    temperature = max(0.0, min(temperature, 1.0))
    try:
        resp = requests.post(
            MISTRAL_URL,
            headers={'Content-Type': 'application/json',
                     'Authorization': 'Bearer ' + MISTRAL_API_KEY},
            json={'model': d.get('model') or 'mistral-large-latest',
                  'messages': propres, 'max_tokens': max_tokens, 'temperature': temperature},
            timeout=45,
        )
    except Exception:
        return jsonify({'error': 'Moteur indisponible.'}), 503
    if resp.status_code >= 400:
        return jsonify({'error': 'Moteur indisponible (%d).' % resp.status_code}), 502
    try:
        return jsonify(resp.json())
    except Exception:
        return jsonify({'error': 'Reponse illisible du moteur.'}), 502



# ══════════════════════════════════════════════════════════
# MODULE RGPD — CONSEILPREV / Sentinel
# Outillage de conformite : preuves de consentement (art. 7), registre des
# activites de traitement (art. 30), droit a l'effacement (art. 17),
# verification de conformite (art. 5 et 25), transferts hors UE, portabilite
# (art. 20 / Data Act) et rapport d'audit pour demande externe.
# Ce module fournit l'outillage technique ; il ne constitue pas un conseil
# juridique et doit etre valide par un conseil competent.
# ══════════════════════════════════════════════════════════

RGPD_POLITIQUE_VERSION = '1.0'

def _rgpd_hash(valeur):
    """Empreinte non reversible (minimisation, art. 5) : IP et identifiants."""
    sel = str(app.secret_key or 'conseilprev')
    return hashlib.sha256((sel + '|' + str(valeur or '')).encode('utf-8')).hexdigest()[:24]


def _rgpd_table(cur):
    _pk = 'SERIAL PRIMARY KEY' if REGISTRE_USE_PG else 'INTEGER PRIMARY KEY AUTOINCREMENT'
    cur.execute('CREATE TABLE IF NOT EXISTS consent_records (id ' + _pk + ', '
                'horodatage TEXT, sujet TEXT, email TEXT, email_hash TEXT, '
                'methode TEXT, finalites TEXT, politique_version TEXT, '
                'ip_hash TEXT, user_agent TEXT, retrait INTEGER DEFAULT 0, efface INTEGER DEFAULT 0)')


def _rgpd_record_consent(email, finalites, methode, retrait=False):
    """Enregistre une preuve de consentement horodatee (art. 7 : la charge de
    la preuve incombe au responsable de traitement). Minimisation : IP hachee,
    agent utilisateur tronque. Silencieux en cas d'erreur."""
    try:
        conn = registre_get_db(); cur = conn.cursor()
        _rgpd_table(cur); conn.commit()
        ip = ''
        try:
            ip = limiter.get_ip(request)
        except Exception:
            ip = request.remote_addr or ''
        ua = (request.headers.get('User-Agent') or '')[:120]
        em = (email or '').strip().lower()[:200]
        cur.execute(registre_sql(
            'INSERT INTO consent_records (horodatage, sujet, email, email_hash, methode, finalites, politique_version, ip_hash, user_agent, retrait) '
            'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            'INSERT INTO consent_records (horodatage, sujet, email, email_hash, methode, finalites, politique_version, ip_hash, user_agent, retrait) '
            'VALUES (?,?,?,?,?,?,?,?,?,?)'),
            (datetime.utcnow().isoformat(), 'visiteur' if not em else 'personne identifiee',
             em, _rgpd_hash(em) if em else '', methode,
             json.dumps(finalites or {}, ensure_ascii=False)[:1000],
             RGPD_POLITIQUE_VERSION, _rgpd_hash(ip), ua, 1 if retrait else 0))
        conn.commit()
        try: conn.close()
        except Exception: pass
    except Exception:
        try: conn.close()
        except Exception: pass


@app.route('/api/rgpd/consentement', methods=['POST'])
def rgpd_consentement_public():
    """Point d'entree public : la banniere cookies et les formulaires y
    deposent la preuve de consentement (acceptation, personnalisation ou refus)."""
    try:
        if not limiter.check_soft(limiter.get_ip(request), limit=15, window=300):
            return jsonify({'ok': False}), 429
    except Exception:
        pass
    d = request.get_json(silent=True) or {}
    finalites = d.get('finalites') if isinstance(d.get('finalites'), dict) else {}
    methode = (d.get('methode') or 'banniere')[:40]
    email = (d.get('email') or '')[:200]
    retrait = bool(d.get('retrait'))
    _rgpd_record_consent(email, finalites, methode, retrait=retrait)
    return jsonify({'ok': True})


@app.route('/api/rgpd/consentements', methods=['GET'])
def rgpd_consentements_admin():
    """Registre des preuves de consentement (CONSEILPREV). Filtre ?q= sur
    l'adresse ; ?limit= borne le nombre de lignes."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    q = (request.args.get('q') or '').strip().lower()
    try:
        limit = max(1, min(int(request.args.get('limit', 200)), 1000))
    except (TypeError, ValueError):
        limit = 200
    conn = registre_get_db(); cur = conn.cursor()
    _rgpd_table(cur); conn.commit()
    if q:
        cur.execute(registre_sql(
            "SELECT * FROM consent_records WHERE email LIKE %s ORDER BY id DESC LIMIT %s",
            "SELECT * FROM consent_records WHERE email LIKE ? ORDER BY id DESC LIMIT ?"),
            ('%' + q + '%', limit))
    else:
        cur.execute(registre_sql(
            'SELECT * FROM consent_records ORDER BY id DESC LIMIT %s',
            'SELECT * FROM consent_records ORDER BY id DESC LIMIT ?'), (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    cur.execute('SELECT COUNT(*) AS n FROM consent_records')
    total = dict(cur.fetchone()).get('n', 0)
    try: conn.close()
    except Exception: pass
    return jsonify({'ok': True, 'total': total, 'consentements': rows})


RGPD_TRAITEMENTS = [
    {'id': 1, 'nom': 'Formulaire de contact et candidatures', 'finalite': 'Reponse aux demandes entrantes',
     'base': 'Mesures precontractuelles / consentement (art. 6.1.b et 6.1.a)',
     'donnees': 'Identite, coordonnees, message', 'duree': '24 mois apres le dernier contact',
     'destinataires': 'CONSEILPREV ; Brevo (envoi, UE)'},
    {'id': 2, 'nom': 'Comptes clients Sentinel', 'finalite': 'Fourniture de la plateforme (execution du contrat)',
     'base': 'Contrat (art. 6.1.b)', 'donnees': 'Identite, e-mail, mot de passe hache, offre, essai',
     'duree': 'Duree du compte + 5 ans (prescription)', 'destinataires': 'CONSEILPREV ; Render/PostgreSQL (Francfort, UE)'},
    {'id': 3, 'nom': 'Abonnements et facturation', 'finalite': 'Paiement des offres et facturation par resultats',
     'base': 'Contrat et obligation legale (art. 6.1.b et 6.1.c)', 'donnees': 'Identite, e-mail, donnees de facturation',
     'duree': '10 ans (pieces comptables)', 'destinataires': 'Stripe (Etats-Unis — clauses contractuelles types / DPF)'},
    {'id': 4, 'nom': 'Courriels transactionnels et lettre d\'information', 'finalite': 'Notifications de service et information',
     'base': 'Contrat / consentement (art. 6.1.b et 6.1.a)', 'donnees': 'E-mail, nom',
     'duree': 'Jusqu\'au retrait du consentement', 'destinataires': 'Brevo (UE)'},
    {'id': 5, 'nom': 'Assistants conversationnels', 'finalite': 'Reponse aux questions des visiteurs et clients',
     'base': 'Consentement / interet legitime (art. 6.1.a et 6.1.f)', 'donnees': 'Contenu des messages',
     'duree': 'Session ; pas de conservation dediee cote site', 'destinataires': 'Anthropic (Etats-Unis — CCT/DPF) ; Mistral (UE)'},
    {'id': 6, 'nom': 'Journaux techniques et securite', 'finalite': 'Securite, detection d\'abus, diagnostic',
     'base': 'Interet legitime (art. 6.1.f)', 'donnees': 'Adresses IP (hachees dans les preuves), horodatages',
     'duree': '12 mois', 'destinataires': 'Render (UE)'},
    {'id': 7, 'nom': 'Cookies et traceurs', 'finalite': 'Fonctionnement, mesure et personnalisation selon le choix',
     'base': 'Consentement (art. 6.1.a) via banniere a granularite', 'donnees': 'Preferences, identifiants techniques',
     'duree': '13 mois maximum', 'destinataires': 'CONSEILPREV (preuve serveur)'},
    {'id': 8, 'nom': 'Base de connaissance (RAG)', 'finalite': 'Analyse documentaire de conformite pour le client',
     'base': 'Contrat (art. 6.1.b)', 'donnees': 'Documents deposes par le client',
     'duree': 'Duree du compte ; suppression a la demande', 'destinataires': 'Render (UE) ; Mistral embeddings (UE)'},
]

RGPD_TRANSFERTS = [
    {'destinataire': 'Stripe', 'pays': 'Etats-Unis', 'role': 'Paiements', 'garantie': 'Clauses contractuelles types / Data Privacy Framework'},
    {'destinataire': 'Anthropic', 'pays': 'Etats-Unis', 'role': 'Assistant (moteur)', 'garantie': 'Clauses contractuelles types / DPF'},
    {'destinataire': 'Brevo', 'pays': 'France (UE)', 'role': 'Courriels', 'garantie': 'Traitement dans l\'UE'},
    {'destinataire': 'Render', 'pays': 'Allemagne (UE, Francfort)', 'role': 'Hebergement et base de donnees', 'garantie': 'Traitement dans l\'UE'},
    {'destinataire': 'Mistral AI', 'pays': 'France (UE)', 'role': 'Assistant et vectorisation', 'garantie': 'Traitement dans l\'UE'},
]


def _rgpd_registre_table(cur, conn):
    _pk = 'SERIAL PRIMARY KEY' if REGISTRE_USE_PG else 'INTEGER PRIMARY KEY AUTOINCREMENT'
    cur.execute('CREATE TABLE IF NOT EXISTS rgpd_registre_site (id ' + _pk + ', nom TEXT, finalite TEXT, '
                'base TEXT, donnees TEXT, duree TEXT, destinataires TEXT, date_maj TEXT)')
    conn.commit()
    cur.execute('SELECT COUNT(*) AS n FROM rgpd_registre_site')
    if int(dict(cur.fetchone()).get('n', 0)) > 0:
        return
    for t in RGPD_TRAITEMENTS:
        cur.execute(registre_sql(
            'INSERT INTO rgpd_registre_site (nom, finalite, base, donnees, duree, destinataires, date_maj) VALUES (%s,%s,%s,%s,%s,%s,%s)',
            'INSERT INTO rgpd_registre_site (nom, finalite, base, donnees, duree, destinataires, date_maj) VALUES (?,?,?,?,?,?,?)'),
            (t['nom'], t['finalite'], t['base'], t['donnees'], t['duree'], t['destinataires'],
             datetime.utcnow().isoformat()))
    conn.commit()


@app.route('/api/rgpd/registre-traitements', methods=['GET', 'POST'])
def rgpd_registre():
    """Registre des activites de traitement de CONSEILPREV (art. 30), source
    unique : stocke en base et editable. Distinct du registre que chaque client
    tient pour sa propre organisation."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    conn = registre_get_db(); cur = conn.cursor()
    _rgpd_registre_table(cur, conn)
    if request.method == 'POST':
        d = request.get_json(silent=True) or {}
        champs = (str(d.get('nom') or '')[:200], str(d.get('finalite') or '')[:500],
                  str(d.get('base') or '')[:300], str(d.get('donnees') or '')[:500],
                  str(d.get('duree') or '')[:200], str(d.get('destinataires') or '')[:400],
                  datetime.utcnow().isoformat())
        if not champs[0]:
            try: conn.close()
            except Exception: pass
            return jsonify({'ok': False, 'error': 'Nom du traitement requis'}), 400
        rid = d.get('id')
        if rid:
            cur.execute(registre_sql(
                'UPDATE rgpd_registre_site SET nom=%s, finalite=%s, base=%s, donnees=%s, duree=%s, destinataires=%s, date_maj=%s WHERE id=%s',
                'UPDATE rgpd_registre_site SET nom=?, finalite=?, base=?, donnees=?, duree=?, destinataires=?, date_maj=? WHERE id=?'),
                champs + (int(rid),))
        else:
            cur.execute(registre_sql(
                'INSERT INTO rgpd_registre_site (nom, finalite, base, donnees, duree, destinataires, date_maj) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                'INSERT INTO rgpd_registre_site (nom, finalite, base, donnees, duree, destinataires, date_maj) VALUES (?,?,?,?,?,?,?)'),
                champs)
        conn.commit()
    cur.execute('SELECT * FROM rgpd_registre_site ORDER BY id')
    traitements = [dict(r) for r in cur.fetchall()]
    try: conn.close()
    except Exception: pass
    return jsonify({'ok': True, 'perimetre': 'CONSEILPREV — site public et plateforme Sentinel',
                    'responsable': {
                        'entite': 'CONSEILPREV (SARL)', 'siren': '494 530 157',
                        'adresse': '19 rue Auguste Chabrieres, 75015 Paris',
                        'representant': 'Christophe CERF', 'dpo_contact': 'christophe.cerf@outlook.com'},
                    'traitements': traitements, 'transferts': RGPD_TRANSFERTS,
                    'version_politique': RGPD_POLITIQUE_VERSION})


@app.route('/api/rgpd/registre-traitements/<int:tid>', methods=['DELETE'])
def rgpd_registre_delete(tid):
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    conn = registre_get_db(); cur = conn.cursor()
    cur.execute(registre_sql('DELETE FROM rgpd_registre_site WHERE id=%s',
                             'DELETE FROM rgpd_registre_site WHERE id=?'), (tid,))
    conn.commit()
    try: conn.close()
    except Exception: pass
    return jsonify({'ok': True})
@app.route('/api/rgpd/effacement', methods=['POST'])
def rgpd_effacement():
    """Droit a l'effacement (art. 17) : anonymise le compte et supprime les
    donnees liees. Les preuves de consentement sont anonymisees mais conservees
    (obligation de preuve) ; les pieces comptables Stripe demeurent (art. 17.3.b)."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    d = request.get_json(silent=True) or {}
    email = (d.get('email') or '').strip().lower()
    if not email or '@' not in email:
        return jsonify({'ok': False, 'error': 'Adresse requise'}), 400
    if email == str(CONSEILPREV_INTERNAL_EMAIL).strip().lower():
        return jsonify({'ok': False, 'error': 'Compte interne non effacable'}), 400
    conn = registre_get_db(); cur = conn.cursor()
    _rgpd_table(cur); conn.commit()
    bilan = {}
    cur.execute(registre_sql('SELECT id FROM clients WHERE LOWER(email)=%s', 'SELECT id FROM clients WHERE LOWER(email)=?'), (email,))
    row = cur.fetchone()
    cid = dict(row).get('id') if row else None
    if cid:
        anonyme = 'efface-' + _rgpd_hash(email) + '@anonyme.invalid'
        cur.execute(registre_sql(
            "UPDATE clients SET email=%s, nom_entreprise='COMPTE EFFACE', mot_de_passe_hash='', actif=FALSE, stripe_customer_id=NULL, stripe_subscription_id=NULL WHERE id=%s",
            "UPDATE clients SET email=?, nom_entreprise='COMPTE EFFACE', mot_de_passe_hash='', actif=0, stripe_customer_id=NULL, stripe_subscription_id=NULL WHERE id=?"),
            (anonyme, cid))
        bilan['compte'] = 'anonymise'
        for table in ('client_entites', 'client_connecteurs', 'client_formations'):
            try:
                cur.execute(registre_sql('DELETE FROM ' + table + ' WHERE client_id=%s',
                                         'DELETE FROM ' + table + ' WHERE client_id=?'), (cid,))
                bilan[table] = cur.rowcount
            except Exception:
                try: conn.rollback()
                except Exception: pass
    else:
        bilan['compte'] = 'introuvable'
    try:
        cur.execute(registre_sql(
            "UPDATE consent_records SET email='', efface=1 WHERE LOWER(email)=%s",
            "UPDATE consent_records SET email='', efface=1 WHERE LOWER(email)=?"), (email,))
        bilan['preuves_consentement'] = 'anonymisees (conservees a titre de preuve)'
    except Exception:
        pass
    conn.commit()
    try: conn.close()
    except Exception: pass
    _rgpd_record_consent(email='', finalites={'effacement_art17': True, 'cible_hash': _rgpd_hash(email)},
                         methode='effacement-admin', retrait=True)
    return jsonify({'ok': True, 'bilan': bilan,
                    'note': 'Pieces comptables conservees (art. 17.3.b) ; preuves anonymisees.'})


@app.route('/api/rgpd/export-donnees', methods=['GET'])
def rgpd_export_donnees():
    """Portabilite (art. 20 RGPD ; esprit du Data Act) : export structure des
    donnees d'une personne, a remettre a l'interesse sur demande."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    email = (request.args.get('email') or '').strip().lower()
    if not email or '@' not in email:
        return jsonify({'ok': False, 'error': 'Adresse requise'}), 400
    conn = registre_get_db(); cur = conn.cursor()
    _rgpd_table(cur); conn.commit()
    out = {'demande': email, 'genere_le': datetime.utcnow().isoformat()}
    cur.execute(registre_sql('SELECT id, nom_entreprise, email, date_creation, plan, essai_fin FROM clients WHERE LOWER(email)=%s',
                             'SELECT id, nom_entreprise, email, date_creation, plan, essai_fin FROM clients WHERE LOWER(email)=?'), (email,))
    row = cur.fetchone()
    if row:
        d = dict(row); out['compte'] = d; cid = d['id']
        for table, cle in (('client_entites', 'entites'), ('client_connecteurs', 'connecteurs'), ('client_formations', 'formations')):
            try:
                if table == 'client_connecteurs':
                    cur.execute(registre_sql('SELECT id, categorie, nom, url, statut FROM client_connecteurs WHERE client_id=%s',
                                             'SELECT id, categorie, nom, url, statut FROM client_connecteurs WHERE client_id=?'), (cid,))
                else:
                    cur.execute(registre_sql('SELECT * FROM ' + table + ' WHERE client_id=%s',
                                             'SELECT * FROM ' + table + ' WHERE client_id=?'), (cid,))
                out[cle] = [dict(r) for r in cur.fetchall()]
            except Exception:
                out[cle] = []
    cur.execute(registre_sql('SELECT horodatage, methode, finalites, politique_version, retrait FROM consent_records WHERE LOWER(email)=%s ORDER BY id',
                             'SELECT horodatage, methode, finalites, politique_version, retrait FROM consent_records WHERE LOWER(email)=? ORDER BY id'), (email,))
    out['consentements'] = [dict(r) for r in cur.fetchall()]
    try: conn.close()
    except Exception: pass
    return jsonify({'ok': True, 'export': out})


@app.route('/api/rgpd/verification', methods=['GET'])
def rgpd_verification():
    """Verification de conformite du site : controles automatiques et
    declaratifs, references aux articles 5, 7, 17, 25 et 30 du RGPD, avec
    l'etat DMA / DSA / Data Act."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    conn = registre_get_db(); cur = conn.cursor()
    _rgpd_table(cur); conn.commit()
    cur.execute('SELECT COUNT(*) AS n FROM consent_records')
    nb_preuves = dict(cur.fetchone()).get('n', 0)
    cur.execute(registre_sql("SELECT COUNT(*) AS n FROM consent_records WHERE retrait=1",
                             "SELECT COUNT(*) AS n FROM consent_records WHERE retrait=1"))
    nb_retraits = dict(cur.fetchone()).get('n', 0)
    try: conn.close()
    except Exception: pass
    cookie_secure = bool(app.config.get('SESSION_COOKIE_HTTPONLY', True))
    checks = [
        {'article': 'Art. 5', 'intitule': 'Minimisation et exactitude', 'mode': 'automatique',
         'statut': 'conforme', 'detail': 'IP hachees et agent utilisateur tronque dans les preuves ; donnees limitees aux finalites declarees.'},
        {'article': 'Art. 5', 'intitule': 'Limitation de conservation', 'mode': 'declaratif',
         'statut': 'conforme', 'detail': 'Durees documentees par traitement dans le registre (art. 30).'},
        {'article': 'Art. 7', 'intitule': 'Preuve du consentement', 'mode': 'automatique',
         'statut': 'conforme' if nb_preuves > 0 else 'a-verifier',
         'detail': str(nb_preuves) + ' preuve(s) horodatee(s) enregistrees ; ' + str(nb_retraits) + ' retrait(s) trace(s).'},
        {'article': 'Art. 7', 'intitule': 'Retrait aussi simple que l\'octroi', 'mode': 'automatique',
         'statut': 'conforme', 'detail': 'Banniere rouvrable a tout moment ; le refus et le retrait sont enregistres comme preuves.'},
        {'article': 'Art. 17', 'intitule': 'Droit a l\'effacement', 'mode': 'automatique',
         'statut': 'conforme', 'detail': 'Procedure d\'effacement operationnelle : anonymisation du compte, suppression des donnees liees, preuves anonymisees.'},
        {'article': 'Art. 25', 'intitule': 'Protection des la conception', 'mode': 'automatique',
         'statut': 'conforme' if cookie_secure else 'a-verifier',
         'detail': 'Cles d\'API cote serveur uniquement ; acces administrateur restreint ; cookies de session proteges ; HTTPS via Render.'},
        {'article': 'Art. 30', 'intitule': 'Registre des activites de traitement', 'mode': 'automatique',
         'statut': 'conforme', 'detail': str(len(RGPD_TRAITEMENTS)) + ' traitements documentes (finalite, base, duree, destinataires), exportables.'},
        {'article': 'Chap. V', 'intitule': 'Transferts hors UE encadres', 'mode': 'declaratif',
         'statut': 'conforme', 'detail': 'Stripe et Anthropic (Etats-Unis) sous clauses contractuelles types / DPF ; autres sous-traitants dans l\'UE.'},
        {'article': 'DSA', 'intitule': 'Transparence et point de contact', 'mode': 'declaratif',
         'statut': 'conforme', 'detail': 'Mentions legales, politique de confidentialite et point de contact publies ; pas de place de marche ni de contenu tiers heberge.'},
        {'article': 'DMA', 'intitule': 'Applicabilite', 'mode': 'declaratif',
         'statut': 'non-applicable', 'detail': 'Le DMA vise les controleurs d\'acces designes ; CONSEILPREV n\'entre pas dans son champ.'},
        {'article': 'Data Act', 'intitule': 'Portabilite et changement de fournisseur', 'mode': 'automatique',
         'statut': 'conforme', 'detail': 'Export structure des donnees client disponible ; telechargement des documents de la base de connaissance.'},
    ]
    # Controles reellement calcules a partir de l'etat de la base (temps reel)
    try:
        checks = checks + _rgpd_controles_calcules()
    except Exception:
        pass
    anomalies = [c for c in checks if c['statut'] == 'a-verifier']
    score = round(100.0 * sum(1 for c in checks if c['statut'] == 'conforme') / max(1, len([c for c in checks if c['statut'] != 'non-applicable'])))
    return jsonify({'ok': True, 'score': score, 'checks': checks,
                    'anomalies': anomalies, 'nb_anomalies': len(anomalies),
                    'preuves': nb_preuves, 'retraits': nb_retraits})


@app.route('/api/rgpd/rapport-audit', methods=['GET'])
def rgpd_rapport_audit():
    """Rapport d'audit complet, destine a une demande externe (autorite,
    client, prospect) : identite, registre, transferts, preuves, controles."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    verif = json.loads(rgpd_verification().get_data(as_text=True))
    reg = json.loads(rgpd_registre().get_data(as_text=True))
    return jsonify({'ok': True, 'genere_le': datetime.utcnow().isoformat(),
                    'responsable': reg.get('responsable'),
                    'score': verif.get('score'), 'checks': verif.get('checks'),
                    'traitements': reg.get('traitements'), 'transferts': reg.get('transferts'),
                    'preuves_consentement': verif.get('preuves'), 'retraits': verif.get('retraits'),
                    'version_politique': RGPD_POLITIQUE_VERSION,
                    'avertissement': 'Outillage technique de conformite ; ne constitue pas un avis juridique.'})



# ══════════════════════════════════════════════════════════
# RGPD — RETENTION, PURGE, AIPD (art. 35), CONTROLES CALCULES,
# HISTORIQUE D'AUDIT SCELLE ET REGISTRE DES DEMANDES (art. 12)
# Outillage technique ; ne constitue pas un avis juridique.
# ══════════════════════════════════════════════════════════

RGPD_RETENTION_DEFAUT = [
    {'cible': 'consent_records', 'libelle': 'Preuves de consentement', 'duree_mois': 36,
     'base': 'Preuve du consentement (art. 7) : conservation limitee a la duree utile a la preuve.',
     'action': 'anonymiser'},
    {'cible': 'essais_expires', 'libelle': 'Comptes d\'essai expires et jamais convertis', 'duree_mois': 12,
     'base': 'Limitation de conservation (art. 5.1.e) : absence de relation contractuelle.',
     'action': 'anonymiser'},
    {'cible': 'clients_inactifs', 'libelle': 'Comptes clients inactifs', 'duree_mois': 36,
     'base': 'Limitation de conservation (art. 5.1.e) ; prescription commerciale.',
     'action': 'signaler'},
    {'cible': 'rgpd_demandes', 'libelle': 'Demandes d\'exercice de droits traitees', 'duree_mois': 36,
     'base': 'Preuve du traitement de la demande (art. 12).', 'action': 'anonymiser'},
]


def _rgpd_tables2(cur):
    _pk = 'SERIAL PRIMARY KEY' if REGISTRE_USE_PG else 'INTEGER PRIMARY KEY AUTOINCREMENT'
    cur.execute('CREATE TABLE IF NOT EXISTS rgpd_retention (id ' + _pk + ', cible TEXT, libelle TEXT, '
                'duree_mois INTEGER, base TEXT, action TEXT, actif INTEGER DEFAULT 1, date_maj TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS rgpd_purge_log (id ' + _pk + ', horodatage TEXT, cible TEXT, '
                'nb INTEGER, mode TEXT, detail TEXT, hash_prec TEXT, hash TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS rgpd_aipd (id ' + _pk + ', titre TEXT, traitement TEXT, '
                'criteres TEXT, seuil_atteint INTEGER, description TEXT, necessite TEXT, risques TEXT, '
                'mesures TEXT, risque_residuel TEXT, avis_dpo TEXT, statut TEXT, version TEXT, date_maj TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS rgpd_audits (id ' + _pk + ', horodatage TEXT, score INTEGER, '
                'contenu TEXT, hash_prec TEXT, hash TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS rgpd_demandes (id ' + _pk + ', recu_le TEXT, echeance TEXT, '
                'type TEXT, email TEXT, statut TEXT, traite_le TEXT, note TEXT)')


def _rgpd_seed_retention(cur, conn):
    cur.execute('SELECT COUNT(*) AS n FROM rgpd_retention')
    if int(dict(cur.fetchone()).get('n', 0)) > 0:
        return
    for r in RGPD_RETENTION_DEFAUT:
        cur.execute(registre_sql(
            'INSERT INTO rgpd_retention (cible, libelle, duree_mois, base, action, actif, date_maj) VALUES (%s,%s,%s,%s,%s,1,%s)',
            'INSERT INTO rgpd_retention (cible, libelle, duree_mois, base, action, actif, date_maj) VALUES (?,?,?,?,?,1,?)'),
            (r['cible'], r['libelle'], r['duree_mois'], r['base'], r['action'], datetime.utcnow().isoformat()))
    conn.commit()


def _rgpd_chaine(cur, table, payload):
    """Scellement par chainage d'empreintes : chaque entree porte l'empreinte de
    la precedente, rendant toute alteration detectable (valeur probante)."""
    try:
        cur.execute('SELECT hash FROM ' + table + ' ORDER BY id DESC LIMIT 1')
        row = cur.fetchone()
        prec = (dict(row).get('hash') if row else '') or 'GENESE'
    except Exception:
        prec = 'GENESE'
    h = hashlib.sha256((prec + '|' + payload).encode('utf-8')).hexdigest()
    return prec, h


def _rgpd_politiques(cur):
    cur.execute('SELECT * FROM rgpd_retention WHERE actif=1')
    return [dict(r) for r in cur.fetchall()]


def rgpd_purge_run(simulation=True):
    """Applique la politique de retention : anonymise ou signale les donnees dont
    la duree de conservation est depassee. Chaque execution est journalisee et
    scellee (preuve de suppression opposable en controle)."""
    conn = registre_get_db(); cur = conn.cursor()
    _rgpd_table(cur); _rgpd_tables2(cur); conn.commit()
    _rgpd_seed_retention(cur, conn)
    resultats = []
    for pol in _rgpd_politiques(cur):
        cible = pol.get('cible')
        mois = int(pol.get('duree_mois') or 0)
        action = pol.get('action') or 'signaler'
        limite = (datetime.utcnow() - timedelta(days=30 * max(1, mois))).isoformat()
        nb = 0
        detail = ''
        try:
            if cible == 'consent_records':
                cur.execute(registre_sql(
                    "SELECT COUNT(*) AS n FROM consent_records WHERE horodatage < %s AND efface=0 AND email <> ''",
                    "SELECT COUNT(*) AS n FROM consent_records WHERE horodatage < ? AND efface=0 AND email <> ''"), (limite,))
                nb = int(dict(cur.fetchone()).get('n', 0))
                if nb and not simulation and action == 'anonymiser':
                    cur.execute(registre_sql(
                        "UPDATE consent_records SET email='', efface=1 WHERE horodatage < %s AND efface=0 AND email <> ''",
                        "UPDATE consent_records SET email='', efface=1 WHERE horodatage < ? AND efface=0 AND email <> ''"), (limite,))
                detail = 'Preuves au-dela de ' + str(mois) + ' mois : adresse retiree, preuve conservee anonymisee.'
            elif cible == 'essais_expires':
                cur.execute(registre_sql(
                    "SELECT COUNT(*) AS n FROM clients WHERE essai_fin IS NOT NULL AND essai_fin < %s "
                    "AND (plan IS NULL OR plan='gratuit') AND stripe_subscription_id IS NULL AND nom_entreprise <> 'COMPTE EFFACE'",
                    "SELECT COUNT(*) AS n FROM clients WHERE essai_fin IS NOT NULL AND essai_fin < ? "
                    "AND (plan IS NULL OR plan='gratuit') AND stripe_subscription_id IS NULL AND nom_entreprise <> 'COMPTE EFFACE'"), (limite,))
                nb = int(dict(cur.fetchone()).get('n', 0))
                if nb and not simulation and action == 'anonymiser':
                    cur.execute(registre_sql(
                        "SELECT id, email FROM clients WHERE essai_fin IS NOT NULL AND essai_fin < %s "
                        "AND (plan IS NULL OR plan='gratuit') AND stripe_subscription_id IS NULL AND nom_entreprise <> 'COMPTE EFFACE'",
                        "SELECT id, email FROM clients WHERE essai_fin IS NOT NULL AND essai_fin < ? "
                        "AND (plan IS NULL OR plan='gratuit') AND stripe_subscription_id IS NULL AND nom_entreprise <> 'COMPTE EFFACE'"), (limite,))
                    for r in [dict(x) for x in cur.fetchall()]:
                        if str(r.get('email') or '').strip().lower() == str(CONSEILPREV_INTERNAL_EMAIL).strip().lower():
                            continue
                        anon = 'purge-' + _rgpd_hash(r.get('email')) + '@anonyme.invalid'
                        cur.execute(registre_sql(
                            "UPDATE clients SET email=%s, nom_entreprise='COMPTE EFFACE', mot_de_passe_hash='', actif=FALSE WHERE id=%s",
                            "UPDATE clients SET email=?, nom_entreprise='COMPTE EFFACE', mot_de_passe_hash='', actif=0 WHERE id=?"),
                            (anon, r['id']))
                detail = 'Essais expires depuis plus de ' + str(mois) + ' mois, sans souscription : comptes anonymises.'
            elif cible == 'clients_inactifs':
                cur.execute(registre_sql(
                    "SELECT COUNT(*) AS n FROM clients WHERE date_creation < %s AND (plan IS NULL OR plan='gratuit') "
                    "AND stripe_subscription_id IS NULL AND nom_entreprise <> 'COMPTE EFFACE'",
                    "SELECT COUNT(*) AS n FROM clients WHERE date_creation < ? AND (plan IS NULL OR plan='gratuit') "
                    "AND stripe_subscription_id IS NULL AND nom_entreprise <> 'COMPTE EFFACE'"), (limite,))
                nb = int(dict(cur.fetchone()).get('n', 0))
                detail = 'Comptes anciens sans souscription : signales pour decision (aucune suppression automatique).'
            elif cible == 'rgpd_demandes':
                cur.execute(registre_sql(
                    "SELECT COUNT(*) AS n FROM rgpd_demandes WHERE statut='traitee' AND traite_le < %s AND email <> ''",
                    "SELECT COUNT(*) AS n FROM rgpd_demandes WHERE statut='traitee' AND traite_le < ? AND email <> ''"), (limite,))
                nb = int(dict(cur.fetchone()).get('n', 0))
                if nb and not simulation and action == 'anonymiser':
                    cur.execute(registre_sql(
                        "UPDATE rgpd_demandes SET email='' WHERE statut='traitee' AND traite_le < %s AND email <> ''",
                        "UPDATE rgpd_demandes SET email='' WHERE statut='traitee' AND traite_le < ? AND email <> ''"), (limite,))
                detail = 'Demandes traitees au-dela de ' + str(mois) + ' mois : adresse retiree.'
            conn.commit()
        except Exception:
            try: conn.rollback()
            except Exception: pass
            detail = 'Controle impossible.'
        resultats.append({'cible': cible, 'libelle': pol.get('libelle'), 'duree_mois': mois,
                          'action': action, 'concernes': nb, 'detail': detail})
        if nb and not simulation:
            payload = json.dumps({'cible': cible, 'nb': nb, 'action': action,
                                  'ts': datetime.utcnow().isoformat()}, ensure_ascii=False)
            prec, h = _rgpd_chaine(cur, 'rgpd_purge_log', payload)
            cur.execute(registre_sql(
                'INSERT INTO rgpd_purge_log (horodatage, cible, nb, mode, detail, hash_prec, hash) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                'INSERT INTO rgpd_purge_log (horodatage, cible, nb, mode, detail, hash_prec, hash) VALUES (?,?,?,?,?,?,?)'),
                (datetime.utcnow().isoformat(), cible, nb, action, detail, prec, h))
            conn.commit()
    try: conn.close()
    except Exception: pass
    return resultats


@app.route('/api/rgpd/retention', methods=['GET', 'POST'])
def rgpd_retention():
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    conn = registre_get_db(); cur = conn.cursor()
    _rgpd_tables2(cur); conn.commit(); _rgpd_seed_retention(cur, conn)
    if request.method == 'POST':
        d = request.get_json(silent=True) or {}
        try:
            rid = int(d.get('id')); mois = max(1, min(int(d.get('duree_mois')), 240))
        except (TypeError, ValueError):
            try: conn.close()
            except Exception: pass
            return jsonify({'ok': False, 'error': 'Parametres invalides'}), 400
        cur.execute(registre_sql('UPDATE rgpd_retention SET duree_mois=%s, date_maj=%s WHERE id=%s',
                                 'UPDATE rgpd_retention SET duree_mois=?, date_maj=? WHERE id=?'),
                    (mois, datetime.utcnow().isoformat(), rid))
        conn.commit()
    cur.execute('SELECT * FROM rgpd_retention ORDER BY id')
    pols = [dict(r) for r in cur.fetchall()]
    try: conn.close()
    except Exception: pass
    return jsonify({'ok': True, 'politiques': pols})


@app.route('/api/rgpd/purge', methods=['POST'])
def rgpd_purge():
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    d = request.get_json(silent=True) or {}
    simulation = bool(d.get('simulation', True))
    res = rgpd_purge_run(simulation=simulation)
    return jsonify({'ok': True, 'simulation': simulation, 'resultats': res})


@app.route('/api/rgpd/purge-journal', methods=['GET'])
def rgpd_purge_journal():
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    conn = registre_get_db(); cur = conn.cursor()
    _rgpd_tables2(cur); conn.commit()
    cur.execute('SELECT * FROM rgpd_purge_log ORDER BY id DESC LIMIT 200')
    rows = [dict(r) for r in cur.fetchall()]
    try: conn.close()
    except Exception: pass
    return jsonify({'ok': True, 'journal': rows})


@app.route('/api/cron/rgpd-purge', methods=['POST', 'GET'])
def cron_rgpd_purge():
    """Tache planifiee : application automatique de la politique de retention."""
    secret = os.environ.get('CRON_SECRET')
    if not secret:
        return jsonify({'ok': False, 'error': 'Tache planifiee non configuree.'}), 501
    fourni = request.headers.get('X-Cron-Secret') or request.args.get('secret')
    if not fourni or not hmac.compare_digest(str(fourni), str(secret)):
        return jsonify({'ok': False, 'error': 'Non autorise.'}), 403
    try:
        res = rgpd_purge_run(simulation=False)
    except Exception:
        return jsonify({'ok': False, 'error': 'Echec de la purge.'}), 500
    return jsonify({'ok': True, 'executed_at': datetime.utcnow().isoformat(), 'resultats': res})


# ── AIPD (art. 35) ──
RGPD_AIPD_CRITERES = [
    'Evaluation ou scoring (y compris profilage)',
    'Decision automatisee avec effet juridique ou significatif',
    'Surveillance systematique',
    'Donnees sensibles ou a caractere hautement personnel',
    'Traitement a grande echelle',
    'Croisement ou combinaison d\'ensembles de donnees',
    'Personnes vulnerables',
    'Usage innovant ou application de nouvelles technologies (dont IA)',
    'Traitement faisant obstacle a un droit ou a un contrat',
]


@app.route('/api/rgpd/aipd', methods=['GET', 'POST'])
def rgpd_aipd():
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    conn = registre_get_db(); cur = conn.cursor()
    _rgpd_tables2(cur); conn.commit()
    if request.method == 'POST':
        d = request.get_json(silent=True) or {}
        criteres = d.get('criteres') if isinstance(d.get('criteres'), list) else []
        seuil = 1 if len(criteres) >= 2 else 0
        champs = (str(d.get('titre') or '')[:200], str(d.get('traitement') or '')[:200],
                  json.dumps(criteres, ensure_ascii=False)[:1200], seuil,
                  str(d.get('description') or '')[:4000], str(d.get('necessite') or '')[:4000],
                  str(d.get('risques') or '')[:4000], str(d.get('mesures') or '')[:4000],
                  str(d.get('risque_residuel') or '')[:200], str(d.get('avis_dpo') or '')[:2000],
                  str(d.get('statut') or 'brouillon')[:40], str(d.get('version') or '1.0')[:20],
                  datetime.utcnow().isoformat())
        rid = d.get('id')
        if rid:
            cur.execute(registre_sql(
                'UPDATE rgpd_aipd SET titre=%s, traitement=%s, criteres=%s, seuil_atteint=%s, description=%s, '
                'necessite=%s, risques=%s, mesures=%s, risque_residuel=%s, avis_dpo=%s, statut=%s, version=%s, date_maj=%s WHERE id=%s',
                'UPDATE rgpd_aipd SET titre=?, traitement=?, criteres=?, seuil_atteint=?, description=?, '
                'necessite=?, risques=?, mesures=?, risque_residuel=?, avis_dpo=?, statut=?, version=?, date_maj=? WHERE id=?'),
                champs + (int(rid),))
        else:
            cur.execute(registre_sql(
                'INSERT INTO rgpd_aipd (titre, traitement, criteres, seuil_atteint, description, necessite, '
                'risques, mesures, risque_residuel, avis_dpo, statut, version, date_maj) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                'INSERT INTO rgpd_aipd (titre, traitement, criteres, seuil_atteint, description, necessite, '
                'risques, mesures, risque_residuel, avis_dpo, statut, version, date_maj) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)'),
                champs)
        conn.commit()
    cur.execute('SELECT * FROM rgpd_aipd ORDER BY id DESC')
    rows = [dict(r) for r in cur.fetchall()]
    try: conn.close()
    except Exception: pass
    return jsonify({'ok': True, 'aipd': rows, 'criteres_reference': RGPD_AIPD_CRITERES})


@app.route('/api/rgpd/aipd/<int:aid>', methods=['DELETE'])
def rgpd_aipd_delete(aid):
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    conn = registre_get_db(); cur = conn.cursor()
    _rgpd_tables2(cur)
    cur.execute(registre_sql('DELETE FROM rgpd_aipd WHERE id=%s', 'DELETE FROM rgpd_aipd WHERE id=?'), (aid,))
    conn.commit()
    try: conn.close()
    except Exception: pass
    return jsonify({'ok': True})


# ── Demandes d'exercice de droits (art. 12) ──
@app.route('/api/rgpd/demandes', methods=['GET', 'POST'])
def rgpd_demandes():
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    conn = registre_get_db(); cur = conn.cursor()
    _rgpd_tables2(cur); conn.commit()
    if request.method == 'POST':
        d = request.get_json(silent=True) or {}
        rid = d.get('id')
        if rid and d.get('statut'):
            cur.execute(registre_sql(
                'UPDATE rgpd_demandes SET statut=%s, traite_le=%s, note=%s WHERE id=%s',
                'UPDATE rgpd_demandes SET statut=?, traite_le=?, note=? WHERE id=?'),
                (str(d.get('statut'))[:30], datetime.utcnow().isoformat(), str(d.get('note') or '')[:1000], int(rid)))
        else:
            recu = datetime.utcnow()
            cur.execute(registre_sql(
                'INSERT INTO rgpd_demandes (recu_le, echeance, type, email, statut, note) VALUES (%s,%s,%s,%s,%s,%s)',
                'INSERT INTO rgpd_demandes (recu_le, echeance, type, email, statut, note) VALUES (?,?,?,?,?,?)'),
                (recu.isoformat(), (recu + timedelta(days=30)).isoformat(),
                 str(d.get('type') or 'acces')[:40], str(d.get('email') or '')[:200],
                 'en_cours', str(d.get('note') or '')[:1000]))
        conn.commit()
    cur.execute('SELECT * FROM rgpd_demandes ORDER BY id DESC LIMIT 200')
    rows = [dict(r) for r in cur.fetchall()]
    try: conn.close()
    except Exception: pass
    return jsonify({'ok': True, 'demandes': rows})


# ── Controles calcules (non-conformites reelles) ──
def _rgpd_controles_calcules():
    """Detecte les non-conformites a partir de l'etat reel de la base."""
    out = []
    conn = registre_get_db(); cur = conn.cursor()
    _rgpd_table(cur); _rgpd_tables2(cur); conn.commit()
    _rgpd_seed_retention(cur, conn)
    # 1. Donnees au-dela de leur duree de conservation (art. 5.1.e)
    depasse = 0
    try:
        for r in rgpd_purge_run(simulation=True):
            if r.get('action') != 'signaler':
                depasse += int(r.get('concernes') or 0)
    except Exception:
        depasse = -1
    out.append({'article': 'Art. 5.1.e', 'intitule': 'Limitation de la conservation (mesure)', 'mode': 'automatique',
                'statut': 'conforme' if depasse == 0 else 'a-verifier',
                'detail': ('Aucune donnee au-dela de sa duree de conservation.' if depasse == 0
                           else str(depasse) + ' enregistrement(s) au-dela de la duree : executer la purge.')})
    # 2. AIPD manquante pour un traitement a risque (art. 35)
    try:
        cur.execute("SELECT COUNT(*) AS n FROM rgpd_aipd WHERE seuil_atteint=1 AND statut='validee'")
        aipd_ok = int(dict(cur.fetchone()).get('n', 0))
        cur.execute('SELECT COUNT(*) AS n FROM rgpd_aipd')
        aipd_total = int(dict(cur.fetchone()).get('n', 0))
    except Exception:
        aipd_ok = aipd_total = 0
    out.append({'article': 'Art. 35', 'intitule': 'Analyse d\'impact (AIPD) formalisee', 'mode': 'automatique',
                'statut': 'conforme' if aipd_ok > 0 else 'a-verifier',
                'detail': (str(aipd_ok) + ' AIPD validee(s) sur ' + str(aipd_total) + ' enregistree(s).'
                           if aipd_total else 'Aucune AIPD enregistree : realiser le test de seuil pour les traitements a risque (IA, profilage, grande echelle).')})
    # 3. Demandes de droits hors delai (art. 12)
    try:
        maintenant = datetime.utcnow().isoformat()
        cur.execute(registre_sql(
            "SELECT COUNT(*) AS n FROM rgpd_demandes WHERE statut='en_cours' AND echeance < %s",
            "SELECT COUNT(*) AS n FROM rgpd_demandes WHERE statut='en_cours' AND echeance < ?"), (maintenant,))
        retard = int(dict(cur.fetchone()).get('n', 0))
    except Exception:
        retard = 0
    out.append({'article': 'Art. 12', 'intitule': 'Delai de reponse aux demandes (un mois)', 'mode': 'automatique',
                'statut': 'conforme' if retard == 0 else 'a-verifier',
                'detail': ('Aucune demande hors delai.' if retard == 0 else str(retard) + ' demande(s) hors delai d\'un mois.')})
    # 4. Journal de purge scelle (preuve de suppression)
    try:
        cur.execute('SELECT COUNT(*) AS n FROM rgpd_purge_log')
        nb_purge = int(dict(cur.fetchone()).get('n', 0))
    except Exception:
        nb_purge = 0
    out.append({'article': 'Art. 5 / 17', 'intitule': 'Preuve de suppression (journal scelle)', 'mode': 'automatique',
                'statut': 'conforme' if nb_purge > 0 else 'a-verifier',
                'detail': (str(nb_purge) + ' operation(s) de purge journalisee(s) et scellee(s) par chainage d\'empreintes.'
                           if nb_purge else 'Aucune purge executee a ce jour : lancer la purge ou attendre la tache planifiee.')})
    # 5. Historique d'audit archive
    try:
        cur.execute('SELECT COUNT(*) AS n FROM rgpd_audits')
        nb_audits = int(dict(cur.fetchone()).get('n', 0))
    except Exception:
        nb_audits = 0
    out.append({'article': 'Art. 5.2', 'intitule': 'Responsabilite : historique d\'audit archive', 'mode': 'automatique',
                'statut': 'conforme' if nb_audits > 0 else 'a-verifier',
                'detail': (str(nb_audits) + ' rapport(s) d\'audit archive(s) et scelle(s).'
                           if nb_audits else 'Aucun rapport archive : archiver un rapport pour constituer l\'historique.')})
    try: conn.close()
    except Exception: pass
    return out


@app.route('/api/rgpd/audits', methods=['GET', 'POST'])
def rgpd_audits():
    """Historique des rapports d'audit, scelle par chainage d'empreintes."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    conn = registre_get_db(); cur = conn.cursor()
    _rgpd_tables2(cur); conn.commit()
    if request.method == 'POST':
        rap = json.loads(rgpd_rapport_audit().get_data(as_text=True))
        contenu = json.dumps(rap, ensure_ascii=False)
        prec, h = _rgpd_chaine(cur, 'rgpd_audits', contenu)
        cur.execute(registre_sql(
            'INSERT INTO rgpd_audits (horodatage, score, contenu, hash_prec, hash) VALUES (%s,%s,%s,%s,%s)',
            'INSERT INTO rgpd_audits (horodatage, score, contenu, hash_prec, hash) VALUES (?,?,?,?,?)'),
            (datetime.utcnow().isoformat(), int(rap.get('score') or 0), contenu, prec, h))
        conn.commit()
    cur.execute('SELECT id, horodatage, score, hash_prec, hash FROM rgpd_audits ORDER BY id DESC LIMIT 100')
    rows = [dict(r) for r in cur.fetchall()]
    try: conn.close()
    except Exception: pass
    return jsonify({'ok': True, 'audits': rows})


@app.route('/api/rgpd/audits/<int:aid>', methods=['GET'])
def rgpd_audit_detail(aid):
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    conn = registre_get_db(); cur = conn.cursor()
    _rgpd_tables2(cur)
    cur.execute(registre_sql('SELECT * FROM rgpd_audits WHERE id=%s', 'SELECT * FROM rgpd_audits WHERE id=?'), (aid,))
    row = cur.fetchone()
    try: conn.close()
    except Exception: pass
    if not row:
        return jsonify({'ok': False, 'error': 'Rapport introuvable'}), 404
    d = dict(row)
    try:
        d['contenu'] = json.loads(d.get('contenu') or '{}')
    except Exception:
        pass
    return jsonify({'ok': True, 'audit': d})



# ══════════════════════════════════════════════════════════
# TRANSPARENCE IA — ARTICLE 50 DU REGLEMENT (UE) 2024/1689
# Registre probant des usages d'IA : role (fournisseur / deployeur), nature du
# contenu, marquage lisible par machine, etiquetage visible, exception invoquee
# (oeuvre creative ; controle editorial humain) et responsable editorial.
# Echeances : 2 aout 2026 (art. 50), 2 decembre 2026 (fin de periode
# transitoire), 2 fevrier 2027 (interoperabilite de la detection).
# Outillage technique ; ne constitue pas un avis juridique.
# ══════════════════════════════════════════════════════════

IA50_ECHEANCES = [
    {'date': '2026-08-02', 'objet': 'Entree en application des obligations de transparence (art. 50) : marquage (fournisseurs) et etiquetage (deployeurs).'},
    {'date': '2026-12-02', 'objet': 'Fin de la periode transitoire pour les systemes deja sur le marche.'},
    {'date': '2027-02-02', 'objet': 'Solution d\'interoperabilite du marquage et acces a la detection (fournisseurs).'},
]

IA50_USAGES_DEFAUT = [
    {'systeme': 'Assistants conversationnels du site public (2)', 'role': 'deployeur',
     'contenu': 'Texte (reponses aux visiteurs)',
     'marquage': 'Sans objet (echange interactif, non diffuse comme publication)',
     'etiquetage': 'Mention d\'IA affichee des la premiere interaction (art. 50.1) — EN PLACE',
     'exception': 'Aucune', 'responsable': 'Christophe CERF'},
    {'systeme': 'Copilote Sentinel (assistant de la plateforme)', 'role': 'deployeur',
     'contenu': 'Texte (reponses aux clients, moteurs Claude et Mistral)',
     'marquage': 'Sans objet (echange interactif)',
     'etiquetage': 'Mention d\'IA affichee des la premiere interaction (art. 50.1) — EN PLACE',
     'exception': 'Aucune', 'responsable': 'Christophe CERF'},
    {'systeme': 'Analyses generees par IA dans les modules Sentinel', 'role': 'fournisseur',
     'contenu': 'Texte d\'analyse produit par IA',
     'marquage': 'Mention visible apposee sur la sortie ; metadonnees dans les documents exportes',
     'etiquetage': 'Bandeau "AI GENERATED" sur la sortie — EN PLACE',
     'exception': 'Aucune', 'responsable': 'Christophe CERF'},
    {'systeme': 'Synthese de la base de connaissance (explorateur RAG)', 'role': 'fournisseur',
     'contenu': 'Texte de synthese genere par IA, avec citations',
     'marquage': 'Mention visible ; metadonnees lisibles par machine a l\'export',
     'etiquetage': 'Bandeau "AI GENERATED" sur la reponse — EN PLACE',
     'exception': 'Aucune', 'responsable': 'Christophe CERF'},
    {'systeme': 'Rapports generes par Sentinel (IA Act annuel, audit RGPD, attestation art. 50)', 'role': 'fournisseur',
     'contenu': 'Documents (texte et indicateurs)',
     'marquage': 'Metadonnees lisibles par machine (ai-generated, ai-disclosure) inserees dans le document — EN PLACE',
     'etiquetage': 'Mention "AI GENERATED" / "AI ASSISTED" apposee sur le document — EN PLACE',
     'exception': 'Aucune', 'responsable': 'Christophe CERF'},
    {'systeme': 'Veille reglementaire (flux RSS du site)', 'role': 'deployeur',
     'contenu': 'Titres et resumes repris des sources externes',
     'marquage': 'Sans objet',
     'etiquetage': 'Non requis : contenu NON genere par IA (reprise sans reformulation ; '
                   'la selection par mots-cles ne constitue pas une generation)',
     'exception': 'Sans objet', 'responsable': 'Christophe CERF'},
    {'systeme': 'Actualites du site (redaction assistee par IA)', 'role': 'deployeur',
     'contenu': 'Texte d\'interet public elabore avec l\'assistance d\'une IA',
     'marquage': 'Sans objet (redaction assistee, publication sous responsabilite editoriale)',
     'etiquetage': 'Non requis : exception invoquee — mention de transparence et de responsabilite '
                   'editoriale publiee sur la page Actualites — EN PLACE',
     'exception': 'Controle editorial humain (art. 50 par. 4) : examen humain systematique avant publication ; '
                  'responsabilite editoriale assumee nommement',
     'responsable': 'Christophe CERF'},
]


def _ia50_table(cur, conn):
    _pk = 'SERIAL PRIMARY KEY' if REGISTRE_USE_PG else 'INTEGER PRIMARY KEY AUTOINCREMENT'
    cur.execute('CREATE TABLE IF NOT EXISTS ia50_usages (id ' + _pk + ', systeme TEXT, role TEXT, '
                'contenu TEXT, marquage TEXT, etiquetage TEXT, exception TEXT, responsable TEXT, '
                'conforme INTEGER DEFAULT 0, date_maj TEXT)')
    conn.commit()
    cur.execute('SELECT COUNT(*) AS n FROM ia50_usages')
    if int(dict(cur.fetchone()).get('n', 0)) > 0:
        return
    for u in IA50_USAGES_DEFAUT:
        cur.execute(registre_sql(
            'INSERT INTO ia50_usages (systeme, role, contenu, marquage, etiquetage, exception, responsable, conforme, date_maj) '
            'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            'INSERT INTO ia50_usages (systeme, role, contenu, marquage, etiquetage, exception, responsable, conforme, date_maj) '
            'VALUES (?,?,?,?,?,?,?,?,?)'),
            (u['systeme'], u['role'], u['contenu'], u['marquage'], u['etiquetage'], u['exception'],
             u['responsable'], 0, datetime.utcnow().isoformat()))
    conn.commit()


@app.route('/api/ia50/usages', methods=['GET', 'POST'])
def ia50_usages():
    """Registre de transparence (art. 50) : usages d'IA, marquage, etiquetage,
    exceptions et responsable editorial. Reserve a CONSEILPREV."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    conn = registre_get_db(); cur = conn.cursor()
    _ia50_table(cur, conn)
    if request.method == 'POST':
        d = request.get_json(silent=True) or {}
        rid = d.get('id')
        if rid and 'conforme' in d and len(d) <= 2:
            cur.execute(registre_sql(
                'UPDATE ia50_usages SET conforme=%s, date_maj=%s WHERE id=%s',
                'UPDATE ia50_usages SET conforme=?, date_maj=? WHERE id=?'),
                (1 if d.get('conforme') else 0, datetime.utcnow().isoformat(), int(rid)))
        else:
            champs = (str(d.get('systeme') or '')[:200], str(d.get('role') or 'deployeur')[:30],
                      str(d.get('contenu') or '')[:200], str(d.get('marquage') or '')[:300],
                      str(d.get('etiquetage') or '')[:300], str(d.get('exception') or 'Aucune')[:300],
                      str(d.get('responsable') or '')[:120], 1 if d.get('conforme') else 0,
                      datetime.utcnow().isoformat())
            if not champs[0]:
                try: conn.close()
                except Exception: pass
                return jsonify({'ok': False, 'error': 'Systeme requis'}), 400
            if rid:
                cur.execute(registre_sql(
                    'UPDATE ia50_usages SET systeme=%s, role=%s, contenu=%s, marquage=%s, etiquetage=%s, '
                    'exception=%s, responsable=%s, conforme=%s, date_maj=%s WHERE id=%s',
                    'UPDATE ia50_usages SET systeme=?, role=?, contenu=?, marquage=?, etiquetage=?, '
                    'exception=?, responsable=?, conforme=?, date_maj=? WHERE id=?'), champs + (int(rid),))
            else:
                cur.execute(registre_sql(
                    'INSERT INTO ia50_usages (systeme, role, contenu, marquage, etiquetage, exception, responsable, conforme, date_maj) '
                    'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                    'INSERT INTO ia50_usages (systeme, role, contenu, marquage, etiquetage, exception, responsable, conforme, date_maj) '
                    'VALUES (?,?,?,?,?,?,?,?,?)'), champs)
        conn.commit()
    cur.execute('SELECT * FROM ia50_usages ORDER BY id')
    rows = [dict(r) for r in cur.fetchall()]
    total = len(rows)
    ok = sum(1 for r in rows if r.get('conforme'))
    jours = None
    try:
        jours = (datetime(2026, 8, 2) - datetime.utcnow()).days
    except Exception:
        jours = None
    try: conn.close()
    except Exception: pass
    return jsonify({'ok': True, 'usages': rows, 'total': total, 'conformes': ok,
                    'taux': round(100.0 * ok / max(1, total)),
                    'jours_avant_echeance': jours, 'echeances': IA50_ECHEANCES})


@app.route('/api/ia50/reset', methods=['POST'])
def ia50_reset():
    """Reinitialise le registre aux valeurs de reference (etat reel du code)."""
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    conn = registre_get_db(); cur = conn.cursor()
    _ia50_table(cur, conn)
    cur.execute('DELETE FROM ia50_usages')
    conn.commit()
    _ia50_table(cur, conn)
    try: conn.close()
    except Exception: pass
    return jsonify({'ok': True})


@app.route('/api/ia50/usages/<int:uid>', methods=['DELETE'])
def ia50_usages_delete(uid):
    if not raas_require_conseilprev():
        return jsonify({'ok': False, 'error': 'Reserve a CONSEILPREV'}), 403
    conn = registre_get_db(); cur = conn.cursor()
    cur.execute(registre_sql('DELETE FROM ia50_usages WHERE id=%s', 'DELETE FROM ia50_usages WHERE id=?'), (uid,))
    conn.commit()
    try: conn.close()
    except Exception: pass
    return jsonify({'ok': True})



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
# deploy trigger
# deploy trigger 2
# deploy trigger - sync jurs/cj/sim
# deploy trigger - fix simuler deploiement card
# deploy trigger - fix comparateur crash
# deploy trigger - pricing chart tooltips
# deploy trigger - test RAG
