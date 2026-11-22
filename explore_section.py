# Explore & visit (explore.html): the business finder, getting here, parking and questions on one page.
# Pulled into build.py with exec(), so it shares build.py's names (page, page_hero, crumbs, ext, E, EVENTS ...).
# The business list comes from the same data as the directory (directory.json plus content/directory-updates.yml),
# so every count on this page is worked out here, never typed in.
import math as _math, urllib.parse

# ---------------------------------------------------------------- Rough positions, for "Park nearby" only
# Each address is placed on a simple downtown grid: x runs east from the Kalamazoo Mall, y runs north from
# Michigan Ave, both in address numbers. It's approximate, so check the "Park nearby" picks before publishing.
_EX_NS = {'westnedge': -480, 'park': -330, 'church': -260, 'rose': -200, 'kalamazoo mall': 0, 'burdick': 0,
       'edwards': 120, 'pitcher': 300, 'harrison': 560}
_EX_EW = {'kalamazoo': 380, 'eleanor': 250, 'water': 150, 'farmers alley': 70,
       'michigan': 0, 'main': 0, 'south': -320, 'lovell': -470}
_EX_PORTAGE = ((230, 0), (0.62, -0.78))   # starts at Michigan Ave and runs southeast


def ex_approx_xy(where):
    w = re.sub(r'\s*(#|suite|ste\b|unit|,|·).*$', '', (where or '').lower()).replace('.', '')
    if 'park trades' in (where or '').lower():
        return (-326, 380)
    m = re.match(r'(\d+)\s+(.*)', w)
    if not m:
        return None
    n, rest = int(m.group(1)), m.group(2)
    side = 1
    if re.match(r'(w|west)\s', rest):
        side = -1
    north = 1 if re.match(r'(n|north)\s', rest) else -1
    rest = re.sub(r'^(n|s|e|w|north|south|east|west)\s+', '', rest)
    rest = re.sub(r'\s+(st|street|ave|avenue)$', '', rest).strip()
    if rest.startswith('portage'):
        (x0, y0), (dx, dy) = _EX_PORTAGE
        return (x0 + dx * n, y0 + dy * n)
    for k, x in _EX_NS.items():
        if rest.startswith(k):
            return (x, north * n)
    for k, y in _EX_EW.items():
        if rest.startswith(k):
            return (side * n, y)
    return None


# Public parking and transit. Positions are approximate (preview).
EX_PARKING = [
    dict(id='park-epic', name='Epic Center Ramp', short='Epic Center Ramp', kind='ramp', where='136 E. South St.', xy=(136, -335)),
    dict(id='park-mall', name='Kalamazoo Mall Ramp', short='Kalamazoo Mall Ramp', kind='ramp', where='130 Portage St.', xy=(311, -101)),
    dict(id='park-arcadia', name='Arcadia Ramp (Ramp 4)', short='Arcadia Ramp', kind='lot', where='Rose St. at Eleanor St.', xy=(-200, 250)),
    dict(id='park-radisson', name='Radisson Plaza ramp', short='Radisson Plaza ramp', kind='lot', where='W. Michigan Ave. at Rose St.', xy=(-230, 30)),
    dict(id='park-bells', name='Bell’s Parking Emporium', short='Bell’s Parking Emporium', kind='lot', where='N. Pitcher St. at E. Kalamazoo Ave.', xy=(300, 395)),
]
EX_TRANSIT = dict(name='Kalamazoo Transportation Center', where='459 N. Burdick St.', xy=(0, 459))
EX_TROLLEY_START = dict(name='City Hall, trolley start', where='241 W. South St.', xy=(-241, -335))
EX_RAMP_BONUS = 60   # a city ramp wins over a slightly closer private lot, for the 90 free minutes


def ex_nearest_parking(xy):
    if not xy:
        return None
    best = min(EX_PARKING, key=lambda p: _math.dist(xy, p['xy']) - (EX_RAMP_BONUS if p['kind'] == 'ramp' else 0))
    return best


