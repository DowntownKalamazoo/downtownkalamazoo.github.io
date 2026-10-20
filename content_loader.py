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


def occurrences(ev, start, months_ahead=9):
    """Dates for one event. A one-off event uses `date` (and `end`); a repeating one uses
    `repeats: first friday` (or second/third/fourth/last + any weekday), with optional `until` and `skip` dates."""
    rule = str(ev.get('repeats') or '').strip().lower()
    if not rule:
        d = _date(ev.get('date'))
        return [(d, _date(ev.get('end')))] if d else []
    nth, _, day = rule.partition(' ')
    if nth not in ORD or day not in DAYS:
        raise ValueError(f'{ev.get("source_file")}: "repeats" should look like "first friday", not "{rule}"')
    until = _date(ev.get('until'))
    skip = {_date(s) for s in (ev.get('skip') or [])}
    first = _date(ev.get('starts')) or start
    out, y, m = [], start.year, start.month
    limit = (start.year * 12 + start.month - 1) + months_ahead
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


# ---------------------------------------------------------------- Placemaking projects
FUNDING = ['Fully funded', 'Partially funded', 'Seeking funding']
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
