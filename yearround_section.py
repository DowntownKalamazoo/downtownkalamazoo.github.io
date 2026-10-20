# ---------------------------------------------------------------- Year-round site
# Pages for the permanent Downtown Kalamazoo site. Runs inside build.py (exec'd), so it uses its helpers:
# page, page_hero, in_short, ext, E, date_tile, MON, DOW, EVENTS, SD, directory_page, weave, snow, k_window ...
import content_loader as CL

TODAY = dt.date.fromisoformat(os.environ['DK_TODAY']) if os.environ.get('DK_TODAY') else dt.date.today()
DOWNTOWN_EMAIL = 'downtown@kalamazoocity.org'
DOWNTOWN_PHONE = '(269) 337-8993'
CITY = 'https://www.kalamazoocity.org'
BOARDS_URL = CITY + '/Government/Boards-Commissions/Downtown-Development-Authority-Downtown-Economic-Growth-Authority'
DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
MONTH_NAMES = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


def long_date(d):
    return f'{MONTH_NAMES[d.month]} {d.day}, {d.year}'


def sources_list(items, level='h2'):
    return f'<{level} class="h3" style="margin-top:2rem">Sources</{level}><ul class="sources">' + ''.join(f'<li>{ext(h, E(t))}</li>' for t, h in items) + '</ul>'


def status_tag(text):
    cls = {'Underway': 'st-now', 'Planned': 'st-next', 'Complete': 'st-done', 'In design': 'st-next', 'Open for comment': 'st-now',
           'In planning': 'st-next', 'Fully funded': 'st-now', 'Partially funded': 'st-next', 'Seeking funding': 'st-done'}.get(text, '')
    return f'<span class="status-tag {cls}">{E(text)}</span>'


# ---------------------------------------------------------------- Calendar data
NEWS = CL.news()
CAL_EVENTS = CL.events()


def calendar_items():
    items = []
    for e in EVENTS:
        items.append(dict(date=e['date'], end=e.get('end'), title=e['title'], when=e['when_short'], where=e['where_short'],
                          summary=e['summary'], href=f'holidays/events/{e["slug"]}.html', external=False, fill=e['fill'], tags=['Holidays']))
    for ev in CAL_EVENTS:
        for d, end in CL.occurrences(ev, TODAY.replace(day=1)):
            href = f'events/{ev["slug"]}.html' if ev.get('body_html') else (ev.get('link') or '')
            when = f'{DOW[d.weekday()]}, {MON[d.month]} {d.day}' + (f' · {ev["time"]}' if ev.get('time') else '')
            items.append(dict(date=d.isoformat(), end=end.isoformat() if end else None, title=ev['title'], when=when, where=ev.get('where', ''),
                              summary=ev.get('summary', ''), href=href, external=not ev.get('body_html') and bool(ev.get('link')),
                              fill=ev.get('fill', 'f-green'), tags=ev['tags']))
    items = [o for o in items if dt.date.fromisoformat(o['end'] or o['date']) >= TODAY]
    return sorted(items, key=lambda o: (o['date'], o['title']))


def cal_row(o, heading='h3', show_tags=True):
    end = o['end'] or o['date']
    if o['external']:
        title = ext(o['href'], E(o['title']))
    elif o['href']:
        title = f'<a href="{{R}}{o["href"]}">{E(o["title"])}</a>'
    else:
        title = E(o['title'])
    tags = ''.join(f'<span class="mini-tag">{E(t)}</span>' for t in o['tags']) if show_tags else ''
    return f'''<li class="event-row" data-end="{end}" data-tags="{E('|'.join(o['tags']))}">
  {date_tile(o)}
  <div class="body">
    <{heading} class="h3">{title}</{heading}>
    <p class="meta"><span>{E(o["when"])}</span>{f'<span>{E(o["where"])}</span>' if o['where'] else ''}</p>
    <p>{E(o["summary"])}</p>
    {f'<p class="tags">{tags}</p>' if tags else ''}
  </div>
</li>'''


# ---------------------------------------------------------------- Home
def news_card(p, heading='h3'):
    href = p.get('source_url') if p['type'] == 'In the news' and not p['body_html'] else f'news/{p["slug"]}.html'
    link = ext(href, E(p['title'])) if href.startswith('http') else f'<a href="{{R}}{href}">{E(p["title"])}</a>'
    src = f'<p class="news-source">{"From " if p["type"] == "In the news" else ""}{E(p.get("source") or p.get("author") or "")}</p>' if (p.get('source') or p.get('author')) else ''
    return f'''<li class="news-item" data-type="{E(p['type'])}"><article>
  <p class="news-meta"><span class="type-tag t-{re.sub(r'[^a-z]+', '-', p['type'].lower())}">{E(p['type'])}</span><time datetime="{p['date']}">{long_date(p['date'])}</time></p>
  <{heading} class="news-title">{link}</{heading}>
  <p>{E(p.get('summary', ''))}</p>
  {src}
</article></li>'''


CATEGORY_TILES = [
    ('directory.html#shop', 'Shop', 'confetti', 'f-pink'),
    ('directory.html#dine', 'Dine & drink', 'dots', 'f-green'),
    ('directory.html#arts', 'Arts & entertainment', 'arcs', 'f-red'),
    ('directory.html#stay', 'Stay', 'loops', 'f-mist'),
    ('directory.html#services', 'Services', 'dashes', 'f-blue'),
    ('directory.html#social', 'Social District', 'waves', 'f-green'),
    ('directory.html#dollars', 'Takes Downtown Dollars', 'speckle', 'f-pink'),
]

PROGRAMS = [
    ('ambassadors.html', 'Downtown Ambassadors', 'The crew in green and gray who keep downtown clean, bright and easy to find your way around.', 'f-blue', 'dashes'),
    ('waste-recycling.html', 'Waste & recycling', 'Smart Bigbelly bins on downtown sidewalks, and how to keep recycling out of the trash.', 'f-green', 'dots'),
    ('social-district.html', 'Social District', 'Grab a drink from a participating business and take it for a stroll.', 'f-pink', 'waves'),
    ('projects.html', 'Projects', 'New gathering spaces, rebuilt streets, better connections, and a few good things on the way.', 'f-red', 'arcs'),
    ('boards.html', 'DDA & DEGA', 'The boards that invest in downtown, with their budgets, reports and meetings.', 'f-mist', 'stripes'),
    ('history.html', 'History', 'From the Village of Bronson to the nation’s first pedestrian mall.', 'f-blue', 'quilt'),
]
if TEAM_LIVE:
    PROGRAMS.insert(0, ('team.html', 'Our team', 'The City staff who serve the DDA and DEGA, the board, and who to contact for what.', 'f-pink', 'loops'))


def program_card(href, title, text, fill, pat, heading='h3'):
    return (f'<li><a class="program {fill}" href="{{R}}{href}"><span class="program-pat" style="background-image:url({{R}}pattern-{pat}-sm.webp)" aria-hidden="true"></span>'
            f'<span class="program-body"><{heading} class="program-title">{E(title)}</{heading}><span class="program-text">{E(text)}</span></span></a></li>')


def holiday_banner():
    if not HOLIDAY_SEASON:
        return ''
    return f'''<section class="section" style="padding-top:0" aria-labelledby="hol-title">
  <div class="wrap">
    <div class="holiday-feature">
      {snow(14, seed=3)}
      <div class="hf-copy">
        <p class="eyebrow">November 6 – December 31</p>
        <h2 class="display" id="hol-title">Find the Holidays Downtown</h2>
        <p>The traditions you love. A few new ones in the making. Find parades, tree lighting, local gifts, holiday outings, and a little something hidden along the way.</p>
        <div class="btn-row"><a class="btn btn-primary" href="{{R}}holidays/index.html">Explore the holidays</a><a class="btn" href="{{R}}holidays/events.html">Holiday events</a></div>
      </div>
      <div class="hf-quilt" aria-hidden="true">{''.join(f'<span style="background-image:url({{R}}pattern-{n}-sm.webp)"></span>' for n in ['squiggle', 'confetti', 'speckle', 'dots', 'arcs', 'stripes'])}</div>
    </div>
  </div>
</section>'''


def build_year_home():
    finds = discover_data()
    first = next((b for b in finds if b['n'] == 'Kalamazoo Candle Company'), finds[0])
    data = json.dumps(finds, ensure_ascii=False).replace('</', '<\\/')
    dd = '<span class="dd-badge"><span class="dd-coin" aria-hidden="true">$</span>Accepts Downtown Dollars</span>'
    upcoming = ''.join(cal_row(o, show_tags=False) for o in [o for o in calendar_items() if 'Public meetings' not in o['tags']][:8])
    tiles = ''.join(f'<li><a class="cat-tile {fill}" href="{{R}}{h}"><span class="ct-pat" style="background-image:url({{R}}pattern-{pat}-sm.webp)" aria-hidden="true"></span><span class="ct-name">{E(t)}</span></a></li>'
                    for h, t, pat, fill in CATEGORY_TILES)
    latest = ''.join(news_card(p) for p in NEWS[:3])
    programs = ''.join(program_card(*p) for p in PROGRAMS)
    n_biz = len(directory_page.BIZ)
    body = f'''<section class="hero-weave" aria-labelledby="page-title" id="hero-weave">
  {weave.weave_svg()}
  {snow() if HOLIDAY_SEASON else ''}
  <div class="wrap hero-weave-inner">
    <div class="hero-card">
      <p class="eyebrow">Downtown Kalamazoo</p>
      <h1 class="display" id="page-title">Find it downtown</h1>
      <p class="tagline">A little different. A lot to love.</p>
      <p class="lede">Locally owned shops, good food, creative people, and a few surprises. All within a few walkable blocks.</p>
      <form class="hero-search" action="{{R}}directory.html" method="get" role="search" aria-label="Search the business directory">
        <label for="home-q">Find a business</label>
        <div class="hs-row"><input type="search" id="home-q" name="q" placeholder="Coffee, gifts, pizza, a name…" autocomplete="off"><button class="btn btn-primary" type="submit">Search</button></div>
      </form>
    </div>
  </div>
  <button class="weave-toggle" type="button" id="weave-toggle">Pause motion</button>
</section>

<section class="section" aria-labelledby="cats-title">
  <div class="wrap">
    <div class="section-head"><div><p class="eyebrow">Explore downtown</p><h2 class="h2" id="cats-title">{n_biz} places, a few blocks apart</h2></div>
      <a class="btn" href="{{R}}directory.html">See the whole directory</a></div>
    {in_short('Choose a kind of place to see those businesses in the directory.')}
    <ul class="cat-tiles">{tiles}</ul>
  </div>
</section>

{holiday_banner()}

<section class="section band" aria-labelledby="discover-title">
  <div class="wrap discover">
    <div class="prose">
      <p class="eyebrow">Find something local</p>
      <h2 class="h2" id="discover-title">Around every corner</h2>
      <p>A candle you pour yourself. A toy store full of things you forgot you loved. A glass studio tucked inside an old factory. Downtown has a way of surprising you. Turn the corner and see what turns up.</p>
      <div class="btn-row"><button class="btn btn-primary" type="button" id="discover-next">Turn the corner</button><a class="btn" href="{{R}}directory.html">See all {n_biz} businesses</a></div>
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

<section class="section" aria-labelledby="upcoming-title">
  <div class="wrap">
    <div class="section-head">
      <div><p class="eyebrow">What’s happening</p><h2 class="h2" id="upcoming-title">Something'ss always happening. You might as well be here.</h2></div>
      <a class="btn" href="{{R}}events.html">Full events calendar</a>
    </div>
    {in_short('These are the next few events downtown. Select one to see the details.')}
    <ul class="event-list" id="upcoming">{upcoming}</ul>
  </div>
</section>

<section class="section" style="padding-top:0" aria-labelledby="dd-title">
  <div class="wrap">
    <div class="dd-band">
      <div>
        <p class="eyebrow" style="color:var(--ink)">The gift that stays downtown</p>
        <h2 id="dd-title">Downtown Dollars</h2>
        <p>Digital gift certificates in $5, $10 and $20 amounts, good at {sum(1 for b in directory_page.BIZ if b['dd'])} downtown businesses and counting.</p>
        <div class="btn-row"><a class="btn btn-primary" href="{{R}}dollars.html">How they work</a><a class="btn" href="{{R}}directory.html#dollars">Where to spend them</a></div>
      </div>
      <div class="art" style="background-image:url({{R}}pattern-dashes.webp)" aria-hidden="true"></div>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="news-title">
  <div class="wrap">
    <div class="section-head"><div><p class="eyebrow">News &amp; stories</p><h2 class="h2" id="news-title">The latest from downtown</h2></div>
      <a class="btn" href="{{R}}news.html">All news</a></div>
    <ul class="news-list news-cards">{latest}</ul>
  </div>
</section>

<section class="section band" aria-labelledby="programs-title">
  <div class="wrap">
    <div class="section-head"><div><p class="eyebrow">Behind the scenes</p><h2 class="h2" id="programs-title">Who keeps downtown going</h2></div>
      <a class="btn" href="{{R}}about.html">About downtown</a></div>
    <ul class="programs">{programs}</ul>
  </div>
</section>

<section class="section" aria-labelledby="host-title">
  <div class="wrap">
    <div class="host-band">
      <div class="copy">
        <p class="eyebrow" style="color:var(--ink)">For businesses, groups and neighbors</p>
        <h2 id="host-title">Make something happen downtown</h2>
        <p>Got an event, a business, or an idea worth sharing? There's room for that here. Find resources, get involved, or tell us what makes downtown yours.</p>
        <div class="btn-row"><a class="btn btn-primary" href="{{R}}submit-event.html">Submit an event</a><a class="btn" href="{{R}}businesses.html">Business resources</a></div>
        <p style="margin-top:1rem"><a href="{{R}}newsletter.html">Get the downtown newsletter</a> · <a href="{{R}}your-downtown.html">Share your downtown</a></p>
      </div>
      <div class="art" style="background-image:url({{R}}pattern-squiggle.webp)" aria-hidden="true"></div>
    </div>
  </div>
</section>
''' + (welcome_dialog() if HOLIDAY_SEASON else '')
    page('index.html', 'Downtown Kalamazoo', body, None,
         'Downtown Kalamazoo: local shops, restaurants and stages, the business directory, events, Downtown Dollars, news and how downtown works.')


