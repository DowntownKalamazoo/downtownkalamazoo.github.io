/* Events calendar page: month view (full grid, or tap-a-day on narrow screens or with large text) and list view.
   Inlined into events.html by build_calendar() in yearround_section.py. */
(() => {
  'use strict';
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
  const root = document.documentElement;
  /* ---------- Events calendar: month view and list view ----------
     Month view is a full grid on wide screens. On narrow screens, or with large text, it becomes a
     tap-a-day grid: dots mark days with events, and the chosen day's events show below it. */
  (() => {
    const dataEl = $('#cal-data');
    if (!dataEl) return;
    let EVS = [];
    try { EVS = JSON.parse(dataEl.textContent || '[]'); } catch (e) { return; }
    const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    const MON = MONTHS.map(m => m.slice(0, 3));
    const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const pad = n => String(n).padStart(2, '0');
    const iso = d => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
    const parse = s => { const [y, m, d] = s.split('-').map(Number); return new Date(y, m - 1, d); };
    const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    const longDay = d => `${DAYS[d.getDay()]}, ${MONTHS[d.getMonth()]} ${d.getDate()}`;
    const plural = (n, w) => `${n} ${w}${n === 1 ? '' : 's'}`;
    const key = (y, m) => y * 12 + m;
    const now = new Date(); now.setHours(0, 0, 0, 0);
    const todayIso = iso(now);
    const [ly, lm] = dataEl.dataset.last.split('-').map(Number);
    const minK = key(now.getFullYear(), now.getMonth());
    const maxK = Math.max(key(ly, lm - 1), minK);

    const chips = $$('#cal-filter .chip'), viewBtns = $$('#cal-view button');
    const monthView = $('#cal-month-view'), listView = $('#cal-list-view'), grid = $('#cal-grid'), dayView = $('#cal-dayview');
    const title = $('#cal-title'), prev = $('#cal-prev'), next = $('#cal-next'), todayBtn = $('#cal-today');
    const status = $('#cal-status'), empty = $('#cal-empty');
    let tag = 'all', view = 'month', cur = minK, sel = todayIso, compact = null, total = 0;

    const shows = e => tag === 'all' || e.tags.includes(tag);
    // Events on one day: multi-day events first (oldest first) so their bars line up across the week.
    const on = d => d < todayIso ? [] : EVS.filter(e => shows(e) && e.s <= d && e.e >= d)
      .sort((a, b) => (b.e !== b.s) - (a.e !== a.s) || a.s.localeCompare(b.s) || (a.t + a.l).localeCompare(b.t + b.l));
    const inMonth = (y, m) => {
      const a = iso(new Date(y, m, 1)), b = iso(new Date(y, m + 1, 0));
      return EVS.filter(e => shows(e) && e.s <= b && e.e >= a && e.e >= todayIso);
    };
    const range = e => {
      const a = parse(e.s), b = parse(e.e);
      return a.getMonth() === b.getMonth() ? `${MON[a.getMonth()]} ${a.getDate()}–${b.getDate()}` : `${MON[a.getMonth()]} ${a.getDate()} – ${MON[b.getMonth()]} ${b.getDate()}`;
    };

    /* Full grid: event titles in each day, up to three, then "+ more" */
    const MAX = 3;
    function chip(e, d, col) {
      const multi = e.e !== e.s, start = e.s === d, end = e.e === d;
      // A long event shows its name where it starts, at the start of each week and on the 1st; the rest is a plain bar.
      const named = !multi || start || col === 0 || d.endsWith('-01');
      const cls = `cal-ev ${esc(e.fill)}${multi ? ' cal-bar' : ''}${start ? ' is-start' : ''}${end ? ' is-end' : ''}`;
      const text = named
        ? `<span class="n">${esc(e.t)}${multi && !start ? '<span class="sr-only"> (continues)</span>' : ''}</span>${!multi && (e.l || e.time) ? `<span class="t">${[e.l, e.time].filter(Boolean).map(esc).join(' · ')}</span>` : ''}`
        : `<span aria-hidden="true">&nbsp;</span><span class="sr-only">${esc(e.t)} (continues)</span>`;
      return `<li><a class="${cls}" href="${esc(e.href)}"${named ? '' : ' tabindex="-1"'}>${text}</a></li>`;
    }
    function table(y, m, cell, heads) {
      const lead = new Date(y, m, 1).getDay(), days = new Date(y, m + 1, 0).getDate();
      let h = `<table class="cal-grid${compact ? ' is-compact' : ''}"><caption class="sr-only">Events in ${MONTHS[m]} ${y}</caption>` +
        `<thead><tr>${DAYS.map((d, i) => `<th scope="col"><abbr title="${d}">${heads[i]}</abbr></th>`).join('')}</tr></thead><tbody>`;
      const cells = Math.ceil((lead + days) / 7) * 7;
      for (let c = 0; c < cells; c++) {
        if (c % 7 === 0) h += '<tr>';
        const n = c - lead + 1;
        h += n < 1 || n > days ? '<td class="cal-out"></td>' : cell(new Date(y, m, n), c % 7);
        if (c % 7 === 6) h += '</tr>';
      }
      return h + '</tbody></table>';
    }
    function renderFull(y, m) {
      grid.innerHTML = table(y, m, (date, col) => {
        const d = iso(date), evs = on(d), isToday = d === todayIso;
        const shown = evs.length > MAX ? evs.slice(0, MAX - 1) : evs, more = evs.length - shown.length;
        const cls = [d < todayIso && 'cal-past', isToday && 'cal-is-today'].filter(Boolean).join(' ');
        return `<td${cls ? ` class="${cls}"` : ''}><div class="cal-dnum"><span aria-hidden="true">${date.getDate()}</span>` +
          `<span class="sr-only">${longDay(date)}${isToday ? ', today' : ''}, ${evs.length ? plural(evs.length, 'event') : 'no events'}</span>` +
          `${isToday ? '<span class="cal-today-tag" aria-hidden="true">Today</span>' : ''}</div>` +
          (evs.length ? `<ul class="cal-evs">${shown.map(e => chip(e, d, col)).join('')}` +
            (more ? `<li><button type="button" class="cal-more" data-day="${d}">+${more} more<span class="sr-only"> on ${longDay(date)}</span></button></li>` : '') + '</ul>' : '') + '</td>';
      }, ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']);
      dayView.hidden = true;
    }

    /* Tap-a-day grid: one button per day, arrow keys move between days */
    function renderCompact(y, m) {
      grid.innerHTML = table(y, m, date => {
        const d = iso(date), evs = on(d), isToday = d === todayIso;
        return `<td><button type="button" class="cal-daybtn${isToday ? ' is-today' : ''}${d < todayIso ? ' is-past' : ''}" data-day="${d}" aria-pressed="${d === sel}" tabindex="${d === sel ? 0 : -1}" ` +
          `aria-label="${longDay(date)}${isToday ? ', today' : ''}, ${evs.length ? plural(evs.length, 'event') : 'no events'}">` +
          `<span class="n" aria-hidden="true">${date.getDate()}</span><span class="cal-dots" aria-hidden="true">${evs.slice(0, 3).map(e => `<i class="${esc(e.fill)}"></i>`).join('')}</span></button></td>`;
      }, ['S', 'M', 'T', 'W', 'T', 'F', 'S']);
      renderDay();
    }
    function row(e, d) {
      const multi = e.e !== e.s, cont = multi && d > e.s;
      const meta = [e.time && esc(e.time), multi && `${cont ? 'Continues · runs' : 'Runs'} ${range(e)}`, e.where && esc(e.where)].filter(Boolean);
      return `<li class="event-row cal-row ${esc(e.fill)}${cont ? ' is-cont' : ''}"><div class="body"><h4 class="h3"><a href="${esc(e.href)}">${esc(e.l ? `${e.t}: ${e.l}` : e.t)}</a></h4>` +
        `<p class="meta">${meta.map(x => `<span>${x}</span>`).join('')}</p></div></li>`;
    }
    function renderDay() {
      const date = parse(sel), evs = on(sel);
      dayView.hidden = false;
      dayView.innerHTML = `<h3 class="cal-day-head">${longDay(date)}</h3>` + (evs.length
        ? `<ul class="event-list">${evs.map(e => row(e, sel)).join('')}</ul>`
        : `<p class="muted">${sel < todayIso ? 'This day has passed.' : 'Nothing on the calendar this day.'}</p>`);
    }
    function select(d, focus) {
      sel = d;
      $$('.cal-daybtn', grid).forEach(b => { const on_ = b.dataset.day === d; b.setAttribute('aria-pressed', String(on_)); b.tabIndex = on_ ? 0 : -1; if (on_ && focus) b.focus(); });
      renderDay();
    }
    // The day picked when a month opens: today, or the month's first day with events.
    function firstDay(k) {
      const y = Math.floor(k / 12), m = k % 12, days = new Date(y, m + 1, 0).getDate();
      if (k === minK) return todayIso;
      for (let n = 1; n <= days; n++) { const d = iso(new Date(y, m, n)); if (on(d).length) return d; }
      return iso(new Date(y, m, 1));
    }

    function render(announce) {
      const y = Math.floor(cur / 12), m = cur % 12;
      title.textContent = `${MONTHS[m]} ${y}`;
      prev.disabled = cur <= minK;
      next.disabled = cur >= maxK;
      if (compact) renderCompact(y, m); else renderFull(y, m);
      if (announce) status.textContent = `${MONTHS[m]} ${y}: ${plural(inMonth(y, m).length, 'event')}`;
    }
    function go(k, focusEl) {
      cur = Math.min(maxK, Math.max(minK, k));
      sel = firstDay(cur);
      render(true);
      if (focusEl && focusEl.disabled) title.focus();
    }
    prev.addEventListener('click', () => go(cur - 1, prev));
    next.addEventListener('click', () => go(cur + 1, next));
    todayBtn.addEventListener('click', () => go(minK));

    grid.addEventListener('click', ev => {
      const day = ev.target.closest('.cal-daybtn');
      if (day) { select(day.dataset.day); return; }
      const more = ev.target.closest('.cal-more');
      if (more) showDay(more.dataset.day);
    });
    grid.addEventListener('keydown', ev => {
      const b = ev.target.closest('.cal-daybtn');
      if (!b) return;
      const d = parse(b.dataset.day), step = { ArrowLeft: -1, ArrowRight: 1, ArrowUp: -7, ArrowDown: 7 }[ev.key];
      let t;
      if (step) t = new Date(d.getFullYear(), d.getMonth(), d.getDate() + step);
      else if (ev.key === 'Home') t = new Date(d.getFullYear(), d.getMonth(), d.getDate() - d.getDay());
      else if (ev.key === 'End') t = new Date(d.getFullYear(), d.getMonth(), d.getDate() + 6 - d.getDay());
      else return;
      ev.preventDefault();
      const k = key(t.getFullYear(), t.getMonth());
      if (k < minK || k > maxK) return;
      if (k !== cur) { cur = k; sel = iso(t); render(true); $(`.cal-daybtn[data-day="${sel}"]`, grid).focus(); }
      else select(iso(t), true);
    });

    /* List view and filters */
    function showDay(d) {
      setView('list', true);
      const h = $('#dh-' + d);
      if (h) { h.closest('.cal-day').scrollIntoView({ block: 'start' }); h.focus({ preventScroll: true }); }
    }
    function applyTag(v, announce) {
      tag = v;
      chips.forEach(c => c.setAttribute('aria-pressed', String(c.dataset.tag === v)));
      const all = new Set();
      $$('.cal-month', listView).forEach(sec => {
        const seen = new Set();
        $$('.cal-day', sec).forEach(day => {
          const past = day.dataset.day < todayIso;
          let any = false;
          $$('.cal-row', day).forEach(r => {
            const ok = !past && (v === 'all' || (r.dataset.tags || '').split('|').includes(v));
            r.hidden = !ok;
            if (ok) { any = true; seen.add(r.dataset.occ); all.add(r.dataset.occ); }
          });
          day.hidden = !any;
        });
        sec.hidden = seen.size === 0;
        const c = $('.cal-count', sec); if (c) c.textContent = plural(seen.size, 'event');
      });
      total = all.size;
      empty.hidden = total > 0;
      if (view === 'month') render(false);
      if (announce) status.textContent = `Showing ${plural(total, 'event')}`;
    }
    chips.forEach(c => c.addEventListener('click', () => applyTag(c.dataset.tag, true)));

    function setView(v, save) {
      view = v;
      viewBtns.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.view === v)));
      monthView.hidden = v !== 'month';
      listView.hidden = v !== 'list';
      if (v === 'month') render(false);
      if (save) {
        try { localStorage.setItem('dk-cal-view', v); } catch (e) {}
        try { history.replaceState(null, '', v === 'list' ? '#list' : location.pathname + location.search); } catch (e) {}
      }
    }
    viewBtns.forEach(b => b.addEventListener('click', () => { setView(b.dataset.view, true); status.textContent = b.dataset.view === 'list' ? 'Showing the list of events' : `Showing ${title.textContent}`; }));

    /* Switch between the full grid and the tap-a-day grid by the space available at the current text size */
    function fit() {
      const w = (monthView.parentElement || monthView).clientWidth;
      const em = parseFloat(getComputedStyle(monthView).fontSize) || 16;
      const c = w / em < 42;
      if (c !== compact) { compact = c; if (view === 'month') render(false); }
    }
    if ('ResizeObserver' in window) new ResizeObserver(fit).observe(monthView.parentElement);
    else window.addEventListener('resize', fit);
    new MutationObserver(fit).observe(root, { attributes: true, attributeFilter: ['style', 'class'] });

    let start = 'month';
    try { start = localStorage.getItem('dk-cal-view') === 'list' ? 'list' : 'month'; } catch (e) {}
    const hash = location.hash.slice(1);
    if (hash === 'list' || /^d-\d{4}-\d{2}-\d{2}$/.test(hash)) start = 'list';
    else if (hash === 'month') start = 'month';
    applyTag('all', false);
    fit();
    setView(start, false);
    if (/^d-/.test(hash)) { const h = $('#dh-' + hash.slice(2)); if (h) h.closest('.cal-day').scrollIntoView({ block: 'start' }); }
  })();
})();
