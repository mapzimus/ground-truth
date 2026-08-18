(function(){
  const box = document.getElementById('swipe');
  if (!box) return;
  const stage = document.getElementById('swipeStage');
  const top = document.getElementById('swipeTop');
  const bar = document.getElementById('swipeBar');
  const fsBtn = document.getElementById('swipeFs');
  let frac = 0.5, scale = 1, tx = 0, ty = 0;
  function apply(){
    top.style.clipPath = 'inset(0 ' + ((1 - frac) * 100) + '% 0 0)';
    bar.style.left = (frac * 100) + '%';
    box.setAttribute('aria-valuenow', Math.round(frac * 100));
    stage.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + scale + ')';
  }
  apply();
  function setFrac(e){
    const r = stage.getBoundingClientRect();
    frac = Math.max(0.02, Math.min(0.98, (e.clientX - r.left) / r.width));
  }
  function zoomAt(cx, cy, factor){
    const ns = Math.min(6, Math.max(1, scale * factor));
    const r = box.getBoundingClientRect();
    const ox = cx - (r.left + r.width / 2), oy = cy - (r.top + r.height / 2);
    tx -= ox * (ns / scale - 1); ty -= oy * (ns / scale - 1);
    scale = ns;
    if (scale === 1){ tx = 0; ty = 0; }
    apply();
  }
  const ptrs = new Map();
  let pinch = 0, onBar = false, lastTap = 0;
  box.addEventListener('pointerdown', e => {
    if (e.target === fsBtn) return;
    e.preventDefault();
    ptrs.set(e.pointerId, e);
    box.setPointerCapture(e.pointerId);
    if (ptrs.size === 1){
      const r = stage.getBoundingClientRect();
      const barX = r.left + frac * r.width;
      onBar = scale === 1 || Math.abs(e.clientX - barX) < 48;
      if (onBar){ setFrac(e); apply(); }
      const now = Date.now();                       // double-tap zoom toggle
      if (now - lastTap < 300){
        if (scale > 1){ scale = 1; tx = ty = 0; apply(); }
        else zoomAt(e.clientX, e.clientY, 2.5);
        onBar = false;
      }
      lastTap = now;
    } else if (ptrs.size === 2){
      const [a, b] = [...ptrs.values()];
      pinch = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
      onBar = false;
    }
  });
  box.addEventListener('pointermove', e => {
    if (!ptrs.has(e.pointerId)) return;
    const prev = ptrs.get(e.pointerId);
    ptrs.set(e.pointerId, e);
    if (ptrs.size === 1){
      if (onBar){ setFrac(e); apply(); }
      else if (scale > 1){ tx += e.clientX - prev.clientX; ty += e.clientY - prev.clientY; apply(); }
    } else if (ptrs.size === 2){
      const [a, b] = [...ptrs.values()];
      const d = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
      if (pinch > 0) zoomAt((a.clientX + b.clientX) / 2, (a.clientY + b.clientY) / 2, d / pinch);
      pinch = d;
    }
  });
  ['pointerup', 'pointercancel'].forEach(ev => box.addEventListener(ev, e => {
    ptrs.delete(e.pointerId);
    pinch = 0;
  }));
  box.addEventListener('wheel', e => {
    e.preventDefault();
    zoomAt(e.clientX, e.clientY, Math.exp(-e.deltaY * 0.0018));
  }, {passive: false});
  box.addEventListener('keydown', e => {
    const step = e.shiftKey ? 0.1 : 0.03;
    if (e.key === 'ArrowLeft') frac = Math.max(0.02, frac - step);
    else if (e.key === 'ArrowRight') frac = Math.min(0.98, frac + step);
    else if (e.key === 'Home') frac = 0.02;
    else if (e.key === 'End') frac = 0.98;
    else return;
    e.preventDefault();
    apply();
  });
  function setFs(on){
    box.classList.toggle('fs', on);
    document.body.style.overflow = on ? 'hidden' : '';
    fsBtn.textContent = on ? '✕' : '⛶';
    scale = 1; tx = ty = 0; apply();
  }
  fsBtn.addEventListener('click', () => setFs(!box.classList.contains('fs')));
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && box.classList.contains('fs')) setFs(false);
  });
})();


