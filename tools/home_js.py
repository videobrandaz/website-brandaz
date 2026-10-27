# Scripts exclusivos da home: capas A/B, trajeto das especialidades, filmes em loop e partículas.
# Ficam embutidos na própria página (rodam depois de /assets/js/site.js, que expõe window.BZ).

HOME = r'''
(()=>{const {$,$$}=BZ;
// especialidades: o ponto de magia percorre o trajeto ao lado da lista
const wrap=$('.spec-wrap'),road=$('#road'),ahead=$('#ahead'),trail=$('#trail'),mpath=$('#mpath'),orb=$('#orb'),specs=$$('#specs li');
const pin=$('.spec-pin'),stick=$('.spec-stick'),scta=$('.spec-cta'),pinned=()=>getComputedStyle(stick).position==='sticky';
let table=[],total=0,L0=0,L1=0;BZ.orbXY=[-999,-999];BZ.orbK=0;
function buildRoad(){const W=64,H=wrap.offsetHeight,top=wrap.getBoundingClientRect().top;road.setAttribute('width',W);road.setAttribute('height',H);road.setAttribute('viewBox',`0 0 ${W} ${H}`);
  const pts=[[32,-30]];specs.forEach((li,i)=>{const r=li.getBoundingClientRect();const x=i%2?14:46;pts.push([x,r.top-top+r.height/2]);li.querySelector('.node').style.left=(x-64-6)+'px'});pts.push([32,H+30]);
  let d=`M${pts[0][0]},${pts[0][1]}`;for(let i=0;i<pts.length-1;i++){const p0=pts[i-1]||pts[i],p1=pts[i],p2=pts[i+1],p3=pts[i+2]||p2;
    d+=` C${p1[0]+(p2[0]-p0[0])/6},${p1[1]+(p2[1]-p0[1])/6} ${p2[0]-(p3[0]-p1[0])/6},${p2[1]-(p3[1]-p1[1])/6} ${p2[0]},${p2[1]}`}
  [ahead,trail,mpath].forEach(p=>p.setAttribute('d',d));total=ahead.getTotalLength();mpath.style.strokeDasharray=total;
  table=[];for(let l=0;l<=total;l+=3){const q=ahead.getPointAtLength(l);table.push([l,q.x,q.y])}BZ.roadTable=table;
  const at=y=>{let b=table[0];table.forEach(t=>{if(Math.abs(t[2]-y)<Math.abs(b[2]-y))b=t});return b[0]};L0=at(pts[1][1]);L1=at(pts[pts.length-2][1])}
function moveOrb(){if(!table.length)return;const r=wrap.getBoundingClientRect();let k=0;
  if(pinned()){const pr=pin.getBoundingClientRect(),p=Math.max(0,Math.min(1,-pr.top/(pr.height-innerHeight))),L=L0+(L1-L0)*p;while(k+1<table.length&&table[k+1][0]<=L)k++;scta.classList.toggle('done',p>.97)}
  else{const target=innerHeight*.55-r.top;while(k+1<table.length&&table[k+1][2]<=target)k++;scta.classList.add('done')}
  const [len,x,y]=table[k];orb.style.transform=`translate(${x}px,${y}px)`;mpath.style.strokeDashoffset=total-len;BZ.orbXY=[r.left+x,r.top+y];BZ.orbK=k;
  specs.forEach(li=>{const b=li.getBoundingClientRect(),c=b.top+b.height/2-r.top;li.classList.toggle('past',c<y-4);li.classList.toggle('lit',Math.abs(c-y)<b.height*.6)})}
BZ.onScroll.push(moveOrb);
const re=()=>{buildRoad();moveOrb()};addEventListener('resize',()=>{clearTimeout(window._hr);window._hr=setTimeout(re,160)});addEventListener('load',re);document.fonts&&document.fonts.ready.then(re);re();
// cada filme roda em loop no próprio box enquanto está na tela
const reelIO=new IntersectionObserver(es=>es.forEach(e=>{const v=e.target.querySelector('video');e.isIntersecting&&!BZ.still?v.play().catch(()=>{}):v.pause()}),{threshold:.15});
$$('.cinema-reel').forEach(b=>reelIO.observe(b));
const inView=x=>{const r=x.getBoundingClientRect();return r.bottom>0&&r.top<innerHeight&&r.right>0&&r.left<innerWidth};
BZ.onStill.push(v=>$$('.cinema-reel video,.wf video').forEach(x=>v||!inView(x)?x.pause():x.play().catch(()=>{})));
// clientes embaralhados a cada visita
$$('[data-shuffle]').forEach(t=>{const items=[...t.children].slice(0,t.children.length/2);for(let i=items.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[items[i],items[j]]=[items[j],items[i]]}
  t.innerHTML='';[...items,...items.map(n=>n.cloneNode(true))].forEach((n,i)=>{if(i>=items.length){n.setAttribute('aria-hidden','true');n.tabIndex=-1;n.querySelector('img').alt=''}t.appendChild(n)})});

// ---- partículas: começam no +20, deslizam (sem elástico) e trocam de forma conforme o assunto do capítulo
const cv=$('#dust'),ctx=cv.getContext('2d'),DPR=Math.min(2,devicePixelRatio||1),MOB=()=>innerWidth<768,N=innerWidth<768?1100:2400;
function resize(){cv.width=innerWidth*DPR;cv.height=innerHeight*DPR}addEventListener('resize',resize);resize();
function sample(draw){const S=420,c=document.createElement('canvas');c.width=c.height=S;const g=c.getContext('2d');g.fillStyle='#fff';g.strokeStyle='#fff';g.lineCap='round';g.lineJoin='round';draw(g,S);
  const d=g.getImageData(0,0,S,S).data,pts=[];for(let y=0;y<S;y+=2)for(let x=0;x<S;x+=2)if(d[(y*S+x)*4+3]>120)pts.push([x/S-.5,y/S-.5]);
  return Array.from({length:N},()=>{const p=pts[(Math.random()*pts.length)|0]||[0,0];return[p[0]+(Math.random()-.5)*.003,p[1]+(Math.random()-.5)*.003]})}
const SH={};let P=[],ready=false;
const rr=(g,x,y,w,h,r)=>{g.beginPath();g.moveTo(x+r,y);g.arcTo(x+w,y,x+w,y+h,r);g.arcTo(x+w,y+h,x,y+h,r);g.arcTo(x,y+h,x,y,r);g.arcTo(x,y,x+w,y,r);g.closePath();g.fill()};
async function init(){try{await document.fonts.load('800 200px Karibu')}catch(e){}
  const img=new Image();img.src=cv.dataset.mark;await img.decode().catch(()=>{});
  SH.mark=sample((g,S)=>{const h=S*.96,w=h*img.naturalWidth/img.naturalHeight;g.drawImage(img,(S-w)/2,(S-h)/2,w,h)});
  // número compacto: "+" encostado nos dígitos, centrado no box
  const num=t=>(g,S)=>{let f=200;g.textBaseline='alphabetic';g.textAlign='left';g.font=`800 ${f}px Karibu`;
    const pw=g.measureText('+').width,gap=-f*.07,dw=g.measureText(t).width,sc=S*.8/(pw+gap+dw);f*=sc;g.font=`800 ${f}px Karibu`;
    const m=g.measureText(t),base=S/2+(m.actualBoundingBoxAscent-m.actualBoundingBoxDescent)/2,x0=(S-(pw+gap+dw)*sc)/2;g.fillText('+',x0,base);g.fillText(t,x0+(pw+gap)*sc,base)};
  SH['20']=sample(num('20'));SH['21']=sample(num('21'));
  // resultados: barras que crescem + seta de tendência
  SH.growth=sample((g,S)=>{const b=S*.13,gap=S*.07,base=S*.9,hs=[.16,.27,.38,.49];hs.forEach((h,i)=>rr(g,S*.12+i*(b+gap),base-S*h,b,S*h,S*.02));
    g.lineWidth=S*.032;g.beginPath();g.moveTo(S*.1,S*.34);g.lineTo(S*.34,S*.22);g.lineTo(S*.5,S*.27);g.lineTo(S*.86,S*.06);g.stroke();
    g.beginPath();g.moveTo(S*.86,S*.06);g.lineTo(S*.74,S*.06);g.moveTo(S*.86,S*.06);g.lineTo(S*.84,S*.18);g.stroke()});
  // formas desenhadas ponto a ponto (coordenadas 0–1): aglomerados brilhantes, linhas finas e poeira
  const G=()=>(Math.random()+Math.random()+Math.random()-1.5)/1.5,pick=a=>a[(Math.random()*a.length)|0];
  const bez=(c,t)=>{const u=1-t;return[u*u*u*c[0]+3*u*u*t*c[2]+3*u*t*t*c[4]+t*t*t*c[6],u*u*u*c[1]+3*u*u*t*c[3]+3*u*t*t*c[5]+t*t*t*c[7]]};
  const gen=f=>Array.from({length:N},()=>{const p=f();return[p[0]-.5,p[1]-.5]});
  // constelação: estrelas ligadas por linhas finas + poeira em volta
  const ST=[[.08,.58],[.28,.44],[.46,.12],[.64,.44],[.56,.78],[.36,.7],[.9,.3],[.82,.72]],ED=[[0,1],[1,2],[2,3],[3,4],[4,5],[5,1],[3,6],[4,7]],BIG=[1,2,3,6];
  SH.stars=gen(()=>{const r=Math.random();
    if(r<.5){const i=(Math.random()*ST.length)|0,s=BIG.includes(i)?.022:.014;return[ST[i][0]+G()*s,ST[i][1]+G()*s]}
    if(r<.84){const e=pick(ED),t=Math.random(),a=ST[e[0]],b=ST[e[1]];return[a[0]+(b[0]-a[0])*t+G()*.003,a[1]+(b[1]-a[1])*t+G()*.003]}
    return[Math.random(),.02+Math.random()*.96]});
  // livro de magia aberto, com faíscas subindo das páginas
  const BK=[],TOP=[.5,.64,.38,.47,.2,.45,.03,.5];[1,-1].forEach(d=>{const X=x=>.5+d*(x-.5),c=a=>a.map((v,i)=>i%2?v:X(v));
    BK.push(c(TOP),c([.03,.5,.03,.62,.03,.74,.03,.86]),c([.03,.86,.2,.81,.38,.83,.5,.95]),c([.5,.99,.36,.9,.18,.89,0,.92]));
    [.1,.18,.26].forEach(o=>BK.push(c([.45,.66+o,.36,.5+o,.22,.48+o,.1,.52+o])))});
  BK.push([.5,.64,.5,.74,.5,.84,.5,.95]);
  const SP=[[.5,.22,.028],[.34,.12,.018],[.68,.1,.02],[.62,.36,.014],[.37,.34,.013]];
  SH.book=gen(()=>{const r=Math.random();
    if(r<.64){const c=pick(BK),p=bez(c,Math.random());return[p[0]+G()*.0025,p[1]+G()*.0025]}
    if(r<.78){const s=pick(SP);return[s[0]+G()*s[2],s[1]+G()*s[2]]}
    const t=Math.pow(Math.random(),.7),w=.03+t*.26;return[.5+G()*w,.62-t*.58]});
  SH.play=sample((g,S)=>{g.beginPath();g.moveTo(S*.28,S*.16);g.lineTo(S*.84,S*.5);g.lineTo(S*.28,S*.84);g.closePath();g.fill()});
  SH.none=Array.from({length:N},()=>[(Math.random()-.5)*2.4,.8+Math.random()*1.2]);
  SH.flow=Array.from({length:N},()=>[Math.random(),(Math.random()-.5)]);
  P=SH.none.map(()=>({x:-99,y:-99,ox:0,oy:0,s:Math.random()<.15?2.1:1.4,c:Math.random()<.7?0:1,ph:Math.random()*6.28,init:false}));ready=true}
const secs=$$('[data-shape]'),ease=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
function state(){let idx=0,k=1;secs.forEach((s,i)=>{const t=s.getBoundingClientRect().top;const kk=Math.max(0,Math.min(1,(innerHeight*.55-t)/(innerHeight*.35)));if(kk>0){idx=i;k=kk}});return[secs[Math.max(0,idx-1)],secs[idx],idx===0?1:ease(k)]}
const ALPHA={'20':.95,growth:.8,play:.8,stars:.95,book:.95,mark:.9,flow:1};
function place(sec){const n=sec.dataset.shape;
  if(n==='none'){const b=secs[1].querySelector('.dust-anchor').getBoundingClientRect();return[b.left+b.width/2,b.top+b.height*2,260,0]}
  if(n==='flow')return[0,0,1,1];
  if(MOB()){const r=sec.getBoundingClientRect();return[innerWidth*.72,Math.max(120,Math.min(innerHeight-120,r.top+140)),innerWidth*.48,.3]}
  const a=sec.querySelector('.dust-anchor');if(!a)return[innerWidth*.8,innerHeight*.5,220,.6];const b=a.getBoundingClientRect();return[b.left+b.width/2,b.top+b.height/2,Math.max(b.width,b.height),ALPHA[n]??.8]}
// pó que flui pelo caminho já percorrido até o ponto de magia
function flowPos(i,time){const f=SH.flow[i];if(!table.length)return[BZ.orbXY[0],BZ.orbXY[1]];const r=wrap.getBoundingClientRect();
  const u=(f[0]+time*.06)%1,end=table[BZ.orbK][0],back=Math.min(end,260);const L=end-back*(1-u*u);
  let lo=0,hi=table.length-1;while(lo<hi){const m=(lo+hi)>>1;if(table[m][0]<L)lo=m+1;else hi=m}const q=table[lo];
  const spread=f[1]*(6+18*(1-u));return[r.left+q[1]+spread,r.top+q[2]+f[1]*4]}
function pos(sec,pl,arr,i,time){if(sec.dataset.shape==='flow')return flowPos(i,time);return[pl[0]+arr[i][0]*pl[2],pl[1]+arr[i][1]*pl[2]]}
let mx=-999,my=-999;addEventListener('pointermove',e=>{mx=e.clientX;my=e.clientY},{passive:true});addEventListener('pointerleave',()=>{mx=my=-999});
const caps=$$('.dust-cap');
function frame(t){requestAnimationFrame(frame);if(!ready)return;const [sa,sb,k]=state();caps.forEach(c=>c.classList.toggle('on',!MOB()&&k>.85&&sb.contains(c)));const A=SH[sa.dataset.shape],B=SH[sb.dataset.shape],pa=place(sa),pb=place(sb);
  const al=pa[3]+(pb[3]-pa[3])*k;ctx.setTransform(DPR,0,0,DPR,0,0);ctx.clearRect(0,0,innerWidth,innerHeight);if(al<.01){P.forEach(p=>p.init=false);return}
  ctx.globalCompositeOperation='lighter';const time=t/1000;
  for(let i=0;i<P.length;i++){const p=P[i];const lag=Math.max(0,Math.min(1,k*1.3-(i/P.length)*.3));
    const a=pos(sa,pa,A,i,time),b=pos(sb,pb,B,i,time);let tx=a[0]+(b[0]-a[0])*lag,ty=a[1]+(b[1]-a[1])*lag;
    if(!BZ.still&&sb.dataset.shape!=='flow'){tx+=Math.sin(time*.9+p.ph)*1.2;ty+=Math.cos(time*.8+p.ph)*1.2}
    if(!p.init){p.x=tx;p.y=ty+40;p.init=true}
    p.x+=(tx-p.x)*.12;p.y+=(ty-p.y)*.12; // desliza até o alvo, sem passar do ponto
    const dx=p.x+p.ox-mx,dy=p.y+p.oy-my,d2=dx*dx+dy*dy;let px=0,py=0;if(d2<9000){const d=Math.sqrt(d2)||1,f=(1-d2/9000)*22;px=dx/d*f;py=dy/d*f}
    p.ox+=(px-p.ox)*.1;p.oy+=(py-p.oy)*.1;
    ctx.fillStyle=p.c?`rgba(234,232,238,${.7*al})`:`rgba(215,127,78,${.9*al})`;ctx.fillRect(p.x+p.ox,p.y+p.oy,p.s,p.s)}
  ctx.globalCompositeOperation='source-over'}
init();requestAnimationFrame(frame);
})();
'''