# ---------------------------------------------------------------- One place in the list
def _ex_place_row(b, xy, near, origin):
    import directory_page as D
    gifts = D.GIFTS.get(b['id'])
    evs = D.EVENTS.get(b['id'])
    tags = (D.dd_badge('Downtown Dollars') if b['dd'] else '') + (D.sd_badge() if b.get('sd') else '') + (D.gift_badge('Gift Guide') if gifts else '')
    week = D.week_hours(b.get('hours'))
    today = (f'<p class="biz-today" data-hours="{E(json.dumps(week, ensure_ascii=False))}" hidden></p>' if week else '')
    hours_line = '<br>'.join(E(x) for x in (b.get('hours') or [])) or 'Hours not listed yet'
    directions = 'https://www.google.com/maps/dir/?api=1&destination=' + urllib.parse.quote_plus(b['address'] or (b['where'] + ', Kalamazoo, MI'))
    acts = [f'<a class="btn btn-small btn-primary" href="{E(directions)}" target="_blank" rel="noopener">Directions<span class="sr-only"> to {E(b["name"])} (opens in a new tab)</span></a>']
    if near:
        acts.append(f'<a class="btn btn-small btn-quiet" href="#{near["id"]}">Park nearby: {E(near["short"])}</a>')
    if b.get('website'):
        acts.append(f'<a class="ex-link" href="{E(b["website"])}" target="_blank" rel="noopener">Website<span class="sr-only"> for {E(b["name"])} (opens in a new tab)</span></a>')
    if b.get('phone'):
        acts.append(f'<a class="ex-link" href="{E(b["tel"])}">{E(b["phone"])}</a>')
    search = ' '.join([b['name'], b['where'], b['cat_label']] + list(b.get('aliases') or [])).lower()
    pos = ''
    return (f'<li class="ex-place" id="p-{b["id"]}" data-cat="{b["cat"]}" data-dd="{1 if b["dd"] else 0}" data-sd="{1 if b.get("sd") else 0}" '
            f'data-gift="{1 if gifts else 0}" data-search="{E(search)}"{pos}>'
            f'<div class="ex-body">'
            f'<p class="ex-cat"><span class="chip-swatch" aria-hidden="true" style="background-image:url({{R}}pattern-{D.CAT_PATTERN.get(b["cat"], "squiggle")}-sm.webp)"></span>{E(b["cat_label"])}</p>'
            f'<h3 class="ex-name">{E(b["name"])}</h3>'
            f'<p class="ex-where">{E(b["where"])}</p>'
            f'<div class="ex-meta">{today}<details class="ex-hours"><summary>All hours<span class="sr-only"> for {E(b["name"])}</span></summary><p>{hours_line}</p></details></div>'
            + (f'<div class="biz-tags">{tags}</div>' if tags else '')
            + f'<div class="ex-acts">{"".join(acts)}</div></div></li>')


