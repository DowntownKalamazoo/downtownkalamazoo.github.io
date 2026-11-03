"""Business directory page: flip cards built from directory.json (made by import_directory.py)."""
import json, os, re, urllib.parse, html

E = html.escape
HERE = os.path.dirname(os.path.abspath(__file__))
BIZ = json.load(open(os.path.join(HERE, 'directory.json')))
# Gift names by business id, set by build.py from content/gift-guide.yml during the holiday season.
# Businesses with a gift get an "In the Gift Guide" tag and a directory filter.
GIFTS = {}


def _hours_lines(h):
    """Hours from directory-updates.yml, as a list of lines. Accepts a list, or one string with lines split by ';'."""
    if not h:
        return []
    if isinstance(h, str):
        h = h.split(';')
    return [str(x).strip() for x in h if str(x).strip()]


def _apply_updates():
    """Layer staff edits from content/directory-updates.yml on top of directory.json."""
    import content_loader
    up = content_loader.directory_updates()
    hide = set((up.get('hide') or {}).keys())
    BIZ[:] = [b for b in BIZ if b['id'] not in hide]
    by_id = {b['id']: b for b in BIZ}
    missing = [i for i in list((up.get('update') or {}).keys()) + list(up.get('social_district') or []) if i not in by_id]
    if missing:
        print('directory-updates.yml: no business with these ids (check spelling):', ', '.join(missing))
    fills = {}
    for b in BIZ:
        fills.setdefault(b['cat'], b['fill'])
    labels = dict(BIZ_CATS)
    for bid, fields in (up.get('update') or {}).items():
        if bid in by_id and fields:
            b = by_id[bid]
            b.update(fields)
            # Keep the fields that are worked out from others in step with the change.
            if 'phone' in fields:
                b['tel'] = ('tel:+1' + re.sub(r'\D', '', b['phone'])[-10:]) if b['phone'] else ''
            if 'address' in fields:
                b['where'] = re.sub(r',\s*Kalamazoo.*$', '', b['address'])
            if 'cat' in fields:
                b['cat_label'] = labels.get(b['cat'], b['cat'].title())
                b['fill'] = fills.get(b['cat'], b['fill'])
    for b in BIZ:
        b.setdefault('sd', False)
        b['hours'] = _hours_lines(b.get('hours'))
    for bid in up.get('social_district') or []:
        if bid in by_id:
            by_id[bid]['sd'] = True
    # Other names a business goes by, so an event's where: line or a form submission still finds it
    for bid, names in (up.get('aliases') or {}).items():
        if bid in by_id:
            by_id[bid]['aliases'] = [str(n) for n in (names if isinstance(names, list) else [names]) if str(n).strip()]
        else:
            print(f'directory-updates.yml: aliases: no business with the id {bid} (check spelling)')
    for a in up.get('add') or []:
        name = a['name'].strip()
        bid = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
        if bid in by_id:
            continue
        cat = a.get('cat', 'dine')
        addr = a.get('address', '')
        b = dict(id=bid, name=name, cat=cat, cat_label=labels.get(cat, cat.title()), fill=a.get('fill') or fills.get(cat, 'f-green'),
                 address=addr, where=re.sub(r',\s*Kalamazoo.*$', '', addr), phone=a.get('phone', ''), tel=('tel:' + re.sub(r'\D', '', a['phone'])) if a.get('phone') else '',
                 website=a.get('website', ''), desc=a.get('desc') or ('Part of the downtown Social District.' if a.get('social_district') else ''),
                 desc_es='', includes='', dd=bool(a.get('downtown_dollars')), featured=False, sd=bool(a.get('social_district')),
                 hours=_hours_lines(a.get('hours')))
        BIZ.append(b); by_id[bid] = b
    BIZ.sort(key=lambda b: re.sub(r'^the\s+', '', b['name'].lower()))
BIZ_CATS = [('shop', 'Shop'), ('dine', 'Dine'), ('arts', 'Arts & Entertainment'), ('services', 'Services'), ('stay', 'Stay'),
            ('offices', 'Offices & professional'), ('orgs', 'Organizations')]
