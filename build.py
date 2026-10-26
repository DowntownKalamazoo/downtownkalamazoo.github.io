#!/usr/bin/env python3
"""Builds the Downtown Kalamazoo holiday site into ./out (full documents, ready to host)
and ./artifact (same, with index.html stripped to page content for the artifact skeleton)."""
import html, os, re, shutil, json, datetime as dt
from holiday_content import EVENTS, GIFT_GUIDES
import directory_page
# Plan your day itineraries live in content/itineraries.yml (see itineraries.py and plan_section.py).
import itineraries as IT
PLANS, SANTA, TROLLEY, PARKING = IT.load(EVENTS)
# Each holiday event page lists the plans built around it under "Make a day of it".
for _e in EVENTS:
    _paired = [p['slug'] for p in PLANS if _e['slug'] in p['events']]
    if _paired:
        _e['plans'] = _paired[:4]
import weave

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
E = html.escape
CSS = open(os.path.join(HERE, 'site.css')).read()
JS = open(os.path.join(HERE, 'site.js')).read()
# Brand headline font. HWT Konop is an Adobe Font: create a web project at fonts.adobe.com that includes
# HWT Konop and paste its kit ID here (the part before .css in https://use.typekit.net/abc1234.css).
# Until then, Unbounded stands in.
ADOBE_FONTS_KIT = ''
FONTS = 'https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Jost:wght@400;500;700&family=Montserrat:wght@600;700;800&family=Unbounded:wght@800;900&display=swap'

import random as _random

# The holiday hub (holidays/) is promoted across the site while this is True: a "Holidays" link in the
# main menu, a banner on the homepage and a Holidays column in the footer. Set it to False after the season.
HOLIDAY_SEASON = True

# Pages that are switched off for now. Their content stays in this repository. To bring one back,
# change False to True and commit; every menu, footer and page link to it comes back with it.
SHOW_NEWS = False            # News & stories (news.html, made from content/news)
SHOW_HISTORY = False         # History of downtown (history.html)
SHOW_ACCESS_GUIDE = False    # Accessible downtown guide (access-guide.html)
SHOW_ACCOMMODATION = False   # "Need an accommodation?" box on event, plan and Visit pages

# Downtown's social media accounts. They show in the footer of every page and on the About page.
SOCIAL = [
    ('Facebook', 'https://www.facebook.com/downtownkalamazoo/'),
    ('Instagram', 'https://www.instagram.com/downtownkalamazoo/'),
]
SITE_URL = 'https://downtownkalamazoo.us/'

# Each part of the site has its own brand pattern, so people can tell where they are by texture as well as color.
SECTION_PATTERN = {'directory': 'maze', 'events': 'confetti', 'plan': 'arcs', 'gifts': 'stripes', 'dollars': 'dashes',
                   'visit': 'waves', 'businesses': 'pinstripes', 'news': 'speckle'}
PATH_PATTERN = {'index.html': 'squiggle', 'holidays/index.html': 'squiggle', 'holidays/sbs.html': 'quilt', 'newsletter.html': 'speckle',
                'accessibility.html': 'loops', 'access-guide.html': 'loops', 'take-home.html': 'quilt',
                'your-downtown.html': 'squiggle', '404.html': 'quilt',
                'about.html': 'squiggle', 'history.html': 'quilt', 'boards.html': 'stripes', 'projects.html': 'arcs',
                'ambassadors.html': 'dashes', 'team.html': 'loops', 'waste-recycling.html': 'dots', 'social-district.html': 'waves'}
PATTERNS = ['squiggle', 'confetti', 'arcs', 'dots', 'quilt', 'stripes', 'waves', 'speckle', 'loops', 'maze', 'pinstripes', 'dashes']
FOOTER_PATCH = ['squiggle', 'confetti', 'dots', 'arcs', 'speckle', 'maze', 'stripes', 'quilt', 'dashes', 'waves', 'loops', 'pinstripes']

def pattern_for(path, current):
    if path.startswith('news/'):
        return 'speckle'
    for prefix, pat in (('holidays/events', 'confetti'), ('holidays/plan', 'arcs'), ('holidays/gifts', 'stripes'), ('holidays/businesses', 'pinstripes'), ('events/', 'confetti')):
        if path.startswith(prefix):
            return pat
    return PATH_PATTERN.get(path) or SECTION_PATTERN.get(current) or 'squiggle'

def _brush(vertical, seed):
    """A hand-painted edge, as an SVG mask (black = visible)."""
    rnd = _random.Random(seed)
    import math
    L, D = (400, 40) if vertical else (900, 30)
    pts, bristles = [], []
    for i in range(0, L + 1, 4):
        a = 13 + 5 * math.sin(i / 37 + seed) + 3 * math.sin(i / 11 + 2 * seed) + rnd.uniform(-2.2, 2.2)
        if rnd.random() < .05: a += rnd.uniform(4, 9)
        pts.append((round(a, 1), i))
        if rnd.random() < .12:
            bristles.append((round(rnd.uniform(1, a - 3), 1), i, round(rnd.uniform(3, 9), 1), round(rnd.uniform(.8, 2), 1)))
    if vertical:
        d = f'M{D} 0 ' + ' '.join(f'L{x} {y}' for x, y in pts) + f' L{D} {L}Z'
        br = ''.join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}"/>' for x, y, w, h in bristles)
    else:
        d = f'M0 {D} ' + ' '.join(f'L{y} {x}' for x, y in pts) + f' L{L} {D}Z'
        br = ''.join(f'<rect x="{y}" y="{x}" width="{h}" height="{w}" rx="{h/2}"/>' for x, y, w, h in bristles)
    vb = f'0 0 {D} {L}' if vertical else f'0 0 {L} {D}'
    svg = f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='{vb}' preserveAspectRatio='none'><path d='{d}'/>{br}</svg>"
    return "url(\"data:image/svg+xml," + svg.replace('"', "'").replace('<', '%3C').replace('>', '%3E').replace('#', '%23') + "\")"

BRUSH_V = _brush(True, 3)
BRUSH_H = _brush(False, 5)

NAV = [
    ('directory.html', 'Explore downtown', 'directory'),
    ('events.html', 'Events', 'events'),
    ('dollars.html', 'Downtown Dollars', 'dollars'),
] + ([('news.html', 'News', 'news')] if SHOW_NEWS else []) + [
    ('visit.html', 'Visit', 'visit'),
    ('businesses.html', 'For businesses', 'businesses'),
]
ABOUT_MENU = [
    ('about.html', 'About downtown'),
] + ([('history.html', 'History of downtown')] if SHOW_HISTORY else []) + [
    ('boards.html', 'DDA & DEGA'),
    ('projects.html', 'Projects'),
    ('ambassadors.html', 'Downtown Ambassadors'),
    ('waste-recycling.html', 'Waste & recycling'),
    ('social-district.html', 'Social District'),
]
# The Our team page joins the About menu and footer once content/team.yml is out of draft.
import content_loader as _CL
TEAM_LIVE = not _CL.team()['draft']
if TEAM_LIVE:
    ABOUT_MENU.insert(1, ('team.html', 'Our team'))
HOLIDAY_NAV = [
    ('holidays/index.html', 'Find the Holidays Downtown'),
    ('holidays/events.html', 'Holiday events'),
    ('holidays/plan.html', 'Plan your day'),
    ('holidays/gifts.html', 'Gift guides'),
    ('holidays/sbs.html', 'Small Business Saturday'),
]

def ext(href, text, cls=''):
    c = f' class="{cls}"' if cls else ''
    return f'<a{c} href="{E(href)}" target="_blank" rel="noopener">{text}<span class="sr-only"> (opens in a new tab)</span></a>'


SOCIAL_ICONS = {
    'Facebook': '<path fill="currentColor" d="M13.5 21v-7.5h2.6l.4-3h-3V8.6c0-.9.3-1.5 1.5-1.5h1.6V4.4c-.3 0-1.2-.1-2.3-.1-2.3 0-3.9 1.4-3.9 4v2.2H7.8v3h2.6V21h3.1z"/>',
    'Instagram': '<rect x="3.5" y="3.5" width="17" height="17" rx="5" fill="none" stroke="currentColor" stroke-width="2"/>'
                 '<circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.3" cy="6.7" r="1.2" fill="currentColor"/>',
}


def social_links(label='Downtown Kalamazoo on social media'):
    """Facebook and Instagram, with visible names so they never rely on an icon alone."""
    if not SOCIAL:
        return ''
    items = ''.join(
        f'<li><a href="{E(url)}" target="_blank" rel="noopener me">'
        f'<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24">{SOCIAL_ICONS.get(name, "")}</svg>'
        f'{E(name)}<span class="sr-only">: Downtown Kalamazoo (opens in a new tab)</span></a></li>'
        for name, url in SOCIAL)
    return f'<ul class="social" aria-label="{E(label)}">{items}</ul>'

def header(r, current, path=''):
    cur = lambda key: ' aria-current="page"' if key == current else ''
    items = ''.join(f'<li><a href="{r}{h}"{cur(key)}>{E(t)}</a></li>' for h, t, key in NAV)
    about_on = path in [h for h, _ in ABOUT_MENU]
    about = ''.join(f'<li><a href="{r}{h}"{" aria-current=\"page\"" if h == path else ""}>{E(t)}</a></li>' for h, t in ABOUT_MENU)
    items += (f'<li class="has-menu"><button type="button" class="nav-menu-btn{" is-current" if about_on else ""}" aria-expanded="false" aria-controls="menu-about">About'
              f'<svg aria-hidden="true" width="12" height="12" viewBox="0 0 12 12"><path d="M2 4l4 4 4-4" fill="none" stroke="currentColor" stroke-width="2"/></svg></button>'
              f'<ul class="nav-menu" id="menu-about">{about}</ul></li>')
    if HOLIDAY_SEASON:
        items += f'<li class="nav-holiday"><a href="{r}holidays/index.html"{cur("holidays")}>Holidays</a></li>'
    hbar = ''
    if path.startswith('holidays/'):
        links = ''.join(f'<li><a href="{r}{h}"{" aria-current=\"page\"" if h == path or (h != "holidays/index.html" and path.startswith(h[:-5] + "/")) else ""}>{E(t)}</a></li>' for h, t in HOLIDAY_NAV[1:])
        hbar = (f'<nav class="holiday-bar" aria-label="Find the Holidays Downtown"><div class="wrap hb-row">'
                f'<a class="hb-home" href="{r}holidays/index.html"{" aria-current=\"page\"" if path == "holidays/index.html" else ""}>Find the Holidays Downtown</a>'
                f'<ul>{links}</ul></div></nav>')
    return f'''<a class="skip" href="#main">Skip to content</a>
<div id="ruler" aria-hidden="true"></div>
<header class="site-header">
  <div class="wrap header-row">
    <a class="brand" href="{r}index.html"><img src="{r}dk-logo-green.png" width="900" height="692" alt="Downtown Kalamazoo home"></a>
    <button class="btn btn-small btn-quiet menu-btn" type="button" id="menu-btn" aria-expanded="false" aria-controls="site-nav">Menu</button>
    <nav class="site-nav" id="site-nav" aria-label="Main"><ul>{items}</ul></nav>
    <div class="header-tools">
      <button class="btn btn-small btn-quiet" type="button" data-open-display aria-haspopup="dialog">
        <svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h10M18 7h2M4 17h4M12 17h8"/><circle cx="16" cy="7" r="2"/><circle cx="10" cy="17" r="2"/></svg>
        Display
      </button>
    </div>
  </div>
</header>{hbar}'''

