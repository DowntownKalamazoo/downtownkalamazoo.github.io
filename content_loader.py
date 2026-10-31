"""Reads the staff-editable files in content/ (Markdown with a short header, and YAML lists).

Each Markdown file starts with a header between two lines of three dashes, for example:

    ---
    title: Downtown parking updates take effect
    date: 2026-04-01
    type: Press release
    summary: One or two sentences for the news list.
    ---
    The article itself, in Markdown.
"""
import calendar
import datetime as dt
import os
import re

import markdown
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(HERE, 'content')
MD = markdown.Markdown(extensions=['extra', 'sane_lists', 'smarty'])


def _date(v):
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    if v in (None, ''):
        return None
    return dt.date.fromisoformat(str(v).strip())


def read_md(path):
    text = open(path, encoding='utf-8').read().lstrip('﻿')
    meta, body = {}, text
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n?(.*)$', text, re.S)
    if m:
        meta = yaml.safe_load(m.group(1)) or {}
        body = m.group(2)
    MD.reset()
    meta['body_html'] = MD.convert(body.strip()) if body.strip() else ''
    stem = os.path.splitext(os.path.basename(path))[0]
    meta.setdefault('slug', re.sub(r'^\d{4}-\d{2}-\d{2}-', '', stem))
    meta['source_file'] = os.path.relpath(path, HERE)
    return meta


def load(folder):
    d = os.path.join(CONTENT, folder)
    if not os.path.isdir(d):
        return []
    items = [read_md(os.path.join(d, f)) for f in sorted(os.listdir(d)) if f.endswith('.md') and not f.startswith(('_', 'README'))]
    return [i for i in items if not i.get('draft')]


def load_yaml(name, default=None):
    p = os.path.join(CONTENT, name)
    if not os.path.exists(p):
        return default
    return yaml.safe_load(open(p, encoding='utf-8')) or default


# ---------------------------------------------------------------- News
NEWS_TYPES = ['Press release', 'News', 'Feature', 'In the news']


def news():
    posts = []
    for p in load('news'):
        p['date'] = _date(p.get('date'))
        p['type'] = p.get('type') if p.get('type') in NEWS_TYPES else 'News'
        posts.append(p)
    return sorted(posts, key=lambda p: p['date'] or dt.date.min, reverse=True)


