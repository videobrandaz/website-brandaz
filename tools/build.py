"""Gera o site estático da Brandaz a partir de content/*.json + static/.

    python3 tools/build.py                 -> site/ (produção: URLs limpas, Cloudflare Pages)
    python3 tools/build.py --preview DIR   -> DIR/ (prévia no Claude: arquivos .html soltos e links relativos)
    python3 tools/build.py --pages DIR     -> DIR/ (prévia no GitHub Pages: links relativos, fora do Google)

Só usa a biblioteca padrão do Python, para rodar direto no build do Cloudflare Pages.
"""
import html, json, os, re, shutil, sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from home_js import HOME, COVER_A, COVER_B

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREVIEW = '--preview' in sys.argv
PAGES = '--pages' in sys.argv
RELATIVE = PREVIEW or PAGES  # links relativos: funciona em qualquer subpasta (ex.: conta.github.io/website-brandaz/)
OUT = (os.path.abspath(sys.argv[sys.argv.index('--preview' if PREVIEW else '--pages') + 1]) if RELATIVE
       else os.path.join(ROOT, 'site'))

def load(name):
    with open(os.path.join(ROOT, 'content', name), encoding='utf-8') as f:
        return json.load(f)

C = load('site.json')
SITE = C['site']
PROJECTS = load('projetos.json')
POSTS = sorted(load('blog.json'), key=lambda b: b['date'], reverse=True)
DIMS = load('dimensoes.json')
DEP = load('depoimentos.json')
BY_SLUG = {p['slug']: p for p in PROJECTS}
BASE = SITE['url']
YEAR = date.today().year
E = html.escape
WA = SITE['phone']['whatsapp']
MAPS = SITE['maps']

