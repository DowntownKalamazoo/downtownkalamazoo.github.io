"""Plan your day: loads content/itineraries.yml, checks it, and turns each plan's steps into HTML with
links to the business directory, holiday event pages and gift guides.

Business names link on their own when they match a name in the directory (directory.json plus
content/directory-updates.yml). Holiday events, Santa's Workshop and the trolley link through PLACES below.
"""
import datetime as dt
import html
import re
import unicodedata

import content_loader
import directory_page

E = html.escape

DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
DAY_NAMES = dict(zip(DAYS, ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']))
DAY_SHORT = dict(zip(DAYS, ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']))

BUDGETS = [('free', 'Free', 'Free', 'No paid activity needed'),
           ('$', '$', 'Under $25', 'Under $25 per person'),
           ('$$', '$$', '$25 to $60', '$25 to $60 per person'),
           ('$$$', '$$$', 'Over $60', 'Over $60 per person')]
BUDGET_KEY = {'free': 'free', '$': 'b1', '$$': 'b2', '$$$': 'b3'}

WHO = [('families', 'Families with kids'), ('couples', 'Couples'), ('friends', 'Friends'), ('adults', 'Adults'),
       ('teens', 'Teens'), ('solo', 'On my own'), ('visitors', 'Visiting guests'), ('pets', 'With a pet')]

GIFT_GUIDES = {'all': 'Holiday gift guides', 'art-lover': 'For the art lover', 'foodie': 'For the food lover',
               'kids': 'For kids', 'host': 'For the host', 'stocking': 'Stocking stuffers', 'experiences': 'Experiences'}

FILLS = ['f-pink', 'f-blue', 'f-green', 'f-red', 'f-mist']
CARD_PATTERNS = ['arcs', 'confetti', 'dots', 'squiggle', 'quilt', 'stripes', 'waves', 'speckle', 'loops']


def art_hop_slug(today=None):
    today = today or dt.date.today()
    return 'first-friday-nov' if today <= dt.date(2026, 11, 6) else 'first-friday-dec'


def places():
    """Names that aren't in the business directory but should still link. (name, page, kind)."""
    hop = art_hop_slug()
    return [
        ('First Friday & Art Hop', f'events/{hop}.html', 'event'),
        ('Art Hop', f'events/{hop}.html', 'event'),
        ('Shop Small Saturday', 'sbs.html', 'event'),
        ('Small Business Saturday', 'sbs.html', 'event'),
        ('Fox Motors Maple Hill Holiday Parade', 'events/holiday-parade.html', 'event'),
        ('Holiday Parade', 'events/holiday-parade.html', 'event'),
        ('after-parade activities', 'events/after-parade.html', 'event'),
        ('Tree Lighting Ceremony', 'events/tree-lighting.html', 'event'),
        ('Tree Lighting', 'events/tree-lighting.html', 'event'),
        ('Moonlight Madness', 'events/moonlight-madness.html', 'event'),
        ('Gingerbread Wonderland', 'events/gingerbread-wonderland.html', 'event'),
        ('December to Remember', 'events/december-to-remember.html', 'event'),
        ("New Year's Fest", 'events/new-years-fest.html', 'event'),
        ('Moms in the Zoo', 'events/moms-in-the-zoo.html', 'event'),
        ('Pets with Santa', 'events/small-business-saturday.html', 'event'),
        ("Santa's Workshop", 'events/small-business-saturday.html', 'event'),
        ('Holly Jolly Trolley', 'visit.html#trolley-title', 'event'),
        ('Downtown Dollars', 'dollars.html', 'event'),
        ('Kalamazoo Valley Museum', 'https://kalamazoomuseum.org', 'place'),
    ]


def _norm(s):
    """Lowercase and fold accents and curly quotes, one character for one, so positions still line up."""
    out = []
    for c in s:
        if c in '‘’ʼ`´':
            out.append("'")
            continue
        if c in '“”':
            out.append('"')
            continue
        d = unicodedata.normalize('NFKD', c)
        base = d[0] if d else c
        lo = base.lower()
        out.append(lo if len(lo) == 1 else base)
    return ''.join(out)


def _targets():
    t = []
    for b in directory_page.BIZ:
        t.append(dict(name=b['name'], href=f'directory.html#b-{b["id"]}', kind='biz', biz=b))
    for name, href, kind in places():
        t.append(dict(name=name, href=href, kind=kind, biz=None))
    for x in t:
        x['n'] = _norm(x['name'])
    t.sort(key=lambda x: -len(x['n']))
    return t


_MD_LINK = re.compile(r'\[([^\]]+)\]\(([^)\s]+)\)')


def _href(target):
    return target if target.startswith(('http://', 'https://', 'mailto:')) else '{R}' + target


def _a(href, text, extra=''):
    if href.startswith('http'):
        return f'<a href="{E(href)}" target="_blank" rel="noopener"{extra}>{text}<span class="sr-only"> (opens in a new tab)</span></a>'
    return f'<a href="{E(_href(href))}"{extra}>{text}</a>'


def linkify(text, targets, found=None):
    """Plain text from the YAML file to HTML. Links the first mention of each business or event in this line.
    `found` collects what was matched, in order, for the plan's list of places."""
    out = []
    pos = 0
    for m in list(_MD_LINK.finditer(text)) + [None]:
        seg = text[pos:m.start()] if m else text[pos:]
        out.append(_autolink(seg, targets, found))
        if m:
            out.append(_a(m.group(2), E(m.group(1))))
            pos = m.end()
    return ''.join(out)


def _autolink(seg, targets, found):
    n = _norm(seg)
    taken = [False] * len(seg)
    hits = []
    for t in targets:
        start = 0
        while True:
            i = n.find(t['n'], start)
            if i < 0:
                break
            j = i + len(t['n'])
            start = i + 1
            before_ok = i == 0 or not n[i - 1].isalnum()
            after_ok = j == len(n) or not n[j].isalnum()
            if before_ok and after_ok and not any(taken[i:j]):
                for k in range(i, j):
                    taken[k] = True
                # One link per page in a line: "Pets with Santa at Santa's Workshop" links once.
                if not any(h[2]['href'] == t['href'] for h in hits):
                    hits.append((i, j, t))
                break   # first mention only
    hits.sort(key=lambda h: h[0])
    res, p = [], 0
    for i, j, t in hits:
        res.append(E(seg[p:i]))
        res.append(_a(t['href'], E(seg[i:j])))
        p = j
        if found is not None and t not in found:
            found.append(t)
    res.append(E(seg[p:]))
    return ''.join(res)


def short(text, n=64):
    """A step cut down to fit two lines of a postcard."""
    if len(text) <= n:
        return text
    cut = text[:n].rsplit(' ', 1)[0].rstrip(',;.')
    return cut + '…'


def plain(text):
    return _MD_LINK.sub(lambda m: m.group(1), text)


class ItineraryError(ValueError):
    pass


def _check(p, i, event_slugs):
    where = f'content/itineraries.yml, plan {i + 1} ({p.get("slug") or p.get("title") or "no slug"})'
    for k in ['slug', 'title', 'summary', 'best_for', 'time', 'budget', 'who', 'days', 'steps']:
        if not p.get(k):
            raise ItineraryError(f'{where}: "{k}" is missing.')
    if p['slug'] == 'build-your-own':
        raise ItineraryError(f'{where}: the slug build-your-own is used by the build-your-own page. Pick another.')
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', str(p['slug'])):
        raise ItineraryError(f'{where}: the slug should be lowercase words with dashes, like family-afternoon.')
    b = str(p['budget']).strip().lower()
    if b not in BUDGET_KEY:
        raise ItineraryError(f'{where}: budget should be "Free", "$", "$$" or "$$$" (in quotes).')
    who_ok = {k for k, _ in WHO}
    for w in p['who']:
        if w not in who_ok:
            raise ItineraryError(f'{where}: "{w}" isn\'t one of the who options: {", ".join(sorted(who_ok))}.')
    days = DAYS if p['days'] == 'all' else p['days']
    for d in days:
        if d not in DAYS:
            raise ItineraryError(f'{where}: "{d}" isn\'t a day. Use mon tue wed thu fri sat sun, or all.')
    for s in p.get('events') or []:
        if s not in event_slugs:
            raise ItineraryError(f'{where}: there\'s no holiday event called "{s}". Use one of: {", ".join(event_slugs)}.')
    if p.get('gifts') and p['gifts'] not in GIFT_GUIDES:
        raise ItineraryError(f'{where}: gifts should be one of {", ".join(GIFT_GUIDES)}.')
    for s in p['steps']:
        if not isinstance(s, str):
            raise ItineraryError(f'{where}: a step isn\'t plain text. If it has a colon in it, put it in double quotes.')


def days_label(days):
    if len(days) == 7:
        return 'Any day'
    idx = [DAYS.index(d) for d in days]
    if len(idx) > 2 and idx == list(range(idx[0], idx[-1] + 1)):
        return f'{DAY_NAMES[days[0]]} to {DAY_NAMES[days[-1]]}'
    if len(days) == 1:
        return DAY_NAMES[days[0]] + 's'
    return ', '.join(DAY_NAMES[d] + 's' for d in days[:-1]) + ' and ' + DAY_NAMES[days[-1]] + 's'


def load(events):
    data = content_loader.load_yaml('itineraries.yml', {}) or {}
    raw = [p for p in (data.get('plans') or []) if not p.get('draft')]
    slugs = [e['slug'] for e in events]
    seen = set()
    targets = _targets()
    plans = []
    for i, p in enumerate(raw):
        _check(p, i, slugs)
        if p['slug'] in seen:
            raise ItineraryError(f'content/itineraries.yml: two plans use the slug "{p["slug"]}".')
        seen.add(p['slug'])
        days = DAYS[:] if p['days'] == 'all' else [d for d in DAYS if d in p['days']]
        found = []
        steps = [linkify(str(s).strip(), targets, found) for s in p['steps']]
        holiday = linkify(str(p['holiday']).strip(), targets, None) if p.get('holiday') else ''
        b = str(p['budget']).strip().lower()
        blabel = next(x for x in BUDGETS if x[0] == b)
        plans.append(dict(
            slug=p['slug'], title=str(p['title']).strip(), summary=str(p['summary']).strip(),
            best_for=str(p['best_for']).strip(), time=str(p['time']).strip(),
            budget_key=BUDGET_KEY[b], budget=blabel[1], budget_text=blabel[2], budget_long=blabel[3],
            who=list(p['who']), days=days, days_text=days_label(days), when=str(p.get('when') or days_label(days)).strip(),
            events=list(p.get('events') or []), gifts=p.get('gifts') or '',
            steps=steps, steps_plain=[plain(str(s).strip()) for s in p['steps']],
            holiday=holiday, before=str(p.get('before_you_go') or '').strip(),
            places=[t for t in found if t['kind'] == 'biz'], mentions=found,
            fill=FILLS[i % len(FILLS)], pattern=CARD_PATTERNS[i % len(CARD_PATTERNS)],
            # Kept for the older parts of the site that read these
            tag=str(p['best_for']).strip(), stops=[dict(time=str(n + 1), place=short(plain(str(s).strip())), what='') for n, s in enumerate(p['steps'])],
        ))
    parking = data.get('parking') or {}
    return plans, data.get('santa') or {}, data.get('trolley') or {}, parking


def schedule_json(s):
    """Santa or trolley hours as plain data for the page script."""
    if not s:
        return None
    return dict(name=s.get('name', ''), where=s.get('where', ''), opens=str(s.get('opens', '')), closes=str(s.get('closes', '')),
                hours={k: str(v) for k, v in (s.get('hours') or {}).items()},
                special={str(k): str(v) for k, v in (s.get('special') or {}).items()})


# Stops people can add on the build-your-own page that aren't businesses or events.
EXPERIENCES = [
    dict(id='santa', n="Santa's Workshop", w='City Centre, second floor, 125 S. Kalamazoo Mall', h='events/small-business-saturday.html',
         d='Visit Santa, write a letter and make a craft. Free. Open Thursday to Sunday from Nov. 28.'),
    dict(id='trolley', n='Ride the Holly Jolly Trolley', w='Leaves from City Hall, 241 W. South St.', h='visit.html#trolley-title',
         d='A free trolley loop around downtown, Thursday to Sunday through Dec. 24, and Dec. 31.'),
    dict(id='mall', n='Stroll the Kalamazoo Mall', w='Kalamazoo Mall', h='',
         d='Holiday windows, lights and photo spots on downtown’s pedestrian street. Free.'),
    dict(id='bronson', n='Bronson Park', w='200 S. Rose St.', h='',
         d='The holiday tree and lights, a block west of the Kalamazoo Mall. Free.'),
    dict(id='museum', n='Kalamazoo Valley Museum', w='230 N. Rose St.', h='https://kalamazoomuseum.org',
         d='Hands-on science and history exhibits. General admission is free.'),
]
_X_BY_NAME = {"santa's workshop": 'santa', 'pets with santa': 'santa', 'holly jolly trolley': 'trolley', 'kalamazoo valley museum': 'museum'}


def stop_keys(plan):
    """A plan's places, as build-your-own stops (b: business, e: event, x: experience)."""
    keys = []
    for t in plan['mentions']:
        k = None
        if t['kind'] == 'biz':
            k = 'b:' + t['biz']['id']
        elif _norm(t['name']) in _X_BY_NAME:
            k = 'x:' + _X_BY_NAME[_norm(t['name'])]
        elif t['href'] == 'sbs.html':
            k = 'e:small-business-saturday'
        elif t['href'].startswith('events/'):
            k = 'e:' + t['href'][7:-5]
        if k and k not in keys:
            keys.append(k)
    return keys