def footer(r):
    hol = ''
    if HOLIDAY_SEASON:
        hol = '<nav aria-label="Holidays"><h2>Holidays</h2><ul>' + ''.join(f'<li><a href="{r}{h}">{E(t)}</a></li>' for h, t in HOLIDAY_NAV) + '</ul></nav>'
    return f'''<footer class="site-footer">
  <div class="footer-stripe" aria-hidden="true">{''.join(f'<span style="background-image:url({r}pattern-{n}-sm.webp)"></span>' for n in FOOTER_PATCH)}</div>
  <div class="wrap">
    <div class="footer-grid{" has-holidays" if hol else ""}">
      <div>
        <p class="footer-word">Downtown<br>Kalamazoo</p>
        <p>Creative. Welcoming. Rooted.</p>
        <p style="margin-top:.75rem">City Hall, 241 W. South St.<br>Email downtown@kalamazoocity.org, or call 311 or (269) 337-8000.</p>
        {social_links('Follow Downtown Kalamazoo')}
      </div>
      <nav aria-label="Explore"><h2>Explore</h2><ul>
        <li><a href="{r}directory.html">Business directory</a></li>
        <li><a href="{r}events.html">Events calendar</a></li>
        <li><a href="{r}dollars.html">Downtown Dollars</a></li>
        <li><a href="{r}social-district.html">Social District</a></li>
        <li><a href="{r}visit.html">Visit &amp; park</a></li>{f'{chr(10)}        <li><a href="{r}access-guide.html">Accessible downtown</a></li>' if SHOW_ACCESS_GUIDE else ''}
      </ul></nav>
      <nav aria-label="About downtown"><h2>Downtown</h2><ul>{f'{chr(10)}        <li><a href="{r}news.html">News &amp; stories</a></li>' if SHOW_NEWS else ''}{f'{chr(10)}        <li><a href="{r}team.html">Our team</a></li>' if TEAM_LIVE else ''}{f'{chr(10)}        <li><a href="{r}history.html">History</a></li>' if SHOW_HISTORY else ''}
        <li><a href="{r}projects.html">Projects</a></li>
        <li><a href="{r}boards.html">DDA &amp; DEGA</a></li>
        <li><a href="{r}ambassadors.html">Downtown Ambassadors</a></li>
        <li><a href="{r}waste-recycling.html">Waste &amp; recycling</a></li>
      </ul></nav>
      <nav aria-label="Get involved"><h2>Get involved</h2><ul>
        <li><a href="{r}businesses.html">Business resources</a></li>
        <li><a href="{r}submit-event.html">Submit an event</a></li>
        <li><a href="{r}newsletter.html">Newsletter</a></li>
        <li><a href="{r}your-downtown.html">Share your downtown</a></li>
        <li><a href="{r}take-home.html">Take a pattern home</a></li>
      </ul></nav>
      {hol}
    </div>
    <div class="footer-base">
      <span>#SomethingNewKalamazoo <span class="found-count" id="found-count" hidden></span></span>
      <span><a href="{r}accessibility.html">Accessibility statement</a> · <button type="button" data-open-display aria-haspopup="dialog">Display settings</button></span>
    </div>
  </div>
</footer>'''

def display_dialog(r):
    return f'''<dialog id="display-dialog" aria-labelledby="display-title">
  <div class="dialog-inner">
    <div class="dialog-head">
      <div><h2 id="display-title">Display settings</h2>
      <p>These change how this site looks for you and are saved on this device. <a href="{r}accessibility.html">Accessibility statement</a></p></div>
      <button class="icon-btn" type="button" data-close aria-label="Close display settings">✕</button>
    </div>
    <ul class="settings-list">
      <li><span class="s-text"><span class="s-name" id="lbl-size">Text size</span><span class="s-hint">Scales every word on the page</span></span>
        <span class="stepper" role="group" aria-labelledby="lbl-size"><button class="icon-btn" type="button" id="size-down" aria-label="Smaller text">A−</button><output id="size-out" aria-live="polite">100%</output><button class="icon-btn" type="button" id="size-up" aria-label="Larger text">A+</button></span></li>
      <li><span class="s-text"><span class="s-name" id="lbl-theme">Theme</span><span class="s-hint">Auto follows your device</span></span>
        <span class="segmented" role="group" aria-labelledby="lbl-theme" id="theme-group"><button type="button" data-theme-val="auto">Auto</button><button type="button" data-theme-val="light">Light</button><button type="button" data-theme-val="dark">Dark</button></span></li>
    </ul>
    <ul class="settings-list" id="switches"></ul>
    <div class="dialog-actions"><button class="btn" type="button" id="reset-display">Reset all</button><button class="btn btn-primary" type="button" data-close>Done</button></div>
  </div>
</dialog>'''

HOLIDAY_SLUGS = [e['slug'] for e in EVENTS]
_MOVE_EVENTS = re.compile(r'(\{R\}|^)events/(' + '|'.join(map(re.escape, HOLIDAY_SLUGS)) + r')\.html')
_MOVE_PAGES = re.compile(r'(\{R\}|^)(plan\.html|plan/|gifts\.html|sbs\.html)')


def relink(html_, holiday=False):
    """The holiday pages moved into holidays/. Point old-style links at their new home."""
    html_ = _MOVE_EVENTS.sub(lambda m: f'{m.group(1)}holidays/events/{m.group(2)}.html', html_)
    html_ = _MOVE_PAGES.sub(lambda m: f'{m.group(1)}holidays/{m.group(2)}', html_)
    if holiday:
        html_ = html_.replace('{R}events.html', '{R}holidays/events.html').replace('{R}businesses.html', '{R}holidays/businesses.html')
    return html_


def _moved_pool():
    pool = {}
    for k, v in SD.POOL.items():
        v = dict(v)
        if v.get('l'):
            v['l'] = [relink(v['l'][0]), v['l'][1]]
        pool[k] = v
    return pool


def page(path, title, body, current=None, description='', root=None):
    depth = path.count('/')
    r = '../' * depth if root is None else root
    pat = pattern_for(path, current)
    holiday = path.startswith('holidays/')
    body = relink(body, holiday)
    if holiday and path != 'holidays/index.html':
        body = body.replace('<li><a href="{R}index.html">Home</a></li>', '<li><a href="{R}index.html">Home</a></li><li><a href="{R}holidays/index.html">Holidays</a></li>', 1)
    body = body.replace('<!--CORNER-->', '', 1).replace('{PAT}', pat).replace('{R}', r)
    picks = SD.PAGE_PICKS.get(path) or SD.PAGE_PICKS.get(path.replace('holidays/', '', 1), [])
    global _POOL
    if '_POOL' not in globals():
        _POOL = _moved_pool()
    finds = json.dumps(dict(pool=_POOL, page=picks, r=r), ensure_ascii=False).replace('</', '<\\/')
    full_title = title if path == 'index.html' else f'{title} · Downtown Kalamazoo'
    url = SITE_URL + ('' if path == 'index.html' else path)
    head = f'''<title>{E(full_title)}</title>
<meta name="description" content="{E(description)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(description)}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="{'article' if path.startswith('news/') else 'website'}">
<meta property="og:image" content="{SITE_URL}og-image.png">
<link rel="icon" href="{r}favicon.png">
<meta name="claude:viewport-fit-sides" content="cover">
<script>document.documentElement.classList.add('js')</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">{f'{chr(10)}<link rel="stylesheet" href="https://use.typekit.net/{ADOBE_FONTS_KIT}.css">' if ADOBE_FONTS_KIT else ''}
<style>{CSS}</style>
<style>:root{{--pat-sq:url({r}pattern-squiggle.webp);--pat-dots:url({r}pattern-dots.webp);--pat-page:url({r}pattern-{pat}.webp);--pat-page-sm:url({r}pattern-{pat}-sm.webp);--brush-v:{BRUSH_V};--brush-h:{BRUSH_H}}}</style>'''
    content = f'''{header(r, current, path)}
<main id="main" tabindex="-1">
{body}
</main>
{footer(r)}
{display_dialog(r)}
<script type="application/json" id="dk-finds">{finds}</script>
<script>{JS}</script>'''
    full = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{head}
</head>
<body>
{content}
</body>
</html>
'''
    os.makedirs(os.path.join(OUT, os.path.dirname(path)), exist_ok=True)
    with open(os.path.join(OUT, path), 'w') as f:
        f.write(full)
    if path == 'index.html':
        with open(os.path.join(HERE, 'artifact_index.html'), 'w') as f:
            f.write(head + '\n' + content + '\n')

def crumbs(trail):
    parts = []
    for i, (href, text) in enumerate(trail):
        if i == len(trail) - 1:
            parts.append(f'<li><span aria-current="page">{E(text)}</span></li>')
        else:
            parts.append(f'<li><a href="{{R}}{href}">{E(text)}</a></li>')
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{"".join(parts)}</ol></nav>'

def page_hero(trail, eyebrow, title, lede, fill='f-green', extra='', photo=None):
    """photo: optional (src, alt). It fills the painted-edge area on the right in place of the pattern."""
    if photo and photo[0]:
        art = (f'<figure class="hero-pat hero-photo"><img src="{{R}}{E(photo[0])}" alt="{E(photo[1] or '')}" '
               f'fetchpriority="high" decoding="async"></figure>')
        fill += ' has-photo'
    else:
        art = '<div class="hero-pat" aria-hidden="true"></div>'
    return f'''<section class="band page-hero {fill}" aria-labelledby="page-title">
  {art}
  <div class="wrap">
    {crumbs(trail)}
    <div class="hero-row">
      <div>
        <p class="eyebrow" style="margin-top:1.25rem">{eyebrow}</p>
        <h1 class="display h1" id="page-title">{title}</h1>
        <p class="lede">{lede}</p>
        {extra}
      </div>
      <!--CORNER-->
    </div>
  </div>
</section>'''


import secrets_data as SD
_TURN_N = [0]

def secret_note(sec, label):
    link = ''
    if sec.get('link'):
        href, text = sec['link']
        link = f'<p><a href="{{R}}{href}">{E(text)}</a></p>'
    return (f'<div class="secret-note" tabindex="-1" role="region" aria-label="{E(label)}">'
            f'<span class="kicker">{E(sec["kicker"])}</span><p class="secret-title">{E(sec["title"])}</p>'
            f'<p>{E(sec["text"])}</p>{link}'
            f'<button class="btn btn-small btn-quiet turn-back" type="button">Turn back</button></div>')

def turn_box(cls, front, sec, label, pattern='pattern-dots.webp', tag='div', attrs=''):
    _TURN_N[0] += 1
    uid = f'turn-{_TURN_N[0]}'
    return (f'<{tag} class="peel turn {cls}" data-turn {attrs}>'
            f'<div class="peel-under" style="background-image:url({{R}}{pattern})" aria-hidden="true"></div>'
            f'<div class="turn-secret" id="{uid}" inert>{secret_note(sec, label)}</div>'
            f'<div class="peel-card">{front}</div>'
            f'<span class="peel-flap" aria-hidden="true"></span>'
            f'<button class="turn-corner" type="button" aria-expanded="false" aria-controls="{uid}"><span class="sr-only">Turn the corner: {E(label)}</span></button>'
            f'</{tag}>')

def corner_card(path):
    sec = SD.PAGE_SECRETS.get(path)
    if not sec:
        return ''
    teaser = SD.TEASERS[sum(map(ord, path)) % len(SD.TEASERS)]
    front = (f'<span class="cc-kicker">Around this corner</span>'
             f'<span class="cc-line">{E(teaser)}</span>'
             f'<span class="cc-hint">Turn the corner to find something about downtown.</span>')
    pattern = 'pattern-squiggle.webp' if sum(map(ord, path)) % 2 else 'pattern-dots.webp'
    return turn_box('corner-card', front, sec, f'{sec["kicker"]}: {sec["title"]}', pattern=pattern, tag='aside')

def in_short(text):
    return f'<p class="in-short"><strong>In short</strong>{text}</p>'

MON = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
DOW = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

def date_tile(e):
    d = dt.date.fromisoformat(e['date'])
    if e.get('end'):
        d2 = dt.date.fromisoformat(e['end'])
        return f'<div class="date-tile range {e["fill"]}" aria-hidden="true"><span class="mon">{MON[d.month]}</span><span class="day">{d.day}–{d2.day}</span><span class="dow">{DOW[d.weekday()]}–{DOW[d2.weekday()]}</span></div>'
    return f'<div class="date-tile {e["fill"]}" aria-hidden="true"><span class="mon">{MON[d.month]}</span><span class="day">{d.day}</span><span class="dow">{DOW[d.weekday()]}</span></div>'

def event_row(e, heading='h3', mark_next=True):
    end = e.get('end') or e['date']
    mn = ' data-mark-next' if mark_next else ''
    return f'''<li class="event-row" data-end="{end}"{mn}>
  {date_tile(e)}
  <div class="body">
    <span class="tag status" hidden></span>
    <{heading} class="h3"><a href="{{R}}events/{e["slug"]}.html">{E(e["title"])}</a></{heading}>
    <p class="meta"><span>{E(e["when_short"])}</span><span>{E(e["where_short"])}</span></p>
    <p>{E(e["summary"])}</p>
  </div>