def _ver(rel):
    """Versão curta do arquivo (muda quando o conteúdo muda): força o navegador a buscar o CSS/JS novo."""
    import hashlib
    with open(os.path.join(ROOT, 'static', rel), 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()[:8]
CSS_V, JS_V = _ver('assets/css/site.css'), _ver('assets/js/site.js')

# ---------------------------------------------------------------- URLs
def U(p):
    """Converte um caminho do site ("/projetos/x/", "/assets/...") no link certo para o modo atual."""
    if not p or p.startswith(('http:', 'https:', 'mailto:', 'tel:', '#', 'data:')):
        return p
    path, _, frag = p.partition('#')
    frag = '#' + frag if frag else ''
    if not RELATIVE:
        if not path.startswith('/assets/') and '.' not in path.rsplit('/', 1)[-1] and not path.endswith('/'):
            path += '/'
        return path + frag
    if path.startswith('/assets/') or '.' in path.rsplit('/', 1)[-1]:
        return path.lstrip('/') + frag
    clean = path.strip('/')
    if not clean:
        return './' + frag
    return clean.replace('/', '-') + '.html' + frag

def out_file(canon):
    if RELATIVE:
        return 'index.html' if canon == '/' else U(canon)
    return canon.strip('/') + '/index.html' if canon != '/' else 'index.html'

def dims(src):
    w, h = DIMS.get(src, (1600, 1200))
    return w, h

# ---------------------------------------------------------------- ícones
def svg(body, cls='ic', vb='0 0 24 24', extra=''):
    return f'<svg class="{cls}" viewBox="{vb}" aria-hidden="true"{extra}>{body}</svg>'

ARROW = svg('<path d="M5 12h14M13 6l6 6-6 6"/>')
BACK = svg('<path d="M19 12H5M11 6l-6 6 6 6"/>')
I_PAUSE = svg('<path d="M8 5v14M16 5v14"/>')
I_PLAY = svg('<path d="M7 4.5v15l12-7.5z"/>')
LINE = ' fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"'
I_WA = svg('<path d="M3.5 20.5l1.2-4.2A8.5 8.5 0 1 1 8 19.6z"/><path d="M9 8.6c0 3.5 2.9 6.4 6.4 6.4l1.1-1.6-2-.9-1 1c-1.2-.5-2.1-1.4-2.6-2.6l1-1-.9-2z"/>', 'ic5', extra=LINE)
I_MAIL = svg('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>', 'ic5', extra=LINE)
I_IG = svg('<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".6"/>', 'ic5', extra=LINE)
I_FB = svg('<path d="M14 8.5h3V5h-3c-2.6 0-4 1.7-4 4.2V11H7.5v3.5H10V21h3.6v-6.5H16l.6-3.5h-3V9.4c0-.5.3-.9.9-.9z"/>', 'ic5', extra=' fill="currentColor"')
I_BE = svg('<path d="M3 6h5.2c2 0 3.3 1 3.3 2.7 0 1.1-.6 1.9-1.5 2.2 1.2.3 2 1.3 2 2.6 0 2-1.5 3.2-3.7 3.2H3zm2.4 4.3h2.4c.9 0 1.4-.4 1.4-1.1s-.5-1.1-1.4-1.1H5.4zm0 4.6h2.6c1 0 1.6-.5 1.6-1.3s-.6-1.3-1.6-1.3H5.4zM14.5 7.2h5.3v1.3h-5.3zM17.2 9.6c2.4 0 3.7 1.7 3.6 4.3h-5.3c.1 1.2.8 1.8 1.8 1.8.8 0 1.3-.3 1.5-.9h1.9c-.4 1.6-1.7 2.5-3.4 2.5-2.3 0-3.8-1.5-3.8-3.9s1.5-3.8 3.7-3.8zm1.5 3c-.1-.9-.6-1.5-1.5-1.5s-1.5.6-1.6 1.5z"/>', 'ic5', extra=' fill="currentColor"')
I_PIN = svg('<path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>', 'ic5', extra=LINE)
I_PHONE = svg('<path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 5a2 2 0 0 1 2-2z"/>', 'ic5', extra=LINE)
I_CHECK = svg('<circle cx="12" cy="12" r="9"/><path d="m8 12.5 2.6 2.5L16 9.5"/>', 'ic5', extra=LINE)
QUOTE_D = ('M3 21v-6.6C3 9 5.9 5.2 10.6 3.4l1.1 2.3C9 7 7.6 9.2 7.4 12H11v9zm12 0v-6.6c0-5.4 2.9-9.2 7.6-11l1.1 2.3'
           'C21 7 19.6 9.2 19.4 12H23v9z')
QUOTE = svg(f'<path d="{QUOTE_D}"/>', 'qmark', vb='0 0 26 24', extra=' fill="currentColor"')
I_MENU = svg('<path d="M4 7h16M4 12h16M4 17h16"/>', 'ic6', extra=LINE)
DIFF_ICONS = [
    '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
    '<circle cx="12" cy="4.5" r="2.5"/><circle cx="4.5" cy="12" r="2.5"/><circle cx="19.5" cy="12" r="2.5"/><circle cx="12" cy="19.5" r="2.5"/><path d="M10.2 6.3 6.3 10.2M13.8 6.3l3.9 3.9M6.3 13.8l3.9 3.9M17.7 13.8l-3.9 3.9"/>',
    '<path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.3 1 2.3h6c0-1 .4-1.8 1-2.3A7 7 0 0 0 12 2z"/>',
    '<path d="M13 2 3 14h9l-1 8 10-12h-9z"/>',
    '<path d="m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z"/>',
    '<path d="M3 3v18h18"/><path d="M8 17v-5M13 17V8M18 17v-9"/>',
]
SOCIALS = [('WhatsApp', WA, I_WA), ('Instagram', SITE['instagram']['url'], I_IG), ('Facebook', SITE['facebook'], I_FB), ('Behance', SITE['behance'], I_BE)]

# ---------------------------------------------------------------- peças de texto
def accent(text):
    """*trecho* vira destaque na cor de acento."""
    return re.sub(r'\*(.+?)\*', r'<span class="text-accent">\1</span>', E(text))

def title(first, second, tag='h2', hero=False, up=True, cls=''):
    c = 'editorial-title' + (' editorial-title-hero' if hero else '') + (' up' if up and not hero else '') + (' ' + cls if cls else '')
    return (f'<{tag} class="{c}" aria-label="{E(first)} {E(second)}"><span class="ln"><span class="l1">{E(first)}</span></span>'
            f'<span class="ln"><span class="l2">{E(second)}</span></span></{tag}>')

def label(text):
    return f'<p class="editorial-label">{E(text)}</p>'

def btn(text, href, cls='', ext=False):
    tgt = ' target="_blank" rel="noopener noreferrer"' if ext else ''
    return f'<a class="btn {cls}" data-slot="button" href="{U(href)}"{tgt}>{E(text)} {ARROW}</a>'

def words(text, cls, ident=''):
    """Frase que acende palavra por palavra com o scroll (*destaques* em acento)."""
    out, em = [], False
    for raw in text.split(' '):
        if raw.startswith('*'):
            em = True
        out.append(f'<span class="w{" em" if em else ""}" aria-hidden="true">{E(raw.replace("*", ""))} </span>')
        if raw.rstrip('.,').endswith('*'):
            em = False
    idattr = f' id="{ident}"' if ident else ''
    return f'<p class="{cls}"{idattr} data-scrub aria-label="{E(text.replace("*", ""))}">{"".join(out)}</p>'

def img(src, alt, cls='', lazy=True, sizes=''):
    w, h = dims(src)
    return (f'<img{" class=" + chr(34) + cls + chr(34) if cls else ""} src="{U(src)}" alt="{E(alt)}" width="{w}" height="{h}"'
            f'{" loading=" + chr(34) + "lazy" + chr(34) if lazy else ""} decoding="async">')

def date_br(iso):
    meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
    y, m, d = map(int, iso.split('-'))
    return f'{d} de {meses[m - 1]} de {y}'

def md(text):
    """Markdown simples dos posts: ##, ###, listas, citações, **negrito**, *itálico*, [links](url)."""
    def inline(s):
        s = E(s, quote=False)
        s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: f'<a href="{E(U(m.group(2)))}"{" target=_blank rel=noopener" if m.group(2).startswith("http") else ""}>{m.group(1)}</a>', s)
        s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
        return re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', s)
    out, para, lst = [], [], []
    def flush():
        if para:
            out.append(f'<p>{inline(" ".join(para))}</p>'); para.clear()
        if lst:
            out.append('<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in lst) + '</ul>'); lst.clear()
    for line in text.split('\n'):
        s = line.strip()
        if not s:
            flush()
        elif s.startswith('### '):
            flush(); out.append(f'<h3>{inline(s[4:])}</h3>')
        elif s.startswith('## '):
            flush(); out.append(f'<h2>{inline(s[3:])}</h2>')
        elif s.startswith('> '):
            flush(); out.append(f'<blockquote>{inline(s[2:])}</blockquote>')
        elif s.startswith(('- ', '* ')):
            if para:
                flush()
            lst.append(s[2:])
        else:
            if lst:
                flush()
            para.append(s)
    flush()
    return '\n'.join(out)

# ---------------------------------------------------------------- mapa, cabeçalho, rodapé
def static_map(cls=''):
    return (f'<a class="map {cls}" href="{MAPS}" target="_blank" rel="noopener noreferrer" aria-label="Mapa: Agência Brandaz, Chapecó. Abrir no Google Maps">'
            f'<img src="{U("/assets/site/map-brandaz.webp")}" alt="Mapa da localização da Agência Brandaz em Chapecó" loading="lazy" width="3000" height="640">'
            f'<span class="pin" aria-hidden="true"><img src="{U("/assets/site/mark-clean.png")}" alt=""></span>'
            f'<span class="tag">Agência Brandaz · Sala 902</span><small>© OpenStreetMap</small></a>')

def nav_links(current, cls='nav-link'):
    return ''.join(f'<a class="{cls}{" current" if current and href.startswith(current) and current != "/" else ""}" href="{U(href)}"'
                   f'{" aria-current=" + chr(34) + "page" + chr(34) if current == href else ""}>{E(name)}</a>' for name, href in C['nav'])

def header(current, home):
    logo = U('/assets/site/logo-brandaz.png')
    socials = ''.join(f'<a href="{u}" target="_blank" rel="noopener noreferrer" aria-label="{n}">{i}</a>' for n, u, i in SOCIALS)
    return f'''<a class="skip" href="#conteudo">Pular para o conteúdo</a>
<div class="reading-progress" aria-hidden="true"><i id="prog"></i></div>
<header class="site-header" id="hdr" data-home="{str(home).lower()}" data-scrolled="false"><div class="site-header-inner">
  <a class="hlogo" href="{U('/')}" aria-label="Brandaz, página inicial"><img src="{logo}" alt="Brandaz Agência" width="600" height="300"></a>
  <nav class="main" aria-label="Menu principal">{nav_links(current)}</nav>
  <div class="hright"><a class="btn px5 hcta" data-slot="button" href="{U('/contato/')}">Contato {ARROW}</a><button type="button" class="menu-btn" id="menuBtn" aria-label="Abrir menu" aria-expanded="false" aria-controls="mm">{I_MENU}</button></div>
</div></header>
<div class="mobile-menu" id="mm" aria-hidden="true">
  <div class="top"><img src="{logo}" alt="Brandaz" width="600" height="300"><button type="button" class="menu-btn x" id="mmX" aria-label="Fechar menu">×</button></div>
  <nav aria-label="Menu"><a href="{U('/')}">Início</a>{nav_links(current, '')}<a href="{U('/contato/')}">Contato</a></nav>
  <div class="socials mm-socials">{socials}</div>
</div>'''

def footer(full=False):
    fnav = ''.join(f'<a href="{U(h)}">{E(n)}</a>' for n, h in C['nav']) + f'<a href="{U("/contato/")}">Contato</a>'
    if not full:
        return f'''<footer class="site-footer" data-ch="Contato"><div class="f-in">
  <nav class="f-nav" aria-label="Rodapé">{fnav}</nav>
  <div class="f-addr"><p>Brandaz</p><p>{E(SITE['address_full'])}</p><a href="tel:{SITE['phone']['tel']}">{SITE['phone']['intl']}</a><a class="maps" href="{MAPS}" target="_blank" rel="noopener noreferrer">Ver no Google Maps</a></div>
  {static_map('mini')}
  <p class="f-copy">© {YEAR} Brandaz. Todos os direitos reservados.</p></div>
</footer>'''
    socials = ''.join(f'<a href="{u}" target="_blank" rel="noopener noreferrer" aria-label="{n}">{i}</a>' for n, u, i in SOCIALS)
    return f'''<section class="editorial-band footer-cta" data-ch="Próximo capítulo"><div class="editorial-container">
  {label("Vamos conversar")}<h2 class="type-h1 mt6"><strong>O próximo capítulo</strong> já começou.</h2>
  <div class="mt10 hero-buttons static">{btn("Falar no WhatsApp", WA, ext=True)}{btn("Ver portfólio", "/projetos/", "ghost")}</div></div></section>
<footer class="site-footer" data-ch="Contato"><div class="f-full">
  <div class="f-grid">
    <div><p class="k">Fale com a gente</p><a class="mail" href="mailto:{SITE['email']}">{SITE['email']}</a><a class="tel" href="tel:{SITE['phone']['tel']}">{SITE['phone']['display']}</a></div>
    <div><div class="socials">{socials}</div><p class="addr">{E(SITE['address'])}</p><a class="maps" href="{MAPS}" target="_blank" rel="noopener noreferrer">Ver no Google Maps</a></div>
    <nav aria-label="Rodapé">{fnav}<a href="{U('/como-trabalhamos/')}">Como trabalhamos</a></nav>
  </div>
  {static_map('mini wide')}
  <p class="copy">© {YEAR} Brandaz · Onde a estratégia ganha magia. Todos os direitos reservados.</p>
</div></footer>'''

# ---------------------------------------------------------------- SEO
ORG = {"@type": "Organization", "@id": f"{BASE}/#organization", "name": "Brandaz", "url": BASE, "logo": f"{BASE}/assets/site/logo-brandaz.png",
       "image": f"{BASE}/og-image.jpg", "email": SITE['email'], "telephone": SITE['phone']['intl'], "slogan": SITE['slogan'],
       "founder": {"@type": "Person", "name": SITE['founder']}, "sameAs": [SITE['instagram']['url'], SITE['facebook'], SITE['behance']]}
PRO = dict(ORG, **{"@type": "ProfessionalService", "@id": f"{BASE}/#agency",
       "address": {"@type": "PostalAddress", "streetAddress": SITE['street'], "addressLocality": SITE['city'], "addressRegion": SITE['region'],
                   "postalCode": SITE['postal'], "addressCountry": "BR"},
       "geo": {"@type": "GeoCoordinates", "latitude": SITE['geo'][0], "longitude": SITE['geo'][1]}, "hasMap": MAPS,
       "areaServed": [{"@type": "Place", "name": n} for n in SITE['cities']]})

def crumbs(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + p} for i, (n, p) in enumerate([("Início", "/")] + items)]}

def ld(obj):
    return f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>'

# ---------------------------------------------------------------- página
SITEMAP = []

