// Brandaz — comportamento comum a todas as páginas (cabeçalho, régua A–Z, revelações, esteiras, janela de mídia, filtros, formulário).
(() => {
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const BZ = window.BZ = { $, $$, still: false, onStill: [], onScroll: [], casePaused: false };
  try { BZ.still = localStorage.getItem('bz-still') === '1' } catch (e) {}

  // pausar movimento (filmes, esteiras, partículas)
  const mot = $('#mot');
  BZ.setStill = v => {
    BZ.still = v; document.documentElement.classList.toggle('still', v);
    if (mot) { mot.setAttribute('aria-pressed', v); mot.textContent = v ? 'Retomar movimento' : 'Pausar movimento' }
    try { localStorage.setItem('bz-still', v ? '1' : '0') } catch (e) {}
    BZ.onStill.forEach(f => f(v));
  };
  if (mot) mot.onclick = () => BZ.setStill(!BZ.still);
  document.documentElement.classList.toggle('still', BZ.still);

  // cabeçalho: some ao descer, volta ao subir; barra de leitura; WhatsApp flutuante
  const hdr = $('#hdr'), prog = $('#prog'), fwa = $('#floatWa'); let lastY = scrollY;
  function header() {
    const y = scrollY; hdr.dataset.scrolled = y > 40;
    if (y < 80 || document.body.classList.contains('menu-open')) hdr.classList.remove('hide');
    else if (y > lastY + 4) hdr.classList.add('hide'); else if (y < lastY - 4) hdr.classList.remove('hide');
    lastY = y;
    const max = document.documentElement.scrollHeight - innerHeight; prog.style.transform = `scaleX(${max > 0 ? y / max : 0})`;
    const on = y > Math.min(innerHeight * .7, 600); fwa.classList.toggle('on', on); fwa.tabIndex = on ? 0 : -1;
  }

  // menu no celular
  const mb = $('#menuBtn'), mm = $('#mm');
  const menu = open => {
    mm.classList.toggle('open', open); mm.setAttribute('aria-hidden', !open); mb.setAttribute('aria-expanded', open);
    document.body.classList.toggle('menu-open', open); document.body.style.overflow = open ? 'hidden' : '';
    if (open) $('#mmX').focus(); else mb.focus();
  };
  mb.onclick = () => menu(true); $('#mmX').onclick = () => menu(false);
  $$('a', mm).forEach(a => a.addEventListener('click', () => menu(false)));

  // títulos sobem linha a linha; blocos entram ao chegar na tela
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target) } }), { threshold: .15 });
  $$('.editorial-title,.reveal,[data-reveal],[data-deck]').forEach(el => io.observe(el));

  // régua A–Z: avança com a leitura e mostra o capítulo atual
  const letters = $$('.az i'), hudL = $('#hudL'), hudT = $('#hudT'), chs = $$('[data-ch]'), rail = $('.az-rail');
  function hud() {
    if (!rail) return;
    const max = document.documentElement.scrollHeight - innerHeight, p = max > 0 ? scrollY / max : 0, n = Math.min(25, Math.floor(p * 25.999));
    letters.forEach((l, i) => { l.classList.toggle('on', i < n); l.classList.toggle('cur', i === n) });
    hudL.textContent = String.fromCharCode(65 + n);
    let cur = chs.length ? chs[0].dataset.ch : ''; chs.forEach(c => { if (c.getBoundingClientRect().top < innerHeight * .5) cur = c.dataset.ch }); hudT.textContent = cur;
    const under = document.elementFromPoint(innerWidth - 24, innerHeight / 2);
    rail.classList.toggle('on-paper', !!(under && under.closest('.bg-paper')));
  }

  // frases que acendem palavra por palavra
  const scrubs = $$('[data-scrub]').map(el => ({ el, w: $$('.w', el) }));
  function scrub() {
    scrubs.forEach(({ el, w }) => {
      const r = el.getBoundingClientRect(), a = innerHeight * .9, b = innerHeight * .45;
      const p = Math.min(1, Math.max(0, (a - r.top) / ((a - b) + r.height))); const n = p * w.length;
      w.forEach((x, i) => x.classList.toggle('on', i < n));
    });
  }

  // trajeto do método: a linha se desenha com o scroll e acende as etapas
  const paths = $$('[data-method]').map(box => {
    const svg = $('.method-svg', box), base = $('.method-line-base', svg), act = $('.method-line-active', svg), nodes = $$('.method-node', box);
    let len = 0, stops = [];
    function build() {
      const r = box.getBoundingClientRect(); svg.setAttribute('viewBox', `0 0 ${r.width} ${r.height}`);
      const pts = nodes.map(n => { const d = $('.method-dot', n).getBoundingClientRect(); return [d.left - r.left + d.width / 2, d.top - r.top + d.height / 2] });
      let d = `M${pts[0][0]},${pts[0][1]}`;
      for (let i = 0; i < pts.length - 1; i++) { const p0 = pts[i - 1] || pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] || p2; d += ` C${p1[0] + (p2[0] - p0[0]) / 6},${p1[1] + (p2[1] - p0[1]) / 6} ${p2[0] - (p3[0] - p1[0]) / 6},${p2[1] - (p3[1] - p1[1]) / 6} ${p2[0]},${p2[1]}` }
      base.setAttribute('d', d); act.setAttribute('d', d); len = act.getTotalLength(); act.style.strokeDasharray = len;
      // comprimento do trajeto em cada etapa
      stops = pts.map(p => { let best = 0, bd = 1e9; for (let l = 0; l <= len; l += 4) { const q = act.getPointAtLength(l), dd = (q.x - p[0]) ** 2 + (q.y - p[1]) ** 2; if (dd < bd) { bd = dd; best = l } } return best });
      draw();
    }
    function draw() {
      if (!len) return; const r = box.getBoundingClientRect();
      const p = Math.min(1, Math.max(0, (innerHeight * .78 - r.top) / (r.height * .9))), l = p * len;
      act.style.strokeDashoffset = len - l; nodes.forEach((n, i) => n.classList.toggle('on', l >= stops[i] - 2));
    }
    return { build, draw };
  });

  // números dos resultados contam até o valor final
  const fmt = (n, dec) => n.toLocaleString('pt-BR', { minimumFractionDigits: dec, maximumFractionDigits: dec });
  const cio = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return; cio.unobserve(e.target);
    const el = e.target, raw = el.dataset.count, m = raw.match(/[\d.,]+/); if (!m || BZ.still) return;
    const pre = raw.slice(0, m.index), suf = raw.slice(m.index + m[0].length), dec = (m[0].split(',')[1] || '').length;
    const target = parseFloat(m[0].replace(/\./g, '').replace(',', '.')); const t0 = performance.now();
    (function f(t) { const k = Math.min(1, (t - t0) / 1400), v = target * (1 - Math.pow(1 - k, 3)); el.textContent = pre + fmt(v, dec) + suf; if (k < 1) requestAnimationFrame(f); else el.textContent = raw })(t0);
  }), { threshold: .6 });
  $$('[data-count]').forEach(el => cio.observe(el));

  // esteiras: velocidade constante, param no hover, arrastam com o mouse/dedo
  BZ.belt = (row, speed, getPaused = () => false) => {
    const track = row.querySelector('.case-marquee-track,.belt-track'), group = track.firstElementChild;
    let x = 0, v = 0, w = 0, vis = false, hov = false, drag = null, last = performance.now();
    new ResizeObserver(() => { w = group.getBoundingClientRect().width }).observe(group);
    new IntersectionObserver(([e]) => vis = e.isIntersecting).observe(row);
    const norm = val => w ? (((val % w) + w) % w) - w : val;
    row.addEventListener('pointerover', e => { if (e.pointerType === 'mouse') hov = true });
    row.addEventListener('pointerleave', () => hov = false);
    row.addEventListener('pointerdown', e => { if (e.button !== 0) return; drag = { s: e.clientX, l: e.clientX, m: false } });
    row.addEventListener('pointermove', e => { if (!drag) return; if (Math.abs(e.clientX - drag.s) > 6 && !drag.m) { drag.m = true; row.setPointerCapture(e.pointerId) } if (drag.m) { x = norm(x + e.clientX - drag.l); v = 0 } drag.l = e.clientX });
    row.addEventListener('pointerup', () => { if (drag && drag.m) row.dataset.sup = '1'; drag = null });
    row.addEventListener('pointercancel', () => drag = null);
    row.addEventListener('click', e => { if (row.dataset.sup) { e.preventDefault(); e.stopPropagation(); delete row.dataset.sup } }, true);
    (function f(t) {
      const s = Math.min(t - last, 50) / 1000; last = t;
      if (vis && w) { const stop = BZ.still || getPaused() || hov || drag; v += ((stop ? 0 : speed) - v) * (1 - Math.exp(-s * 8)); if (!drag) x = norm(x + v * s); track.style.transform = `translateX(${x}px)` }
      requestAnimationFrame(f);
    })(last);
  };
  $$('[data-speed]').forEach(r => BZ.belt(r, +r.dataset.speed, r.hasAttribute('data-pausable') ? () => BZ.casePaused : undefined));
  const cp = $('#casePause');
  if (cp) cp.onclick = () => {
    BZ.casePaused = !BZ.casePaused; cp.setAttribute('aria-pressed', BZ.casePaused);
    cp.setAttribute('aria-label', BZ.casePaused ? 'Reproduzir esteira de cases' : 'Pausar esteira de cases');
    cp.innerHTML = BZ.casePaused ? cp.dataset.play : cp.dataset.pause;
  };

  // filmes em streaming (HLS): Safari toca direto; os outros navegadores carregam o hls.js só quando um filme é aberto
  const HLS_SRC = ((document.currentScript && document.currentScript.src) || '').replace(/site\.js(\?.*)?$/, 'vendor/hls.min.js');
  let hlsLib = null;
  const loadHls = () => window.Hls ? Promise.resolve(window.Hls) : (hlsLib = hlsLib || new Promise((ok, err) => {
    const s = document.createElement('script'); s.src = HLS_SRC; s.onload = () => ok(window.Hls); s.onerror = err; document.head.appendChild(s);
  }));
  BZ.playStream = (video, src) => {
    if (!/\.m3u8$/.test(src) || video.canPlayType('application/vnd.apple.mpegurl')) { video.src = src; video.play().catch(() => {}); return }
    loadHls().then(Hls => {
      if (!Hls.isSupported()) return;
      // começa na qualidade máxima em conexões boas e ajusta sozinho se a internet cair
      const h = new Hls({ abrEwmaDefaultEstimate: 8e6, capLevelToPlayerSize: false, maxBufferLength: 30 });
      h.loadSource(src); h.attachMedia(video); video._hls = h;
      h.on(Hls.Events.MANIFEST_PARSED, () => video.play().catch(() => {}));
    });
  };
  const stopMedia = () => { const v = media && media.querySelector('video'); if (v && v._hls) v._hls.destroy(); if (v) v.pause() };

  // janela de mídia: fotos e filmes (com som) ampliados, com navegação
  const dlg = document.createElement('div'); dlg.className = 'dlg'; dlg.hidden = true;
  dlg.innerHTML = '<div class="dbox" role="dialog" aria-modal="true" aria-label="Mídia ampliada"><button type="button" class="x" aria-label="Fechar">×</button><div class="media"></div><p class="cap"></p></div><button type="button" class="nav prev" aria-label="Anterior">‹</button><button type="button" class="nav next" aria-label="Próximo">›</button>';
  document.body.appendChild(dlg);
  const box = $('.dbox', dlg), media = $('.media', dlg), cap = $('.cap', dlg); let group = [], gi = 0, opener = null;
  function show(i) {
    stopMedia(); gi = (i + group.length) % group.length; const it = group[gi], d = it.dataset;
    box.classList.toggle('film', 'vertical' in d);
    media.innerHTML = d.type === 'video'
      ? `<video ${d.poster ? `poster="${d.poster}"` : ''} controls controlslist="nodownload noplaybackrate noremoteplayback" disablepictureinpicture disableremoteplayback autoplay playsinline></video>`
      : `<img src="${d.src}" alt="">`;
    const im = media.firstElementChild; if (d.type !== 'video') im.alt = d.cap || '';
    cap.textContent = d.cap || ''; $$('.nav', dlg).forEach(b => b.hidden = group.length < 2);
    if (d.type === 'video') BZ.playStream(im, d.src);
  }
  function close() { stopMedia(); dlg.hidden = true; media.innerHTML = ''; document.body.style.overflow = ''; opener && opener.focus() }
  document.addEventListener('click', e => {
    const t = e.target.closest('[data-lb]'); if (!t) return; e.preventDefault();
    group = $$(`[data-lb="${t.dataset.lb}"]`).filter(x => !x.closest('[aria-hidden="true"]'));
    opener = t; let i = group.indexOf(t); if (i < 0) { group.push(t); i = group.length - 1 }
    dlg.hidden = false; document.body.style.overflow = 'hidden'; show(i); $('.x', dlg).focus();
  });
  $('.x', dlg).onclick = close; $('.prev', dlg).onclick = () => show(gi - 1); $('.next', dlg).onclick = () => show(gi + 1);
  dlg.addEventListener('click', e => { if (e.target === dlg) close() });
  addEventListener('keydown', e => {
    if (e.key === 'Escape') { if (!dlg.hidden) close(); else if (mm.classList.contains('open')) menu(false) }
    if (!dlg.hidden && group.length > 1) { if (e.key === 'ArrowRight') show(gi + 1); if (e.key === 'ArrowLeft') show(gi - 1) }
  });

  // portfólio: filtros por segmento e escopo + "Carregar mais"
  const grid = $('#projGrid');
  if (grid) {
    const items = $$('.proj-item', grid), more = $('#loadMore'), count = $('#projCount'), seg = $('#segSel'), scopeBtns = $$('[data-scope]');
    let scope = '', shown = 12;
    function apply() {
      const s = seg.value, match = items.filter(it => (!s || it.dataset.seg === s) && (!scope || it.dataset.scopes.split('|').includes(scope)));
      items.forEach(it => it.hidden = true); match.slice(0, shown).forEach(it => it.hidden = false);
      more.hidden = match.length <= shown; count.textContent = `${Math.min(shown, match.length)} de ${match.length} ${match.length === 1 ? "projeto" : "projetos"}`;
    }
    seg.onchange = () => { shown = 12; apply() };
    scopeBtns.forEach(b => b.onclick = () => { scope = b.dataset.scope; scopeBtns.forEach(x => x.setAttribute('aria-pressed', x === b)); shown = 12; apply() });
    more.onclick = () => { shown += 12; apply() };
    apply();
  }

  // blog: filtro por categoria
  const posts = $$('.post-card[data-cat]'), catBtns = $$('[data-cat-btn]');
  catBtns.forEach(b => b.onclick = () => { const c = b.dataset.catBtn; catBtns.forEach(x => x.setAttribute('aria-pressed', x === b)); posts.forEach(p => p.hidden = !!c && p.dataset.cat !== c) });

  // contato: o formulário monta a mensagem e abre o WhatsApp
  const form = $('#waForm');
  if (form) form.addEventListener('submit', e => {
    e.preventDefault(); const f = new FormData(form), v = k => (f.get(k) || '').toString().trim();
    let msg = `Olá, Brandaz! Sou ${v('nome')}`; if (v('empresa')) msg += ` da ${v('empresa')}`; msg += '.';
    if (v('escopo')) msg += ` Gostaria de falar sobre ${v('escopo')}.`; if (v('mensagem')) msg += ` ${v('mensagem')}`;
    const url = `${form.dataset.wa}?text=${encodeURIComponent(msg)}`, link = $('#waOut');
    link.href = url; link.hidden = false; link.click();
  });

  // proteção do material: sem "salvar como" no clique direito e sem arrastar fotos e vídeos para fora da página
  const media_sel = 'img,video,picture,.g-item,.cinema-reel,.wf,.office-portal,.case-marquee-card,.project-media,.dlg .media';
  document.addEventListener('contextmenu', e => { if (e.target.closest && e.target.closest(media_sel)) e.preventDefault() });
  document.addEventListener('dragstart', e => { if (e.target.closest && e.target.closest(media_sel)) e.preventDefault() });

  // botões magnéticos
  if (matchMedia('(hover: hover) and (pointer: fine)').matches) {
    let act = null;
    document.addEventListener('pointermove', e => {
      const t = e.target.closest && e.target.closest('[data-slot="button"]');
      if (t !== act && act) act.style.translate = ''; act = t; if (!t) return;
      const r = t.getBoundingClientRect(); t.style.translate = `${(e.clientX - r.left - r.width / 2) * .12}px ${(e.clientY - r.top - r.height / 2) * .12}px`;
    });
  }

  function onScroll() { header(); hud(); scrub(); paths.forEach(p => p.draw()); BZ.onScroll.forEach(f => f()) }
  addEventListener('scroll', onScroll, { passive: true });
  const relayout = () => { paths.forEach(p => p.build()); onScroll() };
  addEventListener('resize', () => { clearTimeout(BZ._rt); BZ._rt = setTimeout(relayout, 150) });
  addEventListener('load', relayout); document.fonts && document.fonts.ready.then(relayout);
  BZ.relayout = relayout; relayout();
})();
