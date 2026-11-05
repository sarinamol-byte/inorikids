#!/usr/bin/env python3
"""Builds the static, SEO-ready inorikids.com site from src/, static/ and content/ into dist/."""
import json, os, re, html, shutil, glob
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src')
OUT = os.path.join(ROOT, 'dist')
CONTENT = os.path.join(ROOT, 'content')
SITE = 'https://inorikids.com'
TODAY = __import__('datetime').date.today().isoformat()

_created = {}
def load(name, default):
    """Read an editable content file; on first run, write it from the defaults."""
    path = os.path.join(CONTENT, name)
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    _created[path] = default
    return default

def stem(path):
    return os.path.splitext(os.path.basename(path))[0]

SETTINGS = load('settings.json', {
    'contact1_name': 'Amol Sarin', 'contact1_phone': '+91 96504 41666',
    'contact2_name': 'Hosung Yoo', 'contact2_phone': '+91 78880 02985',
    'email': '', 'instagram': 'https://www.instagram.com/i_norikids/',
    'linkedin': 'https://www.linkedin.com/company/inorikids/', 'video': 'https://youtu.be/huSECLJfJdI'})

def phone_forms(d):
    digits = re.sub(r'\D', '', d)
    return '+' + digits[:2] + '-' + '-'.join(d.split()[1:]) if d.startswith('+') else d, d, digits

C1N, C2N = SETTINGS['contact1_name'], SETTINGS['contact2_name']
PHONE1, PHONE1_D, PHONE1_WA = phone_forms(SETTINGS['contact1_phone'])
PHONE2, PHONE2_D, PHONE2_WA = phone_forms(SETTINGS['contact2_phone'])
EMAIL = SETTINGS.get('email', '').strip()
IG = SETTINGS['instagram']
LI = SETTINGS['linkedin']
VIDEO = SETTINGS['video']

# ---------- prepare output: static files + images (any upload becomes optimised WebP) ----------
shutil.rmtree(OUT, ignore_errors=True)
shutil.copytree(os.path.join(ROOT, 'static'), OUT, ignore=shutil.ignore_patterns('img'))
os.makedirs(os.path.join(OUT, 'img'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
for f in glob.glob(os.path.join(ROOT, 'static', 'img', '*')):
    ext = os.path.splitext(f)[1].lower()
    if ext not in ('.jpg', '.jpeg', '.png', '.webp'):
        continue
    dest = os.path.join(OUT, 'img', stem(f) + '.webp')
    if ext == '.webp':
        shutil.copy(f, dest)
    else:
        with Image.open(f) as im:
            im = im.convert('RGB'); im.thumbnail((1600, 1600)); im.save(dest, 'WEBP', quality=76, method=6)
with open(os.path.join(OUT, 'assets', 'styles.css'), 'w') as f:
    f.write(open(os.path.join(SRC, 'base.css')).read() + open(os.path.join(SRC, 'extra.css')).read())
shutil.copy(os.path.join(SRC, 'main.js'), os.path.join(OUT, 'assets', 'main.js'))

E = html.escape

# ---------- helpers ----------
_dims = {}
def dims(name):
    if name not in _dims:
        with Image.open(f'{OUT}/img/{name}.webp') as im:
            _dims[name] = im.size
    return _dims[name]

def img(name, alt, eager=False):
    w, h = dims(name)
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return f'<img src="/img/{name}.webp" alt="{E(alt)}" width="{w}" height="{h}" {load}>'

MARK = ('<svg viewBox="0 0 100 120" aria-hidden="true"><polygon points="50,0 34,16 50,32" fill="var(--sun)"/>'
        '<polygon points="50,0 66,16 50,32" fill="var(--sun-light)"/><polygon points="34,40 50,48 50,120 34,112" fill="var(--accent)"/>'
        '<polygon points="50,48 66,40 66,112 50,120" fill="var(--accent-deep)"/></svg>')
WA_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.1l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.1-1.2l-.4-.2Z"/></svg>')

NAV = [
    ('outdoor-play-areas.html', 'Outdoor play'),
    ('indoor-play-areas.html', 'Indoor play'),
    ('landscape-furniture.html', 'Landscape furniture'),
    ('outdoor-gym-equipment.html', 'Outdoor gym'),
    ('kids-furniture.html', 'Kids furniture'),
    ('projects.html', 'Projects'),
    ('about.html', 'About'),
]

def url(slug):
    return SITE + '/' if slug == 'index.html' else f'{SITE}/{slug[:-5] if slug.endswith(".html") else slug}'

def clean_links(doc):
    doc = doc.replace('href="./"', 'href="/"').replace('href="index.html"', 'href="/"')
    return re.sub(r'href="([a-z0-9-]+)\.html(#[^"]*)?"', lambda m: f'href="/{m.group(1)}{m.group(2) or ""}"', doc)

ORG_ID = SITE + '/#organization'
ORG = {
    '@type': 'Organization', '@id': ORG_ID, 'name': 'Inori Kids', 'alternateName': ['iNori Kids', 'inorikids'],
    'url': SITE + '/', 'logo': {'@type': 'ImageObject', 'url': SITE + '/logo-512.png', 'width': 512, 'height': 512},
    'image': SITE + '/og-image.jpg',
    'description': 'Indian company bringing world-class kids play areas, indoor play solutions, landscape furniture, pavilions, kids furniture and outdoor gym equipment to India, in partnership with Chungwoo Funstation, Spacetalk and Ittang of South Korea. Design, import, installation and guarantee.',
    'address': {'@type': 'PostalAddress', 'addressLocality': 'Gurugram', 'addressRegion': 'Haryana', 'addressCountry': 'IN'},
    'areaServed': {'@type': 'Country', 'name': 'India'},
    'sameAs': [IG, LI],
    **({'email': EMAIL} if EMAIL else {}),
    'contactPoint': [
        {'@type': 'ContactPoint', 'telephone': PHONE1, 'contactType': 'sales', 'areaServed': 'IN', 'name': C1N, **({'email': EMAIL} if EMAIL else {})},
        {'@type': 'ContactPoint', 'telephone': PHONE2, 'contactType': 'sales', 'areaServed': 'IN', 'name': C2N},
    ],
    'knowsAbout': ['kids play area design', 'playground equipment', 'indoor play areas', 'soft play', 'landscape furniture',
                   'pergolas and pavilions', 'outdoor gym equipment', 'kids furniture', 'custom playground design', 'playground safety surfacing'],
}

def crumbs_schema(trail):
    return {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': url(s)} for i, (s, n) in enumerate(trail)]}

def faq_schema(faqs):
    return {'@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': re.sub('<[^>]+>', '', a)}} for q, a in faqs]}

def service_schema(slug, name, stype, desc, items):
    return {'@type': 'Service', '@id': url(slug) + '#service', 'name': name, 'serviceType': stype, 'description': desc,
            'provider': {'@id': ORG_ID}, 'areaServed': {'@type': 'Country', 'name': 'India'}, 'url': url(slug),
            'hasOfferCatalog': {'@type': 'OfferCatalog', 'name': name, 'itemListElement': [
                {'@type': 'Offer', 'itemOffered': {'@type': 'Service', 'name': i}} for i in items]}}

# ---------- page shell ----------
def header(slug):
    links = ''.join(f'<a href="{s}"{" aria-current=\"page\"" if s == slug else ""}>{n}</a>' for s, n in NAV)
    mlinks = ''.join(f'<a href="{s}">{n}</a>' for s, n in NAV) + '<a href="custom-playground-design.html">Bespoke design</a><a href="guides.html">Guides</a><a href="contact.html">Contact</a>'
    return f'''<a class="skip" href="#main">Skip to content</a>
<header>
  <div class="wrap nav">
    <a class="logo" href="./" aria-label="Inori Kids home">{MARK}nori <span>kids</span></a>
    <nav aria-label="Main">{links}</nav>
    <details class="menu"><summary>Menu</summary><div class="menu-panel">{mlinks}</div></details>
    <a class="btn" href="contact.html">Get a quote</a>
  </div>
</header>'''

def footer():
    return f'''<footer>
  <div class="wrap">
    <div class="fgrid">
      <div style="display:grid;gap:12px;align-content:start">
        <a class="logo" href="./" aria-label="Inori Kids home" style="font-size:1.2rem">{MARK}nori <span>kids</span></a>
        <p>World-class kids play areas, indoor play, landscape furniture, kids furniture and outdoor gym equipment, designed with leading Korean studios and installed and guaranteed in India.</p><p>Gurugram, Haryana, India</p>
      </div>
      <div><h2>Solutions</h2><ul>
        <li><a href="outdoor-play-areas.html">Kids play areas</a></li>
        <li><a href="indoor-play-areas.html">Indoor play areas</a></li>
        <li><a href="landscape-furniture.html">Landscape furniture</a></li>
        <li><a href="outdoor-gym-equipment.html">Outdoor gym equipment</a></li>
        <li><a href="kids-furniture.html">Kids furniture</a></li>
        <li><a href="custom-playground-design.html">Bespoke design</a></li>
      </ul></div>
      <div><h2>Company</h2><ul>
        <li><a href="projects.html">Projects</a></li>
        <li><a href="about.html">About and partners</a></li>
        <li><a href="guides.html">Guides</a></li>
        <li><a href="contact.html">Get a quote</a></li>
      </ul></div>
      <div><h2>Talk to us</h2><ul>
        <li>{C1N}<br><a href="tel:+{PHONE1_WA}">{PHONE1_D}</a></li>
        <li>{C2N}<br><a href="tel:+{PHONE2_WA}">{PHONE2_D}</a></li>
        {f'<li><a href="mailto:{EMAIL}">{EMAIL}</a></li>' if EMAIL else ''}
        <li><a href="{IG}" target="_blank" rel="noopener">Instagram</a> · <a href="{LI}" target="_blank" rel="noopener">LinkedIn</a></li>
      </ul></div>
    </div>
    <p class="fine">© 2026 Inori Kids · inorikids.com</p>
  </div>
</footer>
<a class="wa" href="https://wa.me/{PHONE1_WA}?text={E('Hi Inori Kids, I would like to discuss a project.').replace(' ', '%20')}" target="_blank" rel="noopener" aria-label="Chat with Inori Kids on WhatsApp">{WA_ICON}<span>WhatsApp us</span></a>'''

def page(slug, title, desc, body, graph, trail=None, ogimg='og-image.jpg', ogtype='website'):
    nodes = [ORG] + graph
    if trail:
        nodes.append(crumbs_schema(trail))
    nodes.append({'@type': 'WebPage', '@id': url(slug) + '#webpage', 'url': url(slug), 'name': title, 'description': desc,
                  'isPartOf': {'@id': SITE + '/#website'}, 'about': {'@id': ORG_ID}, 'inLanguage': 'en-IN',
                  'primaryImageOfPage': SITE + '/' + ogimg if ogimg.endswith('.jpg') else SITE + '/img/' + ogimg})
    ld = json.dumps({'@context': 'https://schema.org', '@graph': nodes}, ensure_ascii=False, indent=1)
    crumb_html = ''
    if trail and len(trail) > 1:
        lis = ''.join(f'<li><a href="{"./" if s == "index.html" else s}">{E(n)}</a></li>' if i < len(trail) - 1 else f'<li aria-current="page">{E(n)}</li>'
                      for i, (s, n) in enumerate(trail))
        crumb_html = f'<nav class="crumbs wrap" aria-label="Breadcrumb"><ol>{lis}</ol></nav>'
    og = SITE + '/' + ogimg if ogimg.endswith('.jpg') else f'{SITE}/img/{ogimg}'
    head = f'''<!doctype html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{E(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<link rel="canonical" href="{url(slug)}">
<link rel="alternate" hreflang="en-in" href="{url(slug)}">
<link rel="alternate" hreflang="x-default" href="{url(slug)}">
<meta property="og:type" content="{ogtype}">
<meta property="og:site_name" content="Inori Kids">
<meta property="og:locale" content="en_IN">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url(slug)}">
<meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#13203A">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Unbounded:wght@500;700&family=Figtree:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap">
<link rel="stylesheet" href="/assets/styles.css">
<script type="application/ld+json">
{ld}
</script>
</head>
<body>
'''
    doc = head + header(slug) + '\n' + crumb_html + '\n<main id="main">\n' + body + '\n</main>\n' + footer() + '\n<script src="/assets/main.js" defer></script>\n</body>\n</html>\n'
    open(f'{OUT}/{slug}', 'w').write(clean_links(doc))
    PAGES.append((slug, title, desc))