def page(canon, ttl, desc, body, *, current='', home=False, full_footer=False, og='/og-image.jpg', schema=(), noindex=False,
         og_type='website', extra_js='', dock=''):
    url = BASE + canon
    meta = [f'<title>{E(ttl)}</title>', f'<meta name="description" content="{E(desc)}">',
            f'<link rel="canonical" href="{BASE + ("/" if noindex else canon)}">',
            f'<meta property="og:title" content="{E(ttl)}"><meta property="og:description" content="{E(desc)}">',
            f'<meta property="og:type" content="{og_type}"><meta property="og:url" content="{url}"><meta property="og:locale" content="pt_BR"><meta property="og:site_name" content="Brandaz">',
            f'<meta property="og:image" content="{BASE + og}"><meta name="twitter:card" content="summary_large_image">',
            '<meta name="theme-color" content="#341131">']
    if noindex or PAGES:
        meta.append('<meta name="robots" content="noindex">')
    else:
        SITEMAP.append(canon)
    head_assets = (f'<link rel="icon" type="image/png" href="{U("/favicon.png")}"><link rel="apple-touch-icon" href="{U("/apple-touch-icon.png")}">'
                   f'<link rel="preload" href="{U("/assets/fonts/karibu-800.woff2")}" as="font" type="font/woff2" crossorigin>'
                   f'<link rel="preload" href="{U("/assets/fonts/karibu-400.woff2")}" as="font" type="font/woff2" crossorigin>'
                   f'<link rel="stylesheet" href="{U("/assets/css/site.css")}?v={CSS_V}">')
    wrapper_less = PREVIEW and out_file(canon) == 'index.html'  # a página principal da prévia recebe o esqueleto do publicador
    top = '' if wrapper_less else '<!doctype html>\n<html lang="pt-BR"><head>'
    doc = f'''{top}<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{chr(10).join(meta)}
{head_assets}
<script>document.documentElement.classList.add('js')</script>
{"".join(ld(s) for s in schema)}
{'' if wrapper_less else '</head><body>'}
{header(current, home)}
<main id="conteudo">
{body}
</main>
{footer(full_footer)}
<a class="float-wa" id="floatWa" href="{WA}" target="_blank" rel="noopener noreferrer" aria-label="Fale com a Brandaz pelo WhatsApp" tabindex="-1">{I_WA}</a>
{dock}
<script src="{U('/assets/js/site.js')}?v={JS_V}"></script>
{f"<script>{extra_js}</script>" if extra_js else ""}
{'' if wrapper_less else '</body></html>'}
'''
    # nenhum vídeo oferece "baixar", picture-in-picture ou transmissão
    doc = doc.replace('<video ', '<video controlslist="nodownload noremoteplayback" disablepictureinpicture disableremoteplayback ')
    path = os.path.join(OUT, out_file(canon))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(doc)

def cta_band(lbl, first, second, text, button, ch='Contato', paper=False, belt=False):
    row = case_row(PROJECTS, False, False) if belt else ''
    return f'''<section class="editorial-band cta-band{" bg-paper" if paper else " cinema-band"}{" with-belt" if belt else ""}" data-ch="{E(ch)}">
  <div class="editorial-container home-chapter-grid reveal"><div class="home-chapter-body">{label(lbl)}<div class="mt6">{title(first, second)}</div>{f'<p class="type-lead mt6 muted">{E(text)}</p>' if text else ''}</div>
  <div class="home-chapter-cta">{button}</div></div>{row}</section>'''

def method_path(steps, paper=True, tag='h3'):
    nodes = ''.join(f'<li class="method-node"><span class="method-dot" aria-hidden="true"></span><p class="num">{E(n)}</p><{tag}>{E(t)}</{tag}><p class="t">{E(d)}</p></li>' for n, t, d in steps)
    return (f'<div class="method-path" data-method><svg class="method-svg" aria-hidden="true"><path class="method-line-base"/><path class="method-line-active"/></svg>'
            f'<ol class="method-nodes">{nodes}</ol></div>')

def case_card(p, large):
    if large:
        cap = (f'<p class="cap-k">Case {p.get("caseNumber", "")} · {E(p["discipline"])}</p><h3 class="cap-l">{E(p["name"])}</h3>'
               f'<p class="cap-h">{E(p.get("highlight") or p["text"])}</p>')
    else:
        cap = f'<h3 class="cap-s">{E(p["name"])}</h3>'
    w, h = dims(p['image'])
    return (f'<a class="case-marquee-card" href="{U("/projetos/" + p["slug"] + "/")}" draggable="false"><img class="case-cover" src="{U(p["image"])}" alt="{E(p["name"])}"'
            f' width="{w}" height="{h}" loading="lazy" decoding="async" draggable="false"><div class="case-marquee-caption">{cap}</div></a>')

def case_row(items, large, pausable=True):
    cards = ''.join(case_card(p, large) for p in items)
    return (f'<div class="case-marquee-row {"is-large" if large else "is-small"}" data-speed="{-32 if large else 43}"{" data-pausable" if pausable else ""} aria-label="{"Cases em destaque" if large else "Mais projetos"}">'
            f'<div class="case-marquee-track"><div class="case-marquee-group">{cards}</div><div class="case-marquee-group" aria-hidden="true">{cards}</div></div></div>')

def client_items(rows=None):
    out = ''
    for key, name, slug in C['clients']:
        logo = f'<img class="client-marquee-logo" src="{U("/assets/img/clientes/" + key + ".webp")}" alt="{E(name)}" width="320" height="160" loading="lazy" decoding="async">'
        out += (f'<a class="client-marquee-item" href="{U("/projetos/" + slug + "/")}" title="{E(name)}">{logo}</a>' if slug
                else f'<span class="client-marquee-item">{logo}</span>')
    return out

def testimonials(cls='', book=False):
    """Depoimentos de clientes. Itens "modelo" só aparecem nas prévias, nunca no site oficial."""
    real = [d for d in DEP['depoimentos'] if d.get('texto') and not d.get('modelo')]
    items = real or ([d for d in DEP['depoimentos'] if d.get('modelo')] if RELATIVE else [])
    if not items:
        return ''
    cards = ''
    for i, d in enumerate(items):
        ini = ''.join(w[0] for w in d['nome'].split()[:2]).upper()
        foto = (f'<img class="t-photo" src="{U(d["foto"])}" alt="{E(d["nome"])}" width="112" height="112" loading="lazy" decoding="async">' if d.get('foto')
                else f'<span class="t-photo t-ini" aria-hidden="true">{E(ini)}</span>')
        role = ' · '.join(x for x in (d.get('cargo'), d.get('empresa')) if x)
        case = (f'<a class="t-case" href="{U("/projetos/" + d["case"] + "/")}">Ver o case {ARROW}</a>' if d.get('case') in BY_SLUG else '')
        tag = '<span class="t-tag">Espaço para depoimento</span>' if d.get('modelo') else ''
        cards += (f'<figure class="t-card{" modelo" if d.get("modelo") else ""}" data-reveal style="--d:{i * 110}ms">{tag}<div class="quoted">{QUOTE}<blockquote>{E(d["texto"])}</blockquote></div>'
                  f'<figcaption>{foto}<span><b>{E(d["nome"])}</b><small>{E(role)}</small></span></figcaption>{case}</figure>')
    return f'''<section class="editorial-band testimonials {cls}" data-ch="Depoimentos"{' data-shape="book"' if book else ''} aria-labelledby="dep-title"><div class="editorial-container">
  <div class="t-head"><div><div id="dep-title">{title(*DEP['titulo'])}</div><p class="type-lead muted mt6 measure">{E(DEP['texto'])}</p></div>
    {f'<i class="dust-anchor book" aria-hidden="true"><b class="dust-cap">{E(DEP["legenda"])}</b></i>' if book else ''}</div>
  <div class="t-grid">{cards}</div>
</div></section>'''

FEATURED = [BY_SLUG[s] for s in C['transformamos']['caseSlugs']]
OTHERS = [p for p in PROJECTS if p['slug'] not in C['transformamos']['caseSlugs']]

# ================================================================ HOME (capas A e B)
F90 = "Filme · 90 Graus Móveis sob Medida"
SLIDES = [("filmA", 0, 7.6, F90), ("benefatto_kv", None, None, "Case · Benefatto"), ("nexo_logo", None, None, "Case · Nexo Contábil"),
          ("filmB", 0, 7.6, F90), ("fimano_h", None, None, "Case · Royal — Super Fim de Ano"), ("bpo_logo", None, None, "Case · Nosso BPO"),
          ("filmC", 0, 7.6, F90), ("nicos_quiosque", None, None, "Case · Nico's Soft Cream"), ("rc_logo", None, None, "Case · RC Investimentos Imobiliários"),
          ("black_logo", None, None, "Case · Royal — Black Friday"), ("solvitas_logo", None, None, "Case · Solvitas Cursos"),
          ("criancas25_kv", None, None, "Case · Royal — Dia das Crianças"), ("oeste_logo", None, None, "Case · Oeste Home Imobiliária")]
H = lambda f: U('/assets/home/' + f)
HERO_A = ('<div class="projection-hero" aria-hidden="true"><div class="reel-show" id="show">'
          f'<video class="hero-film on" id="filmA" src="{H("hero-90-graus-a.mp4")}" poster="{H("hero-90-graus.jpg")}" autoplay muted playsinline preload="auto"></video>'
          f'<video class="hero-film" id="filmB" src="{H("hero-90-graus-b.mp4")}" muted playsinline preload="auto"></video>'
          f'<video class="hero-film" id="filmC" src="{H("hero-90-graus-c.mp4")}" muted playsinline preload="auto"></video>'
          + ''.join(f'<img src="{H("slide-" + n + ".webp")}" alt="" decoding="async">' for n, a, b, c in SLIDES if not n.startswith('film')) +
          '</div><div class="projection-gradient"></div><div class="hero-bottom"></div></div>'
          '<div class="credit-bar" aria-hidden="true"><div class="ticks" id="ticks">' + ''.join('<i><b></b></i>' for _ in SLIDES) + f'</div><p class="film-credit" id="credit">{F90}</p></div>')