COVER_A = r'''
// capa A: o filme e os cases se alternam; cada trecho tem sua legenda
(()=>{const {$}=BZ,S=__SLIDES__;const show=$('#show'),V={filmA:$('#filmA'),filmB:$('#filmB'),filmC:$('#filmC')},imgs=[...show.querySelectorAll('img')],ticks=[...document.querySelectorAll('#ticks b')],cr=$('#credit');
  let i=0,t0=performance.now(),dur=0;
  function go(k){i=k%S.length;const s=S[i];show.querySelectorAll('.on').forEach(e=>e.classList.remove('on'));
    if(s[0].startsWith('film')){const v=V[s[0]];Object.values(V).forEach(x=>{if(x!==v)x.pause()});v.currentTime=s[1];if(!BZ.still)v.play().catch(()=>{});v.classList.add('on');dur=(s[2]-s[1])*1000}
    else{const im=imgs[S.slice(0,i).filter(x=>!x[0].startsWith('film')).length];im.classList.remove('on');void im.offsetWidth;im.classList.add('on');dur=3800}
    cr.textContent=s[3];ticks.forEach((b,j)=>b.style.width=j<i?'100%':'0');t0=performance.now()}
  (function f(t){if(!BZ.still){const k=Math.min(1,(t-t0)/dur);ticks[i].style.width=(k*100)+'%';if(k>=1)go(i+1)}else t0=t-(parseFloat(ticks[i].style.width||0)/100)*dur;requestAnimationFrame(f)})(t0);
  BZ.onStill.push(v=>{const on=show.querySelector('video.on');if(on)v?on.pause():on.play().catch(()=>{})});
  go(0)})();
'''

COVER_B = r'''
// capa B: só tocam os filmes visíveis da parede
(()=>{const io=new IntersectionObserver(es=>es.forEach(e=>{e.isIntersecting&&!BZ.still?e.target.play().catch(()=>{}):e.target.pause()}),{threshold:.05});document.querySelectorAll('.wf video').forEach(x=>io.observe(x))})();
'''