PAGES = []
_FAQ_FILE = os.path.join(CONTENT, 'faqs.json')
_FAQS = json.load(open(_FAQ_FILE, encoding='utf-8')) if os.path.exists(_FAQ_FILE) else {}
_faq_defaults = {}
def faqs(key, default):
    _faq_defaults[key] = [{'question': q, 'answer': a} for q, a in default]
    items = _FAQS.get(key, _faq_defaults[key])
    return [(i['question'], i['answer']) for i in items if i.get('question') and i.get('answer')]

_RANGE_FILE = os.path.join(CONTENT, 'ranges.json')
_RANGES = json.load(open(_RANGE_FILE, encoding='utf-8')) if os.path.exists(_RANGE_FILE) else {}
_range_defaults = {}
def ranges(key, default):
    """Product-range cards: title, text, optional photo, label. Editable in the CMS."""
    _range_defaults[key] = [{'title': it[0], 'text': it[1],
                             'image': f'img/{it[2]}.webp' if len(it) > 2 and it[2] else '',
                             'image_description': it[3] if len(it) > 3 and it[3] else '',
                             'label': it[4] if len(it) > 4 else ''} for it in default]
    out = []
    for i in _RANGES.get(key, _range_defaults[key]):
        if not i.get('title'):
            continue
        pic = stem(i['image']) if i.get('image') else None
        out.append((i['title'], i.get('text', ''), pic, i.get('image_description') or i['title'], i.get('label', '')))
    return out

# ---------- reusable blocks ----------
def page_hero(eyebrow, h1, lead, im, alt, ctas=None):
    ctas = ctas or [('contact.html', 'Get a quote', ''), ('projects.html', 'See projects', 'ghost')]
    c = ''.join(f'<a class="btn {k}" href="{h}">{t}</a>' for h, t, k in ctas)
    return f'''<section class="page-hero"><div class="wrap"><div class="hero-grid">
  <div class="hero-copy"><p class="eyebrow">{eyebrow}</p><h1>{h1}</h1><p class="lead">{lead}</p><div class="hero-actions">{c}</div></div>
  <figure class="hero-img facet">{img(im, alt, eager=True)}</figure>
</div></div></section>'''

def answer(q, a):
    return f'<div class="answer"><p class="eyebrow">{q}</p><p>{a}</p></div>'

def sec(inner, top=True, cls=''):
    return f'<section class="{cls}"{"" if top else " style=\"padding-top:0\""}><div class="wrap">{inner}</div></section>'

def head(eyebrow, h2, lead=''):
    return f'<div class="sec-head"><p class="eyebrow">{eyebrow}</p><h2>{h2}</h2>{f"<p class=lead>{lead}</p>" if lead else ""}</div>'

def range_grid(items):
    out = []
    items = sorted(items, key=lambda it: 0 if (len(it) > 2 and it[2]) else 1)
    for it in items:
        h3, p = it[0], it[1]
        tag = it[4] if len(it) > 4 else ''
        t = f'<p class="tag">{tag}</p>' if tag else ''
        if len(it) > 2 and it[2]:
            out.append(f'<article><div class="ph facet">{img(it[2], it[3])}</div><div class="txt">{t}<h3>{h3}</h3><p>{p}</p></div></article>')
        else:
            out.append(f'<article class="noimg"><div class="txt">{t}<h3>{h3}</h3><p>{p}</p></div></article>')
    return f'<div class="range">{"".join(out)}</div>'

def faq_block(faqs, h2='Frequently asked questions'):
    d = ''.join(f'<details><summary>{E(q)}</summary><p>{a}</p></details>' for q, a in faqs)
    return sec(head('FAQ', h2) + f'<div class="faq">{d}</div>', top=False)

def related(links):
    a = ''.join(f'<a href="{s}"><b>{t}</b><span>{d}</span></a>' for s, t, d in links)
    return sec(head('Related', 'Explore more solutions') + f'<div class="related">{a}</div>', top=False)

def cta(h2='Planning a play area, garden or open gym? Talk to us.'):
    return f'''<section class="cta-band"><div class="wrap"><h2>{h2}</h2><div class="acts">
<a class="btn" href="contact.html">Get a quote</a><a class="btn ghost" href="tel:+{PHONE1_WA}">Call {PHONE1_D}</a>{f'<a class="btn ghost" href="mailto:{EMAIL}">{EMAIL}</a>' if EMAIL else ''}</div></div></section>'''

STANDARDS = ('Our play equipment carries EN 1176 and ASTM international safety certifications and Korea\'s KC certification '
             'for children\'s products. Every installation is planned with safety zones and impact-absorbing '
             'surfacing matched to the critical fall height of each piece.')

TIE = ('Inori Kids is an Indian company bringing world-class play and landscape solutions to India. We have tied up with Chungwoo Funstation, '
       'Spacetalk and Ittang of South Korea to bring the best designs and materials to India.')

AWARD_PICS = [
    ('artistic-playground-reddot', 'Red Dot Award 2024', 'Artistic playground', 'Red spiral net playground with a tall red canopy in a residential courtyard'),
    ('arcloud-reddot', 'Red Dot Award 2024', 'Arcloud', 'Illuminated cloud-shaped canopy structure at night'),
    ('award-presidential-sanmaru', 'Presidential Award 2019', 'Sanmaru Playground', 'Orange multi-storey play tower seen from below'),
    ('award-good-design-teahouse', 'Good Design Award 2023', 'Teahouse', 'Glazed teahouse pavilion among apartment towers'),
    ('award-good-design-inout', 'Good Design Award 2023', 'Playground', 'Timber and black steel play tower with long slide on green surfacing'),
]
AWARD_LIST = [
    ('Red Dot Design Award', '2024 winner for an artistic playground and for Arcloud; "Best of the Best" in 2012; product award 2014; winner for Anytime Playground at Raemian One Bailey'),
    ('Presidential Award, Korea', '2019, for Sanmaru Playground'),
    ('iF Product Design Award', '2014 winner'),
    ('Asia Design Prize', '2018 winner'),
    ('Good Design Award', '20 awards, including a teahouse and a playground in 2023, the "Sky Hope" playground tower and "Where Wind Stays" book café in 2016, and outdoor fitness equipment in 2015'),
    ('IDEA Award', 'Winner'),
    ('Seoul Mayor\'s Award', '2016, Landscape Architect Day'),
    ('Eco-friendly playground', 'Recognised 8 times'),
]
_aw = load('awards.json', {'photos': [{'image': f'img/{f}.webp', 'award': a, 'project': n, 'description': alt} for f, a, n, alt in AWARD_PICS],
                            'awards': [{'award': a, 'details': d} for a, d in AWARD_LIST]})
AWARD_PICS = [(stem(p['image']), p['award'], p['project'], p.get('description', p['project'])) for p in _aw['photos']]
AWARD_LIST = [(a['award'], a['details']) for a in _aw['awards']]

def awards_section(top=True, band=True):
    pics = ''.join(f'<figure><div class="ph facet">{img(f, alt)}</div><figcaption><b>{a}</b><span>{n}</span></figcaption></figure>' for f, a, n, alt in AWARD_PICS)
    lis = ''.join(f'<li><b>{a}</b><span>{d}</span></li>' for a, d in AWARD_LIST)
    return f'''<section class="{'band ' if band else ''}awards"{'' if top else ' style="padding-top:0"'}><div class="wrap">
  {head('Award-winning design', 'Designs recognised by the world\'s leading design awards.', 'The play, landscape and furniture designs we bring to India have won the Red Dot, iF, Asia Design Prize and Korea\'s Presidential Award.')}
  <div class="aw-grid">{pics}</div>
  <ul class="aw-list">{lis}</ul>
</div></section>'''

CITIES = ('Delhi NCR (Gurugram, Noida, Greater Noida, Faridabad, Ghaziabad), Mumbai, Pune, Bengaluru, Hyderabad, Chennai, '
          'Ahmedabad, Chandigarh, Jaipur and Lucknow')

# =====================================================================
# HOME
# =====================================================================
home_faq = [
    ('What does Inori Kids do?', 'Inori Kids designs, imports, installs and guarantees kids play areas, indoor play solutions, landscape furniture (pergolas, pavilions, benches), kids furniture and outdoor gym equipment in India. ' + TIE),
    ('Who are your clients?', 'Residential developers and housing societies, schools and preschools, malls and retail centres, and hotels and resorts. We also work with landscape architects and contractors on their projects.'),
    ('How does a project with Inori Kids start?', 'You give us the area, your site plan and what you want there. Developers and contractors often come with a space and a product in mind and ask us to design the area around it. Our award-winning design team then designs the complete play area, landscape or open gym for that space, and we import, install and guarantee it.'),
    ('Do you sell off-the-shelf play equipment?', 'No. We are a kids play area solution provider: every project is designed for the client\'s space, from the layout and safety zones to the equipment, surfacing and shade, and can include a one-of-a-kind landmark piece.'),
    ('Where is the equipment made?', 'In South Korea, in our partners\' own factories, with in-house manufacturing and powder coating. We handle import, installation, warranty and after-sales in India.'),
    ('Is the equipment safety certified?', STANDARDS),
    ('Which cities do you work in?', f'We are based in Gurugram, Haryana, and take on projects across India, including {CITIES}.'),
    ('How do I get a quote?', f'Send your site details through our <a href="contact.html">enquiry form</a>, or call or WhatsApp {C1N} on {PHONE1_D} or {C2N} on {PHONE2_D}. We follow up with a site visit and a proposal.'),
]
home_faq = faqs('home', home_faq)
sols = [
    ('outdoor-play-areas.html', 'Outdoor kids play areas', 'blossom-aerial', 'Aerial view of a circular kids play area with yellow, pink and lilac blossom towers', 'Outdoor play',
     'Playground equipment for societies, schools and parks: play towers, slides, climbing nets, swings, in-ground trampolines and safety surfacing.', ['Housing societies', 'Schools', 'Parks', 'Hotels']),
    ('indoor-play-areas.html', 'Indoor play areas', 'in-net-tree', 'Indoor kids play area with a giant green net treehouse and climbing hill', 'Indoor play',
     'Complete indoor play solutions for malls, clubhouses, play cafés and preschools: net towers, soft play, tube slides and themed interiors.', ['Malls', 'Clubhouses', 'Play cafés', 'Preschools']),
    ('landscape-furniture.html', 'Landscape furniture, pergolas and pavilions', 'dramatic-circle', 'Curved white community lounge pavilion lit at night between apartment towers', 'Landscape',
     'Pavilions, tea houses, pergolas, shelters, benches and public art that give a landscape its identity.', ['Podium gardens', 'Campuses', 'Retail plazas', 'Resorts']),
    ('outdoor-gym-equipment.html', 'Outdoor gym equipment', 'fit-plus', 'Black outdoor gym stations on green rubber surfacing in a residential park', 'Fitness',
     'Open gym stations for strength, cardio, calisthenics and senior fitness, plus smart fitness play for children.', ['Society amenities', 'Jogging tracks', 'Public parks']),
    ('kids-furniture.html', 'Kids furniture', 'kids-play-kitchen-furniture', 'Birch plywood kids play kitchen and market stall furniture in a preschool', 'Furniture',
     'Preschool and daycare furniture, role-play kitchens, climbing beds and kids\' room furniture in certified birch plywood.', ['Preschools', 'Kids rooms', 'Libraries']),
    ('custom-playground-design.html', 'Bespoke landmark design', 'unicorn', 'White faceted-steel unicorn climbing structure', 'Our strength',
     'One-of-a-kind sculptural play structures and pavilions designed for your site, your brand and your story.', ['Developers', 'Townships', 'Destinations']),
]
sol_html = ''.join(f'''<article class="sol facet"><div class="ph">{img(im, alt)}</div><div class="body"><p class="tag">{tag}</p>
<h3><a href="{s}">{t}</a></h3><p>{p}</p><ul>{"".join(f"<li>{x}</li>" for x in chips)}</ul><a class="more" href="{s}">Explore {t.lower()} →</a></div></article>'''
                   for s, t, im, alt, tag, p, chips in sols)