</li>'''

def card(href, top, title, text, fill, more='Learn more'):
    return f'''<li><article class="card {fill}">
  <div class="card-top" aria-hidden="true">{E(top)}</div>
  <div class="card-body">
    <h3 class="h3"><a href="{{R}}{href}">{E(title)}</a></h3>
    <p>{E(text)}</p>
    <p class="more" aria-hidden="true">{E(more)} →</p>
  </div>
</article></li>'''

GETTING_HERE = '''<section class="panel" aria-labelledby="gh-title">
  <h2 id="gh-title">Getting here</h2>
  <ul>
    <li>The first 90 minutes are free in the Epic Center and Kalamazoo Mall parking ramps.</li>
    <li>The free Holly Jolly Trolley loops downtown from City Hall, 241 W. South St., Thursday through Sunday until Christmas Eve.</li>
  </ul>
  <p><a href="{R}visit.html">Parking, trolley and getting around</a></p>
</section>'''

ACCOMMODATION = '''<section class="panel" aria-labelledby="acc-title">
  <h2 id="acc-title">Need an accommodation?</h2>
  <p>Ask about seating, interpreters, quiet spaces or anything else that would help you enjoy the event. Email downtown@kalamazoocity.org or call 311 ahead of time.</p>
</section>''' if SHOW_ACCOMMODATION else ''
# The access guide link, for pages that point people to it. Empty while the guide is switched off.
ACCESS_GUIDE_LINK = ' · <a href="{R}access-guide.html">Accessible downtown</a>' if SHOW_ACCESS_GUIDE else ''

# ---------------------------------------------------------------- Home
STREETS_FOR_ALL = 'https://www.kalamazoocity.org/Community/Projects/Streets-for-All/Streets-for-All-Kalamazoo-Ave-2026-2028'

PILLARS = [
    dict(fill='f-green', title='Find something local',
         text='Locally owned shops, restaurants, makers and services, a few blocks apart.',
         links=[('Explore downtown', 'directory.html'), ('Gift guides', 'gifts.html'), ('Downtown Dollars', 'dollars.html')]),
    dict(fill='f-red', title='Find more to do',
         text='Pair a holiday event with dinner, shopping, a show or a walk through the lights.',
         links=[('Holiday events', 'events.html'), ('Plan your day', 'plan.html'), ('Small Business Saturday', 'sbs.html')]),
    dict(fill='f-pink', title='Find your tradition',
         text='Keep the ones you love, like the parade and the tree lighting, or start a new one.',
         links=[('Holiday Parade', 'events/holiday-parade.html'), ('Tree Lighting', 'events/tree-lighting.html'), ('New Year’s Fest', 'events/new-years-fest.html')]),
    dict(fill='f-blue', title='Find your way',
         text='Parking, the free trolley, accessibility and what to know about street construction.' if SHOW_ACCESS_GUIDE else 'Parking, the free trolley and what to know about street construction.',
         links=[('Visit & park', 'visit.html')] + ([('Accessible downtown', 'access-guide.html')] if SHOW_ACCESS_GUIDE else [])),
]


def pillar(i, p):
    links = ''.join(f'<li><a href="{{R}}{h}">{E(t)}</a></li>' for t, h in p['links'])
    front = (f'<div class="pillar-top"><span class="num" aria-hidden="true">Find {i} of 4</span><h3 id="pillar-{i}">{E(p["title"])}</h3></div>'
             f'<div class="pillar-body"><p>{E(p["text"])}</p><ul>{links}</ul></div>')
    sec = SD.PILLAR_SECRETS[i - 1]
    return '<li>' + turn_box(f'pillar {p["fill"]}', front, sec, f'{p["title"]}, {sec["kicker"].lower()}', tag='article', attrs=f'aria-labelledby="pillar-{i}"') + '</li>'


def discover_data():
    picks = [b for b in directory_page.BIZ if b['desc'] and b['cat'] in directory_page.VISITOR_CATS]
    return [dict(id=b['id'], n=b['name'], c=b['cat_label'], f=b['fill'], d=b['desc'], w=b['where'], dd=b['dd']) for b in picks]


def snow(n=20, seed=11):
    """Falling dots, borrowed from the dots pattern. Decorative; still when motion is reduced."""
    rnd = _random.Random(seed)
    flakes = ''.join(
        f'<span style="--x:{rnd.uniform(2, 98):.1f}%;--y:{rnd.uniform(4, 92):.1f}%;--s:{rnd.choice([7, 9, 11, 14, 18])}px;'
        f'--d:{rnd.uniform(14, 26):.1f}s;--w:{rnd.uniform(-1.5, 1.5):.1f}rem;animation-delay:-{rnd.uniform(0, 26):.1f}s"'
        f'{" class=pink" if rnd.random() < .3 else ""}></span>' for _ in range(n))
    return f'<div class="snow" aria-hidden="true">{flakes}</div>'


def lights(n=34, seed=4):
    """A string of holiday lights made from the confetti pattern's rounded dashes."""
    rnd = _random.Random(seed)
    cols = ['#e5572e', '#38a669', '#058ac7', '#f5b8d1', '#f2b829']
    W, span = 1600, 1600 / n
    wire = 'M0 6 ' + ' '.join(f'Q{(i + .5) * span:.1f} 30 {(i + 1) * span:.1f} 6' for i in range(n))
    bulbs = ''
    for i in range(n):
        x = (i + .5) * span
        a = rnd.uniform(-14, 14)
        bulbs += (f'<g transform="translate({x:.1f} 18) rotate({a:.1f})"><rect x="-2.6" y="0" width="5.2" height="5" rx="1" fill="#121345"/>'
                  f'<rect class="bulb" style="--i:{i % 7}" x="-5" y="4" width="10" height="21" rx="5" fill="{cols[i % 5]}"/></g>')
    return (f'<div class="lights" aria-hidden="true"><svg viewBox="0 0 {W} 52" preserveAspectRatio="xMidYMin slice">'
            f'<path d="{wire}" fill="none" stroke="#121345" stroke-width="2"/>{bulbs}</svg></div>')


def build_home():
    upcoming = ''.join(event_row(e, mark_next=False) for e in EVENTS)
    pillars = ''.join(pillar(i + 1, p) for i, p in enumerate(PILLARS))
    finds = discover_data()
    first = next((b for b in finds if b['n'] == 'Kalamazoo Candle Company'), finds[0])
    data = json.dumps(finds, ensure_ascii=False).replace('</', '<\\/')
    dd = '<span class="dd-badge"><span class="dd-coin" aria-hidden="true">$</span>Accepts Downtown Dollars</span>'
    body = f'''<section class="hero-weave" aria-labelledby="page-title" id="hero-weave">
  {weave.weave_svg()}
  {snow()}
  <div class="wrap hero-weave-inner">
    <div class="hero-card">
      <h1 class="display" id="page-title">Find the Holidays Downtown</h1>
      <p class="tagline">Shop. Dine. Celebrate. Find it downtown.</p>
      <p class="lede">Downtown has more to experience than you remember. Come back, explore, and make a full day or evening of it.</p>
      <div class="btn-row" style="margin-top:1.6rem">
        <a class="btn btn-primary" href="{{R}}plan.html">Plan your downtown experience</a>
        <a class="btn" href="{{R}}events.html">See holiday events</a>
      </div>
    </div>
  </div>
  <button class="weave-toggle" type="button" id="weave-toggle">Pause motion</button>
</section>

<section class="section" aria-labelledby="pillars-title">
  <div class="wrap">
    <div class="section-head"><div><p class="eyebrow">Start anywhere</p><h2 class="h2" id="pillars-title">Four ways to find the holidays</h2></div></div>
    {in_short('There are four ways to use this site: find local businesses, find things to do, find holiday traditions, and find your way around downtown.')}
    <ul class="pillars">{pillars}</ul>
  </div>
</section>

<section class="section" style="padding-top:0" aria-labelledby="upcoming-title">
  <div class="wrap">
    <div class="section-head">
      <div><p class="eyebrow">Find more to do</p><h2 class="h2" id="upcoming-title">What’s next downtown</h2></div>
      <a class="btn" href="{{R}}events.html">All 11 holiday events</a>
    </div>
    {in_short('These are the next few holiday events. Select one to see the time, place and cost.')}
    <ul class="event-list" id="upcoming">{upcoming}</ul>
  </div>
</section>

<section class="section band" aria-labelledby="discover-title">
  <div class="wrap discover">
    <div class="prose">
      <p class="eyebrow">Find something local</p>
      <h2 class="h2" id="discover-title">Around every corner</h2>
      <p>Downtown is full of small surprises: a candle you pour yourself, a toy store full of things you forgot you loved, a glass studio hidden in an old factory. Turn the corner and see what turns up.</p>
      <div class="btn-row"><button class="btn btn-primary" type="button" id="discover-next">Turn the corner</button><a class="btn" href="{{R}}directory.html">See all {len(directory_page.BIZ)} businesses</a></div>
      <p class="discover-count" id="discover-count" aria-live="polite">One of {len(finds)} downtown finds.</p>
    </div>
    <div class="discover-stage">
      <div class="discover-mat quilt-mat" id="quilt-mat" aria-hidden="true">{''.join(f'<span style="background-image:url({{R}}pattern-{n}-sm.webp)"></span>' for n in ['dots', 'squiggle', 'confetti', 'speckle', 'arcs', 'maze'])}</div>
      <article class="discover-card {first["f"]}" id="discover-card" aria-live="polite" aria-atomic="true" data-current="{first["id"]}">
        <span class="cat">{E(first["c"])}</span>
        <h3>{E(first["n"])}</h3>
        <p>{E(first["d"])}</p>
        {f'<p class="where">{E(first["w"])}</p>' if first["w"] else ''}
        <div class="foot">{dd if first["dd"] else '<span></span>'}<a href="{{R}}directory.html#b-{first["id"]}">See it in the directory<span class="sr-only">: {E(first["n"])}</span></a></div>
      </article>
    </div>
  </div>
  <script type="application/json" id="discover-data">{data}</script>
</section>