# ---------------------------------------------------------------- Events
ORD = {'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'last': -1}
DAYS = {d.lower(): i for i, d in enumerate(calendar.day_name)}


def _nth_weekday(year, month, nth, weekday):
    days = [d for d in range(1, calendar.monthrange(year, month)[1] + 1) if dt.date(year, month, d).weekday() == weekday]
    return dt.date(year, month, days[nth - 1] if nth > 0 else days[-1])


def occurrences(ev, start, months_ahead=12):
    """Dates for one event. A one-off event uses `date` (and `end`); a repeating one uses
    `repeats: first friday` (or second/third/fourth/last + any weekday) for monthly events, or
    `repeats: every wednesday` for weekly ones, with optional `starts`, `until` and `skip` dates."""
    rule = str(ev.get('repeats') or '').strip().lower()
    if not rule:
        d = _date(ev.get('date'))
        return [(d, _date(ev.get('end')))] if d else []
    nth, _, day = rule.partition(' ')
    if (nth not in ORD and nth != 'every') or day not in DAYS:
        raise ValueError(f'{ev.get("source_file")}: "repeats" should look like "first friday" or "every wednesday", not "{rule}"')
    until = _date(ev.get('until'))
    skip = {_date(s) for s in (ev.get('skip') or [])}
    first = _date(ev.get('starts')) or start
    out, y, m = [], start.year, start.month
    limit = (start.year * 12 + start.month - 1) + months_ahead
    if nth == 'every':
        d = max(first, start)
        d += dt.timedelta(days=(DAYS[day] - d.weekday()) % 7)
        while d.year * 12 + d.month - 1 <= limit and (not until or d <= until):
            if d not in skip:
                out.append((d, None))
            d += dt.timedelta(days=7)
        return out
    while y * 12 + m - 1 <= limit:
        d = _nth_weekday(y, m, ORD[nth], DAYS[day])
        if d >= first and (not until or d <= until) and d not in skip:
            out.append((d, None))
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return out


def events():
    evs = load('events')
    for e in evs:
        e['tags'] = e.get('tags') or []
        if isinstance(e['tags'], str):
            e['tags'] = [t.strip() for t in e['tags'].split(',')]
    return evs


def documents():
    docs = load_yaml('documents.yml', []) or []
    for d in docs:
        d['year'] = str(d.get('year', '')).strip()
    return docs


def directory_updates():
    return load_yaml('directory-updates.yml', {}) or {}


# ---------------------------------------------------------------- Downtown Ambassadors
AMB_STATS = ['trash', 'recycling', 'litter', 'graffiti', 'assists', 'flower_gallons', 'snow_hours', 'project_hours']


def ambassadors():
    """The team and monthly reports from content/ambassadors.yml, newest report first."""
    data = load_yaml('ambassadors.yml', {}) or {}
    team = [t for t in (data.get('team') or []) if t and t.get('name')]
    reports = []
    for r in data.get('reports') or []:
        if not r or not r.get('month'):
            continue
        y, m = (int(x) for x in str(r['month']).strip()[:7].split('-'))
        r['year'], r['mon'] = y, m
        r['file'] = (r.get('file') or '').strip()
        r['highlights'] = [h for h in (r.get('highlights') or []) if h]
        for k in AMB_STATS:
            try:
                r[k] = int(str(r.get(k) or 0).replace(',', ''))
            except ValueError:
                raise ValueError(f'content/ambassadors.yml: {r["month"]} {k} should be a number, not "{r.get(k)}"')
        reports.append(r)
    reports.sort(key=lambda r: (r['year'], r['mon']), reverse=True)
    return team, reports


def ambassador_info():
    """Phone, hours and the header photo from the top of content/ambassadors.yml."""
    data = load_yaml('ambassadors.yml', {}) or {}
    phone = str(data.get('phone') or '').strip()
    hours = [h for h in (data.get('hours') or []) if h and h.get('days') and h.get('time')]
    return dict(phone=phone, hours=hours,
                photo=str(data.get('team_photo') or '').strip(),
                photo_alt=str(data.get('team_photo_alt') or '').strip())


# ---------------------------------------------------------------- Our team
TEAM_WHO = ['Downtown Ambassadors', 'DDA & DEGA page', 'Downtown team']
_PLACEHOLDER = re.compile(r'\[[^\]]*\]')


def _s(v):
    return str(v if v is not None else '').strip()


def team():
    """Staff, the contact list and the board from content/team.yml.
    The board list is used even while the page itself is a draft (the DDA & DEGA page shows it)."""
    f = 'content/team.yml'
    data = load_yaml('team.yml', {}) or {}
    draft = bool(data.get('draft'))

    staff = []
    for i, s in enumerate(data.get('staff') or [], 1):
        if not s:
            continue
        p = {k: _s(s.get(k)) for k in ('name', 'title', 'bio', 'pronunciation', 'pronouns', 'email', 'phone', 'photo', 'photo_alt')}
        for k in ('name', 'title', 'email'):
            if not p[k]:
                raise ValueError(f'{f}: staff member {i} needs a {k}')
        if p['photo'] and not p['photo_alt']:
            raise ValueError(f'{f}: add a photo_alt sentence describing {p["name"]}’s photo')
        p['handles'] = [_s(h) for h in (s.get('handles') or []) if _s(h)]
        staff.append(p)
    names = {p['name'] for p in staff}

    contacts = []
    for i, c in enumerate(data.get('contacts') or [], 1):
        if not c:
            continue
        need, who = _s(c.get('need')), _s(c.get('who'))
        if not need or not who:
            raise ValueError(f'{f}: contact {i} needs both "need" and "who"')
        if who not in names and who not in TEAM_WHO:
            raise ValueError(f'{f}: in "{need}", who should be a staff name from the list above or one of '
                             f'{", ".join(TEAM_WHO)}, not "{who}"')
        contacts.append(dict(need=need, detail=_s(c.get('detail')), who=who))

    members = []
    for i, m in enumerate(data.get('members') or [], 1):
        if not m or not _s(m.get('name')):
            continue
        members.append(dict(name=_s(m.get('name')), role=_s(m.get('role')) or 'Member'))

    out = dict(draft=draft, staff=staff, contacts=contacts, members=members,
               board_as_of=_s(data.get('board_as_of')),
               show_board_roster=data.get('show_board_roster', True) is not False,
               office_hours=_s(data.get('office_hours')),
               hiring_text=_s(data.get('hiring_text')), hiring_url=_s(data.get('hiring_url')))

    if not draft:
        left = []
        for p in staff:
            left += [v for k, v in p.items() if k != 'handles' and isinstance(v, str) and _PLACEHOLDER.search(v)]
            left += [h for h in p['handles'] if _PLACEHOLDER.search(h)]
        for c in contacts:
            left += [v for v in c.values() if _PLACEHOLDER.search(v)]
        left += [v for k, v in out.items() if isinstance(v, str) and _PLACEHOLDER.search(v)]
        if left:
            raise ValueError(f'{f}: replace the placeholder "{left[0]}" before publishing the page, '
                             f'or set draft: true to keep it hidden')
    return out


# ---------------------------------------------------------------- Placemaking projects
FUNDING =['Fully funded', 'Partially funded', 'Seeking funding']
LEAD = ['City', 'DEGA', 'DDA', 'DDA & DEGA']


def _lead(p):
    lead = str(p.get('lead') or '').strip()
    if lead and lead not in LEAD:
        raise ValueError(f'{p["source_file"]}: "lead" should be one of {", ".join(LEAD)}, not "{lead}"')
    return lead


def placemaking():
    """One Markdown file per project in content/placemaking, sorted by `order`."""
    out = []
    for p in load('placemaking'):
        if not p.get('title'):
            raise ValueError(f'{p["source_file"]}: add a title')
        if p.get('funding') not in FUNDING:
            raise ValueError(f'{p["source_file"]}: "funding" should be one of {", ".join(FUNDING)}, not "{p.get("funding")}"')
        for k in ('stage', 'where', 'summary', 'timeline', 'design', 'image', 'image_alt', 'news'):
            p[k] = str(p.get(k) or '').strip()
        p['lead'] = _lead(p)
        p['links'] = [l for l in (p.get('links') or []) if l and l.get('text') and l.get('url')]
        try:
            p['order'] = int(p.get('order') or 99)
        except ValueError:
            raise ValueError(f'{p["source_file"]}: "order" should be a number, not "{p.get("order")}"')
        out.append(p)
    return sorted(out, key=lambda p: (p['order'], p['title']))


# ---------------------------------------------------------------- Investing in downtown
def investments():
    """One Markdown file per private investment in content/investment, sorted by `order`."""
    out = []
    for p in load('investment'):
        if not p.get('title'):
            raise ValueError(f'{p["source_file"]}: add a title')
        for k in ('kind', 'status', 'where', 'summary', 'image', 'image_alt'):
            p[k] = str(p.get(k) or '').strip()
        p['links'] = [l for l in (p.get('links') or []) if l and l.get('text') and l.get('url')]
        try:
            p['order'] = int(p.get('order') or 99)
        except ValueError:
            raise ValueError(f'{p["source_file"]}: "order" should be a number, not "{p.get("order")}"')
        out.append(p)
    return sorted(out, key=lambda p: (p['order'], p['title']))


# ---------------------------------------------------------------- For businesses page
NEEDS = {
    'start': 'Starting up',
    'funding': 'Loans & grants',
    'advice': 'Free advice & classes',
    'network': 'Networks',
    'space': 'Space & kitchens',
    'permits': 'Permits & City help',
    'customers': 'Reaching customers',
    'hiring': 'Hiring & training',
}
STALE_MONTHS = 12


def _month(v):
    s = _s(v)
    m = re.match(r'^(\d{4})-(\d{1,2})', s)
    return (int(m.group(1)), int(m.group(2))) if m else None


def _links(item, f, label):
    out = []
    for l in item.get('links') or []:
        if not l:
            continue
        t, u = _s(l.get('text')), _s(l.get('url'))
        if not t or not u:
            raise ValueError(f'{f}: a link under "{label}" needs both text and url')
        out.append(dict(text=t, url=u))
    return out


def business_resources(today=None):
    """Everything on the For businesses page, from content/business-resources.yml.
    Returns the cleaned data plus a list of warnings for entries not checked in a year."""
    f = 'content/business-resources.yml'
    today = today or dt.date.today()
    data = load_yaml('business-resources.yml', {}) or {}
    warnings = []

    def stale(item, label):
        m = _month(item.get('checked'))
        if not m:
            warnings.append(f'"{label}" has no checked date. Add one like checked: {today.year}-{today.month:02d}')
        elif (today.year * 12 + today.month) - (m[0] * 12 + m[1]) >= STALE_MONTHS:
            warnings.append(f'"{label}" was last checked {m[0]}-{m[1]:02d}. Confirm its details and link, then update checked.')

    stats = []
    for i, s in enumerate(data.get('stats') or [], 1):
        if not s or s.get('draft'):
            continue
        st = {k: _s(s.get(k)) for k in ('number', 'label', 'source', 'source_url', 'as_of')}
        if not st['number'] or not st['label']:
            raise ValueError(f'{f}: stat {i} needs a number and a label')
        if not st['source']:
            raise ValueError(f'{f}: the stat "{st["number"]} {st["label"]}" needs a source, or add draft: true to hide it')
        stats.append(st)

    tools = []
    for i, t in enumerate(data.get('tools') or [], 1):
        if not t or t.get('draft'):
            continue
        tl = {k: _s(t.get(k)) for k in ('group', 'title', 'text')}
        if not tl['title'] or not tl['text']:
            raise ValueError(f'{f}: tool {i} needs a title and text')
        tl['group'] = tl['group'] or 'More from downtown'
        tl['links'] = _links(t, f, tl['title'])
        stale(t, tl['title'])
        tools.append(tl)

    def entries(key, need_tags):
        out = []
        for i, r in enumerate(data.get(key) or [], 1):
            if not r or r.get('draft'):
                continue
            e = {k: _s(r.get(k)) for k in ('name', 'url', 'what', 'for', 'cost')}
            if not e['name'] or not e['what']:
                raise ValueError(f'{f}: entry {i} under {key} needs a name and what')
            e['links'] = _links(r, f, e['name'])
            if need_tags:
                needs = r.get('needs') or []
                if isinstance(needs, str):
                    needs = [n.strip() for n in needs.split(',')]
                needs = [_s(n).lower() for n in needs if _s(n)]
                bad = [n for n in needs if n not in NEEDS]
                if bad:
                    raise ValueError(f'{f}: in "{e["name"]}", needs should be from {", ".join(NEEDS)}, not "{bad[0]}"')
                if not needs:
                    raise ValueError(f'{f}: "{e["name"]}" needs at least one of {", ".join(NEEDS)}')
                e['needs'] = needs
            stale(r, e['name'])
            out.append(e)
        return out

    research = []
    for i, d in enumerate(data.get('research') or [], 1):
        if not d or d.get('draft'):
            continue
        r = {k: _s(d.get(k)) for k in ('title', 'by', 'year', 'url', 'note')}
        if not r['title'] or not r['url']:
            raise ValueError(f'{f}: research item {i} needs a title and url')
        stale(d, r['title'])
        research.append(r)

    partners = []
    for i, p in enumerate(data.get('partners') or [], 1):
        if not p or p.get('draft'):
            continue
        pt = {k: _s(p.get(k)) for k in ('name', 'url', 'what')}
        if not pt['name']:
            raise ValueError(f'{f}: partner {i} needs a name')
        partners.append(pt)

    return dict(stats=stats, tools=tools, resources=entries('resources', True), develop=entries('develop', False),
                research=research, partners=partners, warnings=warnings)


# ---------------------------------------------------------------- Downtown Dollars page
def dollars():
    """content/dollars.yml, checked so a typo shows up as a clear message on the Actions tab."""
    d = load_yaml('dollars.yml', {}) or {}
    where = 'content/dollars.yml'
    for k in ('through', 'since', 'bought', 'spent', 'waiting', 'recipients', 'half_spent_weeks', 'businesses'):
        if d.get(k) in (None, ''):
            raise SystemExit(f'{where}: "{k}:" is missing or blank.')
    for k in ('bought', 'spent', 'waiting'):
        if not isinstance(d[k], int):
            raise SystemExit(f'{where}: "{k}:" should be a plain number with no $ or commas, like 392485.')
    total = sum(int(x.get('cents', 0)) for x in d.get('split') or [])
    if d.get('split') and total != 100:
        print(f'::warning file={where},title=Downtown Dollars::The cents under split: add up to {total}, not 100.')
    for m in d.get('months') or []:
        for k in ('month', 'businesses', 'bought', 'spent'):
            if k not in m:
                raise SystemExit(f'{where}: a line under months: is missing "{k}". Copy an existing line and change it.')
    r = d.get('reminder') or {}
    if r:
        r['show_from'], r['show_until'] = _date(r.get('show_from')), _date(r.get('show_until'))
    v = d.get('video') or {}
    if v.get('file'):
        for k in ('poster', 'captions', 'transcript'):
            if not v.get(k):
                raise SystemExit(f'{where}: the video needs "{k}:" too. Captions and a transcript are required so everyone can follow it.')
        for k in ('file', 'poster', 'captions'):
            if not os.path.exists(os.path.join(HERE, v[k])):
                raise SystemExit(f'{where}: video {k} "{v[k]}" isn\'t in the repository. Check the folder and spelling.')
    d['video'] = v
    return d