# ---------------------------------------------------------------- Events calendar
def build_calendar():
    items = calendar_items()
    tags = []
    for o in items:
        for t in o['tags']:
            if t not in tags:
                tags.append(t)
    order = ['Holidays', 'Arts', 'Community', 'Family', 'Food & drink', 'Music', 'Public meetings']
    tags.sort(key=lambda t: order.index(t) if t in order else 99)
    chips = (f'<li><button type="button" class="chip" data-tag="all" aria-pressed="true">All events</button></li>' +
             ''.join(f'<li><button type="button" class="chip" data-tag="{E(t)}" aria-pressed="false">{E(t)}</button></li>' for t in tags))
    months, groups = [], {}
    for o in items:
        k = o['date'][:7]
        if k not in groups:
            groups[k] = []; months.append(k)
        groups[k].append(o)
    sections = ''
    for k in months:
        y, m = int(k[:4]), int(k[5:])
        n = len(groups[k])
        sections += (f'<section class="cal-month" aria-labelledby="m-{k}"><div class="month-head"><h2 class="h2" id="m-{k}">{MONTH_NAMES[m]} {y}</h2>'
                     f'<span class="muted cal-count">{n} event{"s" if n != 1 else ""}</span></div>'
                     f'<ul class="event-list">{"".join(cal_row(o) for o in groups[k])}</ul></section>')
    body = page_hero([('index.html', 'Home'), ('events.html', 'Events')], 'What’s happening', 'Events downtown',
                     'Art Hops, holiday traditions, festivals and public meetings. Everything happening downtown, in one place.', 'f-red',
                     '<div class="btn-row" style="margin-top:1.25rem"><a class="btn btn-primary" href="{R}submit-event.html">Submit an event</a></div>')
    body += f'''<section class="section calendar" aria-label="Events calendar">
  <div class="wrap">
    {in_short('Events are listed by date, starting today. Use the buttons to show one kind of event.')}
    <div class="cal-tools"><span class="label" id="cal-filter-label">Show</span><ul class="chips" id="cal-tags" role="list" aria-labelledby="cal-filter-label">{chips}</ul></div>
    <p class="sr-only" id="cal-status" role="status" aria-live="polite"></p>
    {sections}
    <p class="note" id="cal-empty" hidden>No events of this kind are on the calendar yet.</p>
    <div class="two-col" style="margin-top:2.5rem">
      <section class="panel f-pink"><h2>Hosting something downtown?</h2><p>Groups, venues and businesses can send an event for the calendar. Every event is reviewed before it’s posted. <a href="{{R}}submit-event.html">Submit an event</a></p></section>
      <section class="panel"><h2>Details can change</h2><p>Events are confirmed with organizers, but times and places sometimes change. Check the organizer’s link before you go, and see <a href="{{R}}visit.html">Visit &amp; park</a> for getting here.</p></section>
    </div>
  </div>
</section>'''
    page('events.html', 'Events', body, 'events', 'The Downtown Kalamazoo events calendar: Art Hop, holiday events, festivals and public meetings.')


def build_cal_event_pages():
    for ev in CAL_EVENTS:
        if not ev.get('body_html'):
            continue
        dates = CL.occurrences(ev, TODAY)
        if ev.get('repeats'):
            when = 'The ' + ev['repeats'].lower() + ' of every month'
        else:
            d = dates[0][0] if dates else None
            when = long_date(d) if d else ''
        glance = [('When', E(when)), ('Time', E(ev.get('time', ''))), ('Where', E(ev.get('where', '')))]
        if ev.get('link'):
            glance.append(('More', ext(ev['link'], E(ev.get('link_text') or 'Event website'))))
        gl = ''.join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in glance if v)
        upcoming = ''
        if ev.get('repeats') and dates:
            upcoming = '<section class="panel"><h2>Coming dates</h2><ul>' + ''.join(
                f'<li><time datetime="{d.isoformat()}">{DAY_NAMES[d.weekday()]}, {MONTH_NAMES[d.month]} {d.day}</time></li>' for d, _ in dates[:6]) + '</ul></section>'
        body = page_hero([('index.html', 'Home'), ('events.html', 'Events'), (f'events/{ev["slug"]}.html', ev['title'])],
                         E(', '.join(ev['tags']) or 'Event'), E(ev['title']), E(ev.get('summary', '')), ev.get('fill', 'f-green'))
        body += f'''<section class="section" aria-labelledby="glance-title"><div class="wrap"><h2 class="sr-only" id="glance-title">At a glance</h2><dl class="glance">{gl}</dl></div></section>
<section class="section" style="padding-top:0" aria-label="About this event">
  <div class="wrap two-col">
    <div class="prose">{ev['body_html']}</div>
    <div class="aside">{upcoming}<section class="panel"><h2>Getting here</h2><p><a href="{{R}}visit.html">Parking and getting around</a> · <a href="{{R}}access-guide.html">Accessible downtown</a></p></section></div>
  </div>
</section>
<section class="section-tight"><div class="wrap"><p><a href="{{R}}events.html">← All events</a></p></div></section>'''
        page(f'events/{ev["slug"]}.html', ev['title'], body, 'events', ev.get('summary', ''))


# ---------------------------------------------------------------- News
def build_news():
    types = [t for t in CL.NEWS_TYPES if any(p['type'] == t for p in NEWS)]
    plural = {'Press release': 'Press releases', 'News': 'News', 'Feature': 'Features', 'In the news': 'In the news'}
    chips = (f'<li><button type="button" class="chip" data-type="all" aria-pressed="true">Everything</button></li>' +
             ''.join(f'<li><button type="button" class="chip" data-type="{E(t)}" aria-pressed="false">{E(plural[t])}</button></li>' for t in types))
    body = page_hero([('index.html', 'Home'), ('news.html', 'News')], 'News &amp; media', 'News &amp; stories',
                     'Press releases, updates and stories about downtown Kalamazoo and the people who make it what it is.', 'f-blue')
    body += f'''<section class="section" aria-labelledby="news-list-title">
  <div class="wrap two-col">
    <div>
      {in_short('The newest stories are first. Use the buttons to show only press releases, news, features, or stories about downtown from other outlets.')}
      <h2 class="sr-only" id="news-list-title">All stories</h2>
      <div class="cal-tools"><span class="label" id="news-filter-label">Show</span><ul class="chips" id="news-types" role="list" aria-labelledby="news-filter-label">{chips}</ul></div>
      <p class="sr-only" id="news-status" role="status" aria-live="polite"></p>
      <ul class="news-list" id="news-list">{''.join(news_card(p, 'h3') for p in NEWS)}</ul>
    </div>
    <div class="aside">
      <section class="panel f-blue" aria-labelledby="media-title"><h2 id="media-title">For media</h2>
        <p>For interviews, photos or information about downtown Kalamazoo, contact the City of Kalamazoo’s downtown team.</p>
        <p>Email <span>{DOWNTOWN_EMAIL}</span> <button type="button" class="btn btn-small btn-quiet" data-copy="{DOWNTOWN_EMAIL}">Copy address</button><br>Call {DOWNTOWN_PHONE}</p></section>
      <section class="panel" aria-labelledby="logo-title"><h2 id="logo-title">Logos</h2>
        <p>The Downtown Kalamazoo logo for news stories and event listings.</p>
        <ul><li><a href="{{R}}dk-logo-green.png" download>Green K logo<span class="sr-only"> (PNG)</span></a> <span class="muted">PNG</span></li>
        <li><a href="{{R}}logo-reverse.png" download>White K logo, for dark or patterned backgrounds<span class="sr-only"> (PNG)</span></a> <span class="muted">PNG</span></li></ul>
        <p class="muted" style="font-size:.9rem">Keep the K and the words DOWNTOWN KALAMAZOO together and readable. For brand guidelines, email {DOWNTOWN_EMAIL}.</p></section>
      <section class="panel f-pink"><h2>Have a downtown story?</h2><p>A new business, a milestone, a neighbor worth knowing. <a href="{{R}}your-downtown.html">Tell us</a>, or email {DOWNTOWN_EMAIL}.</p></section>
      <section class="panel"><h2>Never miss a story</h2><p><a href="{{R}}newsletter.html">Get the downtown newsletter</a>.</p></section>
    </div>
  </div>
</section>'''
    page('news.html', 'News & stories', body, 'news', 'Press releases, news and stories from downtown Kalamazoo.')
    for i, p in enumerate(NEWS):
        if p['type'] == 'In the news' and not p['body_html']:
            continue
        build_news_post(p)


def build_news_post(p):
    fig = ''
    if p.get('image'):
        fig = f'<figure class="news-figure"><img src="{{R}}{E(p["image"])}" alt="{E(p.get("image_alt", ""))}" loading="lazy"></figure>'
    src = ''
    if p.get('source_url'):
        label = 'Read the original release' if p['type'] == 'Press release' else 'Read the original story'
        src = f'<p class="news-orig">{ext(p["source_url"], label)}{f" from {E(p.get("source"))}" if p.get("source") else ""}.</p>'
    more = [q for q in NEWS if q is not p][:3]
    by = f'<span>By {E(p["author"])}</span>' if p.get('author') else ''
    meta = (f'<p class="news-meta"><span class="type-tag t-{re.sub(r"[^a-z]+", "-", p["type"].lower())}">{E(p["type"])}</span>'
            f'<time datetime="{p["date"]}">{long_date(p["date"])}</time>{by}</p>')
    body = page_hero([('index.html', 'Home'), ('news.html', 'News'), (f'news/{p["slug"]}.html', p['title'])],
                     E(p['type']), E(p['title']), E(p.get('summary', '')), 'f-blue', meta)
    body += f'''<section class="section" aria-label="Story">
  <div class="wrap two-col">
    <article class="prose news-body">
      {fig}
      {p['body_html']}
      {src}
      <p class="share-row"><button class="btn btn-small" type="button" data-share>Share this story</button> <span class="muted" data-share-status role="status"></span></p>
    </article>
    <div class="aside">
      <section class="panel" aria-labelledby="more-title"><h2 id="more-title">More news</h2><ul>{''.join(f'<li><a href="{{R}}news.html">{E(q["title"])}</a></li>' if (q['type'] == 'In the news' and not q['body_html']) else f'<li><a href="{{R}}news/{q["slug"]}.html">{E(q["title"])}</a></li>' for q in more)}</ul><p><a href="{{R}}news.html">All news &amp; stories</a></p></section>
      <section class="panel f-blue"><h2>For media</h2><p>Email {DOWNTOWN_EMAIL} or call {DOWNTOWN_PHONE}.</p></section>
    </div>
  </div>
</section>'''
    page(f'news/{p["slug"]}.html', p['title'], body, 'news', p.get('summary', ''))