<section class="section" aria-labelledby="visit-title">
  <div class="wrap">
    <div class="section-head"><div><p class="eyebrow">Find your way</p><h2 class="h2" id="visit-title">Easy to get to, easy to get around</h2></div>
    <a class="btn" href="{{R}}visit.html">Parking and trolley details</a></div>
    <ul class="strip">
      <li class="f-blue"><span class="big">90 minutes free</span><span>In the Epic Center and Kalamazoo Mall ramps, all year.</span></li>
      <li class="f-pink"><span class="big">Free trolley</span><span>The Holly Jolly Trolley loops downtown Thursday through Sunday until Christmas Eve.</span></li>
      <li class="f-green"><span class="big">Walkable</span><span>The Kalamazoo Mall, Bronson Park and most holiday events sit within a few blocks.</span></li>
    </ul>
    <div class="construction" style="margin-top:1rem">
      <strong>Streets for All construction</strong>
      <p>Some downtown streets are being rebuilt. Downtown businesses are open throughout, and the city posts current closures and detours.</p>
      <p>{ext(STREETS_FOR_ALL, "See current Streets for All updates")}</p>
    </div>
  </div>
</section>

<section class="section" style="padding-top:0" aria-labelledby="host-title">
  <div class="wrap">
    <div class="host-band">
      <div class="copy">
        <p class="eyebrow" style="color:var(--ink)">For groups and venues</p>
        <h2 id="host-title">Hosting something downtown this season?</h2>
        <p>Shops, venues, nonprofits and community groups can add a holiday event to the downtown calendar. Every submission is reviewed, and details are confirmed before it is posted.</p>
        <ul>
          <li>Events between November 1 and December 31</li>
          <li>Held downtown, and open to the public</li>
          <li>Have the date, time, place, cost and accessibility details ready</li>
        </ul>
        <p><a class="btn btn-primary" href="{{R}}submit-event.html">Submit an event</a></p>
        <p>Own a downtown business? <a href="{{R}}businesses.html">See all the ways to take part</a>.</p>
      </div>
      <div class="art" style="background-image:url({{R}}pattern-squiggle.webp)" aria-hidden="true"></div>
    </div>
  </div>
</section>
'''
    page('holidays/index.html', 'Find the Holidays Downtown', body, 'holidays',
         'Find the Holidays Downtown: holiday events, itineraries, gift guides, local businesses and visitor information for Downtown Kalamazoo, November and December 2026.')


# ---------------------------------------------------------------- Submit an event
def build_submit():
    def field(fid, label, kind='text', req=False, help_='', attrs=''):
        star = ' <span class="req" aria-hidden="true">*</span>' if req else ''
        r = ' required aria-required="true"' if req else ''
        h = f'<p class="help" id="{fid}-help">{help_}</p>' if help_ else ''
        desc = f' aria-describedby="{fid}-help{" " if help_ else ""}{fid}-err"' if help_ else f' aria-describedby="{fid}-err"'
        if kind == 'textarea':
            ctl = f'<textarea id="{fid}" name="{fid}"{r}{desc} {attrs}></textarea>'
        else:
            ctl = f'<input type="{kind}" id="{fid}" name="{fid}"{r}{desc} {attrs}>'
        return f'<div class="field"><label for="{fid}">{label}{star}</label>{h}{ctl}<p class="err-msg" id="{fid}-err" hidden></p></div>'

    audience = ''.join(f'<label><input type="checkbox" name="audience" value="{v}"> {v}</label>' for v in
                       ['All ages', 'Families and kids', 'Students and young adults', 'Adults 21+'])
    body = page_hero([('index.html', 'Home'), ('events.html', 'Events'), ('submit-event.html', 'Submit an event')],
                     'For groups and venues', 'Submit an event',
                     'Hosting something downtown? Tell us about it and we’ll consider it for the downtown events calendar. Holiday events also appear in Find the Holidays Downtown.', 'f-pink')
    body += f'''<section class="section" aria-labelledby="form-title">
  <div class="wrap two-col">
    <div>
      {in_short('Fill in this form to add your event to the downtown calendar. Fields with a star are required. Downtown Kalamazoo staff check every event before it is posted.')}
      <h2 class="sr-only" id="form-title">Event details</h2>
      <div class="err-summary" id="err-summary" role="alert" tabindex="-1" hidden><h2>Please fix these before sending</h2><ul id="err-list"></ul></div>
      <form class="form" id="event-form" novalidate>
        <p class="help">Fields marked <span class="req">*</span> are required.</p>
        <fieldset>
          <legend>About your group</legend>
          {field('org', 'Group, business or venue name', req=True, attrs='autocomplete="organization"')}
          <div class="row2">
            {field('contact', 'Your name', req=True, attrs='autocomplete="name"')}
            {field('phone', 'Phone', 'tel', help_='Optional. Only used if we have a question.', attrs='autocomplete="tel"')}
          </div>
          {field('email', 'Email', 'email', req=True, help_='We’ll use this to confirm your event. It is not published.', attrs='autocomplete="email"')}
        </fieldset>
        <fieldset>
          <legend>About the event</legend>
          {field('title', 'Event name', req=True, attrs='maxlength="90"')}
          <div class="row2">
            {field('date', 'Date', 'date', req=True, help_='For a repeating event, give the first date and describe the schedule below.')}
            {field('end_date', 'Last day, if it runs more than one day', 'date')}
          </div>
          <div class="row2">
            {field('start', 'Start time', 'time', req=True)}
            {field('end', 'End time', 'time')}
          </div>
          <div class="row2">
            {field('venue', 'Venue or location name', req=True, help_='For example, Bronson Park or the name of your shop.')}
            {field('address', 'Street address', req=True, help_='Must be in downtown Kalamazoo.', attrs='autocomplete="street-address"')}
          </div>
          {field('description', 'Short description', 'textarea', req=True, help_='Two or three plain-language sentences about what people will see and do. Up to 400 characters.', attrs='maxlength="400"')}
          <fieldset style="border:0;padding:0">
            <legend class="label" style="font-family:var(--font-ui);font-size:.9rem;text-transform:none;padding:0">Cost <span class="req" aria-hidden="true">*</span></legend>
            <div class="choices" id="cost-group">
              <label><input type="radio" name="cost" value="Free" required> Free</label>
              <label><input type="radio" name="cost" value="Paid"> Paid or ticketed</label>
            </div>
            <p class="err-msg" id="cost-err" hidden></p>
          </fieldset>
          {field('price', 'Price', help_='If it’s paid, list the price or price range.')}
          <fieldset style="border:0;padding:0">
            <legend class="label" style="font-family:var(--font-ui);font-size:.9rem;text-transform:none;padding:0">Who it’s for</legend>
            <div class="choices">{audience}</div>
          </fieldset>
          {field('link', 'Event or ticket link', 'url', help_='Optional. Starts with https://', attrs='placeholder="https://"')}
          {field('photo', 'Photo link', 'url', help_='Optional. A link to a photo we may use, such as a shared Google Drive or Dropbox file. Please make sure you have the right to share it.', attrs='placeholder="https://"')}
        </fieldset>
        <fieldset>
          <legend>Access</legend>
          {field('access', 'Accessibility details', 'textarea', help_='Tell people what to expect: step-free entry, seating, accessible restrooms, ASL or captioning, quiet spaces, lighting or noise levels, and who to contact with access questions.')}
        </fieldset>
        <div class="field agree">
          <div class="choices"><label><input type="checkbox" id="agree" name="agree" required aria-describedby="agree-err"> I confirm these details are accurate. Downtown Kalamazoo staff may edit the listing for length and will confirm it with me before it is posted. <span class="req" aria-hidden="true">*</span></label></div>
          <p class="err-msg" id="agree-err" hidden></p>
        </div>
        <div class="btn-row"><button class="btn btn-primary" type="submit" id="event-submit">Submit event</button></div>
      </form>
      <div class="done" id="event-done" tabindex="-1" hidden></div>
    </div>
    <div class="aside">
      <section class="panel f-pink"><h2>What gets posted</h2><ul>
        <li>Events held downtown and open to the public</li>
        <li>Free or paid, for any age</li>
        <li>Holiday events between November 1 and December 31 also go in Find the Holidays Downtown</li>
      </ul><p>Staff review each submission and confirm the details with you first. Popular weekends fill up, so send events early.</p></section>
      <section class="panel"><h2>Questions?</h2><p>Email <span>downtown@kalamazoocity.org</span> <button type="button" class="btn btn-small btn-quiet" data-copy="downtown@kalamazoocity.org">Copy address</button></p><p>Or call 311.</p></section>
      <section class="panel"><h2>Own a downtown business?</h2><p>You can also join the directory, gift guides and Small Business Saturday. <a href="{{R}}businesses.html">See how to take part</a>.</p></section>
    </div>
  </div>
</section>'''
    page('submit-event.html', 'Submit an event', body, 'events',
         'Submit an event for the Downtown Kalamazoo events calendar.')

# ---------------------------------------------------------------- Newsletter
NEWS_INTERESTS = ['Weekend and holiday events', 'New shops and restaurants', 'Gift guides and deals', 'Family activities',
                  'Arts, music and culture', 'Parking and construction updates']


def welcome_dialog():
    return '''<dialog class="welcome" id="welcome-dialog" aria-labelledby="welcome-title" aria-describedby="welcome-text">
  <div class="welcome-art" aria-hidden="true" style="background-image:url({R}pattern-squiggle.webp)"></div>
  <div class="welcome-body" tabindex="-1" id="welcome-body">
    <button class="icon-btn welcome-x" type="button" data-welcome-close aria-label="Close">✕</button>
    <p class="eyebrow">Happy holidays from Downtown Kalamazoo</p>
    <h2 id="welcome-title">Welcome to Downtown Kalamazoo this holiday season</h2>
    <p id="welcome-text">We can’t wait to welcome you downtown. Join the community newsletter for weekend events, new shops, gift ideas and the occasional downtown secret.</p>
    <form class="form news-form" data-newsletter novalidate>
      <div class="news-row">
        <div class="field"><label for="w-email">Email address</label><input type="email" id="w-email" name="email" autocomplete="email" required aria-required="true" aria-describedby="w-email-err"><p class="err-msg" id="w-email-err" hidden></p></div>
        <button class="btn btn-primary" type="submit">Join the newsletter</button>
      </div>
      <p class="help">You can unsubscribe anytime. <a href="{R}newsletter.html">Choose what you hear about</a></p>
    </form>
    <div class="news-done" hidden tabindex="-1"></div>
    <p><button class="linkish" type="button" data-welcome-close>Maybe later</button></p>
  </div>
</dialog>'''


def build_newsletter():
    interests = ''.join(f'<label><input type="checkbox" name="interests" value="{E(v)}"> {E(v)}</label>' for v in NEWS_INTERESTS)
    body = page_hero([('index.html', 'Home'), ('newsletter.html', 'Newsletter')], 'Stay in the loop', 'The downtown newsletter',
                     'Weekend events, new shops, gift ideas and the occasional downtown secret, in your inbox now and then.', 'f-blue')
    body += f'''<section class="section" aria-labelledby="news-title">
  <div class="wrap two-col">
    <div>
      {in_short('Give us your email to get the Downtown Kalamazoo newsletter. Your name, ZIP code and interests are optional.')}
      <h2 class="h2" id="news-title" style="margin-bottom:1.25rem">Sign up</h2>
      <form class="form news-form" data-newsletter novalidate>
        <div class="row2">
          <div class="field"><label for="n-first">First name</label><input type="text" id="n-first" name="first" autocomplete="given-name"></div>
          <div class="field"><label for="n-zip">ZIP code</label><p class="help" id="n-zip-help">Optional. Helps us plan events for your part of town.</p><input type="text" id="n-zip" name="zip" inputmode="numeric" autocomplete="postal-code" maxlength="10" aria-describedby="n-zip-help"></div>
        </div>
        <div class="field"><label for="n-email">Email address <span class="req" aria-hidden="true">*</span></label><input type="email" id="n-email" name="email" autocomplete="email" required aria-required="true" aria-describedby="n-email-err"><p class="err-msg" id="n-email-err" hidden></p></div>
        <fieldset style="border:0;padding:0">
          <legend class="label" style="font-family:var(--font-ui);font-size:.9rem;text-transform:none;padding:0">What would you like to hear about?</legend>
          <div class="choices" style="display:grid;gap:.25rem">{interests}</div>
        </fieldset>
        <p class="help">You can unsubscribe anytime. Your email is only used for the Downtown Kalamazoo newsletter.</p>
        <div class="btn-row"><button class="btn btn-primary" type="submit">Join the newsletter</button></div>
      </form>
      <div class="done news-done" hidden tabindex="-1"></div>
    </div>
    <div class="aside">
      <section class="panel f-blue"><h2>What you’ll get</h2><ul>
        <li>What’s happening this weekend</li>
        <li>New businesses and openings</li>
        <li>Gift guides and Downtown Dollars offers</li>
        <li>Parking and Streets for All updates</li>
      </ul></section>
      <section class="panel"><h2>Hosting an event?</h2><p><a href="{{R}}submit-event.html">Submit it for the events calendar</a>.</p></section>
    </div>
  </div>
