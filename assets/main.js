(() => {
  const button = document.querySelector('[data-menu-button]');
  const nav = document.querySelector('[data-site-nav]');

  if (button && nav) {
    const mobileNav = window.matchMedia('(max-width: 920px)');

    const setMenuState = (isOpen, { restoreFocus = false } = {}) => {
      const open = mobileNav.matches && isOpen;
      nav.classList.toggle('is-open', open);
      button.setAttribute('aria-expanded', String(open));
      button.setAttribute('aria-label', open ? 'メニューを閉じる' : 'メニューを開く');
      nav.toggleAttribute('inert', mobileNav.matches && !open);

      if (restoreFocus && mobileNav.matches) button.focus();
    };

    button.addEventListener('click', () => {
      setMenuState(!nav.classList.contains('is-open'));
    });

    nav.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => setMenuState(false));
    });

    document.addEventListener('keydown', (event) => {
      if (event.key !== 'Escape' || !nav.classList.contains('is-open')) return;
      setMenuState(false, { restoreFocus: true });
    });

    document.addEventListener('click', (event) => {
      if (!nav.classList.contains('is-open')) return;
      if (nav.contains(event.target) || button.contains(event.target)) return;
      setMenuState(false);
    });

    mobileNav.addEventListener('change', () => setMenuState(false));
    setMenuState(false);
  }

  const revealItems = document.querySelectorAll('.reveal');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (reduceMotion || !('IntersectionObserver' in window)) {
    revealItems.forEach((item) => item.classList.add('is-visible'));
  } else {
    const observer = new IntersectionObserver((entries, currentObserver) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        currentObserver.unobserve(entry.target);
      });
    }, { threshold: 0.12 });

    revealItems.forEach((item) => observer.observe(item));
  }

  const year = document.querySelector('[data-current-year]');
  if (year) year.textContent = String(new Date().getFullYear());

  const heroMedia = document.querySelector('[data-hero-media]');
  if (heroMedia) {
    const video = heroMedia.querySelector('[data-hero-video]');
    const reduceMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

    const enableStillOnly = () => {
      heroMedia.classList.remove('hero-video-active');
      video.pause();
      video.removeAttribute('src');
      video.querySelectorAll('source').forEach((source) => source.remove());
      video.load();
    };

    const enableVideo = () => {
      if (!video.querySelector('source')) {
        const source = document.createElement('source');
        source.src = video.dataset.src;
        source.type = 'video/mp4';
        video.appendChild(source);
        video.load();
      }
      video.play().catch(() => {
        // Autoplay was blocked; the poster/still image remains visible.
      });
      heroMedia.classList.add('hero-video-active');
    };

    const applyMotionPreference = (query) => {
      if (query.matches) enableStillOnly();
      else enableVideo();
    };

    applyMotionPreference(reduceMotionQuery);
    reduceMotionQuery.addEventListener('change', applyMotionPreference);
  }
})();
