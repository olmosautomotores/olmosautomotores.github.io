(function(){
  const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
  const norm=s=>(s||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');

  function toast(msg){let t=$('.toast');if(!t){t=document.createElement('div');t.className='toast';document.body.appendChild(t)}
    t.textContent=msg;t.classList.add('on');clearTimeout(t._h);t._h=setTimeout(()=>t.classList.remove('on'),2200)}

  /* ---------- Listado ---------- */
  const grid=$('#grid');
  if(grid){
    const cards=$$('.card',grid), q=$('#q'), sort=$('#sort'), chips=$$('.chip'), count=$('#count'), empty=$('#empty');
    let tipo='todos';
    function apply(){
      const t=norm(q.value).split(/\s+/).filter(Boolean);
      let n=0;
      cards.forEach(c=>{
        const ok=(tipo==='todos'||c.dataset.tipo===tipo)&&t.every(w=>c.dataset.txt.includes(w));
        c.hidden=!ok; if(ok)n++;
      });
      const k=sort.value, key={recientes:c=>-+c.dataset.fecha,anio:c=>-+c.dataset.anio,km:c=>+c.dataset.km}[k];
      cards.slice().sort((a,b)=>key(a)-key(b)).forEach(c=>grid.appendChild(c));
      grid.appendChild(empty);
      empty.hidden=n>0;
      count.textContent=n===1?'1 vehículo':n+' vehículos';
    }
    q.addEventListener('input',apply); sort.addEventListener('change',apply);
    chips.forEach(ch=>ch.addEventListener('click',()=>{chips.forEach(x=>x.setAttribute('aria-pressed',x===ch));tipo=ch.dataset.tipo;apply()}));
    apply();
  }

  /* ---------- Galería ---------- */
  const stage=$('.stage');
  if(stage){
    const track=$('.track',stage), imgs=$$('img',track), thumbs=$$('.thumbs button'), counter=$('.counter',stage);
    const lb=$('.lb'), lbImg=$('img',lb), lbCount=$('.counter',lb);
    let i=0; const N=imgs.length;
    function go(k){i=(k+N)%N;track.style.transform=`translateX(${-i*100}%)`;thumbs.forEach((b,j)=>b.setAttribute('aria-current',j===i));
      counter.textContent=`${i+1} / ${N}`;if(lb.classList.contains('on')){lbImg.src=imgs[i].dataset.full||imgs[i].src;lbCount.textContent=`${i+1} / ${N}`}
      const nx=imgs[(i+1)%N]; if(nx.loading==='lazy')nx.loading='eager'}
    $('.prev',stage).onclick=()=>go(i-1); $('.next',stage).onclick=()=>go(i+1);
    thumbs.forEach((b,j)=>b.onclick=()=>go(j));
    let x0=null,y0=null;
    stage.addEventListener('touchstart',e=>{x0=e.touches[0].clientX;y0=e.touches[0].clientY},{passive:true});
    stage.addEventListener('touchend',e=>{if(x0===null)return;const dx=e.changedTouches[0].clientX-x0,dy=e.changedTouches[0].clientY-y0;
      if(Math.abs(dx)>40&&Math.abs(dx)>Math.abs(dy))go(i+(dx<0?1:-1));x0=null},{passive:true});
    imgs.forEach(im=>im.addEventListener('click',()=>{lb.classList.add('on');document.body.style.overflow='hidden';go(i)}));
    const close=()=>{lb.classList.remove('on');document.body.style.overflow=''};
    $('.x',lb).onclick=close; lb.addEventListener('click',e=>{if(e.target===lb)close()});
    $('.prev',lb).onclick=e=>{e.stopPropagation();go(i-1)}; $('.next',lb).onclick=e=>{e.stopPropagation();go(i+1)};
    let lx=null; lb.addEventListener('touchstart',e=>{lx=e.touches[0].clientX},{passive:true});
    lb.addEventListener('touchend',e=>{if(lx===null)return;const dx=e.changedTouches[0].clientX-lx;if(Math.abs(dx)>40)go(i+(dx<0?1:-1));lx=null},{passive:true});
    document.addEventListener('keydown',e=>{if(e.key==='ArrowLeft')go(i-1);else if(e.key==='ArrowRight')go(i+1);else if(e.key==='Escape')close()});
    go(0);
  }

  /* ---------- Formularios -> WhatsApp ---------- */
  const tabs=$$('.tab');
  function showTab(name){tabs.forEach(t=>t.setAttribute('aria-selected',t.dataset.tab===name));$$('.fm').forEach(f=>f.hidden=f.dataset.wa!==name)}
  tabs.forEach(t=>t.addEventListener('click',()=>showTab(t.dataset.tab)));
  $$('a[data-tab]').forEach(a=>a.addEventListener('click',()=>showTab(a.dataset.tab)));
  const WA=(document.querySelector('meta[name=wa]')||{}).content;
  $$('.fm').forEach(f=>f.addEventListener('submit',ev=>{
    ev.preventDefault(); let bad=null;
    $$('[required]',f).forEach(el=>{const ok=el.value.trim()!=='';el.closest('.f').classList.toggle('err',!ok);if(!ok&&!bad)bad=el});
    if(bad){bad.focus();toast('Completá los campos marcados');return}
    const lines=[]; $$('input,select,textarea',f).forEach(el=>{const v=el.value.trim();if(v)lines.push(`• ${el.name}: ${v}`)});
    const head=f.dataset.wa==='cotizar'?'Hola! Quiero cotizar mi auto:':'Hola! Estoy buscando un auto:';
    const msg=head+'\n'+lines.join('\n')+(f.dataset.wa==='cotizar'?'\n\nTe mando fotos por acá.':'');
    window.open(`https://wa.me/${WA}?text=${encodeURIComponent(msg)}`,'_blank','noopener');
  }));
  $$('.fm [required]').forEach(el=>{const clr=()=>el.closest('.f').classList.remove('err');el.addEventListener('input',clr);el.addEventListener('change',clr)});

  /* ---------- Entregas (visor) ---------- */
  const ents=$$('.ent-row button');
  if(ents.length){
    const lb=$('.lb'), im=$('img',lb), ct=$('.counter',lb); let k=0;
    const show=n=>{k=(n+ents.length)%ents.length;im.src=ents[k].dataset.full;im.alt=ents[k].getAttribute('aria-label');ct.textContent=`${k+1} / ${ents.length}`};
    const close=()=>{lb.classList.remove('on');document.body.style.overflow=''};
    ents.forEach((b,i)=>b.addEventListener('click',()=>{show(i);lb.classList.add('on');document.body.style.overflow='hidden'}));
    $('.x',lb).onclick=close; lb.addEventListener('click',e=>{if(e.target===lb)close()});
    $('.prev',lb).onclick=e=>{e.stopPropagation();show(k-1)}; $('.next',lb).onclick=e=>{e.stopPropagation();show(k+1)};
    let x0=null; lb.addEventListener('touchstart',e=>{x0=e.touches[0].clientX},{passive:true});
    lb.addEventListener('touchend',e=>{if(x0===null)return;const dx=e.changedTouches[0].clientX-x0;if(Math.abs(dx)>40)show(k+(dx<0?1:-1));x0=null},{passive:true});
    document.addEventListener('keydown',e=>{if(!lb.classList.contains('on'))return;if(e.key==='ArrowLeft')show(k-1);else if(e.key==='ArrowRight')show(k+1);else if(e.key==='Escape')close()});
  }

  /* ---------- Portada rotativa ---------- */
  const himgs=$$('.hero-media img'), hcaps=$$('.hero-cap');
  if(himgs.length>1){
    const load=im=>{if(im.dataset.src&&!im.src){im.src=im.dataset.src}};
    let h=Math.floor(Math.random()*himgs.length);
    const show=n=>{const im=himgs[n];load(im);const go=()=>{himgs.forEach((x,j)=>x.classList.toggle('on',j===n));hcaps.forEach((x,j)=>x.classList.toggle('on',j===n));load(himgs[(n+1)%himgs.length])};
      if(im.complete&&im.naturalWidth)go();else im.addEventListener('load',go,{once:true})};
    if(h!==0)show(h); else load(himgs[1]);
    setInterval(()=>{if(document.hidden)return;h=(h+1)%himgs.length;show(h)},6000);
  }

  /* ---------- Animaciones al bajar ---------- */
  // Solo se animan los elementos que están más abajo de la pantalla inicial; lo visible al cargar aparece directo.
  const rv=$$('.sec-head,.card,.svc-card,.sell,.fm:not([hidden]),.tabs,.ent-row,.contact-main,.ci,.eq-g,.equip h2');
  const pending=new Set();
  const reveal=t=>{if(!pending.has(t))return;pending.delete(t);t.classList.add('in');setTimeout(()=>{t.classList.remove('rv','in');t.style.transitionDelay=''},1300)};
  const check=()=>{const lim=innerHeight*0.94;pending.forEach(t=>{if(t.getBoundingClientRect().top<lim)reveal(t)})};
  if(!matchMedia('(prefers-reduced-motion: reduce)').matches){
    const seen=new Map();
    rv.forEach(el=>{if(el.getBoundingClientRect().top<innerHeight)return;
      document.documentElement.classList.add('js');el.classList.add('rv');pending.add(el);
      const p=el.parentElement,n=seen.get(p)||0;seen.set(p,n+1);el.style.transitionDelay=Math.min(n,5)*70+'ms'});
    addEventListener('scroll',check,{passive:true}); addEventListener('resize',check);
  }

  /* ---------- Barra fija (ficha) ---------- */
  const bar=$('.bar'), acc=$('#acciones');
  if(bar&&acc){
    document.body.classList.add('has-bar');
    const upd=()=>bar.classList.toggle('on',acc.getBoundingClientRect().bottom<0);
    addEventListener('scroll',upd,{passive:true}); upd();
  }

  /* ---------- Compartir ---------- */
  $$('[data-share]').forEach(b=>b.addEventListener('click',async()=>{
    const data={title:document.title,url:location.href.split('#')[0]};
    if(navigator.share){try{await navigator.share(data)}catch(e){};return}
    try{await navigator.clipboard.writeText(data.url);toast('Link copiado')}catch(e){prompt('Copiá el link:',data.url)}
  }));
})();