FILMS = C['films']
WALL_KEYS = ["croissants", "biscoitos", "cafes-carraro", "cachaca", "inverno", "cuca", "dia-das-maes", "franui", "garibaldi", "granolas", "pratos-prontos"]
COVER = 'B'  # capa da home: 'B' = parede de filmes verticais (aprovada) · 'A' = filme horizontal da 90 Graus + cases
WALL_POSTERS = True
WALL = ''.join(f'<figure class="wf"><video src="{H("wall-" + k + ".mp4")}"{" poster=" + chr(34) + H("wall-" + k + ".jpg") + chr(34) if WALL_POSTERS else ""} muted loop playsinline preload="metadata"></video></figure>' for k in WALL_KEYS)
HERO_B = ('<div class="projection-hero" aria-hidden="true"><div class="wall"><div class="wtrack">' + WALL + WALL + '</div></div>'
          '<div class="projection-gradient"></div><div class="hero-bottom"></div></div>')

def hero_title(first, second):
    """Título da capa em caixa alta; a palavra "magia" ganha brilho e faíscas."""
    stars = ''.join(f'<i style="--x:{x}%;--y:{y}%;--s:{z}px;--t:{t}s"></i>' for x, y, z, t in
                    [(-8, 14, 22, 0), (106, 4, 28, .7), (90, 96, 18, 1.3), (32, -16, 16, 1.9), (58, 108, 20, .4), (114, 62, 14, 2.4), (-12, 80, 14, 1.1), (72, -10, 12, 1.6)])
    l2 = re.sub(r'magia', lambda m: f'<span class="magic">{m.group(0)}<span class="sparks" aria-hidden="true">{stars}</span></span>', E(second), flags=re.I)
    return (f'<h1 class="editorial-title editorial-title-hero up" aria-label="{E(first)} {E(second)}"><span class="ln"><span class="l1">{E(first)}</span></span>'
            f'<span class="ln"><span class="l2">{l2}</span></span></h1>')

def home(variant):
    h = C['home']
    films = ''
    by_name = {p['name']: p['slug'] for p in PROJECTS}
    for f in FILMS:
        vert = '' if f['preview'] == '90-graus' else ' data-vertical'
        wide = ' wide' if not vert else ''  # o filme horizontal ganha box 16:9 na mesma altura dos verticais
        client = by_name.get(f['client'], f['slug'])
        films += (f'<div class="cinema-reel-link{wide}">'
                  f'<button type="button" class="cinema-reel" data-lb="filmes" data-type="video" data-src="{U(f["full"])}" data-poster="{U("/assets/preview/loop-" + f["preview"] + ".jpg")}"{vert} data-cap="{E(f["client"])} · {E(f["name"])}" aria-label="Assistir {E(f["name"])}">'
                  f'<video src="{U("/assets/preview/loop-" + f["preview"] + ".mp4")}" poster="{U("/assets/preview/loop-" + f["preview"] + ".jpg")}" muted loop playsinline preload="metadata"></video>'
                  f'{I_PLAY.replace(chr(34) + "ic" + chr(34), chr(34) + "ic cinema-reel-play" + chr(34))}</button>'
                  f'<p class="film-title"><span>Filme:</span> {E(f.get("title", f["name"]))}</p><a class="film-client" href="{U("/projetos/" + client + "/")}">{E(f["client"])} {ARROW}</a></div>')
    specs = ''.join(f'<li><i class="node" aria-hidden="true"></i><span class="text-accent">{n}</span> {E(t)}</li>' for n, t, d in C['especialidades']['items'])
    clients = client_items()
    dock = '<div class="dock"><button type="button" id="mot" class="mot" aria-pressed="false">Pausar movimento</button></div>'
    body = f'''<canvas id="dust" aria-hidden="true" data-mark="{U('/assets/site/mark-clean.png')}"></canvas>
<section class="v3-hero projection-cover" data-ch="Início" data-shape="none">
{HERO_A if variant == 'A' else HERO_B}
  <div class="v3-hero-content">
    <img class="hero-logo" src="{U('/assets/site/logo-brandaz.png')}" alt="Brandaz" width="600" height="300">
    {hero_title(*h['hero'])}
    <p class="lead type-body">{E(h['lead'])}</p>
    <div class="hero-buttons">{btn("Sobre a Brandaz", "/brandaz/")}{btn("Conheça nosso Portfólio", "/projetos/")}</div>
  </div>
</section>

<section id="brandaz" class="editorial-band home-chapter cinema-band" data-ch="A Brandaz" data-shape="20">
  <div class="editorial-container home-chapter-grid reveal">
    <div class="home-chapter-body">{words(h['statement'], 'home-manifesto')}
      <p class="type-body mt6">{E(h['about'])}</p></div>
    <div class="home-chapter-cta"><i class="dust-anchor num" aria-hidden="true"><b class="dust-cap">anos</b></i>{btn("Conheça a Brandaz", "/brandaz/")}</div>
  </div>
</section>

<section id="cases" class="case-marquee-section" aria-label="Estratégia que ganha forma" data-ch="Cases" data-shape="growth">
  <div class="editorial-container cm-head">
    <div>{title(*C['transformamos']['title'])}
      <p class="type-body muted mt5">Conheça projetos que mostram a criatividade e a diversidade da nossa atuação.</p></div>
    <div class="cm-right"><i class="dust-anchor" aria-hidden="true"></i><button type="button" class="btn icon" data-slot="button" id="casePause" aria-pressed="false" aria-label="Pausar esteira de cases" data-play="{E(I_PLAY)}" data-pause="{E(I_PAUSE)}">{I_PAUSE}</button></div>
  </div>
  {case_row(FEATURED, True)}
  {case_row(OTHERS, False)}
  <div class="editorial-container mt8">{btn("Ver portfólio completo", "/projetos/")}</div>
</section>

<section id="filmes" class="editorial-band cinema-band films-band" aria-labelledby="our-films-title" data-ch="Filmes" data-shape="play">
  <div class="editorial-container films-head"><h2 id="our-films-title" class="editorial-title up xb"><span class="ln"><span class="l1">Nossos <span class="text-accent">filmes</span></span></span></h2><i class="dust-anchor" aria-hidden="true"></i></div>
  <div class="belt films-belt" data-speed="-46" aria-label="Nossos filmes"><div class="belt-track"><div class="belt-group">{films}</div><div class="belt-group" aria-hidden="true">{films}</div></div></div>
  <div class="editorial-container">{btn("Ver portfólio completo", "/projetos/", "mt12")}</div>
</section>

<section id="servicos" class="home-chapter cinema-band spec-pin" data-ch="Especialidades" data-shape="flow">
  <div class="spec-stick"><div class="editorial-container home-chapter-grid reveal">
    <div class="home-chapter-body">{title("O que fazemos", "Da ideia à execução")}
      <div class="spec-wrap"><svg class="spec-road" id="road" aria-hidden="true"><defs><mask id="done"><path id="mpath" fill="none" stroke="#fff" stroke-width="30"/></mask></defs><path id="ahead" fill="none"/><path id="trail" fill="none" mask="url(#done)"/></svg><i class="orb" id="orb" aria-hidden="true"></i>
      <ol class="home-specialties" id="specs">{specs}</ol></div></div>
    <div class="home-chapter-cta spec-cta">{btn("Conheça nossos serviços", "/servicos/")}</div>
  </div></div>
</section>

<section class="editorial-band home-chapter cinema-band" id="clientes" data-ch="Clientes" data-shape="stars">
  <div class="editorial-container home-chapter-grid reveal">
    <div class="home-chapter-body">{title(*C['marcas']['title'])}
      <p class="type-lead muted mt6">{accent(C['marcas']['text'])}</p></div>
    <div class="home-chapter-cta"><i class="dust-anchor stars" aria-hidden="true"><b class="dust-cap">{E(C['marcas']['caption'])}</b></i>{btn("Ver portfólio completo", "/projetos/")}</div>
  </div>
  <!-- duas fileiras de ponta a ponta, como no Portfólio, em ritmo mais lento para cada marca ser reconhecida -->
  <div class="client-marquee home-brands" aria-label="Marcas atendidas pela Brandaz">
    <div class="client-marquee-row"><div class="client-marquee-track" data-shuffle>{clients}{clients}</div></div>
    <div class="client-marquee-row"><div class="client-marquee-track rev" data-shuffle>{clients}{clients}</div></div>
  </div>
</section>

{testimonials('cinema-band', book=True)}

<section id="contato" class="editorial-band home-chapter cinema-band" data-ch="Contato" data-shape="mark">
  <div class="editorial-container home-chapter-grid reveal">
    <div class="home-chapter-body">{title(*C['contato']['title'])}
      <p class="type-body muted mt7">Conte para a gente o que sua marca precisa. Estamos prontos para conversar.</p>
      <div class="contact-links"><a class="b" href="{WA}" target="_blank" rel="noopener noreferrer">{I_WA}WhatsApp · {SITE['phone']['display']}</a><a href="mailto:{SITE['email']}">{I_MAIL}{SITE['email']}</a><a href="{SITE['instagram']['url']}" target="_blank" rel="noreferrer">{I_IG}Instagram · {SITE['instagram']['handle']}</a></div></div>
    <div class="home-chapter-cta"><i class="dust-anchor" aria-hidden="true"></i>{btn("Falar com a Brandaz", WA, ext=True)}<a class="btn ghost mt4" data-slot="button" href="{U('/contato/')}">Outras formas de contato {ARROW}</a></div>
  </div>
</section>'''
    js = HOME + (COVER_A.replace('__SLIDES__', json.dumps([list(x) for x in SLIDES], ensure_ascii=False)) if variant == 'A' else COVER_B)
    page('/', h['title'], h['description'], body, current='/', home=True,
         schema=[{"@context": "https://schema.org", "@graph": [ORG, PRO]}, crumbs([])], extra_js=js, dock=dock)

