"""Holiday Gift Guide: reads content/gift-guide.yml, checks it, resizes the photos and builds
holidays/gifts.html (the fill-in-the-tag page).

Staff only edit content/gift-guide.yml and upload photos to files/gifts. Everything else here is automatic:
- business names, links and Downtown Dollars badges come from the business directory
- gifts with [placeholders] or no description stay off the page and are listed as warnings
- photos are resized to two widths, so any size works
- the order of the gifts changes every day (the site rebuilds each morning), so no business is always first
"""
import datetime as dt
import difflib
import html
import json
import os
import random
import re
import shutil

import content_loader
import directory_page

E = html.escape
HERE = os.path.dirname(os.path.abspath(__file__))
FILE = 'content/gift-guide.yml'
CSS = open(os.path.join(HERE, 'gift.css'), encoding='utf-8').read()
JS = open(os.path.join(HERE, 'gift.js'), encoding='utf-8').read()

# kind: (label on the tag, words in the sentence, pattern for the band under a photo)
KINDS = {
    'unwrap': ('To unwrap', 'something to unwrap', 'stripes'),
    'experience': ('Experience', 'an experience', 'confetti'),
    'eat-drink': ('Eat & drink', 'something to eat or drink', 'dots'),
    'gift-card': ('Gift card', 'a gift card', 'squiggle'),
}
# for: (words in the sentence, "To:" line on the tag)
FOR = {
    'foodie': ('the foodie', 'The foodie'),
    'maker': ('the maker', 'The maker'),
    'kid': ('the kid', 'The kid'),
    'kalamazoo-lover': ('the Kalamazoo lover', 'The Kalamazoo lover'),
    'self-care': ('the self-care fan', 'The self-care fan'),
    'adventurer': ('the adventurer', 'The adventurer'),
    'coffee-tea': ('the coffee and tea drinker', 'The coffee & tea drinker'),
    'arts-fan': ('the arts and theater fan', 'The arts fan'),
    'someone-special': ('your someone special', 'Someone special'),
    'host': ('the host', 'The host'),
    'pet': ('the pet (and their person)', 'The pet'),
    'has-everything': ('the one who has everything', 'The one who has everything'),
}
BUDGETS = [('any', 'any amount'), ('low', 'under $25'), ('mid', '$25 to $75'), ('high', '$75 or more')]
FOCUS = {'': 'center', 'center': 'center', 'top': 'center top', 'bottom': 'center bottom'}
PLACEHOLDER = re.compile(r'\[[^\]]*\]')
PHOTO_WIDTHS = (600, 1200)
MAX_DESC = 220


class GiftGuideError(ValueError):
    pass


def _yes(v):
    return v is True or str(v or '').strip().lower() in ('yes', 'true', 'y')


def _text(v):
    return '' if v is None else str(v).strip()


def _band(price):
    """The budget filter uses the lowest dollar amount in the price."""
    amounts = [float(a.replace(',', '')) for a in re.findall(r'\$\s*([\d,]+(?:\.\d+)?)', price)]
    if not amounts:
        return ''
    low = min(amounts)
    return 'low' if low < 25 else 'mid' if low < 75 else 'high'


