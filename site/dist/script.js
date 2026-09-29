(() => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const word = document.getElementById('typed-word');
  const hero = document.querySelector('.hero');
  const tracks = document.querySelectorAll('.marquee-track');
  const words = ['development', 'testing', 'deployment', 'design'];
  let index = 0, deleting = true, timer, heroVisible = true;
  function syncMotion() {
    clearTimeout(timer);
    const active = !reduced.matches && !document.hidden;
    hero?.classList.toggle('typing-paused', !active || !heroVisible);
    tracks.forEach(track => track.classList.toggle('paused', !active));
    if (active && word && heroVisible) timer = setTimeout(tick, 120);
  }
  function tick() {
    const target = words[index];
    let delay;
    if (deleting) {
      word.textContent = word.textContent.slice(0, -1);
      delay = 55;
      if (!word.textContent) { deleting = false; index = (index + 1) % words.length; delay = 330; }
    } else {
      word.textContent = target.slice(0, word.textContent.length + 1);
      delay = 105;
      if (word.textContent === target) { deleting = true; delay = 2200; }
    }
    timer = setTimeout(tick, delay);
  }
  if (hero) new IntersectionObserver(entries => {
    heroVisible = entries[0].isIntersecting;
    syncMotion();
  }).observe(hero);
  document.addEventListener('visibilitychange', syncMotion);
  reduced.addEventListener('change', () => {
    if (reduced.matches && word) { word.textContent = 'development'; index = 0; deleting = true; }
    syncMotion();
  });
  syncMotion();

  const header = document.querySelector('.site-header');
  const links = [...document.querySelectorAll('nav a')];
  const sections = links.map(link => ({link, section: document.getElementById(link.hash.slice(1))})).filter(item => item.section);
  let scheduled = false;
  function updateNavigation() {
    scheduled = false;
    const threshold = header.getBoundingClientRect().height + 70;
    let current = null;
    for (const item of sections) {
      if (item.section.getBoundingClientRect().top <= threshold) current = item;
    }
    if (window.scrollY > 0 && window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2) current = sections.at(-1);
    for (const item of sections) {
      if (item === current) item.link.setAttribute('aria-current', 'location');
      else item.link.removeAttribute('aria-current');
    }
  }
  function scheduleNavigation() {
    if (!scheduled) { scheduled = true; requestAnimationFrame(updateNavigation); }
  }
  if (header) new ResizeObserver(() => {
    document.documentElement.style.setProperty('--header-height', `${header.getBoundingClientRect().height}px`);
    scheduleNavigation();
  }).observe(header);
  if (sections.length) {
    window.addEventListener('scroll', scheduleNavigation, {passive: true});
    window.addEventListener('resize', scheduleNavigation);
    updateNavigation();
  } else if (/\/contact(?:\.html)?\/?$/.test(location.pathname)) {
    document.querySelector('.nav-contact')?.setAttribute('aria-current', 'location');
  } else if (location.pathname.includes('/work/')) {
    links.find(link => link.hash === '#experience')?.setAttribute('aria-current', 'location');
  }
})();

(() => {
  const form = document.getElementById('idea-form');
  if (!form) return;
  const status = document.getElementById('form-status');
  const button = form.querySelector('button[type="submit"]');
  let widget;
  let ready = false;
  const initialise = async () => {
    try {
      const response = await fetch('/api/form-config');
      if (!response.ok) throw new Error();
      const {siteKey} = await response.json();
      if (!siteKey) throw new Error();
      const script = document.createElement('script');
      script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
      script.async = true;
      script.onload = () => {
        widget = window.turnstile.render('#turnstile-widget', {sitekey:siteKey,action:'enquiry',theme:'light'});
        ready = true;
      };
      script.onerror = () => { status.textContent = 'The spam check could not load. Please refresh or email us.'; };
      document.head.append(script);
    } catch { status.textContent = 'The form is not available here yet. You can email hello@liquidjelly.co.uk.'; }
  };
  // Load the spam check only when someone reaches the form.
  const observer = new IntersectionObserver(entries => {
    if (entries.some(entry => entry.isIntersecting)) { observer.disconnect(); void initialise(); }
  }, {rootMargin:'200px'});
  observer.observe(form);
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    if (!ready) { status.textContent = 'The form is not ready. Please try again shortly or email us.'; return; }
    const token = window.turnstile.getResponse(widget);
    if (!token) { status.textContent = 'Please complete the spam check before sending.'; return; }
    button.disabled = true; status.textContent = 'Sending your enquiry…';
    try {
      const data = Object.fromEntries(new FormData(form));
      const response = await fetch('/api/enquiries', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...data,token})});
      const result = await response.json();
      if (!response.ok || !result.ok) throw new Error(result.error || 'Please try again or email us.');
      form.reset(); status.textContent = 'Thank you. Your enquiry has been received. We’ll be in touch by email.';
    } catch (error) { status.textContent = error.message || 'We could not send your enquiry. Please try again or email us.'; }
    finally { button.disabled = false; window.turnstile.reset(widget); }
  });
})();

(() => {
  const work = document.querySelector('.selected-work');
  if (!work) return;
  const headings = [...work.querySelectorAll('.work-heading')];
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let pending = false;
  function render() {
    pending = false;
    work.classList.toggle('work-scroll-effects', !reduced.matches);
    if (reduced.matches) return;
    const headerBottom = document.querySelector('.site-header')?.getBoundingClientRect().bottom || 0;
    const entrance = Math.min(180, innerHeight * .22);
    for (const heading of headings) {
      const bounds = heading.getBoundingClientRect();
      const entering = (innerHeight - 35 - bounds.top) / entrance;
      const leaving = (bounds.bottom - headerBottom - 20) / 110;
      const progress = Math.max(0, Math.min(1, entering, leaving));
      // Smoothstep gives a gentle arrival and departure in either scroll direction.
      const eased = progress * progress * (3 - 2 * progress);
      heading.style.setProperty('--work-reveal', eased.toFixed(3));
    }
  }
  function schedule() {
    if (!pending) { pending = true; requestAnimationFrame(render); }
  }
  window.addEventListener('scroll', schedule, {passive:true});
  window.addEventListener('resize', schedule);
  reduced.addEventListener('change', schedule);
  document.fonts?.ready.then(schedule);
  render();
})();
