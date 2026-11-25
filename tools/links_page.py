"""Página de links da bio do Instagram (brandaz.com.br/contatos).

Página avulsa, sem o cabeçalho do site: logo, chamada, botões (lidos de content/links.json) e redes no rodapé.
O fundo é um céu de partículas que reage ao toque/mouse; os botões têm vidro, brilho que segue o cursor e faíscas.
"""
import json
from datetime import date

LINE = ' fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"'


def _ic(body, fill=False):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true"{" fill=currentColor" if fill else LINE}>{body}</svg>'


ICONS = {
    'whatsapp': _ic('<path d="M3.5 20.5l1.2-4.2A8.5 8.5 0 1 1 8 19.6z"/><path d="M9 8.6c0 3.5 2.9 6.4 6.4 6.4l1.1-1.6-2-.9-1 1c-1.2-.5-2.1-1.4-2.6-2.6l1-1-.9-2z"/>'),
    'site': _ic('<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.8 3.9 5.8 3.9 9s-1.3 6.2-3.9 9c-2.6-2.8-3.9-5.8-3.9-9S9.4 5.8 12 3z"/>'),
    'projetos': _ic('<rect x="3" y="7" width="18" height="13" rx="2.5"/><path d="M9 7V5.5A1.5 1.5 0 0 1 10.5 4h3A1.5 1.5 0 0 1 15 5.5V7M3 12.5h18"/>'),
    'apresentacao': _ic('<path d="M6 3h8l4 4v12.5A1.5 1.5 0 0 1 16.5 21h-10A1.5 1.5 0 0 1 5 19.5v-15A1.5 1.5 0 0 1 6.5 3z"/><path d="M14 3v4h4M8.5 12h7M8.5 15.5h5"/>'),
    'vagas': _ic('<circle cx="9" cy="8" r="3.2"/><path d="M3 20c.6-3.4 3-5.4 6-5.4s5.4 2 6 5.4"/><circle cx="17" cy="9" r="2.4"/><path d="M16.5 14.4c2.4.2 4 1.9 4.5 4.6"/>'),
    'mapa': _ic('<path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>'),
    'estrela': _ic('<path d="M12 3l1.9 6.1L20 12l-6.1 1.9L12 20l-1.9-6.1L4 12l6.1-1.9z"/>'),
    'calendario': _ic('<rect x="3.5" y="5" width="17" height="15.5" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/>'),
    'megafone': _ic('<path d="M4 10v4a1 1 0 0 0 1 1h2l6 4V5L7 9H5a1 1 0 0 0-1 1zM17 9a4 4 0 0 1 0 6"/>'),
}
SOCIAL = {
    'instagram': _ic('<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".7" fill="currentColor"/>'),
    'facebook': _ic('<path d="M14 8.5h3V5h-3c-2.6 0-4 1.7-4 4.2V11H7.5v3.5H10V21h3.6v-6.5H16l.6-3.5h-3V9.4c0-.5.3-.9.9-.9z"/>', True),
    'behance': _ic('<path d="M3 6h5.2c2 0 3.3 1 3.3 2.7 0 1.1-.6 1.9-1.5 2.2 1.2.3 2 1.3 2 2.6 0 2-1.5 3.2-3.7 3.2H3zm2.4 4.3h2.4c.9 0 1.4-.4 1.4-1.1s-.5-1.1-1.4-1.1H5.4zm0 4.6h2.6c1 0 1.6-.5 1.6-1.3s-.6-1.3-1.6-1.3H5.4zM14.5 7.2h5.3v1.3h-5.3zM17.2 9.6c2.4 0 3.7 1.6 3.6 4.2h-5.4c.1 1.2.8 1.8 1.9 1.8.8 0 1.3-.3 1.6-.9h1.8c-.5 1.6-1.8 2.4-3.5 2.4-2.3 0-3.7-1.5-3.7-3.8 0-2.2 1.5-3.7 3.7-3.7zm1.7 3c-.1-1-.7-1.6-1.7-1.6s-1.6.6-1.8 1.6z"/>', True),
    'linkedin': _ic('<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 10.5V17M8 7.5v.01M12 17v-3.6c0-1.6 1-2.6 2.3-2.6s2 .9 2 2.6V17M12 10.5V17"/>'),
    'youtube': _ic('<rect x="2.5" y="5.5" width="19" height="13" rx="4"/><path d="M10.5 9.5v5l4.3-2.5z" fill="currentColor"/>'),
}
ARROW = _ic('<path d="M7 17 17 7M9 7h8v8"/>')