home_body = f'''<section class="hero"><div class="wrap">
  <div class="hero-grid">
    <div class="hero-copy">
      <p class="eyebrow">World-class play and landscape solutions, made for India</p>
      <h1>Kids play areas that become <em>landmarks</em>.</h1>
      <p class="lead">A kids play area solution provider for developers and contractors. Give us your space and your design intent; we design the play area, landscape or open gym around it with our award-winning Korean design partners, then install and guarantee it in India.</p>
      <div class="hero-actions"><a class="btn" href="contact.html">Discuss your project</a><a class="btn ghost" href="projects.html">See the work</a></div>
    </div>
    <div class="hero-media">
      <figure class="facet">{img('unicorn', 'White faceted-steel unicorn climbing structure in a residential kids play area', eager=True)}<figcaption>Unicorn · bespoke</figcaption></figure>
      <figure class="facet">{img('reindeer', 'Blue faceted reindeer play tower with tube slide')}<figcaption>Blue Reindeer</figcaption></figure>
      <figure class="facet">{img('pinecones', 'Ring-shaped timber and steel play structure with pinecone towers, lit at night')}<figcaption>Pinecones</figcaption></figure>
    </div>
  </div>
  <div class="facts">
    <div><b>Red Dot</b><span>Winner 2024 and "Best of the Best"</span></div>
    <div><b>iF</b><span>Product Design Award winner</span></div>
    <div><b>Presidential</b><span>Award, Republic of Korea, 2019</span></div>
    <div><b>20</b><span>Good Design Awards</span></div>
  </div>
</div></section>
{sec(answer('In short', TIE + ' We supply and install kids play areas, indoor play areas, landscape furniture, kids furniture and outdoor gym equipment for residential developers, contractors, schools, malls and hotels across India. You give us the space; we design the solution around it.'), top=False)}
<section id="solutions" style="padding-top:0"><div class="wrap">
  {head('What we offer', 'Six solutions, one partner for the whole site.', 'Use one or combine them into a single landscape plan. Every project is designed around your space and your design intent.')}
  <div class="sol-grid" style="grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr))">{sol_html}</div>
</div></section>
<section style="padding-top:0"><div class="wrap"><div class="ways">
  <div class="way"><p class="k">You bring</p><h3>The space and the intent</h3><p>Developers and contractors come to us with an area, a site plan and often a product or theme in mind, and ask us to design around it.</p>
    <ol><li>Site plan and area available</li><li>Who the space is for: ages, residents, visitors</li><li>Your design intent, theme or product idea</li></ol></div>
  <div class="way"><p class="k">We deliver</p><h3>A complete, designed solution</h3><p>Our award-winning design team designs the whole area for that space, then we import, install and guarantee it in India.</p>
    <ol><li>Layout, safety zones and surfacing</li><li>3D design and engineering</li><li>Installation, handover and warranty</li></ol>
    <a class="btn ghost" href="custom-playground-design.html" style="justify-self:start">How our design process works</a></div>
</div></div></section>
<section class="band"><div class="wrap">
  {head('Bespoke landmarks', 'Each one is designed for a single site.', 'Created by our partners for residential and public projects in South Korea. The same design team and factory are now developing bespoke concepts for developers in India.')}
  <div class="landmarks">
    <figure><div class="ph facet">{img('unicorn', 'Unicorn sculptural play structure')}</div><figcaption><b>Unicorn</b><span>Residential · Korea</span></figcaption></figure>
    <figure><div class="ph facet">{img('reindeer', 'Blue Reindeer play tower')}</div><figcaption><b>Blue Reindeer</b><span>Residential · Korea</span></figcaption></figure>
    <figure><div class="ph facet">{img('tiger', 'White faceted tiger play structure with slide')}</div><figcaption><b>White Tiger</b><span>Residential · Korea</span></figcaption></figure>
    <figure><div class="ph facet">{img('ant-tower', 'Orange and charcoal net play frame with giant ant sculptures')}</div><figcaption><b>Ant Colony</b><span>Residential · Korea</span></figcaption></figure>
    <figure><div class="ph facet">{img('pinecones', 'Circular elevated play deck with pinecone towers at night')}</div><figcaption><b>Playing with Pinecones</b><span>Residential · Korea</span></figcaption></figure>
  </div>
</div></section>
{awards_section(top=True, band=False)}
<section style="padding-top:0"><div class="wrap">
  {head('Who we work with', 'Built for the people who commission spaces.')}
  <div class="aud">
    <div><h3>Developers and contractors</h3><p>Bring us the space and the brief, and we design a signature kids play area, clubhouse kids room or podium garden that shows up in every brochure and site visit.</p></div>
    <div><h3>Schools and preschools</h3><p>Safe, durable outdoor and indoor play and classroom furniture, planned around age groups and daily heavy use.</p></div>
    <div><h3>Malls and retail</h3><p>Indoor play zones and plaza installations that bring families in and keep them on site longer.</p></div>
    <div><h3>Hotels and resorts</h3><p>Kids clubs, garden play and pavilions that fit the property\'s design language.</p></div>
  </div>
</div></section>
<section style="padding-top:0"><div class="wrap">
  {head('How we work', 'From first site visit to handover.', 'One team in India for the whole project, including import, installation and after-sales.')}
  <div class="steps">
    <div class="step"><h3>Site brief and survey</h3><p>We visit the site, take measurements and understand users, budget and theme.</p><span class="where">India</span></div>
    <div class="step"><h3>Concept and 3D design</h3><p>A design for your space, presented in 3D for approval.</p><span class="where">Korea + India</span></div>
    <div class="step"><h3>Engineering and safety</h3><p>Structural detailing, safety zones and fall-height surfacing planned to international standards.</p><span class="where">Korea</span></div>
    <div class="step"><h3>Manufacturing</h3><p>Made in the partners\' own factories, with quality checks before dispatch.</p><span class="where">Korea</span></div>
    <div class="step"><h3>Import and installation</h3><p>We handle shipping, customs and on-site installation.</p><span class="where">India</span></div>
    <div class="step"><h3>Handover and guarantee</h3><p>Safety check, handover documents, warranty and after-sales support.</p><span class="where">India</span></div>
  </div>
  <div class="film" id="film">
    <a class="poster facet" href="{VIDEO}" target="_blank" rel="noopener" aria-label="Watch the design-to-installation film on YouTube (opens in a new tab)">
      {img('pinecones', '')}<span class="play" aria-hidden="true"><svg viewBox="0 0 24 24"><polygon points="5,3 21,12 5,21" fill="#13203A"/></svg></span><span class="poster-cap">Watch on YouTube ↗</span></a>
    <div class="film-copy"><p class="eyebrow">Watch the process</p><h3 style="font-size:clamp(1.3rem,2.4vw,1.8rem);font-weight:700">One bespoke project, from first sketch to installation.</h3>
      <p>See how a complete custom play solution comes together across every stage.</p>
      <a class="btn ghost" href="{VIDEO}" target="_blank" rel="noopener" style="justify-self:start">Watch the film ↗</a></div>
  </div>
</div></section>
{faq_block(home_faq)}
{cta()}'''
page('index.html', 'Kids Play Area Design & Solutions in India | Inori Kids',
     'Kids play areas, indoor play solutions, landscape furniture, kids furniture and outdoor gym equipment for developers, schools, malls and hotels in India. Korean-made, installed and guaranteed by Inori Kids.',
     home_body, [{'@type': 'WebSite', '@id': SITE + '/#website', 'url': SITE + '/', 'name': 'Inori Kids', 'publisher': {'@id': ORG_ID}, 'inLanguage': 'en-IN'},
                 faq_schema(home_faq)], trail=[('index.html', 'Home')])

