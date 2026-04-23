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

  // ===== intersection reveal (subtle fade) =====
  if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const targets = document.querySelectorAll('.reveal, .proc-card, .padece-card, .tech-card, .proc-list > li, .proc-item, .diag-flow, .pull-quote, .detail-title, .tech-headline, .intro-statement, .diag-points li');
    targets.forEach(t => {
      t.style.opacity = '0';
      t.style.transform = 'translateY(12px)';
      t.style.transition = 'opacity 600ms var(--ease-out), transform 600ms var(--ease-out)';
    });
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry, i) => {
        if (entry.isIntersecting) {
          const delay = (entry.target._idx || i % 6) * 60;
          setTimeout(() => {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
          }, delay);
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    targets.forEach((t, i) => { t._idx = i; io.observe(t); });
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
