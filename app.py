import os, re as _re, time, hashlib, json, logging
import requests, feedparser
from functools import wraps
from collections import defaultdict
from flask import Flask, send_from_directory, jsonify, request, abort, make_response
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
MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY', 'f5NFzuhlT1830mek1QYix3ofyBS3Y8gf')
MISTRAL_URL     = "https://api.mistral.ai/v1/chat/completions"
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
    _re.compile(r'(.)\1{8,}'),                     # Répétitions de chars (aaaaaaa)
    _re.compile(r'\b\d{10,}\b'),                   # Grands nombres
    _re.compile(r'[^\w\s@.,!?\'"-]{5,}'),          # Trop de caractères spéciaux
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
        "script-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://api.mistral.ai; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: blob: https:; "
        "media-src 'self' blob:; "
        "connect-src 'self' https://api.mistral.ai https://api.rss2json.com https://rss2json.com; "
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

_news_cache = {"data": [], "ts": 0}
CACHE_TTL   = 600

def _detect_cat(title, default_cat):
    t = (title or "").lower()
    if _re.search(r"mistral|gemini|gpt|llm|ia g.n.r|generat|intelligence artif", t): return "ai"
    if _re.search(r"france|cnil|anssi|gouvernement|s.nat|assembl.e|dinum",       t): return "fr"
    if _re.search(r"rgpd|gdpr|ia act|nist|iso|conformit|r.glement|directive",    t): return "regl"
    if _re.search(r"cyber|attaque|malware|ransomware|phish|s.curit|vulnerab",     t): return "secu"
    if _re.search(r"europe|usa|chine|international|mondial|onu|ocde|g7",          t): return "intl"
    return default_cat

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
        # Construire messages
        messages = [{"role": "system", "content": MISTRAL_SYSTEM}]
        for h in history[-8:]:
            if h.get('role') in ('user','assistant') and h.get('content'):
                messages.append({"role": h['role'], "content": str(h['content'])[:1000]})
        messages.append({"role": "user", "content": user_msg})
        resp = requests.post(
            MISTRAL_URL,
            headers={"Content-Type":"application/json","Authorization":f"Bearer {MISTRAL_API_KEY}"},
            json={"model":"mistral-large-latest","messages":messages,"max_tokens":800,"temperature":0.7},
            timeout=30
        )
        if not resp.ok:
            bf_protector.record_attempt(bf_key, success=False)
            return jsonify({"error": f"API error {resp.status_code}"}), 500
        bf_protector.record_attempt(bf_key, success=True)
        reply = resp.json()['choices'][0]['message']['content']
        return jsonify({"reply": reply, "model": "mistral-large-latest"})
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
