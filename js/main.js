/* ========================================
   THEWEAVE — main.js
   ======================================== */

// Nav: scroll-triggered background transition (index only)
(function initNav() {
  var nav = document.getElementById('nav');
  if (!nav) return;

  var isHeroPage = document.body.classList.contains('hero-page');
  if (!isHeroPage) return;

  function onScroll() {
    if (window.scrollY > 40) {
      nav.classList.add('is-scrolled');
    } else {
      nav.classList.remove('is-scrolled');
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();

// Nav: mobile hamburger toggle
(function initHamburger() {
  var btn = document.getElementById('nav-hamburger');
  var links = document.getElementById('nav-links');
  if (!btn || !links) return;

  btn.addEventListener('click', function () {
    var isOpen = links.classList.toggle('is-open');
    btn.classList.toggle('is-open', isOpen);
    btn.setAttribute('aria-expanded', String(isOpen));
    document.body.style.overflow = isOpen ? 'hidden' : '';
  });

  links.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', function () {
      links.classList.remove('is-open');
      btn.classList.remove('is-open');
      btn.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    });
  });
})();

// Scroll reveal: fade-in + slide-up for .reveal elements
(function initReveal() {
  var els = document.querySelectorAll('.reveal');
  if (!els.length || !window.IntersectionObserver) {
    // Fallback: show all immediately
    els.forEach(function (el) { el.classList.add('is-visible'); });
    return;
  }

  var obs = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -32px 0px' });

  els.forEach(function (el) { obs.observe(el); });
})();

// Stats: counter animation (IntersectionObserver, unobserved after trigger)
(function initCounters() {
  var counters = document.querySelectorAll('.stat-counter[data-target]');
  if (!counters.length || !window.IntersectionObserver) return;

  function animateCounter(el) {
    var target = parseInt(el.getAttribute('data-target'), 10);
    if (isNaN(target)) return;
    var duration = 1400;
    var start = null;

    function step(ts) {
      if (!start) start = ts;
      var elapsed = ts - start;
      var progress = Math.min(elapsed / duration, 1);
      // ease-out cubic
      var eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(eased * target);
      if (progress < 1) requestAnimationFrame(step);
    }

    requestAnimationFrame(step);
  }

  var obs = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        obs.unobserve(entry.target); // fire once only
      }
    });
  }, { threshold: 0.5 });

  counters.forEach(function (el) { obs.observe(el); });
})();

// Hero parallax: subtle offset on scroll
(function initHeroParallax() {
  var inner = document.querySelector('.hero-inner');
  if (!inner) return;

  var ticking = false;
  window.addEventListener('scroll', function () {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      var sy = window.scrollY;
      if (sy < window.innerHeight) {
        inner.style.transform = 'translateY(' + (sy * 0.22) + 'px)';
      }
      ticking = false;
    });
  }, { passive: true });
})();