# ---------------------------------------------------------------- History
HISTORY = [
    ('1829', 'Titus Bronson arrives', 'On June 21, 1829, Titus Bronson reached the site that would become Kalamazoo, the first white settler to make his home here.', 'kpl-bronson'),
    ('1831', 'The Village of Bronson', 'Bronson and his brother-in-law Stephen Richardson filed the plat for the Village of Bronson on March 12, 1831. They donated land at the center of town to the county, hoping to win the county seat. Part of it became Bronson Park.', 'kpl-park'),
    ('1836', 'Bronson becomes Kalamazoo', 'In March 1836, after a falling-out between Bronson and his neighbors, the village was renamed Kalamazoo.', 'kpl-bronson'),
    ('1856', 'Lincoln in Bronson Park', 'Abraham Lincoln, then a lawyer from Illinois, spoke at a political rally in the park.', 'kpl-park'),
    ('1873', 'A creek goes underground', 'To deal with flooding, the village and then the city began about two decades of work burying Arcadia Creek beneath downtown. By around 1930 it ran through concrete culverts.', 'kpl-arcadia'),
    ('1899', 'Bronson Park gets its name', 'A city ordinance in February 1899 officially named the town square Bronson Park.', 'kpl-park'),
    ('1927', 'The State Theatre opens', 'Chicago architect John Eberson’s “atmospheric” movie palace opened at South Burdick and Lovell streets in July 1927, with seats for up to 1,300 people.', 'kpl-state'),
    ('1940s', 'Curb cuts, made in Kalamazoo', 'Kalamazoo installed curb cuts as a pilot project, introduced by veteran and lawyer Jack H. Fischer to help veterans with disabilities get to work.', None),
    ('1959', 'The nation’s first pedestrian mall', 'On August 19, 1959, two blocks of South Burdick Street closed to cars and opened as the Kalamazoo Mall. About 50,000 people came the first day. Blocks were added in 1960 and 1975.', 'kpl-mall'),
    ('1962', 'The holiday parade begins', 'Gilmore Department Store started Kalamazoo’s holiday parade in 1962. Today it draws close to 30,000 people to the curb.', None),
    ('1990s', 'Arcadia Creek sees daylight', 'From the late 1980s into the early 1990s, redevelopment uncovered parts of Arcadia Creek and created the pond and festival site that host downtown’s summer festivals.', 'kpl-arcadia'),
    ('1998', 'One street, a few cars', 'On October 9, 1998, a narrow access street reopened through two blocks of the Kalamazoo Mall, with a raffle to choose the first driver since 1959.', 'kpl-mall'),
    ('1999', 'A band shell for the park', 'The Bronson Park band shell was built, a stage for the concerts and celebrations that still fill the park.', 'kpl-park'),
    ('2018', 'The DEGA is created', 'The City Commission created the Downtown Economic Growth Authority in October 2018 to invest in downtown’s commercial corridors.', 'city-boards'),
    ('2020', 'The Social District', 'On August 3, 2020, the City Commission approved a downtown Social District, so people could carry a drink from a participating business along the Mall and Michigan Avenue.', 'swm-sd'),
    ('2021', 'Ambassadors and a landmark', 'The Downtown Ambassador program launched in May. Later that year the State Theatre was added to the National Register of Historic Places.', 'wmu-amb'),
    ('2026', 'Something new downtown', 'A new Downtown Kalamazoo brand arrived, built on what people said they love: creative, welcoming, rooted. Construction was approved for new downtown plazas, and work began on rebuilding Kalamazoo Avenue.', 'city-place'),
]
HISTORY_SOURCES = {
    'kpl-bronson': ('Kalamazoo Public Library: Titus Bronson (1788–1853)', 'https://www.kpl.gov/local-history/kalamazoo-history/biographies/bronson-titus/'),
    'kpl-park': ('Kalamazoo Public Library: Bronson Park', 'https://www.kpl.gov/local-history/kalamazoo-history/parks/bronson-park/'),
    'kpl-arcadia': ('Kalamazoo Public Library: Arcadia Creek', 'https://www.kpl.gov/local-history/kalamazoo-history/general/arcadia-creek/'),
    'kpl-state': ('Kalamazoo Public Library: The State Theatre', 'https://www.kpl.gov/local-history/kalamazoo-history/arts-entertainment/state-theatre/'),
    'kpl-mall': ('Kalamazoo Public Library: From Wheels to Heels, the Mall City', 'https://www.kpl.gov/local-history/kalamazoo-history/business/kalamazoo-mall/'),
    'city-boards': ('City of Kalamazoo: DDA & DEGA', BOARDS_URL),
    'swm-sd': ('Second Wave Media: Kalamazoo’s Social District (August 2020)', 'https://www.secondwavemedia.com/southwest-michigan/features/Kalamazoo-s-Social-District-gives-restaurant-tavern-customers-a-chance-to-be-outdoors-082120.aspx'),
    'wmu-amb': ('WMU News: Downtown Kalamazoo Ambassador Program launches (May 2021)', 'https://wmich.edu/bulletins/64347'),
    'city-place': ('City of Kalamazoo: Downtown Kalamazoo Placemaking', CITY + '/Community/Projects/2025/Downtown-Kalamazoo-Placemaking'),
}


def build_history():
    pats = ['quilt', 'squiggle', 'dots', 'arcs', 'confetti', 'maze', 'speckle', 'stripes', 'dashes', 'waves', 'loops', 'pinstripes']
    items = ''.join(
        f'<li class="tl-item"><span class="tl-year" style="background-image:url({{R}}pattern-{pats[i % len(pats)]}-sm.webp)"><span>{E(y)}</span></span>'
        f'<div class="tl-body"><h3 class="h3">{E(t)}</h3><p>{E(x)}</p></div></li>' for i, (y, t, x, _) in enumerate(HISTORY))
    used = []
    for *_, k in HISTORY:
        if k and HISTORY_SOURCES[k] not in used:
            used.append(HISTORY_SOURCES[k])
    feature = next((p for p in NEWS if p['type'] == 'Feature'), None)
    body = page_hero([('index.html', 'Home'), ('about.html', 'About'), ('history.html', 'History')], 'Since 1829', 'A history of downtown',
                     'A village named Bronson, a creek that went underground and came back, and the first street in the nation built just for people on foot.', 'f-mist')
    body += f'''<section class="section" aria-labelledby="tl-title">
  <div class="wrap two-col">
    <div>
      {in_short('These are some important moments in the history of downtown Kalamazoo, from 1829 to today, in order.')}
      <h2 class="h2" id="tl-title" style="margin-bottom:1.25rem">Moments that made downtown</h2>
      <ol class="timeline-hist">{items}</ol>
      {sources_list(used)}
    </div>
    <div class="aside">
      {f'<section class="panel f-blue"><h2>Read the story</h2><p><a href="{{R}}news/{feature["slug"]}.html">{E(feature["title"])}</a></p></section>' if feature else ''}
      <section class="panel"><h2>Dig deeper</h2><p>The Kalamazoo Public Library’s local history room has photos, maps and stories about nearly every downtown block.</p><p>{ext('https://www.kpl.gov/local-history/', 'Kalamazoo Public Library local history')}</p></section>
      <section class="panel f-pink"><h2>Your downtown memory</h2><p>Remember a store, a parade or a first date downtown? <a href="{{R}}your-downtown.html">Tell us about it</a>.</p></section>
    </div>
  </div>
</section>'''
    page('history.html', 'A history of downtown', body, None, 'The history of downtown Kalamazoo, from the Village of Bronson in 1829 to the Kalamazoo Mall and today.')


# ---------------------------------------------------------------- DDA & DEGA
# The board list lives in content/team.yml, shared with the Our team page.
TEAM = CL.team()
BOARD = [(m['name'], m['role']) for m in TEAM['members']]


def build_boards():
    docs = CL.documents()
    meet = next((ev for ev in CAL_EVENTS if ev['slug'] == 'dda-dega-board-meeting'), None)
    next_dates = [d for d, _ in CL.occurrences(meet, TODAY)][:3] if meet else []
    rows = ''.join(f'<tr><th scope="row">{E(n)}</th><td>{E(r_)}</td></tr>' for n, r_ in BOARD)
    def doc_row(d):
        href = d['url'] if d['url'].startswith('http') else '{R}' + d['url']
        link = ext(href, E(d['title'])) if href.startswith('http') else f'<a href="{href}">{E(d["title"])}</a>'
        return f'<tr data-board="{E(d["board"])}"><th scope="row">{link}</th><td>{E(d["board"])}</td><td>{E(d.get("kind", ""))}</td><td class="num">{E(d["year"])}</td></tr>'
    docs_sorted = sorted(docs, key=lambda d: (d['year'] or '0000'), reverse=True)
    doc_rows = ''.join(doc_row(d) for d in docs_sorted)
    nd = ''.join(f'<li><time datetime="{d.isoformat()}">{DAY_NAMES[d.weekday()]}, {MONTH_NAMES[d.month]} {d.day}</time>, 3–5 p.m.</li>' for d in next_dates)
    body = page_hero([('index.html', 'Home'), ('about.html', 'About'), ('boards.html', 'DDA & DEGA')], 'Downtown governance', 'DDA &amp; DEGA',
                     'Two public authorities invest in downtown Kalamazoo: the Downtown Development Authority and the Downtown Economic Growth Authority. Here’s what they do, who serves, and where the money goes.', 'f-mist')
    body += f'''<section class="section" aria-labelledby="what-title">
  <div class="wrap two-col">
    <div class="prose" style="max-width:none">
      {in_short('The DDA and DEGA are public boards that use downtown tax revenue to improve downtown. They share one board, meet in public every month, and post their budgets and reports.')}
      <h2 class="h2" id="what-title">What they do</h2>
      <div class="pair">
        <section class="panel f-blue"><h3 class="h3">Downtown Development Authority (DDA)</h3><p>A special-purpose local authority created to halt deterioration and foster development in the downtown business area. It’s funded by a tax increment financing (TIF) district and a 2-mill tax levy in the Downtown Development District.</p></section>
        <section class="panel f-green"><h3 class="h3">Downtown Economic Growth Authority (DEGA)</h3><p>Created by the City Commission in October 2018 under Michigan’s Corridor Improvement Authority Act, to help fund improvements along downtown’s commercial corridors. It can adopt a development plan and a TIF plan for its district.</p></section>
      </div>
      <p>Their work shows up across downtown: the <a href="{{R}}ambassadors.html">Downtown Ambassadors</a>, the <a href="{{R}}waste-recycling.html">Bigbelly waste and recycling units</a>, <a href="{{R}}social-district.html">Social District</a> signs and seating, event sponsorships and <a href="{{R}}projects.html">downtown projects</a>.</p>

      <h2 class="h2" id="money-title" style="margin-top:2rem">Budgets &amp; reports</h2>
      <p>Each authority’s budget is approved by the City Commission. After 2023, the DDA and DEGA stopped issuing separate audited financial statements; their audited figures are now part of the City of Kalamazoo’s financial statements.</p>
      <div class="doc-tools"><span class="label" id="doc-filter-label">Show</span><span class="segmented" role="group" aria-labelledby="doc-filter-label" id="doc-filter"><button type="button" data-board="all" aria-pressed="true">Both</button><button type="button" data-board="DDA" aria-pressed="false">DDA</button><button type="button" data-board="DEGA" aria-pressed="false">DEGA</button></span></div>
      <div class="table-wrap"><table class="docs" id="docs-table"><caption>Budgets, reports and governing documents</caption>
        <thead><tr><th scope="col">Document</th><th scope="col">Board</th><th scope="col">Type</th><th scope="col" class="num">Year</th></tr></thead>
        <tbody>{doc_rows}</tbody></table></div>
      <p class="muted">More financial reports are on the {ext(CITY + '/Government/Budgets-and-Financial-Reports', 'City of Kalamazoo’s budgets and financial reports page')}. Plans, presentations and data behind downtown marketing are in the {ext(LIBRARY_URL, 'downtown plan library')}.</p>

      <h2 class="h2" id="board-title" style="margin-top:2rem">The board</h2>
      <p>One board of nine members serves both authorities. A majority must have an interest in property in the downtown district, at least one must live in the district, and the mayor serves ex officio. Terms are four years, with a limit of two in a row.</p>
      <div class="table-wrap"><table><caption>DDA and DEGA board members{(", " + E(TEAM["board_as_of"])) if TEAM["board_as_of"] else ""}</caption><thead><tr><th scope="col">Name</th><th scope="col">Role</th></tr></thead><tbody>{rows}</tbody></table></div>
      <p class="muted">A City of Kalamazoo downtown coordinator serves as staff liaison to the board.</p>

      <h2 class="h2" id="spon-title" style="margin-top:2rem">Event &amp; marketing sponsorships</h2>
      <p>The DDA/DEGA Events and Marketing Committee considers sponsorship requests for downtown events: up to <strong>$2,500</strong> for a single-day or partial event, and up to <strong>$5,000</strong> for a multi-day event.</p>
      <p>{ext(BOARDS_URL + '/Apply-for-a-DDADEGA-Events-Marketing-Sponsorship', 'Apply for an events and marketing sponsorship')}</p>
      {sources_list([('City of Kalamazoo: DDA & DEGA', BOARDS_URL), ('City of Kalamazoo: DEGA financial reports', CITY + '/Government/Budgets-and-Financial-Reports/DEGA'), ('City of Kalamazoo: DDA financial reports', CITY + '/Government/Budgets-and-Financial-Reports/DDA'), ('WMUK: Kalamazoo approves new downtown growth authority (2018)', 'https://www.wmuk.org/wmuk-news/2018-10-16/kalamazoo-approves-new-downtown-growth-authority')])}
    </div>
    <div class="aside">
      <section class="panel f-mist" aria-labelledby="meet-title"><h2 id="meet-title">Meetings</h2>
        <p>Third Monday of the month, 3 to 5 p.m., at City Hall, 241 W. South St., unless noted. Meetings are open to the public.</p>
        {f'<ul>{nd}</ul>' if nd else ''}
        <ul><li>{ext(CITY + '/Government/Boards-Commissions/Minutes-Agendas', 'Agendas and minutes')}</li><li>{ext(CITY + '/Government/Boards-Commissions/Meeting-Calendar', 'City meeting calendar')}</li></ul></section>
      <section class="panel"><h2>Join the board</h2><p>Board members are appointed. Anyone interested can apply through the City.</p><p>{ext(CITY + '/Government/Boards-Commissions/Apply-to-Join-a-Board-or-Commission', 'Apply to join a board')}</p></section>
      <section class="panel"><h2>Bylaws</h2><ul>{''.join(f'<li>{ext(d["url"], E(d["title"]) + " (PDF)")}</li>' for d in docs if d.get('kind') == 'Bylaws')}</ul></section>
      <section class="panel f-pink"><h2>Questions</h2><p>Email {DOWNTOWN_EMAIL} or call {DOWNTOWN_PHONE}.</p></section>
    </div>
  </div>
</section>'''
    page('boards.html', 'DDA & DEGA', body, None, 'The Downtown Development Authority and Downtown Economic Growth Authority: board, meetings, budgets and reports.')


