/* ========================================
   THEWEAVE — artists.js
   ======================================== */
(function () {
  function esc(s) {
    return String(s || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function publishedSorted(artists) {
    return (artists || [])
      .filter(function (a) { return a && a.published === true; })
      .sort(function (a, b) { return (a.order || 0) - (b.order || 0); });
  }

  function observeReveal(root) {
    var els = (root || document).querySelectorAll('.reveal');
    if (!els.length) return;
    if (!window.IntersectionObserver) {
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
    }, { threshold: 0.08, rootMargin: '0px 0px -32px 0px' });
    els.forEach(function (el) { obs.observe(el); });
  }

  function displayName(a) {
    return (a && (a.nameEn || a.name)) || '';
  }

  function cardHtml(a, withOneLiner) {
    var href = 'artist.html?id=' + encodeURIComponent(a.id || a.slug);
    var name = displayName(a);
    var img = a.heroImage
      ? '<img src="' + esc(a.heroImage) + '" alt="' + esc(name) + '" loading="lazy">'
      : '';
    var one = (withOneLiner && a.oneLiner)
      ? '<p class="artist-card-oneliner">' + esc(a.oneLiner) + '</p>'
      : '';
    return (
      '<a class="artist-card-link reveal" href="' + href + '">' +
        '<div class="artist-card-img">' + img + '</div>' +
        '<h3 class="artist-card-name">' + esc(name) + '</h3>' +
        one +
      '</a>'
    );
  }

  function renderGrid(grid, artists, withOneLiner) {
    var list = publishedSorted(artists);
    if (!list.length) {
      grid.innerHTML = '';
      return;
    }
    grid.innerHTML = list.map(function (a) {
      return cardHtml(a, withOneLiner);
    }).join('');
    observeReveal(grid);
  }

  function loadArtists() {
    return fetch('./data/artists.json?v=heo-bio', { cache: 'no-store' })
      .then(function (res) {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return res.json();
      })
      .then(function (data) { return data.artists || []; });
  }

  function ensureLightbox() {
    var lb = document.getElementById('artist-lightbox');
    if (lb) return lb;

    if (!document.getElementById('artist-lightbox-styles')) {
      var style = document.createElement('style');
      style.id = 'artist-lightbox-styles';
      style.textContent =
        '.artist-lightbox{position:fixed;inset:0;z-index:3000;display:none;align-items:center;justify-content:center;padding:48px 24px;}' +
        '.artist-lightbox.is-open{display:flex;}' +
        '.artist-lightbox-backdrop{position:absolute;inset:0;background:rgba(0,0,0,.92);cursor:pointer;}' +
        '.artist-lightbox-close{position:absolute;top:20px;right:20px;z-index:2;min-width:72px;height:40px;padding:0 14px;border:1px solid rgba(255,255,255,.55);background:rgba(0,0,0,.35);color:#fff;font-size:14px;font-weight:600;letter-spacing:.02em;cursor:pointer;}' +
        '.artist-lightbox-close:hover{border-color:#fff;background:rgba(0,0,0,.55);}' +
        '.artist-lightbox-figure{position:relative;z-index:1;margin:0;max-width:min(1100px,100%);max-height:calc(100vh - 96px);}' +
        '.artist-lightbox-img{display:block;max-width:100%;max-height:calc(100vh - 96px);width:auto;height:auto;object-fit:contain;margin:0 auto;}';
      document.head.appendChild(style);
    }

    lb = document.createElement('div');
    lb.id = 'artist-lightbox';
    lb.className = 'artist-lightbox';
    lb.setAttribute('role', 'dialog');
    lb.setAttribute('aria-modal', 'true');
    lb.setAttribute('aria-label', '작품 이미지 보기');
    lb.innerHTML =
      '<div class="artist-lightbox-backdrop" data-lightbox-close></div>' +
      '<button type="button" class="artist-lightbox-close" data-lightbox-close aria-label="닫기">닫기</button>' +
      '<figure class="artist-lightbox-figure">' +
        '<img class="artist-lightbox-img" alt="">' +
      '</figure>';
    document.body.appendChild(lb);

    function closeLightbox() {
      lb.classList.remove('is-open');
      document.body.style.overflow = '';
      var img = lb.querySelector('.artist-lightbox-img');
      if (img) {
        img.removeAttribute('src');
        img.alt = '';
      }
    }

    lb.addEventListener('click', function (e) {
      if (e.target.closest('[data-lightbox-close]')) closeLightbox();
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && lb.classList.contains('is-open')) closeLightbox();
    });

    lb._close = closeLightbox;
    return lb;
  }

  function openLightbox(src, alt) {
    if (!src) return;
    var lb = ensureLightbox();
    var img = lb.querySelector('.artist-lightbox-img');
    img.src = src;
    img.alt = alt || '';
    lb.classList.add('is-open');
    document.body.style.overflow = 'hidden';
    var closeBtn = lb.querySelector('.artist-lightbox-close');
    if (closeBtn) closeBtn.focus();
  }

  function bindWorkLightbox(root) {
    if (!root) return;
    root.querySelectorAll('[data-lightbox-src]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        openLightbox(btn.getAttribute('data-lightbox-src'), btn.getAttribute('data-lightbox-alt'));
      });
    });
  }

  function initHomeOrList() {
    var grid = document.getElementById('artists-grid');
    if (!grid) return;
    var withOneLiner = grid.getAttribute('data-with-oneliner') === 'true';
    loadArtists()
      .then(function (artists) { renderGrid(grid, artists, withOneLiner); })
      .catch(function () {
        grid.innerHTML = '<p class="magazine-error">작가 정보를 불러오는 중 오류가 발생했습니다.</p>';
      });
  }

  function renderParagraphs(content) {
    if (!content) return '';
    return content.split('\n\n')
      .filter(function (p) { return p.trim(); })
      .map(function (p) {
        return '<p>' + esc(p.trim()).replace(/\n/g, '<br>') + '</p>';
      })
      .join('');
  }

  function workMetaLine(w) {
    var parts = [w.year, w.medium, w.size].filter(Boolean);
    return parts.length ? parts.join(' · ') : '';
  }

  function yearSortKey(year) {
    var m = String(year || '').match(/(\d{4})/g);
    if (!m || !m.length) return -1;
    // Prefer the latest year in ranges like "2025–2026"
    return Math.max.apply(null, m.map(Number));
  }

  function sortByYearDesc(items) {
    return (items || []).slice().sort(function (a, b) {
      return yearSortKey(b.year) - yearSortKey(a.year);
    });
  }

  function renderCvDownload(href, downloadName) {
    if (!href) return '';
    var fname = downloadName || 'CV.pdf';
    return (
      '<a class="artist-cv-download" href="' + esc(href) + '" download="' + esc(fname) + '">' +
        'CV 다운로드 (PDF)' +
      '</a>'
    );
  }

  function renderCvBlock(title, items, mapFn) {
    if (!items || !items.length) return '';
    var sorted = sortByYearDesc(items);
    return (
      '<div class="artist-cv-block">' +
        '<div class="artist-cv-head">' +
          '<h3 class="artist-cv-title">' + esc(title) + '</h3>' +
        '</div>' +
        '<ul class="artist-cv-list">' +
          sorted.map(mapFn).join('') +
        '</ul>' +
      '</div>'
    );
  }

  function initArtistDetail() {
    var container = document.getElementById('artist-container');
    if (!container) return;

    var id = new URLSearchParams(window.location.search).get('id');
    if (!id) {
      window.location.href = 'artists.html';
      return;
    }

    function notFound() {
      container.innerHTML =
        '<div class="article-not-found">' +
          '<div class="container">' +
            '<span class="section-label">404</span>' +
            '<h1>작가를 찾을 수 없습니다</h1>' +
            '<p>요청하신 작가 페이지가 존재하지 않거나 비공개입니다.</p>' +
            '<a href="artists.html" class="btn btn-primary" style="margin-top:32px;display:inline-flex;">Artists 목록으로</a>' +
          '</div>' +
        '</div>';
    }

    loadArtists()
      .then(function (artists) {
        var a = artists.find(function (x) {
          return x.id === id || x.slug === id;
        });
        if (!a || a.published !== true) {
          notFound();
          return;
        }

        var nameEn = displayName(a);
        document.title = nameEn + ' — THEWEAVE 더위브';
        var metaDesc = document.querySelector('meta[name="description"]');
        if (metaDesc) {
          metaDesc.setAttribute('content', a.oneLiner || (nameEn + ' — THEWEAVE Artists'));
        }

        var html = '';

        html +=
          '<section class="artist-hero">' +
            '<div class="container">' +
              '<a href="artists.html" class="artist-back">← Artists</a>' +
              '<h1 class="artist-hero-name">' + esc(nameEn) + '</h1>' +
              (a.name && a.nameEn && a.name !== a.nameEn
                ? '<p class="artist-hero-en">' + esc(a.name) + '</p>'
                : '') +
            '</div>' +
          '</section>';

        var cvFileName = (a.cvPdf || '').split('/').pop() || ((a.name || 'CV') + '_CV.pdf');
        var cvDownload = renderCvDownload(a.cvPdf, cvFileName);

        if (a.bio || cvDownload) {
          html +=
            '<section class="artist-section">' +
              '<div class="container">' +
                (a.bio ? '<div class="artist-bio">' + renderParagraphs(a.bio) + '</div>' : '') +
                (cvDownload
                  ? '<div class="artist-intro-foot">' + cvDownload + '</div>'
                  : '') +
              '</div>' +
            '</section>';
        }

        if (a.works && a.works.length) {
          html +=
            '<section class="artist-section">' +
              '<div class="container">' +
                '<span class="section-label">WORKS</span>' +
                '<div class="artist-works-grid">' +
                  a.works.map(function (w) {
                    var meta = workMetaLine(w);
                    var alt = w.title || a.name;
                    var caption = '';
                    if (w.title || meta) {
                      caption =
                        '<figcaption class="artist-work-caption">' +
                          (w.title ? '<span class="artist-work-title">' + esc(w.title) + '</span>' : '') +
                          (meta ? '<span class="artist-work-meta">' + esc(meta) + '</span>' : '') +
                        '</figcaption>';
                    }
                    return (
                      '<figure class="artist-work">' +
                        '<button type="button" class="artist-work-img" data-lightbox-src="' + esc(w.image || '') + '" data-lightbox-alt="' + esc(alt) + '" aria-label="' + esc(alt) + ' 크게 보기">' +
                          (w.image
                            ? '<img src="' + esc(w.image) + '" alt="' + esc(alt) + '" loading="lazy">'
                            : '') +
                        '</button>' +
                        caption +
                      '</figure>'
                    );
                  }).join('') +
                '</div>' +
              '</div>' +
            '</section>';
        }

        // Temporarily hidden: CV / EXHIBITIONS section
        // var cvHtml = renderCvBlock('CV', a.cv, function (item) {
        //   return (
        //     '<li>' +
        //       '<span class="artist-cv-year">' + esc(item.year || '') + '</span>' +
        //       '<span>' + esc(item.text || '') + '</span>' +
        //     '</li>'
        //   );
        // });
        // var exhHtml = renderCvBlock('Exhibitions', a.exhibitions, function (item) {
        //   var line = [item.title, item.venue].filter(Boolean).join(' — ');
        //   return (
        //     '<li>' +
        //       '<span class="artist-cv-year">' + esc(item.year || '') + '</span>' +
        //       '<span>' + esc(line) + '</span>' +
        //     '</li>'
        //   );
        // });
        // if (cvHtml || exhHtml) {
        //   html +=
        //     '<section class="artist-section">' +
        //       '<div class="container">' +
        //         '<span class="section-label">CV / EXHIBITIONS</span>' +
        //         cvHtml + exhHtml +
        //       '</div>' +
        //     '</section>';
        // }

        if (a.promo && a.promo.length) {
          html +=
            '<section class="artist-section">' +
              '<div class="container">' +
                '<span class="section-label">STUDIO / PRESS</span>' +
                '<div class="artist-promo-grid">' +
                  a.promo.map(function (p) {
                    return (
                      '<figure>' +
                        '<div class="artist-promo-img">' +
                          (p.image
                            ? '<img src="' + esc(p.image) + '" alt="' + esc(p.caption || a.name) + '" loading="lazy">'
                            : '') +
                        '</div>' +
                        (p.caption ? '<figcaption class="artist-promo-caption">' + esc(p.caption) + '</figcaption>' : '') +
                      '</figure>'
                    );
                  }).join('') +
                '</div>' +
              '</div>' +
            '</section>';
        }

        html +=
          '<section class="artist-cta">' +
            '<div class="container">' +
              '<p>이 작가의 작품이 궁금하신가요?</p>' +
              '<a href="contact.html" class="btn btn-primary">문의하기</a>' +
            '</div>' +
          '</section>';

        container.innerHTML = html;
        observeReveal(container);
        bindWorkLightbox(container);
      })
      .catch(function () {
        container.innerHTML =
          '<div class="article-not-found">' +
            '<div class="container">' +
              '<span class="section-label">ERROR</span>' +
              '<h1>콘텐츠를 불러올 수 없습니다</h1>' +
              '<p>잠시 후 다시 시도해 주세요.</p>' +
              '<a href="artists.html" class="btn btn-primary" style="margin-top:32px;display:inline-flex;">Artists 목록으로</a>' +
            '</div>' +
          '</div>';
      });
  }

  window.THEWEAVE_ARTISTS = {
    loadArtists: loadArtists,
    publishedSorted: publishedSorted,
    esc: esc,
    observeReveal: observeReveal,
    initHomeOrList: initHomeOrList
  };

  initHomeOrList();
  initArtistDetail();
})();
