# Plan your day: the planner (holidays/plan.html) and one page per plan (holidays/plan/<slug>.html).
# Run from build.py with exec(), so it shares build.py's helpers (page, page_hero, in_short, EVENTS, PLANS ...).
# The plans themselves are in content/itineraries.yml.

PLAN_CSS = '<style>' + open(os.path.join(HERE, 'plan.css'), encoding='utf-8').read() + '</style>'
PLAN_JS = '<script>' + open(os.path.join(HERE, 'plan.js'), encoding='utf-8').read() + '</script>'
_EV = {e['slug']: e for e in EVENTS}
SEASON = (min(e['date'] for e in EVENTS), max(e.get('end') or e['date'] for e in EVENTS))


def _ev_time(e):
    parts = e['when_short'].split(' · ')
    return parts[1] if len(parts) > 1 else ''


def _events_json():
    return [dict(slug=e['slug'], title=e['title'], date=e['date'], end=e.get('end') or e['date'], time=_ev_time(e),
                 href=f'{{R}}events/{e["slug"]}.html') for e in EVENTS]


def _pick(name, value, visible, sr, extra=''):
    return (f'<label class="pick"><input type="checkbox" name="{name}" value="{E(value)}">'
            f'<span class="pick-text">{visible}{f"<span class=sr-only>{sr}</span>" if sr else ""}{extra}</span>'
            f'<span class="n"></span></label>')


def _mentions(p, n=3):
    names = [t['name'] for t in p['mentions']]
    if not names:
        return ''
    more = len(names) - n
    shown = ', '.join(E(x) for x in names[:n])
    return f'<p class="pc-incl"><span class="k">Includes</span> {shown}{f" and {more} more" if more > 0 else ""}</p>'


def plan_card(p):
    href = f'{{R}}plan/{p["slug"]}.html'
    facts = ''.join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in [
        ('Best for', E(p['best_for'])), ('Time', E(p['time'])), ('When', E(p['when']))])
    return f'''<li class="plan-card {p["fill"]}" data-slug="{p["slug"]}" data-days="{" ".join(p["days"])}" data-budget="{p["budget_key"]}" data-who="{" ".join(p["who"])}" data-days-text="{E(p["days_text"])}" data-budget-text="{E(p["budget_text"])}" data-best="{E(p["best_for"])}">
  <article aria-labelledby="pc-{p["slug"]}">
    <div class="pc-top" style="--pc-pat:url({{R}}pattern-{p["pattern"]}-sm.webp)" aria-hidden="true"></div>
    <div class="pc-body">
      <p class="pc-badges"><span class="budget-badge b-{p["budget_key"]}">{E(p["budget"] if p["budget_key"] != "free" else "Free")}<span class="bt">{"" if p["budget_key"] == "free" else E(p["budget_text"])}</span></span><span class="time-badge">{E(p["time"])}</span></p>
      <p class="pc-close" hidden></p>
      <h3 class="h3" id="pc-{p["slug"]}"><a href="{href}" data-plan-link>{E(p["title"])}</a></h3>
      <p>{E(p["summary"])}</p>
      <dl class="pc-facts">{facts}</dl>
      {_mentions(p)}
      <div class="btn-row pc-actions">
        <a class="btn btn-primary btn-small" href="{href}" data-plan-link>See the full plan<span class="sr-only">: {E(p["title"])}</span></a>
        <a class="btn btn-small" href="{href}?print=1" data-plan-link data-print>Print it<span class="sr-only">: {E(p["title"])}</span></a>
      </div>
      <a class="pc-remix" href="{{R}}plan/build-your-own.html?from={p["slug"]}"><svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>Make it yours: swap stops<span class="sr-only"> in {E(p["title"])}</span></a>
    </div>
  </article>
</li>'''