# ---------------------------------------------------------------- Ambassadors
AMB_PATTERNS = ['dots', 'squiggle', 'confetti', 'loops', 'waves', 'arcs', 'quilt', 'dashes']
AMB_FILLS = ['f-blue', 'f-pink', 'f-green', 'f-red', 'f-mist']


def _initials(name):
    parts = [p for p in re.split(r'\s+', name.strip()) if p]
    return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else '')).upper()


def _file_size(rel):
    p = os.path.join(HERE, rel)
    if not os.path.exists(p):
        print(f'  ! content/ambassadors.yml points to {rel}, but that file isn’t in the repository.')
        return ''
    b = os.path.getsize(p)
    return f'{b / 1048576:.1f} MB' if b >= 1048576 else f'{max(1, round(b / 1024))} KB'


def amb_card(t, i):
    name = E(str(t['name']).strip())
    fill = AMB_FILLS[i % len(AMB_FILLS)]
    pat = AMB_PATTERNS[i % len(AMB_PATTERNS)]
    photo = (t.get('photo') or '').strip()
    if photo:
        alt = E(str(t.get('photo_alt') or f'{t["name"]} in Downtown Ambassador gear').strip())
        pic = f'<img src="{{R}}{E(photo)}" alt="{alt}" loading="lazy" width="400" height="500">'
    else:
        pic = (f'<div class="amb-ph" style="background-image:url({{R}}pattern-{pat}.webp)" aria-hidden="true">'
               f'<span class="amb-initials">{E(_initials(str(t["name"])))}</span></div>')
    role = f'<p class="amb-role">{E(str(t["role"]).strip())}</p>' if t.get('role') else ''
    since = f'<p class="amb-since">On the team since {E(str(t["since"]))}</p>' if t.get('since') else ''
    note = f'<p class="amb-note">{E(str(t["note"]).strip())}</p>' if t.get('note') else ''
    return (f'<li class="amb {fill}" style="--amb-pat:url({{R}}pattern-{pat}.webp)"><figure class="amb-pic">{pic}</figure>'
            f'<div class="amb-body"><h3 class="amb-name">{name}</h3>{role}{since}{note}</div></li>')


def _tel(phone):
    digits = re.sub(r'\D', '', phone)
    return '+1' + digits if len(digits) == 10 else '+' + digits


def amb_hours(info, cls='amb-hours'):
    if not info['hours']:
        return ''
    rows = ''.join(f'<div><dt>{E(str(h["days"]))}</dt><dd>{E(str(h["time"]))}</dd></div>' for h in info['hours'])
    return f'<dl class="{cls}">{rows}</dl>'


PHONE_ICON = ('<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" '
              'd="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg>')

RIBBON_DOTS = ['f-blue', 'f-pink', 'f-green', 'f-red']
LINE_FILLS = ['f-blue', 'f-pink', 'f-green', 'f-red']


def amb_line_card(t, i):
    name = E(str(t['name']).strip())
    alt = E(str(t.get('photo_alt') or f'{t["name"]} in Downtown Ambassador gear').strip())
    role = f'<p class="amb-role">{E(str(t["role"]).strip())}</p>' if t.get('role') else ''
    fill = LINE_FILLS[i % len(LINE_FILLS)]
    return (f'<li class="amb-person {fill}"><img src="{{R}}{E(t["photo"].strip())}" alt="{alt}" loading="lazy" width="640" height="800">'
            f'<div class="amb-person-body"><h3 class="amb-name">{name}</h3>{role}</div></li>')


def _and(names):
    return names[0] if len(names) == 1 else ', '.join(names[:-1]) + ' and ' + names[-1]


def build_ambassadors():
    team, reports = CL.ambassadors()
    info = CL.ambassador_info()
    phone = info['phone']

    # Hero: group photo, phone and hours
    duty = ''
    if phone or info['hours']:
        call = f'<a class="btn btn-primary amb-call" href="tel:{_tel(phone)}">{PHONE_ICON}Call {E(phone)}</a>' if phone else ''
        hours = f'<div class="amb-duty-hours"><p class="amb-duty-k">On duty downtown</p>{amb_hours(info)}</div>' if info['hours'] else ''
        duty = f'<div class="amb-duty"><h2 class="sr-only">Hours and phone</h2>{call}{hours}</div>'
    body = page_hero([('index.html', 'Home'), ('about.html', 'About'), ('ambassadors.html', 'Downtown Ambassadors')],
                     'Clean, friendly, here to help', 'Downtown Ambassadors',
                     'Look for the green Downtown Kalamazoo shirts and caps. Downtown Ambassadors are on the streets seven days a week, keeping downtown clean and helping people find their way.',
                     'f-blue', extra=duty, photo=(info['photo'], info['photo_alt']))

    # Stats ribbon, right under the hero
    if reports:
        yr = reports[0]['year']
        ytd = sorted([r for r in reports if r['year'] == yr], key=lambda r: r['mon'])
        tot = {k: sum(r[k] for r in ytd) for k in CL.AMB_STATS}
        lbs = tot['trash'] + tot['recycling'] + tot['litter']
        span = MONTH_NAMES[ytd[0]['mon']][:3] + (f'–{MONTH_NAMES[ytd[-1]["mon"]][:3]}' if len(ytd) > 1 else '')
        stats = [(f'{lbs:,}', 'pounds of trash, recycling and litter'),
                 (f'{round(lbs / 2000):,}', 'tons kept off downtown sidewalks'),
                 (f'{tot["assists"]:,}', 'times they helped someone find their way'),
                 (f'{tot["graffiti"]:,}', 'pieces of graffiti and hand bills removed')]
        if tot['snow_hours']:
            stats.append((f'{tot["snow_hours"]:,}', 'hours shoveling snow'))
        if tot['flower_gallons']:
            stats.append((f'{tot["flower_gallons"]:,}', 'gallons of water for downtown flowers'))
        if tot['project_hours']:
            stats.append((f'{tot["project_hours"]:,}', 'hours on special projects and events'))
        items = ''.join(f'<li class="{RIBBON_DOTS[i % len(RIBBON_DOTS)]}"><span class="n">{n}</span> {E(t)}</li>' for i, (n, t) in enumerate(stats))
        body += f'''<section class="amb-ribbon" aria-labelledby="ytd-title">
  <h2 class="amb-ribbon-k" id="ytd-title"><span>{yr} so far</span><span class="amb-ribbon-span">{span}</span></h2>
  <div class="amb-ribbon-view" tabindex="0" role="region" aria-label="{yr} numbers, scrollable">
    <div class="amb-ribbon-track">
      <ul class="amb-ribbon-list">{items}</ul>
      <ul class="amb-ribbon-list amb-ribbon-dup" aria-hidden="true">{items}</ul>
    </div>
  </div>
  <button class="amb-ribbon-btn" type="button" data-ribbon-toggle aria-label="Pause the scrolling numbers">Pause</button>
</section>'''

    # What they do, plus how to reach them | About the program
    reach = f'call the ambassadors at <a href="tel:{_tel(phone)}">{E(phone)}</a> while they’re on duty' if phone else 'call 311'
    left = in_short('Downtown Ambassadors clean sidewalks, empty trash and recycling, clear snow and graffiti, water the flowers and help visitors find their way. They work downtown seven days a week and post a report every month.')
    left += f'''
      <h2 class="h2" id="do-title">What ambassadors do</h2>
      <ul class="amb-do">
        <li class="f-blue"><h3>Keep it clean</h3><p>Sweeping sidewalks, picking up litter, clearing leaves and weeds, and removing graffiti and hand bills.</p></li>
        <li class="f-pink"><h3>Clear the way</h3><p>Shoveling snow so sidewalks and crossings stay open in winter.</p></li>
        <li class="f-green"><h3>Lend a hand</h3><p>Directions, places to shop and eat, and what’s happening downtown today.</p></li>
        <li class="f-red"><h3>Empty the Bigbellys</h3><p>The smart bins tell ambassadors when they’re full, so they get emptied before they overflow.</p></li>
        <li class="f-green"><h3>Keep it blooming</h3><p>Watering planters and hanging baskets, and setting out tables and chairs when the weather turns.</p></li>
        <li class="f-blue"><h3>Get ready for events</h3><p>Prepping the Kalamazoo Mall and Arcadia Creek Festival Place before festivals, and cleaning up after.</p></li>
      </ul>
      <section class="panel f-blue amb-contact" aria-labelledby="help-title"><h2 id="help-title">Need something cleaned up?</h2>
        <p>Overflowing trash, graffiti or a sidewalk that needs attention? {reach[0].upper() + reach[1:]}. After hours, email {DOWNTOWN_EMAIL} or call 311.</p></section>'''

    srcs = ''.join(f'<li>{ext(h, E(t))}</li>' for t, h in [
        ('City of Kalamazoo: Downtown Kalamazoo', CITY + '/Community/Downtown-Kalamazoo'),
        ('WMU News: Downtown Kalamazoo Ambassador Program launches (May 2021)', 'https://wmich.edu/bulletins/64347'),
        ('Block by Block: Downtown Ambassadors hit the streets in Kalamazoo', 'https://blockbyblock.com/?p=1547'),
        ('WMUK: smart recycling units and the ambassadors (2025)', 'https://www.wmuk.org/wmuk-news/2025-08-01/the-city-of-kalamazoo-will-replace-old-trash-cans-downtown-with-more-smart-recycling-units')])
    right = f'''<section class="amb-about" aria-labelledby="about-title">
        <p class="eyebrow">Since 2021</p>
        <h2 class="h2" id="about-title">About the program</h2>
        <p>The program launched in May 2021 with five full-time ambassadors, working on foot, on bikes and in marked cars. In their first two days they picked up 4,731 pounds of trash, cleared weeds on 36 blocks, removed 101 pieces of graffiti and introduced themselves to 33 downtown businesses.</p>
        <p>The jobs were designed as a workforce program with room to grow, so ambassadors build skills and can move up.</p>
        <h3 class="h3">Four zones</h3>
        <p>The team covers the <strong>Kalamazoo Mall</strong>, <strong>North</strong>, <strong>East</strong> and <strong>West</strong>. Each monthly report breaks the numbers down by zone.</p>
        <h3 class="h3">Neighbors who need help</h3>
        <p>Ambassadors aren’t outreach workers, but they’re trained to treat people experiencing homelessness with respect, share the services that are available, and call on Public Safety’s Community Service Team when someone needs more help.</p>
        <details class="amb-src"><summary>Sources</summary><ul class="sources">{srcs}</ul></details>
      </section>'''

    body += f'''<section class="section" aria-labelledby="do-title">
  <div class="wrap two-col amb-cols">
    <div class="amb-main">
      {left}
    </div>
    <div class="amb-aside">
      {right}
    </div>
  </div>
</section>'''

    # The team, in one line
    pictured = [t for t in team if (t.get('photo') or '').strip()]
    coming = [str(t['name']).strip() for t in team if not (t.get('photo') or '').strip()]
    if team:
        line = ''.join(amb_line_card(t, i) for i, t in enumerate(pictured))
        line = f'<div class="amb-line-wrap" role="region" aria-label="Ambassador photos" tabindex="0"><ul class="amb-line">{line}</ul></div>' if line else ''
        also = (f'<p class="amb-also">Also on the team: {E(_and(coming))}. '
                f'{"Photo" if len(coming) == 1 else "Photos"} coming soon.</p>') if coming else ''
        body += f'''<section class="section amb-band amb-team" aria-labelledby="meet-title">
  <div class="wrap">
    <div class="section-head"><div><p class="eyebrow">Say hello</p><h2 class="h2" id="meet-title">Meet the Ambassadors</h2></div>
      <p class="muted" style="max-width:30rem">They’re happy to point you to a good lunch spot or tonight’s show. Just ask.</p></div>
    {line}
    {also}
  </div>
</section>'''

    # Monthly reports, at the very bottom
    listed = [r for r in reports if r['file'] or r['highlights']]
    if listed:
        cards = ''
        for r in listed:
            label = f'{MONTH_NAMES[r["mon"]]} {r["year"]}'
            hl = ''.join(f'<li>{E(h)}</li>' for h in r['highlights'])
            hl = f'<details class="amb-hl"><summary>Highlights<span class="sr-only"> from {label}</span></summary><ul>{hl}</ul></details>' if hl else ''
            if r['file']:
                size = _file_size(r['file'])
                sr = f' (PDF{", " + size if size else ""})'
                meta = f' · {size}' if size else ''
                link = (f'<a class="btn btn-small" href="{{R}}{E(r["file"])}">Read the report<span class="sr-only"> for {label}{sr}</span></a>'
                        f'<span class="meta" aria-hidden="true">PDF{meta}</span>')
            else:
                link = '<span class="meta">Report not posted</span>'
            latest = '<span class="amb-latest">Latest</span>' if r is listed[0] else ''
            cards += (f'<li class="amb-rep"><div class="amb-rep-head"><div class="date-tile f-blue" aria-hidden="true"><span class="day">{MONTH_NAMES[r["mon"]][:3]}</span></div>'
                      f'<h3 class="amb-rep-title">{label}</h3>{latest}</div>'
                      f'<div class="amb-rep-link">{link}</div>{hl}</li>')
        body += f'''<section class="section amb-reports-sec" aria-labelledby="reports-title">
  <div class="wrap">
    <div class="section-head"><div><p class="eyebrow">Every month</p><h2 class="h2" id="reports-title">Monthly reports</h2></div>
      <p class="muted" style="max-width:34rem">Photos from around town, highlights, and each month’s numbers zone by zone. Questions? Email {DOWNTOWN_EMAIL}.</p></div>
    <ol class="amb-rep-grid">{cards}</ol>
  </div>
</section>'''
    page('ambassadors.html', 'Downtown Ambassadors', body, None, 'Downtown Kalamazoo’s ambassadors: hours, phone number, this year’s numbers, the team, and monthly reports.')