# ================================================================ A BRANDAZ
def brandaz():
    hi, ev, li, pr, ca = C['historia'], C['evolucao'], C['lider'], C['proposito'], C['caminho']
    stats = ''.join(f'<div class="stat {"a" if i == 0 else "b"}" data-reveal style="--d:{i * 120}ms"><p class="n" data-count="{E(n)}">{E(n)}</p><p class="t">{E(t)}</p>'
                    f'{btn("Conheça esse case", "/projetos/supermercado-royal/") if i == 1 else ""}</div>' for i, (n, t) in enumerate(hi['stats']))
    office = ''.join(f'<button type="button" class="office-portal" data-lb="escritorio" data-type="image" data-src="{U(s)}" data-cap="{E(a)}" aria-label="Ampliar foto: {E(a)}">{img(s, a)}</button>' for s, a in ev['office'])
    diffs = ''.join(f'<div class="diff{" hot" if i == 5 else ""}" data-reveal style="--d:{i * 80}ms">{svg(DIFF_ICONS[i], "ic6", extra=LINE)}<h3>{E(t)}</h3><p>{E(d)}</p></div>' for i, (t, d) in enumerate(pr['differentials']))
    checks = ''.join(f'<li>{I_CHECK}<span>{E(c)}</span></li>' for c in pr['checks'])
    body = f'''
<section class="editorial-opening bg-paper" data-ch="Nossa história"><div class="editorial-container two-col a">
  <div>{label("A Brandaz")}<div class="mt6">{title(*hi['title'], tag='h1')}</div>
    {''.join(f'<p class="type-lead mt6 paper-muted">{E(p)}</p>' for p in hi['paragraphs'])}
    <p class="type-h3 mt8"><strong>{E(hi['closing'][0])}</strong><br><span class="fw3">{E(hi['closing'][1])}</span></p></div>
  <div class="stats-wrap self-center"><img class="stats-mark" src="{U('/assets/site/mark-clean.png')}" alt="" width="230" height="380" aria-hidden="true"><div class="stats">{stats}</div></div>
</div></section>

<section class="editorial-band bg-accent" data-ch="Nova forma de enxergar"><div class="editorial-container">
  {words(C['scrub'], 'scrub-phrase scrub fw8')}
</div></section>

<section class="editorial-band cinema-band" data-ch="Nossa evolução"><div class="editorial-container two-col">
  <div>{label(ev['label'])}<div class="mt6">{title(*ev['title'])}</div></div>
  <div class="self-end"><p class="type-lead muted">{E(ev['text'])}</p><p class="chips">{''.join(f'<span class="{"on" if i == 0 else ""}">{E(c)}</span>' for i, c in enumerate(ev['chips']))}</p></div>
</div>
<div class="belt office-belt mt12" data-speed="-28" aria-label="Fotos do novo espaço"><div class="belt-track"><div class="belt-group">{office}</div><div class="belt-group" aria-hidden="true">{office}</div></div></div>
</section>

<section class="editorial-band bg-paper" data-ch="Liderança"><div class="editorial-container two-col b">
  <div data-reveal>{img(li['image'], li['name'] + ', ' + li['role'] + ' da Brandaz', 'diego-photo')}</div>
  <div class="self-center"><h2 class="type-h2 fw8">{E(li['name'])}</h2><p class="type-label mt3 accent-dark">{E(li['role'])}</p>
    <p class="type-lead mt6 paper-muted">{E(li['bio'])}</p><div class="quoted big mt10">{QUOTE}<blockquote class="big-quote">{E(li['quote'])}</blockquote></div></div>
</div></section>

<section class="editorial-band cinema-band" data-ch="O que nos move"><div class="editorial-container two-col">
  <div>{label(pr['label'])}<div class="mt6">{title(*pr['title'])}</div><p class="type-lead muted mt6">{E(pr['text'])}</p><ul class="checks mt6">{checks}</ul></div>
  <div>{label(pr['differentialsLabel'])}<div class="diffs-wrap"><div class="magic-bg" aria-hidden="true"><i></i><i></i><i></i></div><div class="diffs">{diffs}</div></div></div>
</div></section>

<section class="editorial-band bg-paper" data-ch="Como trabalhamos"><div class="editorial-container">
  {label(ca['label'])}<div class="mt6">{title(*ca['title'])}</div><p class="type-lead paper-muted mt6 measure">{E(ca['text'])}</p>
  {method_path(ca['steps'])}
  <div class="mt12">{btn("Entenda nosso processo", "/como-trabalhamos/")}</div>
</div></section>

{cta_band("Portfólio", "Ideias que", "ganharam forma.", "Conheça projetos de branding, campanhas, conteúdo e audiovisual que desenvolvemos ao lado de nossos clientes.", btn("Ver portfólio", "/projetos/"), "Portfólio", belt=True)}
{cta_band("Vamos conversar", "Qual é o próximo desafio", "da sua marca?", "Conte para a gente. Estamos prontos para conversar.", btn("Falar no WhatsApp", WA, ext=True), "Contato")}'''
    page('/brandaz/', 'A Brandaz | Mais de 20 anos de comunicação em Chapecó',
         'Conheça a Brandaz: mais de 20 anos de história, marcas e conexões em Chapecó. Novo espaço, nova equipe e o mesmo propósito: criatividade com estratégia e resultado.',
         body, current='/brandaz/', schema=[{"@context": "https://schema.org", "@type": "AboutPage", "url": BASE + "/brandaz/", "about": {"@id": f"{BASE}/#organization"}}, crumbs([("A Brandaz", "/brandaz/")])])

# ================================================================ COMO TRABALHAMOS
def como():
    ca = C['caminho']
    flow = ''.join(f'<div data-reveal style="--d:{i * 90}ms"><span class="n">{i + 1:02d}</span><div><dt>{E(t)}</dt><dd>{E(d)}</dd></div></div>' for i, (t, d) in enumerate([
        ("Desafio", "Entendemos o negócio, o mercado, o público e o momento da marca antes de propor qualquer solução."),
        ("Estratégia", "Definimos objetivos, posicionamento, canais e indicadores que vão guiar o projeto."),
        ("Ideia", "Transformamos a estratégia em conceito criativo, identidade e narrativa."),
        ("Execução", "Produzimos, publicamos e acompanhamos cada entrega com atenção aos detalhes."),
        ("Resultado", "Medimos o desempenho, aprendemos com os dados e evoluímos a cada ciclo.")]))
    specs = ''.join(f'<li><a href="{U("/servicos/#" + s["id"])}"><span class="text-accent">{i + 1:02d}</span> {E(s["title"])} <span class="arr">{ARROW}</span></a></li>' for i, s in enumerate(C['services']))
    body = f'''
<section class="editorial-opening bg-paper" data-ch="O caminho"><div class="editorial-container">
  {label(ca['label'])}<div class="mt6">{title("Toda grande ideia", "precisa de um caminho.", tag='h1')}</div>
  <p class="type-lead paper-muted mt6 measure">{E(ca['text'])}</p>
  {method_path(ca['steps'], tag='h2')}
</div></section>

<section class="editorial-band cinema-band" data-ch="Do desafio ao resultado"><div class="editorial-container two-col">
  <div>{label(C['transformamos']['caseFlowLabel'])}<div class="mt6">{title("Método claro,", "entregas consistentes.")}</div>
    <p class="type-lead muted mt6">Cada etapa conecta a anterior à próxima. É assim que a estratégia vira ideia e a ideia vira resultado mensurável.</p></div>
  <div class="flow"><dl>{flow}</dl></div>
</div></section>

<section class="editorial-band" data-ch="Especialidades"><div class="editorial-container two-col">
  <div>{label(C['especialidades']['label'])}<div class="mt6">{title(*C['especialidades']['title'])}</div></div>
  <ol class="svc-links">{specs}</ol>
</div></section>

{cta_band("Vamos conversar", "Qual é o próximo desafio", "da sua marca?", "", btn("Falar no WhatsApp", WA, ext=True), "Contato")}'''
    page('/como-trabalhamos/', 'Como trabalhamos | Estratégia e criatividade em Chapecó – Brandaz',
         'Do desafio ao resultado: entender, planejar, criar, executar e evoluir. Conheça o método da Brandaz para projetos de marketing, branding e comunicação em Chapecó.',
         body, current='/como-trabalhamos/', schema=[crumbs([("Como trabalhamos", "/como-trabalhamos/")])])

# ================================================================ SERVIÇOS
def related_for(scopes, n=2):
    want = {s.lower() for s in scopes}
    return [p for p in PROJECTS if want & {s.lower() for s in p['scope']}][:n]