// click-to-enlarge with zoom + pan for every figure image (except the swipe pair)
(function(){
  const lb = document.createElement('div');
  lb.className = 'lightbox';
  lb.innerHTML = '<button class="close" aria-label="Close enlarged image">✕</button>' +
    '<img alt="" draggable="false"><div class="cap"></div>' +
    '<div class="hint">scroll or pinch to zoom · drag to pan · double-click resets · Esc or click outside closes</div>';
  lb.setAttribute('role', 'dialog');
  lb.setAttribute('aria-modal', 'true');
  lb.setAttribute('aria-label', 'Enlarged image');
  document.body.appendChild(lb);
  const lbImg = lb.querySelector('img'), lbCap = lb.querySelector('.cap'), lbClose = lb.querySelector('.close');

  let scale = 1, tx = 0, ty = 0;
  function apply(){ lbImg.style.transform = `translate(${tx}px, ${ty}px) scale(${scale})`; }
  function reset(){ scale = 1; tx = 0; ty = 0; apply(); }
  function zoomAt(cx, cy, factor){
    const ns = Math.min(10, Math.max(1, scale * factor));
    const r = lbImg.getBoundingClientRect();
    const ox = cx - (r.left + r.width / 2), oy = cy - (r.top + r.height / 2);
    tx -= ox * (ns / scale - 1); ty -= oy * (ns / scale - 1);
    scale = ns;
    if (scale === 1){ tx = 0; ty = 0; }
    apply();
  }

  let lastTrigger = null;
  function openFor(img){
    lbImg.src = img.src;
    lbImg.alt = img.alt;
    const fc = img.closest('figure').querySelector('figcaption');
    lbCap.textContent = fc ? fc.textContent : '';
    reset();
    lastTrigger = img;
    lb.classList.add('open');
    lbClose.focus();
  }
  document.querySelectorAll('figure img').forEach(img => {
    if (img.closest('.swipe')) return;
    img.tabIndex = 0;
    img.setAttribute('role', 'button');
    img.addEventListener('click', () => openFor(img));
    img.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' '){ e.preventDefault(); openFor(img); }
    });
  });

  lb.addEventListener('wheel', e => {
    e.preventDefault();
    zoomAt(e.clientX, e.clientY, Math.exp(-e.deltaY * 0.0018));
  }, {passive: false});
  lbImg.addEventListener('dblclick', e => {
    e.stopPropagation();
    if (scale > 1) reset(); else zoomAt(e.clientX, e.clientY, 3);
  });

  // drag pan + two-finger pinch
  const ptrs = new Map();
  let pinchDist = 0;
  lbImg.addEventListener('pointerdown', e => {
    e.preventDefault();
    ptrs.set(e.pointerId, e);
    lbImg.setPointerCapture(e.pointerId);
    if (ptrs.size === 2){
      const [a, b] = [...ptrs.values()];
      pinchDist = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
    }
  });
  lbImg.addEventListener('pointermove', e => {
    if (!ptrs.has(e.pointerId)) return;
    const prev = ptrs.get(e.pointerId);
    ptrs.set(e.pointerId, e);
    if (ptrs.size === 1){
      tx += e.clientX - prev.clientX; ty += e.clientY - prev.clientY;
      apply();
    } else if (ptrs.size === 2){
      const [a, b] = [...ptrs.values()];
      const d = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
      if (pinchDist > 0) zoomAt((a.clientX + b.clientX) / 2, (a.clientY + b.clientY) / 2, d / pinchDist);
      pinchDist = d;
    }
  });
  ['pointerup', 'pointercancel'].forEach(ev => lbImg.addEventListener(ev, e => {
    ptrs.delete(e.pointerId);
    pinchDist = 0;
  }));
  lbImg.addEventListener('click', e => e.stopPropagation());   // img clicks never close

  function close(){
    lb.classList.remove('open');
    ptrs.clear();
    if (lastTrigger){ lastTrigger.focus(); lastTrigger = null; }
  }
  lb.addEventListener('click', close);                          // backdrop click closes
  lb.addEventListener('keydown', e => {                         // minimal focus trap
    if (e.key === 'Tab'){ e.preventDefault(); lbClose.focus(); }
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
})();