# ---------------------------------------------------------------- Waste & recycling
def build_waste():
    body = page_hero([('index.html', 'Home'), ('about.html', 'About'), ('waste-recycling.html', 'Waste & recycling')], 'Bigbelly program', 'Waste &amp; recycling',
                     'Downtown’s smart Bigbelly bins sort trash from recycling and let the ambassadors know when they’re full. Here’s how they work, and how to use them right.', 'f-green')
    body += f'''<section class="section" aria-labelledby="how-title">
  <div class="wrap two-col">
    <div class="prose" style="max-width:none">
      {in_short('Bigbelly bins have two sides: one for trash and one for recycling. Keep food and liquids out of the recycling side. When you are not sure, use the trash side.')}
      <h2 class="h2" id="how-title">How the bins work</h2>
      <ul class="checks f-green">
        <li><strong>Two sides.</strong> Every unit has one bin for trash and one for recycling.</li>
        <li><strong>Smart sensors.</strong> When a bin is full, it sends an alert, and the Downtown Ambassadors empty it.</li>
        <li><strong>Off the sidewalk.</strong> Ambassadors take what they collect to a dumpster site on Farmers Alley for pickup.</li>
      </ul>
      <dl class="glance" style="margin-block:1.5rem">
        <div><dt>Dual units downtown</dt><dd>51</dd></div>
        <div><dt>New units added in 2025</dt><dd>26</dd></div>
        <div><dt>Old cans replaced</dt><dd>58</dd></div>
        <div><dt>Units downtown by December 2021</dt><dd>25</dd></div>
      </dl>
      <h2 class="h2">Recycle right</h2>
      <p>Western Michigan University interns from the Industrial-Organizational Behavior Management program audited the downtown bins and found that <strong>nearly 44% of what went into the recycling side was contamination</strong>, mostly food waste and things that can’t be recycled. A little care makes the whole bin recyclable.</p>
      <ul class="checks f-blue">
        <li>Put food, napkins and anything wet or greasy on the trash side.</li>
        <li>Empty cups and bottles before you recycle them.</li>
        <li>Follow the labels on the unit for what goes where.</li>
        <li>Not sure? Trash it. One wrong item can spoil a whole bin of recycling.</li>
      </ul>
      <h2 class="h2" style="margin-top:2rem">Who makes it happen</h2>
      <p>The City of Kalamazoo runs the program with the Downtown Ambassadors. The 2025 expansion was funded by the <a href="{{R}}boards.html">Downtown Economic Growth Authority (DEGA)</a>, and trash and recycling are hauled by the city’s contractor, Best Way Disposal. Audits will continue, and their results guide the signs on the bins.</p>
      {sources_list([('WMUK: Kalamazoo will replace old trash cans downtown with more smart recycling units (August 2025)', 'https://www.wmuk.org/wmuk-news/2025-08-01/the-city-of-kalamazoo-will-replace-old-trash-cans-downtown-with-more-smart-recycling-units'), ('Waste360: Kalamazoo updates downtown recycling with smart bins and an audit program', 'https://www.waste360.com/waste-recycling/kalamazoo-mi-updates-downtown-recycling-with-smart-bins-audit-program')])}
    </div>
    <div class="aside">
      <section class="panel f-green"><h2>Bin full or broken?</h2><p>Email {DOWNTOWN_EMAIL} or call 311 with the location.</p></section>
      <section class="panel"><h2>Businesses</h2><p>Questions about trash and recycling for your business? Email {DOWNTOWN_EMAIL}.</p></section>
      <section class="panel"><h2>Related</h2><ul><li><a href="{{R}}ambassadors.html">Downtown Ambassadors</a></li><li><a href="{{R}}news/more-smart-recycling-units.html">More smart recycling units coming downtown</a></li></ul></section>
    </div>
  </div>
</section>'''
    page('waste-recycling.html', 'Waste & recycling', body, None, 'Downtown Kalamazoo’s Bigbelly smart trash and recycling program, and how to recycle right.')


# ---------------------------------------------------------------- Social District
def build_social():
    sd = [b for b in directory_page.BIZ if b.get('sd')]
    cards = ''.join(f'<li class="{b["fill"]}"><a href="{{R}}directory.html#b-{b["id"]}"><span class="sd-name">{E(b["name"])}</span><span class="sd-where">{E(b["where"])}</span></a></li>' for b in sd)
    map_pdf = CITY + '/files/assets/public/v/19/social-districts/social-district-map_041526.pdf'
    body = page_hero([('index.html', 'Home'), ('about.html', 'About'), ('social-district.html', 'Social District')], 'Sip and stroll', 'Social District',
                     'Grab a drink from a participating business and take it with you as you shop, stroll and people-watch downtown.', 'f-pink',
                     f'<div class="btn-row" style="margin-top:1.25rem"><a class="btn btn-primary" href="{{R}}directory.html#social">See participating businesses</a>{ext(map_pdf, "Social District map (PDF)", "btn")}</div>')
    body += f'''<section class="section" aria-labelledby="how-title">
  <div class="wrap two-col">
    <div class="prose" style="max-width:none">
      {in_short('Buy a drink at a participating business. It comes in a Social District cup. You can carry it anywhere in the marked area between 10 a.m. and midnight, but not into another bar or restaurant.')}
      <h2 class="h2" id="how-title">How it works</h2>
      <ol class="strip" style="list-style:none">
        <li class="f-pink"><span class="big">1. Order</span><span>Buy a drink at a participating business. It’s served in a designated Social District cup.</span></li>
        <li class="f-green"><span class="big">2. Stroll</span><span>Take it anywhere inside the marked Commons Area, every day from 10 a.m. to midnight.</span></li>
        <li class="f-blue"><span class="big">3. Finish up</span><span>Keep it inside the area, and finish or toss it before you walk into another bar or restaurant.</span></li>
      </ol>
      <h2 class="h2" style="margin-top:2rem">Good to know</h2>
      <ul class="checks f-pink">
        <li>The downtown district is called the Central Commons Refreshment Area. Signs mark its edges.</li>
        <li>Drinks must stay in the designated Social District cup and inside the Commons Area.</li>
        <li>Businesses check IDs, and won’t serve anyone who has had too much.</li>
        <li>Dogs are welcome on a leash. Please pick up after them.</li>
        <li>Use the trash and recycling bins when you’re done.</li>
      </ul>
      <h2 class="h2" id="list-title" style="margin-top:2rem">Participating businesses</h2>
      <p>These {len(sd)} open downtown businesses are on the City of Kalamazoo’s list of Social District licensees (April 2026). Look for the Social District tag in the <a href="{{R}}directory.html#social">directory</a>.</p>
      <ul class="sd-list" aria-labelledby="list-title">{cards}</ul>
      <p class="note">The list can change. Look for Social District signs and cups at the business, or check the city’s map.</p>
      <h2 class="h2" style="margin-top:2rem">A little history</h2>
      <p>Michigan made social districts possible in 2020. Kalamazoo’s City Commission approved the downtown district unanimously on August 3, 2020, as a way to give people more room outdoors. Kalamazoo now has two: the downtown Central Commons and the Northside Cultural Business District.</p>
      {sources_list([('City of Kalamazoo: Central Commons Refreshment Area', CITY + '/Community/Downtown-Kalamazoo/Central-Commons-Refreshment-Area'), ('City of Kalamazoo: Social District map, licensees and maintenance plan (April 2026)', map_pdf), ('City of Kalamazoo: Social Districts', CITY + '/Community/Social-Districts'), ('Second Wave Media: Kalamazoo’s Social District (August 2020)', HISTORY_SOURCES['swm-sd'][1])])}
    </div>
    <div class="aside">
      <section class="panel f-pink"><h2>Hours</h2><p class="big-num">10 a.m. – midnight</p><p>Every day.</p></section>
      <section class="panel"><h2>For businesses</h2><p>Licensed bars and restaurants inside the district can apply for a Social District permit.</p><p>{ext(CITY + '/Community/Downtown-Kalamazoo/Central-Commons-Refreshment-Area/Apply-for-a-Social-District-Permit', 'Apply for a Social District permit')}</p></section>
      <section class="panel"><h2>Questions</h2><p>Email {DOWNTOWN_EMAIL} or call 311.</p></section>
    </div>
  </div>
</section>'''
    page('social-district.html', 'Social District', body, None, 'How the downtown Kalamazoo Social District works, and the businesses that take part.')


# ---------------------------------------------------------------- Projects
# Who leads each project. The keys are what goes in `lead=` below and in `lead:` in the content files.
LEADS = {
    'DEGA': dict(label='Led by the DEGA', group='Led by the Downtown Economic Growth Authority (DEGA)', cls='lead-dega',
                 intro='The DEGA invests in downtown’s commercial corridors with money set aside for downtown, and the DDA and DEGA boards decide these projects at their public monthly meetings.'),
    'DDA': dict(label='Led by the DDA', group='Led by the Downtown Development Authority (DDA)', cls='lead-dda',
                intro='The DDA invests in downtown with money set aside for downtown, and the DDA and DEGA boards decide these projects at their public monthly meetings.'),
    'DDA & DEGA': dict(label='Led by the DDA & DEGA', group='Led by the DDA & DEGA', cls='lead-dega',
                       intro='The DDA and DEGA boards decide these projects together at their public monthly meetings.'),
    'City': dict(label='Led by the City of Kalamazoo', group='Led by the City of Kalamazoo', cls='lead-city',
                 intro='City of Kalamazoo projects and plans that shape downtown, from street rebuilds to parking and the citywide vision.'),
}
LEAD_ORDER = ['DEGA', 'DDA & DEGA', 'DDA', 'City']


def lead_line(lead):
    if lead not in LEADS:
        return ''
    return f'<p class="lead-tag {LEADS[lead]["cls"]}"><span class="lead-mark" aria-hidden="true"></span>{E(LEADS[lead]["label"])}</p>'


PROJECTS = [
    dict(title='Placemaking projects', lead='DEGA', status='Underway', pat='squiggle', fill='f-green',
         text='Turning downtown’s alleys, plazas and streets into places people want to spend time. Four projects are fully or partially funded: Farmers Alley Pocket Park, Rose Street Plaza, Water Street and the South Burdick festival street. Farmers Alley and Rose Street move to construction first.',
         links=[('City of Kalamazoo project page', CITY + '/Community/Projects/2025/Downtown-Kalamazoo-Placemaking')], page='placemaking.html', page_label='See the placemaking projects'),
    dict(title='Downtown Master Pedestrian Wayfinding and Signage', lead='DEGA', status='In planning', pat='loops', fill='f-mist',
         text='A master plan for the signs, maps and markers that help people on foot find their way around downtown: to businesses, parking, parks, trails and events. It’s part of the first phase of the DDA and DEGA’s ten-year plan for downtown, with the master plan scheduled for 2026 and new signs phased in starting in 2027.',
         links=[('WWMT: the DDA and DEGA’s ten-year plan (June 2025)', 'https://wwmt.com/news/local/support-kalamazoo-ten-year-transformation-plan-downtown-development-business-safety-signage-project')]),
    dict(title='Bigbelly expansion', lead='DEGA', status='Complete', pat='dots', fill='f-green',
         text='Twenty-six new smart trash and recycling units replaced 58 old cans in 2025, bringing downtown to 51 dual units, funded by the DEGA.',
         links=[], page='waste-recycling.html'),
    dict(title='Arcadia Creek Festival Place', lead='City', status='Underway', pat='waves', fill='f-blue',
         text='A $3.6 million transformation of downtown’s festival grounds, with a new pedestrian bridge, stages, a playground, water features, a pavilion and amphitheater, and a plaza. The park closed in December 2025 for the work and is expected to reopen in 2027 at the earliest.',
         links=[('WOOD TV 8 coverage (March 2026)', 'https://www.woodtv.com/news/kalamazoo-county/kalamazoo-pride-other-events-still-happening-at-arcadia-creek-amid-renovation/amp')]),
    dict(title='Streets for All: Kalamazoo Avenue', lead='City', status='Underway', pat='dashes', fill='f-red',
         text='Kalamazoo Avenue is being rebuilt from the ground up, starting in July 2026 and moving east one block at a time through 2028: new water and storm lines, buried power lines, new lighting, sidewalks and street trees. Later it will become a two-way street. One lane stays open for most of the work.',
         links=[('Project page and current detours', STREETS_FOR_ALL), ('Construction email updates', 'https://mailchi.mp/kalamazoocity/kalamazoo-ave-streets-for-all')]),
    dict(title='Downtown parking updates', lead='City', status='Complete', pat='maze', fill='f-mist',
         text='New parking zones and rates started April 1, 2026, with the first 90 minutes free in the Epic Center and Kalamazoo Mall ramps. New accessible parking spaces are being added on downtown blocks that didn’t have them, after curb ramp upgrades.',
         links=[('City of Kalamazoo announcement', 'https://www.kalamazoocity.org/News-articles/Downtown-Parking-Updates-Take-Effect-to-Improve-Parking-Access-and-Availability')], news='downtown-parking-updates'),
    dict(title='Imagine Kalamazoo 2035', lead='City', status='Open for comment', pat='quilt', fill='f-mist',
         text='The City’s updated vision for Kalamazoo, which will guide future priorities and investments. A draft was released for public review in September 2026.',
         links=[('Review the draft vision', 'https://www.kalamazoocity.org/News-articles/Review-and-Comment-on-the-Draft-Imagine-Kalamazoo-2035-Vision')]),
]