# ---------------------------------------------------------------- The page
def build_explore():
    import directory_page as D
    seasonal = trolley_in_season()
    biz = D.BIZ
    total = len(biz)
    counts = {c: sum(1 for b in biz if b['cat'] == c) for c, _ in D.BIZ_CATS}
    n_dd = sum(1 for b in biz if b['dd'])
    n_sd = sum(1 for b in biz if b.get('sd'))
    n_gift = sum(1 for b in biz if D.GIFTS.get(b['id']))
    origin = (0, 0)
    rows, unplaced = [], []
    for b in biz:
        xy = ex_approx_xy(b['where'])
        if not xy:
            unplaced.append(b['name'])
        rows.append(_ex_place_row(b, xy, ex_nearest_parking(xy), origin))
    if unplaced:
        print('explore.html: no Park nearby for (address not understood)', ', '.join(unplaced))

    chips = (f'<li><button type="button" class="chip" data-cat="all" aria-pressed="true">All<span class="n">{total}</span></button></li>'
             + ''.join(f'<li><button type="button" class="chip" data-cat="{c}" aria-pressed="false"><span class="chip-swatch" aria-hidden="true" '
                       f'style="background-image:url({{R}}pattern-{D.CAT_PATTERN[c]}-sm.webp)"></span>{E(l)}<span class="n">{counts[c]}</span></button></li>'
                       for c, l in D.BIZ_CATS if counts[c]))
    flags = (f'<li><button type="button" class="chip chip-dd" data-flag="dd" aria-pressed="false"><span class="dd-coin" aria-hidden="true" style="margin-inline-end:.4rem">$</span>Takes Downtown Dollars<span class="n">{n_dd}</span></button></li>'
             f'<li><button type="button" class="chip chip-sd" data-flag="sd" aria-pressed="false"><span class="sd-cup" aria-hidden="true" style="margin-inline-end:.4rem"></span>Social District<span class="n">{n_sd}</span></button></li>'
             + (f'<li><button type="button" class="chip chip-gift" data-flag="gift" aria-pressed="false"><span class="gift-swatch" aria-hidden="true" style="background-image:url({{R}}pattern-stripes-sm.webp);margin-inline-end:.4rem"></span>Holiday Gift Guide<span class="n">{n_gift}</span></button></li>' if n_gift else ''))

    trolley_fact = ('<div class="ex-fact-season"><dt>This season</dt><dd>Free Holly Jolly Trolley, Thursday to Sunday</dd></div>' if seasonal else '')
    facts = (f'<dl class="glance ex-facts">'
             f'<div><dt>City ramps</dt><dd>First 90 minutes free</dd></div>'
             f'<div><dt>Street parking</dt><dd>First 30 minutes free</dd></div>'
             f'<div><dt>Sundays</dt><dd>Free parking all day</dd></div>{trolley_fact}</dl>')
    search = (f'<form class="hero-search" id="ex-search" action="{{R}}directory.html" method="get" role="search" aria-label="Search downtown places">'
              f'<label for="ex-q">Search {total} downtown places</label>'
              f'<div class="hs-row"><input type="search" id="ex-q" name="q" placeholder="Business name, street or building" autocomplete="off">'
              f'<button class="btn btn-primary" type="submit">Search</button></div></form>')
    lede = f'{total} places, a few blocks apart. Find where you’re going, then how to get here and where to park.'
    body = page_hero([('index.html', 'Home'), ('explore.html', 'Explore & visit')], 'Find it downtown', 'Explore &amp; visit', lede, 'f-green', search + facts)

    body += '''<nav class="jump ex-jump" aria-label="On this page"><div class="wrap"><ul class="chips">
  <li><a class="chip" href="#find">Find a place</a></li><li><a class="chip" href="#getting-here">Getting here</a></li>
  <li><a class="chip" href="#parking">Parking</a></li>
  <li><a class="chip" href="#help">Questions</a></li></ul></div></nav>'''

    body += f'''<section class="section" id="find" aria-labelledby="find-title">
  <div class="wrap">
    <div class="section-head">
      <div><h2 class="h2" id="find-title">Find a place</h2>
      <p class="muted">Pick a type of place to see what’s here, how to get directions and where to park nearby.</p></div>
      <a class="ex-all" href="{{R}}directory.html">Open the full directory ({total} places)</a>
    </div>
    <div class="dir-tools ex-tools">
      <div class="field"><span class="label" id="ex-cats-label">Type of place</span><div role="group" aria-labelledby="ex-cats-label"><ul class="chips" id="ex-cats">{chips}</ul></div></div>
      <div class="field"><span class="label" id="ex-flags-label">Show only</span><div role="group" aria-labelledby="ex-flags-label"><ul class="chips" id="ex-flags">{flags}</ul></div></div>
    </div>
    <div class="ex-finder">
      <div class="ex-results">
        <p class="dir-result"><span id="ex-count" role="status" aria-live="polite">Showing all {total} places</span>
          <button type="button" class="linkish" id="ex-clear" hidden>Clear filters</button></p>
        <ol class="ex-list" id="ex-list">{"".join(rows)}</ol>
        <p class="panel" id="ex-empty" hidden>No places match. Try another type, clear the filters, or <a href="{{R}}directory.html">browse the full directory</a>.</p>
        <p class="ex-more-row"><button type="button" class="btn" id="ex-more" hidden>Show more places</button></p>
      </div>
    </div>
  </div>
</section>'''

    # Getting here
    trolley_band = ''
    if seasonal:
        trolley_band = '''<!-- SEASONAL: shows only during the holiday season (trolley_in_season in build.py) -->
    <div class="ex-trolley">
      <div class="ex-trolley-pat" aria-hidden="true"></div>
      <div class="ex-trolley-copy">
        <h3 class="h3">This season: Holly Jolly Trolley</h3>
        <p>Park once and ride free. The trolley loops downtown Thursday through Sunday until Christmas Eve, plus New Year’s Eve, starting at City Hall, 241 W. South St. It stops near Santa’s Workshop, Bell’s Eccentric Café and the Kalamazoo Valley Museum.</p>
      </div>
      <a class="btn btn-primary" href="{R}events/holly-jolly-trolley.html">Trolley stops and hours</a>
    </div>'''
    body += f'''<section class="section band" id="getting-here" aria-labelledby="here-title">
  <div class="wrap">
    <div class="section-head"><div><h2 class="h2" id="here-title">Getting here</h2>
      <p class="lede">Downtown is easy to walk once you arrive. The Kalamazoo Mall is a pedestrian street, and Bronson Park is a short walk west at 200 S. Rose St.</p></div></div>
    <ul class="cards ex-ways">
      <li class="card f-blue"><div class="card-top">Driving</div><div class="card-body">
        <p>Use a city ramp for a longer visit or the street for a quick stop. On event nights, ramps and nearby blocks fill up, so give yourself extra time or park a few blocks out and walk in.</p>
        <p><a href="#parking">Parking options and rates</a></p></div></li>
      <li class="card f-green"><div class="card-top">Bus &amp; train</div><div class="card-body">
        <p>Kalamazoo Metro routes meet at the Kalamazoo Transportation Center, 459 N. Burdick St., a few blocks north of the Kalamazoo Mall. Amtrak, Greyhound and Indian Trails stop there too.</p>
        <p>{ext('https://www.kmetro.com/', 'Plan a Metro trip')}</p></div></li>
      <li class="card f-red"><div class="card-top">Biking</div><div class="card-body">
        <p>Park Kalamazoo rents secure bike lockers by the month, season or year. Call (269) 342-6383 to ask about one.</p></div></li>
    </ul>
    {trolley_band}
  </div>
</section>'''

    # Parking
    ramp_rates = [('First 90 minutes', 'Free'), ('Next hour', '$2'), ('Each additional half hour', '$1'), ('Sundays', 'Free all day')]
    ramp_rate_rows = ''.join(f'<tr><th scope="row">{a}</th><td class="num">{b}</td></tr>' for a, b in ramp_rates)
    street = [('Premium blocks, in the core of downtown', '$2 an hour', 'Monday to Saturday, 10 a.m. to 5 p.m.'),
              ('Base blocks, on surrounding streets', '$1.50 an hour', 'Weekdays, 10 a.m. to 5 p.m.'),
              ('Free blocks', 'Free', 'Follow the time limit on the sign')]
    street_rows = ''.join(f'<tr><th scope="row">{a}</th><td>{b}</td><td>{c}</td></tr>' for a, b, c in street)
    ramp_ids = {'Epic Center Ramp (Ramp 2)': 'park-epic', 'Kalamazoo Mall Ramp (Ramp 3)': 'park-mall'}
    ramp_rows = ''.join(f'<tr id="{ramp_ids.get(n, "")}"><th scope="row">{E(n)}</th><td>{ext(_map(w), E(w))}</td><td>{E(note)}</td></tr>' for n, w, note in CITY_RAMPS)
    other_ids = {'Radisson Plaza ramp': 'park-radisson', 'Arcadia Ramp (Ramp 4)': 'park-arcadia', 'Bell’s Parking Emporium': 'park-bells'}
    other_items = ''.join(
        f'<li class="panel" id="{other_ids.get(o["name"], "")}"><h3>{E(o["name"])}</h3><p>{E(o["where"])}</p><p>{E(o["note"])}</p><p>{ext(o["link"][1], E(o["link"][0]))}</p></li>'
        for o in OTHER_PARKING)
    lot_items = ''.join(f'<li><strong>{E(n)}</strong>, {ext(_map(w), E(w))}</li>' for n, w in CITY_LOTS)
    pk_links = ''.join(f'<li>{ext(u, E(t))}</li>' for t, u in PARK_KZOO_PAGES)
    body += f'''<section class="section" id="parking" aria-labelledby="parking-title">
  <div class="wrap">
    <div class="section-head"><div><h2 class="h2" id="parking-title">Parking</h2>
      <p class="lede">For a longer visit, use a city ramp. For a quick stop, park on the street. On Sundays, both are free.</p></div></div>
    <div class="two-col">
      <div class="prose" style="max-width:none">
        <h3 class="h3" id="ramps-title">City parking ramps</h3>
        <p>The city’s two downtown ramps are a short walk from the Kalamazoo Mall and most downtown restaurants, and you don’t have to watch a meter.</p>
        <div class="table-wrap"><table><caption>City parking ramps</caption><thead><tr><th scope="col">Ramp</th><th scope="col">Entrance</th><th scope="col">Good to know</th></tr></thead><tbody>{ramp_rows}</tbody></table></div>
        <div class="table-wrap"><table><caption>Ramp rates</caption><thead><tr><th scope="col">Time parked</th><th scope="col" class="num">Cost</th></tr></thead><tbody>{ramp_rate_rows}</tbody></table></div>
        <h3 class="h3" id="street-title" style="margin-top:1rem">Street parking</h3>
        <p>Downtown blocks are paid, free or time-limited. The sign or kiosk on each block tells you which.</p>
        <div class="table-wrap"><table><caption>Street parking rates and hours</caption><thead><tr><th scope="col">Where</th><th scope="col">Rate</th><th scope="col">When you pay</th></tr></thead><tbody>{street_rows}</tbody></table></div>
        <ul>
          <li><strong>The first 30 minutes are free</strong> on paid blocks, but you still need to start a session with your license plate at a kiosk or in the ParkMobile app.</li>
          <li><strong>Pay</strong> at a kiosk with coins, a credit card or a debit card, or with the {ext('https://parkmobile.io/', 'ParkMobile app')}. You can add time from your phone.</li>
          <li><strong>Most blocks allow up to three hours.</strong> Check the sign for the limit.</li>
          <li><strong>Sundays and holidays</strong> are free on the street.</li>
          <li><strong>No street parking from 2 to 6 a.m.</strong> unless you have a residential permit.</li>
        </ul>
      </div>
      <div class="aside">
        <section class="panel f-green" aria-labelledby="pk-title"><h3 id="pk-title">Park Kalamazoo</h3>
          <p>Runs the city’s ramps, lots and meters.</p>
          <p>215 E. Water St.<br>Monday to Friday, 8 a.m. to 4 p.m.<br>(269) 342-6383</p>
          <ul>{pk_links}</ul>
        </section>
        <section class="panel" aria-labelledby="monthly-title"><h3 id="monthly-title">Monthly parking</h3>
          <p>Work or live downtown? Park Kalamazoo sells monthly permits for both city ramps, a 10-hour street meter permit, and these city lots:</p>
          <ul>{lot_items}</ul>
          <p>Apply on the {ext('https://parkkalamazoo.org/parking-permits-1', 'Park Kalamazoo permits page')}. Permits are usually approved within one business day.</p>
        </section>
      </div>
    </div>
    <h3 class="h3" id="other-title" style="margin-block:2rem .5rem">More public parking</h3>
    <p style="margin-bottom:1rem">These ramps and lots are privately run but open to the public. Each sets its own rates and hours, so check before you go.</p>
    <ul class="cards ex-other">{other_items}</ul>
  </div>
</section>'''

    # Questions
    body += f'''<section class="section band" id="help" aria-labelledby="help-title">
  <div class="wrap">
    <h2 class="h2" id="help-title" style="margin-bottom:1.25rem">Questions?</h2>
    <ul class="cards ex-help">
      <li class="panel"><h3>City of Kalamazoo</h3><p>Call 311 or (269) 337-8000, or email <a href="mailto:311@kalamazoocity.org">311@kalamazoocity.org</a>.</p></li>
      <li class="panel"><h3>Park Kalamazoo</h3><p>215 E. Water St.<br>Monday to Friday, 8 a.m. to 4 p.m.<br>(269) 342-6383</p></li>
      <li class="panel"><h3>Parking tickets and meters</h3><ul>
        <li>{ext('https://parkkalamazoo.org/paycitation', 'Pay a parking ticket')}</li>
        <li>{ext('https://parkkalamazoo.org/need-to-reserve-a-meter', 'Reserve a meter for an event or move')}</li></ul></li>
    </ul>
  </div>
</section>'''
    body += '<script>' + EXPLORE_JS + '</script>'
    desc = (f'Find {total} shops, restaurants and things to do in Downtown Kalamazoo, then how to get here and where to park: '
            'city ramps with 90 free minutes, street parking rates and transit.')
    page('explore.html', 'Explore & visit', body, 'explore', desc)


