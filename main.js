(() => {
  'use strict';

  // ===== year =====
  document.querySelectorAll('[data-year]').forEach(el => {
    el.textContent = new Date().getFullYear();
  });

  // ===== mobile nav =====
  const nav = document.querySelector('[data-nav]');
  const burger = document.querySelector('[data-burger]');
  if (nav && burger) {
    burger.addEventListener('click', () => {
      const open = nav.classList.toggle('is-open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.querySelectorAll('[data-links] a').forEach(a => {
      a.addEventListener('click', () => {
        nav.classList.remove('is-open');
        burger.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // ===== procedure carousel =====
  const carousel = document.querySelector('[data-carousel]');
  if (carousel) {
    const grid = carousel.querySelector('[data-carousel-grid]');
    const prev = carousel.querySelector('[data-prev]');
    const next = carousel.querySelector('[data-next]');
    const firstCard = grid?.querySelector('.proc-card');

    const cardStep = () => {
      if (!firstCard) return 320;
      const style = getComputedStyle(grid);
      const gap = parseFloat(style.columnGap || style.gap || '0') || 0;
      return firstCard.getBoundingClientRect().width + gap;
    };

    let autoScrollInterval;
    const startAutoScroll = () => {
      autoScrollInterval = setInterval(() => {
        const max = grid.scrollWidth - grid.clientWidth - 2;
        if (grid.scrollLeft >= max) {
          grid.scrollTo({ left: 0, behavior: 'smooth' });
        } else {
          grid.scrollBy({ left: cardStep(), behavior: 'smooth' });
        }
      }, 3500);
    };

    const stopAutoScroll = () => clearInterval(autoScrollInterval);

    grid.addEventListener('mouseenter', stopAutoScroll);
    grid.addEventListener('mouseleave', startAutoScroll);
    grid.addEventListener('touchstart', stopAutoScroll, { passive: true });
    grid.addEventListener('touchend', startAutoScroll, { passive: true });

    startAutoScroll();

    prev?.addEventListener('click', () => {
      grid.scrollBy({ left: -cardStep(), behavior: 'smooth' });
    });
    next?.addEventListener('click', () => {
      grid.scrollBy({ left: cardStep(), behavior: 'smooth' });
    });

    const updateNav = () => {
      const max = grid.scrollWidth - grid.clientWidth - 2;
      if (prev) prev.style.opacity = grid.scrollLeft <= 0 ? '0.35' : '1';
      if (next) next.style.opacity = grid.scrollLeft >= max ? '0.35' : '1';
    };
    grid.addEventListener('scroll', updateNav, { passive: true });
    updateNav();
  }

  // ===== contact form fake submit =====
  const form = document.querySelector('[data-form]');
  if (form) {
    const success = form.querySelector('[data-success]');
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      if (success) {
        success.hidden = false;
        form.querySelector('button[type="submit"]').setAttribute('disabled', 'true');
      }
    });
  }

  // ===== intersection reveal (refined) =====
  if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const targets = document.querySelectorAll('.reveal, .proc-card, .padece-card, .tech-card, .proc-list > li, .proc-item, .diag-flow, .pull-quote, .detail-title, .tech-headline, .intro-statement, .diag-points li');
    
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('active');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.1 });

    targets.forEach((t) => io.observe(t));
  }

  // ===== anchor offset for sticky nav =====
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href');
      if (id.length < 2) return;
      const el = document.querySelector(id);
      if (!el) return;
      e.preventDefault();
      const navH = document.querySelector('.nav')?.offsetHeight || 72;
      window.scrollTo({ top: el.offsetTop - navH - 8, behavior: 'smooth' });
    });
  });

})();