# Styles for the Projects, Placemaking and Investment pages live here, so this section can be updated without touching site.css.
SECTION_CSS = ('<style>'
    '.lead-tag { margin: 0; display: flex; align-items: center; gap: .45rem; font-family: var(--font-ui); font-weight: 700; font-size: .85rem; }'
    '.lead-mark { width: .95rem; height: .95rem; flex: none; border: 2px solid var(--fg); }'
    '.lead-dega .lead-mark, .lead-dda .lead-mark { background: var(--dk-blue); border-radius: 50%; }'
    '.lead-city .lead-mark { background: var(--dk-red); border-radius: 3px; }'
    '.lead-group + .lead-group { margin-top: 3rem; }'
    '.lead-group > h2 { display: flex; align-items: center; gap: .6rem; }'
    '.lead-group > h2 .lead-mark { width: 1.3rem; height: 1.3rem; }'
    '.lead-intro { max-width: 46rem; margin: .4rem 0 1.2rem; }'
    '.lead-key { display: flex; flex-wrap: wrap; gap: .5rem 1.5rem; margin: 0 0 2rem; padding: 0; list-style: none; }'
    '.place-tags { display: flex; flex-wrap: wrap; gap: .4rem; margin: 0; } .page-hero .place-tags { margin-top: 1rem; } .page-hero .lead-tag { margin-top: .8rem; }'
    '.place-where { margin: 0; font-family: var(--font-ui); font-weight: 700; font-size: .9rem; color: var(--muted); }'
    '.place-card h3 a { color: inherit; text-decoration-thickness: 2px; text-underline-offset: .2em; } .place-card h3 a:hover { color: var(--link); }'
    '.place-photo { width: 100%; height: 4.5rem; object-fit: cover; border-bottom: 8px solid var(--accent); }'
    '.place-key { grid-template-columns: repeat(3, minmax(0, 1fr)); } .place-key dt { text-transform: none; letter-spacing: 0; }'
    '@media (max-width: 820px) { .place-key { grid-template-columns: 1fr; } }'
    '</style>')


def lead_key(leads):
    return '<ul class="lead-key" aria-label="Who leads each project">' + ''.join(f'<li>{lead_line(k)}</li>' for k in LEAD_ORDER if k in leads) + '</ul>'


def project_card(p):
    links = ''.join(f'<li>{ext(h, E(t))}</li>' for t, h in p['links'])
    if p.get('news'):
        links = f'<li><a href="{{R}}news/{p["news"]}.html">Read our story</a></li>' + links
    if p.get('page'):
        links = f'<li><a href="{{R}}{p["page"]}">{E(p.get("page_label") or "Learn more")}</a></li>' + links
    return (f'<li class="project {p["fill"]}"><div class="project-pat" style="background-image:url({{R}}pattern-{p["pat"]}-sm.webp)" aria-hidden="true"></div>'
            f'<div class="project-body">{status_tag(p["status"])}<h3 class="h3">{E(p["title"])}</h3>{lead_line(p.get("lead"))}<p>{E(p["text"])}</p>{f"<ul class=project-links>{links}</ul>" if links else ""}</div></li>')


def build_projects():
    groups = ''
    for k in LEAD_ORDER:
        items = [p for p in PROJECTS if p.get('lead') == k]
        if not items:
            continue
        gid = 'lead-' + re.sub(r'[^a-z]+', '-', k.lower()).strip('-')
        more = f' <a href="{{R}}boards.html">Meet the DDA &amp; DEGA</a>.' if k != 'City' else ''
        groups += (f'<section class="lead-group" aria-labelledby="{gid}"><h2 class="h2 {LEADS[k]["cls"]}" id="{gid}"><span class="lead-mark" aria-hidden="true"></span>{E(LEADS[k]["group"])}</h2>'
                   f'<p class="lead-intro">{E(LEADS[k]["intro"])}{more}</p><ul class="projects">{"".join(project_card(p) for p in items)}</ul></section>')
    body = SECTION_CSS + page_hero([('index.html', 'Home'), ('about.html', 'About'), ('projects.html', 'Projects')], 'Downtown in progress', 'Projects',
                     'New plazas and pocket parks, rebuilt streets, a creekside festival site and new signs. Here’s what’s changing downtown, who’s leading it, and where to follow along.', 'f-red')
    body += f'''<section class="section" aria-label="Projects by who leads them">
  <div class="wrap">
    {in_short('Projects are grouped by who leads them: the Downtown Economic Growth Authority (DEGA), or the City of Kalamazoo. Each project shows what is happening now and links for updates.')}
    {lead_key({p.get('lead') for p in PROJECTS})}
    {groups}
    <div class="two-col" style="margin-top:2.5rem">
      <section class="panel f-blue"><h2>Investing in downtown</h2><p>Restored landmarks and new buildings from private owners and developers.</p><p><a href="{{R}}investment.html">See private investment downtown</a></p></section>
      <section class="panel"><h2>Construction and detours</h2><p>Downtown businesses stay open during construction. For current closures, see {ext(STREETS_FOR_ALL, 'Streets for All updates')}, or call 311.</p></section>
    </div>
    <section class="panel f-pink" style="margin-top:1rem"><h2>Have a question about a project?</h2><p>Email {DOWNTOWN_EMAIL} or call {DOWNTOWN_PHONE}. DDA and DEGA projects are discussed at the monthly <a href="{{R}}boards.html">DDA &amp; DEGA meetings</a>.</p></section>
  </div>
</section>'''
    page('projects.html', 'Projects', body, None, 'Downtown Kalamazoo projects led by the DEGA and the City of Kalamazoo: placemaking, wayfinding and signage, Arcadia Creek, Streets for All and more.')


# ---------------------------------------------------------------- Placemaking
PLACEMAKING = CL.placemaking()
PATH_PATTERN['placemaking.html'] = 'squiggle'
PATH_PATTERN.update({f'placemaking/{p["slug"]}.html': 'squiggle' for p in PLACEMAKING})
PLACE_PATS = [('squiggle', 'f-green'), ('waves', 'f-blue'), ('dashes', 'f-red'), ('confetti', 'f-pink'), ('dots', 'f-mist'), ('arcs', 'f-green')]
PLACE_URL = CITY + '/Community/Projects/2025/Downtown-Kalamazoo-Placemaking'
PLACE_CRUMBS = [('index.html', 'Home'), ('about.html', 'About'), ('projects.html', 'Projects'), ('placemaking.html', 'Placemaking')]
PLACE_CSS = SECTION_CSS
FUNDING_NOTE = {
    'Fully funded': 'All the money needed to build it is in place.',
    'Partially funded': 'Some funding is in place. The rest is still being secured.',
    'Seeking funding': 'Designed or planned, and waiting on funding.',
}


def place_look(i, p):
    pat, fill = PLACE_PATS[i % len(PLACE_PATS)]
    return p.get('pattern') or pat, p.get('fill') or fill


def link_item(text, url):
    return f'<li>{ext(url, E(text))}</li>' if url.startswith('http') else f'<li><a href="{{R}}{E(url)}">{E(text)}</a></li>'


def place_tags(p):
    stage = f'<span class="status-tag">{E(p["stage"])}</span>' if p['stage'] else ''
    return f'<p class="place-tags">{status_tag(p["funding"])}{stage}</p>'


def build_placemaking():
    cards = ''
    for i, p in enumerate(PLACEMAKING):
        pat, fill = place_look(i, p)
        art = (f'<img class="place-photo" src="{{R}}{E(p["image"])}" alt="" loading="lazy">' if p['image']
               else f'<div class="project-pat" style="background-image:url({{R}}pattern-{pat}-sm.webp)" aria-hidden="true"></div>')
        where = f'<p class="place-where"><span class="sr-only">Where: </span>{E(p["where"])}</p>' if p['where'] else ''
        cards += (f'<li class="project place-card {fill}">{art}<div class="project-body">{place_tags(p)}'
                  f'<h3 class="h3"><a href="{{R}}placemaking/{p["slug"]}.html">{E(p["title"])}</a></h3>{lead_line(p["lead"])}{where}<p>{E(p["summary"])}</p></div></li>')
    funded = sum(1 for p in PLACEMAKING if p['funding'] == 'Fully funded')
    partial = sum(1 for p in PLACEMAKING if p['funding'] == 'Partially funded')
    key = ''.join(f'<div><dt>{status_tag(k)}</dt><dd>{E(v)}</dd></div>' for k, v in FUNDING_NOTE.items())
    body = PLACE_CSS + page_hero(PLACE_CRUMBS, 'Downtown in progress', 'Placemaking',
                     'Turning downtown’s alleys, plazas and streets into places people want to be, not just pass through.', 'f-green')
    body += f'''<section class="section" aria-labelledby="place-why">
  <div class="wrap two-col">
    <div class="prose" style="max-width:none">
      {in_short(f'Downtown has {len(PLACEMAKING)} placemaking projects with funding in place: {funded} fully funded and {partial} partially funded. Choose a project to see what’s changing and when.')}
      <h2 class="h2" id="place-why">Why placemaking</h2>
      <p>One-way streets and fast traffic push people on foot toward downtown’s alleys and the Kalamazoo Mall. Placemaking makes those spaces worth lingering in, with lighting, public art, landscaping, places to sit and room for events, and ties them together so it’s easy to walk from one to the next.</p>
      <p>The work follows the Downtown Kalamazoo Placemaking plan, designed by SmithGroup with the City of Kalamazoo. Projects move ahead as funding is secured.</p>
    </div>
    <div class="aside">
      <section class="panel f-green" aria-labelledby="place-docs"><h2 id="place-docs">Plans and designs</h2><ul>{link_item('City of Kalamazoo project page', PLACE_URL)}{link_item('Designs from SmithGroup', 'https://downtown-placemaking-smithgroup.hub.arcgis.com/')}{link_item('DDA & DEGA budgets and reports', 'boards.html')}</ul></section>
    </div>
  </div>
</section>
<section class="section" style="padding-top:0" aria-labelledby="place-list">
  <div class="wrap">
    <h2 class="h2" id="place-list" style="margin-bottom:1rem">Funded projects</h2>
    <ul class="projects">{cards}</ul>
    <h3 class="h3" style="margin-top:2rem" id="place-key">What the labels mean</h3>
    <dl class="glance place-key" aria-labelledby="place-key">{key}</dl>
  </div>
</section>
<section class="section" style="padding-top:0" aria-labelledby="place-next">
  <div class="wrap two-col">
    <div class="prose" style="max-width:none">
      <h2 class="h2" id="place-next">Also in the plan</h2>
      <p>These parts of the placemaking plan are designed in concept, and their schedules depend on funding:</p>
      <ul>
        <li><strong>Exchange Alley:</strong> lighting, public art and painted pavement, with a walking connection from Farmers Alley to Rose Street.</li>
        <li><strong>North Kalamazoo Mall:</strong> a design that’s more open to festivals, pop-up events, walking and biking.</li>
      </ul>
    </div>
    <div class="aside">
      <section class="panel f-pink"><h2>Questions or ideas?</h2><p>Email {DOWNTOWN_EMAIL} or call {DOWNTOWN_PHONE}. Board-funded projects are discussed at the monthly <a href="{{R}}boards.html">DDA &amp; DEGA meetings</a>.</p></section>
    </div>
  </div>
</section>'''
    page('placemaking.html', 'Placemaking', body, None, 'Downtown Kalamazoo placemaking projects: Farmers Alley Pocket Park, Rose Street Plaza, Water Street and the South Burdick festival street.')
    for i, p in enumerate(PLACEMAKING):
        build_place(i, p)


def build_place(i, p):
    pat, fill = place_look(i, p)
    glance = [('Led by', LEADS[p['lead']]['label'].replace('Led by the ', '').replace('Led by ', '') if p['lead'] in LEADS else ''), ('Where', p['where']), ('Timeline', p['timeline']), ('Design', p['design'])]
    gl = ''.join(f'<div><dt>{k}</dt><dd>{E(v)}</dd></div>' for k, v in glance if v)
    links = ''.join(link_item(l['text'], str(l['url']).strip()) for l in p['links'])
    if p['news']:
        links = f'<li><a href="{{R}}news/{E(p["news"])}.html">Read our story</a></li>' + links
    others = ''.join(f'<li><a href="{{R}}placemaking/{q["slug"]}.html">{E(q["title"])}</a></li>' for q in PLACEMAKING if q is not p)
    photo = (p['image'], p['image_alt']) if p['image'] else None
    body = PLACE_CSS + page_hero(PLACE_CRUMBS + [(f'placemaking/{p["slug"]}.html', p['title'])], 'Placemaking project', E(p['title']),
                     E(p['summary']), fill, place_tags(p) + lead_line(p['lead']), photo)
    body += f'''<section class="section" aria-labelledby="glance-title"><div class="wrap"><h2 class="sr-only" id="glance-title">At a glance</h2><dl class="glance">{gl}</dl><p class="muted" style="margin-top:.6rem;font-size:.95rem"><strong>{E(p['funding'])}:</strong> {E(FUNDING_NOTE[p['funding']])}</p></div></section>
<section class="section" style="padding-top:0" aria-label="About this project">
  <div class="wrap two-col">
    <article class="prose">
      {p['body_html']}
    </article>
    <div class="aside">
      {f'<section class="panel" aria-labelledby="pl-links"><h2 id="pl-links">Plans and updates</h2><ul>{links}</ul></section>' if links else ''}
      <section class="panel f-green" aria-labelledby="pl-more"><h2 id="pl-more">More placemaking</h2><ul>{others}</ul><p><a href="{{R}}placemaking.html">All placemaking projects</a></p></section>
      <section class="panel f-pink"><h2>Questions?</h2><p>Email {DOWNTOWN_EMAIL} or call {DOWNTOWN_PHONE}.</p></section>
    </div>
  </div>
</section>'''
    page(f'placemaking/{p["slug"]}.html', p['title'], body, None, p['summary'])


