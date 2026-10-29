# Scripts exclusivos da home: capas A/B, trajeto das especialidades, filmes em loop e partículas.
# Ficam embutidos na própria página (rodam depois de /assets/js/site.js, que expõe window.BZ).

HOME = r'''
(()=>{const {$,$$}=BZ;
// especialidades: o ponto de magia percorre o trajeto ao lado da lista
const wrap=$('.spec-wrap'),road=$('#road'),ahead=$('#ahead'),trail=$('#trail'),mpath=$('#mpath'),orb=$('#orb'),specs=$$('#specs li');
const pin=$('.spec-pin'),stick=$('.spec-stick'),scta=$('.spec-cta'),pinned=()=>getComputedStyle(stick).position==='sticky';
let table=[],total=0,L0=0,L1=0;BZ.orbXY=[-999,-999];BZ.orbK=0;
function buildRoad(){const W=64,H=wrap.offsetHeight,top=wrap.getBoundingClientRect().top;road.setAttribute('width',W);road.setAttribute('height',H);road.setAttribute('viewBox',`0 0 ${W} ${H}`);
  const pts=[[32,-30]];specs.forEach((li,i)=>{const r=li.getBoundingClientRect();const x=i%2?14:46;pts.push([x,r.top-top+r.height/2]);li.querySelector('.node').style.left=(x-64-6)+'px'}); // o caminho termina no 07
  let d=`M${pts[0][0]},${pts[0][1]}`;for(let i=0;i<pts.length-1;i++){const p0=pts[i-1]||pts[i],p1=pts[i],p2=pts[i+1],p3=pts[i+2]||p2;
    d+=` C${p1[0]+(p2[0]-p0[0])/6},${p1[1]+(p2[1]-p0[1])/6} ${p2[0]-(p3[0]-p1[0])/6},${p2[1]-(p3[1]-p1[1])/6} ${p2[0]},${p2[1]}`}
  [ahead,trail,mpath].forEach(p=>p.setAttribute('d',d));total=ahead.getTotalLength();mpath.style.strokeDasharray=total;
  table=[];for(let l=0;l<=total;l+=3){const q=ahead.getPointAtLength(l);table.push([l,q.x,q.y])}BZ.roadTable=table;
  const at=y=>{let b=table[0];table.forEach(t=>{if(Math.abs(t[2]-y)<Math.abs(b[2]-y))b=t});return b[0]};L0=at(pts[1][1]);L1=total}
// a rolagem define o alvo; a bolinha desliza até ele a cada quadro e a magia segue a posição dela
let orbT=0,orbL=-1;
function moveOrb(){if(!table.length)return;const r=wrap.getBoundingClientRect();
  if(pinned()){const pr=pin.getBoundingClientRect(),p=Math.max(0,Math.min(1,-pr.top/(pr.height-innerHeight)));orbT=L0+(L1-L0)*p;scta.classList.toggle('done',p>.97)}
  else{const target=innerHeight*.55-r.top;let k=0;while(k+1<table.length&&table[k+1][2]<=target)k++;orbT=Math.max(L0,Math.min(L1,table[k][0]));scta.classList.add('done')}}
(function orbLoop(){requestAnimationFrame(orbLoop);if(!table.length)return;orbL=orbL<0?orbT:orbL+(orbT-orbL)*.16;
  const r=wrap.getBoundingClientRect();let k=Math.min(table.length-1,Math.max(0,Math.round(orbL/3)));
  const [len,x,y]=table[k];orb.style.transform=`translate(${x}px,${y}px)`;mpath.style.strokeDashoffset=total-len;BZ.orbXY=[r.left+x,r.top+y];BZ.orbK=k;
  specs.forEach(li=>{const b=li.getBoundingClientRect(),c=b.top+b.height/2-r.top;li.classList.toggle('past',c<y-4);li.classList.toggle('lit',Math.abs(c-y)<b.height*.6)})})();
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
const cv=$('#dust'),ctx=cv.getContext('2d'),DPR=Math.min(2,devicePixelRatio||1),MOB=()=>innerWidth<768,N=innerWidth<768?2000:3400;
function resize(){cv.width=innerWidth*DPR;cv.height=innerHeight*DPR}addEventListener('resize',resize);resize();
function sample(draw){const S=420,c=document.createElement('canvas');c.width=c.height=S;const g=c.getContext('2d');g.fillStyle='#fff';g.strokeStyle='#fff';g.lineCap='round';g.lineJoin='round';draw(g,S);
  const d=g.getImageData(0,0,S,S).data,pts=[];for(let y=0;y<S;y+=2)for(let x=0;x<S;x+=2)if(d[(y*S+x)*4+3]>120)pts.push([x/S-.5,y/S-.5]);
  return Array.from({length:N},()=>{const p=pts[(Math.random()*pts.length)|0]||[0,0];return[p[0]+(Math.random()-.5)*.003,p[1]+(Math.random()-.5)*.003]})}
const SH={};let P=[],ready=false;
const rr=(g,x,y,w,h,r)=>{g.beginPath();g.moveTo(x+r,y);g.arcTo(x+w,y,x+w,y+h,r);g.arcTo(x+w,y+h,x,y+h,r);g.arcTo(x,y+h,x,y,r);g.arcTo(x,y,x+w,y,r);g.closePath();g.fill()};
async function init(){try{await document.fonts.load('800 200px Grift')}catch(e){}
  const img=new Image();img.src=cv.dataset.mark;await img.decode().catch(()=>{});
  SH.mark=sample((g,S)=>{const h=S*.96,w=h*img.naturalWidth/img.naturalHeight;g.drawImage(img,(S-w)/2,(S-h)/2,w,h)});
  // número compacto: "+" encostado nos dígitos, centrado no box
  const num=t=>(g,S)=>{let f=200;g.textBaseline='alphabetic';g.textAlign='left';g.font=`800 ${f}px Grift`;
    const pw=g.measureText('+').width,gap=-f*.07,dw=g.measureText(t).width,sc=S*.8/(pw+gap+dw);f*=sc;g.font=`800 ${f}px Grift`;
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
  // as formas abaixo guardam [x, y, tipo, fase, opacidade, profundidade]; o tipo define tamanho, brilho e animação
  // de cada partícula (ver sty) e a profundidade faz a forma girar em 3D (ver pos)
  // constelação: núcleos com brilho e cruz de luz em profundidades diferentes, linhas com um pulso de energia e poeira estelar
  const ST=[[.08,.58],[.28,.44],[.46,.12],[.64,.44],[.56,.78],[.36,.7],[.9,.3],[.82,.72]],ED=[[0,1],[1,2],[2,3],[3,4],[4,5],[5,1],[3,6],[4,7]],BIG=[1,2,3,6];
  const ZS=[-.06,-.1,.18,-.14,.06,-.18,.22,-.04],seg=(a,b,t)=>[a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t];
  SH.stars=Array.from({length:N},(_,i)=>{let p;
    if(i<ST.length)p=[ST[i][0],ST[i][1],2,BIG.includes(i)?1:.62,1,ZS[i]];
    else{const r=Math.random();
      if(r<.12){const j=(Math.random()*ST.length)|0,s=ST[j],d=Math.pow(Math.random(),2.2)*.07,a=Math.random()*6.28;p=[s[0]+Math.cos(a)*d,s[1]+Math.sin(a)*d,8,0,1,ZS[j]+G()*.03]}
      else if(r<.48){const j=(Math.random()*ED.length)|0,e=ED[j],t=Math.random(),A=ST[e[0]],B=ST[e[1]],q=seg(A,B,t);
        p=[q[0]+G()*.0016,q[1]+G()*.0016,1,t*Math.hypot(B[0]-A[0],B[1]-A[1])*14+j*1.9,.85,ZS[e[0]]+(ZS[e[1]]-ZS[e[0]])*t]}
      else if(r<.5)p=[.04+Math.random()*.92,.04+Math.random()*.92,3,Math.random()*6.28,1,G()*.5];
      else if(r<.8){const e=pick(ED),t=Math.random(),q=seg(ST[e[0]],ST[e[1]],t);p=[q[0]+G()*.1,q[1]+G()*.1,9,0,1,ZS[e[0]]+(ZS[e[1]]-ZS[e[0]])*t+G()*.25]}
      else p=[Math.random()*1.2-.1,Math.random()*1.2-.1,9,0,1,G()*.7]}
    return[p[0]-.5,p[1]-.5,p[2],p[3],p[4],p[5]]});
  // livro de magia: contorno, bloco de páginas e linhas de texto em partículas, papel iluminado a partir da lombada,
  // um redemoinho de luz que sobe em espiral, um anel de poeira orbitando e páginas soltas flutuando
  const TOP=[.5,.7,.42,.6,.24,.57,.05,.63],EDG=[.05,.63,.045,.69,.045,.75,.05,.8],BOT=[.05,.8,.22,.77,.4,.79,.5,.87],COV=[-.01,.85,.2,.84,.38,.88,.5,.935];
  const mir=(c,d)=>d>0?c:c.map((v,i)=>i%2?v:1-v),dn=(c,o)=>c.map((v,i)=>i%2?v+o:v),side=(c,o)=>c.map((v,i)=>i%2?v:v-o);
  const PG=[1,-1].map(d=>{const pl=[];[TOP,EDG,BOT].forEach(c=>{for(let k=0;k<=24;k++)pl.push(bez(mir(c,d),k/24))});return pl});
  const inPoly=(x,y,pl)=>{let o=false;for(let a=0,b=pl.length-1;a<pl.length;b=a++){const A=pl[a],B=pl[b];if((A[1]>y)!==(B[1]>y)&&x<(B[0]-A[0])*(y-A[1])/(B[1]-A[1])+A[0])o=!o}return o};
  const OUT=[],TXT=[];[1,-1].forEach(d=>{OUT.push([mir(TOP,d),1,3],[mir(EDG,d),.85,1],[mir(BOT,d),.95,2],[mir(COV,d),.8,2]);
    [.008,.015,.022,.029,.036].forEach((o,j)=>OUT.push([mir(dn(BOT,o),d),.7-j*.1,1]));[.006,.012].forEach(o=>OUT.push([mir(side(dn(EDG,o*.6),o),d),.5,.5]));
    for(let o=.035;o<.15;o+=.022)TXT.push(mir([.45,.71+o,.38,.62+o,.24,.6+o,.1,.65+o],d))});
  OUT.push([[.5,.7,.5,.76,.5,.82,.5,.87],.9,1]);const OW=OUT.reduce((a,o)=>a+o[2],0),pickO=()=>{let r=Math.random()*OW;for(const o of OUT)if((r-=o[2])<=0)return o;return OUT[0]};
  const FP=[[.3,.24,-25,.06],[.72,.2,22,.055],[.78,.44,35,.042],[.2,.42,-40,.038],[.6,.1,10,.032]].map(([cx,cy,a,sz])=>{const r=a*Math.PI/180,w=sz*1.35,h=sz*1.35*.75;
    return[[-w/2,-h/2],[w/2,-h/2+h*.15],[w/2,h/2],[-w/2,h/2-h*.1]].map(([x,y])=>[cx+x*Math.cos(r)-y*Math.sin(r),cy+x*Math.sin(r)+y*Math.cos(r)])});
  const SPK=[[.5,.26,.8],[.35,.14,.55],[.66,.1,.62],[.62,.38,.45],[.37,.36,.42],[.86,.3,.5],[.13,.26,.45]],LIT=[[.5,.665,5,95],[.5,.655,5,46],[.5,.66,5,17]];
  const bz=y=>-(y-.7)*.7; // a frente do livro (embaixo) fica mais perto
  SH.book=Array.from({length:N},(_,i)=>{let p;
    if(i<SPK.length)p=[SPK[i][0],SPK[i][1],2,SPK[i][2],1,G()*.3];
    else if(i<SPK.length+LIT.length)p=[...LIT[i-SPK.length],1,0];
    else{const r=Math.random();
      if(r<.27){const o=pickO(),t=Math.random(),q=bez(o[0],t);p=[q[0]+G()*.0016,q[1]+G()*.0016,1,t*7,o[1],bz(q[1])]}
      else if(r<.38){const c=pick(TXT),t=.1+Math.random()*.8,q=bez(c,t);p=[q[0]+G()*.0011,q[1]+G()*.0011,11,t*6+q[1]*30,.8,bz(q[1])]}
      else if(r<.63){let x,y,k=0,ok=false;do{x=.05+Math.random()*.9;y=.56+Math.random()*.32;k++;
          ok=(inPoly(x,y,PG[0])||inPoly(x,y,PG[1]))&&!(Math.abs(x-.5)<.012&&Math.random()<.7)&&Math.random()<.3+.7*(1-Math.abs(x-.5)/.45)}while(k<80&&!ok);
        const lt=Math.max(0,1-Math.hypot(x-.5,(y-.66)*1.6)/.36);p=[x,y,4,Math.min(1,(1-Math.abs(x-.5)/.45)*.55+lt*.6),1,bz(y)]}
      else if(r<.665){const j=(Math.random()*FP.length)|0,f=FP[j],e=(Math.random()*4)|0,q=seg(f[e],f[(e+1)%4],Math.random());p=[q[0],q[1],7,j*1.7,1,(j-2)*.12]}
      else if(r<.88)return[Math.pow(Math.random(),.65),0,6,Math.random(),1,0];
      else if(r<.94)return[.3+G()*.05,.08+G()*.03,10,Math.random()*6.28,1,0];
      else p=[.04+Math.random()*.92,.0+Math.random()*.62,9,0,1,G()*.6]}
    return[p[0]-.5,p[1]-.5,p[2],p[3],p[4],p[5]]});
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
  const an=sec.querySelector('.dust-anchor');if(MOB()&&!(an&&an.offsetWidth)){const r=sec.getBoundingClientRect();return[innerWidth*.72,Math.max(120,Math.min(innerHeight-120,r.top+140)),innerWidth*.48,.3]}
  const a=sec.querySelector('.dust-anchor');if(!a)return[innerWidth*.8,innerHeight*.5,220,.6];const b=a.getBoundingClientRect();return[b.left+b.width/2,b.top+b.height/2,Math.max(b.width,b.height),ALPHA[n]??.8]}
// pó que flui por todo o caminho já percorrido, do primeiro item até o ponto de magia
function flowPos(i,time){const f=SH.flow[i];if(!table.length)return[BZ.orbXY[0],BZ.orbXY[1]];const r=wrap.getBoundingClientRect();
  const u=(f[0]+time*.05)%1,end=table[BZ.orbK][0],back=Math.max(0,end-Math.max(0,L0-24));const L=end-back*(1-Math.pow(u,.8));
  let lo=0,hi=table.length-1;while(lo<hi){const m=(lo+hi)>>1;if(table[m][0]<L)lo=m+1;else hi=m}const q=table[lo];
  const spread=f[1]*(5+11*(1-u));return[r.left+q[1]+spread,r.top+q[2]+f[1]*4]}
// posição na tela; formas com profundidade giram em 3D (R = [giro, inclinação]) e devolvem a escala da perspectiva
function pos(sec,pl,arr,i,tt,R){if(sec.dataset.shape==='flow')return[...flowPos(i,tt),1];const q=arr[i];let x=q[0],y=q[1],z=q[5]||0,f=1;
  if(q[2]===6){const u=(q[3]+tt*.05)%1,an=(q[3]*9301%1)*6.28+u*2.6+tt*.35,r=(.03+u*.36)*q[0];y=.16-u*.64;x=Math.cos(an)*r;z=Math.sin(an)*r*.8}
  else if(q[2]===7){y+=Math.sin(tt*.8+q[3])*.014;x+=Math.cos(tt*.6+q[3])*.008}
  else if(q[2]===10){const an=q[3]+tt*.32;x=Math.cos(an)*q[0];z=Math.sin(an)*q[0]*.75;y=q[1]+Math.sin(an)*q[0]*.1}
  if(q.length>5){const c=Math.cos(R[0]),s=Math.sin(R[0]),x1=x*c+z*s,z1=z*c-x*s,c2=Math.cos(R[1]),s2=Math.sin(R[1]),y1=y*c2-z1*s2,z2=z1*c2+y*s2;f=1/(1+z2*.6);x=x1*f;y=y1*f}
  return[pl[0]+x*pl[2],pl[1]+y*pl[2],f]}
let pmx=0,pmy=0;const rot=(n,tt)=>n==='stars'?[Math.sin(tt*.17)*.22+pmx*.24,Math.sin(tt*.11)*.08+pmy*.14]:n==='book'?[Math.sin(tt*.21)*.12+pmx*.2,-.03+pmy*.1]:[0,0];
// estilo de cada tipo: [tamanho, raio do brilho, cruz de luz, opacidade, cor]
const CW='255,238,218',CG='255,198,140',CO='215,127,78',CL='234,232,238';
function sty(q,p,tt,i){const k=q.length>2?q[2]:0,ph=q[3],a=q[4]??1;
  switch(k){
    case 1:return[1.25,0,0,a*(.45+.55*Math.pow(.5+.5*Math.sin(ph-tt*2.4),6)),CG];
    case 2:return[2.4*ph,30*ph,ph,.82+.18*Math.sin(tt*1.7+i*2.3),CW];
    case 3:return[1.5,8,.45,.15+.85*Math.pow(Math.abs(Math.sin(tt*.9+ph)),3),CW];
    case 4:return[p.s*.78,0,0,(.12+.55*ph)*(.72+.28*Math.sin(tt*1.4+i*.37)),ph>.55?CW:CG];
    case 5:return[0,ph,0,.7+.12*Math.sin(tt*2.2),CG];
    case 6:{const u=(ph+tt*.05)%1;return[p.s*.85,0,0,Math.min(1,u/.08)*Math.pow(1-u,1.3),p.c?CW:CG]}
    case 7:return[1.15,0,0,.55,CW];
    case 8:return[1.3,0,0,.6,CW];
    case 9:return[1.15,0,0,.3,p.c?CG:CO];
    case 10:return[p.s*.8,0,0,.5+.3*Math.sin(tt*2+i),p.c?CW:CO];
    case 11:return[1.1,0,0,a*(.45+.55*Math.pow(.5+.5*Math.sin(ph-tt*1.6),4)),CW];
    default:return[p.s,0,0,p.c?.7:.9,p.c?CL:CO]}}
const spr=f=>{const c=document.createElement('canvas');c.width=c.height=128;f(c.getContext('2d'));return c};
const GLOW=spr(g=>{const r=g.createRadialGradient(64,64,0,64,64,64);r.addColorStop(0,'rgba(255,244,228,1)');r.addColorStop(.1,'rgba(255,216,168,.8)');r.addColorStop(.38,'rgba(232,146,86,.22)');r.addColorStop(1,'rgba(215,127,78,0)');g.fillStyle=r;g.fillRect(0,0,128,128)});
const FLARE=spr(g=>{g.translate(64,64);[0,Math.PI/2].forEach(a=>{g.save();g.rotate(a);const l=g.createLinearGradient(-64,0,64,0);l.addColorStop(0,'rgba(255,220,180,0)');l.addColorStop(.5,'rgba(255,248,236,1)');l.addColorStop(1,'rgba(255,220,180,0)');
  g.fillStyle=l;g.beginPath();g.moveTo(-64,0);g.lineTo(0,-2.4);g.lineTo(64,0);g.lineTo(0,2.4);g.closePath();g.fill();g.restore()})});
let mx=-999,my=-999;addEventListener('pointermove',e=>{mx=e.clientX;my=e.clientY},{passive:true});addEventListener('pointerleave',()=>{mx=my=-999});
const caps=$$('.dust-cap');let lastSY=scrollY;
function frame(t){requestAnimationFrame(frame);if(!ready)return;
  const dS=lastSY-scrollY;lastSY=scrollY; // as partículas andam junto com a página (sem atraso em relação às imagens)
  const [sa,sb,k]=state();caps.forEach(c=>{const on=!!c.offsetParent&&k>.85&&sb.contains(c);c.classList.toggle('on',on);c.parentElement.classList.toggle('on',on)});const A=SH[sa.dataset.shape],B=SH[sb.dataset.shape],pa=place(sa),pb=place(sb);
  const al=pa[3]+(pb[3]-pa[3])*k;ctx.setTransform(DPR,0,0,DPR,0,0);ctx.clearRect(0,0,innerWidth,innerHeight);if(al<.01){P.forEach(p=>p.init=false);return}
  ctx.globalCompositeOperation='lighter';const time=t/1000,tt=BZ.still?0:time,sc=(pa[2]+(pb[2]-pa[2])*k)/400;
  pmx+=((mx<-900?0:mx/innerWidth-.5)-pmx)*.04;pmy+=((my<-900?0:my/innerHeight-.5)-pmy)*.04;const RA=rot(sa.dataset.shape,tt),RB=rot(sb.dataset.shape,tt);
  for(let i=0;i<P.length;i++){const p=P[i];const lag=Math.max(0,Math.min(1,k*1.3-(i/P.length)*.3));
    const a=pos(sa,pa,A,i,tt,RA),b=pos(sb,pb,B,i,tt,RB);let tx=a[0]+(b[0]-a[0])*lag,ty=a[1]+(b[1]-a[1])*lag;
    if(!BZ.still&&sb.dataset.shape!=='flow'){tx+=Math.sin(time*.9+p.ph)*1.2;ty+=Math.cos(time*.8+p.ph)*1.2}
    if(!p.init){p.x=tx;p.y=ty+40;p.init=true}else p.y+=dS;
    if(lag>=1&&B[i][2]===6&&p.y-ty<-pb[2]*.2){p.x=tx;p.y=ty} // a coluna de luz recomeça embaixo sem riscar a tela
    if(lag>=1&&sb.dataset.shape==='flow'){p.x=tx;p.y=ty} // no trajeto o pó fica colado ao caminho (sem atraso nem saltos ao rolar)
    else{p.x+=(tx-p.x)*.12;p.y+=(ty-p.y)*.12} // desliza até o alvo, sem passar do ponto
    const dx=p.x+p.ox-mx,dy=p.y+p.oy-my,d2=dx*dx+dy*dy;let px=0,py=0;if(d2<9000){const d=Math.sqrt(d2)||1,f=(1-d2/9000)*22;px=dx/d*f;py=dy/d*f}
    p.ox+=(px-p.ox)*.1;p.oy+=(py-p.oy)*.1;
    const s1=sty(A[i],p,tt,i),s2=sty(B[i],p,tt,i),m=j=>s1[j]+(s2[j]-s1[j])*lag;
    const df=a[2]+(b[2]-a[2])*lag,dk=Math.min(1.3,Math.max(.35,1+(df-1)*2.4)); // perto: maior e mais forte; longe: menor e apagado
    const X=p.x+p.ox,Y=p.y+p.oy,sz=m(0)*df,gr=m(1)*sc*df,fl=m(2),op=m(3)*al*dk;
    if(gr>.6){ctx.globalAlpha=Math.min(1,op)*.85;ctx.drawImage(GLOW,X-gr,Y-gr,gr*2,gr*2);
      if(fl>.05){const r=gr*1.35;ctx.globalAlpha=Math.min(1,op*fl);ctx.drawImage(FLARE,X-r,Y-r,r*2,r*2)}ctx.globalAlpha=1}
    if(sz>.1){ctx.fillStyle=`rgba(${lag<.5?s1[4]:s2[4]},${op})`;ctx.fillRect(X-sz/2,Y-sz/2,sz,sz)}}
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