def build_plan_index():
    days = ''.join(_pick('day', d, f'<span aria-hidden="true">{IT.DAY_SHORT[d]}</span>', IT.DAY_NAMES[d]) for d in IT.DAYS)
    budgets = ''.join(_pick('budget', IT.BUDGET_KEY[k], f'<b aria-hidden="true">{E(sym) if k != "free" else "Free"}</b>' + (f' {E(txt)}' if k != 'free' else ''),
                            '') for k, sym, txt, _ in IT.BUDGETS)
    who = ''.join(_pick('who', k, E(label), '') for k, label in IT.WHO)
    cards = ''.join(plan_card(p) for p in PLANS)
    n = len(PLANS)
    rows = ''.join(f'<tr><th scope="row"><a href="{{R}}plan/{p["slug"]}.html">{E(p["title"])}</a></th><td>{E(p["best_for"])}</td>'
                   f'<td>{E(p["time"])}</td><td>{E(p["budget"])}<span class="sr-only"> ({E(p["budget_long"])})</span></td><td>{E(p["days_text"])}</td></tr>' for p in PLANS)
    body = page_hero([('index.html', 'Home'), ('plan.html', 'Plan your day')], 'Find the holidays your way', 'Plan your day',
                     f'Let us pick three of our {n} downtown plans for your day, or build your own stop by stop. Either way, print it or send it to whoever’s coming along.',
                     'f-blue')
    body += f'''{PLAN_CSS}<section class="section planner" aria-labelledby="build-title">
  <div class="wrap">
    {in_short('There are two ways to plan. “Pick for me” uses the questions below: choose the days you can go, your budget and who is coming, and three plans that fit show up, picked at random. “Build my own” lets you choose every stop yourself. Every plan can be printed or shared.')}
    <ul class="paths" aria-label="Two ways to plan your day">
      <li><a class="path is-here" href="#planner" aria-describedby="path-1"><span class="path-ic" aria-hidden="true" style="background-image:url({{R}}pattern-confetti-sm.webp)"></span><span class="path-name">Pick for me</span><span class="path-go" aria-hidden="true">↓</span><span class="path-text" id="path-1">Choose a day, budget and who’s coming. We’ll pull three plans that fit.</span><span class="path-badge">You’re here</span></a></li>
      <li><a class="path is-byo" href="{{R}}plan/build-your-own.html" aria-describedby="path-2"><span class="path-ic" aria-hidden="true" style="background-image:url({{R}}pattern-squiggle-sm.webp)"></span><span class="path-name">Build my own</span><span class="path-go" aria-hidden="true">Start →</span><span class="path-text" id="path-2">Pick your own stops from {sum(1 for b in directory_page.BIZ if b['cat'] in directory_page.VISITOR_CATS)} businesses and every holiday event, then print it with parking.</span></a></li>
    </ul>
    <form class="planner-form" id="planner" novalidate>
      <div class="pf-head"><h2 class="h2" id="build-title">Tell us about your day</h2><p class="help">Choose as many as you like in each row. Leave a row empty if anything works.</p></div>
      <fieldset class="pf-group"><legend><span class="pf-num" aria-hidden="true">1</span>What day are you going?</legend><div class="picks">{days}</div></fieldset>
      <fieldset class="pf-group"><legend><span class="pf-num" aria-hidden="true">2</span>Budget per person</legend><div class="picks">{budgets}</div></fieldset>
      <fieldset class="pf-group"><legend><span class="pf-num" aria-hidden="true">3</span>Who’s coming?</legend><div class="picks">{who}</div></fieldset>
      <div class="pf-actions">
        <button type="button" class="btn btn-primary" id="pf-more"><svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 3h5v5"/><path d="M4 20 21 3"/><path d="M21 16v5h-5"/><path d="m15 15 6 6"/><path d="M4 4l5 5"/></svg>Show me three more</button>
        <button type="reset" class="btn" id="pf-clear">Clear my choices</button>
      </div>
    </form>
    <div class="pf-result-row"><p class="pf-status" id="pf-status" role="status" aria-live="polite"></p><a class="pf-byo" href="{{R}}plan/build-your-own.html">Not quite right? Build your own<span aria-hidden="true"> →</span></a></div>
    <h2 class="sr-only" id="results-title">Plans for your day</h2>
    <ul class="plan-cards" id="plan-cards" aria-labelledby="results-title">{cards}</ul>
  </div>
</section>
<section class="section" style="padding-top:0" aria-labelledby="all-title">
  <div class="wrap">
    <details class="all-plans">
      <summary><span class="h3" id="all-title">Browse all {n} plans</span></summary>
      <div class="table-wrap" style="margin-top:1rem">
        <table>
          <caption>Every downtown holiday plan. Budgets are per person: free, $ under $25, $$ $25 to $60, $$$ over $60.</caption>
          <thead><tr><th scope="col">Plan</th><th scope="col">Best for</th><th scope="col">Time</th><th scope="col">Budget</th><th scope="col">Days</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </details>
    <p class="note" style="margin-top:1.5rem">Plans are ideas, not bookings. Hours, menus and event details change through the season, so check before you go. Budgets don’t include shopping, tickets or optional add-ons.</p>
  </div>
</section>{PLAN_JS}'''
    page('holidays/plan.html', 'Plan your day', body, 'holidays',
         f'Pick a day, a budget and who’s coming, and get downtown Kalamazoo holiday plans to print or share. {n} itineraries for families, couples, friends and visitors.')