# ---------------------------------------------------------------- Investing in downtown
INVESTMENTS = CL.investments()
PATH_PATTERN['investment.html'] = 'pinstripes'
if not any(h == 'investment.html' for h, _ in ABOUT_MENU):
    ABOUT_MENU.insert(next((i + 1 for i, (h, _) in enumerate(ABOUT_MENU) if h == 'projects.html'), len(ABOUT_MENU)), ('investment.html', 'Investing in downtown'))
INVEST_PATS = [('arcs', 'f-pink'), ('pinstripes', 'f-blue'), ('maze', 'f-mist'), ('stripes', 'f-red'), ('speckle', 'f-green')]


def build_investment():
    cards = ''
    for i, p in enumerate(INVESTMENTS):
        pat, fill = INVEST_PATS[i % len(INVEST_PATS)]
        art = (f'<img class="place-photo" src="{{R}}{E(p["image"])}" alt="{E(p["image_alt"])}" loading="lazy">' if p['image']
               else f'<div class="project-pat" style="background-image:url({{R}}pattern-{pat}-sm.webp)" aria-hidden="true"></div>')
        tags = ''.join(f'<span class="status-tag{" st-next" if j else ""}">{E(t)}</span>' for j, t in enumerate([p['kind'], p['status']]) if t)
        where = f'<p class="place-where"><span class="sr-only">Where: </span>{E(p["where"])}</p>' if p['where'] else ''
        links = ''.join(link_item(l['text'], str(l['url']).strip()) for l in p['links'])
        cards += (f'<li class="project place-card {fill}">{art}<div class="project-body"><p class="place-tags">{tags}</p>'
                  f'<h3 class="h3">{E(p["title"])}</h3>{where}{f"<p>{E(p["summary"])}</p>" if p["summary"] else ""}'
                  f'{p["body_html"]}{f"<ul class=project-links>{links}</ul>" if links else ""}</div></li>')
    body = SECTION_CSS + page_hero([('index.html', 'Home'), ('about.html', 'About'), ('investment.html', 'Investing in downtown')], 'Building downtown’s future', 'Investing in downtown',
                     'Owners and developers are restoring landmarks and building new. Here’s the private investment taking shape in downtown Kalamazoo.', 'f-blue')
    body += f'''<section class="section" aria-labelledby="inv-title">
  <div class="wrap">
    {in_short('This page lists private investment in downtown Kalamazoo: restorations and new buildings by owners and developers. Projects led by the City or the DEGA are on the Projects page.')}
    <h2 class="h2" id="inv-title" style="margin-bottom:1rem">Private investment</h2>
    <ul class="projects">{cards}</ul>
    <div class="two-col" style="margin-top:2.5rem">
      <section class="panel f-blue"><h2>Thinking about investing downtown?</h2><p>Talk with the City of Kalamazoo’s downtown team about sites, site plan review and support for downtown businesses. Email {DOWNTOWN_EMAIL} or call {DOWNTOWN_PHONE}.</p><p><a href="{{R}}businesses.html">Business resources</a></p></section>
      <section class="panel"><h2>Public investment</h2><p>See the projects led by the City and the DEGA, and the DDA &amp; DEGA budgets and reports.</p><ul><li><a href="{{R}}projects.html">Downtown projects</a></li><li><a href="{{R}}boards.html">DDA &amp; DEGA</a></li></ul></section>
    </div>
  </div>
</section>'''
    page('investment.html', 'Investing in downtown', body, None, 'Private investment in downtown Kalamazoo: the State Theatre restoration and new development.')


# ---------------------------------------------------------------- Business resources
def build_business_resources():
    def res(title, text, links, fill=''):
        ls = ''.join(f'<li>{ext(h, E(t)) if h.startswith("http") else f"<a href=\"{{R}}{h}\">{E(t)}</a>"}</li>' for t, h in links)
        return f'<section class="panel {fill}"><h3 class="h3">{E(title)}</h3><p>{text}</p>{f"<ul>{ls}</ul>" if ls else ""}</section>'
    body = page_hero([('index.html', 'Home'), ('businesses.html', 'For businesses')], 'Open, grow, take part', 'Business resources',
                     'Grants, permits, programs and the people to call, for anyone running a business or planning one in downtown Kalamazoo.', 'f-blue')
    body += f'''<section class="section" aria-labelledby="money-title">
  <div class="wrap">
    {in_short('This page lists grants, permits and downtown programs for businesses, with links to apply. For help, email downtown@kalamazoocity.org.')}
    <h2 class="h2" id="money-title" style="margin-bottom:1rem">Grants &amp; funding</h2>
    <div class="res-grid">
      {res('Kalamazoo Micro-Enterprise Grants', '$5,000 grants for for-profit microbusinesses in the city of Kalamazoo: open at least a year, 10 or fewer employees, and $1 million or less in yearly revenue. A partnership of the City and United Way of South Central Michigan, funded by the Foundation for Excellence. Application dates vary by round, so check the United Way page.', [('Kalamazoo Micro-Enterprise Grants', 'https://unitedforscmi.org/battle-creek-kalamazoo/kalamazoo-micro-enterprise-grants/')], 'f-green')}
      {res('Match on Main', 'A state grant from the Michigan Economic Development Corporation for storefront businesses in downtowns and commercial corridors. The City applies on behalf of the businesses it selects. In 2026 it could request up to $25,000 for two downtown businesses, with a 10% match.', [('2026 Match on Main announcement', 'news/match-on-main-grant.html')], 'f-pink')}
      {res('Event & marketing sponsorships', 'The DDA and DEGA sponsor downtown events: up to $2,500 for a single-day event and up to $5,000 for a multi-day event.', [('Apply for a sponsorship', BOARDS_URL + '/Apply-for-a-DDADEGA-Events-Marketing-Sponsorship'), ('About the DDA & DEGA', 'boards.html')], 'f-blue')}
    </div>
    <h2 class="h2" style="margin:2.5rem 0 1rem">Permits &amp; plans</h2>
    <div class="res-grid">
      {res('Social District permit', 'Licensed bars and restaurants inside the Social District can apply to serve drinks people can carry within the Commons Area.', [('Apply for a Social District permit', CITY + '/Community/Downtown-Kalamazoo/Central-Commons-Refreshment-Area/Apply-for-a-Social-District-Permit'), ('How the Social District works', 'social-district.html')])}
      {res('Building or renovating', 'New construction and major changes go through the City’s site plan review. You can see recently approved downtown plans, too.', [('Site plan review', CITY + '/Business-Development/Real-Estate-Development/Apply-for-Site-Plan-Review'), ('Downtown projects', 'projects.html')])}
      {res('City business help', 'Licenses, development and working with the City of Kalamazoo.', [('City of Kalamazoo business development', CITY + '/Business-Development')])}
    </div>
    <h2 class="h2" style="margin:2.5rem 0 1rem">Get the word out</h2>
    <div class="res-grid">
      {res('Get listed in the directory', 'Add or update your listing in the Explore downtown directory with your website, a short description and whether you take Downtown Dollars.', [('See the directory', 'directory.html')], 'f-green')}
      {res('Accept Downtown Dollars', 'Join the businesses that take Downtown Dollars. Customers can spend them at your door for five years.', [('How Downtown Dollars work', 'dollars.html')], 'f-pink')}
      {res('Put your event on the calendar', 'Workshops, sales, shows and celebrations. Every submission is reviewed before it’s posted.', [('Submit an event', 'submit-event.html')], 'f-blue')}
      {res('Use the brand', 'Window decals, stickers and the downtown patterns help customers spot you. Email us for brand files and guidelines.', [('Take a pattern home', 'take-home.html')])}
    </div>
    <h2 class="h2" style="margin:2.5rem 0 1rem">Downtown services</h2>
    <div class="res-grid">
      {res('Downtown Ambassadors', 'Cleaning, snow removal, graffiti and a friendly face on the street, seven days a week.', [('About the ambassadors', 'ambassadors.html')])}
      {res('Waste & recycling', 'Smart Bigbelly bins on downtown sidewalks, emptied when they’re full.', [('How the bins work', 'waste-recycling.html')])}
      {res('Parking for customers and staff', 'The first 90 minutes are free in the Epic Center and Kalamazoo Mall ramps.', [('Visit & park', 'visit.html')])}
    </div>
  </div>
</section>
<section class="section" style="padding-top:0" aria-labelledby="stay-title">
  <div class="wrap two-col">
    <div class="prose" style="max-width:none">
      <h2 class="h2" id="stay-title">Stay in the loop</h2>
      <ul class="checks f-blue">
        <li><a href="{{R}}newsletter.html">Get the downtown newsletter</a> for events, programs and grant rounds.</li>
        <li>Come to a <a href="{{R}}boards.html">DDA &amp; DEGA board meeting</a>, the third Monday of the month.</li>
        <li>Follow {ext(STREETS_FOR_ALL, 'Streets for All construction')} if you’re on Kalamazoo Avenue.</li>
        <li>Planning for the holidays? See the <a href="{{R}}holidays/businesses.html">holiday partner toolkit</a>.</li>
      </ul>
    </div>
    <div class="aside">
      <section class="panel f-blue"><h2>Talk to the downtown team</h2><p>Email <span>{DOWNTOWN_EMAIL}</span> <button type="button" class="btn btn-small btn-quiet" data-copy="{DOWNTOWN_EMAIL}">Copy address</button></p><p>Call {DOWNTOWN_PHONE}, or 311 for City services.</p></section>
      <section class="panel"><h2>Marketing plan library</h2><p>Presentations, data, plans and projections behind downtown marketing.</p><p>{ext(LIBRARY_URL, 'Open the plan library')}</p></section>
    </div>
  </div>
</section>'''
    page('businesses.html', 'Business resources', body, 'businesses', 'Grants, permits, programs and contacts for businesses in downtown Kalamazoo.')


# ---------------------------------------------------------------- Our team
GENERAL_PHONE = '(269) 337-8000'
STAFF_FILLS = ['f-blue', 'f-green', 'f-pink', 'f-red']
STAFF_PATTERNS = ['dots', 'arcs', 'loops', 'confetti']
NUMBER_WORDS = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve']


def _slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-') or 'contact'


def _vcard_text(v):
    return v.replace('\\', '\\\\').replace(',', '\\,').replace(';', '\\;')


def write_vcard(p):
    """A contact card people can save to their phone or address book: out/team/<name>.vcf"""
    parts = p['name'].split()
    first, last = (' '.join(parts[:-1]), parts[-1]) if len(parts) > 1 else (p['name'], '')
    lines = ['BEGIN:VCARD', 'VERSION:3.0', f'FN:{_vcard_text(p["name"])}', f'N:{_vcard_text(last)};{_vcard_text(first)};;;',
             f'TITLE:{_vcard_text(p["title"])}', 'ORG:City of Kalamazoo;Downtown Kalamazoo', f'EMAIL;TYPE=WORK:{p["email"]}']
    if p['phone']:
        lines.append(f'TEL;TYPE=WORK,VOICE:{_tel(p["phone"])}')
    lines += ['ADR;TYPE=WORK:;;241 W. South St.;Kalamazoo;MI;49007;USA', f'URL:{SITE_URL}team.html', 'END:VCARD']
    path = f'team/{_slug(p["name"])}.vcf'
    os.makedirs(os.path.join(OUT, 'team'), exist_ok=True)
    with open(os.path.join(OUT, path), 'w', newline='') as f:
        f.write('\r\n'.join(lines) + '\r\n')
    return path


def copy_row(email, whose, strong=False):
    link = f'<a href="mailto:{E(email)}"{" class=\"who-strong\"" if strong else ""}>{E(email)}</a>'
    return (f'<p class="copy-row">{link} <button type="button" class="btn btn-small btn-quiet" data-copy="{E(email)}" '
            f'aria-label="Copy email for {E(whose)}">Copy email</button></p>')


