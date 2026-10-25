#!/usr/bin/env python3
"""Turns the staff directory spreadsheet into directory.json for the website.

Usage:  python3 import_directory.py data/DK_Directory_2026-10-19.xlsx [data/DK_Directory_with_web_research.xlsx]

The first file is the staff spreadsheet and decides which businesses appear and their details.
The optional second file is the October 2026 web-research workbook: where the staff sheet leaves a website,
description, address or phone blank, the researched value fills in.

Rules
- Only rows with show_on_site = TRUE are published.
- Only public columns are read. Email (private), Issues to review and Staff note never leave the spreadsheet.
- Website and Description appear on a card as soon as they are filled in. Hours are not published.
- When Address or Phone is blank, the web-research 'Suggested address' / 'Suggested phone' columns fill in.
- MERGE lists obvious duplicate rows. The dropped row's Downtown Dollars status carries over to the kept row.
- ADDRESS_HOLD hides an address that is clearly wrong until staff correct it in the spreadsheet.
"""
import json, re, sys, os
import openpyxl

CATS = {  # spreadsheet "Public category" -> (id, label, brand fill)
    'Shop': ('shop', 'Shop', 'f-pink'),
    'Dine': ('dine', 'Dine', 'f-green'),
    'Arts & Entertainment': ('arts', 'Arts & Entertainment', 'f-red'),
    'Services': ('services', 'Services', 'f-blue'),
    'Stay': ('stay', 'Stay', 'f-mist'),
    'Offices & professional': ('offices', 'Offices & professional', 'f-blue'),
    'Organizations': ('orgs', 'Organizations', 'f-green'),
}

# dropped row name -> row it merges into
MERGE = {
    'Beowoof Provisions': 'Beowoof Provisions for Pets',
    'Pedal': 'PEDAL Bicycles',
    'The Station': 'The Station: Dancewear and Studios',
    'Water Street Coffee Joint - Downtown': 'Water Street Coffee Joint',
}
# addresses that are clearly not downtown Kalamazoo; held back until staff confirm
ADDRESS_HOLD = {
    'Gazelle Sports': 'Listed as 24 W 8th St, Holland (ZIP 49423). That is the Holland store.',
}


def truthy(v):
    return str(v).strip().upper() in ('TRUE', 'YES', '1', 'Y')


def clean(v):
    if v is None:
        return ''
    s = str(v).strip()
    return '' if s.upper() in ('NONE', 'N/A', 'NA') else s


def tidy_address(a):
    a = a.replace("\\'", "'")
    a = re.sub(r',\s*,', ',', a)
    a = re.sub(r',\s*Suite #[A-Za-z\'’]+(?=,)', '', a)  # import artifacts like "Suite #Cherri'S"
    a = re.sub(r'\s{2,}', ' ', a)
    return a.strip(' ,')


def short_street(addr):
    return addr.split(',')[0].strip() if addr else ''


def tel_href(phone):
    m = re.match(r'\D*(\d{3})\D*(\d{3})\D*(\d{4})(?:\s*ext\.?\s*(\d+))?', phone or '')
    if not m:
        return ''
    num = '+1' + ''.join(m.groups()[:3])
    return f'tel:{num},{m.group(4)}' if m.group(4) else f'tel:{num}'


# staff-sheet name -> research-workbook name, where the row was renamed or split
RESEARCH_ALIAS = {
    'The Radisson Hotel': 'The Radisson Hotel (includes Blush Spa, Rio Gift Shop, Brick+Brine, Burdicks)',
}


def clean_url(u):
    """Drop tracking parameters (fbclid, utm_*) from links."""
    import urllib.parse as up
    if not u:
        return u
    parts = up.urlsplit(u)
    q = [(k, v) for k, v in up.parse_qsl(parts.query) if not (k.lower() == 'fbclid' or k.lower().startswith('utm_'))]
    return up.urlunsplit(parts._replace(query=up.urlencode(q)))