# =====================================================================
# OUTDOOR PLAY
# =====================================================================
o_items = [
    ('Combination play structures', 'Multi-level play towers with decks, bridges, slides, climbing walls and nets, sized for ages 2–5, 5–12 or both. The core of most society and school play areas.', 'lookout', 'Play tower with tube slide, net bridge and in-ground trampoline', 'Play systems'),
    ('Sculptural and themed play', 'Animal, art and signature play series: faceted unicorns, reindeer and tigers that children climb through and slide down. A play area that doubles as public art.', 'unicorn', 'Faceted white unicorn climbing structure', 'Signature · Art · Animal series'),
    ('Rope and net climbing', 'Rope towers, climbing nets, net tunnels and space-net frames that build strength and coordination and suit a wide age range.', 'ant-tower', 'Net climbing frame with tube slide and ant sculptures', 'Rope play series'),
    ('Nature and timber play', 'Robinia timber play, log balance trails and forest-style play that blend into green landscapes and podium gardens.', 'pinecones', 'Timber and steel ring play deck with pinecone towers', 'Robinia play series'),
    ('Slides, swings, spinners and springers', 'Freestanding classics: straight, wave, tube and spiral slides, swings, spinners, rockers and springers to complete a play area or fill a smaller corner.'),
    ('Toddler play zones', 'Low-height play houses, crawl tunnels, sensory panels and small slides for ages 1–5, set apart from older children\'s equipment.'),
    ('Inclusive play', 'Ground-level play, wide transfer platforms, accessible routes and sensory elements so children of all abilities can play together. Available on request, planned with your project team.'),
    ('Water play', 'Splash pads, water tables and interactive water play structures, from small features to destination water play zones. Available on request: we work with your project team, with the water connection and drainage in your scope.', None, None, 'On request'),
    ('In-ground trampolines', 'Flush-mounted trampolines that sit level with the surfacing, a favourite in society play areas and school grounds.', 'blossom-aerial', 'Circular play area with blossom towers seen from above'),
    ('Safety surfacing', 'Poured EPDM rubber, rubber tiles and artificial grass, laid to the depth each piece of equipment needs for its critical fall height, in colours and patterns that suit your landscape.'),
]
o_items = ranges('outdoor_play', o_items)
o_faq = [
    ('What equipment goes into a kids play area for a housing society?', 'A typical society play area combines one combination play structure (towers, slides, climbing), a separate toddler zone, freestanding swings or spinners, and impact-absorbing safety surfacing. Larger societies add a sculptural landmark piece, an in-ground trampoline or a water play feature.'),
    ('How much space does a kids play area need?', 'Each piece of equipment needs its own footprint plus a clear safety zone around it, typically at least 1.5 to 2 metres on every side. Even a compact area can hold a small combination unit and a toddler zone; a full society play area usually needs several hundred square metres. We work out the exact layout from your site plan.'),
    ('What does a kids play area cost in India?', 'Cost depends on the size of the area, the design (a complete play area or a sculptural landmark piece), the amount of safety surfacing, shade structures and site work. We give a detailed quote once we have designed the area for your space.'),
    ('Which safety standards does your playground equipment meet?', STANDARDS),
    ('Will the equipment survive Indian summers and monsoons?', 'The equipment is built for permanent outdoor use and long service life. During design we also plan shade, drainage and surfacing for local conditions, which matters as much as the equipment itself in Indian summers and monsoons.'),
    ('Do you install the play area and provide a warranty?', 'Yes. We handle import, installation and handover on site, and provide the manufacturer\'s warranty and after-sales support in India. Warranty terms are set out in your quote.'),
]
o_faq = faqs('outdoor_play', o_faq)
o_body = page_hero('Kids play areas · Playground equipment', 'Outdoor kids play areas and playground equipment',
    'Korean-made playground equipment for housing societies, townships, schools, parks and hotels in India. Give us your space and we design the complete play area around it, from play towers to sculptural landmarks, installed with safety surfacing and guaranteed.',
    'blossom-aerial', 'Aerial view of a circular kids play area with blossom-shaped play towers in a residential garden') + \
 sec(answer('What is a kids play area?', 'A kids play area is a dedicated, fenced or zoned space with playground equipment such as play towers, slides, swings and climbing nets, set on impact-absorbing safety surfacing. In Indian housing societies and schools it usually includes separate zones for toddlers and for children aged 5–12.'), top=False) + \
 sec(head('Our range', 'Playground equipment for every age and site.', 'A complete outdoor play range, from compact society play areas to destination playgrounds.') + range_grid(o_items), top=False) + \
 sec(f'''<div class="prose"><div class="col"><h2>Where our play areas work</h2>
<ul><li><strong>Residential societies and townships:</strong> central play areas, podium and terrace play, play next to the clubhouse.</li>
<li><strong>Schools and preschools:</strong> age-zoned playgrounds that stand up to daily heavy use.</li>
<li><strong>Parks and public spaces:</strong> robust, vandal-resistant equipment and inclusive play.</li>
<li><strong>Hotels, resorts and malls:</strong> outdoor kids zones and themed play that fit the property.</li></ul>
<p>We are based in Gurugram, Haryana, and take on projects across India, including {CITIES}.</p></div>
<div class="col"><h2>Safety, built in</h2><p>{STANDARDS}</p>
<p>Every layout we propose shows the equipment footprint, safety zones, fall heights and surfacing depth, so your architect and safety consultant can review it before anything is ordered. Read our <a href="kids-play-area-planning-guide.html">kids play area planning guide</a> for the full checklist.</p></div></div>''', top=False) + \
 faq_block(o_faq, 'Kids play area questions') + \
 related([('custom-playground-design.html', 'Bespoke landmark play', 'Sculptural play structures designed for one site.'),
          ('indoor-play-areas.html', 'Indoor play areas', 'Net towers, soft play and kids rooms.'),
          ('outdoor-gym-equipment.html', 'Outdoor gym equipment', 'Open gyms next to the play area.')]) + cta('Planning a kids play area? Send us your site plan.')
o_items_names = [i[0] for i in o_items]
page('outdoor-play-areas.html', 'Kids Play Area & Outdoor Playground Equipment | Inori Kids',
     'Kids play areas and playground equipment for societies, schools and parks in India: play towers, slides, swings, climbing nets, themed play and safety surfacing. Korean-made, installed and guaranteed.',
     o_body, [service_schema('outdoor-play-areas.html', 'Outdoor kids play areas and playground equipment', 'Playground equipment supply and installation',
              'Design, supply and installation of outdoor kids play areas and playground equipment in India.', o_items_names), faq_schema(o_faq)],
     trail=[('index.html', 'Home'), ('outdoor-play-areas.html', 'Outdoor kids play areas')], ogimg='blossom-aerial.webp')

# =====================================================================
# INDOOR PLAY
# =====================================================================
i_items = [
    ('Multi-level net towers', 'Two- and three-storey play frames with climbing nets, spiral routes and lookouts, built to make the most of double-height atriums.', 'in-spiral-tower', 'Spiral net play tower rising through a double-height atrium', 'Play frames'),
    ('Themed play landscapes', 'Treehouses, cloud trees and forest hills that turn a whole room into one immersive play scene.', 'in-net-tree', 'Indoor play hall with a giant green net treehouse, climbing hill and rope bridge', 'Themed interiors'),
    ('Tube and spiral slides', 'Clear and coloured tube slides that link levels and give every structure its signature moment.', 'in-cloud-slide', 'Brown tube slides curving down from a cloud tree play structure', 'Slides'),
    ('Soft play and toddler zones', 'Padded hedges, tunnels, mirrors and low climbers for babies and toddlers, kept apart from older children.', 'in-hedges', 'Soft play zone with green hedge shapes and a yellow tube slide', 'Ages 1–5'),
    ('Indoor trampolines and net bridges', 'In-floor trampolines, net bridges and high-level walkways for active play in malls and play centres.', 'in-trampoline', 'Indoor trampolines beside a yellow play house and net bridge', 'Active play'),
    ('Clubhouse kids rooms', 'Complete kids rooms for residential clubhouses: play structure, reading corner, role play and furniture designed as one space.', 'indoor-tree-slide-childcare', 'Indoor play room with a timber tree, climbing hill and twin slides', 'Residential'),
    ('Play cafés and family centres', 'Kids cafés and family play centres with play, seating and parent areas planned together. Our partners have designed municipal kids cafés in Seoul.'),
    ('Interactive and digital play', 'Smart play content and interactive learning play, including coding play, for edutainment centres and libraries.'),
]
i_items = ranges('indoor_play', i_items)
i_faq = [
    ('What is an indoor play area?', 'An indoor play area is a climate-controlled play space inside a building, such as a mall, clubhouse, hotel, preschool or play café, fitted with play frames, slides, climbing nets and soft play on safe flooring. It lets children play year-round regardless of heat, rain or pollution.'),
    ('How much floor area does a kids indoor play area need?', 'A clubhouse kids room can work in a few hundred square feet; a mall play zone or play café usually needs a few thousand. Ceiling height matters as much as floor area, because double-height spaces allow multi-level net towers. We plan to your floor plate.'),
    ('Do you design the full interior or just supply equipment?', 'Both. We design complete children\'s interiors, including play structures, themed walls, flooring, lighting and furniture, or we can supply play equipment into a space designed by your architect.'),
    ('Is indoor play equipment safe for toddlers?', 'Yes, when toddlers have their own zone. We separate under-5 soft play from taller structures and use padded edges, enclosed platforms and impact-absorbing flooring. The play products carry Korean KC safety certification.'),
    ('Can you fit an indoor play area into an existing mall or clubhouse?', 'Yes. Structures are made in modules in Korea and assembled on site, so they can go into existing buildings. We check access routes, ceiling heights and floor loading during the survey.'),
]
i_faq = faqs('indoor_play', i_faq)
i_body = page_hero('Kids indoor play areas · Indoor play solutions', 'Kids indoor play areas, designed and built end to end',
    'Indoor play solutions for malls, residential clubhouses, play cafés, hotels and preschools in India. Multi-level net towers, tube slides, soft play and themed interiors, designed in Korea and installed by Inori Kids.',
    'in-net-tree', 'Indoor kids play area with a giant green net treehouse, slide and climbing hill') + \
 sec(answer('In short', 'Inori Kids designs and installs complete kids indoor play areas, from a clubhouse kids room to a multi-level mall play zone, using award-winning Korean play structures and interiors. We handle the design, import, installation and warranty in India.'), top=False) + \
 sec(head('Indoor play solutions', 'Everything an indoor play space needs.') + range_grid(i_items), top=False) + \
 sec(f'''<div class="prose"><div class="col"><h2>Who we build indoor play for</h2>
<ul><li><strong>Malls and retail:</strong> anchor play zones that increase family footfall and dwell time.</li>
<li><strong>Residential developers:</strong> clubhouse kids rooms and indoor play for gated communities.</li>
<li><strong>Hotels and resorts:</strong> kids clubs designed to match the property.</li>
<li><strong>Preschools, daycares and play cafés:</strong> play and learning spaces in one.</li></ul></div>
<div class="col"><h2>Why indoor play matters in Indian cities</h2><p>Summer heat, monsoon rain and winter air quality limit outdoor play for months each year. A well-designed indoor play area gives children a safe place to climb, slide and run every day of the year, and gives your building a reason for families to visit.</p>
<p>Our design team\'s work includes public indoor playgrounds, kids cafés, childcare centres and community kids rooms for residential complexes in Korea. See them in our <a href="projects.html">project gallery</a>.</p></div></div>''', top=False) + \
 faq_block(i_faq, 'Indoor play area questions') + \
 related([('kids-furniture.html', 'Kids furniture', 'Furniture for preschools, kids rooms and play cafés.'),
          ('outdoor-play-areas.html', 'Outdoor kids play areas', 'Playgrounds for societies and schools.'),
          ('custom-playground-design.html', 'Bespoke design', 'A one-off play structure for your atrium.')]) + cta('Planning an indoor play area? Send us your floor plan.')
page('indoor-play-areas.html', 'Kids Indoor Play Area & Indoor Play Solutions | Inori Kids',
     'Kids indoor play areas for malls, clubhouses, play cafés, hotels and preschools in India: net towers, tube slides, soft play and themed interiors. Korean design, installed and guaranteed in India.',
     i_body, [service_schema('indoor-play-areas.html', 'Kids indoor play areas and indoor play solutions', 'Indoor play area design and installation',
              'Design, supply and installation of kids indoor play areas in India.', [x[0] for x in i_items]), faq_schema(i_faq)],
     trail=[('index.html', 'Home'), ('indoor-play-areas.html', 'Indoor play areas')], ogimg='in-net-tree.webp')