EXPLORE_JS = r'''
(() => {
  const $ = (s, el = document) => el.querySelector(s), $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const list = $('#ex-list'); if (!list) return;
  const items = $$('.ex-place', list), cats = $$('#ex-cats .chip'), flags = $$('#ex-flags .chip');
  const count = $('#ex-count'), empty = $('#ex-empty'), more = $('#ex-more'), clear = $('#ex-clear');
  const q = $('#ex-q');
  const PAGE = 18;
  let cat = 'all', on = new Set(), shown = PAGE, term = '';
  const total = items.length;
  const header = $('.site-header');
  const setH = () => document.documentElement.style.setProperty('--header-h', (header ? header.offsetHeight : 64) + 'px');
  setH(); addEventListener('resize', setH);

  // "Open today", worked out in the visitor's own day (same as the directory)
  const dow = String(new Date().getDay());
  $$('.biz-today[data-hours]', list).forEach(p => {
    let w = {}; try { w = JSON.parse(p.dataset.hours); } catch (e) { return; }
    if (!(dow in w)) return;
    p.textContent = w[dow] ? `Open today ${w[dow]}` : 'Closed today'; p.hidden = false;
  });

  function matches(li) {
    if (cat !== 'all' && li.dataset.cat !== cat) return false;
    for (const f of on) if (li.dataset[f] !== '1') return false;
    if (term && !li.dataset.search.includes(term)) return false;
    return true;
  }
  function render(focusFrom) {
    const hits = items.filter(matches);
    items.forEach(li => { li.hidden = true; });
    hits.forEach((li, i) => { li.hidden = i >= shown; });
    const filtered = cat !== 'all' || on.size || term;
    count.textContent = hits.length === total ? `Showing all ${total} places` : `Showing ${hits.length} of ${total} places`;
    empty.hidden = hits.length > 0;
    clear.hidden = !filtered;
    const left = hits.length - shown;
    more.hidden = left <= 0;
    more.textContent = left > 0 ? `Show ${Math.min(PAGE, left)} more of ${left}` : '';
    if (focusFrom != null && hits[focusFrom]) { const h = $('.ex-name', hits[focusFrom]); h.tabIndex = -1; h.focus(); }
  }
  cats.forEach(b => b.addEventListener('click', () => {
    cat = b.dataset.cat; cats.forEach(c => c.setAttribute('aria-pressed', String(c === b))); shown = PAGE; render();
  }));
  flags.forEach(b => b.addEventListener('click', () => {
    const f = b.dataset.flag, now = !on.has(f); now ? on.add(f) : on.delete(f); b.setAttribute('aria-pressed', String(now)); shown = PAGE; render();
  }));
  more.addEventListener('click', () => { const from = shown; shown += PAGE; render(from); });
  clear.addEventListener('click', () => {
    cat = 'all'; on.clear(); term = ''; if (q) q.value = ''; shown = PAGE;
    cats.forEach(c => c.setAttribute('aria-pressed', String(c.dataset.cat === 'all'))); flags.forEach(f => f.setAttribute('aria-pressed', 'false')); render();
  });
  // The hero search filters this list in place (without JavaScript it opens the full directory).
  const form = $('#ex-search');
  if (form) form.addEventListener('submit', e => {
    e.preventDefault(); term = q.value.trim().toLowerCase(); shown = PAGE; render();
    $("#find").scrollIntoView();
  });
  if (q) q.addEventListener('input', () => { term = q.value.trim().toLowerCase(); shown = PAGE; render(); });
  const h = location.hash.replace('#', '');
  if (cats.some(c => c.dataset.cat === h)) $(`#ex-cats [data-cat="${h}"]`).click(); else render();
})();
'''