def servicos():
    a = C['aaz']
    letters = ''.join(f'<div class="service-letter-item" data-reveal style="--d:{i * 90}ms"><span class="services-letter">{L}</span><p>{E(t)}</p></div>' for i, (L, t) in enumerate(a['letters']))
    letters += ('<div class="service-letter-item z" data-reveal style="--d:450ms"><span class="services-letter"><span class="dots" aria-hidden="true"><i></i><i></i><i></i></span>'
                '<span class="zl" data-run="FGHIJKLMNOPQRSTUVWXYZ">Z</span></span><p>Do insight ao último detalhe</p></div>')
    items = ''
    for i, s in enumerate(C['services']):
        rel = ''.join(f'<a href="{U("/projetos/" + p["slug"] + "/")}">{img(p["image"], p["name"])}<h4>{E(p["name"])}</h4><p>{E(p["segment"])}</p></a>' for p in related_for(s['scopes']))
        items += f'''<details class="service-expand" id="{s['id']}"{" open" if i == 0 else ""}><summary><span class="n">{i + 1:02d}</span><h3>{E(s['title'])}</h3></summary>
  <div class="svc-body"><div class="txt"><p class="type-label text-accent">Entregas</p><p class="mt3">{E(s['deliverables'])}</p><p class="muted">{E(s['description'])}</p>
    <div class="mt6">{btn("Conheça nossos projetos", "/projetos/", "ghost")}</div></div>
  <div><p class="type-label muted">Projetos relacionados</p><div class="related">{rel}</div></div></div></details>'''
    body = f'''
<section class="editorial-opening cinema-band" data-ch="De A a Z"><div class="editorial-container two-col">
  <div>{label(a['label'])}<div class="mt6">{title(*a['title'], tag='h1')}</div><p class="type-lead muted mt6">{E(a['text'])}</p>
    <p class="type-h3 mt8 fw3">{accent(a['closing'])}</p></div>
  <div class="services-letters" data-az>{letters}</div>
</div></section>

<section class="editorial-band bg-paper svc-band" data-ch="Especialidades"><div class="editorial-container">
  {label(C['especialidades']['label'])}<div class="mt6">{title(*C['especialidades']['title'])}</div>
  <div class="mt12">{items}</div>
</div></section>

{cta_band("Vamos conversar", "Qual solução", "sua marca precisa?", "Conte o seu desafio e montamos o caminho com você.", btn("Falar no WhatsApp", WA, ext=True), "Contato")}'''
    svc = {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "item": {"@type": "Service", "name": s['title'], "description": s['description'], "serviceType": s['deliverables'],
                                                          "provider": {"@id": f"{BASE}/#agency"}, "areaServed": SITE['cities']}} for i, s in enumerate(C['services'])]}
    page('/servicos/', 'Serviços de Marketing, Branding e Publicidade em Chapecó | Brandaz',
         'Estratégia, branding, campanhas, conteúdo e audiovisual, tráfego pago, sites e comunicação institucional. A Brandaz é uma agência de A a Z em Chapecó e no Oeste de SC.',
         body, current='/servicos/', schema=[svc, crumbs([("Serviços", "/servicos/")])])

# ================================================================ PORTFÓLIO
def result_block(p, prefix=''):
    if not p.get('metrics'):
        return ''
    ms = ''.join(f'<div><p class="result-number" data-count="{E(m["value"])}">{E(m["value"])}</p><p>{E(m["label"])}</p></div>' for m in p['metrics'])
    per = f' · {E(p["metricsPeriod"])}' if p.get('metricsPeriod') else ''
    note = f'<p class="note">{E(p["metricsNote"])}</p>' if p.get('metricsNote') else ''
    return f'<div class="result-block"><p class="k">{prefix}Resultado{per}</p><div class="result-metrics">{ms}</div>{note}</div>'

def norm_scope(s):
    return {'social media': 'Social Media', 'campanhas': 'Campanha'}.get(s.lower(), s)

def projetos():
    feats = ''
    for i, p in enumerate(FEATURED):
        feats += f'''<article class="group glass" data-reveal style="--d:{(i % 2) * 120}ms"><a href="{U("/projetos/" + p["slug"] + "/")}" class="project-media">{img(p["image"], p["name"], "case-cover")}<span class="see">Ver case →</span></a>
  <div><p class="cap-k">Case {p["caseNumber"]} · {E(p["discipline"])}</p><h2><a href="{U("/projetos/" + p["slug"] + "/")}">{E(p["name"])}</a></h2><p class="type-body muted mt3">{E(p["tagline"])}</p></div>
  {result_block(p) or f'<p class="type-h3 fw3 text-accent">{E(p["highlight"])}</p>'}</article>'''
    segs = sorted({p['segment'] for p in PROJECTS})
    scopes = sorted({norm_scope(s) for p in PROJECTS for s in p['scope']})
    grid = ''
    for p in PROJECTS:
        sc = [norm_scope(s) for s in p['scope']]
        tags = ''.join(f'<span>{E(s)}</span>' for s in p['scope'][:2])
        grid += f'''<article class="proj-item group" data-seg="{E(p["segment"])}" data-scopes="{E("|".join(sc))}"><a href="{U("/projetos/" + p["slug"] + "/")}">
  <div class="project-media">{img(p["image"], p["name"], "case-cover")}<span class="see">Ver case →</span></div>
  <div class="pi-body"><p class="seg type-label">{E(p["segment"])}</p><h2>{E(p["name"])} <small>{E(p["year"])}</small></h2><p class="txt">{E(p["text"])}</p><div class="tags">{tags}</div></div></a></article>'''
    rows = client_items()
    body = f'''
<section class="page-top bg-paper port-top" data-ch="Portfólio"><div class="wrap-1500">
  {label("Portfólio")}<div class="mt6">{title(*C['transformamos']['title'], tag='h1')}</div>
  <p class="type-lead paper-muted mt6 measure">Conheça projetos que mostram a criatividade e a diversidade da nossa atuação: branding, campanhas, conteúdo, audiovisual e mídia para marcas de Chapecó e do Oeste catarinense.</p>
  <p class="section-label mt16">Marcas que fazem parte da nossa história</p></div>
  <div class="client-marquee"><div class="client-marquee-row"><div class="client-marquee-track">{rows}{rows}</div></div><div class="client-marquee-row"><div class="client-marquee-track rev">{rows}{rows}</div></div></div>
</section>

<section class="editorial-band cases-band" data-ch="Cases"><div class="wrap-1500">{title("Cases de marketing e publicidade", "em Chapecó e no Oeste catarinense")}
  <div class="featured-cases">{feats}</div>
</div></section>

<section class="editorial-band more-band" data-ch="Mais projetos"><div class="wrap-1500">
  <p class="section-label">Mais projetos</p>
  <div class="proj-tools"><label class="type-label muted" for="segSel">Segmento</label><select class="select" id="segSel"><option value="">Todos os segmentos</option>{''.join(f'<option>{E(s)}</option>' for s in segs)}</select></div>
  <div class="filters" role="group" aria-label="Filtrar por escopo"><button type="button" data-scope="" aria-pressed="true">Todos</button>{''.join(f'<button type="button" data-scope="{E(s)}" aria-pressed="false">{E(s)}</button>' for s in scopes)}</div>
  <p class="type-label muted mt6" id="projCount" aria-live="polite"></p>
  <div class="project-grid" id="projGrid">{grid}<div class="load-more"><button type="button" class="btn" id="loadMore">Carregar mais</button></div></div>
</div></section>

{testimonials('tight')}

{cta_band("Vamos conversar", "Sua marca pode ser", "nosso próximo case.", "", btn("Falar no WhatsApp", WA, ext=True), "Contato")}'''
    lst = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Portfólio Brandaz", "url": BASE + "/projetos/",
           "hasPart": [{"@type": "CreativeWork", "name": p['name'], "url": f"{BASE}/projetos/{p['slug']}/"} for p in PROJECTS]}
    page('/projetos/', 'Portfólio e Cases | Brandaz – Agência em Chapecó',
         'Cases de branding, campanhas, conteúdo, audiovisual e mídia da Brandaz: Supermercado Royal, Marlos Campos Concursos, Hospital Regional do Oeste, Melira Films e mais.',
         body, current='/projetos/', schema=[lst, crumbs([("Portfólio", "/projetos/")])])

def gallery(p):
    rows = ''
    for row in p['gallery']:
        items = ''
        for it in row:
            w, h = it.get('width', 1600), it.get('height', 1200)
            if it['type'] == 'video':
                items += (f'<button type="button" class="g-item" style="flex-grow:{w / h:.4f};aspect-ratio:{w}/{h}" data-lb="galeria" data-type="video" data-src="{U(it["src"])}" data-poster="{U(it.get("poster", ""))}"'
                          f'{" data-vertical" if h > w else ""} data-cap="{E(it.get("alt", ""))}" aria-label="Assistir: {E(it.get("alt", ""))}">'
                          f'<img src="{U(it.get("poster", ""))}" alt="" width="{w}" height="{h}" loading="lazy" decoding="async"><span class="playb"><span>{I_PLAY}</span></span></button>')
            else:
                items += (f'<button type="button" class="g-item" style="flex-grow:{w / h:.4f};aspect-ratio:{w}/{h}" data-lb="galeria" data-type="image" data-src="{U(it["src"])}" data-cap="{E(it.get("alt", ""))}" aria-label="Ampliar: {E(it.get("alt", ""))}">'
                          f'<img src="{U(it["src"])}" alt="{E(it.get("alt", ""))}" width="{w}" height="{h}" loading="lazy" decoding="async"></button>')
        rows += f'<div class="g-row{" pair" if len(row) == 2 else ""}" data-reveal>{items}</div>'
    return rows