def print_head(label, path):
    return (f'<div class="print-head print-only" aria-hidden="true"><img src="{{R}}dk-logo-green.png" alt="" width="120" height="92">'
            f'<div><strong>{E(label)}</strong><span>downtownkalamazoo.us/{E(path)}</span></div></div>')


def your_day_box(intro, kind):
    noun = 'plan' if kind == 'plan' else 'itinerary'
    return f'''<section class="your-day" id="yourday" aria-labelledby="yd-title">
        <h2 class="h2{"" if kind == "plan" else " no-print"}" id="yd-title">{"Your day" if kind == "plan" else "3. Pick a date and print"}</h2>{"" if kind == "plan" else '<h2 class="h2 print-only" aria-hidden="true">Your day</h2>'}
        <p class="no-print">{intro}</p>
        <div class="yd-grid">
          <div class="field no-print"><label for="yd-date">When are you going?</label><input type="date" id="yd-date" min="2026-11-01" max="2026-12-31" aria-describedby="yd-date-help"><p class="help" id="yd-date-help">Holiday events run November 6 to December 31, 2026.</p></div>
          <div class="field no-print"><label for="yd-note">A note for your group <span class="muted">(optional)</span></label><textarea id="yd-note" rows="3" maxlength="400" aria-describedby="yd-note-help" placeholder="Meet at City Hall at 5. Bring mittens."></textarea><p class="help" id="yd-note-help">It prints with the {noun}. It isn’t sent anywhere.</p></div>
        </div>
        <div class="yd-out" id="yd-out" aria-live="polite"></div>
        <div class="print-only yd-print"><p class="yd-pdate" id="yd-pdate">Date: ______________________</p><p class="yd-pnote" id="yd-pnote" hidden></p></div>
        <div class="btn-row no-print" style="margin-top:1rem"><button class="btn btn-primary" type="button" data-print-plan>Print this {noun}</button><button class="btn" type="button" data-share-plan>Share this {noun}</button><span class="share-done" role="status" aria-live="polite"></span></div>
      </section>'''


def parking_block(print_only=False):
    if not PARKING or not PARKING.get('items'):
        return ''
    items = ''.join(f'<li>{E(str(x))}</li>' for x in PARKING['items'])
    more = f'<p class="pk-more">{E(str(PARKING["more"]))}</p>' if PARKING.get('more') else ''
    cls = 'parking-block print-only' if print_only else 'parking-block'
    hid = ' aria-hidden="true"' if print_only else ''
    return (f'<section class="{cls}"{hid} aria-labelledby="pk-title{"-p" if print_only else ""}"><h2 class="h3" id="pk-title{"-p" if print_only else ""}">'
            f'<span class="pk-p" aria-hidden="true">P</span>{E(PARKING.get("title", "Parking"))}</h2><ul>{items}</ul>{more}</section>')


def _place_row(t):
    b = t['biz']
    street = re.sub(r',\s*Kalamazoo,\s*MI\s*\d{5}$', '', b['address']) if b['address'] else ''
    phone = f'<a href="{E(b["tel"])}">{E(b["phone"])}</a>' if b['tel'] else E(b['phone'])
    dd = '<span class="dd-badge"><span class="dd-coin" aria-hidden="true">$</span>Accepts Downtown Dollars</span>' if b['dd'] else ''
    facts = ''.join(f'<span>{x}</span>' for x in [E(street), phone] if x)
    return (f'<li class="{b["fill"]}"><span class="pl-cat">{E(b["cat_label"])}</span>'
            f'<a class="pl-name" href="{{R}}directory.html#b-{b["id"]}">{E(b["name"])}</a>'
            f'<span class="pl-facts">{facts}</span>{dd}</li>')