# Kinds of places a visitor would plan a stop around. Offices and organizations stay out of Plan your day and the homepage picks.
VISITOR_CATS = {'shop', 'dine', 'arts', 'services', 'stay'}
# How the result count names a category when the label alone would read oddly ("Showing 3 of 206 organizations")
CAT_NOUN = {'offices': ' data-noun="offices and professional firms"', 'orgs': ' data-noun="organizations"'}
_apply_updates()

# Each kind of business has its own brand pattern, so categories differ by texture as well as color.
CAT_PATTERN = {'shop': 'confetti', 'dine': 'dots', 'arts': 'arcs', 'services': 'dashes', 'stay': 'loops', 'offices': 'pinstripes', 'orgs': 'quilt'}
FLIP_ICON = ('<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
             'stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 0 1 15.5-6.2L21 8"/><path d="M21 3v5h-5"/>'
             '<path d="M21 12a9 9 0 0 1-15.5 6.2L3 16"/><path d="M3 21v-5h5"/></svg>')


def ext(href, text):
    return f'<a href="{E(href)}" target="_blank" rel="noopener">{text}<span class="sr-only"> (opens in a new tab)</span></a>'


def dd_badge(label='Accepts Downtown Dollars'):
    return f'<span class="dd-badge"><span class="dd-coin" aria-hidden="true">$</span>{label}</span>'


def gift_badge(label='In the Gift Guide'):
    return ('<span class="gift-badge"><span class="gift-swatch" aria-hidden="true" style="background-image:url({R}pattern-stripes-sm.webp)"></span>'
            f'{label}</span>')


def ev_badge(label='Events coming up'):
    return ('<span class="ev-badge"><span class="gift-swatch" aria-hidden="true" style="background-image:url({R}pattern-confetti-sm.webp)"></span>'
            f'{label}</span>')


def _and(names):
    return names[0] if len(names) == 1 else ', '.join(names[:-1]) + ' and ' + names[-1]


def sd_badge():
    return '<span class="sd-badge"><span class="sd-cup" aria-hidden="true"></span>Social District</span>'


# Upcoming events by business id, set by yearround_section.py from event files that say `business: <id>`.
EVENTS = {}
TODAY = None   # the build's date, set with EVENTS so a run that has started reads "Now through …"


def norm_name(s):
    """A business name reduced for matching: lowercase, "&" read as "and", no leading "The", no punctuation.
    "The Sit & Stay Winery!" and "sit and stay winery" both become "sit and stay winery". site.js does the same
    for the event form, so keep the two in step."""
    s = str(s or '').lower().replace('&', ' and ').replace('’', "'")
    s = re.sub(r"[^a-z0-9 ]+", ' ', s.replace("'", ''))
    s = re.sub(r'\s+', ' ', s).strip()
    return re.sub(r'^the ', '', s)


def name_index():
    """{normalized name or alias: business id}. A name two businesses share is left out, so it never links to the wrong one."""
    idx, clash = {}, set()
    for b in BIZ:
        for n in [b['name']] + list(b.get('aliases') or []):
            k = norm_name(n)
            if not k:
                continue
            if k in idx and idx[k] != b['id']:
                clash.add(k)
            idx[k] = b['id']
    for k in clash:
        idx.pop(k, None)
    return idx
_MON = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
_DOW = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
_DAY = {d.lower(): i for i, d in enumerate(_DOW)}
_T = r'(?:\d{1,2}(?::\d{2})?(?:am|pm)?|noon|midnight)'
_TIME = re.compile(rf'^{_T}\s*[–-]\s*{_T}(?:\s+and\s+{_T}\s*[–-]\s*{_T})?$', re.I)
_DAYTOK = re.compile(r'^(mon|tue|wed|thu|fri|sat|sun)[a-z]*\.?(?:[–-](mon|tue|wed|thu|fri|sat|sun)[a-z]*\.?)?,?$', re.I)


