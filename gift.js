/* Holiday Gift Guide: the fill-in-the-tag filters and "Surprise me". Without JavaScript every gift still shows. */
(function () {
  const grid = document.getElementById('gg-grid');
  if (!grid) return;
  const $ = (s, el) => (el || document).querySelector(s);
  const $$ = (s, el) => Array.from((el || document).querySelectorAll(s));
  const data = JSON.parse($('#gg-data').textContent);
  const items = $$('.gg-item', grid);
  const who = $('#gg-who'), kind = $('#gg-kind'), budget = $('#gg-budget');
  const toggles = $$('.gg-toggle');
  const count = $('#gg-count'), clearBtn = $('#gg-clear'), empty = $('#gg-empty'), emptyWhy = $('#gg-empty-why');
  const fromNote = $('#gg-from-note'), fromText = $('#gg-from-text');
  const KINDS = ['unwrap', 'experience', 'eat-drink', 'gift-card'];
  const flags = { dd: false, local: false, stocking: false, adult: false };
  let fromBiz = '';

  $('#gg-form').addEventListener('submit', e => e.preventDefault());

  function matches(li) {
    const d = li.dataset;
    if (fromBiz && d.biz !== fromBiz) return false;
    if (who.value !== 'any' && !d.who.split(' ').includes(who.value)) return false;
    if (kind.value !== 'any' && d.kind !== kind.value) return false;
    if (budget.value !== 'any' && d.band !== budget.value) return false;
    if (flags.dd && d.dd !== '1') return false;
    if (flags.local && d.local !== '1') return false;
    if (flags.stocking && d.stocking !== '1') return false;
    if (flags.adult && d.adult === '1') return false;
    return true;
  }

  function toLabel(li) {
    const w = who.value !== 'any' ? who.value : li.dataset.who.split(' ')[0];
    return data.who[w][1];
  }

  function run() {
    let n = 0;
    items.forEach(li => {
      const ok = matches(li);
      li.hidden = !ok;
      if (ok) n++;
      $('.gg-to-who', li).textContent = toLabel(li);
    });
    const active = who.value !== 'any' || kind.value !== 'any' || budget.value !== 'any' || Object.values(flags).some(Boolean);
    const forWho = who.value !== 'any' ? ' for ' + data.who[who.value][0] : '';
    count.textContent = n === items.length ? 'Showing all ' + n + ' gift ideas'
      : 'Showing ' + n + ' gift ' + (n === 1 ? 'idea' : 'ideas') + forWho;
    clearBtn.hidden = !active;
    empty.hidden = n > 0;
    emptyWhy.textContent = budget.value !== 'any'
      ? 'Many businesses haven’t shared prices yet, so choosing an amount hides a lot of gifts. Try “any amount,” or turn off a choice.'
      : 'Try another blank, or turn off a choice. Downtown Dollars fit every tag.';
    toggles.forEach(t => t.setAttribute('aria-pressed', String(flags[t.dataset.flag])));
    fromNote.hidden = !fromBiz;
  }

  function clearAll() {
    who.value = 'any'; kind.value = 'any'; budget.value = 'any';
    Object.keys(flags).forEach(k => { flags[k] = false; });
    fromBiz = '';
    run();
  }

  [who, kind, budget].forEach(s => s.addEventListener('change', run));
  toggles.forEach(t => t.addEventListener('click', () => { flags[t.dataset.flag] = !flags[t.dataset.flag]; run(); }));
  clearBtn.addEventListener('click', () => { clearAll(); fitAll(); who.focus(); });
  $('#gg-empty-clear').addEventListener('click', () => { clearAll(); fitAll(); who.focus(); });
  $('#gg-from-all').addEventListener('click', () => {
    fromBiz = '';
    try { history.replaceState(null, '', location.pathname + location.search); } catch (e) {}
    run();
    count.setAttribute('tabindex', '-1');
    count.focus();
  });

  // Each blank is only as wide as the words chosen in it, so the sentence reads like a sentence
  const blanks = [who, kind, budget];
  const meas = document.createElement('span');
  meas.setAttribute('aria-hidden', 'true');
  meas.style.cssText = 'position:absolute;left:-9999px;top:0;visibility:hidden;white-space:pre';
  document.body.appendChild(meas);
  function fit(sel) {
    const cs = getComputedStyle(sel);
    meas.style.font = cs.fontStyle + ' ' + cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily;
    meas.style.letterSpacing = cs.letterSpacing;
    meas.textContent = sel.options[sel.selectedIndex].text;
    sel.style.width = Math.ceil(meas.getBoundingClientRect().width + parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight) + 6) + 'px';
  }
  const fitAll = () => blanks.forEach(fit);
  blanks.forEach(s => s.addEventListener('change', () => fit(s)));
  let rt; window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(fitAll, 150); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitAll);

  // Links from plans and the directory: gifts.html#foodie, #experience, #stocking, #dollars or #from-<directory id>
  function applyHash() {
    const hash = decodeURIComponent((location.hash || '').slice(1));
    if (data.who[hash]) who.value = hash;
    else if (KINDS.includes(hash)) kind.value = hash;
    else if (hash === 'stocking') flags.stocking = true;
    else if (hash === 'dollars') flags.dd = true;
    else if (hash.indexOf('from-') === 0) {
      const id = hash.slice(5);
      const first = items.find(li => li.dataset.biz === id);
      if (first) { fromBiz = id; fromText.textContent = 'Showing gifts from ' + first.dataset.bizname + '.'; }
    }
  }
  applyHash();
  run();
  fitAll();
  window.addEventListener('hashchange', () => { clearAll(); applyHash(); run(); fitAll(); });

  // Surprise me: picks one of the gifts that fit the tag, and shows it in place of the present
  const spot = $('#gg-spot'), pkg = $('#gg-package'), sText = $('#gg-surprise-text'), sBtn = $('#gg-surprise'), sStatus = $('#gg-spot-status');
  let picked = null;
  sBtn.addEventListener('click', () => {
    let pool = items.filter(li => !li.hidden);
    if (!pool.length) pool = items.slice();
    if (pool.length > 1 && picked) pool = pool.filter(li => li !== picked);
    const li = pool[Math.floor(Math.random() * pool.length)];
    if (picked) { picked.classList.remove('is-picked'); $('.gg-pick', picked).hidden = true; }
    picked = li;
    li.classList.add('is-picked');
    $('.gg-pick', li).hidden = false;
    const card = $('.gg-tag', li).cloneNode(true);
    card.removeAttribute('aria-labelledby');
    $$('[id]', card).forEach(el => el.removeAttribute('id'));
    const h3 = $('.gg-name', card), h2 = document.createElement('h2');
    h2.className = h3.className; h2.textContent = h3.textContent; h3.replaceWith(h2);
    spot.replaceChildren(card);
    spot.hidden = false; pkg.hidden = true; sText.hidden = true;
    sBtn.textContent = 'Pick another';
    sStatus.textContent = 'Downtown picked ' + h2.textContent + ', from ' + li.dataset.bizname + '.';
  });
})();