def _similar(p, k=3):
    def score(q):
        return (len(set(q['who']) & set(p['who'])) * 2 + (q['budget_key'] == p['budget_key']) + len(set(q['days']) & set(p['days'])) / 7)
    others = sorted((q for q in PLANS if q is not p), key=lambda q: (-score(q), q['title']))
    return others[:k]


def build_plan(i, p):
    glance = ''.join(f'<div><dt>{E(k)}</dt><dd>{v}</dd></div>' for k, v in [
        ('Best for', E(p['best_for'])), ('Time', E(p['time'])),
        ('Budget', f'{E(p["budget"])}{"" if p["budget_key"] == "free" else " · " + E(p["budget_text"])}<span class="g-sub">per person</span>'),
        ('Best days', E(p['when']))])
    stops = ''.join(f'<li class="stop"><span class="stop-n" aria-hidden="true">{n + 1}</span><div class="body"><p>{s}</p></div></li>' for n, s in enumerate(p['steps']))
    gifts = ''
    if p['gifts']:
        g = p['gifts']
        href = 'gifts.html' + (f'#{IT.GIFT_HASH[g]}' if IT.GIFT_HASH[g] else '')
        label = IT.GIFT_GUIDES[g]
        gifts = (f'<p class="gift-link"><span class="gl-ribbon" aria-hidden="true"></span>Shopping for someone? '
                 f'<a href="{{R}}{href}">{"See the Holiday Gift Guide" if g == "all" else "Holiday Gift Guide: " + E(label)}</a></p>')
    evs = ''.join(f'<li><a href="{{R}}events/{s}.html">{E(_EV[s]["title"])}</a> <span class="muted">{E(_EV[s]["when_short"])}</span></li>' for s in p['events'])
    tie = ''
    if p['holiday'] or evs:
        tie = '<h2 class="h3" style="margin-top:1.75rem">The holiday tie-in</h2>'
        if p['holiday']:
            tie += f'<p>{p["holiday"]}</p>'
        if evs:
            tie += f'<ul class="tie-events">{evs}</ul>'
    before = f'<p class="note"><strong>Before you go:</strong> {E(p["before"])}</p>' if p['before'] else ''
    places = ''
    if p['places']:
        places = (f'<section class="plan-places" aria-labelledby="places-title"><h2 class="h2" id="places-title">Places on this plan</h2>'
                  f'<p class="muted">Pick one, or try them all. Each name opens its listing in the business directory.</p>'
                  f'<ul class="place-list">{"".join(_place_row(t) for t in p["places"])}</ul></section>')
    sim = ''.join(f'<li><a href="{{R}}plan/{q["slug"]}.html">{E(q["title"])}</a> <span class="muted">{E(q["budget"])}, {E(q["time"].lower())}</span></li>' for q in _similar(p))
    pc_panel, pc_dialog = postcard_bits(i, p)
    data = json.dumps(dict(slug=p['slug'], title=p['title'], days=p['days'], when=p['when'], events=p['events'],
                           santa=IT.schedule_json(SANTA), trolley=IT.schedule_json(TROLLEY), all=_events_json(), season=SEASON),
                      ensure_ascii=False).replace('</', '<\\/')
    tools = ('<div class="btn-row plan-tools" style="margin-top:1.4rem">'
             '<button class="btn btn-primary" type="button" data-print-plan><svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M6 9V3h12v6"/><rect x="3" y="9" width="18" height="8" rx="2"/><path d="M6 14h12v7H6z"/></svg>Print this plan</button>'
             '<button class="btn" type="button" data-share-plan><svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 13.5 6.8 4M15.4 6.5l-6.8 4"/></svg>Share this plan</button>'
             '<a class="btn" href="{R}plan/build-your-own.html?from=' + p['slug'] + '">Change the stops</a>'
             '<span class="share-done" role="status" aria-live="polite"></span></div>')
    plain_line = f'This plan has {len(p["steps"])} stops. It is for {p["best_for"].lower()}. It takes {p["time"].lower()} and costs {p["budget_long"].lower()}.'
    body = page_hero([('index.html', 'Home'), ('plan.html', 'Plan your day'), (f'plan/{p["slug"]}.html', p['title'])],
                     f'Plan your day · {E(p["best_for"])}', E(p['title']), E(p['summary']), p['fill'], tools)
    body += f'''{PLAN_CSS}{print_head('Plan your day', 'holidays/plan/' + p['slug'] + '.html')}
<section class="section" aria-labelledby="glance-title"><div class="wrap"><h2 class="sr-only" id="glance-title">At a glance</h2><dl class="glance">{glance}</dl></div></section>
<section class="section" style="padding-top:0" aria-labelledby="stops-title">
  <div class="wrap two-col">
    <div class="prose plan-main" style="max-width:none">
      {in_short(E(plain_line))}
      <h2 class="h2" id="stops-title">The plan</h2>
      <ol class="timeline plan-steps">{stops}</ol>
      {gifts}
      {tie}
      {before}
      {your_day_box('Pick a date to see what’s on downtown that day, Santa’s Workshop and trolley hours included. Add a note for your group, then print or share.', 'plan')}
      {places}
      {parking_block(print_only=True)}
      <p class="print-only print-foot">Find more plans at downtownkalamazoo.us/holidays/plan.html · Plans are ideas, not bookings. Check hours before you go. · #SomethingNewKalamazoo</p>
    </div>
    <div class="aside no-print">
      {GETTING_HERE}
      {pc_panel}
      <section class="panel" aria-labelledby="sim-title"><h2 id="sim-title">More plans like this</h2><ul>{sim}</ul><p><a href="{{R}}plan/build-your-own.html?from={p["slug"]}">Swap stops in this plan</a></p><p><a href="{{R}}plan.html">Build a different day</a></p></section>
      {ACCOMMODATION}
    </div>
  </div>
</section>{pc_dialog}<script type="application/json" id="plan-data">{data}</script>{PLAN_JS}'''
    page(f'holidays/plan/{p["slug"]}.html', p['title'], body, 'holidays', p['summary'])