def _slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def load():
    """Returns dict(gifts, by_business, warnings). Raises GiftGuideError for problems that must be fixed."""
    import yaml
    try:
        data = content_loader.load_yaml('gift-guide.yml', {}) or {}
    except yaml.YAMLError as err:
        mark = getattr(err, 'problem_mark', None)
        line = f' near line {mark.line + 1}' if mark else ''
        raise GiftGuideError(f'{FILE}: the file couldn’t be read{line}. Check for a missing quote mark, a value with a colon '
                             f'in it that needs double quotes, or a line that isn’t lined up with the ones around it.') from None
    if not isinstance(data, dict):
        raise GiftGuideError(f'{FILE}: the file should start with "businesses:" on its own line.')
    blocks = data.get('businesses') or []
    by_id = {b['id']: b for b in directory_page.BIZ}
    gifts, warnings, used_ids = [], [], set()
    by_business = {}
    for bi, blk in enumerate(blocks):
        if not isinstance(blk, dict):
            raise GiftGuideError(f'{FILE}: business {bi + 1} isn’t set up right. Each business starts with "- business:" at the left edge, '
                                 f'with its gifts indented under it.')
        bid = _text(blk.get('business'))
        if bid.startswith('b-'):
            bid = bid[2:]
        if bid == 'downtown':
            biz = dict(id='', name='Downtown Kalamazoo', pat='quilt', dd=False, href='')
        elif bid:
            b = by_id.get(bid)
            if not b:
                close = difflib.get_close_matches(bid, list(by_id), n=1, cutoff=0.6)
                hint = f' Did you mean {close[0]}?' if close else ' Use the end of its directory link, like rustica for directory.html#b-rustica.'
                raise GiftGuideError(f'{FILE}: there’s no business with the id "{bid}" in the directory.{hint}')
            biz = dict(id=bid, name=b['name'], pat=directory_page.CAT_PATTERN.get(b['cat'], 'squiggle'),
                       dd=bool(b['dd']), href=f'directory.html#b-{bid}')
        elif _text(blk.get('name')):
            name = _text(blk['name'])
            biz = dict(id='', name=name, pat='squiggle', dd=False, href=_text(blk.get('website')))
            if not _yes(blk.get('draft')):
                warnings.append(f'{name} isn’t in the business directory, so its gifts don’t link to a listing. '
                                f'Add it to the directory, then change "name: {name}" to "business:" and its id.')
        else:
            raise GiftGuideError(f'{FILE}: business {bi + 1} needs "business:" with its directory id '
                                 f'(or "name:" for a business that isn’t in the directory yet).')
        if _yes(blk.get('draft')):
            continue
        items = blk.get('gifts') or []
        if not isinstance(items, list):
            raise GiftGuideError(f'{FILE}, {biz["name"]}: list its gifts under "gifts:", each starting with "- name:".')
        for gi, g in enumerate(items):
            where = f'{FILE}, {biz["name"]}, gift {gi + 1}'
            if not isinstance(g, dict):
                raise GiftGuideError(f'{where}: each gift starts with "- name:", with its other lines lined up under name.')
            name = _text(g.get('name'))
            if name:
                where += f' ({name})'
            if _yes(g.get('draft')):
                continue
            if not name:
                raise GiftGuideError(f'{where}: add a name.')
            kind = _text(g.get('kind')).lower()
            if kind not in KINDS:
                raise GiftGuideError(f'{where}: kind should be one of {", ".join(KINDS)}, not "{kind}".')
            who = g.get('for') or []
            if isinstance(who, str):
                who = [w.strip() for w in who.split(',')]
            who = [_text(w).lower() for w in who if _text(w)]
            if not who:
                raise GiftGuideError(f'{where}: add "for:" with at least one of {", ".join(FOR)}, like for: [foodie, host]')
            for w in who:
                if w not in FOR:
                    close = difflib.get_close_matches(w, list(FOR), n=1)
                    raise GiftGuideError(f'{where}: "{w}" isn’t one of the "for" choices.' + (f' Did you mean {close[0]}?' if close else '')
                                         + f' Use any of: {", ".join(FOR)}.')
            image = _text(g.get('image')).lstrip('/')
            alt = _text(g.get('image_alt'))
            if image:
                if not image.startswith('files/'):
                    image = 'files/gifts/' + image
                if not os.path.isfile(os.path.join(HERE, image)):
                    raise GiftGuideError(f'{where}: the photo {image} isn’t in the repository. Upload it to files/gifts, '
                                         f'or check the spelling (capital letters and the .jpg ending count).')
                if not alt:
                    raise GiftGuideError(f'{where}: add an image_alt sentence describing the photo for people who can’t see it.')
            focus = _text(g.get('photo_focus')).lower()
            if focus not in FOCUS:
                raise GiftGuideError(f'{where}: photo_focus should be top, center or bottom.')
            desc = _text(g.get('description'))
            price = _text(g.get('price'))
            wrap = _text(g.get('wrap_label')) or name
            link = _text(g.get('link'))
            fields = [name, desc, price, wrap, alt, link]
            if any(PLACEHOLDER.search(f) for f in fields):
                warnings.append(f'Not shown yet: {biz["name"]}, "{name}" still has something in [brackets]. Replace it to show the gift.')
                continue
            if not desc:
                warnings.append(f'Not shown yet: {biz["name"]}, "{name}" needs a description.')
                continue
            if len(desc) > MAX_DESC:
                warnings.append(f'{biz["name"]}, "{name}": the description is {len(desc)} characters. '
                                f'Tags read best under {MAX_DESC}, so try cutting it to a sentence or two.')
            gid = 'gift-' + _slug((biz['id'] or biz['name']) + '-' + name)[:60]
            base, n = gid, 2
            while gid in used_ids:
                gid = f'{base}-{n}'; n += 1
            used_ids.add(gid)
            if link and not link.startswith(('http://', 'https://')):
                link = link.lstrip('/')
            gifts.append(dict(
                id=gid, name=name, kind=kind, who=who, desc=desc, price=price, band=_band(price),
                image=image, alt=alt, focus=FOCUS[focus], wrap=wrap,
                biz=biz['name'], biz_id=biz['id'], href=link or biz['href'], pat=biz['pat'], dd=biz['dd'],
                local=_yes(g.get('only_in_kalamazoo')), gives=_yes(g.get('gives_back')),
                stocking=_yes(g.get('stocking_stuffer')), adult=_yes(g.get('age_21')),
            ))
            if biz['id']:
                by_business.setdefault(biz['id'], []).append(name)
    return dict(gifts=gifts, by_business=by_business, warnings=warnings)