</section>'''
    page('newsletter.html', 'Newsletter', body, None, 'Sign up for the Downtown Kalamazoo community newsletter.')


# ---------------------------------------------------------------- Events index
def build_events():
    nov = ''.join(event_row(e) for e in EVENTS if e['date'][5:7] == '11')
    dec = ''.join(event_row(e) for e in EVENTS if e['date'][5:7] == '12')
    body = page_hero([('index.html', 'Home'), ('events.html', 'Holiday events')], 'November 6 – December 31, 2026',
                     'Holiday events', 'Eleven reasons to come downtown this season, from the first Art Hop of November to midnight on New Year’s Eve.', 'f-red')
    body += lights() + f'''<section class="section" aria-label="Event calendar">
  <div class="wrap">
    {in_short('Events are listed by date. November has six events and December has five. Select an event to see full details.')}
    <div class="month-head"><h2 class="h2" id="nov">November</h2><span class="muted">6 events</span></div>
    <ul class="event-list" aria-labelledby="nov">{nov}</ul>
    <div class="month-head"><h2 class="h2" id="dec">December</h2><span class="muted">5 events</span></div>
    <ul class="event-list" aria-labelledby="dec">{dec}</ul>
    <p class="note" style="margin-top:2rem">Details are confirmed with organizers before each event. Check back before you go.</p>
    <div class="panel f-pink" style="margin-top:1.5rem;max-width:46rem"><h2>Hosting a holiday event downtown?</h2><p>Groups, venues and businesses can send an event for the calendar. <a href="{{R}}submit-event.html">Submit an event</a></p></div>
  </div>
</section>'''
    page('holidays/events.html', 'Holiday events', body, 'holidays', 'Every Downtown Kalamazoo holiday event for November and December 2026.')

def build_event(i, e):
    d = dt.date.fromisoformat(e['date'])
    glance = ''.join(f'<div><dt>{E(k)}</dt><dd>{v}</dd></div>' for k, v in e['glance'])
    paras = ''.join(f'<p>{p}</p>' for p in e['body'])
    extra = ''
    if e.get('highlights'):
        extra += f'<h2 class="h3">{E(e.get("highlights_title", "What to expect"))}</h2><ul class="checks {e["fill"]}">' + ''.join(f'<li>{h}</li>' for h in e['highlights']) + '</ul>'
    if e.get('route'):
        extra += '<h2 class="h3">Parade route</h2><p class="muted">Last year’s route. It starts and ends at the staging area at Portage and Lovell streets.</p><ol class="route">' + ''.join(f'<li>{E(s)}</li>' for s in e['route']) + '</ol>'
    if e.get('hours'):
        rows = ''.join(f'<tr><th scope="row">{E(a)}</th><td>{E(b)}</td></tr>' for a, b in e['hours'])
        extra += f'<div class="table-wrap"><table><caption>{E(e["hours_caption"])}</caption><tbody>{rows}</tbody></table></div>'
    if e.get('tips'):
        extra += '<h2 class="h3">Tips</h2><ul>' + ''.join(f'<li>{t}</li>' for t in e['tips']) + '</ul>'
    if e.get('note'):
        extra += f'<p class="note">{e["note"]}</p>'
    links = ''
    if e.get('links'):
        links = '<section class="panel" aria-labelledby="links-title"><h2 id="links-title">More information</h2><ul>' + ''.join(
            f'<li>{ext(h, E(t)) if h.startswith("http") else f"<a href=\"{{R}}{h}\">{E(t)}</a>"}</li>' for t, h in e['links']) + '</ul></section>'
    pairs = ''.join(f'<li><a href="{{R}}plan/{p}.html">{E(next(x["title"] for x in PLANS if x["slug"] == p))}</a></li>' for p in e.get('plans', []))
    pair_panel = f'<section class="panel" aria-labelledby="pair-title"><h2 id="pair-title">Make a day of it</h2><ul>{pairs}</ul></section>' if pairs else ''
    prev_e = EVENTS[i - 1] if i > 0 else None
    next_e = EVENTS[i + 1] if i < len(EVENTS) - 1 else None
    pager = '<nav class="pager" aria-label="More events">'
    if prev_e: pager += f'<a href="{{R}}events/{prev_e["slug"]}.html"><span class="dir">← Previous event</span><span>{E(prev_e["title"])}</span><span class="muted">{E(prev_e["when_short"])}</span></a>'
    if next_e: pager += f'<a class="next" href="{{R}}events/{next_e["slug"]}.html"><span class="dir">Next event →</span><span>{E(next_e["title"])}</span><span class="muted">{E(next_e["when_short"])}</span></a>'
    pager += '</nav>'
    hero_extra = f'<div style="display:flex;gap:1rem;align-items:center;margin-top:1.25rem">{date_tile(e)}<p class="h3" style="font-weight:500">{E(e["when_long"])}</p></div>'
    body = page_hero([('index.html', 'Home'), ('events.html', 'Holiday events'), (f'events/{e["slug"]}.html', e['title'])],
                     E(e['eyebrow']), E(e['title']), E(e['summary']), e['fill'], hero_extra)
    body += lights(seed=i + 5) + f'''<section class="section" aria-labelledby="glance-title">
  <div class="wrap">
    <h2 class="sr-only" id="glance-title">At a glance</h2>
    <dl class="glance">{glance}</dl>
  </div>
</section>
<section class="section" style="padding-top:0" aria-labelledby="about-title">
  <div class="wrap two-col">
    <div class="prose">
      {in_short(E(e["plain"]))}
      <h2 class="h2" id="about-title">About this event</h2>
      {paras}
      {extra}
    </div>
    <div class="aside">
      {links}
      {GETTING_HERE}
      {pair_panel}
      {ACCOMMODATION}
    </div>
  </div>
</section>
<section class="section-tight"><div class="wrap">{pager}<p style="margin-top:1.25rem"><a href="{{R}}events.html">← All holiday events</a></p></div></section>'''
    page(f'holidays/events/{e["slug"]}.html', e['title'], body, 'holidays', e['summary'])

# ---------------------------------------------------------------- Plans
# The planner and plan pages are built in plan_section.py.

# ---------------------------------------------------------------- Directory
def build_directory():
    body, total = directory_page.directory_body(page_hero, in_short)
    page('directory.html', 'Explore downtown', body, 'directory', f'A directory of {total} shops, restaurants, studios and places to stay in Downtown Kalamazoo.')

# ---------------------------------------------------------------- Gifts
def build_gifts():
    toc = ''.join(f'<li><a class="chip" href="#{g["id"]}">{E(g["title"])}</a></li>' for g in GIFT_GUIDES)
    sections = ''
    for g in GIFT_GUIDES:
        ideas = ''.join(f'<li>{x}</li>' for x in g['ideas'])
        look = ' · '.join(f'<a href="{{R}}{h}">{E(t)}</a>' for t, h in g['look'])
        sections += f'''<section class="section-tight" aria-labelledby="{g["id"]}" style="border-top:1px solid var(--line)">
  <div class="two-col" style="align-items:start">
    <div class="prose">
      <h2 class="h2" id="{g["id"]}">{E(g["title"])}</h2>
      <p>{g["intro"]}</p>
      <ul class="checks {g["fill"]}">{ideas}</ul>
    </div>
    {turn_box('pick-card wrapped ' + g["fill"], f'<span class="ribbon" aria-hidden="true"></span><h3>Where to look</h3><p>{look}</p>', SD.biz(SD.GUIDE_PICKS[g["id"]], kicker='Local pick'), 'Local pick for ' + g["title"].lower(), pattern='pattern-stripes.webp')}
  </div>
</section>'''
    body = page_hero([('index.html', 'Home'), ('gifts.html', 'Gift guides')], 'Shop local', 'Gift guides',
                     'Gifts for everyone on your list, found a few blocks apart. When in doubt, Downtown Dollars fit everyone.', 'f-pink')
    body += f'''<section class="section" aria-label="Guides">
  <div class="wrap">
    {in_short('There are six gift guides. Each has ideas and a link to the places downtown where you can find them.')}
    <nav aria-label="Jump to a guide"><ul class="chips" style="margin-bottom:1.5rem">{toc}</ul></nav>
    {sections}
  </div>
</section>'''
    page('holidays/gifts.html', 'Gift guides', body, 'holidays', 'Holiday gift ideas from Downtown Kalamazoo shops, makers and venues.')

# ---------------------------------------------------------------- SBS
def build_sbs():
    sbs = next(e for e in EVENTS if e['slug'] == 'small-business-saturday')
    body = page_hero([('index.html', 'Home'), ('sbs.html', 'Small Business Saturday')], 'Saturday, November 28, 2026', 'Small Business Saturday',
                     'The Saturday after Thanksgiving is downtown’s biggest day to shop small. Start your list here, then stay for Santa.', 'f-green',
                     f'<div class="btn-row" style="margin-top:1.25rem"><a class="btn btn-primary" href="{{R}}events/small-business-saturday.html">Event details</a><a class="btn" href="{{R}}plan/shop-small.html">Shop small itinerary</a></div>')
    body += f'''<section class="section" aria-labelledby="why-title">
  <div class="wrap two-col">
    <div class="prose">
      {in_short('On November 28, shop at downtown’s local businesses. Santa’s Workshop opens the same day and visits are free.')}
      <h2 class="h2" id="why-title">Why shop small downtown</h2>
      <p>Downtown’s shops, restaurants and makers are owned by people who live here. Holiday spending at a local business stays closer to home, and it keeps the storefronts on the Kalamazoo Mall lit up all year.</p>
      <h2 class="h3">How to make the most of the day</h2>
      <ul class="checks f-green">
        <li>Bring your list and start on the Kalamazoo Mall, where shops are a short walk apart.</li>
        <li>Pay with <a href="{{R}}dollars.html">Downtown Dollars</a>, or buy some as gifts while you’re out.</li>
        <li>Stop by <a href="{{R}}events/small-business-saturday.html">Santa’s Workshop</a> at City Centre, 125 S. Kalamazoo Mall. Visits are free.</li>
        <li>Eat lunch at a downtown restaurant instead of a chain.</li>
        <li>Share what you find with <strong>#SomethingNewKalamazoo</strong>.</li>
      </ul>
      <h2 class="h3">Need ideas?</h2>
      <p>Our <a href="{{R}}gifts.html">gift guides</a> cover the art lover, the cook, the kids and everyone in between. The <a href="{{R}}directory.html">directory</a> lists places to start.</p>
    </div>
    <div class="aside">
      <section class="panel f-green"><h2>Santa’s Workshop</h2><p>Santa settles in at City Centre on Small Business Saturday. Last season’s Saturday hours were noon to 6 p.m. Bring a camera for the photo backdrops.</p></section>
      {GETTING_HERE}
      <section class="panel"><h2>Own a business?</h2><p>Get the Small Business Saturday toolkit, window decals and directory listing on the <a href="{{R}}businesses.html">For businesses</a> page.</p></section>
    </div>
  </div>