CSS = r'''
@font-face{font-family:"Grift";font-weight:400;font-display:swap;src:url(/assets/fonts/grift-400.woff2?v=2) format("woff2")}
@font-face{font-family:"Grift";font-weight:600;font-display:swap;src:url(/assets/fonts/grift-600.woff2?v=2) format("woff2")}
@font-face{font-family:"Grift";font-weight:800;font-display:swap;src:url(/assets/fonts/grift-800.woff2?v=2) format("woff2")}
:root{--purple:#341131;--deep:#1d0f1e;--orange:#D77F4E;--gold:#ffc48c;--lilac:#EAE8EE;--muted:rgba(234,232,238,.62);color-scheme:dark}
*{box-sizing:border-box;margin:0}
html,body{min-height:100%}
body{background:var(--deep);color:var(--lilac);font:400 16px/1.45 "Grift",system-ui,sans-serif;-webkit-font-smoothing:antialiased;overflow-x:hidden}
body::before{content:"";position:fixed;inset:0;z-index:-2;background:radial-gradient(120% 70% at 50% -10%,#5a1f50 0%,var(--purple) 38%,var(--deep) 78%)}
#sky{position:fixed;inset:0;z-index:-1;width:100%;height:100%;pointer-events:none}
a{color:inherit;text-decoration:none}
.wrap{position:relative;width:min(560px,100%);margin:0 auto;padding:calc(40px + env(safe-area-inset-top,0px)) max(18px,env(safe-area-inset-right,0px)) calc(28px + env(safe-area-inset-bottom,0px)) max(18px,env(safe-area-inset-left,0px));display:flex;flex-direction:column;align-items:center;min-height:100svh}
/* cabeçalho: logo com halo e órbita de faíscas */
.crest{position:relative;width:230px;height:150px;display:grid;place-items:center;margin-bottom:6px}
.crest::before{content:"";position:absolute;inset:-10% -14%;border-radius:50%;background:radial-gradient(closest-side,rgba(215,127,78,.38),rgba(215,127,78,.08) 60%,transparent);filter:blur(6px);animation:halo 5s ease-in-out infinite}
.crest img{position:relative;width:210px;height:auto;filter:drop-shadow(0 6px 22px rgba(0,0,0,.45))}
.orbit{position:absolute;inset:-6px -20px;border-radius:50%;animation:spin 16s linear infinite}
.orbit i{position:absolute;width:9px;height:9px;background:#fff1de;clip-path:polygon(50% 0,60% 40%,100% 50%,60% 60%,50% 100%,40% 60%,0 50%,40% 40%);filter:drop-shadow(0 0 5px var(--gold))}
.orbit i:nth-child(1){left:6%;top:42%}.orbit i:nth-child(2){right:3%;top:24%;width:12px;height:12px}.orbit i:nth-child(3){left:58%;bottom:-2%;width:7px;height:7px}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes halo{50%{opacity:.65;transform:scale(1.06)}}
.kicker{font-size:12.5px;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:#f0a477;text-align:center}
.motto{margin-top:8px;font-size:clamp(22px,6.4vw,28px);font-weight:800;line-height:1.1;text-align:center;text-transform:uppercase;text-wrap:balance}
.motto em{font-style:normal;color:transparent;background:linear-gradient(100deg,var(--orange) 20%,#ffe3c6 45%,var(--orange) 70%) 0 0/250% 100%;-webkit-background-clip:text;background-clip:text;animation:shine 4.5s ease-in-out infinite}
@keyframes shine{0%,100%{background-position:100% 0}50%{background-position:0 0}}
/* botões */
.links{width:100%;display:flex;flex-direction:column;gap:12px;margin:30px 0 26px;padding:0;list-style:none}
.lk{--mx:50%;--my:50%;position:relative;isolation:isolate;overflow:hidden;display:grid;grid-template-columns:46px 1fr 22px;align-items:center;gap:14px;min-height:68px;padding:12px 16px 12px 12px;border-radius:18px;
  background:linear-gradient(140deg,rgba(255,255,255,.085),rgba(255,255,255,.025));border:1px solid rgba(234,232,238,.13);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
  box-shadow:0 10px 30px rgba(10,3,10,.28);transition:transform .45s cubic-bezier(.22,1,.36,1),border-color .4s,box-shadow .4s;animation:rise .8s cubic-bezier(.22,1,.36,1) both;animation-delay:calc(.25s + var(--i)*.08s);-webkit-tap-highlight-color:transparent}
@keyframes rise{from{opacity:0;translate:0 16px}}
.lk::before{content:"";position:absolute;inset:0;z-index:-1;background:radial-gradient(220px circle at var(--mx) var(--my),rgba(215,127,78,.36),transparent 65%);opacity:0;transition:opacity .4s}
.lk::after{content:"";position:absolute;inset:0;border-radius:inherit;padding:1px;background:radial-gradient(180px circle at var(--mx) var(--my),rgba(255,214,170,.95),transparent 60%);-webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask:linear-gradient(#000 0 0) content-box exclude,linear-gradient(#000 0 0);opacity:0;transition:opacity .4s;pointer-events:none}
.lk:focus-visible::before,.lk:focus-visible::after{opacity:1}
@media (hover:hover){.lk:hover::before,.lk:hover::after{opacity:1}.lk:hover{transform:translateY(-3px);box-shadow:0 18px 40px rgba(10,3,10,.4),0 0 30px rgba(215,127,78,.18)}.lk:hover .ico{transform:rotate(-8deg) scale(1.08)}.lk:hover .go{transform:translate(2px,-2px);color:var(--lilac)}.social a:hover{transform:translateY(-3px);background:var(--orange);border-color:var(--orange);color:#2a0f27}}
.lk:active{transform:scale(.985);transition-duration:.12s}
.lk:focus-visible{outline:2px solid var(--gold);outline-offset:3px}
.lk .ico{width:46px;height:46px;border-radius:14px;display:grid;place-items:center;background:rgba(215,127,78,.14);color:var(--orange);transition:transform .45s cubic-bezier(.22,1,.36,1)}
.lk .ico svg{width:23px;height:23px}
.lk b{display:block;font-size:16.5px;font-weight:800;line-height:1.2}
.lk small{display:block;margin-top:2px;font-size:13px;color:var(--muted)}
.lk .go{width:20px;height:20px;color:var(--muted);transition:transform .4s,color .4s}
/* destaque: comercial */
.lk.hot{min-height:80px;background:linear-gradient(120deg,#e6915e,#dc8452 50%,#cf7642);border-color:rgba(255,220,190,.55);color:#2a0f27;box-shadow:0 14px 40px rgba(215,127,78,.35)}
.lk.hot::before{background:radial-gradient(220px circle at var(--mx) var(--my),rgba(255,244,230,.55),transparent 62%)}
.lk.hot .ico{background:rgba(42,15,39,.14);color:#2a0f27}
.lk.hot small{color:#2a0f27;opacity:.88}.lk.hot .go{color:rgba(42,15,39,.72)}
.lk.hot b{font-size:18px}
.lk.hot .shine{position:absolute;inset:0;z-index:-1;background:linear-gradient(105deg,transparent 35%,rgba(255,255,255,.45) 50%,transparent 65%) -150% 0/60% 100% no-repeat;animation:sweep 3.6s ease-in-out 1.2s infinite}
@keyframes sweep{0%{background-position:-150% 0}55%,100%{background-position:250% 0}}
.lk.hot .ping{position:absolute;left:52px;top:14px;width:10px;height:10px;border-radius:50%;background:#3ddc84;box-shadow:0 0 0 2px #e08a57}
.lk.hot .ping::after{content:"";position:absolute;inset:0;border-radius:50%;background:#3ddc84;animation:ping 1.8s ease-out infinite}
@keyframes ping{to{transform:scale(3);opacity:0}}
.spk{position:absolute;z-index:0;width:var(--sz);height:var(--sz);margin:calc(var(--sz)/-2) 0 0 calc(var(--sz)/-2);background:#ffe6cc;clip-path:polygon(50% 0,58% 42%,100% 50%,58% 58%,50% 100%,42% 58%,0 50%,42% 42%);filter:drop-shadow(0 0 4px #ffae74);pointer-events:none;animation:spk var(--t,1s) ease-out forwards}
.spk.dot{clip-path:circle(50%)}
.toast{position:fixed;left:50%;bottom:calc(24px + env(safe-area-inset-bottom,0px));translate:-50% 20px;opacity:0;padding:12px 18px;border-radius:999px;background:var(--lilac);color:#2a0f27;font-weight:600;font-size:14px;transition:opacity .3s,translate .3s;pointer-events:none;z-index:5}.toast.on{opacity:1;translate:-50% 0}
@keyframes spk{0%{opacity:0;transform:scale(.2)}15%{opacity:1;transform:scale(1)}100%{opacity:0;transform:translate(var(--dx),var(--dy)) scale(.3) rotate(140deg)}}
/* rodapé */
.social{display:flex;gap:12px;margin-top:auto}
.social a{width:48px;height:48px;border-radius:50%;display:grid;place-items:center;border:1px solid rgba(234,232,238,.18);background:rgba(255,255,255,.04);color:var(--lilac);transition:transform .35s,background .35s,color .35s,border-color .35s}
.social a:focus-visible{transform:translateY(-3px);background:var(--orange);border-color:var(--orange);color:#2a0f27}
.social svg{width:21px;height:21px}
.copy{margin-top:18px;font-size:12.5px;color:var(--muted);text-align:center}
.copy a{border-bottom:1px solid rgba(234,232,238,.25)}
@media (min-width:768px){.wrap{padding-top:64px}.crest{width:260px;height:170px}.crest img{width:236px}.links{gap:14px}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}.lk{opacity:1;transform:none}}
'''