# ---------------------------------------------------------------- Photos
def prepare_photos(gifts, out_dir, warnings):
    """Resizes each gift photo to two widths in out/files/gifts. Any size or shape of upload works."""
    try:
        from PIL import Image, ImageOps
    except ImportError:
        Image = None
    if any(g['image'] for g in gifts) and Image is None:
        warnings.append('Photos were published at their original size because the photo resizer isn’t installed. '
                        'In .github/workflows/publish.yml, the install line should read: pip install markdown pyyaml pillow')
    done = {}
    for g in gifts:
        if not g['image']:
            continue
        src = os.path.join(HERE, g['image'])
        if src in done:
            g['img'] = done[src]
            continue
        stem = _slug(os.path.splitext(os.path.basename(g['image']))[0]) or 'gift'
        rel_dir = 'files/gifts'
        os.makedirs(os.path.join(out_dir, rel_dir), exist_ok=True)
        if Image is None:
            name = os.path.basename(g['image'])
            shutil.copy(src, os.path.join(out_dir, rel_dir, name))
            img = dict(src=f'{rel_dir}/{name}', srcset='')
        else:
            with Image.open(src) as im:
                im = ImageOps.exif_transpose(im).convert('RGB')
                if im.width < 800:
                    warnings.append(f'{g["biz"]}, "{g["name"]}": the photo is only {im.width} pixels wide, so it may look soft. '
                                    f'Ask for a larger one if you can.')
                outs = []
                for w in sorted({min(w, im.width) for w in PHOTO_WIDTHS}):
                    ww = w
                    hh = round(im.height * ww / im.width)
                    name = f'{stem}-{w}.jpg'
                    im.resize((ww, hh), Image.LANCZOS).save(os.path.join(out_dir, rel_dir, name), 'JPEG',
                                                            quality=80, optimize=True, progressive=True)
                    outs.append((name, ww))
            img = dict(src=f'{rel_dir}/{outs[-1][0]}', srcset=', '.join(f'{{R}}{rel_dir}/{n} {w}w' for n, w in outs))
        done[src] = img
        g['img'] = img


# ---------------------------------------------------------------- Page
CHEVRON = ('<svg class="gg-chev" aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
           'stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>')
TICK = ('<svg class="gg-tick" aria-hidden="true" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12l5 5 9-10"/></svg>')
BOW = ('<svg class="gg-bow" aria-hidden="true" viewBox="0 0 56 34"><path d="M28 15 C 18 2, 4 2, 4 12 C 4 22, 18 22, 28 15 Z"/>'
       '<path d="M28 15 C 38 2, 52 2, 52 12 C 52 22, 38 22, 28 15 Z"/><circle cx="28" cy="15" r="5.5"/></svg>')


def _select(sid, label, options):
    opts = ''.join(f'<option value="{E(v)}">{E(t)}</option>' for v, t in options)
    return (f'<span class="gg-blank"><label class="sr-only" for="{sid}">{E(label)}</label>'
            f'<select id="{sid}">{opts}</select>{CHEVRON}</span>')