</section>'''
    page('holidays/sbs.html', 'Small Business Saturday', body, 'holidays', 'Shop small in Downtown Kalamazoo on Small Business Saturday, November 28, 2026.')

# ---------------------------------------------------------------- Dollars
def build_dollars():
    city = 'https://kalamazoocity.org/Community/Downtown-Kalamazoo/Downtown-Dollars'
    mapu = 'https://apps.conpoto.com/members/3725acad-1c4a-4e38-b149-3ee431751939/merchants/publicMap'
    faqs = [
        ('Where can I use them?', f'<p>At participating downtown restaurants, bars, shops, salons, cafés and entertainment venues. In the <a href="{{R}}directory.html#dollars">business directory</a>, look for the Accepts Downtown Dollars tag. The {ext(mapu, "Downtown Dollars merchant map")} has the official list.</p>'),
        ('How long are they good for?', '<p>Five years from the date you buy them. Promotional certificates may expire sooner, and the expiration date is printed on each one.</p>'),
        ('Do I need to print them?', '<p>No. You can show them on your phone or print them, whichever is easier.</p>'),
        ('Can I buy a lot at once for my team or clients?', '<p>Yes. For orders of $1,000 or more, email downtown@kalamazoocity.org and the downtown team will help.</p>'),
        ('Who do I contact with a problem?', '<p>Email downtown@kalamazoocity.org, call 311, or call (269) 337-8000.</p>'),
    ]
    faq_html = ''.join(f'<details><summary>{E(q)}</summary><div>{a}</div></details>' for q, a in faqs)
    body = page_hero([('index.html', 'Home'), ('dollars.html', 'Downtown Dollars')], 'The gift that stays downtown', 'Downtown Dollars',
                     'Digital gift certificates in $5, $10 and $20 amounts, good at participating downtown businesses for five years.', 'f-blue',
                     f'<div class="btn-row" style="margin-top:1.25rem">{ext(city, "Buy Downtown Dollars", "btn btn-primary")}<a class="btn" href="{{R}}directory.html#dollars">See where they’re accepted</a></div>')
    body += f'''<section class="section" aria-labelledby="how-title">
  <div class="wrap">
    {in_short('Downtown Dollars are gift certificates for downtown businesses. Buy them online, get them by email, and spend them at shops and restaurants downtown.')}
    <h2 class="h2" id="how-title" style="margin-bottom:1.25rem">How it works</h2>
    <ol class="strip" style="list-style:none">
      <li class="f-blue"><span class="big">1. Buy online</span><span>Choose $5, $10 or $20 certificates on the City of Kalamazoo’s order page.</span></li>
      <li class="f-pink"><span class="big">2. Get them by email</span><span>Your certificates arrive by email, ready to forward as a gift or print.</span></li>
      <li class="f-green"><span class="big">3. Spend downtown</span><span>Show them on your phone or on paper at any participating business.</span></li>
    </ol>
  </div>
</section>
<section class="section" style="padding-top:0" aria-labelledby="faq-title">
  <div class="wrap two-col">
    <div><h2 class="h2" id="faq-title" style="margin-bottom:1rem">Questions</h2>{faq_html}</div>
    <div class="aside">
      <section class="panel f-blue"><h2>Last-minute gift</h2><p>Because they arrive by email, Downtown Dollars still work on Christmas Eve. See <a href="{{R}}plan/last-minute.html">A last-minute downtown outing</a>.</p></section>
      <section class="panel"><h2>Businesses</h2><p>Want to accept Downtown Dollars? See <a href="{{R}}businesses.html">For businesses</a>.</p></section>
    </div>
  </div>
</section>'''
    page('dollars.html', 'Downtown Dollars', body, 'dollars', 'Downtown Dollars: digital gift certificates for Downtown Kalamazoo businesses.')

# ---------------------------------------------------------------- Visit
def build_visit():
    rates = [('First 90 minutes', 'Free'), ('Next hour', '$2'), ('Each additional half hour', '$1'), ('Daily maximum (24 hours)', '$10')]
    rate_rows = ''.join(f'<tr><th scope="row">{a}</th><td class="num">{b}</td></tr>' for a, b in rates)
    hours = [('Thursday to Sunday', 'Through December 24'), ('New Year’s Eve', 'Special run on December 31'), ('Departures', 'On the hour and half hour from City Hall')]
    hour_rows = ''.join(f'<tr><th scope="row">{a}</th><td>{b}</td></tr>' for a, b in hours)
    body = page_hero([('index.html', 'Home'), ('visit.html', 'Visit & park')], 'Getting here', 'Visit &amp; park',
                     'Where to park, how to ride the free holiday trolley, and how to get around once you’re here.', 'f-green')
    body += f'''<section class="section" aria-labelledby="park-title">
  <div class="wrap two-col">
    <div class="prose" style="max-width:none">
      {in_short('Park in the Epic Center or Kalamazoo Mall ramps, where the first 90 minutes are free. A free trolley loops downtown Thursday through Sunday.')}
      <h2 class="h2" id="park-title">Parking</h2>
      <p>The Epic Center and Kalamazoo Mall parking ramps are the closest to the Kalamazoo Mall and Bronson Park. Since April 2026, the first 90 minutes in both ramps are free all year. Street meters downtown take coins and cards at the kiosks, or the ParkMobile app.</p>
      <div class="table-wrap"><table><caption>Ramp rates during last year’s holiday season</caption><thead><tr><th scope="col">Time parked</th><th scope="col" class="num">Cost</th></tr></thead><tbody>{rate_rows}</tbody></table></div>
      <p class="note">2026 holiday parking rates will be confirmed by the City of Kalamazoo. On parade day, expect road closures along the route from mid-morning into the afternoon.</p>

      <h2 class="h2" id="trolley-title" style="margin-top:1.5rem">Holly Jolly Trolley</h2>
      <p>The free Holly Jolly Trolley loops around downtown, starting and ending at City Hall, 241 W. South St. Stops have included City Hall, the Kalamazoo Mall and Bell’s Eccentric Café.</p>
      <div class="table-wrap"><table><caption>Trolley schedule (last season)</caption><tbody>{hour_rows}</tbody></table></div>
      <p>The trolley seats 24 people. On busy nights it may be full and pass a stop, so leave a little extra time.</p>

      <h2 class="h2" style="margin-top:1.5rem">Getting around</h2>
      <p>The Kalamazoo Mall is a pedestrian street lined with shops and restaurants. Bronson Park, home to the tree lighting, December to Remember and New Year’s Fest, is a short walk west at 200 S. Rose St.</p>
    </div>
    <div class="aside">
      <section class="panel f-green"><h2>Key addresses</h2><ul>
        <li>City Hall and trolley stop: 241 W. South St.</li>
        <li>Bronson Park: 200 S. Rose St.</li>
        <li>Santa’s Workshop, City Centre: 125 S. Kalamazoo Mall</li>
      </ul></section>
      {'<section class="panel f-blue"><h2>Accessible downtown</h2><p>Accessible parking, rides, places to rest and quieter times to visit. <a href="{R}access-guide.html">See the access guide</a>.</p></section>' if SHOW_ACCESS_GUIDE else ''}
      {ACCOMMODATION}
      <section class="panel"><h2>Questions</h2><p>Call 311 or (269) 337-8000, or email 311@kalamazoocity.org.</p></section>
    </div>
  </div>
</section>'''
    page('visit.html', 'Visit & park', body, 'visit', 'Parking, the free Holly Jolly Trolley, and getting around Downtown Kalamazoo.')

# ---------------------------------------------------------------- Businesses
def build_businesses():
    steps = [
        ('Get listed', 'Add your business to the Explore downtown directory, with your website, a short description, holiday specials and accessibility details.'),
        ('Accept Downtown Dollars', 'Join the businesses that take Downtown Dollars. Customers can spend them at your door for five years.'),
        ('Host during events', 'Plan something for After Parade activities, Art Hop, Gingerbread Wonderland or Moonlight Madness, and submit it for the holiday calendar.'),
        ('Show the brand', 'Place a decal in your window, wear a sticker, and share the brand with #SomethingNewKalamazoo.'),
    ]
    step_html = ''.join(f'<li class="{f}"><span class="big">{E(a)}</span><span>{E(b)}</span></li>' for (a, b), f in zip(steps, ['f-blue', 'f-pink', 'f-green', 'f-red']))
    body = page_hero([('index.html', 'Home'), ('businesses.html', 'Holiday partner toolkit')], 'For downtown businesses', 'Holiday partner toolkit',
                     'The holiday season brings the biggest crowds of the year downtown. Here’s how to make sure they find you.', 'f-pink')
    body += f'''<section class="section" aria-labelledby="ways-title">
  <div class="wrap">
    {in_short('Businesses can join the holiday campaign four ways: get listed, accept Downtown Dollars, host something during an event, and use the new brand. Email downtown@kalamazoocity.org to start.')}
    <h2 class="h2" id="ways-title" style="margin-bottom:1.25rem">Four ways to take part</h2>
    <ul class="strip" style="grid-template-columns:repeat(auto-fit,minmax(14rem,1fr))">{step_html}</ul>
  </div>
</section>
<section class="section" style="padding-top:0" aria-labelledby="dates-title">
  <div class="wrap two-col">
    <div class="prose" style="max-width:none">
      <h2 class="h2" id="dates-title">Dates to plan around</h2>
      <ul class="event-list">{''.join(event_row(e, mark_next=False) for e in EVENTS if e.get('biz'))}</ul>
      <h2 class="h3" style="margin-top:1rem">Making your holiday event accessible</h2>
      <ul>
        <li>Keep a clear, step-free path from the door to your counter, and space to turn a wheelchair or stroller.</li>
        <li>Post prices and specials in large, high-contrast print at eye level.</li>
        <li>Offer a chair and a quieter spot for anyone who needs a break from the crowd.</li>
        <li>Add your accessibility details to your directory listing so people can plan ahead.</li>
      </ul>
    </div>
    <div class="aside">
      <section class="panel"><h2>Have an event?</h2><p><a href="{{R}}submit-event.html">Submit it for the holiday calendar</a>.</p></section>
      <section class="panel f-pink"><h2>Get started</h2><p>Email <span>downtown@kalamazoocity.org</span> <button type="button" class="btn btn-small btn-quiet" data-copy="downtown@kalamazoocity.org">Copy address</button></p><p>Tell us your business name, address, and which ways you want to take part.</p></section>
    </div>
  </div>
</section>'''
    page('holidays/businesses.html', 'Holiday partner toolkit', body, 'holidays', 'How Downtown Kalamazoo businesses can take part in the 2026 holiday campaign.')

# ---------------------------------------------------------------- Accessibility
def build_accessibility():
    items = [
        ('Standard', 'Written to meet WCAG 2.2 Level AA. Text is checked against contrast minimums in the light, dark and high-contrast themes. Brand colors appear as fills behind dark blue text so they stay readable.'),
        ('Display settings', 'Text size, theme, high contrast, reduced motion, extra text spacing, a plain typeface, underlined links, plain-language summaries, visible image descriptions and a reading ruler. Your choices are saved only in your browser and carry across every page.'),
        ('Built with', 'Native HTML links, buttons and form fields, a skip link on every page, labeled landmarks and breadcrumbs, and tables for schedules and prices so screen readers can read them row by row.'),
    ] + ([('Events', 'Every event page has a way to ask for an accommodation before you go.')] if SHOW_ACCOMMODATION else []) + [
        ('Found a barrier?', 'Email downtown@kalamazoocity.org or call 311 with what happened and what you were using. The downtown team will reply and work on a fix.'),
        ('Last reviewed', 'October 2026'),
    ]
    dl = ''.join(f'<div><dt>{E(a)}</dt><dd>{E(b)}</dd></div>' for a, b in items)
    body = page_hero([('index.html', 'Home'), ('accessibility.html', 'Accessibility')], 'Accessibility statement', 'Built for everyone downtown',
                     'A welcoming downtown should be easy for everyone to explore, online and in person. Here is the standard this site aims for.', 'f-blue')
    body += f'''<section class="section" aria-label="Statement">
  <div class="wrap">
    {in_short('This site works with screen readers, keyboards, zoom and other tools. If something gets in your way, tell us.')}
    <dl class="statement">{dl}</dl>
    <p style="margin-top:2rem"><button class="btn btn-primary" type="button" data-open-display aria-haspopup="dialog">Open display settings</button></p>
  </div>