# ---------------------------------------------------------------- Build your own itinerary
BUILDER_PATH = 'holidays/plan/build-your-own.html'


def _builder_data():
    items = []
    for e in EVENTS:
        items.append(dict(k='e', id=e['slug'], n=e['title'], c='Holiday event', g='holiday', w=e['where_short'], when=e['when_short'],
                          date=e['date'], end=e.get('end') or e['date'], h=f'{{R}}events/{e["slug"]}.html', d=e['summary']))
    for x in IT.EXPERIENCES:
        h = x['h'] if (not x['h'] or x['h'].startswith('http')) else '{R}' + x['h']
        items.append(dict(k='x', id=x['id'], n=x['n'], c='Holiday experience', g='holiday', w=x['w'], h=h, d=x['d']))
    for b in [b for b in directory_page.BIZ if b['cat'] in directory_page.VISITOR_CATS]:
        street = re.sub(r',\s*Kalamazoo,\s*MI\s*\d{5}$', '', b['address']) if b['address'] else (b.get('where') or '')
        items.append(dict(k='b', id=b['id'], n=b['name'], c=b['cat_label'], g=b['cat'], w=street, ph=b['phone'], tel=b['tel'],
                          dd=bool(b['dd']), d=(b['desc'] or '')[:150], h=f'{{R}}directory.html#b-{b["id"]}'))
    plans = [dict(slug=p['slug'], title=p['title'], stops=IT.stop_keys(p)) for p in PLANS]
    return dict(items=items, plans=plans, days=IT.DAYS, when='any day', events=[], title='Build your own itinerary',
                santa=IT.schedule_json(SANTA), trolley=IT.schedule_json(TROLLEY), all=_events_json(), season=SEASON)


