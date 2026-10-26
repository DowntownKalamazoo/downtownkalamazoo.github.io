(() => {
  'use strict';
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
  const root = document.documentElement;
  root.classList.add('js');

  /* ---------- Display settings (saved in this browser only) ---------- */
  const KEY = 'dk-display-v1';
  const DEFAULTS = { scale: 100, theme: 'auto', contrast: false, motion: false, spacing: false, plain: false, underline: false, summaries: false, descriptions: false, ruler: false };
  const SWITCHES = [
    ['contrast', 'High contrast', 'Stronger text and border contrast'],
    ['motion', 'Reduce motion', 'Stops animation and smooth scrolling'],
    ['spacing', 'More text spacing', 'Wider lines, letters and words'],
    ['plain', 'Plain typeface', 'Swaps the brand fonts for a highly readable sans'],
    ['underline', 'Underline links', 'Marks links without relying on color'],
    ['summaries', 'Plain-language summaries', 'Adds a short, simple summary to each section'],
    ['descriptions', 'Show image descriptions', 'Shows the text a screen reader hears for each image'],
    ['ruler', 'Reading ruler', 'Dims everything but the line you are on'],
  ];
  let prefs = { ...DEFAULTS };
  try { const raw = localStorage.getItem(KEY); if (raw) prefs = { ...DEFAULTS, ...JSON.parse(raw) }; } catch (e) {}
  const hostTheme = root.getAttribute('data-theme');

  const list = $('#switches');
  if (list) SWITCHES.forEach(([k, name, hint]) => {
    const li = document.createElement('li');
    const id = 'sw-' + k;
    li.innerHTML = `<span class="s-text"><span class="s-name" id="${id}-l"></span><span class="s-hint" id="${id}-h"></span></span><button type="button" class="switch" role="switch" id="${id}" aria-labelledby="${id}-l" aria-describedby="${id}-h"></button>`;
    li.querySelector('.s-name').textContent = name;
    li.querySelector('.s-hint').textContent = hint;
    li.querySelector('button').addEventListener('click', () => { prefs[k] = !prefs[k]; save(); });
    list.appendChild(li);
  });
  function save() { try { localStorage.setItem(KEY, JSON.stringify(prefs)); } catch (e) {} apply(); }
  function apply() {
    root.style.setProperty('--scale', String(prefs.scale / 100));
    if (prefs.theme === 'auto') { if (hostTheme) root.setAttribute('data-theme', hostTheme); else root.removeAttribute('data-theme'); }
    else root.setAttribute('data-theme', prefs.theme);
    SWITCHES.forEach(([k]) => { root.classList.toggle('a11y-' + k, !!prefs[k]); const b = $('#sw-' + k); if (b) b.setAttribute('aria-checked', String(!!prefs[k])); });
    const out = $('#size-out'); if (out) out.textContent = prefs.scale + '%';
    const dn = $('#size-down'), up = $('#size-up');
    if (dn) dn.disabled = prefs.scale <= 80; if (up) up.disabled = prefs.scale >= 200;
    $$('#theme-group button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.themeVal === prefs.theme)));
  }
  const on = (sel, ev, fn) => { const n = $(sel); if (n) n.addEventListener(ev, fn); };
  on('#size-down', 'click', () => { prefs.scale = Math.max(80, prefs.scale - 10); save(); });
  on('#size-up', 'click', () => { prefs.scale = Math.min(200, prefs.scale + 10); save(); });
  $$('#theme-group button').forEach(b => b.addEventListener('click', () => { prefs.theme = b.dataset.themeVal; save(); }));
  on('#reset-display', 'click', () => { prefs = { ...DEFAULTS }; save(); });
  apply();

  const dlg = $('#display-dialog');
  let opener = null;
  $$('[data-open-display]').forEach(b => b.addEventListener('click', () => {
    opener = b;
    try { dlg.showModal(); } catch (e) { dlg.setAttribute('open', ''); }
  }));
  if (dlg) {
    dlg.addEventListener('click', e => { if (e.target.closest('[data-close]')) dlg.close(); });
    dlg.addEventListener('close', () => { if (opener) opener.focus(); });
  }

  const ruler = $('#ruler');
  const place = y => ruler && ruler.style.setProperty('--y', Math.round(y) + 'px');
  document.addEventListener('pointermove', e => { if (prefs.ruler) place(e.clientY); }, { passive: true });
  document.addEventListener('focusin', e => { if (prefs.ruler && e.target.getBoundingClientRect) { const r = e.target.getBoundingClientRect(); place(r.top + r.height / 2); } });

  /* ---------- Mobile menu ---------- */
  const menuBtn = $('#menu-btn'), nav = $('#site-nav');
  if (menuBtn && nav) {
    menuBtn.addEventListener('click', () => {
      const open = menuBtn.getAttribute('aria-expanded') !== 'true';
      menuBtn.setAttribute('aria-expanded', String(open));
      nav.classList.toggle('open', open);
    });
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && nav.classList.contains('open')) { nav.classList.remove('open'); menuBtn.setAttribute('aria-expanded', 'false'); menuBtn.focus(); } });
  }

  /* ---------- Main menu: "About" dropdown ---------- */
  $$('.nav-menu-btn').forEach(btn => {
    const menu = document.getElementById(btn.getAttribute('aria-controls'));
    if (!menu) return;
    const set = open => { btn.setAttribute('aria-expanded', String(open)); menu.classList.toggle('open', open); };
    btn.addEventListener('click', () => set(btn.getAttribute('aria-expanded') !== 'true'));
    btn.parentElement.addEventListener('keydown', e => { if (e.key === 'Escape' && menu.classList.contains('open')) { e.stopPropagation(); set(false); btn.focus(); } });
    btn.parentElement.addEventListener('focusout', e => { if (!btn.parentElement.contains(e.relatedTarget)) set(false); });
    document.addEventListener('click', e => { if (!btn.parentElement.contains(e.target)) set(false); });
  });

  /* ---------- Filter buttons: events calendar, news, board documents, business resources ---------- */
  function filterChips(chipSel, attr, itemSel, groupSel, statusEl, emptyEl, noun) {
    const chips = $$(chipSel);
    if (!chips.length) return;
    const items = $$(itemSel);
    const apply = val => {
      chips.forEach(c => c.setAttribute('aria-pressed', String(c.dataset[attr] === val)));
      let n = 0;
      items.forEach(it => {
        const vals = (it.dataset[attr === 'tag' ? 'tags' : attr] || '').split('|');
        const ok = val === 'all' || vals.includes(val);
        it.hidden = !ok;
        if (ok && !it.classList.contains('is-past')) n++;
      });
      if (groupSel) $$(groupSel).forEach(g => {
        const vis = $$(itemSel, g).filter(it => !it.hidden && !it.classList.contains('is-past')).length;
        g.hidden = vis === 0;
        const c = $('.cal-count', g); if (c) c.textContent = `${vis} event${vis === 1 ? '' : 's'}`;
      });
      if (statusEl) statusEl.textContent = `Showing ${n} ${noun}${n === 1 ? '' : 's'}`;
      if (emptyEl) emptyEl.hidden = n > 0;
    };
    chips.forEach(c => c.addEventListener('click', () => apply(c.dataset[attr])));
    if (groupSel) apply('all');
  }
  filterChips('#cal-tags .chip', 'tag', '.calendar .event-row', '.cal-month', $('#cal-status'), $('#cal-empty'), 'event');
  filterChips('#news-types .chip', 'type', '#news-list .news-item', null, $('#news-status'), null, 'story');
  filterChips('#doc-filter button', 'board', '#docs-table tbody tr', null, null, null, 'document');
  filterChips('#res-needs .chip', 'need', '#res-list .res-card', null, $('#res-status'), null, 'resource');

  /* ---------- Share a news story ---------- */
  $$('[data-share]').forEach(b => b.addEventListener('click', async () => {
    const status = $('[data-share-status]');
    const data = { title: document.title, url: (document.querySelector('link[rel="canonical"]') || {}).href || location.href };
    try {
      if (navigator.share) { await navigator.share(data); return; }
      await navigator.clipboard.writeText(data.url);
      if (status) status.textContent = 'Link copied.';
    } catch (e) { if (status && e.name !== 'AbortError') status.textContent = 'Copy this page’s address from your browser to share it.'; }
  }));

  /* ---------- Upcoming / past events ---------- */
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const rows = $$('[data-end]');
  let nextMarked = false;
  rows.forEach(r => {
    const end = new Date(r.dataset.end + 'T23:59:59');
    if (end < today) {
      r.classList.add('is-past');
      const t = r.querySelector('.status'); if (t) { t.textContent = 'Past event'; t.hidden = false; }
    } else if (!nextMarked && r.hasAttribute('data-mark-next')) {
      nextMarked = true;
      const t = r.querySelector('.status'); if (t) { t.textContent = 'Up next'; t.classList.add('tag-next'); t.hidden = false; }
    }
  });
  // Home: show only the next three upcoming events
  const upcoming = $('#upcoming');
  if (upcoming) {
    const items = $$('li', upcoming);
    const future = items.filter(li => new Date(li.dataset.end + 'T23:59:59') >= today);
    const show = (future.length ? future : items.slice(-3)).slice(0, 3);
    items.forEach(li => { li.hidden = !show.includes(li); });
  }

  /* ---------- Business directory: flip cards ---------- */
  const grid = $('#biz-grid');
  if (grid) {
    const cards = $$('.biz', grid);
    const q = $('#dir-q'), chips = $$('#dir-cats .chip'), ddChip = $('#dir-dd'), sdChip = $('#dir-sd'), count = $('#dir-count'), empty = $('#dir-empty');
    const VIEW_KEY = 'dk-dir-view';
    const canHover = window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    let cat = 'all', ddOnly = false, sdOnly = false;
    const hash = (location.hash || '').replace('#', '');
    if (hash === 'dollars') ddOnly = true;
    else if (hash === 'social') sdOnly = true;
    else if (chips.some(c => c.dataset.cat === hash)) cat = hash;

    const st = new Map(cards.map(c => [c, { pinned: false, hovered: false, suppress: false, timer: 0 }]));
    const listView = () => grid.classList.contains('view-list');
    function sync(card) {
      const s = st.get(card);
      const flipped = !listView() && (s.pinned || (s.hovered && !s.suppress));
      card.classList.toggle('is-flipped', flipped);
      const front = $('.front', card), back = $('.back', card), btn = $('.flip-btn', card);
      if (listView()) { front.inert = false; back.inert = false; btn.removeAttribute('aria-expanded'); return; }
      front.inert = flipped; back.inert = !flipped;
      btn.setAttribute('aria-expanded', String(flipped));
    }
    function setPinned(card, val, focus) {
      const s = st.get(card);
      if (val) cards.forEach(c => { if (c !== card && st.get(c).pinned) { st.get(c).pinned = false; sync(c); } });
      s.pinned = val;
      if (!val && s.hovered) s.suppress = true;
      sync(card);
      if (focus === 'back') $('.back-body', card).focus({ preventScroll: true });
      if (focus === 'front') $('.flip-btn', card).focus({ preventScroll: true });
    }
    cards.forEach(card => {
      const s = st.get(card);
      $('.flip-btn', card).addEventListener('click', e => {
        if (listView()) return;
        const viaKeyboard = e.detail === 0;
        setPinned(card, true, viaKeyboard ? 'back' : null);
      });
      $('.flip-back', card).addEventListener('click', e => { setPinned(card, false, 'front'); });
      $('.back', card).addEventListener('click', e => {
        if (listView() || e.target.closest('a, button')) return;
        setPinned(card, !s.pinned);
      });
      card.addEventListener('keydown', e => { if (e.key === 'Escape' && card.classList.contains('is-flipped')) { setPinned(card, false, 'front'); } });
      if (canHover) {
        card.addEventListener('pointerenter', e => {
          if (e.pointerType !== 'mouse') return;
          clearTimeout(s.timer);
          s.timer = setTimeout(() => { s.hovered = true; sync(card); }, 140);
        });
        card.addEventListener('pointerleave', e => {
          clearTimeout(s.timer);
          s.hovered = false; s.suppress = false;
          if (s.pinned && !card.contains(document.activeElement)) s.pinned = false;
          sync(card);
        });
      }
      sync(card);
    });

    function run() {
      const term = (q.value || '').trim().toLowerCase();
      let n = 0;
      cards.forEach(c => {
        const ok = (cat === 'all' || c.dataset.cat === cat) && (!ddOnly || c.dataset.dd === '1') && (!sdOnly || c.dataset.sd === '1') && (!term || c.dataset.search.includes(term));
        c.hidden = !ok; if (ok) n++;
      });
      chips.forEach(c => c.setAttribute('aria-pressed', String(c.dataset.cat === cat)));
      ddChip.setAttribute('aria-pressed', String(ddOnly));
      if (sdChip) sdChip.setAttribute('aria-pressed', String(sdOnly));
      const label = cat === 'all' ? 'businesses' : (chips.find(c => c.dataset.cat === cat).dataset.noun || (chips.find(c => c.dataset.cat === cat).dataset.label + ' businesses'));
      count.textContent = `Showing ${n} of ${cards.length} ${n === cards.length ? 'businesses' : label}${ddOnly ? ' that accept Downtown Dollars' : ''}${sdOnly ? ' in the Social District' : ''}`;
      empty.hidden = n > 0;
    }
    chips.forEach(c => c.addEventListener('click', () => { cat = c.dataset.cat; run(); }));
    ddChip.addEventListener('click', () => { ddOnly = !ddOnly; run(); });
    if (sdChip) sdChip.addEventListener('click', () => { sdOnly = !sdOnly; run(); });
    // Searches from the home page arrive as directory.html?q=…
    const qp = new URLSearchParams(location.search).get('q');
    if (qp) q.value = qp.slice(0, 80);
    let t; q.addEventListener('input', () => { clearTimeout(t); t = setTimeout(run, 150); });
    $('#dir-form').addEventListener('submit', e => e.preventDefault());
    $('#dir-clear').addEventListener('click', () => { cat = 'all'; ddOnly = false; sdOnly = false; q.value = ''; run(); q.focus(); });

    const viewBtns = $$('#view-group button');
    function setView(v, save) {
      grid.classList.toggle('view-list', v === 'list');
      viewBtns.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.view === v)));
      cards.forEach(c => { const s = st.get(c); s.pinned = false; s.hovered = false; sync(c); });
      $('#dir-hint').hidden = v === 'list';
      if (save) { try { localStorage.setItem(VIEW_KEY, v); } catch (e) {} }
    }
    viewBtns.forEach(b => b.addEventListener('click', () => setView(b.dataset.view, true)));
    let saved = 'cards'; try { saved = localStorage.getItem(VIEW_KEY) || 'cards'; } catch (e) {}
    setView(saved === 'list' ? 'list' : 'cards', false);
    run();

    // A link like directory.html#b-some-business opens that card
    if (/^b-[a-z0-9-]+$/.test(hash)) {
      const target = document.getElementById(hash);
      if (target && st.has(target)) {
        target.hidden = false;
        target.scrollIntoView({ block: 'center' });
        if (!listView()) setPinned(target, true, 'back');
        else { const n = $('.flip-btn', target); if (n) n.focus({ preventScroll: true }); }
      }
    }
  }

  /* ---------- Turn the corner: pages that peel away to reveal a hidden find ---------- */
  const reduceMotion = () => root.classList.contains('a11y-motion') || (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
  function setTurned(box, on, moveFocus) {
    const page = $('.peel-card', box), secret = $('.turn-secret', box), corner = $('.turn-corner', box);
    if (on) {
      box.classList.add('is-turned');
      page.inert = true; secret.inert = false;
      corner.setAttribute('aria-expanded', 'true');
      if (moveFocus) { const n = $('.secret-note', secret); setTimeout(() => n && n.focus({ preventScroll: true }), reduceMotion() ? 0 : 450); }
    } else {
      box.classList.remove('is-turned');
      page.inert = false; secret.inert = true;
      corner.setAttribute('aria-expanded', 'false');
      if (moveFocus) corner.focus({ preventScroll: true });
    }
  }
  $$('[data-turn]').forEach(box => {
    const corner = $('.turn-corner', box), back = $('.turn-back', box);
    if (!corner) return;
    corner.addEventListener('click', () => setTurned(box, true, true));
    if (back) back.addEventListener('click', () => setTurned(box, false, true));
    box.addEventListener('keydown', e => { if (e.key === 'Escape' && box.classList.contains('is-turned')) setTurned(box, false, true); });
  });
  // Measure each card so the peel line stays at 45 degrees at any size
  const measure = b => { b.style.setProperty('--bw', b.offsetWidth + 'px'); b.style.setProperty('--bh', b.offsetHeight + 'px'); };
  const turns = $$('[data-turn]');
  turns.forEach(measure);
  if (window.ResizeObserver) { const ro = new ResizeObserver(es => es.forEach(e => measure(e.target))); turns.forEach(b => ro.observe(b)); }
  else window.addEventListener('resize', () => turns.forEach(measure));

  /* ---------- Serendipity: curled corners that turn up somewhere new on each visit ---------- */
  (function nooks() {
    const dataEl = $('#dk-finds');
    if (!dataEl) return;
    let data; try { data = JSON.parse(dataEl.textContent); } catch (e) { return; }
    const ids = Object.keys(data.pool || {});
    if (!ids.length) return;
    const FOUND_KEY = 'dk-found';
    let found = [];
    try { found = JSON.parse(localStorage.getItem(FOUND_KEY) || '[]'); } catch (e) {}
    const counter = $('#found-count');
    const showCount = () => {
      if (!counter || !found.length) return;
      counter.textContent = `· ${found.length} of ${ids.length} downtown secrets found`;
      counter.hidden = false;
    };
    showCount();

    const main = $('#main');
    if (!main) return;
    const sel = '.event-row, .cards .card, .aside .panel, .strip li, .timeline .stop, .two-col > .panel, .host-band, .construction, .checks li';
    const hosts = $$(sel, main).filter(el => !el.closest('.turn, .biz, .hero-weave, .hero-card, dialog, .dir-tools, form') && el.offsetParent !== null);
    if (!hosts.length || Math.random() < 0.12) return;   // sometimes there is nothing to find
    const howMany = hosts.length > 9 ? 2 : 1;
    const pickHosts = [];
    const pool = hosts.slice();
    while (pickHosts.length < howMany && pool.length) pickHosts.push(pool.splice(Math.floor(Math.random() * pool.length), 1)[0]);

    const unfound = id => !found.includes(id);
    const queue = (data.page || []).filter(unfound);
    const rest = ids.filter(id => unfound(id) && !queue.includes(id)).sort(() => Math.random() - 0.5);
    const order = queue.concat(rest.length ? rest : ids.slice().sort(() => Math.random() - 0.5));
    const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    let openNote = null;

    function close(note, focusBack) {
      if (!note) return;
      const btn = note._nook;
      note.remove();
      btn.setAttribute('aria-expanded', 'false');
      if (focusBack) btn.focus({ preventScroll: true });
      if (openNote === note) openNote = null;
    }

    pickHosts.forEach((host, i) => {
      const id = order[i % order.length];
      const f = data.pool[id];
      const dots = Math.random() < 0.5;
      host.classList.add('has-nook');
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'nook' + (dots ? ' is-dots' : '');
      btn.setAttribute('aria-label', 'Lift the corner');
      btn.setAttribute('aria-expanded', 'false');
      host.appendChild(btn);
      btn.addEventListener('click', e => {
        e.preventDefault(); e.stopPropagation();
        if (openNote) close(openNote, false);
        if (!found.includes(id)) { found.push(id); try { localStorage.setItem(FOUND_KEY, JSON.stringify(found)); } catch (x) {} showCount(); }
        const note = document.createElement('div');
        note.className = 'nook-note' + (dots ? ' is-dots' : '');
        const link = f.l ? `<p><a href="${esc((data.r || '') + f.l[0])}">${esc(f.l[1])}</a></p>` : '';
        note.innerHTML = `<div class="secret-note" tabindex="-1" role="region" aria-label="${esc(f.t)}"><span class="kicker">${esc(f.k)}</span><p class="secret-title">${esc(f.t)}</p><p>${esc(f.x)}</p>${link}<div class="btn-row" style="align-items:center;justify-content:space-between"><button type="button" class="btn btn-small btn-quiet nook-close">Tuck it back</button><span class="found">${found.length} of ${ids.length} found</span></div></div>`;
        note._nook = btn;
        note.addEventListener('click', ev => ev.stopPropagation());
        $('.nook-close', note).addEventListener('click', () => close(note, true));
        note.addEventListener('keydown', ev => { if (ev.key === 'Escape') close(note, true); });
        host.appendChild(note);
        btn.setAttribute('aria-expanded', 'true');
        const r = note.getBoundingClientRect();
        if (r.left < 8) note.style.right = (r.left - 8) + 'px';
        openNote = note;
        $('.secret-note', note).focus({ preventScroll: true });
      });
    });
    document.addEventListener('click', () => { if (openNote) close(openNote, false); });
  })();

  /* ---------- Newsletter sign-up ---------- */
  // Connect a mailing list here. For Mailchimp, paste the embedded form's action URL
  // (https://….list-manage.com/subscribe/post?u=…&id=…) into `mailchimp`.
  // For Formspree or a similar service, put its endpoint in `endpoint`.
  // With both blank, the form opens a pre-filled email to `to`.
  const NEWSLETTER = { mailchimp: '', endpoint: '', to: 'downtown@kalamazoocity.org' };
  function mailchimpJsonp(fields) {
    return new Promise((resolve, reject) => {
      const cb = 'dkmc' + Date.now();
      const url = NEWSLETTER.mailchimp.replace('/post?', '/post-json?') + '&' + new URLSearchParams(fields).toString() + '&c=' + cb;
      const s = document.createElement('script');
      const t = setTimeout(() => { cleanup(); reject(new Error('timeout')); }, 10000);
      function cleanup() { clearTimeout(t); delete window[cb]; s.remove(); }
      window[cb] = res => { cleanup(); res && res.result === 'success' ? resolve(res) : reject(new Error((res && res.msg) || 'error')); };
      s.onerror = () => { cleanup(); reject(new Error('network')); };
      s.src = url; document.head.appendChild(s);
    });
  }
  $$('form[data-newsletter]').forEach(form => {
    const done = form.parentElement.querySelector('.news-done');
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const email = form.elements.email, err = form.querySelector('#' + email.id + '-err');
      const val = email.value.trim();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) {
        email.setAttribute('aria-invalid', 'true');
        err.textContent = val ? 'Enter an email address like name@example.com.' : 'Enter your email address.';
        err.hidden = false; email.focus(); return;
      }
      email.removeAttribute('aria-invalid'); err.hidden = true;
      const first = form.elements.first ? form.elements.first.value.trim() : '';
      const zip = form.elements.zip ? form.elements.zip.value.trim() : '';
      const interests = $$('input[name="interests"]:checked', form).map(i => i.value);
      const btn = form.querySelector('button[type="submit"]');
      const showDone = html => { form.hidden = true; done.innerHTML = html; done.hidden = false; done.focus(); };
      if (NEWSLETTER.mailchimp || NEWSLETTER.endpoint) {
        btn.disabled = true; const label = btn.textContent; btn.textContent = 'Joining…';
        try {
          if (NEWSLETTER.mailchimp) await mailchimpJsonp({ EMAIL: val, FNAME: first, MMERGE5: zip });
          else {
            const fd = new FormData(); fd.append('email', val); fd.append('first', first); fd.append('zip', zip); fd.append('interests', interests.join(', '));
            const res = await fetch(NEWSLETTER.endpoint, { method: 'POST', body: fd, headers: { Accept: 'application/json' } });
            if (!res.ok) throw new Error(res.status);
          }
          showDone('<p class="h3" style="font-weight:700">You’re on the list. Welcome downtown!</p><p>Watch your inbox for the next newsletter. If you don’t see a confirmation email, check your spam folder.</p>');
          try { localStorage.setItem('dk-welcome-seen', 'joined'); } catch (x) {}
          return;
        } catch (x) {
          btn.disabled = false; btn.textContent = label;
          err.textContent = 'That didn’t go through. Check your connection and try again.'; err.hidden = false;
          return;
        }
      }
      const body = ['Please add me to the Downtown Kalamazoo newsletter.', '', 'Email: ' + val, first ? 'First name: ' + first : '', zip ? 'ZIP: ' + zip : '', interests.length ? 'Interests: ' + interests.join(', ') : ''].filter(Boolean).join('\n');
      const mail = 'mailto:' + NEWSLETTER.to + '?subject=' + encodeURIComponent('Newsletter sign-up') + '&body=' + encodeURIComponent(body);
      showDone('<p class="h3" style="font-weight:700">One more step: send the email</p><p>Your email app should open with your sign-up filled in. Press Send there to join.</p><p>If no email opened, send your address to <span>' + NEWSLETTER.to + '</span> with “Newsletter sign-up” in the subject.</p>');
      try { window.location.href = mail; } catch (x) {}
    });
  });

  /* ---------- Home: welcome pop-up, once per visitor ---------- */
  const welcome = $('#welcome-dialog');
  if (welcome && welcome.showModal) {
    let seen = true;
    try { seen = !!localStorage.getItem('dk-welcome-seen'); } catch (e) {}
    const markSeen = () => { try { if (!localStorage.getItem('dk-welcome-seen')) localStorage.setItem('dk-welcome-seen', '1'); } catch (e) {} };
    let lastFocus = null;
    const closeWelcome = () => { welcome.close(); };
    welcome.addEventListener('close', () => { markSeen(); if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true }); });
    $$('[data-welcome-close]', welcome).forEach(b => b.addEventListener('click', closeWelcome));
    welcome.addEventListener('click', e => { if (e.target === welcome) closeWelcome(); });
    if (!seen) {
      setTimeout(() => {
        if ($$('dialog[open]').length) return;
        lastFocus = document.activeElement;
        welcome.showModal();
        $('#welcome-body', welcome).focus();
        markSeen();
      }, 3500);
    }
  }

  /* ---------- Home hero: pause or play the weaving lines ---------- */
  const weaveBtn = $('#weave-toggle'), weaveBox = $('#hero-weave');
  if (weaveBtn && weaveBox) {
    let paused = false;
    try { paused = localStorage.getItem('dk-weave-paused') === '1'; } catch (e) {}
    const setPaused = v => {
      paused = v;
      weaveBox.classList.toggle('is-paused', v);
      weaveBtn.textContent = v ? 'Play motion' : 'Pause motion';
      try { localStorage.setItem('dk-weave-paused', v ? '1' : '0'); } catch (e) {}
    };
    weaveBtn.removeAttribute('aria-pressed');
    setPaused(paused);
    weaveBtn.addEventListener('click', () => setPaused(!paused));
  }

  /* ---------- Home: "Around every corner" discovery ---------- */
  const dcard = $('#discover-card'), dnext = $('#discover-next'), ddata = $('#discover-data');
  if (dcard && dnext && ddata) {
    let finds = [];
    try { finds = JSON.parse(ddata.textContent); } catch (e) {}
    const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    const base = (dcard.querySelector('a') || {}).getAttribute ? dcard.querySelector('a').getAttribute('href').split('#')[0] : 'directory.html';
    let seen = new Set([dcard.dataset.current]);
    let shown = 1;
    dnext.addEventListener('click', () => {
      if (!finds.length) return;
      let pool = finds.filter(f => !seen.has(f.id));
      if (!pool.length) { seen = new Set([dcard.dataset.current]); pool = finds.filter(f => !seen.has(f.id)); }
      const f = pool[Math.floor(Math.random() * pool.length)];
      seen.add(f.id); shown++;
      dcard.className = 'discover-card ' + f.f;
      dcard.dataset.current = f.id;
      dcard.innerHTML = `<span class="cat">${esc(f.c)}</span><h3>${esc(f.n)}</h3><p>${esc(f.d)}</p>${f.w ? `<p class="where">${esc(f.w)}</p>` : ''}<div class="foot">${f.dd ? '<span class="dd-badge"><span class="dd-coin" aria-hidden="true">$</span>Accepts Downtown Dollars</span>' : '<span></span>'}<a href="${esc(base)}#b-${esc(f.id)}">See it in the directory<span class="sr-only">: ${esc(f.n)}</span></a></div>`;
      if (!root.classList.contains('a11y-motion')) { dcard.classList.remove('turning'); void dcard.offsetWidth; dcard.classList.add('turning'); }
      const cnt = $('#discover-count');
      if (cnt) cnt.textContent = `${shown} found so far, out of ${finds.length} downtown finds. Keep going.`;
      dnext.textContent = 'Turn another corner';
    });
  }

  /* ---------- Brand extras: shared helpers ---------- */
  const escH = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  let FINDS = null;
  try { FINDS = JSON.parse(($('#dk-finds') || {}).textContent || 'null'); } catch (e) {}
  const findHTML = id => {
    const f = FINDS && FINDS.pool && FINDS.pool[id];
    if (!f) return '';
    const link = f.l ? `<p><a href="${escH(FINDS.r + f.l[0])}">${escH(f.l[1])}</a></p>` : '';
    return `<span class="kicker">${escH(f.k)}</span><p class="t">${escH(f.t)}</p><p>${escH(f.x)}</p>${link}`;
  };
  const motionOff = () => root.classList.contains('a11y-motion') || matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Home: reshuffle the patchwork behind the discovery card on every turn */
  const quilt = $('#quilt-mat');
  if (quilt && dnext) {
    dnext.addEventListener('click', () => {
      const spans = $$('span', quilt), bgs = spans.map(s => s.style.backgroundImage);
      const swap = () => { bgs.sort(() => Math.random() - 0.5); spans.forEach((s, i) => { s.style.backgroundImage = bgs[i]; }); };
      if (motionOff()) { swap(); return; }
      quilt.classList.add('is-shuffling');
      setTimeout(() => { swap(); quilt.classList.remove('is-shuffling'); }, 350);
    });
  }

  /* 404: offer a random discovery instead */
  const lost = $('#lost-find');
  if (lost && FINDS && FINDS.pool) {
    const ids = Object.keys(FINDS.pool);
    lost.innerHTML = findHTML(ids[Math.floor(Math.random() * ids.length)]);
    lost.hidden = false;
  }

  /* ---------- Simple forms that send to an inbox (Share your downtown) ---------- */
  // Put a form service URL (for example Formspree) in `endpoint` to collect answers directly.
  // Left blank, the form opens a pre-filled email to `to`.
  const FORMS = { endpoint: '', to: 'downtown@kalamazoocity.org' };
  $$('form[data-mailform]').forEach(mf => {
    const box = mf.parentElement, done = $('.done', box), summary = $('.err-summary', box);
    const labelOf = f => {
      const l = f.type === 'checkbox' ? f.closest('label') : $(`label[for="${f.id}"]`, mf);
      return l ? l.textContent.replace('*', '').trim() : f.name;
    };
    const setErr = (f, msg) => {
      const err = $('#' + f.id + '-err', mf);
      if (msg) { f.setAttribute('aria-invalid', 'true'); if (err) { err.textContent = msg; err.hidden = false; } }
      else { f.removeAttribute('aria-invalid'); if (err) err.hidden = true; }
    };
    mf.addEventListener('submit', async e => {
      e.preventDefault();
      const errs = [];
      $$('input, textarea, select', mf).forEach(f => {
        let msg = '';
        const v = (f.value || '').trim();
        if (f.required && (f.type === 'checkbox' ? !f.checked : !v)) msg = f.type === 'checkbox' ? 'Please check this box so we can share your answer.' : 'Please fill this in.';
        else if (f.type === 'email' && v && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) msg = 'Enter an email address like name@example.com.';
        setErr(f, msg);
        if (msg) errs.push([f, msg]);
      });
      if (errs.length) {
        if (summary) {
          $('ul', summary).innerHTML = errs.map(([f, m]) => `<li><a href="#${f.id}">${escH(labelOf(f).slice(0, 60))}: ${escH(m)}</a></li>`).join('');
          summary.hidden = false; summary.focus();
          $$('a', summary).forEach(a => a.addEventListener('click', ev => { ev.preventDefault(); const t = $(a.getAttribute('href')); if (t) t.focus(); }));
        } else errs[0][0].focus();
        return;
      }
      if (summary) summary.hidden = true;
      const lines = [];
      $$('input, textarea, select', mf).forEach(f => {
        if (f.type === 'checkbox') { if (f.checked) lines.push(`${f.name}: Yes`); return; }
        const v = f.value.trim();
        if (v && !(f.tagName === 'SELECT' && f.selectedIndex === 0)) lines.push(`${f.name}: ${v}`);
      });
      const subject = mf.dataset.subject || 'Message from the downtown website';
      const show = html => { mf.hidden = true; done.innerHTML = html; done.hidden = false; done.focus(); };
      if (FORMS.endpoint) {
        const btn = $('button[type="submit"]', mf), label = btn.textContent;
        btn.disabled = true; btn.textContent = 'Sending…';
        try {
          const fd = new FormData(); fd.append('_subject', subject); lines.forEach(l => { const i = l.indexOf(': '); fd.append(l.slice(0, i), l.slice(i + 2)); });
          const res = await fetch(FORMS.endpoint, { method: 'POST', body: fd, headers: { Accept: 'application/json' } });
          if (!res.ok) throw new Error(res.status);
          show('<h2 class="h3">Thank you!</h2><p>We got your answer. Keep an eye out for it on this page and around downtown.</p>');
        } catch (x) { btn.disabled = false; btn.textContent = label; alert('That didn’t go through. Check your connection and try again.'); }
        return;
      }
      const mail = 'mailto:' + FORMS.to + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(lines.join('\n'));
      show(`<h2 class="h3">One more step: send the email</h2><p>Your email app should open with your answer filled in. Press Send there and you’re done.</p><p>If no email opened, send your answer to <span>${FORMS.to}</span>.</p>`);
      try { window.location.href = mail; } catch (x) {}
    });
  });

  /* ---------- Plan pages: make a postcard ---------- */
  const pcBtn = $('[data-postcard]'), pcDlg = $('#postcard-dialog'), pcData = $('#postcard-data');
  if (pcBtn && pcDlg && pcData && pcDlg.showModal) {
    let P = null;
    try { P = JSON.parse(pcData.textContent); } catch (e) {}
    let blob = null;
    const img = $('#pc-img'), wait = $('#pc-wait'), saveBtn = $('#pc-save'), shareBtn = $('#pc-share');
    const loadImg = src => new Promise((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = rej; i.src = src; });
    const wrapText = (x, text, maxW) => {
      const words = String(text).split(/\s+/), lines = [];
      let line = '';
      words.forEach(w => { const t = line ? line + ' ' + w : w; if (x.measureText(t).width > maxW && line) { lines.push(line); line = w; } else line = t; });
      if (line) lines.push(line);
      return lines;
    };
    const rr = (x, X, Y, W, H, R) => { x.beginPath(); x.moveTo(X + R, Y); x.arcTo(X + W, Y, X + W, Y + H, R); x.arcTo(X + W, Y + H, X, Y + H, R); x.arcTo(X, Y + H, X, Y, R); x.arcTo(X, Y, X + W, Y, R); x.closePath(); };
    async function draw() {
      const W = 1080, Hh = 1350, NAVY = '#121345';
      const c = document.createElement('canvas'); c.width = W; c.height = Hh;
      const x = c.getContext('2d');
      try { await Promise.all(['900 58px Unbounded', '700 30px Jost', '500 34px Jost', '400 28px Jost'].map(f => document.fonts.load(f))); } catch (e) {}
      const r = FINDS ? FINDS.r : '';
      const [pat, logo] = await Promise.all([loadImg(r + 'pattern-' + P.pat + '.webp'), loadImg(r + 'dk-logo-green.png')]);
      const footH = 230;
      x.fillStyle = '#e7f5f5'; x.fillRect(0, 0, W, Hh);
      const bandH = Hh - footH, s = Math.max(W / pat.width, bandH / pat.height);
      x.save(); x.beginPath(); x.rect(0, 0, W, bandH); x.clip();
      x.drawImage(pat, (W - pat.width * s) / 2, (bandH - pat.height * s) / 2, pat.width * s, pat.height * s); x.restore();
      const cx = 60, cw = W - 120, pad = 56, timeW = 190, maxCardH = bandH - 120;
      // Lay out once to measure, then draw the card to fit and lay out again on top of it.
      const layout = (cy, paint) => {
        let y = cy + pad + 26;
        x.font = '700 28px Jost';
        if (paint) { x.fillStyle = '#04679a'; x.fillText(String(P.tag).toUpperCase(), cx + pad, y); }
        y += 30;
        x.font = '900 54px Unbounded';
        wrapText(x, String(P.title).toUpperCase(), cw - pad * 2).slice(0, 3).forEach(l => { y += 62; if (paint) { x.fillStyle = NAVY; x.fillText(l, cx + pad, y); } });
        y += 34;
        if (paint) { x.fillStyle = '#f5b8d1'; x.fillRect(cx + pad, y, 120, 8); }
        y += 30;
        let shown = 0;
        for (const st of P.stops) {
          x.font = '500 33px Jost';
          const lines = wrapText(x, st.p, cw - pad * 2 - timeW).slice(0, 2);
          const need = 40 + (lines.length - 1) * 40 + 18;
          if (y + need > cy + maxCardH - pad - (shown < P.stops.length - 1 ? 46 : 0)) break;
          y += 40;
          if (paint) {
            x.fillStyle = '#04679a'; x.font = '700 30px Jost'; x.fillText(st.t, cx + pad, y);
            x.fillStyle = NAVY; x.font = '500 33px Jost';
            lines.forEach((l, i) => x.fillText(l, cx + pad + timeW, y + i * 40));
          }
          y += (lines.length - 1) * 40 + 18;
          shown++;
        }
        if (shown < P.stops.length) { y += 40; if (paint) { x.fillStyle = NAVY; x.font = '400 28px Jost'; x.fillText(`+ ${P.stops.length - shown} more stops`, cx + pad + timeW, y); } }
        return y + pad - 10;
      };
      const ch = layout(0, false);
      const cy = Math.max(70, (bandH - ch) / 2);
      x.save(); x.shadowColor = 'rgba(18,19,69,.28)'; x.shadowBlur = 40; x.shadowOffsetY = 14;
      rr(x, cx, cy, cw, ch, 28); x.fillStyle = '#fff'; x.fill(); x.restore();
      layout(cy, true);
      const lh = 120, lw = logo.width * lh / logo.height;
      x.drawImage(logo, 60, Hh - lh - 50, lw, lh);
      x.textAlign = 'right'; x.fillStyle = NAVY;
      x.font = '700 34px Jost'; x.fillText('#SomethingNewKalamazoo', W - 60, Hh - 112);
      x.font = '400 28px Jost'; x.fillText('Find the Holidays Downtown', W - 60, Hh - 70);
      return new Promise((res, rej) => c.toBlob(b => b ? res(b) : rej(new Error('blob')), 'image/png'));
    }
    pcBtn.addEventListener('click', async () => {
      pcDlg.showModal();
      if (blob || !P) return;
      try { blob = await draw(); } catch (e) { wait.textContent = 'Sorry, this browser couldn’t draw the postcard. Try another browser, or take a screenshot of the plan.'; return; }
      const url = URL.createObjectURL(blob), name = `downtown-kalamazoo-${P.slug}.png`;
      img.src = url;
      img.alt = `Postcard of the plan “${P.title}”, with the stops: ` + P.stops.map(s => `${s.t}, ${s.p}`).join('; ') + '.';
      img.hidden = false; wait.hidden = true;
      saveBtn.href = url; saveBtn.download = name; saveBtn.hidden = false;
      try {
        const file = new File([blob], name, { type: 'image/png' });
        if (navigator.canShare && navigator.canShare({ files: [file] })) {
          shareBtn.hidden = false;
          shareBtn.addEventListener('click', () => navigator.share({ files: [file], title: P.title, text: 'Our downtown plan #SomethingNewKalamazoo' }).catch(() => {}));
        }
      } catch (e) {}
    });
    $$('[data-pc-close]', pcDlg).forEach(b => b.addEventListener('click', () => pcDlg.close()));
    pcDlg.addEventListener('click', e => { if (e.target === pcDlg) pcDlg.close(); });
    pcDlg.addEventListener('close', () => pcBtn.focus());
  }

  /* ---------- Submit an event ---------- */
  // To collect submissions in an inbox service (for example Formspree or a Google Apps Script),
  // put its URL in `endpoint`. Left blank, the form opens a pre-filled email to `to`.
  const EVENT_FORM = { endpoint: '', to: 'downtown@kalamazoocity.org' };
  const form = $('#event-form');
  if (form) {
    const summary = $('#err-summary'), list = $('#err-list'), done = $('#event-done');
    const labels = {
      org: 'Group, business or venue name', contact: 'Your name', email: 'Email', title: 'Event name', date: 'Date',
      start: 'Start time', venue: 'Venue or location name', address: 'Street address', description: 'Short description',
      cost: 'Cost', agree: 'Confirmation', link: 'Event or ticket link', photo: 'Photo link', end_date: 'Last day', price: 'Price'
    };
    const setErr = (id, msg) => {
      const el = id === 'cost' ? null : form.elements[id];
      const m = $('#' + id + '-err');
      if (el && el.setAttribute) { if (msg) el.setAttribute('aria-invalid', 'true'); else el.removeAttribute('aria-invalid'); }
      if (m) { m.textContent = msg || ''; m.hidden = !msg; }
    };
    function validate() {
      const errs = [];
      const val = id => (form.elements[id] && form.elements[id].value || '').trim();
      ['org', 'contact', 'email', 'title', 'date', 'start', 'venue', 'address', 'description'].forEach(id => {
        setErr(id, '');
        if (!val(id)) errs.push([id, `Enter the ${labels[id].toLowerCase()}.`]);
      });
      if (val('email') && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val('email'))) errs.push(['email', 'Enter an email address like name@example.com.']);
      ['date', 'end_date'].forEach(id => {
        setErr(id === 'date' ? '__none' : id, '');
        const v = val(id);
        if (v && v < new Date().toISOString().slice(0, 10)) errs.push([id, 'Choose a date that hasn’t passed yet.']);
      });
      if (val('end_date') && val('date') && val('end_date') < val('date')) errs.push(['end_date', 'The last day needs to be on or after the first day.']);
      ['link', 'photo'].forEach(id => { setErr(id, ''); if (val(id) && !/^https?:\/\/\S+\.\S+/.test(val(id))) errs.push([id, 'Enter a full link that starts with https://']); });
      setErr('cost', '');
      const cost = form.querySelector('input[name="cost"]:checked');
      if (!cost) errs.push(['cost', 'Choose whether the event is free or paid.']);
      setErr('price', '');
      if (cost && cost.value === 'Paid' && !val('price')) errs.push(['price', 'Enter the price or price range.']);
      setErr('agree', '');
      if (!form.elements.agree.checked) errs.push(['agree', 'Check the box to confirm the details are accurate.']);
      const firstFor = {};
      errs.forEach(([id, msg]) => { if (!firstFor[id]) { firstFor[id] = msg; setErr(id, msg); } });
      return Object.entries(firstFor);
    }
    function compose() {
      const v = id => (form.elements[id] && form.elements[id].value || '').trim();
      const aud = $$('input[name="audience"]:checked', form).map(i => i.value).join(', ');
      const cost = (form.querySelector('input[name="cost"]:checked') || {}).value || '';
      const when = v('date') + (v('end_date') ? ' to ' + v('end_date') : '') + ', ' + v('start') + (v('end') ? ' to ' + v('end') : '');
      return [
        'EVENT SUBMISSION: Downtown Kalamazoo events calendar', '',
        'Event: ' + v('title'), 'When: ' + when, 'Where: ' + v('venue') + ', ' + v('address'),
        'Cost: ' + cost + (v('price') ? ' (' + v('price') + ')' : ''), 'Who it’s for: ' + (aud || 'Not specified'), '',
        'Description:', v('description'), '',
        'Accessibility:', v('access') || 'Not provided', '',
        'Event link: ' + (v('link') || 'None'), 'Photo link: ' + (v('photo') || 'None'), '',
        'Submitted by: ' + v('contact') + ', ' + v('org'), 'Email: ' + v('email'), 'Phone: ' + (v('phone') || 'Not provided')
      ].join('\n');
    }
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const errs = validate();
      if (errs.length) {
        list.innerHTML = '';
        errs.forEach(([id, msg]) => {
          const li = document.createElement('li'), a = document.createElement('a');
          a.href = '#' + (id === 'cost' ? 'cost-group' : id); a.textContent = msg;
          a.addEventListener('click', ev => { ev.preventDefault(); const t = id === 'cost' ? form.querySelector('input[name="cost"]') : form.elements[id]; if (t) t.focus(); });
          li.appendChild(a); list.appendChild(li);
        });
        summary.hidden = false; summary.focus();
        return;
      }
      summary.hidden = true;
      const text = compose();
      const btn = $('#event-submit');
      if (EVENT_FORM.endpoint) {
        btn.disabled = true; btn.textContent = 'Sending…';
        try {
          const res = await fetch(EVENT_FORM.endpoint, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } });
          if (!res.ok) throw new Error(res.status);
          form.hidden = true;
          done.innerHTML = '<h2 class="h3">Thanks. Your event was sent.</h2><p>Downtown Kalamazoo staff will review it and email you to confirm the details before it is posted.</p><p><a href="events.html">Back to the events calendar</a></p>';
          done.hidden = false; done.focus();
          return;
        } catch (err) {
          btn.disabled = false; btn.textContent = 'Submit event';
        }
      }
      const subject = 'Event submission: ' + ((form.elements.title || {}).value || '');
      const mail = 'mailto:' + EVENT_FORM.to + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(text);
      form.hidden = true;
      done.innerHTML = '<h2 class="h3">One more step: send the email</h2>' +
        '<p>Your email app should open with your event filled in. Press Send there to submit it.</p>' +
        '<p>If no email opened, copy the details below and email them to <span>' + EVENT_FORM.to + '</span>.</p>' +
        '<pre id="event-text"></pre>' +
        '<div class="btn-row"><button type="button" class="btn btn-primary" id="copy-event">Copy event details</button><a class="btn" id="open-mail">Open email again</a><button type="button" class="btn btn-quiet" id="edit-event">Edit the form</button></div>';
      $('#event-text', done).textContent = text;
      $('#open-mail', done).href = mail;
      $('#copy-event', done).addEventListener('click', async ev => {
        const b = ev.currentTarget;
        try { await navigator.clipboard.writeText(text); b.textContent = 'Copied'; }
        catch (x) { const r = document.createRange(); r.selectNodeContents($('#event-text', done)); const s = getSelection(); s.removeAllRanges(); s.addRange(r); b.textContent = 'Selected, press Ctrl+C'; }
      });
      $('#edit-event', done).addEventListener('click', () => { done.hidden = true; form.hidden = false; form.elements.title.focus(); });
      done.hidden = false; done.focus();
      try { window.location.href = mail; } catch (x) {}
    });
  }

  /* ---------- Copy buttons ---------- */
  /* ---------- Ambassadors: pause or play the stats ribbon ---------- */
  $$('[data-ribbon-toggle]').forEach(btn => {
    const box = btn.closest('.amb-ribbon');
    btn.addEventListener('click', () => {
      const paused = box.classList.toggle('is-paused');
      btn.textContent = paused ? 'Play' : 'Pause';
      btn.setAttribute('aria-label', paused ? 'Play the scrolling numbers' : 'Pause the scrolling numbers');
    });
  });

  $$('[data-copy]').forEach(b => b.addEventListener('click', async () => {
    const text = b.dataset.copy;
    const label = b.textContent;
    try { await navigator.clipboard.writeText(text); b.textContent = 'Copied'; }
    catch (e) { const n = b.previousElementSibling; if (n) { const r = document.createRange(); r.selectNodeContents(n); const s = getSelection(); s.removeAllRanges(); s.addRange(r); } b.textContent = 'Selected, press Ctrl+C'; }
    setTimeout(() => { b.textContent = label; }, 2200);
  }));
})();