</section>'''
    page('accessibility.html', 'Accessibility', body, None, 'Accessibility statement for the Downtown Kalamazoo website.')

# ---------------------------------------------------------------- Brand extras: K window, take-home, voices, access, 404

_KSVG = open(os.path.join(HERE, 'k-shape.svg')).read()
_KVB = [float(v) for v in re.search(r'viewBox="([^"]+)"', _KSVG).group(1).split()]
_KD = re.search(r' d="([^"]+)"', _KSVG).group(1)
# The K letterform as a clip path in 0–1 units, so any element can be cut into the shape of the K.
K_CLIP = (f'<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'
          f'<clipPath id="k-clip" clipPathUnits="objectBoundingBox"><path transform="scale({1/_KVB[2]:.6f} {1/_KVB[3]:.6f}) translate({-_KVB[0]:.2f} {-_KVB[1]:.2f})" d="{_KD}"/></clipPath>'
          f'</defs></svg>')
K_RATIO = _KVB[2] / _KVB[3]


def k_window(patterns=('quilt', 'squiggle', 'dots', 'confetti'), photo=None, cls=''):
    """The K as a window onto downtown. Holds a drifting patchwork of brand patterns until photos are ready;
    pass photo='images/….jpg' to show a photograph through the K instead."""
    if photo:
        inner = f'<div class="kw-photo" style="background-image:url({{R}}{photo})"></div>'
    else:
        inner = '<div class="kw-quilt">' + ''.join(f'<span style="background-image:url({{R}}pattern-{p}.webp)"></span>' for p in patterns) + '</div>'
    return f'<div class="k-window {cls}" aria-hidden="true" style="--k-ratio:{K_RATIO:.4f}"><div class="kw-shadow"></div><div class="kw-glass">{inner}</div></div>'


# ---------------------------------------------------------------- 404
def build_404():
    body = f'''{K_CLIP}<section class="lost" aria-labelledby="page-title">
  <div class="wrap lost-grid">
    <div>
      <p class="eyebrow">Page not found</p>
      <h1 class="display h1" id="page-title">You took a wrong turn</h1>
      <p class="lede">Downtown, that’s how you find things. The page you were looking for isn’t here, but something else is.</p>
      <div class="btn-row" style="margin-top:1.25rem"><a class="btn btn-primary" href="{{R}}index.html">Go to the homepage</a><a class="btn" href="{{R}}directory.html">Explore downtown</a></div>
      <div class="lost-find" id="lost-find" aria-live="polite" hidden></div>
    </div>
    {k_window(('quilt', 'squiggle', 'dots', 'confetti'))}
  </div>
</section>'''
    page('404.html', 'Wrong turn', body, None, 'This page isn’t here, but something else downtown is.', root='/')


# ---------------------------------------------------------------- Take a pattern home
PATTERN_LABEL = {'squiggle': 'The squiggle', 'dots': 'Snowfall dots', 'quilt': 'The quilt', 'maze': 'The maze',
                 'waves': 'Warm waves', 'confetti': 'Confetti', 'dashes': 'Dashes'}


def build_take_home():
    import downloads_data as MA
    phones = ''.join(
        f'<li><img src="{{R}}downloads/phone-{n}-thumb.webp" width="240" height="519" alt="" loading="lazy">'
        f'<a class="dl" href="{{R}}downloads/phone-{n}.jpg" download>{E(PATTERN_LABEL[n])}<span class="sr-only"> phone wallpaper</span><span class="dl-meta">JPG, 1170 × 2532</span></a></li>' for n in MA.PHONE)
    calls = ''.join(
        f'<li><img src="{{R}}downloads/call-{n}-thumb.webp" width="480" height="270" alt="" loading="lazy">'
        f'<a class="dl" href="{{R}}downloads/call-{n}.jpg" download>{E(PATTERN_LABEL[n])}<span class="sr-only"> video-call background</span><span class="dl-meta">JPG, 1920 × 1080</span></a></li>' for n in MA.CALL)
    swatches = ''.join(f'<li style="background-image:url({{R}}pattern-{n}-sm.webp)"></li>' for n in PATTERNS)
    body = K_CLIP + page_hero([('index.html', 'Home'), ('take-home.html', 'Take a pattern home')], 'Made for downtown', 'Take a pattern home',
                              'The patterns made for Downtown Kalamazoo, ready for your phone, your next video call, or a rainy afternoon with crayons.', 'f-pink')
    body += f'''<section class="section" aria-labelledby="pat-title">
  <div class="wrap pattern-intro">
    <div class="prose">
      {in_short('Download free phone wallpapers, video-call backgrounds and coloring pages made from the Downtown Kalamazoo patterns.')}
      <h2 class="h2" id="pat-title">Twelve patterns, one downtown</h2>
      <p>When the new Downtown Kalamazoo brand launched, it came with a library of patterns: squiggles, confetti, snowfall dots, rainbow arcs and more. You’ll spot them on street banners, in shop windows and all over this site.</p>
      <p>Each part of this site has its own pattern, so you can tell where you are by texture as well as color. The directory is the maze. Holiday events are confetti. Gift guides are wrapped in stripes.</p>
      <ul class="swatches" aria-hidden="true">{swatches}</ul>
    </div>
    {k_window(('arcs', 'speckle', 'maze', 'squiggle'), cls='k-window-sm')}
  </div>
</section>
<section class="section band" aria-labelledby="phone-title">
  <div class="wrap">
    <h2 class="h2" id="phone-title">Phone wallpapers</h2>
    <p class="muted" style="margin:.25rem 0 1.25rem">Sized for most phones. On a phone, press and hold a download to save it to your photos.</p>
    <ul class="downloads phones">{phones}</ul>
  </div>
</section>
<section class="section" aria-labelledby="call-title">
  <div class="wrap">
    <h2 class="h2" id="call-title">Video-call backgrounds</h2>
    <p class="muted" style="margin:.25rem 0 1.25rem">For Zoom, Teams or Google Meet, with the Downtown Kalamazoo logo in the corner.</p>
    <ul class="downloads calls">{calls}</ul>
  </div>
</section>
<section class="section" style="padding-top:0" aria-labelledby="color-title">
  <div class="wrap two-col" style="align-items:center">
    <div class="prose">
      <h2 class="h2" id="color-title">Color your downtown</h2>
      <p>Six coloring pages, each one a downtown pattern in outline. Print them for a family afternoon, a classroom, or a break between holiday errands.</p>
      <p><a class="btn btn-primary" href="{{R}}downloads/coloring-pages.pdf" download>Download the coloring pages<span class="sr-only"> (PDF, 6 pages)</span></a></p>
      <p class="muted">PDF, 6 letter-size pages. Share what you color with #SomethingNewKalamazoo.</p>
    </div>
    <img class="sheet-preview" src="{{R}}downloads/coloring-thumb.webp" width="360" height="466" loading="lazy" alt="The first coloring page: the squiggle pattern in outline under the heading Color your downtown.">
  </div>
</section>
<section class="section band" aria-labelledby="craft-title">
  <div class="wrap two-col" style="align-items:center">
    <div class="prose">
      <p class="eyebrow">For the holidays</p>
      <h2 class="h2" id="craft-title">Holiday color &amp; craft pack</h2>
      <p>Seven pages of downtown patterns in holiday shapes: color the K, deck six ornaments, build a patchwork tree, match a pair of mittens, cut out gift tags, piece together a downtown quilt, and design a pattern of your own.</p>
      <p><a class="btn btn-primary" href="{{R}}downloads/holiday-color-craft-pack.pdf" download>Download the craft pack<span class="sr-only"> (PDF, 7 pages)</span></a></p>
      <p class="muted">PDF, 7 letter-size pages. Great for Gingerbread Wonderland week, classrooms and kids’ tables at holiday dinners.</p>
    </div>
    <img class="sheet-preview" src="{{R}}downloads/craft-pack-thumb.webp" width="360" height="466" loading="lazy" alt="The first craft page: the Downtown Kalamazoo K in outline, filled with the squiggle pattern, under the heading Color the K.">
  </div>
</section>
<section class="section-tight"><div class="wrap"><p class="note">These downloads are free for personal use. Businesses and partners looking for brand files can email downtown@kalamazoocity.org.</p></div></section>'''
    page('take-home.html', 'Take a pattern home', body, None, 'Free Downtown Kalamazoo pattern wallpapers, video-call backgrounds, coloring pages and a holiday craft pack.')


# ---------------------------------------------------------------- Share your downtown
VOICES = []   # Add answers people have agreed to share: dict(quote='…', name='First name', who='Lives downtown')


def build_voices():
    voices = ''
    if VOICES:
        voices = '<ul class="voices">' + ''.join(
            f'<li class="{["f-green", "f-pink", "f-blue", "f-red"][i % 4]}"><blockquote><p>{E(v["quote"])}</p></blockquote><p class="who">{E(v["name"])}{", " + E(v["who"]) if v.get("who") else ""}</p></li>'
            for i, v in enumerate(VOICES)) + '</ul>'
    conn = ''.join(f'<option>{E(o)}</option>' for o in ['Choose one (optional)', 'I live downtown', 'I live in Kalamazoo', 'I work downtown', 'I study nearby', 'I own a downtown business', 'I’m visiting'])
    body = page_hero([('index.html', 'Home'), ('your-downtown.html', 'Share your downtown')], 'You spoke. We listened.', 'Why downtown?',
                     'The new Downtown Kalamazoo brand started with what you told us you love. Keep telling us. Some answers will show up here and around downtown.', 'f-green')
    body += f'''<section class="section" aria-labelledby="share-title">
  <div class="wrap two-col">
    <div>
      {in_short('Tell us, in a sentence or two, what you love about downtown Kalamazoo. Only the first box is required.')}
      <h2 class="h2" id="share-title" style="margin-bottom:1.25rem">Tell us</h2>
      <div class="err-summary" id="v-err-summary" role="alert" tabindex="-1" hidden><h2>Please fix these before sending</h2><ul></ul></div>
      <form class="form" id="voice-form" data-mailform data-subject="Why downtown? A community answer" novalidate>
        <div class="field"><label for="v-love">What do you love about downtown? <span class="req" aria-hidden="true">*</span></label>
          <p class="help" id="v-love-help">A sentence or two is perfect. Up to 280 characters.</p>
          <textarea id="v-love" name="What they love" maxlength="280" required aria-required="true" aria-describedby="v-love-help v-love-err"></textarea><p class="err-msg" id="v-love-err" hidden></p></div>
        <div class="field"><label for="v-corner">Your favorite downtown corner</label><p class="help" id="v-corner-help">Optional. A shop, a bench, a view, a street.</p><input type="text" id="v-corner" name="Favorite corner" maxlength="120" aria-describedby="v-corner-help"></div>
        <div class="row2">
          <div class="field"><label for="v-name">First name</label><p class="help" id="v-name-help">Optional. How we’d credit you.</p><input type="text" id="v-name" name="First name" autocomplete="given-name" aria-describedby="v-name-help"></div>
          <div class="field"><label for="v-who">You…</label><p class="help" id="v-who-help">Optional.</p><select id="v-who" name="Connection" aria-describedby="v-who-help">{conn}</select></div>
        </div>
        <div class="field"><label for="v-email">Email</label><p class="help" id="v-email-help">Optional. Only if we may follow up with you. It is never published.</p><input type="email" id="v-email" name="Email" autocomplete="email" aria-describedby="v-email-help v-email-err"><p class="err-msg" id="v-email-err" hidden></p></div>
        <div class="field agree"><div class="choices"><label><input type="checkbox" id="v-ok" name="Permission to share" value="Yes" required aria-describedby="v-ok-err"> Downtown Kalamazoo may share my answer, with my first name, on this site, in print and on social media. <span class="req" aria-hidden="true">*</span></label></div><p class="err-msg" id="v-ok-err" hidden></p></div>
        <div class="btn-row"><button class="btn btn-primary" type="submit">Send my answer</button></div>
      </form>
      <div class="done" id="voice-done" tabindex="-1" hidden></div>
    </div>
    <div class="aside">
      <section class="panel f-green"><h2>Creative. Welcoming. Rooted.</h2><p>Those three words came from people who love downtown. Your answer helps shape how downtown tells its story.</p></section>
      <section class="panel"><h2>More ways to take part</h2><ul>
        <li><a href="{{R}}newsletter.html">Get the newsletter</a></li>
        <li><a href="{{R}}submit-event.html">Submit a holiday event</a></li>
        <li><a href="{{R}}take-home.html">Take a pattern home</a></li>
      </ul></section>
    </div>
  </div>
