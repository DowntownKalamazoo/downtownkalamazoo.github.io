"""Business directory page: flip cards built from directory.json (made by import_directory.py)."""
import json, os, re, urllib.parse, html

E = html.escape
HERE = os.path.dirname(os.path.abspath(__file__))
BIZ = json.load(open(os.path.join(HERE, 'directory.json')))
# Gift names by business id, set by build.py from content/gift-guide.yml during the holiday season.
# Businesses with a gift get an "In the Gift Guide" tag and a directory filter.
GIFTS = {}


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
    for bid, fields in (up.get('update') or {}).items():
        if bid in by_id and fields:
            by_id[bid].update(fields)
    for b in BIZ:
        b.setdefault('sd', False)
    for bid in up.get('social_district') or []:
        if bid in by_id:
            by_id[bid]['sd'] = True
    fills = {}
    for b in BIZ:
        fills.setdefault(b['cat'], b['fill'])
    labels = dict(BIZ_CATS)
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
                 desc_es='', includes='', dd=bool(a.get('downtown_dollars')), featured=False, sd=bool(a.get('social_district')))
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


def dd_badge():
    return '<span class="dd-badge"><span class="dd-coin" aria-hidden="true">$</span>Accepts Downtown Dollars</span>'


def gift_badge():
    return ('<span class="gift-badge"><span class="gift-swatch" aria-hidden="true" style="background-image:url({R}pattern-stripes-sm.webp)"></span>'
            'In the Gift Guide</span>')


def _and(names):
    return names[0] if len(names) == 1 else ', '.join(names[:-1]) + ' and ' + names[-1]


def sd_badge():
    return '<span class="sd-badge"><span class="sd-cup" aria-hidden="true"></span>Social District</span>'