JS = r'''
(()=>{const still=matchMedia('(prefers-reduced-motion: reduce)').matches;
// céu de partículas: estrelas que cintilam, poeira laranja subindo e um rastro que segue o dedo/mouse
const cv=document.getElementById('sky'),g=cv.getContext('2d'),D=Math.min(2,devicePixelRatio||1);let W,H,P=[],T=[],LW=0;
function size(){W=innerWidth;H=innerHeight;cv.width=W*D;cv.height=H*D;g.setTransform(D,0,0,D,0,0);if(W===LW&&P.length)return;LW=W;
  const n=Math.round(Math.min(220,W*H/5200));P=Array.from({length:n},()=>({x:Math.random()*W,y:Math.random()*H,z:Math.random(),r:Math.random()*6.28,s:.15+Math.random()*.5,o:Math.random()<.7}))}
size();addEventListener('resize',size);
let mx=-1e3,my=-1e3,last=0;const move=e=>{mx=e.clientX;my=e.clientY;const t=performance.now();if(!still&&t-last>16){last=t;for(let k=0;k<2;k++)T.push({x:mx,y:my,vx:(Math.random()-.5)*1.2,vy:-.4-Math.random()*1.2,l:1})}};
addEventListener('pointermove',move,{passive:true});
function frame(t){if(!still)requestAnimationFrame(frame);const s=t/1000;g.clearRect(0,0,W,H);g.globalCompositeOperation='lighter';
  for(const p of P){if(!still){p.y-=p.s*(p.o?.5:.15)*(1+p.z);if(p.y<-4){p.y=H+4;p.x=Math.random()*W}}
    const dx=p.x-mx,dy=p.y-my,d=Math.hypot(dx,dy),push=d<120?(1-d/120)*14:0,x=p.x+(push?dx/d*push:0),y=p.y+(push?dy/d*push:0);
    const tw=.45+.55*Math.abs(Math.sin(s*(.6+p.z)+p.r)),a=(p.o?.7:.9)*tw*(.35+.65*p.z),r=.6+p.z*1.5;
    g.fillStyle=p.o?`rgba(215,127,78,${a})`:`rgba(255,238,218,${a})`;g.beginPath();g.arc(x,y,r,0,6.28);g.fill();
    if(!p.o&&p.z>.88){g.fillStyle=`rgba(255,226,190,${a*.25})`;g.beginPath();g.arc(x,y,r*4,0,6.28);g.fill()}}
  for(let i=T.length-1;i>=0;i--){const q=T[i];q.x+=q.vx;q.y+=q.vy;q.l-=.025;if(q.l<=0){T.splice(i,1);continue}
    g.fillStyle=`rgba(255,${190+q.l*50|0},${130+q.l*90|0},${q.l*.9})`;g.beginPath();g.arc(q.x,q.y,.6+q.l*1.6,0,6.28);g.fill()}
  g.globalCompositeOperation='source-over'}
if(!still)requestAnimationFrame(frame);else frame(0);
// botões: brilho que segue o cursor e faíscas
document.querySelectorAll('.lk').forEach(b=>{let lt=0;const go=e=>{const r=b.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top;
  b.style.setProperty('--mx',x+'px');b.style.setProperty('--my',y+'px');const t=performance.now();if(still||t-lt<40)return;lt=t;
  const k=document.createElement('i'),big=Math.random()<.5;k.className='spk'+(big?'':' dot');
  k.style.cssText=`left:${x}px;top:${y}px;--sz:${big?8+Math.random()*9:3+Math.random()*3}px;--dx:${(Math.random()-.5)*50}px;--dy:${-16-Math.random()*36}px;--t:${.7+Math.random()*.5}s`;
  b.appendChild(k);k.addEventListener('animationend',()=>k.remove())};
  b.addEventListener('pointermove',go);b.addEventListener('pointerdown',go)});
// medição de cliques (GA4 / Meta Pixel, quando configurados em content/links.json)
const toast=t=>{let n=document.querySelector('.toast');if(!n){n=document.createElement('div');n.className='toast';n.setAttribute('role','status');document.body.appendChild(n)}n.textContent=t;n.classList.add('on');clearTimeout(n._t);n._t=setTimeout(()=>n.classList.remove('on'),2600)};
document.addEventListener('click',e=>{const a=e.target.closest('[data-link]');if(!a)return;const id=a.dataset.link;
  if(a.href.startsWith('mailto:')&&/Instagram|FBAN|FBAV/i.test(navigator.userAgent)){const m=decodeURIComponent(a.href.slice(7).split('?')[0]);try{navigator.clipboard.writeText(m).then(()=>toast('E-mail copiado: '+m),()=>toast(m))}catch(_){toast(m)}}
  try{window.gtag&&gtag('event','link_click',{link_id:id,link_url:a.href,transport_type:'beacon'})}catch(_){}
  try{window.fbq&&fbq('trackCustom','LinkClick',{link_id:id});if(window.fbq&&id==='comercial')fbq('track','Contact')}catch(_){}})})();
'''