</section>
{f'<section class="section" style="padding-top:0" aria-labelledby="voices-title"><div class="wrap"><h2 class="h2" id="voices-title" style="margin-bottom:1.25rem">In your words</h2>{voices}</div></section>' if voices else ''}'''
    page('your-downtown.html', 'Why downtown?', body, None, 'Tell us what you love about Downtown Kalamazoo.')


# ---------------------------------------------------------------- Accessible downtown
ACCESS_SOURCES = [
    ('City of Kalamazoo: Downtown parking updates (2026)', 'https://www.kalamazoocity.org/News-articles/Downtown-Parking-Updates-Take-Effect-to-Improve-Parking-Access-and-Availability'),
    ('Downtown parking changes flyer (March 2026)', 'https://assets.simpleviewinc.com/simpleview/image/upload/v1/clients/kalamazoo/Downtown_Parking_Changes_Flyer_UPDATED_March_2026_d6fec8f7-15cf-4386-848b-b0f6ce901912.pdf'),
    ('Kalamazoo Metro: Metro Connect details', 'https://www.kmetro.com/metro-connect/metro-connect-details'),
    ('Kalamazoo Metro: Kalamazoo Transportation Center', 'https://www.kmetro.com/riding/kalamazoo-transportation-center'),
    ('Kalamazoo Public Library: Getting to Central Library', 'https://www.kpl.gov/central/getting-here/'),
]


def build_access():
    src = ''.join(f'<li>{ext(h, E(t))}</li>' for t, h in ACCESS_SOURCES)
    body = page_hero([('index.html', 'Home'), ('visit.html', 'Visit & park'), ('access-guide.html', 'Accessible downtown')], 'Find your way', 'Accessible downtown',
                     'Accessible parking, rides, places to rest and quieter times to visit, so you can plan the downtown day that works for you.', 'f-blue')
    body += f'''<section class="section" aria-labelledby="ag-park">
  <div class="wrap two-col">
    <div class="prose" style="max-width:none">
      {in_short('The first 90 minutes are free in two downtown parking ramps. Metro Connect gives curb-to-curb rides anywhere in Kalamazoo County. If you need an accommodation at an event, ask ahead by email or by calling 311.')}
      <h2 class="h2" id="ag-park">Parking</h2>
      <ul>
        <li>The Epic Center and Kalamazoo Mall parking ramps are free for the first 90 minutes.</li>
        <li>The city has been adding accessible (barrier-free) parking spaces on downtown blocks that didn’t have them, along with new curb ramps.</li>
        <li>On-street meters are paid at kiosks that take coins, credit and debit cards, or with the ParkMobile app.</li>
        <li>Questions about the ramps: call Park Kalamazoo at (269) 342-6383.</li>
      </ul>

      <h2 class="h2" style="margin-top:1.5rem">Buses and rides</h2>
      <ul>
        <li><strong>Kalamazoo Transportation Center</strong>, 459 N. Burdick St., is the downtown hub for Metro buses, Amtrak and intercity buses. The building is open every day, 8 a.m. to 10 p.m.</li>
        <li><strong>Metro Connect</strong> offers shared, curb-to-curb rides anywhere in Kalamazoo County. Anyone can register. Riders 62 and older and certified riders with disabilities pay a reduced fare.</li>
        <li><strong>ADA paratransit</strong> is available for people whose disability prevents them from using Metro’s fixed-route buses some or all of the time.</li>
        <li>To apply for ADA paratransit or ask for a reasonable modification on a bus route, call Metro at (269) 337-8222. For fares and passes, call (269) 337-8858.</li>
        <li>Riding the free Holly Jolly Trolley and need a ramp or lift? Call 311 before you go to check.</li>
      </ul>

      <h2 class="h2" style="margin-top:1.5rem">Getting around</h2>
      <ul>
        <li>The Kalamazoo Mall is a pedestrian street, so the heart of downtown shopping is free of car traffic.</li>
        <li>Kalamazoo installed curb cuts as a pilot project in the 1940s to help veterans with disabilities get to work.</li>
        <li>Some streets are being rebuilt through Streets for All. Detours can change sidewalk routes, so {ext(STREETS_FOR_ALL, "check current closures")} before you go.</li>
      </ul>

      <h2 class="h2" style="margin-top:1.5rem">A place to sit and warm up</h2>
      <p>The Kalamazoo Public Library’s Central Library, 315 S. Rose St., is a block from Bronson Park and open to everyone. Call (269) 553-7800 for hours and access details.</p>

      <h2 class="h2" style="margin-top:1.5rem">Crowds and quieter times</h2>
      <ul>
        <li>The Holiday Parade draws close to 30,000 people along its route. If crowds are hard for you, arrive early to find a spot with room around you, or plan your downtown visit for another day.</li>
        <li>Event nights like Art Hop and Moonlight Madness bring big crowds. For a calmer visit, try a weekday during the day.</li>
      </ul>

      <h2 class="h2" style="margin-top:1.5rem">At holiday events</h2>
      <p>Ask for what would help you enjoy an event, like seating, an ASL interpreter, captioning or a quiet space. Email downtown@kalamazoocity.org or call 311, ideally a week ahead. Each event page has the details.</p>

      <h2 class="h3" style="margin-top:2rem">Sources</h2>
      <ul class="sources">{src}</ul>
      <p class="note">Last checked October 2026. Details change, so call ahead if something is essential to your visit.</p>
    </div>
    <div class="aside">
      <section class="panel f-blue"><h2>On this website</h2><p>Change text size, contrast, spacing, the typeface and motion in Display settings. Your choices are saved on this device.</p><p><button class="btn btn-small" type="button" data-open-display aria-haspopup="dialog">Open display settings</button></p></section>
      <section class="panel"><h2>Something missing or wrong?</h2><p>Tell us about a barrier downtown or on this site. Email downtown@kalamazoocity.org or call 311.</p></section>
      <section class="panel"><h2>Plan your visit</h2><ul><li><a href="{{R}}visit.html">Parking and trolley</a></li><li><a href="{{R}}events.html">Holiday events</a></li><li><a href="{{R}}accessibility.html">This site’s accessibility statement</a></li></ul></section>
    </div>
  </div>
</section>'''
    page('access-guide.html', 'Accessible downtown', body, 'visit', 'Accessible parking, transit, places to rest and quieter times to visit Downtown Kalamazoo.')


# ---------------------------------------------------------------- Itinerary postcards
POSTCARD_PATTERNS = ['squiggle', 'arcs', 'dots', 'confetti', 'quilt', 'speckle']


def postcard_bits(i, p):
    stops = [dict(t=s['time'], p=re.sub(r'<[^>]+>', '', s['place'])) for s in p['stops']]
    data = json.dumps(dict(title=p['title'], tag=p['tag'], slug=p['slug'], stops=stops, pat=POSTCARD_PATTERNS[i % len(POSTCARD_PATTERNS)]),
                      ensure_ascii=False).replace('</', '<\\/')
    panel = ('<section class="panel f-pink postcard-panel" aria-labelledby="pc-title"><h2 id="pc-title">Make it a postcard</h2>'
             '<p>Turn this plan into a picture to save, text to a friend or post with #SomethingNewKalamazoo.</p>'
             '<p><button class="btn btn-small" type="button" data-postcard aria-haspopup="dialog">Make a postcard</button></p></section>')
    dialog = '''<dialog class="postcard-dialog" id="postcard-dialog" aria-labelledby="pcd-title">
  <div class="dialog-inner">
    <div class="dialog-head"><div><h2 id="pcd-title">Your downtown postcard</h2><p>Save it, or share it with whoever’s coming along.</p></div>
      <button class="icon-btn" type="button" data-pc-close aria-label="Close postcard">✕</button></div>
    <div class="pc-stage"><p class="pc-wait" id="pc-wait">Drawing your postcard…</p><img id="pc-img" alt="" hidden></div>
    <div class="dialog-actions"><button class="btn" type="button" id="pc-share" hidden>Share</button><a class="btn btn-primary" id="pc-save" download hidden>Save image</a></div>
  </div>
</dialog>'''
    return panel, dialog + f'<script type="application/json" id="postcard-data">{data}</script>'


exec(open(os.path.join(HERE, 'plan_section.py'), encoding='utf-8').read())

# The permanent, year-round pages live in their own file so they're easier to find and edit.
exec(open(os.path.join(HERE, 'yearround_section.py'), encoding='utf-8').read())

if __name__ == '__main__':
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copy(os.path.join(HERE, 'dk-logo-green.png'), os.path.join(OUT, 'dk-logo-green.png'))
    for n in PATTERNS:
        shutil.copy(os.path.join(HERE, f'pattern-{n}.webp'), os.path.join(OUT, f'pattern-{n}.webp'))
    shutil.copy(os.path.join(HERE, 'logo-reverse.png'), os.path.join(OUT, 'logo-reverse.png'))
    assets = os.path.join(HERE, 'assets_out')   # made by make_assets.py
    for root_, _, fs in os.walk(assets):
        for f in fs:
            src = os.path.join(root_, f); dst = os.path.join(OUT, os.path.relpath(src, assets))
            os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copy(src, dst)
    build_home(); build_submit(); build_newsletter(); build_events(); build_plan_index(); build_directory(); build_gifts(); build_sbs(); build_dollars(); build_visit(); build_businesses(); build_accessibility()
    build_404(); build_take_home(); build_voices()
    if SHOW_ACCESS_GUIDE:
        build_access()
    build_year_round()
    if os.path.isdir(os.path.join(HERE, 'files')):
        shutil.copytree(os.path.join(HERE, 'files'), os.path.join(OUT, 'files'), dirs_exist_ok=True, ignore=shutil.ignore_patterns('README.md'))
    for i, e in enumerate(EVENTS): build_event(i, e)
    for i, p in enumerate(PLANS): build_plan(i, p)
    build_builder()
    n = sum(len(f) for _, _, f in os.walk(OUT))
    print('built', n, 'files')
