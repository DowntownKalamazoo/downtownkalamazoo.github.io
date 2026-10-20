(() => {
  'use strict';
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
  const DAYS = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
  const DAY_NAME = { mon: 'Monday', tue: 'Tuesday', wed: 'Wednesday', thu: 'Thursday', fri: 'Friday', sat: 'Saturday', sun: 'Sunday' };
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const iso = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  const parse = s => { const [y, m, d] = s.split('-').map(Number); return new Date(y, m - 1, d); };
  const shuffle = a => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };

  /* ---------------- The planner (holidays/plan.html) ---------------- */
  const form = $('#planner');
  if (form) {
    const list = $('#plan-cards'), status = $('#pf-status'), more = $('#pf-more');
    const plans = $$('#plan-cards > li').map(li => ({
      li, slug: li.dataset.slug, days: li.dataset.days.split(' '), budget: li.dataset.budget, who: li.dataset.who.split(' '),
      daysText: li.dataset.daysText, budgetText: li.dataset.budgetText, best: li.dataset.best,
      title: $('h3', li).textContent.trim(),
    }));
    const GROUPS = ['day', 'budget', 'who'];
    const fits = (p, g, vals) => !vals.length || (g === 'day' ? vals.some(v => p.days.includes(v)) : g === 'budget' ? vals.includes(p.budget) : vals.some(v => p.who.includes(v)));
    const chosen = () => Object.fromEntries(GROUPS.map(g => [g, $$(`input[name="${g}"]:checked`, form).map(i => i.value)]));
    const why = (p, g) => g === 'day' ? `Best on ${p.daysText}` : g === 'budget' ? (p.budget === 'free' ? 'Free' : `Budget: ${p.budgetText.toLowerCase()} per person`) : `Best for ${p.best.toLowerCase()}`;
    let order = [], at = 0, lastKey = null;

    function counts(s) {
      $$('input', form).forEach(inp => {
        const g = inp.name;
        const n = plans.filter(p => GROUPS.every(h => h === g ? fits(p, g, [inp.value]) : fits(p, h, s[h]))).length;
        const label = inp.closest('.pick');
        $('.n', label).innerHTML = `<span class="sr-only">, </span>${n}<span class="sr-only"> ${n === 1 ? 'plan' : 'plans'}</span>`;
        label.classList.toggle('is-zero', n === 0);
      });
    }

    function linkFor(href, s) {
      const u = new URL(href, location.href);
      u.search = '';
      if (s.day.length) u.searchParams.set('day', s.day[0]);
      return u;
    }

    function render(mode) {
      const s = chosen();
      const key = JSON.stringify(s);
      counts(s);
      const exact = plans.filter(p => GROUPS.every(g => fits(p, g, s[g])));
      if (key !== lastKey) { order = shuffle(exact); at = 0; lastKey = key; }
      else if (mode === 'more') { at += 3; if (at >= order.length) { const prev = order.slice(-3); order = shuffle(exact); if (order.length > 3 && prev.includes(order[0])) order.push(order.shift()); at = 0; } }
      const picks = order.slice(at, at + 3).map(p => ({ p, miss: null }));
      if (picks.length < 3) {
        const active = GROUPS.filter(g => s[g].length);
        const near = plans.filter(p => !exact.includes(p)).map(p => ({ p, miss: active.filter(g => !fits(p, g, s[g])) })).filter(x => x.miss.length === 1);
        // Closest first: a different day, then a different budget, then a different crowd.
        const rank = { day: 0, budget: 1, who: 2 };
        shuffle(near).sort((a, b) => rank[a.miss[0]] - rank[b.miss[0]]).slice(0, 3 - picks.length).forEach(x => picks.push({ p: x.p, miss: x.miss[0] }));
      }
      plans.forEach(p => { p.li.hidden = true; p.li.classList.remove('is-new'); });
      picks.forEach(({ p, miss }) => {
        list.appendChild(p.li);
        p.li.hidden = false;
        void p.li.offsetWidth;
        p.li.classList.add('is-new');
        const note = $('.pc-close', p.li);
        note.hidden = !miss;
        note.textContent = miss ? `Close match · ${why(p, miss)}` : '';
        $$('[data-plan-link]', p.li).forEach(a => {
          const u = linkFor(a.getAttribute('href'), s);
          if (a.hasAttribute('data-print')) u.searchParams.set('print', '1');
          a.href = u.href;
        });
      });
      const n = exact.length, shownExact = picks.filter(x => !x.miss).length, close = picks.length - shownExact;
      const any = GROUPS.every(g => !s[g].length);
      let msg;
      if (any) msg = `Here are 3 of all ${plans.length} plans, picked at random. Narrow it down above, or press “Show me three more.”`;
      else if (n === 0) msg = picks.length ? `No plan fits all of that, so here ${picks.length === 1 ? 'is a close match' : `are ${picks.length} close matches`}. Try fewer choices for more.` : 'Nothing fits all of that yet. Try fewer choices.';
      else if (n <= 3) msg = `${n === 1 ? 'One plan fits' : `${n} plans fit`} everything you picked${close ? `, plus ${close === 1 ? 'a close match' : `${close} close matches`}` : ''}.`;
      else msg = `${n} plans fit. Showing ${at + 1} to ${Math.min(at + 3, n)}, picked at random.`;
      status.textContent = msg;
      more.disabled = !any && n <= 3 && close === 0;
      const q = new URLSearchParams();
      GROUPS.forEach(g => { if (s[g].length) q.set(g, s[g].join(',')); });
      try { history.replaceState(null, '', q.toString() ? `?${q}` : location.pathname); } catch (e) {}
    }

    const q = new URLSearchParams(location.search);
    GROUPS.forEach(g => (q.get(g) || '').split(',').forEach(v => { const i = $(`input[name="${g}"][value="${CSS.escape(v)}"]`, form); if (i) i.checked = true; }));
    form.addEventListener('change', () => render('new'));
    form.addEventListener('submit', e => e.preventDefault());
    form.addEventListener('reset', () => setTimeout(() => render('new'), 0));
    more.addEventListener('click', () => render('more'));
    render('new');
  }

  /* ---------------- "Your day": date, note, hours, print and share (plan pages and the builder) ---------------- */
  const fmt = d => d.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
  const fmtShort = s => parse(s).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  const today = iso(new Date());

  function setupDay(P, opts = {}) {
    const dateIn = $('#yd-date'), noteIn = $('#yd-note'), out = $('#yd-out'), pdate = $('#yd-pdate'), pnote = $('#yd-pnote');
    if (!dateIn) return null;
    const hoursFor = (sch, d) => {
      const k = iso(d);
      if (sch.special && sch.special[k]) return sch.special[k];
      if (sch.opens && k < sch.opens) return `Not open yet. Starts ${fmtShort(sch.opens)}.`;
      if (sch.closes && k > sch.closes) return 'Closed for the season';
      return (sch.hours && sch.hours[DAYS[d.getDay()]]) || 'Not open this day';
    };
    const syncUrl = v => {
      const u = new URL(location.href);
      u.searchParams.delete('day'); u.searchParams.delete('print'); u.searchParams.delete('from');
      if (v) u.searchParams.set('date', v); else u.searchParams.delete('date');
      if (opts.params) opts.params(u.searchParams);
      try { history.replaceState(null, '', u.pathname + (u.search || '')); } catch (e) {}
    };
    function show() {
      const v = dateIn.value;
      if (!v) { out.innerHTML = ''; pdate.hidden = false; syncUrl(''); if (opts.onDate) opts.onDate(''); return; }
      const d = parse(v), wd = DAYS[d.getDay()];
      const evs = P.all.filter(e => v >= e.date && v <= e.end);
      const evHtml = evs.length ? evs.map(e => `<a href="${esc(e.href)}">${esc(e.title)}</a>${e.time && e.date === e.end ? `, ${esc(e.time)}` : ''}`).join('<br>') : 'None scheduled. Shops and restaurants keep their usual hours.';
      let html = `<p class="yd-when">${esc(fmt(d))}</p><ul class="yd-list">`;
      html += `<li><span class="yd-k">Holiday events</span><span>${evHtml}</span></li>`;
      [P.santa, P.trolley].forEach(sch => { if (sch) html += `<li><span class="yd-k">${esc(sch.name)}</span><span>${esc(hoursFor(sch, d))}<br><span class="muted">${esc(sch.where)}</span></span></li>`; });
      html += '</ul>';
      const notes = [];
      if (v < P.season[0] || v > P.season[1]) notes.push(`Holiday events run ${fmtShort(P.season[0])} to ${fmtShort(P.season[1])}, 2026.`);
      if (!P.days.includes(wd)) notes.push(`This plan works best: ${P.when}.`);
      if (opts.dateNotes) notes.push(...opts.dateNotes(v));
      if (notes.length) html += `<p class="note">${notes.map(esc).join(' ')}</p>`;
      html += '<p class="muted" style="font-size:.85rem">Planned hours. Check before you go.</p>';
      out.innerHTML = html;
      pdate.hidden = true;
      syncUrl(v);
      if (opts.onDate) opts.onDate(v);
    }
    const q = new URLSearchParams(location.search);
    let start = q.get('date') && /^\d{4}-\d{2}-\d{2}$/.test(q.get('date')) ? q.get('date') : '';
    const wantDay = q.get('day');
    if (!start && opts.startDate) start = opts.startDate() || '';
    if (!start) {
      const from = today > P.season[0] ? today : P.season[0];
      const evDates = P.all.filter(e => P.events.includes(e.slug) && e.date >= today && e.date === e.end).map(e => e.date).sort();
      const okDay = s => { const wd = DAYS[parse(s).getDay()]; return (wantDay ? wd === wantDay : true) && P.days.includes(wd); };
      if (P.days.length < 7) start = evDates.find(okDay) || '';
      if (!start && wantDay && DAYS.includes(wantDay)) {
        const d = parse(from);
        while (DAYS[d.getDay()] !== wantDay) d.setDate(d.getDate() + 1);
        if (iso(d) <= P.season[1]) start = iso(d);
      }
    }
    if (start) dateIn.value = start;
    dateIn.addEventListener('change', show);
    dateIn.addEventListener('input', show);
    const syncNote = () => { pnote.textContent = noteIn.value ? `Note: ${noteIn.value}` : ''; pnote.hidden = !noteIn.value; if (opts.onNote) opts.onNote(noteIn.value); };
    if (opts.startNote) { noteIn.value = opts.startNote() || ''; }
    noteIn.addEventListener('input', syncNote);
    syncNote();
    show();

    const say = (btn, msg) => { const done = $('.share-done', btn.parentElement); if (done) { done.textContent = msg; setTimeout(() => { done.textContent = ''; }, 6000); } };
    $$('[data-print-plan]').forEach(b => b.addEventListener('click', () => {
      if (opts.canPrint && !opts.canPrint()) { say(b, 'Add at least one stop first.'); return; }
      window.print();
    }));
    $$('[data-share-plan]').forEach(b => b.addEventListener('click', async () => {
      if (opts.canPrint && !opts.canPrint()) { say(b, 'Add at least one stop first.'); return; }
      syncUrl(dateIn.value);
      const url = location.href, title = opts.title ? opts.title() : P.title;
      const text = `Our downtown Kalamazoo plan: ${title}${dateIn.value ? ` on ${fmt(parse(dateIn.value))}` : ''}`;
      if (navigator.share) { try { await navigator.share({ title, text, url }); return; } catch (e) { if (e && e.name === 'AbortError') return; } }
      try { await navigator.clipboard.writeText(url); say(b, 'Link copied. Paste it in a text or email.'); }
      catch (e) { say(b, `Copy this link: ${url}`); }
    }));
    if (q.get('print') === '1') {
      const go = () => setTimeout(() => window.print(), 250);
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(go); else window.addEventListener('load', go);
    }
    return { date: () => dateIn.value, refresh: () => syncUrl(dateIn.value), show };
  }

  /* ---------------- A plan page (holidays/plan/<slug>.html) ---------------- */
  const dataEl = $('#plan-data');
  if (dataEl) {
    let P = null;
    try { P = JSON.parse(dataEl.textContent); } catch (e) {}
    if (P) setupDay(P);
  }

  /* ---------------- Build your own itinerary (holidays/plan/build-your-own.html) ---------------- */
  const bEl = $('#builder-data');
  if (bEl) {
    let B = null;
    try { B = JSON.parse(bEl.textContent); } catch (e) {}
    if (B) builder(B);
  }

  function builder(B) {
    const KEY = 'dk-build-v1', MAX = 15, PAGE = 12;
    const byKey = new Map(B.items.map(it => [`${it.k}:${it.id}`, it]));
    const fold = s => String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[‘’ʼ]/g, "'");
    B.items.forEach(it => { it.key = `${it.k}:${it.id}`; it.s = fold([it.n, it.c, it.w, it.d, it.dd ? 'downtown dollars' : ''].join(' ')); });
    const q = $('#b-q'), chips = $$('#b-chips .chip'), results = $('#b-results'), rcount = $('#b-rcount'), moreBtn = $('#b-moreres');
    const list = $('#b-stops'), empty = $('#b-empty'), live = $('#b-live'), clearBtn = $('#b-clear'), titleIn = $('#b-title');
    const countText = $('#b-count-text'), ptitle = $('#b-ptitle');
    let stops = [], group = 'all', limit = PAGE, saved = {};

    const fmtTime = t => { if (!t) return ''; const [h, m] = t.split(':').map(Number); const ap = h >= 12 ? 'p.m.' : 'a.m.'; const h12 = h % 12 || 12; return m ? `${h12}:${String(m).padStart(2, '0')} ${ap}` : `${h12} ${ap}`; };
    const nameOf = st => st.k === 'c' ? st.n : (byKey.get(`${st.k}:${st.id}`) || {}).n || '';
    const has = key => stops.some(st => `${st.k}:${st.id}` === key);
    const clean = s => String(s || '').replace(/[|~]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 60);

    // Stops travel in the link as  stops=b:sarkozy-bakery~14:30|e:tree-lighting|c:Meet at the fountain
    const encode = () => stops.map(st => (st.k === 'c' ? `c:${st.n}` : `${st.k}:${st.id}`) + (st.t ? `~${st.t}` : '')).join('|');
    const decode = str => String(str || '').split('|').map(part => {
      const [main, t] = part.split('~'); const i = main.indexOf(':'); if (i < 1) return null;
      const k = main.slice(0, i), rest = main.slice(i + 1), time = /^\d{2}:\d{2}$/.test(t || '') ? t : '';
      if (k === 'c') return rest.trim() ? { k, id: 'c' + Math.random().toString(36).slice(2, 8), n: clean(rest), t: time } : null;
      return byKey.has(`${k}:${rest}`) ? { k, id: rest, t: time } : null;
    }).filter(Boolean).slice(0, MAX);

    function persist() {
      try { localStorage.setItem(KEY, JSON.stringify({ stops: encode(), title: titleIn.value, note: $('#yd-note').value, date: day ? day.date() : '' })); } catch (e) {}
      if (day) day.refresh();
    }
    function params(sp) {
      if (stops.length) sp.set('stops', encode()); else sp.delete('stops');
      if (titleIn.value.trim()) sp.set('title', titleIn.value.trim()); else sp.delete('title');
    }

    function drawResults() {
      const term = fold(q.value.trim());
      const words = term.split(/\s+/).filter(Boolean);
      const hits = B.items.filter(it => !(it.k === 'e' && it.end < today) && (group === 'all' || (group === 'dd' ? it.dd : it.g === group)) && words.every(w => it.s.includes(w)));
      results.innerHTML = '';
      hits.slice(0, limit).forEach(it => {
        const li = document.createElement('li');
        li.className = 'b-res';
        const added = has(it.key);
        li.innerHTML = `<div class="b-res-body"><span class="pl-cat">${esc(it.c)}</span>`
          + `<span class="b-res-name">${it.h ? `<a href="${esc(it.h)}"${/^https?:/.test(it.h) ? ' target="_blank" rel="noopener"' : ''}>${esc(it.n)}${/^https?:/.test(it.h) ? '<span class="sr-only"> (opens in a new tab)</span>' : ''}</a>` : esc(it.n)}</span>`
          + `<span class="b-res-where">${esc(it.when ? `${it.when} · ${it.w}` : it.w)}</span>`
          + (it.dd ? '<span class="dd-badge"><span class="dd-coin" aria-hidden="true">$</span>Accepts Downtown Dollars</span>' : '')
          + `</div><button type="button" class="btn btn-small ${added ? 'is-added' : 'btn-primary'}" data-key="${esc(it.key)}" aria-pressed="${added}">`
          + `${added ? 'Added' : 'Add'}<span class="sr-only"> ${esc(it.n)} ${added ? '(press to remove)' : 'to your day'}</span></button>`;
        results.appendChild(li);
      });
      const n = hits.length;
      rcount.textContent = n ? `${n} ${n === 1 ? 'match' : 'matches'}${n > limit ? `, showing ${limit}` : ''}` : 'No matches. Try another word, or add your own stop below.';
      moreBtn.hidden = n <= limit;
    }

    function drawStops(focus) {
      list.innerHTML = '';
      stops.forEach((st, i) => {
        const it = st.k === 'c' ? null : byKey.get(`${st.k}:${st.id}`);
        const name = nameOf(st), uid = `st-${i}`;
        const li = document.createElement('li');
        li.className = 'b-stop' + (it && it.k === 'b' ? '' : ' is-holiday');
        const where = it ? (it.when ? `${it.when} · ${it.w}` : it.w) : '';
        const facts = [where, it && it.ph ? it.ph : ''].filter(Boolean).map(esc).join('<br>');
        li.innerHTML = `<span class="stop-n" aria-hidden="true">${i + 1}</span>`
          + `<div class="b-stop-body"><span class="b-ptime print-only">${esc(fmtTime(st.t))}</span><span class="pl-cat">${esc(it ? it.c : 'Your stop')}</span>`
          + `<span class="b-stop-name">${it && it.h ? `<a href="${esc(it.h)}">${esc(name)}</a>` : esc(name)}</span>`
          + (facts ? `<span class="b-stop-where">${facts}</span>` : '')
          + (it && it.dd ? '<span class="dd-badge"><span class="dd-coin" aria-hidden="true">$</span>Accepts Downtown Dollars</span>' : '') + '</div>'
          + `<div class="b-stop-ctrl no-print"><label class="b-tlabel" for="${uid}-t">Time<span class="sr-only"> for ${esc(name)}</span></label><input type="time" id="${uid}-t" value="${esc(st.t || '')}" step="900">`
          + `<button type="button" class="icon-btn" data-act="up" data-i="${i}" ${i === 0 ? 'disabled' : ''} aria-label="Move ${esc(name)} earlier"><svg aria-hidden="true" width="16" height="16" viewBox="0 0 16 16"><path d="M3 10l5-5 5 5" fill="none" stroke="currentColor" stroke-width="2"/></svg></button>`
          + `<button type="button" class="icon-btn" data-act="down" data-i="${i}" ${i === stops.length - 1 ? 'disabled' : ''} aria-label="Move ${esc(name)} later"><svg aria-hidden="true" width="16" height="16" viewBox="0 0 16 16"><path d="M3 6l5 5 5-5" fill="none" stroke="currentColor" stroke-width="2"/></svg></button>`
          + `<button type="button" class="icon-btn" data-act="remove" data-i="${i}" aria-label="Remove ${esc(name)}">✕</button></div>`;
        $('input', li).addEventListener('change', e => { st.t = e.target.value; li.querySelector('.b-ptime').textContent = fmtTime(st.t); persist(); });
        list.appendChild(li);
      });
      empty.hidden = stops.length > 0;
      clearBtn.hidden = stops.length === 0;
      countText.textContent = stops.length ? `${stops.length} ${stops.length === 1 ? 'stop' : 'stops'} in your day.` : 'No stops yet.';
      if (focus) {
        const [i, act] = focus;
        const row = list.children[Math.min(i, stops.length - 1)];
        let target = row && $(`[data-act="${act}"]`, row);
        if (target && target.disabled) target = $(`[data-act="${act === 'up' ? 'down' : 'up'}"]`, row);
        if (target && !target.disabled) target.focus(); else if (!row) $('#b-stops-title').focus();
      }
      if (day) day.show(); else persist();
    }

    function add(st, announce = true) {
      if (stops.length >= MAX) { live.textContent = `Your day has the most stops it can hold, ${MAX}. Remove one to add another.`; return false; }
      stops.push(st);
      if (announce) live.textContent = `Added ${nameOf(st)}. Stop ${stops.length}.`;
      return true;
    }

    results.addEventListener('click', e => {
      const b = e.target.closest('button[data-key]'); if (!b) return;
      const key = b.dataset.key, i = key.indexOf(':');
      const idx = stops.findIndex(st => `${st.k}:${st.id}` === key);
      if (idx >= 0) { const [gone] = stops.splice(idx, 1); live.textContent = `Removed ${nameOf(gone)}.`; }
      else add({ k: key.slice(0, i), id: key.slice(i + 1), t: '' });
      drawStops(); drawResults();
      const again = $(`button[data-key="${CSS.escape(key)}"]`, results); if (again) again.focus();
    });
    list.addEventListener('click', e => {
      const b = e.target.closest('button[data-act]'); if (!b) return;
      const i = Number(b.dataset.i), act = b.dataset.act, name = nameOf(stops[i]);
      if (act === 'remove') { stops.splice(i, 1); live.textContent = `Removed ${name}.`; drawStops([i, 'remove']); drawResults(); return; }
      const j = act === 'up' ? i - 1 : i + 1;
      if (j < 0 || j >= stops.length) return;
      [stops[i], stops[j]] = [stops[j], stops[i]];
      live.textContent = `${name} is now stop ${j + 1} of ${stops.length}.`;
      drawStops([j, act]);
    });
    clearBtn.addEventListener('click', () => { stops = []; live.textContent = 'All stops removed.'; drawStops(); drawResults(); q.focus(); });
    chips.forEach(c => c.addEventListener('click', () => { group = c.dataset.g; limit = PAGE; chips.forEach(x => x.setAttribute('aria-pressed', String(x === c))); drawResults(); }));
    let t; q.addEventListener('input', () => { clearTimeout(t); t = setTimeout(() => { limit = PAGE; drawResults(); }, 120); });
    moreBtn.addEventListener('click', () => { const first = limit; limit += PAGE; drawResults(); const b = results.children[first] && $('button', results.children[first]); if (b) b.focus(); });
    $('#b-own').addEventListener('submit', e => {
      e.preventDefault();
      const inp = $('#b-own-n'), n = clean(inp.value);
      if (!n) { inp.focus(); return; }
      if (add({ k: 'c', id: 'c' + Date.now().toString(36), n, t: '' })) { inp.value = ''; drawStops(); }
    });
    $('#b-from').addEventListener('submit', e => {
      e.preventDefault();
      const slug = $('#b-from-s').value, p = B.plans.find(x => x.slug === slug);
      if (!p) { $('#b-from-s').focus(); return; }
      stops = decode(p.stops.join('|'));
      if (!titleIn.value.trim()) titleIn.value = p.title;
      live.textContent = `Loaded ${stops.length} stops from ${p.title}.`;
      drawStops(); drawResults(); syncTitle();
    });
    const syncTitle = () => { ptitle.textContent = titleIn.value.trim() || 'My downtown day'; persist(); };
    titleIn.addEventListener('input', syncTitle);

    // Start from the link (?stops= or ?from=), or from what this browser saved last time.
    const sp = new URLSearchParams(location.search);
    try { saved = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { saved = {}; }
    if (sp.get('stops')) { stops = decode(sp.get('stops')); titleIn.value = clean(sp.get('title')); }
    else if (sp.get('from')) {
      const p = B.plans.find(x => x.slug === sp.get('from'));
      if (p) { stops = decode(p.stops.join('|')); titleIn.value = p.title; $('#b-from-s').value = p.slug; }
    } else if (saved.stops) { stops = decode(saved.stops); titleIn.value = clean(saved.title); }

    let day = null;
    day = setupDay(B, {
      params, canPrint: () => stops.length > 0,
      title: () => titleIn.value.trim() || 'My downtown day',
      startDate: () => (!sp.get('stops') && !sp.get('from') && saved.date) || '',
      startNote: () => (!sp.get('stops') && !sp.get('from') && saved.note) || '',
      onDate: () => persist(), onNote: () => persist(),
      dateNotes: v => stops.filter(st => st.k === 'e').map(st => byKey.get(`e:${st.id}`)).filter(e => e && (v < e.date || v > e.end))
        .map(e => `${e.n} isn’t on this date. It’s ${e.when.split(' · ')[0]}.`),
    });
    syncTitle();
    drawStops();
    drawResults();
  }
})();