def week_hours(lines):
    """Hours as {weekday: text} for the card's "Open today" line, with weekday 0 = Sunday to match the browser.
    "" means closed that day. Returns None unless every line reads plainly, like "Tue–Thu 2–8pm", "Sat noon–9pm",
    "Daily 11am–6pm" or "Mon closed"; a line with no days or times in it (a note like "Call ahead") is skipped.
    Anything else ("Box office Mon–Fri…", "Sat brunch 10am–2pm") means no "Open today" line, rather than a wrong one."""
    week = {}
    for line in lines or []:
        toks = line.replace(',', ', ').split()
        days, i = [], 0
        if toks and toks[0].lower() in ('daily', 'everyday'):
            days, i = list(range(7)), 1
        else:
            while i < len(toks) and _DAYTOK.match(toks[i].strip()):
                m = _DAYTOK.match(toks[i].strip())
                a, b = _DAY[m.group(1).lower()], _DAY[(m.group(2) or m.group(1)).lower()]
                days += [(a + k) % 7 for k in range((b - a) % 7 + 1)]
                i += 1
        rest = ' '.join(toks[i:]).strip()
        if not days:
            if re.search(r'\d|\b(mon|tue|wed|thu|fri|sat|sun)', line, re.I):
                return None
            continue
        if rest.lower() == 'closed':
            text = ''
        elif _TIME.match(rest):
            text = rest
        else:
            return None
        for d in days:
            week[str((d + 1) % 7)] = text
    return week or None


def _when(o):
    """When an event is, for cards and the Hosted by box: "Tue, Nov 3 · 6–8 p.m.", or for a run of days
    "Nov 5–22" (or "Now through Nov 22" once it has started)."""
    d, end = o['date'], o.get('end')
    if end:
        import datetime as _dt
        if d <= (TODAY or _dt.date.today()):
            day = f'Now through {_MON[end.month]} {end.day}'
        elif end.month == d.month:
            day = f'{_MON[d.month]} {d.day}–{end.day}'
        else:
            day = f'{_MON[d.month]} {d.day} – {_MON[end.month]} {end.day}'
    else:
        day = f'{_DOW[d.weekday()]}, {_MON[d.month]} {d.day}'
    return day + (f' · {o["time"]}' if o.get('time') else '')


def biz_card(b):
    bid = 'b-' + b['id']
    none = '<span class="none">Not listed yet</span>'
    links = []
    if b['address']:
        maps = 'https://www.google.com/maps/search/?api=1&query=' + urllib.parse.quote(b['name'] + ', ' + b['address'])
        links.append(ext(maps, 'Directions'))
    if b['tel']:
        phone = f'<a href="{E(b["tel"])}">{E(b["phone"])}</a>'
    else:
        phone = E(b['phone']) if b['phone'] else none
    if b['website']:
        links.append(ext(b['website'], 'Website'))
    hours = '<br>'.join(E(x) for x in b.get('hours') or []) or none
    desc = f'<p class="biz-desc">{E(b["desc"])}</p>' if b['desc'] else ''
    if b['includes']:
        desc += f'<p class="biz-desc"><strong>Inside:</strong> {E(b["includes"])}</p>'
    gifts = GIFTS.get(b['id']) or []
    if gifts:
        links.append(f'<a href="{{R}}gifts.html#from-{b["id"]}">Gift ideas</a>')
    evs = EVENTS.get(b['id']) or []
    facts = f'<div><dt>Hours</dt><dd>{hours}</dd></div><div><dt>Phone</dt><dd>{phone}</dd></div>'
    front_next = ''
    if evs:
        nxt = evs[0]
        facts += (f'<div><dt>Next event</dt><dd><a href="{{R}}{nxt["href"]}">{E(nxt["title"])}</a><br>{E(_when(nxt))}</dd></div>')
        front_next = (f'<p class="biz-next"><span class="lbl">Next event</span> <span class="t">{E(nxt["title"])}</span>'
                      f'<span class="d">{E(_when(nxt))}</span></p>')
        links.append(f'<a href="{{R}}events.html?at={b["id"]}#list">All {len(evs)} upcoming events</a>' if len(evs) > 1
                     else f'<a href="{{R}}{nxt["href"]}">Event details</a>')
    week = week_hours(b.get('hours'))
    today = (f'<p class="biz-today" data-hours="{E(json.dumps(week, ensure_ascii=False))}" hidden></p>' if week else '')
    search = ' '.join([b['name'], b['cat_label'], b['address'], b['where'], b['desc'], b['includes'],
                       'downtown dollars' if b['dd'] else '', 'social district' if b.get('sd') else '',
                       'gift guide holiday gifts ' + ' '.join(gifts) if gifts else '',
                       'events ' + ' '.join(o['title'] for o in evs) if evs else '']).lower()
    initial = re.sub(r'^the\s+', '', b['name'], flags=re.I)[:1].upper()
    tags = ((dd_badge('Downtown Dollars') if b['dd'] else '') + (sd_badge() if b.get('sd') else '')
            + (gift_badge('Gift Guide') if gifts else '') + (ev_badge('Events') if evs else ''))
    where = f'<p class="biz-where">{E(b["where"])}</p>' if b['where'] else ''
    link_list = ('<ul class="biz-links">' + ''.join(f'<li>{x}</li>' for x in links) + '</ul>') if links else ''
    name = E(b['name'])
    return (
        f'<li class="biz {b["fill"]}" style="--cat-pat:url({{R}}pattern-{CAT_PATTERN.get(b["cat"], "squiggle")}-sm.webp)" id="{bid}" data-cat="{b["cat"]}" data-dd="{1 if b["dd"] else 0}" data-sd="{1 if b.get("sd") else 0}" data-gift="{1 if gifts else 0}" data-ev="{1 if evs else 0}" data-search="{E(search)}">'
        f'<div class="biz-inner">'
        f'<article class="face front" aria-labelledby="{bid}-n">'
        f'<div class="front-band" aria-hidden="true"><span class="cat">{E(b["cat_label"])}</span><span class="initial">{E(initial)}</span></div>'
        f'<div class="front-body">'
        f'<h3 class="biz-name" id="{bid}-n"><button type="button" class="flip-btn" aria-expanded="false" aria-controls="{bid}-back">{name}</button></h3>'
        f'{where}{today}{front_next}'
        f'<div class="front-foot"><div class="biz-tags">{tags}</div><span class="flip-cue" aria-hidden="true">{FLIP_ICON}'
        f'<span class="cue-hover">Hover for details</span><span class="cue-touch">Tap for details</span></span></div>'
        f'</div></article>'
        f'<section class="face back" id="{bid}-back" aria-label="{name} details" inert>'
        f'<div class="back-head"><span class="cat">{E(b["cat_label"])}</span><p class="back-name" aria-hidden="true">{name}</p></div>'
        f'<div class="back-body" tabindex="-1">{desc}'
        f'<dl class="biz-facts">{facts}</dl>{link_list}'
        f'<div class="back-foot"><button type="button" class="btn btn-small btn-quiet flip-back">Flip back'
        f'<span class="sr-only"> to {name}</span></button></div>'
        f'</div></section></div></li>'
    )