# =====================================================================
# LANDSCAPE FURNITURE
# =====================================================================
l_items = [
    ('Pavilions and community lounges', 'Architectural pavilions for gathering, reading or waiting, such as Dramatic Circle, a curved, lit community lounge in an IPARK residential complex.', 'dramatic-circle', 'Curved white lounge pavilion lit at night', 'Pavilion series'),
    ('Tea houses and garden cafés', 'Glazed tea houses, terrace cafés and garden houses that turn a landscape into a usable outdoor room.', 'wormhole-teahouse', 'White slatted tea house with outdoor seating on a lawn'),
    ('Pergolas', 'Timber, steel and aluminium pergolas designed to your space, from compact 2 m modules to 20 m walkways.', 'ocean-pergola', 'Timber and white pergola on a seafront lawn', 'Pergola series'),
    ('Sculptural canopies', 'Petal, ribbon and shell-shaped canopies that give shade and a focal point at the same time.', 'flower-petal', 'White petal-shaped canopy over garden seating', 'Public art'),
    ('Benches and seating', 'Park benches, low platform benches, seat walls and picnic tables in timber, steel and composite finishes.', 'low-bench', 'Patterned low platform bench on a lawn', 'Bench series'),
    ('Public art and landmark pieces', 'Sculptural installations such as the Pine Cone Tree House that people photograph, sit in and remember.', 'pinecone-treehouse', 'Three woven pinecone-shaped tree houses on a lawn', 'Public art'),
    ('Shelters and stations', 'Bus and shuttle shelters, bicycle shelters and waiting stations for townships and campuses.', None, None, 'Station series'),
    ('Colonnades and garden houses', 'Colonnades, gabled glass garden houses and community houses for podiums and amenity gardens.', 'greenery-house', 'Gabled glass garden house with timber cladding'),
    ('Smart street furniture', 'Smart benches, sharing booths and IoT-enabled street furniture for connected campuses and public spaces.'),
    ('Bollards, planters and enclosures', 'Bollards, planters and waste and recycling enclosures that keep a landscape consistent down to the details.'),
]
l_items = ranges('landscape_furniture', l_items)
l_faq = [
    ('What is landscape furniture?', 'Landscape furniture, also called site furniture or street furniture, is the fixed outdoor furniture in a landscape: benches, pergolas, pavilions, shelters, planters, bollards and public art. It makes outdoor spaces comfortable and gives them a recognisable identity.'),
    ('What is the difference between a pergola and a pavilion?', 'A pergola is an open frame of posts and beams, sometimes with slats or a light canopy, that gives partial shade and defines a walkway or seating area. A pavilion is a fully roofed structure, sometimes enclosed with glass, that gives full shelter and can be used as a lounge, tea house or meeting space.'),
    ('Can pergolas and pavilions be customised?', 'Yes. Every pavilion and pergola is designed for your landscape plan, and our team also creates one-off pavilions and canopies around your brand.'),
    ('Which materials suit Indian weather?', 'For strong sun and heavy rain we recommend powder-coated steel or aluminium frames, stainless fixings, treated or composite timber and UV-stable finishes. Our partners powder-coat in-house, which keeps finish quality consistent.'),
    ('Do you supply landscape furniture for podium gardens and terraces?', 'Yes. We check loading, fixing details and wind exposure for podiums and terraces, and choose bases and anchoring to suit the slab.'),
]
l_faq = faqs('landscape_furniture', l_faq)
l_body = page_hero('Landscape furniture · Pergolas · Pavilions', 'Landscape furniture, pergolas and pavilions',
    'Pavilions, tea houses, pergolas, benches, shelters and public art, Korean-designed and award-winning, for residential developers, campuses, retail plazas, hotels and parks in India.',
    'pinecone-city', 'Woven pinecone-shaped pavilions in a city park at sunset') + \
 sec(answer('In short', 'Inori Kids supplies and installs Korean-designed landscape furniture in India: pavilions, tea houses, pergolas, sculptural canopies, benches, shelters, smart street furniture and public art. Each piece is designed for your landscape.'), top=False) + \
 sec(head('Our range', 'Places to pause, not just places to pass.') + range_grid(l_items), top=False) + \
 sec(f'''<div class="prose"><div class="col"><h2>Where it works</h2>
<ul><li><strong>Residential developers:</strong> podium gardens, amenity lawns, clubhouse forecourts and drop-off shelters.</li>
<li><strong>Corporate and education campuses:</strong> outdoor meeting pavilions, shaded walkways and bicycle shelters.</li>
<li><strong>Retail plazas and hotels:</strong> sculptural canopies and seating that draw people in.</li>
<li><strong>Parks and public spaces:</strong> durable benches, shelters and public art.</li></ul></div>
<div class="col"><h2>Designed, engineered and finished in-house</h2><p>Every piece is designed, engineered, manufactured and powder-coated in-house in Korea, then installed and supported by our team in India. The range has won Good Design Awards for teahouses and gardens and a Red Dot Award for Arcloud.</p></div></div>''', top=False) + \
 faq_block(l_faq, 'Landscape furniture questions') + \
 related([('outdoor-play-areas.html', 'Outdoor kids play areas', 'Play areas to sit beside your pavilions.'),
          ('outdoor-gym-equipment.html', 'Outdoor gym equipment', 'Open gyms along your walking tracks.'),
          ('custom-playground-design.html', 'Bespoke design', 'One-off pavilions and landmark pieces.')]) + cta('Planning a landscape? Send us your drawings.')
page('landscape-furniture.html', 'Landscape Furniture, Pergolas & Pavilions in India | Inori Kids',
     'Landscape furniture for developers, campuses and parks in India: pavilions, tea houses, pergolas, benches, shelters, smart street furniture and public art. Award-winning Korean design.',
     l_body, [service_schema('landscape-furniture.html', 'Landscape furniture, pergolas and pavilions', 'Landscape and site furniture supply and installation',
              'Supply and installation of landscape furniture, pergolas, pavilions and public art in India.', [x[0] for x in l_items]), faq_schema(l_faq)],
     trail=[('index.html', 'Home'), ('landscape-furniture.html', 'Landscape furniture')], ogimg='dramatic-circle.webp')

# =====================================================================
# OUTDOOR GYM
# =====================================================================
g_items = [
    ('Strength stations', 'Chest press, shoulder press, lat pull-down, leg press and combination stations that use body weight as resistance.', 'fit-plus', 'Black outdoor strength stations on green rubber surfacing', 'Strength'),
    ('Cardio equipment', 'Cross-trainers, walkers and other low-impact cardio stations for walking tracks and parks.', 'fitness-park', 'Outdoor fitness park with people exercising on stations and a running track'),
    ('Senior fitness', 'Gentle balance, flexibility and mobility stations designed for older residents.', 'flexo-senior', 'Yellow and black senior fitness stations in a garden', 'Seniors'),
    ('Calisthenics and bar frames', 'Pull-up bars, push-up frames, parallel bars and multi-station rigs for body-weight training.', 'cw-fitness-frame', 'Coloured push-up and pull-up frames along a garden path', 'Body weight'),
    ('Smart fitness for children', 'App-connected fitness play that turns exercise into interactive games for children.', None, None, 'Children'),
    ('Fitness packages and layouts', 'Planned sets of stations for a society open gym, a jogging-track circuit or a park fitness zone, with surfacing and signage.'),
]
g_items = ranges('outdoor_gym', g_items)
g_faq = [
    ('What is an open gym or outdoor gym?', 'An outdoor gym, also called an open gym, is a set of fixed, weather-proof exercise stations installed in a park, society or campus. Most stations use body weight as resistance, so they need no power, weights or supervision and are free for residents to use.'),
    ('What outdoor gym equipment should a housing society install?', 'A good society open gym combines a few strength stations (press and pull movements), one or two cardio stations such as a cross-trainer, a calisthenics bar frame and at least one senior-friendly balance or mobility station, placed along a walking track on rubber or turf surfacing.'),
    ('How much space does an outdoor gym need?', 'Each station needs its own footprint plus clear space for movement around it. A compact society open gym with six to eight stations typically fits in 100 to 200 square metres; a park fitness zone can be much larger. We plan layouts using the safety-zone principles of EN 16630, the European standard for outdoor fitness equipment.'),
    ('Is outdoor gym equipment suitable for senior citizens?', 'Yes, if you choose the right stations. Senior ranges focus on balance, flexibility and gentle strength with low step-on heights and handholds.'),
    ('How do outdoor gym machines hold up to sun and rain?', 'The stations are built for permanent outdoor installation, with powder-coated frames designed for long outdoor life. We recommend shade where possible and include care guidance at handover.'),
]
g_faq = faqs('outdoor_gym', g_faq)
g_body = page_hero('Outdoor gym equipment · Open gym', 'Outdoor gym equipment for societies, parks and campuses',
    'Weather-proof, Korean-designed open gym equipment: strength, cardio, calisthenics and senior fitness stations, plus smart fitness play for children, supplied and installed across India.',
    'fit-plus', 'Outdoor gym stations on rubber surfacing in a residential park') + \
 sec(answer('In short', 'Inori Kids supplies and installs Korean-made outdoor gym equipment in India, including strength and cardio stations, calisthenics frames, senior fitness and children\'s smart fitness, for housing societies, public parks, schools and corporate campuses.'), top=False) + \
 sec(head('Our range', 'Open gym equipment for every resident.') + range_grid(g_items), top=False) + \
 sec(f'''<div class="prose"><div class="col"><h2>Where our open gyms work</h2>
<ul><li><strong>Housing societies and townships:</strong> amenity open gyms and stations along jogging tracks.</li>
<li><strong>Public parks:</strong> durable, unsupervised fitness zones for all ages.</li>
<li><strong>Schools and colleges:</strong> calisthenics and fitness for sports grounds.</li>
<li><strong>Corporate campuses:</strong> outdoor wellness areas for employees.</li></ul></div>
<div class="col"><h2>Fitness next to play</h2><p>Many families want parents exercising within sight of children playing. We often plan the open gym and the <a href="outdoor-play-areas.html">kids play area</a> together, with shared paths, shade and <a href="landscape-furniture.html">seating</a>, so the whole amenity works as one space.</p></div></div>''', top=False) + \
 faq_block(g_faq, 'Outdoor gym questions') + \
 related([('outdoor-play-areas.html', 'Outdoor kids play areas', 'Play areas beside the open gym.'),
          ('landscape-furniture.html', 'Landscape furniture', 'Shade, benches and pavilions.'),
          ('kids-play-area-planning-guide.html', 'Planning guide', 'How to plan a society amenity area.')]) + cta('Planning an open gym? Tell us about your site.')
page('outdoor-gym-equipment.html', 'Outdoor Gym Equipment for Societies & Parks | Inori Kids',
     'Outdoor gym and open gym equipment for housing societies, parks and campuses in India: strength, cardio, calisthenics and senior fitness stations. Korean design, installed in India.',
     g_body, [service_schema('outdoor-gym-equipment.html', 'Outdoor gym equipment', 'Outdoor fitness equipment supply and installation',
              'Supply and installation of outdoor gym and open gym equipment in India.', [x[0] for x in g_items]), faq_schema(g_faq)],
     trail=[('index.html', 'Home'), ('outdoor-gym-equipment.html', 'Outdoor gym equipment')], ogimg='fit-plus.webp')

# =====================================================================
# KIDS FURNITURE
# =====================================================================
k_items = [
    ('Preschool and daycare furniture', 'Child-height tables, chairs, shelving and storage for classrooms and activity rooms, ', 'preschool-classroom-furniture', 'Birch plywood preschool table, stools and shelving with toys', 'Preschools'),
    ('Role-play kitchens and market stalls', 'Play kitchens, washing machines, shop counters and market stalls for imaginative play corners.', 'kids-play-kitchen-furniture', 'Birch plywood play kitchen and market stall furniture', 'Role play'),
    ('Climbing beds and play houses', 'Loft play houses, wall bars, arch climbers and triangle climbers that combine furniture and active play.', 'laf-house-climbing-bed', 'Birch climbing play house with slide and arch climber', 'Active play'),
    ('Kids room furniture', 'Premium children\'s furniture for homes, show flats and clubhouse kids rooms: low shelves, tables, cribs and storage.', 'laflaf-kids-room-furniture', 'Toddlers playing in a kids room with birch shelving and table', 'Kids rooms'),
    ('Learning-space themes', 'Furniture sets for reading forests, block-play tables, art ateliers, maker spaces and role-play rooms.'),
    ('Library and play café furniture', 'Reading nooks, book displays and seating for toy libraries, little libraries and kids cafés.'),
]
k_items = ranges('kids_furniture', k_items)
k_faq = [
    ('What furniture does a preschool or daycare need?', 'Child-height tables and chairs for each age group, low open shelving and storage children can reach, a reading corner, role-play furniture such as a play kitchen, and soft seating. We plan these as themed learning areas: reading, blocks, art, making and role play.'),
    ('What material is your kids furniture made from?', 'Premium SE0-grade birch plywood with extremely low formaldehyde emission, designed and made in-house in Korea.'),
    ('Is the kids furniture safety certified?', 'Yes. The furniture holds Korea\'s KC safety certification for children\'s products and is tested under Korea\'s Special Act on the Safety of Children\'s Products.'),
    ('Can you furnish a clubhouse kids room or show flat?', 'Yes. We can supply furniture alone or design the full kids room, combining furniture with an indoor play structure, flooring and wall graphics.'),
]
k_faq = faqs('kids_furniture', k_faq)
k_body = page_hero('Kids furniture · Preschool furniture', 'Kids furniture for preschools, kids rooms and play cafés',
    'Korean-designed birch plywood children\'s furniture: preschool tables and storage, role-play kitchens, climbing beds and kids room furniture, supplied in India by Inori Kids.',
    'laflaf-kids-room-furniture', 'Toddlers playing in a kids room furnished with birch shelving, table and play kitchen') + \
 sec(answer('In short', 'Inori Kids supplies KC-certified Korean birch plywood furniture for preschools, daycares, clubhouse kids rooms, show flats, libraries and play cafés in India.'), top=False) + \
 sec(head('Our range', 'Furniture built around how children learn and play.') + range_grid(k_items), top=False) + \
 sec('''<div class="prose"><div class="col"><h2>Who it is for</h2>
<ul><li><strong>Preschools, play schools and daycares:</strong> classroom and activity-room furniture.</li>
<li><strong>Residential developers:</strong> clubhouse kids rooms and show-flat children\'s bedrooms.</li>
<li><strong>Libraries, play cafés and family centres:</strong> reading and play furniture.</li>
<li><strong>Hotels:</strong> kids club furniture.</li></ul></div>
<div class="col"><h2>Made for small hands</h2><p>Our design partner has designed children\'s spaces since 1999 and runs its own design research institute. The furniture is sized to children\'s developmental needs, made in-house from eco-friendly birch plywood and tested to Korean children\'s product safety law. Pair it with an <a href="indoor-play-areas.html">indoor play structure</a> for a complete kids room.</p></div></div>''', top=False) + \
 faq_block(k_faq, 'Kids furniture questions') + \
 related([('indoor-play-areas.html', 'Indoor play areas', 'Play structures for the same room.'),
          ('custom-playground-design.html', 'Bespoke design', 'A themed kids room designed for you.'),
          ('contact.html', 'Get a quote', 'Tell us about your space.')]) + cta('Furnishing a preschool or kids room? Talk to us.')