def _tag(g, i):
    who = ' '.join(g['who'])
    tilt = ((i * 37) % 5 - 2) * 0.7
    if g.get('img'):
        srcset = f' srcset="{g["img"]["srcset"]}" sizes="(max-width: 600px) 92vw, 300px"' if g['img']['srcset'] else ''
        media = (f'<div class="gg-media"><img src="{{R}}{E(g["img"]["src"])}"{srcset} alt="{E(g["alt"])}" loading="lazy" decoding="async"'
                 f' style="object-position:{g["focus"]}"></div>'
                 f'<div class="gg-band" aria-hidden="true" style="background-image:url({{R}}pattern-{KINDS[g["kind"]][2]}-sm.webp)"></div>')
    else:
        media = (f'<div class="gg-media gg-wrap" aria-hidden="true" style="background-image:url({{R}}pattern-{g["pat"]}.webp)">'
                 f'<span class="gg-wrap-label">{E(g["wrap"])}</span></div>')
    badges = ''
    if g['dd']:
        badges += directory_page.dd_badge()
    if g['local']:
        badges += '<span class="gg-badge gg-local"><span class="gg-k" aria-hidden="true"></span>Only in Kalamazoo</span>'
    if g['gives']:
        badges += '<span class="gg-badge gg-gives">Gives back</span>'
    if g['adult']:
        badges += '<span class="gg-badge gg-21">21+</span>'
    badges = f'<p class="gg-badges">{badges}</p>' if badges else ''
    price = f'<span class="gg-price">{E(g["price"])}</span>' if g['price'] else ''
    if g['href']:
        external = g['href'].startswith(('http://', 'https://'))
        href = E(g['href']) if external else '{R}' + E(g['href'])
        tail = ' (opens in a new tab)' if external else (', in the business directory' if g['href'].startswith('directory.html') else '')
        target = ' target="_blank" rel="noopener"' if external else ''
        frm = f'<a class="gg-from" href="{href}"{target}>From: {E(g["biz"])}<span class="sr-only">{tail}</span></a>'
    else:
        frm = f'<p class="gg-from">From: {E(g["biz"])}</p>'
    return (f'<li class="gg-item" id="{g["id"]}" style="--tilt:{tilt:.1f}deg" data-who="{who}" data-kind="{g["kind"]}" data-band="{g["band"]}"'
            f' data-dd="{int(g["dd"])}" data-local="{int(g["local"])}" data-stocking="{int(g["stocking"])}" data-adult="{int(g["adult"])}"'
            f' data-biz="{E(g["biz_id"])}" data-bizname="{E(g["biz"])}">'
            f'<span class="gg-string" aria-hidden="true"></span>'
            f'<article class="gg-tag" aria-labelledby="{g["id"]}-n">{media}<span class="gg-hole" aria-hidden="true"></span>'
            f'<div class="gg-body"><p class="gg-pick" hidden>Downtown’s pick</p>'
            f'<p class="gg-to">To: <span class="gg-to-who">{E(FOR[g["who"][0]][1])}</span></p>'
            f'<h3 class="gg-name" id="{g["id"]}-n">{E(g["name"])}</h3>'
            f'<p class="gg-desc">{E(g["desc"])}</p>{badges}'
            f'<p class="gg-meta"><span>{E(KINDS[g["kind"]][0])}</span>{price}</p>'
            f'{frm}</div></article></li>')