def case_page(i, p):
    slug = f'/projetos/{p["slug"]}/'
    imgs = [it for row in p['gallery'] for it in row if it['type'] == 'image']
    ex = imgs[:2]
    steps = [(n, p.get(k, '')) for n, k in C['method'] if p.get(k)]
    if p.get('caseNumber'):  # cases da apresentação (V3)
        flow = ''.join(f'<div><span class="n">{j + 1:02d}</span><div><dt>{E(n)}</dt><dd>{E(t)}</dd></div></div>' for j, (n, t) in enumerate(steps))
        exs = ''.join(f'<img src="{U(it["src"])}" alt="{E(it.get("alt", ""))}" width="{it["width"]}" height="{it["height"]}" loading="lazy" decoding="async">' for it in ex)
        top = f'''<div class="slide-label" data-deck><div class="row"><p><span class="dot"></span>Case {p["caseNumber"]} · {E(p["discipline"])}</p><p class="num">{p["caseNumber"]} / {len(FEATURED):02d}</p></div><div class="deck-line"></div></div>
  <h1 class="deck-title type-h1" data-deck><span class="deck-title-line"><span class="b" style="--i:0">{E(p["name"])}</span></span><span class="deck-title-line"><span class="l" style="--i:1">{E(p["tagline"])}</span></span></h1>
  {f'<p class="type-lead muted mt6 measure">{E(p["statement"])}</p>' if p.get("statement") else ""}
  <div class="v3-grid"><div><div class="v3-imgs">{img(p["hero"], p["name"], "wide", lazy=False)}{exs}</div></div>
    <div><div class="flow"><p class="type-label text-accent">{E(C["transformamos"]["caseFlowLabel"])}</p><dl class="mt4">{flow}</dl></div>
    <div class="mt8">{result_block(p, "05 · ")}</div></div></div>'''
    else:
        rows = ''.join(f'<li class="deck-row" style="--i:{j}"><span class="n">{j + 1:02d}</span><span class="t">{E(n)}</span><span class="d">{E(t)}</span></li>' for j, (n, t) in enumerate(steps))
        exs = ''.join(f'<img class="ex" src="{U(it["src"])}" alt="{E(it.get("alt", ""))}" width="{it["width"]}" height="{it["height"]}" loading="lazy" decoding="async">' for it in ex)
        top = f'''<div class="slide-label" data-deck><div class="row"><p><span class="dot"></span>Case {i + 1:02d}</p><p class="num">{i + 1:02d} / {len(PROJECTS):02d}</p></div><div class="deck-line"></div></div>
  <h1 class="deck-title type-h1" data-deck><span class="deck-title-line"><span class="b" style="--i:0">{E(p["client"] if p["client"] != p["name"] else p["name"])}</span></span><span class="deck-title-line"><span class="l" style="--i:1">{E(p["tagline"])}</span></span></h1>
  <div class="case-grid"><div class="case-imgs">{img(p["image"], p["name"], "main case-cover", lazy=False)}{exs}</div>
    <div class="num-table" data-deck><p class="h">{E(C["transformamos"]["caseFlowLabel"])}</p><ol>{rows}</ol></div></div>'''
    deliv = '' if p.get('metrics') else f'<div class="bar"></div><p class="lbl mt6">Entregas</p><ul class="deliv">{"".join(f"<li>{E(r)}</li>" for r in p.get("results", []))}</ul>'
    nxt = PROJECTS[(i + 1) % len(PROJECTS)]
    body = f'''
<section class="case-top" data-ch="{E(p['name'])}">
  <a class="back" href="{U('/projetos/')}">{BACK} Portfólio</a>
  {top}
</section>

<section class="bg-paper" data-ch="O projeto"><div class="case-about">
  <div><p class="lbl">O projeto</p><p class="type-h3 fw3 mt6">{E(p.get("intro", ""))}</p><p class="type-body paper-muted mt6">{E(p.get("text", ""))}</p></div>
  <div><dl><div><dt>Cliente</dt><dd>{E(p["client"])}</dd></div><div><dt>Ano</dt><dd>{E(p["year"])}</dd></div><div><dt>Segmento</dt><dd>{E(p["segment"])}</dd></div><div><dt>Escopo</dt><dd>{E(", ".join(p["scope"]))}</dd></div></dl>{deliv}</div>
</div></section>

<section class="editorial-band" data-ch="Galeria"><div class="wrap-1500"><p class="section-label">Galeria</p><div class="gallery mt10">{gallery(p)}</div>
  <a class="next-case group" href="{U("/projetos/" + nxt["slug"] + "/")}"><p class="type-label text-accent">Próximo case →</p><div class="img mt4">{img(nxt["image"], nxt["name"], "case-cover")}</div><h3 class="type-h2">{E(nxt["name"])}</h3><p>{E(nxt["tagline"])}</p></a>
</div></section>

<section class="case-marquee-section" data-ch="Mais cases"><div class="editorial-container cm-head"><div>{label("Mais cases")}<h2 class="type-h2 fw8 mt4">Outras histórias que ajudamos a contar.</h2></div></div>
  {case_row([x for x in PROJECTS if x['slug'] != p['slug']], False, False)}
</section>'''
    work = {"@context": "https://schema.org", "@type": "CreativeWork", "name": p['name'], "headline": p['tagline'], "description": p.get('intro') or p['text'],
            "url": BASE + slug, "image": BASE + p['image'], "creator": {"@id": f"{BASE}/#organization"}, "about": p['client'], "keywords": ", ".join(p['scope'])}
    page(slug, f'{p["name"]} — Case de {p["scope"][0]} | Brandaz Chapecó', (p.get('intro') or p['text'])[:300], body, current='/projetos/',
         full_footer=True, og=f'/share/{p["slug"]}.jpg', og_type='article', schema=[work, crumbs([("Portfólio", "/projetos/"), (p['name'], slug)])])

# ================================================================ BLOG
def post_card(b, cls=''):
    return (f'<a class="post-card {cls}" href="{U("/blog/" + b["slug"] + "/")}" data-cat="{E(b["category"])}"><div class="img">{img(b["cover"], b["coverAlt"])}</div>'
            f'<p class="type-label k">{E(b["category"])} · {date_br(b["date"])}</p><h3 class="type-h3">{E(b["title"])}</h3><p class="muted mt3">{E(b["description"])}</p></a>')

def blog():
    cats = sorted({b['category'] for b in POSTS})
    body = f'''
<section class="page-top" data-ch="Blog"><div class="wrap-1500">
  {label("Blog")}<div class="mt6">{title("Ideias em", "movimento.", tag='h1')}</div>
  <p class="type-lead muted mt6 measure">Marketing, branding e comunicação a partir de Chapecó: bastidores, método e aprendizados dos nossos projetos.</p>
  <div class="cat-buttons filters" role="group" aria-label="Filtrar por categoria"><button type="button" data-cat-btn="" aria-pressed="true">Todos</button>{''.join(f'<button type="button" data-cat-btn="{E(c)}" aria-pressed="false">{E(c)}</button>' for c in cats)}</div>
  <div class="post-grid">{''.join(post_card(b) for b in POSTS)}</div>
</div></section>
<div class="spacer"></div>'''
    blogld = {"@context": "https://schema.org", "@type": "Blog", "name": "Blog Brandaz", "url": BASE + "/blog/", "publisher": {"@id": f"{BASE}/#organization"},
              "blogPost": [{"@type": "BlogPosting", "headline": b['title'], "url": f"{BASE}/blog/{b['slug']}/", "datePublished": b['date']} for b in POSTS]}
    page('/blog/', 'Blog | Marketing, Branding e Comunicação – Brandaz',
         'Artigos da Brandaz sobre marketing, branding, comunicação integrada e o processo criativo da agência em Chapecó e no Oeste de SC.',
         body, current='/blog/', schema=[blogld, crumbs([("Blog", "/blog/")])])