page('kids-furniture.html', 'Kids Furniture for Preschools & Kids Rooms | Inori Kids',
     'KC-certified Korean birch plywood kids furniture: preschool tables and storage, play kitchens, climbing beds and kids room furniture for preschools, clubhouses and play cafés in India.',
     k_body, [service_schema('kids-furniture.html', 'Kids furniture', 'Children\'s furniture supply',
              'Supply of children\'s furniture for preschools, kids rooms and play cafés in India.', [x[0] for x in k_items]), faq_schema(k_faq)],
     trail=[('index.html', 'Home'), ('kids-furniture.html', 'Kids furniture')], ogimg='laflaf-kids-room-furniture.webp')

# =====================================================================
# BESPOKE
# =====================================================================
b_faq = [
    ('What is a bespoke or custom playground?', 'A bespoke playground is play equipment designed from scratch for one site. It is usually built around a theme, such as an animal, a local story or a brand, and becomes a landmark for the project.'),
    ('How does the bespoke design process work?', 'We start with your site plan, users and design intent. The partners\' designers develop a concept and 3D design, engineer it for safety, manufacture it in their own factory in Korea, and we install it on site in India.'),
    ('Is a custom play structure safe?', 'Yes. Bespoke pieces are engineered to EN 1176 safety principles, with safety zones, fall heights and surfacing planned in the design.'),
    ('Can a bespoke design reflect our project\'s brand or theme?', 'Yes. That is the point of bespoke work. We are currently developing custom concepts for residential developers in India, each built around the developer\'s design intent.'),
]
b_faq = faqs('bespoke_design', b_faq)
b_body = page_hero('Custom playground design · Bespoke', 'Bespoke landmark play structures, designed for your site',
    'Our strength is one-of-a-kind play structures, pavilions and public art designed around your project\'s story by our award-winning design team, made in Korea and installed in India by Inori Kids.',
    'reindeer', 'Blue faceted reindeer play tower with a tube slide in a residential garden', [('contact.html', 'Start a bespoke project', ''), ('#film', 'Watch the process', 'ghost')]) + \
 sec(answer('In short', 'A bespoke play structure turns a play area into a landmark. Inori Kids offers custom playground and pavilion design in India with a Red Dot, iF and Good Design award-winning team that designs, engineers and manufactures each piece for a single site.'), top=False) + \
f'''<section class="band"><div class="wrap">
  {head('Selected landmarks', 'Each one exists in only one place.', 'Created by our partners for residential and public projects in South Korea.')}
  <div class="landmarks">
    <figure><div class="ph facet">{img('unicorn', 'Faceted white unicorn play structure')}</div><figcaption><b>Unicorn</b><span>Residential · Korea</span></figcaption></figure>
    <figure><div class="ph facet">{img('tiger', 'Faceted white tiger play structure')}</div><figcaption><b>White Tiger</b><span>Residential · Korea</span></figcaption></figure>
    <figure><div class="ph facet">{img('ant-tower', 'Net play frame with giant ant sculptures')}</div><figcaption><b>Ant Colony</b><span>Residential · Korea</span></figcaption></figure>
    <figure><div class="ph facet">{img('dramatic-circle-2', 'Curved lounge pavilion at night')}</div><figcaption><b>Dramatic Circle</b><span>IPARK · 2023</span></figcaption></figure>
    <figure><div class="ph facet">{img('pinecones', 'Pinecone tower play ring at night')}</div><figcaption><b>Playing with Pinecones</b><span>Residential · Korea</span></figcaption></figure>
  </div>
</div></section>''' + \
 sec(f'''{head('How bespoke works', 'From your design intent to a finished landmark.')}
<div class="steps">
<div class="step"><h3>Brief and design intent</h3><p>Your site plan, users, budget and the story the project wants to tell.</p><span class="where">India</span></div>
<div class="step"><h3>Concept and 3D</h3><p>Concept sketches, then a 3D design you can review with your architect.</p><span class="where">Korea + India</span></div>
<div class="step"><h3>Engineering</h3><p>Structure, safety zones and fall heights engineered to EN 1176 principles.</p><span class="where">Korea</span></div>
<div class="step"><h3>Manufacture</h3><p>Built in our partners\' own factories, with quality checks before dispatch.</p><span class="where">Korea</span></div>
<div class="step"><h3>Installation</h3><p>Shipped, cleared and installed on site by our team.</p><span class="where">India</span></div>
<div class="step"><h3>Handover</h3><p>Safety check, documents, warranty and after-sales support.</p><span class="where">India</span></div>
</div>
<div class="film" id="film">
<a class="poster facet" href="{VIDEO}" target="_blank" rel="noopener" aria-label="Watch the design-to-installation film on YouTube (opens in a new tab)">{img('unicorn', '')}<span class="play" aria-hidden="true"><svg viewBox="0 0 24 24"><polygon points="5,3 21,12 5,21" fill="#13203A"/></svg></span><span class="poster-cap">Watch on YouTube ↗</span></a>
<div class="film-copy"><p class="eyebrow">Watch the process</p><h3 style="font-size:clamp(1.3rem,2.4vw,1.8rem);font-weight:700">One bespoke project, from first sketch to installation.</h3><p>See how a complete custom play solution comes together across every stage.</p><a class="btn ghost" href="{VIDEO}" target="_blank" rel="noopener" style="justify-self:start">Watch the film ↗</a></div>
</div>''') + \
 faq_block(b_faq, 'Bespoke design questions') + \
 related([('outdoor-play-areas.html', 'Outdoor kids play areas', 'Play areas designed for your space.'),
          ('landscape-furniture.html', 'Landscape furniture', 'Pavilions and public art.'),
          ('projects.html', 'Projects', 'See more of the work.')]) + cta('Have a design intent in mind? Let\'s develop it.')
page('custom-playground-design.html', 'Custom Playground Design & Themed Play Structures | Inori Kids',
     'Bespoke playground and pavilion design in India: one-of-a-kind sculptural play structures designed, engineered and made in Korea, installed by Inori Kids.',
     b_body, [service_schema('custom-playground-design.html', 'Bespoke landmark play structures', 'Custom playground design',
              'Custom design, manufacture and installation of landmark play structures and pavilions in India.',
              ['Themed play structures', 'Sculptural play landmarks', 'Custom pavilions', 'Public art']), faq_schema(b_faq)],
     trail=[('index.html', 'Home'), ('custom-playground-design.html', 'Bespoke design')], ogimg='reindeer.webp')

# =====================================================================
# PROJECTS
# =====================================================================
gal = [
 ('unicorn', 'outdoor', 'Unicorn sculptural climber'), ('reindeer', 'outdoor', 'Blue Reindeer play tower'), ('pinecones', 'outdoor', 'Playing with Pinecones play ring'),
 ('tiger', 'outdoor', 'White Tiger play structure'), ('ant-tower', 'outdoor', 'Ant Colony net play frame'), ('lookout', 'outdoor', 'Lookout tower with in-ground trampoline'),
 ('blossom-aerial', 'outdoor', 'Blossom courtyard kids play area'),
 ('in-net-tree', 'indoor', 'Net treehouse indoor play hall'), ('in-spiral-tower', 'indoor', 'Spiral net tower in an atrium'), ('in-tree-pillar', 'indoor', 'Tree pillar toddler zone'),
 ('in-cloud-slide', 'indoor', 'Cloud tree with tube slides'), ('in-hedges', 'indoor', 'Hedge maze soft play'), ('in-trampoline', 'indoor', 'Indoor trampolines and net bridge'),
 ('indoor-tree-slide-childcare', 'indoor', 'Childcare centre play room with timber tree and slides'),
 ('dramatic-circle', 'pavilion', 'Dramatic Circle community lounge pavilion'), ('dramatic-circle-2', 'pavilion', 'Dramatic Circle at night'),
 ('pinecone-treehouse', 'pavilion', 'Pine Cone Tree House'), ('flower-petal', 'pavilion', 'Flower Petal Garden canopy'), ('wormhole-teahouse', 'pavilion', 'Wormhole Tea House'),
 ('wormhole-cafe', 'pavilion', 'Wormhole Terrace Cafe'), ('greenery-house', 'pavilion', 'Greenery House'), ('ocean-pergola', 'pavilion', 'Ocean Scent Pergola'),
 ('glass-pavilion', 'pavilion', 'Glass garden pavilion'), ('cw-pavilion', 'pavilion', 'Garden lounge pavilion'), ('yellow-pergola', 'pavilion', 'Curved slat pergola'),
 ('low-bench', 'pavilion', 'Patterned low bench'),
 ('fit-plus', 'fitness', 'Outdoor gym stations'), ('flexo-senior', 'fitness', 'Senior fitness stations'), ('cw-fitness-frame', 'fitness', 'Fitness frames along a garden walk'),
 ('fitness-park', 'fitness', 'Outdoor fitness park'),
 ('kids-play-kitchen-furniture', 'furniture', 'Preschool play kitchen furniture'), ('laflaf-kids-room-furniture', 'furniture', 'Kids room furniture'),
 ('laf-house-climbing-bed', 'furniture', 'Climbing play house'), ('preschool-classroom-furniture', 'furniture', 'Preschool furniture'),
 ('artistic-playground-reddot', 'outdoor', 'Red Dot Award 2024 artistic playground'), ('arcloud-reddot', 'pavilion', 'Red Dot Award 2024 Arcloud canopy'),
 ('award-presidential-sanmaru', 'outdoor', 'Presidential Award 2019 Sanmaru Playground'), ('award-good-design-teahouse', 'pavilion', 'Good Design Award 2023 teahouse'), ('award-good-design-inout', 'outdoor', 'Good Design Award 2023 playground'),
]
_pj = load('projects.json', {'items': [{'image': f'img/{f}.webp', 'category': c, 'title': t} for f, c, t in gal]})
gal = [(stem(p['image']), p['category'], p['title'], p.get('project', ''), p.get('location', '')) for p in _pj['items'] if p.get('image')]
def _gcap(t, pr, lo):
    sub = ' · '.join(x for x in (pr, lo) if x)
    return t, sub