def staff_card(p, i):
    fill = STAFF_FILLS[i % len(STAFF_FILLS)]
    pat = STAFF_PATTERNS[i % len(STAFF_PATTERNS)]
    if p['photo']:
        pic = f'<img src="{{R}}{E(p["photo"])}" alt="{E(p["photo_alt"])}" loading="lazy" width="400" height="500">'
    else:
        pic = (f'<div class="amb-ph" style="background-image:url({{R}}pattern-{pat}.webp)" aria-hidden="true">'
               f'<span class="amb-initials">{E(_initials(p["name"]))}</span></div>')
    say = [f'Say it: {E(p["pronunciation"])}'] if p['pronunciation'] else []
    say += [E(p['pronouns'])] if p['pronouns'] else []
    say = f'<p class="staff-say">{" · ".join(say)}</p>' if say else ''
    bio = f'<p class="staff-bio">{E(p["bio"])}</p>' if p['bio'] else ''
    handles = ''.join(f'<li>{E(h)}</li>' for h in p['handles'])
    handles = f'<div class="staff-handles"><h4>Talk to me about</h4><ul>{handles}</ul></div>' if handles else ''
    phone = f'<p><a href="tel:{_tel(p["phone"])}">{E(p["phone"])}</a></p>' if p['phone'] else ''
    card = write_vcard(p)
    return f'''<li class="staff {fill}">
        <figure class="staff-pic">{pic}</figure>
        <div class="staff-body">
          <div class="staff-id"><h3 class="staff-name">{E(p["name"])}</h3><p class="staff-title">{E(p["title"])}</p>{say}</div>
          {bio}
          {handles}
          <div class="staff-reach">
            {copy_row(p["email"], p["name"])}
            {phone}
            <p class="staff-card-link"><a href="{{R}}{card}" download>Save contact card<span class="sr-only"> for {E(p["name"])}</span></a></p>
          </div>
        </div>
      </li>'''


def who_reach(who, staff_by_name, amb):
    if who in staff_by_name:
        p = staff_by_name[who]
        phone = f'<p><a href="tel:{_tel(p["phone"])}">{E(p["phone"])}</a></p>' if p['phone'] else ''
        return f'<p class="who-name">{E(p["name"])}, {E(p["title"])}</p>{copy_row(p["email"], p["name"])}{phone}'
    if who == 'Downtown Ambassadors':
        call = (f'<p><a class="btn btn-primary" href="tel:{_tel(amb["phone"])}">{PHONE_ICON}Call {E(amb["phone"])}</a></p>'
                if amb['phone'] else '<p>Call 311</p>')
        hours = ' · '.join(f'{E(str(h["days"]))}, {E(str(h["time"]))}' for h in amb['hours'])
        hours = f'<p class="muted who-small">{hours}</p>' if hours else ''
        return f'<p class="who-name">Downtown Ambassadors</p>{call}{hours}'
    if who == 'DDA & DEGA page':
        return ('<p class="who-name"><a href="{R}boards.html">DDA &amp; DEGA page</a></p>'
                '<p class="muted who-small">Meetings are the third Monday of the month, 3 to 5 p.m., at City Hall.</p>')
    return (f'{copy_row(DOWNTOWN_EMAIL, "the downtown team", strong=True)}'
            f'<p>Call <a href="tel:311">311</a> or <a href="tel:{_tel(GENERAL_PHONE)}">{GENERAL_PHONE}</a></p>')


def build_team():
    t = TEAM
    if t['draft']:
        return
    amb = CL.ambassador_info()
    staff_by_name = {p['name']: p for p in t['staff']}

    jump = [('how-title', 'How downtown is organized'), ('contact-title', 'Who to contact')]
    if t['staff']:
        jump.append(('staff-title', 'Downtown staff'))
    jump += [('board-title', 'The board'), ('amb-title', 'Downtown Ambassadors'), ('involved-title', 'Get involved')]
    jump = ('<nav class="jump" aria-label="On this page"><ul class="chips">'
            + ''.join(f'<li><a class="chip" href="#{h}">{E(x)}</a></li>' for h, x in jump) + '</ul></nav>')
    body = page_hero([('index.html', 'Home'), ('about.html', 'About'), ('team.html', 'Our team')], 'About downtown', 'Our team',
                     'The people behind downtown Kalamazoo: City of Kalamazoo staff who serve the DDA and DEGA, the board that guides them, '
                     'and the Downtown Ambassadors you see on the street every day.', 'f-pink', extra=jump)

    # How downtown is organized
    body += f'''<section class="section" aria-labelledby="how-title">
  <div class="wrap">
    {in_short('Downtown staff work for the City of Kalamazoo and serve the DDA and DEGA, two public authorities governed by one board. Below is who to contact for what.')}
    <div class="section-head"><div class="narrow"><h2 class="h2" id="how-title">How downtown is organized</h2>
      <p>Two public authorities invest in downtown, and one board governs both. The City of Kalamazoo provides their staff through a service agreement, so the people you reach are City employees working for the DDA and DEGA.</p></div></div>
    <div class="org-map">
      <div class="org-board">
        <p class="org-k">One shared board of {NUMBER_WORDS[len(t["members"])] if len(t["members"]) < len(NUMBER_WORDS) else len(t["members"])} members</p>
        <div class="org-pair">
          <section class="org-card f-blue" aria-labelledby="org-dda"><div class="card-top" aria-hidden="true">DDA</div><div class="card-body">
            <h3 class="h3" id="org-dda">Downtown Development Authority</h3><p>Invests in the downtown district, funded by tax increment financing and a 2-mill levy.</p></div></section>
          <section class="org-card f-green" aria-labelledby="org-dega"><div class="card-top" aria-hidden="true">DEGA</div><div class="card-body">
            <h3 class="h3" id="org-dega">Downtown Economic Growth Authority</h3><p>Invests along downtown’s commercial corridors. Created by the City Commission in 2018.</p></div></section>
        </div>
      </div>
      <p class="org-link"><svg aria-hidden="true" width="64" height="20" viewBox="0 0 64 20" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 10h56M12 3 4 10l8 7M52 3l8 7-8 7"/></svg><span>Service agreement</span></p>
      <section class="org-card org-city f-pink" aria-labelledby="org-city"><div class="card-top" aria-hidden="true">City of Kalamazoo</div><div class="card-body">
        <h3 class="h3" id="org-city"><span class="sr-only">City of Kalamazoo: </span>Employs downtown staff</h3><p>Staff are City employees who serve as staff to the DDA and DEGA and support the board day to day.</p></div></section>
    </div>
  </div>
</section>'''

    # Who to contact
    rows = ''.join(f'''<li class="who">
        <div class="who-need"><h3>{E(c["need"])}</h3>{f'<p class="muted">{E(c["detail"])}</p>' if c["detail"] else ''}</div>
        <div class="who-reach">{who_reach(c["who"], staff_by_name, amb)}</div>
      </li>''' for c in t['contacts'])
    body += f'''<section class="section" style="padding-top:0" aria-labelledby="contact-title">
  <div class="wrap">
    <div class="section-head"><div class="narrow"><h2 class="h2" id="contact-title">Who to contact</h2>
      <p>Find what you need, and the right person is next to it. Every address and number is written out, so you can copy it or read it aloud.</p></div></div>
    <ul class="who-list">{rows}</ul>
  </div>
</section>'''

    # Downtown staff
    if t['staff']:
        cards = ''.join(staff_card(p, i) for i, p in enumerate(t['staff']))
        body += f'''<section class="section team-band" aria-labelledby="staff-title">
  <div class="wrap">
    <div class="section-head"><div class="narrow"><h2 class="h2" id="staff-title">Downtown staff</h2>
      <p>City of Kalamazoo employees who serve as staff to the DDA and DEGA.</p></div></div>
    <ul class="staff-list">{cards}</ul>
  </div>
</section>'''

    # The board
    if t['show_board_roster'] and t['members']:
        def member(m):
            role = (f'<span class="tag">{E(m["role"])}</span>' if m['role'] != 'Member'
                    else f'<span class="board-role muted">{E(m["role"])}</span>')
            return f'<li><span class="board-name">{E(m["name"])}</span>{role}</li>'
        as_of = f', {E(t["board_as_of"])}' if t['board_as_of'] else ''
        board = (f'<ul class="board-list" aria-label="DDA and DEGA board members{as_of}">{"".join(member(m) for m in t["members"])}</ul>'
                 + (f'<p class="muted who-small">Board members as of {E(t["board_as_of"])}.</p>' if t['board_as_of'] else ''))
    else:
        board = '''<div class="panel board-go"><div><h3 class="h3">Meet the board on the DDA &amp; DEGA page</h3>
      <p>See every member and their role, along with meeting dates, agendas, budgets and reports.</p></div>
      <p><a class="btn btn-primary" href="{R}boards.html">Go to DDA &amp; DEGA</a></p></div>'''
    body += f'''<section class="section" aria-labelledby="board-title">
  <div class="wrap">
    <div class="section-head"><div class="narrow"><h2 class="h2" id="board-title">The board</h2>
      <p>One board serves both the DDA and DEGA. Members are appointed to four-year terms, and the mayor serves ex officio.</p></div>
      <a class="btn" href="{{R}}boards.html">Meetings, budgets and reports</a></div>
    {board}
  </div>
</section>'''

    # Downtown Ambassadors
    photo = f'<img class="team-amb-photo" src="{{R}}{E(amb["photo"])}" alt="{E(amb["photo_alt"])}" loading="lazy">' if amb['photo'] else ''
    call = f'<a class="btn btn-primary" href="tel:{_tel(amb["phone"])}">{PHONE_ICON}Call {E(amb["phone"])}</a>' if amb['phone'] else ''
    body += f'''<section class="section amb-band" aria-labelledby="amb-title">
  <div class="wrap team-amb">
    {photo}
    <div class="team-amb-text">
      <p class="eyebrow">On the street seven days a week</p>
      <h2 class="h2" id="amb-title">Downtown Ambassadors</h2>
      <p>The Ambassadors pick up litter, remove graffiti, help visitors find their way and keep an eye on downtown. If something needs cleaning up, call them directly.</p>
      <div class="btn-row">{call}<a class="btn" href="{{R}}ambassadors.html">Meet the Ambassadors</a></div>
    </div>
  </div>
</section>'''

    # Get involved
    work = ''
    if t['hiring_text'] and t['hiring_url']:
        link = ext(t['hiring_url'], 'See openings') if t['hiring_url'].startswith('http') else f'<a href="{{R}}{E(t["hiring_url"])}">See openings</a>'
        work = f'''<section class="involve f-red" aria-labelledby="gi-work"><h3 id="gi-work">Work downtown</h3><p>{E(t["hiring_text"])}</p><p>{link}</p></section>'''
    hours = f'<br>{E(t["office_hours"])}' if t['office_hours'] else ''
    body += f'''<section class="section" aria-labelledby="involved-title">
  <div class="wrap">
    <h2 class="h2" id="involved-title" style="margin-bottom:1.5rem">Get involved</h2>
    <div class="involve-row">
      <section class="involve f-blue" aria-labelledby="gi-board"><h3 id="gi-board">Join the board</h3><p>Board members are appointed. Anyone interested can apply through the City.</p><p>{ext(CITY + '/Government/Boards-Commissions/Apply-to-Join-a-Board-or-Commission', 'Apply to join a board')}</p></section>
      <section class="involve f-green" aria-labelledby="gi-meet"><h3 id="gi-meet">Come to a meeting</h3><p>Board meetings are open to the public, the third Monday of the month from 3 to 5 p.m.</p><p>{ext(CITY + '/Government/Boards-Commissions/Minutes-Agendas', 'Agendas and minutes')}</p></section>
      {work}
      <section class="involve f-pink" aria-labelledby="gi-visit"><h3 id="gi-visit">Visit the office</h3><p>City Hall, 241 W. South St.{hours}</p><p><a href="{{R}}visit.html">Directions and parking</a></p></section>
    </div>
  </div>
</section>'''
    page('team.html', 'Our team', body, None,
         'Who to contact downtown: the City of Kalamazoo staff who serve the DDA and DEGA, the board and the Downtown Ambassadors.')


# ---------------------------------------------------------------- About
def build_about():
    programs = ''.join(program_card(*p, heading='h2') for p in PROGRAMS)
    body = page_hero([('index.html', 'Home'), ('about.html', 'About')], 'Everyone’s neighborhood', 'About downtown',
                     'Downtown Kalamazoo is looked after by the City of Kalamazoo’s downtown team, two public authorities, a crew of ambassadors and the hundreds of people who open its doors every day.', 'f-green')
    body += f'''<section class="section" aria-label="Downtown programs">
  <div class="wrap">
    {in_short('This section explains who looks after downtown and how. Choose a topic to learn more.')}
    <ul class="programs">{programs}</ul>
    <div class="two-col" style="margin-top:2.5rem">
      <section class="panel f-blue"><h2>Contact the downtown team</h2><p>City of Kalamazoo, City Hall, 241 W. South St.</p><p>Email {DOWNTOWN_EMAIL}<br>Call {DOWNTOWN_PHONE}, or 311 for City services.</p></section>
      <section class="panel"><h2>More about downtown</h2><ul><li><a href="{{R}}news.html">News &amp; stories</a></li><li><a href="{{R}}businesses.html">Business resources</a></li><li><a href="{{R}}access-guide.html">Accessible downtown</a></li><li><a href="{{R}}accessibility.html">This website’s accessibility</a></li></ul></section>
    </div>
  </div>
</section>'''
    page('about.html', 'About downtown', body, None, 'Who looks after downtown Kalamazoo: the downtown team, the DDA and DEGA, the ambassadors and more.')


def build_year_round():
    build_year_home(); build_calendar(); build_cal_event_pages(); build_news(); build_history(); build_boards()
    build_team(); build_ambassadors(); build_waste(); build_social(); build_projects(); build_placemaking(); build_investment(); build_business_resources(); build_about()
