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

  /* ---------- Compartir ---------- */
  $$('[data-share]').forEach(b=>b.addEventListener('click',async()=>{
    const data={title:document.title,url:location.href.split('#')[0]};
    if(navigator.share){try{await navigator.share(data)}catch(e){};return}
    try{await navigator.clipboard.writeText(data.url);toast('Link copiado')}catch(e){prompt('Copiá el link:',data.url)}
  }));
})();