gal_html = ''.join(
    f'<figure class="gitem" data-c="{c}"><button type="button" aria-label="Enlarge: {E(t)}" data-sub="{E(_gcap(t, pr, lo)[1])}">'
    f'{img(f, t + (" at " + pr if pr else "") + (", " + lo if lo else ", South Korea"))}</button>'
    f'<figcaption><b>{E(t)}</b>{f"<span>{E(_gcap(t, pr, lo)[1])}</span>" if (pr or lo) else ""}</figcaption></figure>'
    for f, c, t, pr, lo in gal)
p_body = f'''<section class="page-hero" style="padding-bottom:24px"><div class="wrap"><div class="hero-copy" style="max-width:820px">
<p class="eyebrow">Project gallery</p><h1>Play areas, pavilions and open gyms by our partners</h1>
<p class="lead">Selected work by our design team in South Korea: outdoor kids play areas, indoor play, landscape furniture, outdoor gyms and kids furniture. Our first Indian projects are in design now with residential developers.</p></div></div></section>
<section style="padding-top:24px"><div class="wrap">
<div class="filters" role="group" aria-label="Filter projects">
<button type="button" data-f="all" aria-pressed="true">All</button><button type="button" data-f="outdoor" aria-pressed="false">Outdoor play</button>
<button type="button" data-f="indoor" aria-pressed="false">Indoor play</button><button type="button" data-f="pavilion" aria-pressed="false">Pavilions and furniture</button>
<button type="button" data-f="fitness" aria-pressed="false">Outdoor gym</button><button type="button" data-f="furniture" aria-pressed="false">Kids furniture</button></div>
<div class="gallery" id="gallery">{gal_html}</div></div></section>
<div class="lb" id="lb" hidden role="dialog" aria-modal="true" aria-label="Photo viewer"><button type="button" id="lb-close">Close</button><div><img id="lb-img" alt=""><p id="lb-cap"></p></div></div>
{cta('Want something like this for your project?')}'''
page('projects.html', 'Playground, Indoor Play & Pavilion Projects | Inori Kids',
     'Photo gallery of kids play areas, indoor play areas, pavilions, pergolas, outdoor gyms and kids furniture, including Red Dot and Good Design award winners. Available in India through Inori Kids.',
     p_body, [{'@type': 'ImageGallery', 'name': 'Inori Kids partner project gallery', 'url': url('projects.html'),
               'image': [{'@type': 'ImageObject', 'contentUrl': f'{SITE}/img/{f}.webp', 'name': t, **({'description': ', '.join(x for x in (pr, lo) if x)} if (pr or lo) else {})} for f, c, t, pr, lo in gal]}],
     trail=[('index.html', 'Home'), ('projects.html', 'Projects')], ogimg='unicorn.webp')

# =====================================================================
# ABOUT
# =====================================================================
a_body = page_hero('About Inori Kids', 'World-class play and landscape solutions, brought to India',
    TIE + ' We design with our partners, import, install on site and provide the guarantee in India.',
    'dramatic-circle-2', 'Curved community lounge pavilion lit at night', [('contact.html', 'Talk to us', ''), ('projects.html', 'See projects', 'ghost')]) + \
 sec(f'''<div class="prose"><div class="col"><h2>What we do</h2><p>Developers, schools, malls and hotels deal with one accountable team in India, from the first sketch to handover: design, import, installation, safety surfacing, warranty and after-sales.</p>
<p>We are based in Gurugram, Haryana, and take on projects across India. Our first projects are bespoke concepts for residential developers, each designed around the developer\'s design intent.</p></div>
<div class="col"><h2>Who to talk to</h2><ul><li><strong>{C1N}</strong>: {PHONE1_D}</li><li><strong>{C2N}</strong>: {PHONE2_D}</li>{f'<li><strong>Email</strong>: <a href="mailto:{EMAIL}">{EMAIL}</a></li>' if EMAIL else ''}</ul>
<p>Follow our work on <a href="{IG}" target="_blank" rel="noopener">Instagram</a> and <a href="{LI}" target="_blank" rel="noopener">LinkedIn</a>.</p></div></div>''', top=False) + \
 awards_section(top=False, band=False) + \
 sec('''<div class="trust"><span>EN 1176</span><span>ASTM</span><span>KC</span><span>ISO</span><span>Red Dot Design Award</span><span>iF Design Award</span><span>Asia Design Prize</span><span>Good Design Award</span></div>''', top=False) + cta()
page('about.html', 'About Inori Kids | World-Class Play Spaces for India',
     'Inori Kids is an Indian company bringing award-winning play areas, landscape furniture and outdoor gyms to India with Chungwoo Funstation, Spacetalk and Ittang of South Korea. Based in Gurugram.',
     a_body, [{'@type': 'AboutPage', 'name': 'About Inori Kids', 'url': url('about.html')}],
     trail=[('index.html', 'Home'), ('about.html', 'About')], ogimg='dramatic-circle-2.webp')

# =====================================================================
# CONTACT
# =====================================================================
c_body = f'''<section class="page-hero"><div class="wrap enq">
  <div class="enq-side">
    <p class="eyebrow">Enquiries and quotes</p>
    <h1 style="font-size:clamp(2rem,4vw,3rem)">Get a quote for your play area, garden or open gym</h1>
    <p class="lead">Share a few details and our team will come back with ideas and a design proposal for your space.</p>
    <dl>
      <div><dt>Talk to</dt><dd>{C1N} · <a href="tel:+{PHONE1_WA}">{PHONE1_D}</a></dd></div>
      <div><dt>Or</dt><dd>{C2N} · <a href="tel:+{PHONE2_WA}">{PHONE2_D}</a></dd></div>
      {f'<div><dt>Email</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd></div>' if EMAIL else ''}
      <div><dt>Based in</dt><dd>Gurugram, Haryana, India</dd></div>
      <div><dt>WhatsApp</dt><dd><a href="https://wa.me/{PHONE1_WA}" target="_blank" rel="noopener">Chat with {C1N.split()[0]} ↗</a></dd></div>
      <div><dt>Follow</dt><dd class="social"><a href="{IG}" target="_blank" rel="noopener">Instagram @i_norikids ↗</a><a href="{LI}" target="_blank" rel="noopener">LinkedIn ↗</a></dd></div>
    </dl>
  </div>
  <form id="enq-form" novalidate data-wa1="{PHONE1_WA}" data-name1="{C1N.split()[0]}" data-wa2="{PHONE2_WA}" data-name2="{C2N.split()[0]}">
    <div class="f"><label for="q-name">Your name</label><input id="q-name" name="name" required autocomplete="name"></div>
    <div class="f"><label for="q-org">Organisation</label><input id="q-org" name="org" required autocomplete="organization"></div>
    <div class="f"><label for="q-phone">Phone</label><input id="q-phone" name="phone" type="tel" required autocomplete="tel" placeholder="+91"></div>
    <div class="f"><label for="q-email">Email</label><input id="q-email" name="email" type="email" required autocomplete="email"></div>
    <div class="f"><label for="q-type">Type of project</label><select id="q-type" name="type"><option>Residential development or society</option><option>School or preschool</option><option>Mall or retail</option><option>Hotel or resort</option><option>Public park or campus</option><option>Other</option></select></div>
    <div class="f"><label for="q-city">Project city</label><input id="q-city" name="city" placeholder="e.g. Gurugram"></div>
    <fieldset><legend>Interested in</legend><div class="checks">
      <label><input type="checkbox" id="q-c1" name="line" value="Outdoor play area">Outdoor play area</label>
      <label><input type="checkbox" id="q-c2" name="line" value="Indoor play area">Indoor play area</label>
      <label><input type="checkbox" id="q-c3" name="line" value="Landscape furniture">Landscape furniture</label>
      <label><input type="checkbox" id="q-c4" name="line" value="Outdoor gym">Outdoor gym</label>
      <label><input type="checkbox" id="q-c5" name="line" value="Kids furniture">Kids furniture</label>
      <label><input type="checkbox" id="q-c6" name="line" value="Bespoke landmark">Bespoke landmark</label>
    </div></fieldset>
    <div class="f"><label for="q-area">Approx. area (sq ft)</label><input id="q-area" name="area" inputmode="numeric"></div>
    <div class="f"><label for="q-when">Timeline</label><select id="q-when" name="when"><option>Within 3 months</option><option>3–6 months</option><option>6–12 months</option><option>Just exploring</option></select></div>
    <div class="f full"><label for="q-msg">About the project</label><textarea id="q-msg" name="msg" placeholder="Site, age groups, theme ideas, budget range"></textarea></div>
    <div class="form-foot"><button class="btn" type="submit">Continue</button><small id="q-err" role="status"></small></div>
  </form>
</div></section>'''
page('contact.html', 'Get a Quote for a Kids Play Area or Open Gym | Inori Kids',
     f'Request a quote for a kids play area, indoor play area, landscape furniture, kids furniture or outdoor gym in India. Call {C1N} on {PHONE1_D} or {C2N} on {PHONE2_D}' + (f', or email {EMAIL}.' if EMAIL else '.'),
     c_body, [{'@type': 'ContactPage', 'name': 'Contact Inori Kids', 'url': url('contact.html')}],
     trail=[('index.html', 'Home'), ('contact.html', 'Get a quote')])

