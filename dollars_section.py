# Downtown Dollars page (dollars.html). Pulled into build.py with exec(), so it shares build.py's names
# (page, page_hero, in_short, ext, E, directory_page, HUB_TODAY).
# Numbers, the seasonal reminder and the video come from content/dollars.yml.
# The list of businesses comes from the business directory (the "dd" flag).

def _dd_k(n):
    """$392K style, rounded down so it always reads as 'more than'."""
    return f'${n // 1000:,}K'


def _dd_video(v):
    """The How it works video, or '' until content/dollars.yml has one. Never autoplays; captions and transcript required."""
    if not v.get('file'):
        return ''
    length = f'<span class="muted">{E(str(v.get("length") or ""))}, with captions</span>' if v.get('length') else ''
    paras = ''.join(f'<p>{E(p.strip())}</p>' for p in str(v['transcript']).split('\n\n') if p.strip())
    return f'''<figure class="dd-video" aria-labelledby="video-cap">
      <div class="dd-video-frame">
        <video controls preload="none" playsinline poster="{{R}}{E(v["poster"])}" aria-describedby="video-cap">
          <source src="{{R}}{E(v["file"])}" type="video/mp4">
          <track kind="captions" srclang="en" label="English" src="{{R}}{E(v["captions"])}" default>
          <a href="{{R}}{E(v["file"])}">Download the video</a>
        </video>
      </div>
      <figcaption id="video-cap"><span>How Downtown Dollars work</span> {length}</figcaption>
      <details class="dd-transcript"><summary>Read the transcript</summary><div>{paras}</div></details>
    </figure>'''