def body(crumbs, in_short, gifts, today=None):
    today = today or dt.date.today()
    order = gifts[:]
    random.Random(today.isoformat()).shuffle(order)   # a new order every day
    tags = ''.join(_tag(g, i) for i, g in enumerate(order))
    n_biz = len({g['biz'] for g in gifts})
    who_opts = [('any', 'anyone')] + [(k, v[0]) for k, v in FOR.items()]
    kind_opts = [('any', 'anything')] + [(k, v[1]) for k, v in KINDS.items()]
    sentence = (f'I’m shopping for {_select("gg-who", "Who you’re shopping for", who_opts)} who’d love '
                f'{_select("gg-kind", "What kind of gift", kind_opts)}, and I’d like to spend '
                f'{_select("gg-budget", "How much you’d like to spend", BUDGETS)}.')
    toggles = ''.join(f'<button type="button" class="gg-toggle" data-flag="{f}" aria-pressed="false">{TICK}{E(t)}</button>'
                      for f, t in [('dd', 'Pay with Downtown Dollars'), ('local', 'Only in Kalamazoo'),
                                   ('stocking', 'Stocking stuffers'), ('adult', 'Hide 21+ gifts')])
    labels = json.dumps(dict(who={k: v for k, v in FOR.items()}, total=len(gifts)), ensure_ascii=False).replace('</', '<\\/')
    garland = ('<svg class="gg-garland" aria-hidden="true" viewBox="0 0 1280 60" preserveAspectRatio="none">'
               '<path d="M-10 14 Q 160 58 330 22 T 660 26 T 990 20 T 1300 24"/>'
               '<path class="gg-garland-dots" d="M-10 14 Q 160 58 330 22 T 660 26 T 990 20 T 1300 24"/></svg>')
    return f'''<style>{CSS}</style>
<section class="gg-hero" aria-labelledby="page-title">
  {garland}
  <div class="wrap">
    {crumbs}
    <div class="gg-hero-row">
      <div class="gg-hang">
        <span class="gg-string gg-string-long" aria-hidden="true"></span>
        <div class="gg-bigtag">
          <span class="gg-hole gg-hole-big" aria-hidden="true"></span>
          <p class="eyebrow">Holiday Gift Guide · {n_biz} downtown businesses</p>
          <h1 class="display h1" id="page-title">Fill in the tag</h1>
          <form class="gg-form" id="gg-form" aria-label="Find a gift">
            <p class="gg-sentence">{sentence}</p>
            <div class="gg-toggles" role="group" aria-label="More choices">{toggles}</div>
          </form>
          <p class="gg-nojs">Every gift idea is listed below, from {n_biz} downtown shops, restaurants and studios.</p>
        </div>
        <div class="gg-confetti" aria-hidden="true" style="background-image:url({{R}}pattern-confetti.webp)"></div>
      </div>
      <div class="gg-surprise">
        <span class="gg-string gg-string-long" aria-hidden="true"></span>
        <div class="gg-package" id="gg-package" aria-hidden="true"><span class="gg-paper" style="background-image:url({{R}}pattern-stripes.webp)"></span><span class="gg-ribbon-v"></span><span class="gg-ribbon-h"></span>{BOW}</div>
        <div class="gg-spot" id="gg-spot" hidden></div>
        <p class="gg-surprise-text" id="gg-surprise-text">Not sure where to start? Let downtown pick something for you.</p>
        <button type="button" class="btn gg-surprise-btn" id="gg-surprise">Surprise me</button>
        <p class="sr-only" id="gg-spot-status" role="status" aria-live="polite"></p>
      </div>
    </div>
  </div>
</section>
<section class="section gg-results" aria-labelledby="gg-results-title">
  <div class="wrap">
    {in_short('Each tag is one gift idea from a downtown business. Fill in the sentence at the top to show the gifts that fit the person you’re shopping for. Select a business name to see it in the directory.')}
    <div class="gg-head">
      <div>
        <h2 class="h2" id="gg-results-title">Gift ideas</h2>
        <p id="gg-count" role="status" aria-live="polite">Showing all {len(gifts)} gift ideas</p>
      </div>
      <button type="button" class="btn" id="gg-clear" hidden>Clear the tag</button>
    </div>
    <p class="gg-from-note" id="gg-from-note" hidden><span id="gg-from-text"></span> <button type="button" class="btn btn-small" id="gg-from-all">Show all gifts</button></p>
    <ul class="gg-grid" id="gg-grid">{tags}</ul>
    <div class="gg-empty" id="gg-empty" hidden>
      <p class="h3">No gifts match all of that yet.</p>
      <p id="gg-empty-why">Try another blank, or turn off a choice. Downtown Dollars fit every tag.</p>
      <p><button type="button" class="btn btn-primary" id="gg-empty-clear">Clear the tag</button></p>
    </div>
  </div>
</section>
<section class="section-tight">
  <div class="wrap gg-panels">
    <section class="panel f-pink"><h2>Still stuck?</h2><p>Downtown Dollars fit every tag. They arrive by email in $5, $10 and $20 amounts. <a href="{{R}}dollars.html">Get Downtown Dollars</a></p></section>
    <section class="panel"><h2>Make a day of it</h2><p>Pair your shopping with a holiday event, dinner and the free trolley. <a href="{{R}}plan.html">Plan your day</a></p></section>
    <section class="panel"><h2>Own a downtown business?</h2><p>To add a gift to the guide, email downtown@kalamazoocity.org with a short description, the price and a photo.</p></section>
  </div>
</section>
<script type="application/json" id="gg-data">{labels}</script>
<script>{JS}</script>'''