def biz_card(b):
    bid = 'b-' + b['id']
    none = '<span class="none">Not listed yet</span>'
    if b['address']:
        maps = 'https://www.google.com/maps/search/?api=1&query=' + urllib.parse.quote(b['name'] + ', ' + b['address'])
        street = re.sub(r',\s*Kalamazoo,\s*MI\s*49007$', '', b['address'])
        loc = f'{E(street)}<br>{ext(maps, "Get directions")}'
    else:
        loc = none
    if b['tel']:
        phone = f'<a href="{E(b["tel"])}">{E(b["phone"])}</a>'
    else:
        phone = E(b['phone']) if b['phone'] else none
    web = ext(b['website'], 'Visit website') if b['website'] else none
    desc = f'<p class="biz-desc">{E(b["desc"])}</p>' if b['desc'] else ''
    if b['includes']:
        desc += f'<p class="biz-desc"><strong>Inside:</strong> {E(b["includes"])}</p>'
    gifts = GIFTS.get(b['id']) or []
    if gifts:
        desc += (f'<p class="biz-desc"><strong>Gift ideas:</strong> {E(_and(gifts))}. '
                 f'<a href="{{R}}gifts.html#from-{b["id"]}">See them in the Holiday Gift Guide</a></p>')
    search = ' '.join([b['name'], b['cat_label'], b['address'], b['where'], b['desc'], b['includes'],
                       'downtown dollars' if b['dd'] else '', 'social district' if b.get('sd') else '',
                       'gift guide holiday gifts ' + ' '.join(gifts) if gifts else '']).lower()
    initial = re.sub(r'^the\s+', '', b['name'], flags=re.I)[:1].upper()
    dd = (dd_badge() if b['dd'] else '') + (sd_badge() if b.get('sd') else '') + (gift_badge() if gifts else '')
    where = f'<p class="biz-where">{E(b["where"])}</p>' if b['where'] else ''
    name = E(b['name'])
    return (
        f'<li class="biz {b["fill"]}" style="--cat-pat:url({{R}}pattern-{CAT_PATTERN.get(b["cat"], "squiggle")}-sm.webp)" id="{bid}" data-cat="{b["cat"]}" data-dd="{1 if b["dd"] else 0}" data-sd="{1 if b.get("sd") else 0}" data-gift="{1 if gifts else 0}" data-search="{E(search)}">'
        f'<div class="biz-inner">'
        f'<article class="face front" aria-labelledby="{bid}-n">'
        f'<div class="front-band" aria-hidden="true"><span class="cat">{E(b["cat_label"])}</span><span class="initial">{E(initial)}</span></div>'
        f'<div class="front-body">'
        f'<h3 class="biz-name" id="{bid}-n"><button type="button" class="flip-btn" aria-expanded="false" aria-controls="{bid}-back">{name}</button></h3>'
        f'{where}'
        f'<div class="front-foot">{dd}<span class="flip-cue" aria-hidden="true">{FLIP_ICON}'
        f'<span class="cue-hover">Hover for details</span><span class="cue-touch">Tap for details</span></span></div>'
        f'</div></article>'
        f'<section class="face back" id="{bid}-back" aria-label="{name} details" inert>'
        f'<div class="back-head"><span class="cat">{E(b["cat_label"])}</span><p class="back-name" aria-hidden="true">{name}</p></div>'
        f'<div class="back-body" tabindex="-1">{desc}'
        f'<dl class="biz-facts">'
        f'<div><dt>Location</dt><dd>{loc}</dd></div>'
        f'<div><dt>Phone</dt><dd>{phone}</dd></div>'
        f'<div><dt>Website</dt><dd>{web}</dd></div>'
        f'</dl>'
        f'<div class="back-foot">{dd}<button type="button" class="btn btn-small btn-quiet flip-back">Flip back'
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
    counts = {c: sum(1 for b in BIZ if b['cat'] == c) for c, _ in BIZ_CATS}
    chips = (f'<li><button type="button" class="chip" data-cat="all" data-label="All" aria-pressed="true">All<span class="n">{total}</span></button></li>'
             + ''.join(f'<li><button type="button" class="chip" data-cat="{c}" data-label="{E(l)}"{CAT_NOUN.get(c, '')} aria-pressed="false"><span class="chip-swatch" aria-hidden="true" style="background-image:url({{R}}pattern-{CAT_PATTERN[c]}-sm.webp)"></span>{E(l)}'
                       f'<span class="n">{counts[c]}</span></button></li>' for c, l in BIZ_CATS))
    cards = ''.join(biz_card(b) for b in BIZ)
    stats = (f'<p class="dir-stats"><span><b>{total}</b>businesses</span><span><b>{n_dd}</b>accept Downtown Dollars</span>'
             f'<span><b>{n_sd}</b>in the Social District</span></p>')
    body = page_hero([('index.html', 'Home'), ('directory.html', 'Explore downtown')], 'Business directory', 'Explore downtown',
                     'Shops, restaurants, studios, salons, places to stay, offices and community organizations in the heart of Kalamazoo. Hover over a card, or tap it, to see what each one offers and how to reach it.',
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
          {gift_chip}</div>
      </div>
    </form>
    <div class="dir-result">
      <p id="dir-count" role="status" aria-live="polite">Showing {total} of {total} businesses</p>
      <p class="dir-hint" id="dir-hint"><span class="cue-hover">Hover over a card to flip it, or press Enter on a business name.</span><span class="cue-touch">Tap a card to flip it.</span></p>
    </div>
    <ul class="biz-grid" id="biz-grid">{cards}</ul>
    <div class="note" id="dir-empty" hidden style="margin-top:1rem">No businesses match. Try another word, or <button type="button" id="dir-clear" style="background:none;border:0;padding:0;color:var(--link);font:inherit;font-weight:600;text-decoration:underline;cursor:pointer">clear all filters</button>.</div>
    <div class="two-col" style="margin-top:2.5rem">
      <section class="panel"><h2>Something missing or out of date?</h2><p>Owners and visitors can send corrections, a website or a short description to downtown@kalamazoocity.org. Businesses can also <a href="{{R}}businesses.html">ask to be listed</a>.</p></section>
      <section class="panel"><h2>Downtown Dollars</h2><p>Look for the {dd_badge()} tag. <a href="{{R}}dollars.html">How Downtown Dollars work</a>.</p></section>
      <section class="panel"><h2>Social District</h2><p>Look for the {sd_badge()} tag. Take your drink for a stroll. <a href="{{R}}social-district.html">How the Social District works</a>.</p></section>
    </div>
  </div>
</section>'''
    return body, total