# =====================================================================
# GUIDE (AEO content)
# =====================================================================
gd_faq = [
    ('How do you plan a kids play area for a housing society?', 'Start with who will use it (ages and numbers), then measure the available site, allow for safety zones around each piece, decide whether you want a landmark centrepiece, specify safety surfacing to the right depth, add shade and seating for parents, and agree warranty and after-sales terms before ordering.'),
    ('What age zones should a society play area have?', 'At least two: a toddler zone for ages 1–5 with low platforms and small slides, and a junior zone for ages 5–12 with taller towers, climbing and faster slides. Keeping them apart reduces collisions and lets each zone be designed to the right fall height.'),
    ('What is the safest surface for a kids play area?', 'Impact-absorbing surfacing laid to the depth required for the critical fall height of the equipment above it. Poured EPDM rubber and rubber tiles are the most common in India because they are durable, drain well and need little upkeep. Hard surfaces such as concrete or tiles should never be used under play equipment.'),
    ('How much shade does a play area need in India?', 'As much as you can give it. Plan trees, pergolas or shade sails over the most-used equipment and seating, choose lighter surfacing colours, and orient slides away from direct afternoon sun, since metal and plastic surfaces can get very hot.'),
]
gd_faq = faqs('planning_guide', gd_faq)
gd_body = f'''<section class="page-hero" style="padding-bottom:24px"><div class="wrap"><div class="hero-copy" style="max-width:820px">
<p class="eyebrow">Guide · Updated November 2026</p><h1>How to plan a kids play area for a society or school</h1>
<p class="lead">A practical checklist for developers, RWAs, school managements and architects in India, from the first site measurement to handover.</p></div></div></section>
<section style="padding-top:24px"><div class="wrap"><article class="article">
{answer('Quick answer', 'To plan a kids play area: define the age groups and expected users, measure the site and allow safety zones of about 1.5–2 m around each piece, decide on the design and whether it needs a landmark piece, lay impact-absorbing surfacing to the right depth, add shade and parent seating, and confirm warranty and after-sales support before you order.')}
<h2>1. Know who will play</h2>
<p>Count the flats or students the area will serve and the age mix. Most Indian societies need a <strong>toddler zone (ages 1–5)</strong> and a <strong>junior zone (ages 5–12)</strong>. Schools plan by class group. If teenagers will use the space, add climbing, a ninja-style trail or an <a href="outdoor-gym-equipment.html">open gym</a> nearby.</p>
<h2>2. Measure the site and its safety zones</h2>
<p>Every piece of equipment needs its own footprint plus a clear <strong>safety zone</strong>, typically at least 1.5–2 m on each side and more in front of slides and swings. Note slopes, drainage, trees, underground services and whether the site is on a podium slab, which affects anchoring and load.</p>
<h2>3. Decide what the play area should do for the project</h2>
<p>An everyday amenity for residents needs good play value, age zones and shade. A play area that also sells the project, in brochures and on site visits, benefits from a <a href="custom-playground-design.html">landmark centrepiece</a> designed around the project\'s theme. Many projects combine both: one sculptural piece surrounded by a complete <a href="outdoor-play-areas.html">play area</a>.</p>
<h2>4. Give your designer the right brief</h2>
<p>Share the site plan, the area available, levels and existing trees, the expected users, and any theme or product you have in mind. A good play area designer will turn this into a layout with safety zones, equipment, surfacing and shade before anything is ordered.</p>
<h2>5. Get the surfacing right</h2>
<p>Surfacing is a safety system, not a finish. Its depth must match the <strong>critical fall height</strong> of the equipment above it. Poured EPDM rubber and rubber tiles are the usual choices; artificial grass needs a shock pad underneath. Never install play equipment over concrete, paving or tiles.</p>
<h2>6. Plan for heat, rain and shade</h2>
<p>Indian summers make shade essential. Use trees, <a href="landscape-furniture.html">pergolas or shade structures</a> over the busiest equipment and seating, choose lighter surfacing colours, and plan drainage so the area dries fast after monsoon rain.</p>
<h2>7. Think about the adults</h2>
<p>Parents and caregivers stay longer when there is shaded seating with a clear view of the play area. Benches, a pavilion or an open gym alongside turn a play area into a community space.</p>
<h2>8. Confirm certification, installation and warranty</h2>
<p>Ask for the equipment\'s safety certification (for example EN 1176 or ASTM), who installs it, what the warranty covers and how spare parts are supplied. {STANDARDS}</p>
<h2>9. Plan maintenance from day one</h2>
<p>Agree a simple inspection routine: a quick visual check every week, a fuller check of fixings, moving parts and surfacing every few months, and an annual inspection.</p>
</article></div></section>
{faq_block(gd_faq, 'Play area planning questions')}
{related([('outdoor-play-areas.html', 'Outdoor kids play areas', 'See the equipment range.'), ('outdoor-gym-equipment.html', 'Outdoor gym equipment', 'Add an open gym.'), ('contact.html', 'Get a quote', 'Send us your site plan.')])}
{cta('Want us to plan it with you? Send your site plan.')}'''
page('kids-play-area-planning-guide.html', 'How to Plan a Kids Play Area for a Society or School | Inori Kids',
     'A step-by-step guide to planning a kids play area in India: age zones, safety zones, the design brief, safety surfacing, shade, seating, warranty and maintenance.',
     gd_body, [{'@type': 'Article', 'headline': 'How to plan a kids play area for a society or school', 'datePublished': '2026-11-05', 'dateModified': '2026-11-05',
                'author': {'@id': ORG_ID}, 'publisher': {'@id': ORG_ID}, 'image': SITE + '/img/blossom-aerial.webp', 'inLanguage': 'en-IN',
                'mainEntityOfPage': url('kids-play-area-planning-guide.html')}, faq_schema(gd_faq)],
     trail=[('index.html', 'Home'), ('kids-play-area-planning-guide.html', 'Planning guide')], ogimg='blossom-aerial.webp', ogtype='article')

# =====================================================================
# GUIDES written in the CMS (content/guides/*.md)
# =====================================================================
import markdown, yaml
GUIDES = [('kids-play-area-planning-guide.html', 'How to plan a kids play area for a society or school',
           'A practical checklist for developers, RWAs, school managements and architects in India.', 'blossom-aerial', '2026-11-05')]
for md in sorted(glob.glob(os.path.join(CONTENT, 'guides', '*.md'))):
    raw = open(md, encoding='utf-8').read()
    meta, body_md = {}, raw
    if raw.startswith('---'):
        _, fm, body_md = raw.split('---', 2)
        meta = yaml.safe_load(fm) or {}
    if meta.get('draft'):
        continue
    slug = re.sub(r'[^a-z0-9-]+', '-', (meta.get('slug') or stem(md)).lower()).strip('-') + '.html'
    title = meta.get('title', stem(md).replace('-', ' ').title())
    desc = meta.get('description', '')
    date = str(meta.get('date', TODAY))[:10]
    pic = stem(meta['image']) if meta.get('image') else 'blossom-aerial'
    body_html = markdown.markdown(body_md, extensions=['tables'])
    gbody = f'''<section class="page-hero" style="padding-bottom:24px"><div class="wrap"><div class="hero-copy" style="max-width:820px">
<p class="eyebrow">Guide · {date}</p><h1>{E(title)}</h1><p class="lead">{E(desc)}</p></div></div></section>
<section style="padding-top:24px"><div class="wrap"><article class="article">
<figure class="hero-img facet" style="margin:0 0 12px">{img(pic, title)}</figure>
{body_html}
</article></div></section>
{related([('outdoor-play-areas.html', 'Outdoor kids play areas', 'Play areas designed for your space.'), ('guides.html', 'More guides', 'All Inori Kids guides.'), ('contact.html', 'Get a quote', 'Send us your site plan.')])}
{cta()}'''
    page(slug, f'{title} | Inori Kids', desc, gbody,
         [{'@type': 'Article', 'headline': title, 'datePublished': date, 'dateModified': date, 'author': {'@id': ORG_ID},
           'publisher': {'@id': ORG_ID}, 'image': f'{SITE}/img/{pic}.webp', 'inLanguage': 'en-IN', 'mainEntityOfPage': url(slug)}],
         trail=[('index.html', 'Home'), ('guides.html', 'Guides'), (slug, title)], ogimg=pic + '.webp', ogtype='article')
    GUIDES.append((slug, title, desc, pic, date))

cards = ''.join(f'''<article><div class="ph facet">{img(p, t)}</div><div class="txt"><p class="tag">{d}</p><h3><a href="{s}">{E(t)}</a></h3><p>{E(ds)}</p></div></article>'''
                for s, t, ds, p, d in sorted(GUIDES, key=lambda g: g[4], reverse=True))
page('guides.html', 'Kids Play Area Guides for Developers & Schools | Inori Kids',
     'Practical guides on planning kids play areas, indoor play, landscape furniture and outdoor gyms in India, for developers, contractors, schools and architects.',
     f'''<section class="page-hero" style="padding-bottom:24px"><div class="wrap"><div class="hero-copy" style="max-width:820px">
<p class="eyebrow">Guides</p><h1>Guides to planning play spaces</h1><p class="lead">Practical advice for developers, contractors, schools and architects in India.</p></div></div></section>
<section style="padding-top:24px"><div class="wrap"><div class="range">{cards}</div></div></section>{cta()}''',
     [{'@type': 'CollectionPage', 'name': 'Inori Kids guides', 'url': url('guides.html')}],
     trail=[('index.html', 'Home'), ('guides.html', 'Guides')])

# =====================================================================
# 404 (not in sitemap)
# =====================================================================
nf = f'''<section><div class="wrap notfound"><p class="eyebrow">Page not found</p><h1>This page has moved or never existed.</h1>
<p class="lead">Try one of our solutions instead.</p><div class="hero-actions"><a class="btn" href="./">Home</a><a class="btn ghost" href="outdoor-play-areas.html">Kids play areas</a><a class="btn ghost" href="contact.html">Get a quote</a></div></div></section>'''
page('404.html', 'Page Not Found | Inori Kids', 'The page you are looking for could not be found.', nf, [])
s = open(f'{OUT}/404.html').read().replace('index, follow, max-image-preview:large, max-snippet:-1', 'noindex, follow')
open(f'{OUT}/404.html', 'w').write(s)
PAGES.pop()

# ---------- crawl files ----------
pri = {'index.html': '1.0'}
sm = ''.join(f'<url><loc>{url(s)}</loc><lastmod>{TODAY}</lastmod><priority>{pri.get(s, "0.8")}</priority></url>\n' for s, t, d in PAGES)
open(f'{OUT}/sitemap.xml', 'w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n')
open(f'{OUT}/robots.txt', 'w').write(f'''User-agent: *
Allow: /

# Search and AI answer engines are welcome
User-agent: Googlebot
Allow: /
User-agent: Bingbot
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: GPTBot
Allow: /
User-agent: OAI-SearchBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Claude-SearchBot
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Applebot-Extended
Allow: /

Sitemap: {SITE}/sitemap.xml
''')
llms = f'''# Inori Kids

> Inori Kids (inorikids.com) is an Indian company bringing world-class play and landscape solutions to India, in partnership with Chungwoo Funstation, Spacetalk and Ittang of South Korea. It designs, imports, installs and guarantees kids play areas, playground equipment, kids indoor play areas, landscape furniture (pergolas, pavilions, benches, public art), kids furniture and outdoor gym equipment for residential developers, housing societies, schools, malls and hotels in India. A design-led solution provider: clients give the space, Inori Kids designs the solution around it. Based in Gurugram, Haryana, India. Projects across India.

Contact: {C1N} {PHONE1_D} · {C2N} {PHONE2_D} · {('Email ' + EMAIL + ' · ') if EMAIL else ''} Instagram {IG} · LinkedIn {LI}

## Solutions
''' + ''.join(f'- [{t}]({url(s)}): {d}\n' for s, t, d in PAGES if s not in ('index.html', 'contact.html', 'about.html', 'projects.html', 'kids-play-area-planning-guide.html')) + f'''
## Company
- [About Inori Kids]({url('about.html')}): company, partners, awards and certifications
- [Projects]({url('projects.html')}): photo gallery of award-winning projects in Korea
- [Get a quote]({url('contact.html')}): enquiry form, phone and WhatsApp

## Guides
- [How to plan a kids play area]({url('kids-play-area-planning-guide.html')}): step-by-step planning checklist for societies and schools in India

## Key facts
- Awards for the designs: Red Dot (2024 winner; Best of the Best 2012), iF Product Design Award, Asia Design Prize, Presidential Award (Korea, 2019), 20 Good Design Awards
- Safety: EN 1176 and ASTM certifications; KC certification for children's products
- Made in Korea in partner factories; design, installation, safety surfacing, warranty and after-sales in India by Inori Kids
'''
open(f'{OUT}/llms.txt', 'w').write(llms)
open(f'{OUT}/site.webmanifest', 'w').write(json.dumps({'name': 'Inori Kids', 'short_name': 'Inori Kids', 'start_url': '/', 'display': 'browser',
    'background_color': '#F4F6F5', 'theme_color': '#13203A', 'icons': [{'src': '/logo-512.png', 'sizes': '512x512', 'type': 'image/png'},
    {'src': '/apple-touch-icon.png', 'sizes': '180x180', 'type': 'image/png'}]}, indent=1))
for path, data in _created.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
if not os.path.exists(_RANGE_FILE):
    json.dump(_range_defaults, open(_RANGE_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
if not os.path.exists(_FAQ_FILE):
    json.dump(_faq_defaults, open(_FAQ_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('built', len(PAGES), 'pages into', OUT)