def post(b):
    slug = f'/blog/{b["slug"]}/'
    w, h = dims(b['cover'])
    rel = [x for x in POSTS if x['slug'] != b['slug'] and x['category'] == b['category']]
    rel = (rel + [x for x in POSTS if x['slug'] != b['slug'] and x not in rel])[:2]
    office = C['evolucao']['office'][0]
    body = f'''
<article class="page-top" data-ch="Artigo"><div class="wrap-1200">
  <a class="back" href="{U('/blog/')}">{BACK} Blog</a>
  <p class="editorial-label">Blog · {E(b["category"])}</p>
  <h1 class="type-h2 fw8 mt6 measure-wide">{E(b["title"])}</h1>
  <div class="blog-meta"><span>{E(b["author"])}</span><span>{date_br(b["date"])}</span><span>{b["readingMinutes"]} min de leitura</span></div>
  <img class="blog-cover{" portrait" if h > w else ""}" src="{U(b["cover"])}" alt="{E(b["coverAlt"])}" width="{w}" height="{h}" decoding="async">
</div>
<div class="blog-body">{md(b["body"])}</div>
<div class="wrap-1200"><aside class="related-posts" data-ch="Leia também"><p class="section-label">Leia também</p><div class="grid">{"".join(post_card(x) for x in rel)}</div></aside></div>
</article>

{cta_band("Vamos conversar", "Você traz o desafio.", "A gente encontra o caminho.", "", btn("Fale com a Brandaz", "/contato/"), "Contato")}

<section class="next-chapter" data-ch="Próximo capítulo"><div class="wrap-1500"><a href="{U('/contato/')}"><div><p class="type-label text-accent">Próximo capítulo</p><h2 class="type-h2 fw8 mt4">Seu próximo capítulo começa aqui.</h2><p class="muted mt4">Conte o que sua marca precisa e vamos conversar.</p></div>
  <div class="cover">{img(office[0], office[1])}<b>Contato</b></div></a></div></section>'''
    ld_post = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": b['title'], "description": b['description'], "datePublished": b['date'],
               "dateModified": b['date'], "author": {"@type": "Organization", "name": b['author']}, "publisher": {"@id": f"{BASE}/#organization"},
               "image": BASE + b['cover'], "mainEntityOfPage": BASE + slug, "articleSection": b['category'], "inLanguage": "pt-BR"}
    page(slug, f'{b["title"]} | Blog Brandaz', b['description'], body, current='/blog/', og=f'/share/blog-{b["slug"]}.jpg', og_type='article',
         schema=[ld_post, crumbs([("Blog", "/blog/"), (b['title'], slug)])])

# ================================================================ CONTATO
def contato():
    socials = ''.join(f'<a href="{u}" target="_blank" rel="noopener noreferrer" aria-label="{n}">{i}</a>' for n, u, i in SOCIALS)
    faq = ''.join(f'<details{" open" if i == 0 else ""}><summary>{E(q)}</summary><p>{E(a)}</p></details>' for i, (q, a) in enumerate(C['faq']))
    body = f'''
<section class="page-top bg-paper contact-top" data-ch="Contato"><div class="wrap-1500 contact-grid">
  <div>{label("Contato")}<div class="mt6">{title("Seu próximo capítulo", "começa aqui.", tag='h1')}</div>
    <p class="type-lead paper-muted mt6">Conte o que sua marca precisa. Respondemos pelo WhatsApp, e-mail ou pessoalmente no nosso novo espaço em Chapecó.</p>
    <div class="contact-info">
      <div class="socials">{socials}</div>
      <div><p class="type-label lb">WhatsApp e telefone</p><a class="big" href="{WA}" target="_blank" rel="noopener noreferrer">{SITE['phone']['display']}</a></div>
      <div><p class="type-label lb">E-mail</p><a class="big" href="mailto:{SITE['email']}">{SITE['email']}</a></div>
      <div><p class="type-label lb">Endereço</p><p class="mt2">{E(SITE['address'])}</p><a class="maps" href="{MAPS}" target="_blank" rel="noopener noreferrer">Ver no Google Maps</a></div>
    </div></div>
  <form class="wa-form" id="waForm" data-wa="{WA}" novalidate>
    <h2>Mande uma mensagem</h2><p class="muted">Preencha e a conversa abre direto no WhatsApp da Brandaz.</p>
    <label for="f-nome">Nome</label><input id="f-nome" name="nome" autocomplete="name" required>
    <label for="f-empresa">Empresa</label><input id="f-empresa" name="empresa" autocomplete="organization">
    <label for="f-escopo">Escopo</label><select id="f-escopo" name="escopo"><option value="">Selecione</option>{''.join(f'<option>{E(s)}</option>' for s in C['contato']['scopes'])}<option>Outro assunto</option></select>
    <label for="f-msg">Mensagem</label><textarea id="f-msg" name="mensagem" rows="4"></textarea>
    <button class="btn" type="submit">Enviar pelo WhatsApp {ARROW}</button>
    <a id="waOut" class="wa-out" href="{WA}" target="_blank" rel="noopener noreferrer" hidden>Se o WhatsApp não abriu, toque aqui para continuar →</a>
  </form>
</div></section>

<section class="wrap-1500 loc" data-ch="Localização">{static_map('contact-map')}</section>

<section class="editorial-band" data-ch="Perguntas frequentes"><div class="wrap-1500">{label("Perguntas frequentes")}<div class="mt6">{title("Dúvidas que", "costumam aparecer.")}</div><div class="faq">{faq}</div></div></section>'''
    faqld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in C['faq']]}
    page('/contato/', 'Contato | Brandaz – Agência de Marketing em Chapecó',
         f'Fale com a Brandaz: WhatsApp {SITE["phone"]["display"]}, {SITE["email"]}. {SITE["address"]}.', body, current='/contato/',
         schema=[{"@context": "https://schema.org", "@type": "ContactPage", "url": BASE + "/contato/", "about": {"@id": f"{BASE}/#agency"}}, faqld, {"@context": "https://schema.org", **PRO}, crumbs([("Contato", "/contato/")])])

def not_found():
    body = f'''<section class="page-top" data-ch="Página não encontrada"><div class="wrap-1500 nf">{label("Erro 404")}<div class="mt6">{title("Esta página", "saiu de cena.", tag='h1')}</div>
  <p class="type-lead muted mt6">O endereço pode ter mudado. Que tal seguir por um destes caminhos?</p>
  <div class="hero-buttons static">{btn("Ir para o início", "/")}{btn("Ver portfólio", "/projetos/")}{btn("Falar no WhatsApp", WA, ext=True)}</div></div></section>'''
    page('/404/', 'Página não encontrada | Brandaz', 'A página que você procurou não existe mais.', body, noindex=True)
    os.replace(os.path.join(OUT, '404', 'index.html'), os.path.join(OUT, '404.html'))
    os.rmdir(os.path.join(OUT, '404'))

# ================================================================ arquivos
PREVIEW_SKIP = ('assets/home/hero-90-graus-1080.mp4', 'share/', 'assets/img/site/wizard-character.webp', 'assets/img/site/cover-slide.webp',
                'assets/video/filmes/', 'og-image.jpg')

def copy_static():
    src = os.path.join(ROOT, 'static')
    used_heroes = {p['hero'].lstrip('/') for p in FEATURED}
    for r, _, fs in os.walk(src):
        for f in fs:
            rel = os.path.relpath(os.path.join(r, f), src).replace(os.sep, '/')
            if PREVIEW:
                if rel.startswith(PREVIEW_SKIP) and not (rel.startswith('assets/video/filmes/') and rel.endswith('.mp4')):
                    continue
                if rel.endswith('/hero.webp') and rel not in used_heroes:
                    continue
            if rel.startswith(('assets/home/hero-', 'assets/home/slide-') if COVER == 'B' else ('assets/home/wall-',)):
                continue  # só a mídia da capa escolhida vai para o site
            dst = os.path.join(OUT, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(r, f), dst)

def write(rel, text):
    with open(os.path.join(OUT, rel), 'w', encoding='utf-8') as f:
        f.write(text)

def extras():
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
          ''.join(f'  <url><loc>{BASE}{c}</loc><lastmod>{date.today().isoformat()}</lastmod><priority>{"1.0" if c == "/" else "0.8" if c.count("/") == 2 else "0.6"}</priority></url>\n' for c in SITEMAP) + '</urlset>\n')
    write('robots.txt', f'User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n')
    redirects = [('/a-brandaz', '/brandaz/'), ('/about', '/brandaz/'), ('/contact', '/contato/'), ('/clientes', '/projetos/'), ('/trabalhos', '/projetos/'),
                 ('/works', '/projetos/'), ('/works/*', '/projetos/'), ('/posicionamento', '/como-trabalhamos/'), ('/conteudos', '/blog/'), ('/capa-verticais', '/'), ('/capa-verticais/', '/')]
    write('_redirects', ''.join(f'{a} {b} 301\n' for a, b in redirects))
    write('_headers', '/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n/share/*\n  Cache-Control: public, max-age=86400\n'
          '/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  Permissions-Policy: camera=(), microphone=(), geolocation=()\n')

def main():
    os.makedirs(OUT, exist_ok=True)
    for name in os.listdir(OUT):  # esvazia a pasta de saída sem removê-la (pode estar aberta num servidor local)
        q = os.path.join(OUT, name)
        shutil.rmtree(q) if os.path.isdir(q) else os.remove(q)
    copy_static()
    home(COVER); brandaz(); como(); servicos(); projetos()
    for i, p in enumerate(PROJECTS):
        case_page(i, p)
    blog()
    for b in POSTS:
        post(b)
    contato()
    if not RELATIVE:
        not_found(); extras()
    if PAGES:
        write('.nojekyll', '')
    n = sum(len(fs) for _, _, fs in os.walk(OUT))
    size = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(OUT) for f in fs)
    print(f'ok: {n} arquivos, {size / 1e6:.1f} MB em {OUT}')

if __name__ == '__main__':
    main()