def directory_body(page_hero, in_short):
    total = len(BIZ)
    n_dd = sum(1 for b in BIZ if b['dd'])
    n_sd = sum(1 for b in BIZ if b.get('sd'))
    n_gift = sum(1 for b in BIZ if GIFTS.get(b['id']))
    gift_chip = (f'<button type="button" class="chip chip-gift" id="dir-gift" aria-pressed="false" aria-describedby="dd-label">'
                 f'<span class="gift-swatch" aria-hidden="true" style="background-image:url({{R}}pattern-stripes-sm.webp);margin-inline-end:.4rem"></span>'
                 f'In the Holiday Gift Guide<span class="n">{n_gift}</span></button>') if n_gift else ''
    n_ev = sum(1 for b in BIZ if EVENTS.get(b['id']))
    ev_chip = (f'<button type="button" class="chip chip-ev" id="dir-ev" aria-pressed="false" aria-describedby="dd-label">'
               f'<span class="gift-swatch" aria-hidden="true" style="background-image:url({{R}}pattern-confetti-sm.webp);margin-inline-end:.4rem"></span>'
               f'Events coming up<span class="n">{n_ev}</span></button>') if n_ev else ''
    counts = {c: sum(1 for b in BIZ if b['cat'] == c) for c, _ in BIZ_CATS}
    # A type with no businesses left (offices, since November 2026) gets no filter button.
    chips = (f'<li><button type="button" class="chip" data-cat="all" data-label="All" aria-pressed="true">All<span class="n">{total}</span></button></li>'
             + ''.join(f'<li><button type="button" class="chip" data-cat="{c}" data-label="{E(l)}"{CAT_NOUN.get(c, '')} aria-pressed="false"><span class="chip-swatch" aria-hidden="true" style="background-image:url({{R}}pattern-{CAT_PATTERN[c]}-sm.webp)"></span>{E(l)}'
                       f'<span class="n">{counts[c]}</span></button></li>' for c, l in BIZ_CATS if counts[c]))
    cards = ''.join(biz_card(b) for b in BIZ)
    stats = (f'<p class="dir-stats"><span><b>{total}</b>businesses</span><span><b>{n_dd}</b>accept Downtown Dollars</span>'
             f'<span><b>{n_sd}</b>in the Social District</span></p>')
    body = page_hero([('index.html', 'Home'), ('directory.html', 'Explore downtown')], 'Business directory', 'Explore downtown',
                     'Shops, restaurants, studios, salons, places to stay and community organizations in the heart of Kalamazoo. Hover over a card, or tap it, to see what each one offers, when it’s open and how to reach it.',
                     'f-mist', stats)
    body += f'''<section class="section" aria-labelledby="dir-title">
  <div class="wrap">
    <h2 class="sr-only" id="dir-title">Businesses</h2>
    {in_short('Each card is one downtown business. Hover over a card or tap it to flip it and see what the business does, where it is, and how to reach it. Use the buttons to show one kind of business, or only the ones that take Downtown Dollars.')}
    <form class="dir-tools" id="dir-form" role="search" aria-label="Search the directory">
      <div class="row">
        <div class="field grow"><label for="dir-q">Search</label><input type="search" id="dir-q" placeholder="Business name, street or building" autocomplete="off"></div>
        <div class="field"><span class="label" id="view-label">Show as</span>
          <span class="segmented" role="group" aria-labelledby="view-label" id="view-group"><button type="button" data-view="cards" aria-pressed="true">Flip cards</button><button type="button" data-view="list" aria-pressed="false">All details</button></span></div>
      </div>
      <div class="row">
        <div class="field" style="flex:1 1 auto"><span class="label" id="cats-label">Type of business</span><div role="group" aria-labelledby="cats-label"><ul class="chips" id="dir-cats">{chips}</ul></div></div>
        <div class="field"><span class="label" id="dd-label">Show only</span><button type="button" class="chip chip-dd" id="dir-dd" aria-pressed="false" aria-describedby="dd-label"><span class="dd-coin" aria-hidden="true" style="margin-inline-end:.4rem">$</span>Accepts Downtown Dollars<span class="n">{n_dd}</span></button>
          <button type="button" class="chip chip-sd" id="dir-sd" aria-pressed="false" aria-describedby="dd-label"><span class="sd-cup" aria-hidden="true" style="margin-inline-end:.4rem"></span>Social District<span class="n">{n_sd}</span></button>
          {gift_chip}{ev_chip}</div>
      </div>
    </form>
    <div class="dir-result">
      <p id="dir-count" role="status" aria-live="polite">Showing {total} of {total} businesses</p>
      <p class="dir-hint" id="dir-hint"><span class="cue-hover">Hover over a card to flip it, or press Enter on a business name.</span><span class="cue-touch">Tap a card to flip it.</span></p>
    </div>
    <ul class="biz-grid" id="biz-grid">{cards}</ul>
    <div class="note" id="dir-empty" hidden style="margin-top:1rem">No businesses match. Try another word, or <button type="button" id="dir-clear" style="background:none;border:0;padding:0;color:var(--link);font:inherit;font-weight:600;text-decoration:underline;cursor:pointer">clear all filters</button>.</div>
    <div class="two-col" style="margin-top:2.5rem">
      <section class="panel"><h2>Something missing or out of date?</h2><p>Hours come from each business’s own website and were last checked in October 2026. They can change, especially around holidays, so call ahead if you’re making a special trip.</p><p>Owners and visitors can send corrections, hours, a website or a short description to downtown@kalamazoocity.org. Businesses can also <a href="{{R}}businesses.html">ask to be listed</a>.</p></section>
      <section class="panel"><h2>Downtown Dollars</h2><p>Look for the {dd_badge()} tag. <a href="{{R}}dollars.html">How Downtown Dollars work</a>.</p></section>
      <section class="panel"><h2>Social District</h2><p>Look for the {sd_badge()} tag. Take your drink for a stroll. <a href="{{R}}social-district.html">How the Social District works</a>.</p></section>
    </div>
  </div>
</section>'''
    return body, total