def build_dollars():
    city = 'https://kalamazoocity.org/Community/Downtown-Kalamazoo/Downtown-Dollars'
    mapu = 'https://apps.conpoto.com/members/3725acad-1c4a-4e38-b149-3ee431751939/merchants/publicMap'
    d = _CL.dollars()
    accept = [b for b in directory_page.BIZ if b.get('dd')]
    pat = directory_page.CAT_PATTERN
    sw = lambda c: f'<span class="dd-sw" style="background-image:url({{R}}pattern-{pat[c]}-sm.webp)" aria-hidden="true"></span>'

    hero_extra = (f'<div class="btn-row" style="margin-top:1.25rem">{ext(city, "Buy Downtown Dollars", "btn btn-primary")}'
                  f'<a class="btn" href="#where-title">See where they’re accepted</a></div>')
    body = page_hero([('index.html', 'Home'), ('dollars.html', 'Downtown Dollars')], 'The gift that stays downtown', 'Downtown Dollars',
                     f'Digital gift certificates for downtown shops, restaurants and studios. Since {d["since"]}, more than '
                     f'${d["spent"] // 10000 * 10000:,} has been spent at downtown businesses.', 'f-blue', hero_extra)

    # Seasonal reminder
    rem = d.get('reminder') or {}
    if rem.get('text') and rem.get('show_from') and rem.get('show_until') and rem['show_from'] <= HUB_TODAY <= rem['show_until']:
        body += f'''<aside class="dd-reminder" aria-label="Reminder">
  <div class="wrap"><span class="dd-reminder-icon" aria-hidden="true"></span><p><strong>Spend them soon.</strong> {E(rem["text"])} <a href="#where-title">Where to spend them</a></p></div>
</aside>'''

    # 1. Follow a Downtown Dollar
    steps = [
        ('f-blue', 'Bought', _dd_k(d['bought']), f'in Downtown Dollars bought by neighbors, families and local employers since {d["since"]}.'),
        ('f-pink', 'Given', E(str(d['recipients'])), 'people have opened an email with Downtown Dollars inside.'),
        ('f-green', 'Spent', f'{d["half_spent_weeks"]} <small>weeks</small>', 'is all it takes for half of all certificates to be spent. Gifts don’t sit in a drawer.'),
        ('f-sky', 'Landed', _dd_k(d['spent']), f'spent at {d["businesses"]} downtown shops, restaurants and studios.'),
    ]
    stops = ''.join(f'<li class="{f}"><h3 class="dd-verb"><span class="dd-num">{i}</span>{v}</h3>'
                    f'<p class="dd-n">{n}</p><p>{E(t)}</p></li>' for i, (f, v, n, t) in enumerate(steps, 1))
    body += f'''<section class="section dd-journey" aria-labelledby="journey-title">
  <div class="wrap">
    {in_short(f'Since {d["since"]}, {_dd_k(d["bought"])} in Downtown Dollars has been bought, and {_dd_k(d["spent"])} has been spent at downtown businesses. Half of all certificates are spent within {d["half_spent_weeks"]} weeks.')}
    <h2 class="h2" id="journey-title">Follow a Downtown Dollar</h2>
    <p class="dd-intro">Every certificate makes the same trip: from someone who cares, to someone they care about, to a business down the street.</p>
    <ol class="dd-route">{stops}</ol>
    <p class="dd-source">Program totals from {d["since"]} through {E(str(d["through"]))}. <a href="#numbers-title">See the numbers</a></p>
  </div>
</section>'''

    # 2. How it works, with the video when there is one
    video = _dd_video(d['video'])
    body += f'''<section class="section dd-how" aria-labelledby="how-title">
  <div class="wrap{' dd-how-grid' if video else ''}">
    {video}
    <div>
      <h2 class="h2" id="how-title">How it works</h2>
      <ol class="dd-steps{' dd-steps-row' if not video else ''}">
        <li><h3>Buy online</h3><p>Choose your amount on the City of Kalamazoo’s order page.</p></li>
        <li><h3>Get them by email</h3><p>Certificates arrive by email, ready to forward as a gift or print.</p></li>
        <li><h3>Spend downtown</h3><p>Show them on your phone or on paper at any participating business. They’re good for five years.</p></li>
      </ol>
      <div class="btn-row">{ext(city, "Buy Downtown Dollars", "btn btn-primary")}</div>
    </div>
  </div>
</section>'''

    # 3. Where it lands
    split = d.get('split') or []
    if split:
        bill = ''.join(f'<span class="dd-seg" style="flex:{x["cents"]};background-image:url({{R}}pattern-{pat[x["kind"]]}-sm.webp)">'
                       + (f'<b>{x["cents"]}¢</b>' if x['cents'] >= 15 else '') + '</span>' for x in split)
        legend = ''.join(f'<li><span class="dd-swatch" style="background-image:url({{R}}pattern-{pat[x["kind"]]}-sm.webp)" aria-hidden="true"></span>'
                         f'<span><b>{x["cents"]}¢</b> {E(x["label"])}</span></li>' for x in split)
        facts = ''
        if d.get('mall_share'):
            facts += f'<p><span class="dd-fact-n">{E(str(d["mall_share"]))}</span> is spent on the Kalamazoo Mall.</p>'
        if d.get('typical'):
            facts += f'<p><span class="dd-fact-n">{E(str(d["typical"]))}</span> is what the typical participating business has welcomed in Downtown Dollars.</p>'
        body += f'''<section class="section band dd-lands" aria-labelledby="lands-title">
  <div class="wrap">
    <h2 class="h2" id="lands-title">Where it lands</h2>
    <p class="dd-intro">Out of every Downtown Dollar spent:</p>
    <div class="dd-bill" aria-hidden="true"><span class="dd-bill-k">$1</span><div class="dd-bill-bar">{bill}</div></div>
    <ul class="dd-legend">{legend}</ul>
    <div class="dd-facts">{facts}</div>
  </div>
</section>'''

    # 4. Where to spend them: one group per kind of business. Without JavaScript every group shows;
    # with it (site.js), the buttons show one kind at a time.
    cats = [(c, l, [b for b in accept if b['cat'] == c]) for c, l in directory_page.BIZ_CATS]
    cats = [x for x in cats if x[2]]
    btns = (f'<button class="dd-tab" type="button" data-cat="all" aria-pressed="true">All <span>{len(accept)}</span></button>'
            + ''.join(f'<button class="dd-tab" type="button" data-cat="{c}" data-noun="{E(l)}" aria-pressed="false">{sw(c)}{E(l)} <span>{len(bs)}</span></button>'
                      for c, l, bs in cats))
    groups = ''
    for c, l, bs in cats:
        rows = ''.join(f'<li><a href="{{R}}directory.html#b-{b["id"]}">{E(b["name"])}</a><span class="muted">{E(b["where"])}</span></li>' for b in bs)
        groups += (f'<div class="dd-cat" data-cat="{c}"><h3 class="dd-cat-h">{sw(c)}{E(l)} <span class="muted">({len(bs)})</span></h3>'
                   f'<ul class="dd-tabpanel">{rows}</ul></div>')
    body += f'''<section class="section dd-where" aria-labelledby="where-title">
  <div class="wrap">
    <h2 class="h2" id="where-title">Where to spend them</h2>
    <p class="dd-intro">{len(accept)} downtown businesses accept Downtown Dollars. Pick a kind of place, then choose a name to see its address, hours and contact details.</p>
    <div class="dd-tabs" role="group" aria-label="Show businesses by kind" hidden>{btns}</div>
    <p class="sr-only" id="dd-where-status" role="status" aria-live="polite"></p>
    <div class="dd-cats">{groups}</div>
    <p class="btn-row" style="margin-top:1.5rem"><a class="btn" href="{{R}}directory.html#dollars">Open them in the directory</a></p>
  </div>
</section>'''

    # 5. Questions, plus the numbers
    faqs = [
        ('Where can I use them?', f'<p>At the participating businesses listed above. In the <a href="{{R}}directory.html#dollars">business directory</a>, look for the Accepts Downtown Dollars tag. The {ext(mapu, "Downtown Dollars merchant map")} has the official list.</p>'),
        ('How long are they good for?', '<p>Five years from the date you buy them. Promotional certificates may expire sooner, and the expiration date is printed on each one.</p>'),
        ('Do I need to print them?', '<p>No. You can show them on your phone or print them, whichever is easier.</p>'),
        ('Can I buy a lot at once for my team or clients?', '<p>Yes. For orders of $1,000 or more, email downtown@kalamazoocity.org and the downtown team will help.</p>'),
        ('Who do I contact with a problem?', '<p>Email downtown@kalamazoocity.org, call 311, or call (269) 337-8000.</p>'),
    ]
    faq_html = ''.join(f'<details><summary>{E(q)}</summary><div>{a}</div></details>' for q, a in faqs)
    months = d.get('months') or []
    year_panel = ''
    if months:
        rows = ''.join(f'<tr><th scope="row">{E(str(m["month"]))}</th><td class="num">{m["businesses"]}</td><td class="num">${m["bought"]:,}</td><td class="num">${m["spent"]:,}</td></tr>' for m in months)
        ts, tp = sum(m['bought'] for m in months), sum(m['spent'] for m in months)
        year_panel = f'''<details><summary>{d["year"]} so far, month by month</summary><div>
        <div class="table-wrap" tabindex="0" role="region" aria-label="{d['year']} monthly numbers"><table class="dd-table">
          <caption class="sr-only">Downtown Dollars in {d["year"]} by month</caption>
          <thead><tr><th scope="col">Month</th><th scope="col">Businesses that welcomed them</th><th scope="col">Bought</th><th scope="col">Spent</th></tr></thead>
          <tbody>{rows}</tbody>
          <tfoot><tr><th scope="row">{d["year"]} so far</th><td class="num">{d.get("year_businesses", "")}</td><td class="num">${ts:,}</td><td class="num">${tp:,}</td></tr></tfoot></table></div>
      </div></details>'''
    body += f'''<section class="section" aria-labelledby="faq-title">
  <div class="wrap two-col">
    <div>
      <h2 class="h2" id="faq-title" style="margin-bottom:1rem">Questions</h2>{faq_html}
      <h2 class="h2" id="numbers-title" style="margin:2.5rem 0 1rem">The numbers</h2>
      <details><summary>Downtown Dollars since {d["since"]}</summary><div>
        <table class="dd-table"><caption class="sr-only">Downtown Dollars since {d["since"]}</caption>
          <tbody><tr><th scope="row">Bought</th><td class="num">${d["bought"]:,}</td></tr>
          <tr><th scope="row">Spent at downtown businesses</th><td class="num">${d["spent"]:,}</td></tr>
          <tr><th scope="row">Still waiting to be spent</th><td class="num">${d["waiting"]:,}</td></tr></tbody></table>
        <p class="muted">From {d["since"]} through {E(str(d["through"]))}.</p></div></details>
      {year_panel}
    </div>
    <div class="aside">
      <section class="panel f-blue"><h2>Last-minute gift</h2><p>Because they arrive by email, Downtown Dollars still work on Christmas Eve. See <a href="{{R}}plan/last-minute.html">A last-minute downtown outing</a>.</p></section>
      <section class="panel"><h2>Businesses</h2><p>Want to accept Downtown Dollars? See <a href="{{R}}businesses.html">For businesses</a>.</p></section>
    </div>
  </div>
</section>'''
    page('dollars.html', 'Downtown Dollars', body, 'dollars', 'Downtown Dollars: digital gift certificates for Downtown Kalamazoo businesses.')