def build_builder():
    chips = [('all', 'Everything'), ('holiday', 'Holiday events & experiences')] + [(c, l) for c, l in directory_page.BIZ_CATS if c in directory_page.VISITOR_CATS] + [('dd', 'Takes Downtown Dollars')]
    chip_html = ''.join(f'<li><button type="button" class="chip" data-g="{c}" aria-pressed="{"true" if c == "all" else "false"}">{E(l)}</button></li>' for c, l in chips)
    plan_opts = ''.join(f'<option value="{p["slug"]}">{E(p["title"])}</option>' for p in PLANS)
    data = json.dumps(_builder_data(), ensure_ascii=False).replace('</', '<\\/')
    n_biz = sum(1 for b in directory_page.BIZ if b['cat'] in directory_page.VISITOR_CATS)
    body = page_hero([('index.html', 'Home'), ('plan.html', 'Plan your day'), ('plan/build-your-own.html', 'Build your own')],
                     'Plan your day', 'Build your own itinerary',
                     f'Pick your stops from {n_biz} downtown businesses and every holiday event, put them in order, and print your day with addresses, hours and parking.',
                     'f-pink')
    body += f'''{PLAN_CSS}{print_head('My downtown day', BUILDER_PATH)}
<h1 class="print-only b-ptitle" id="b-ptitle" aria-hidden="true">My downtown day</h1>
<section class="section builder" aria-label="Build your itinerary">
  <div class="wrap">
    {in_short('Search for places and events, then press Add. Your stops show up in “Your stops.” You can add a time to each one, move them up or down, or remove them. Then pick a date and print or share.')}
    <noscript><p class="note">This page needs JavaScript to build an itinerary. You can still <a href="{{R}}plan.html">browse our ready-made plans</a>.</p></noscript>
    <div class="b-grid">
      <div class="b-find no-print">
        <h2 class="h2" id="find-title">1. Add stops</h2>
        <p class="b-count"><span id="b-count-text">No stops yet.</span> <a href="#b-stops-title" class="b-jump">Jump to your stops</a></p>
        <div class="field"><label for="b-q">Search businesses and events</label><input type="search" id="b-q" autocomplete="off" placeholder="Bakery, Santa, Rose Street, gifts…" aria-controls="b-results"></div>
        <div role="group" aria-label="Show"><ul class="chips b-chips" id="b-chips">{chip_html}</ul></div>
        <p class="b-rcount" id="b-rcount" role="status" aria-live="polite"></p>
        <ul class="b-results" id="b-results" aria-labelledby="find-title"></ul>
        <p><button type="button" class="btn btn-small" id="b-moreres" hidden>Show more</button></p>
        <div class="b-extra">
          <form class="b-own" id="b-own" novalidate>
            <label for="b-own-n">Add your own stop</label>
            <p class="help" id="b-own-help">A place or a moment that isn’t listed, like “Meet at the fountain” or “Grandma’s house.”</p>
            <div class="b-row"><input type="text" id="b-own-n" maxlength="60" aria-describedby="b-own-help"><button type="submit" class="btn">Add</button></div>
          </form>
          <form class="b-own" id="b-from" novalidate>
            <label for="b-from-s">Or start from one of our plans</label>
            <p class="help" id="b-from-help">Its stops replace the ones you have.</p>
            <div class="b-row"><select id="b-from-s" aria-describedby="b-from-help"><option value="">Choose a plan</option>{plan_opts}</select><button type="submit" class="btn">Use its stops</button></div>
          </form>
        </div>
      </div>
      <div class="b-mine">
        <div class="b-mine-inner">
          <h2 class="h2 no-print" id="b-stops-title" tabindex="-1">2. Your stops</h2>
          <div class="field no-print"><label for="b-title">Name your day <span class="muted">(optional)</span></label><input type="text" id="b-title" maxlength="60" placeholder="Our holiday Saturday"></div>
          <p class="b-empty" id="b-empty">Nothing here yet. Add a few stops from the list.</p>
          <ol class="b-stops" id="b-stops" aria-labelledby="b-stops-title"></ol>
          <p class="b-live sr-only" id="b-live" role="status" aria-live="polite"></p>
          <p class="no-print"><button type="button" class="btn btn-small btn-quiet" id="b-clear" hidden>Remove all stops</button></p>
        </div>
      </div>
    </div>
    <div class="b-day">
      {your_day_box('Pick a date to see what’s on downtown that day, including Santa’s Workshop and trolley hours. Add a note, then print or share. Your stops are saved in this browser until you clear them.', 'build')}
      {parking_block()}
      <p class="print-only print-foot">Made at downtownkalamazoo.us/holidays/plan/build-your-own.html · Check hours before you go. · #SomethingNewKalamazoo</p>
    </div>
  </div>
</section>
<script type="application/json" id="builder-data">{data}</script>{PLAN_JS}'''
    page(BUILDER_PATH, 'Build your own itinerary', body, 'holidays',
         'Build your own downtown Kalamazoo holiday itinerary from local shops, restaurants and holiday events, then print it with parking details or share it.')