def load_research(path):
    if not path or not os.path.exists(path):
        return {}
    ws = openpyxl.load_workbook(path, data_only=True)['Directory']
    hdr = [clean(c.value) for c in ws[1]]
    return {clean(r[1]): {h: clean(v) for h, v in zip(hdr, r)} for r in ws.iter_rows(min_row=2, values_only=True) if r[1]}


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def main(path, out, research_path=None):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb['Directory']
    hdr = [clean(c.value) for c in ws[1]]
    col = {h: i for i, h in enumerate(hdr)}
    # A Website cell may show a page title while the real address sits in its hyperlink.
    links = {}
    wcol = col.get('Website')
    if wcol is not None:
        for row in openpyxl.load_workbook(path)['Directory'].iter_rows(min_row=2):
            c = row[wcol]
            if c.hyperlink and c.hyperlink.target and row[1].value:
                links[clean(row[1].value)] = c.hyperlink.target
    research = load_research(research_path)
    def g(r, name):
        i = col.get(name)
        v = clean(r[i]) if i is not None and i < len(r) else ''
        if not v and name in ('Website', 'Description (English, about 25 words)', 'Descripción (español)',
                              'Suggested address (web research)', 'Suggested phone (web research)'):
            bn = clean(r[col['Business name']])
            v = research.get(RESEARCH_ALIAS.get(bn, bn), {}).get(name, '')
        return v

    rows = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not g(r, 'Business name') or not truthy(g(r, 'show_on_site')):
            continue
        cat = CATS.get(g(r, 'Public category'))
        if not cat:
            continue
        rows.append(r)

    by_name = {g(r, 'Business name'): r for r in rows}
    dd_carry = {keep for drop, keep in MERGE.items() if drop in by_name and truthy(g(by_name[drop], 'Accepts Downtown Dollars (TRUE/FALSE)'))}

    out_list, seen = [], set()
    for r in rows:
        name = g(r, 'Business name')
        if name in MERGE and MERGE[name] in by_name:
            continue
        cat = CATS[g(r, 'Public category')]
        includes = ''
        m = re.match(r'^(.*?)\s*\(includes (.+)\)\s*$', name, re.I)
        if m:
            name, includes = m.group(1).strip(), m.group(2).strip()
        addr = '' if g(r, 'Business name') in ADDRESS_HOLD else tidy_address(g(r, 'Address'))
        if not addr:
            addr = tidy_address(g(r, 'Suggested address (web research)'))
        building, studio = g(r, 'Building'), g(r, 'Studio #')
        where = ' · '.join(x for x in [building, f'Studio {studio}' if studio else ''] if x) or short_street(addr)
        phone = g(r, 'Phone') or g(r, 'Suggested phone (web research)')
        website = links.get(g(r, 'Business name')) or g(r, 'Website')
        if website and ' ' in website.strip() and not re.match(r'^https?://', website, re.I):
            website = ''   # a page title with no link behind it
        website = clean_url(website)
        if website and not re.match(r'^https?://', website, re.I):
            website = 'https://' + website
        sid = slug(name)
        while sid in seen:
            sid += '-2'
        seen.add(sid)
        out_list.append(dict(
            id=sid, name=name, cat=cat[0], cat_label=cat[1], fill=cat[2],
            address=addr, where=where, phone=phone, tel=tel_href(phone),
            website=website,
            desc=g(r, 'Description (English, about 25 words)'), desc_es=g(r, 'Descripción (español)'),
            includes=includes,
            dd=truthy(g(r, 'Accepts Downtown Dollars (TRUE/FALSE)')) or g(r, 'Business name') in dd_carry,
            featured=truthy(g(r, 'Featured (TRUE/FALSE)')),
            sd=truthy(g(r, 'Social District (TRUE/FALSE)')),
        ))
    out_list.sort(key=lambda b: (not b['featured'], re.sub(r'^the\s+', '', b['name'].lower())))
    with open(out, 'w') as f:
        json.dump(out_list, f, ensure_ascii=False, indent=1)
    print(f'{len(out_list)} businesses written to {out} '
          f'({sum(b["dd"] for b in out_list)} accept Downtown Dollars, {sum(b["sd"] for b in out_list)} in the Social District)')


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, 'data', 'DK_Directory_2026-10-19_FILLED.xlsx')
    res = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, 'data', 'DK_Directory_with_web_research.xlsx')
    main(src, os.path.join(here, 'directory.json'), res)