def render(cfg, *, U, E, base, year, logo, og, noindex, email=''):
    """Monta o HTML da página. U converte caminhos do site; os links internos recebem o UTM da bio."""
    utm = cfg.get('utm', '')
    cfg = json.loads(json.dumps(cfg).replace('{email}', email))  # {email} vem do e-mail cadastrado em site.json

    def href(url):
        if url.startswith('/'):
            path, _, frag = url.partition('#')
            full = U(path)
            if utm:
                full += ('&' if '?' in full else '?') + utm
            return full + ('#' + frag if frag else '')
        return url

    def ext(url):
        # tudo abre em nova guia para a pessoa não sair do hub (e-mail abre o app de e-mail)
        return '' if url.startswith('mailto:') else ' target="_blank" rel="noopener"'

    items = [l for l in cfg['links'] if l.get('ativo', True) and (not l.get('ate') or date.fromisoformat(l['ate']) >= date.today())]
    btns = ''
    for i, l in enumerate(items):
        hot = l.get('destaque')
        btns += (f'<li><a class="lk{" hot" if hot else ""}" style="--i:{i}" href="{E(href(l["url"]))}"{ext(l["url"])} data-link="{E(l["id"])}">'
                 f'{"<span class=shine></span><span class=ping></span>" if hot else ""}'
                 f'<span class="ico">{ICONS.get(l.get("icone"), ICONS["estrela"])}</span>'
                 f'<span><b>{E(l["texto"])}</b>{"<small>" + E(l["sub"]) + "</small>" if l.get("sub") else ""}</span>'
                 f'<span class="go">{ARROW}</span></a></li>')
    social = ''.join(f'<a href="{E(s["url"])}" target="_blank" rel="noopener noreferrer" aria-label="{E(s["nome"])}" data-link="{E(s["id"])}">{SOCIAL.get(s["id"], ICONS["site"])}</a>'
                     for s in cfg.get('redes', []))
    track = ''
    import re
    if cfg.get('ga4'):
        if not re.fullmatch(r'G-[A-Z0-9]+', cfg['ga4']):
            raise ValueError('links.json: ga4 deve ser no formato G-XXXXXXX')
        g = cfg['ga4']
        track += (f'<script async src="https://www.googletagmanager.com/gtag/js?id={g}"></script>'
                  f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{g}');</script>")
    if cfg.get('meta_pixel'):
        if not re.fullmatch(r'\d+', cfg['meta_pixel']):
            raise ValueError('links.json: meta_pixel deve ter só números')
        px = cfg['meta_pixel']
        track += ("<script>!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};"
                  "if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];"
                  f"s.parentNode.insertBefore(t,s)}}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');fbq('init','{px}');fbq('track','PageView');</script>")
    canon = base + '/contatos/'
    title, desc = E(cfg['titulo']), E(cfg['descricao'])
    motto = E(cfg['frase']).replace('magia', '<em>magia</em>')
    return f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title><meta name="description" content="{desc}"><link rel="canonical" href="{canon}">{'<meta name="robots" content="noindex">' if noindex else ''}
<meta name="theme-color" content="#341131"><meta property="og:type" content="website"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="{og}"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{U('/favicon.ico')}" sizes="48x48"><link rel="icon" type="image/png" sizes="512x512" href="{U('/favicon.png')}"><link rel="apple-touch-icon" href="{U('/apple-touch-icon.png')}">
<link rel="preload" href="{U('/assets/fonts/grift-800.woff2')}?v=2" as="font" type="font/woff2" crossorigin>
<style>{CSS.replace('url(/assets/', 'url(' + U('/assets/'))}</style>{track}</head>
<body><canvas id="sky" aria-hidden="true"></canvas>
<main class="wrap">
  <a class="crest" href="{E(href('/'))}" target="_blank" rel="noopener" aria-label="Brandaz, ir para o site" data-link="logo"><span class="orbit" aria-hidden="true"><i></i><i></i><i></i></span><img src="{logo}" alt="Brandaz Agência" width="600" height="300"></a>
  <p class="kicker">{E(cfg['chamada'])}</p>
  <h1 class="motto">{motto}</h1>
  <ul class="links">{btns}</ul>
  <nav class="social" aria-label="Redes sociais">{social}</nav>
  <p class="copy">© {year} BRANDAZ. Todos os direitos reservados.</p>
</main>
<script>{JS}</script>
</body></html>
'''


def load(root):
    import os
    with open(os.path.join(root, 'content', 'links.json'), encoding='utf-8') as f:
        return json.load(f)