// Magazine: fetch data/magazine.json and render cards
(function initMagazine() {
  var grid = document.getElementById('magazine-grid');
  if (!grid) return;

  function formatDate(str) {
    var d = new Date(str);
    if (isNaN(d)) return str;
    return d.getFullYear() + '.' +
      String(d.getMonth() + 1).padStart(2, '0') + '.' +
      String(d.getDate()).padStart(2, '0');
  }

  function esc(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function renderCards(articles) {
    grid.innerHTML = articles.map(function (a) {
      var imgHtml = a.thumbnail
        ? '<img src="' + esc(a.thumbnail) + '" alt="' + esc(a.title) + '" loading="lazy">'
        : '<div class="magazine-card-img-placeholder"></div>';

      var href = a.slug
        ? 'magazine-article.html?slug=' + encodeURIComponent(a.slug)
        : '#';

      return '<a href="' + href + '" class="magazine-card-link">' +
        '<article class="magazine-card reveal">' +
        '<div class="magazine-card-img">' + imgHtml + '</div>' +
        '<span class="magazine-card-category">' + esc(a.category) + '</span>' +
        '<h3 class="magazine-card-title">' + esc(a.title) + '</h3>' +
        '<p class="magazine-card-excerpt">' + esc(a.excerpt) + '</p>' +
        '<time class="magazine-card-date" datetime="' + esc(a.date) + '">' +
          formatDate(a.date) +
        '</time>' +
        '</article>' +
        '</a>';
    }).join('');

    // Attach IntersectionObserver to newly rendered cards
    if (!window.IntersectionObserver) {
      grid.querySelectorAll('.reveal').forEach(function (el) {
        el.classList.add('is-visible');
      });
      return;
    }
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -32px 0px' });

    grid.querySelectorAll('.reveal').forEach(function (el) { obs.observe(el); });
  }

  function renderError() {
    grid.innerHTML = '<p class="magazine-error">콘텐츠를 불러오는 중 오류가 발생했습니다.</p>';
  }

  // Use relative path — works on both GitHub Pages and local npx serve
  fetch('./data/magazine.json')
    .then(function (res) {
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return res.json();
    })
    .then(function (data) {
      if (!data || !Array.isArray(data.articles) || !data.articles.length) {
        renderError();
        return;
      }
      renderCards(data.articles);
    })
    .catch(renderError);
})();

// Hero canvas: silk thread / weave animation
(function initHeroCanvas() {
  var canvas = document.getElementById('hero-canvas');
  if (!canvas || !canvas.getContext) return;

  var ctx = canvas.getContext('2d');
  var W, H, strands, rafId;

  function buildStrands() {
    var count = Math.max(14, Math.floor(W / 75));
    strands = [];
    for (var i = 0; i < count; i++) {
      var isAccent = Math.random() < 0.2;
      strands.push({
        y0:     (i / count) * H * 1.3 - H * 0.15,
        phase:  Math.random() * Math.PI * 2,
        phase2: Math.random() * Math.PI * 2,
        freq:   0.0018 + Math.random() * 0.0025,
        freq2:  0.0038 + Math.random() * 0.003,
        amp:    25 + Math.random() * 65,
        drift:  (Math.random() - 0.5) * 0.012,
        opacity: isAccent ? (0.25 + Math.random() * 0.15) : (0.08 + Math.random() * 0.1),
        width:  0.5 + Math.random() * 1.3,
        isAccent: isAccent
      });
    }
  }

  function resize() {
    var hero = canvas.parentElement;
    W = canvas.width  = (canvas.offsetWidth  || (hero && hero.offsetWidth)  || window.innerWidth);
    H = canvas.height = (canvas.offsetHeight || (hero && hero.offsetHeight) || window.innerHeight);
    buildStrands();
  }

  var t = 0;

  function draw() {
    ctx.clearRect(0, 0, W, H);

    for (var i = 0; i < strands.length; i++) {
      var s = strands[i];

      s.y0 += s.drift;
      if (s.y0 >  H + 60) s.y0 = -60;
      if (s.y0 < -60)      s.y0 = H + 60;

      var steps = Math.ceil(W / 3);
      ctx.beginPath();
      for (var j = 0; j <= steps; j++) {
        var x = (j / steps) * W;
        var y = s.y0
          + Math.sin(x * s.freq  + t * 0.38 + s.phase)  * s.amp
          + Math.sin(x * s.freq2 + t * 0.22 + s.phase2) * (s.amp * 0.32);
        if (j === 0) ctx.moveTo(x, y);
        else         ctx.lineTo(x, y);
      }

      ctx.strokeStyle = s.isAccent
        ? 'rgba(232,114,42,' + s.opacity + ')'
        : 'rgba(215,210,205,' + s.opacity + ')';
      ctx.lineWidth = s.width;
      ctx.stroke();
    }

    t += 0.004;
    rafId = requestAnimationFrame(draw);
  }

  window.addEventListener('resize', function () {
    cancelAnimationFrame(rafId);
    resize();
    draw();
  });

  // defer one frame so layout is computed before reading offsetWidth/Height
  requestAnimationFrame(function startLoop() {
    resize();
    if (W === 0 || H === 0) { requestAnimationFrame(startLoop); return; }
    draw();
  });
})();

// Contact form: Formspree submission
(function initContactForm() {
  var form = document.getElementById('contact-form');
  if (!form) return;

  var submitBtn = form.querySelector('.form-submit-btn');
  var message   = form.querySelector('.form-message');

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    // TODO: Replace data-formspree-id attribute value with actual Formspree form ID
    var formspreeId = form.getAttribute('data-formspree-id');
    if (!formspreeId || formspreeId === 'TODO') {
      showMessage(
        '폼 설정이 완료되지 않았습니다. (Formspree ID 설정 필요)',
        'is-error'
      );
      return;
    }

    setLoading(true);

    fetch('https://formspree.io/f/' + formspreeId, {
      method: 'POST',
      body: new FormData(form),
      headers: { Accept: 'application/json' }
    })
      .then(function (res) {
        if (!res.ok) throw new Error('submit failed');
        form.reset();
        showMessage(
          '문의가 접수되었습니다. 빠른 시일 내에 연락드리겠습니다.',
          'is-success'
        );
      })
      .catch(function () {
        showMessage(
          '전송 중 오류가 발생했습니다. 이메일(info@theweave.co.kr)로 직접 문의해 주세요.',
          'is-error'
        );
      })
      .finally(function () {
        setLoading(false);
      });
  });

  function setLoading(loading) {
    if (!submitBtn) return;
    submitBtn.disabled = loading;
    submitBtn.textContent = loading ? '전송 중…' : '문의 보내기';
  }

  function showMessage(text, cls) {
    if (!message) return;
    message.textContent = text;
    message.className = 'form-message is-visible ' + cls;
  }
})();
