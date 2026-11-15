# Artist Menu Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Nav Artist · 홈 그리드 · 목록 · 상세를 `data/artists.json` 기반으로 추가해, 등록 작가(강민성·제시카 위·진환민·허승희)가 이미지/이름 클릭으로 상세까지 이어지게 한다.

**Architecture:** 매거진과 동일하게 정적 JSON + 클라이언트 렌더. `js/artists.js`가 `data/artists.json`을 fetch해 홈(`#artists-grid`)·목록(`#artists-grid`)·상세(`#artist-container`)를 채운다. 웹용 이미지는 `images/artists/{slug}/`에 두고, `artist/` 원본은 소스만 유지한다.

**Tech Stack:** 정적 HTML/CSS/JS, Pretendard, 기존 `css/style.css` 디자인 토큰, `fetch` + URLSearchParams (magazine-article 패턴)

**Spec:** `docs/superpowers/specs/2026-11-16-artist-menu-design.md`

---

## File map

| File | Responsibility |
|------|----------------|
| `data/artists.json` | 작가 데이터 소스 |
| `images/artists/{slug}/` | hero, works/, promo/ 웹 이미지 |
| `js/artists.js` | fetch, filter(`published`), sort(`order`), 홈/목록/상세 렌더 |
| `css/style.css` | `.artists-*`, `.artist-*` 스타일 추가 |
| `index.html` | Nav Artist + `#artists` 섹션 + `artists.js` |
| `artists.html` | 목록 페이지 |
| `artist.html` | 상세 템플릿 (`?id=`) |
| `about.html`, `services.html`, `contact.html`, `magazine-article.html`, `index_t.html`(있으면) | Nav에 Artist 링크 |
| `admin.html` | **이 플랜 범위 밖** (후속) |

---

### Task 1: Nav에 Artist 링크 추가

**Files:**
- Modify: `index.html`, `about.html`, `services.html`, `contact.html`, `magazine-article.html`
- Modify if present: `index_t.html`

- [ ] **Step 1: 각 페이지 nav에 Artist 삽입**

`About` 다음, `Services` 앞에 추가:

```html
<li><a href="artists.html">Artist</a></li>
```

`artists.html`에서는 `class="active"` 부여.  
Footer의 Company 리스트에는 필수는 아님 (스펙 미요구).

- [ ] **Step 2: 로컬에서 HTML 열어 Nav 확인**

Expected: 모든 기존 페이지 상단에 About · Artist · Services · Magazine · 문의하기

- [ ] **Step 3: Commit** (사용자 요청 시에만)

```bash
git add index.html about.html services.html contact.html magazine-article.html
git commit -m "feat(nav): add Artist menu link"
```

---

### Task 2: `data/artists.json` 스키마 + 4명 스캐폴드

**Files:**
- Create: `data/artists.json`

- [ ] **Step 1: JSON 생성**

`id`/`slug` 규칙:

| 이름 | slug |
|------|------|
| 강민성 | `kang-minseong` |
| 제시카 위 | `jessica-wee` |
| 진환민 | `jin-hwanmin` |
| 허승희 | `heo-seunghee` |

초기에는 `oneLiner`/`bio`/`cv`/`exhibitions`/`works`/`promo`를 빈 배열·빈 문자로 두고 `published: true`, `order` 1~4.  
`heroImage` 경로는 Task 3에서 채울 경로를 미리 적어 둔다:

```json
{
  "artists": [
    {
      "id": "kang-minseong",
      "slug": "kang-minseong",
      "name": "강민성",
      "nameEn": "Kang MinSeong",
      "oneLiner": "",
      "bio": "",
      "heroImage": "images/artists/kang-minseong/hero.jpg",
      "works": [],
      "cv": [],
      "exhibitions": [],
      "promo": [],
      "order": 1,
      "published": true
    },
    {
      "id": "jessica-wee",
      "slug": "jessica-wee",
      "name": "제시카 위",
      "nameEn": "Jessica Wee",
      "oneLiner": "",
      "bio": "",
      "heroImage": "images/artists/jessica-wee/hero.jpg",
      "works": [],
      "cv": [],
      "exhibitions": [],
      "promo": [],
      "order": 2,
      "published": true
    },
    {
      "id": "jin-hwanmin",
      "slug": "jin-hwanmin",
      "name": "진환민",
      "nameEn": "Jin Hwanmin",
      "oneLiner": "",
      "bio": "",
      "heroImage": "images/artists/jin-hwanmin/hero.jpg",
      "works": [],
      "cv": [],
      "exhibitions": [],
      "promo": [],
      "order": 3,
      "published": true
    },
    {
      "id": "heo-seunghee",
      "slug": "heo-seunghee",
      "name": "허승희",
      "nameEn": "Heo Seunghee",
      "oneLiner": "",
      "bio": "",
      "heroImage": "images/artists/heo-seunghee/hero.jpg",
      "works": [],
      "cv": [],
      "exhibitions": [],
      "promo": [],
      "order": 4,
      "published": true
    }
  ]
}
```

- [ ] **Step 2: JSON 유효성 확인**

```bash
node -e "const d=require('./data/artists.json'); if(!Array.isArray(d.artists)||d.artists.length!==4) process.exit(1); console.log('ok', d.artists.map(a=>a.slug).join(','))"
```

Expected: `ok kang-minseong,jessica-wee,jin-hwanmin,heo-seunghee`

- [ ] **Step 3: Commit** (사용자 요청 시에만)

```bash
git add data/artists.json
git commit -m "feat(artists): add artists.json scaffold for four artists"
```

---

### Task 3: 웹용 이미지 선별·복사

**Files:**
- Create dirs: `images/artists/{slug}/`, `works/`, `promo/`
- Copy from `artist/` (원본은 이동하지 않음)

- [ ] **Step 1: 작가별 디렉터리 생성**

```bash
mkdir -p images/artists/kang-minseong/works images/artists/kang-minseong/promo
mkdir -p images/artists/jessica-wee/works images/artists/jessica-wee/promo
mkdir -p images/artists/jin-hwanmin/works images/artists/jin-hwanmin/promo
mkdir -p images/artists/heo-seunghee/works images/artists/heo-seunghee/promo
```

(Windows PowerShell이면 `New-Item -ItemType Directory -Force` 사용)

- [ ] **Step 2: 작가당 hero 1 + works 3~6 + promo 2~4 선별 복사**

기준:

- hero = 목록/홈 대표작 (가장 선명한 작품 컷)
- works = `작품 이미지` (미정 폴더는 제외 가능)
- promo = 스튜디오/설치/프레스 (과다한 진환민 홍보 폴더는 소수만)

파일명은 ASCII로 정규화: `hero.jpg`, `works/01.jpg` …, `promo/01.jpg` …

대용량 `.TIF` / `.mp4` / PDF는 웹용으로 넣지 않는다. JPG/PNG/JPEG/WEBP만.

- [ ] **Step 3: `data/artists.json`의 `heroImage` / `works[].image` / `promo[].image` 경로를 실제 파일에 맞춤**

작품 메타(`title`,`year`,`medium`,`size`)는 파일명에 있으면 파싱해 넣고, 없으면 제목만 파일 stem으로 임시 기입 후 소개글 작업(Task 7)에서 보강.

- [ ] **Step 4: 경로 존재 확인**

```bash
node -e "const fs=require('fs');const d=require('./data/artists.json');let bad=[];for(const a of d.artists){[a.heroImage,...a.works.map(w=>w.image),...a.promo.map(p=>p.image)].filter(Boolean).forEach(p=>{if(!fs.existsSync(p)) bad.push(p)});} if(bad.length){console.error(bad.join('\n'));process.exit(1);} console.log('all images exist');"
```

Expected: `all images exist`

- [ ] **Step 5: Commit** (사용자 요청 시에만)

```bash
git add images/artists data/artists.json
git commit -m "feat(artists): add web-optimized artist images"
```

---

### Task 4: Artist CSS

**Files:**
- Modify: `css/style.css` (파일 끝 magazine/article 스타일 근처에 추가)

- [ ] **Step 1: 홈/목록/상세 스타일 추가**

기존 토큰만 사용 (`--tw-black`, `--tw-white`, `--tw-orange`, `--tw-gray-*`).  
카드 박스 섀도/라운드 과다 금지 — 매거진 카드와 비슷한 미니멀 톤.

필수 클래스:

```css
/* Home / list grid */
.artists-section { /* padding, bg */ }
.artists-section--home { /* home: dark or light — match adjacent sections; prefer light gray-50 or white after hero */ }
.artists-section .section-label { margin-bottom: 28px; }
.artists-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 28px 20px;
}
.artist-card-link { display: block; text-decoration: none; color: inherit; }
.artist-card-img { overflow: hidden; aspect-ratio: 1 / 1; background: var(--tw-gray-100); }
.artist-card-img img { width: 100%; height: 100%; object-fit: cover; transition: transform .4s ease; }
.artist-card-link:hover .artist-card-img img { transform: scale(1.03); }
.artist-card-name { margin-top: 12px; font-size: 16px; font-weight: 600; letter-spacing: -0.01em; }
.artist-card-oneliner { margin-top: 4px; font-size: 13px; color: var(--tw-gray-500); }

/* List page header */
.artists-page-header { padding: 120px 0 48px; }
.artists-page-header h1 { font-size: clamp(36px, 5vw, 56px); }

/* Detail */
.artist-hero { padding: 120px 0 48px; background: var(--tw-black); color: var(--tw-white); }
.artist-hero .artist-back { color: var(--tw-orange); }
.artist-hero-name { font-size: clamp(36px, 5vw, 56px); font-weight: 700; }
.artist-hero-en { color: rgba(255,255,255,.55); margin-top: 8px; }
.artist-hero-oneliner { margin-top: 16px; max-width: 36em; color: rgba(255,255,255,.8); }
.artist-section { padding: 72px 0; border-bottom: 1px solid var(--tw-gray-100); }
.artist-section .section-label { margin-bottom: 20px; }
.artist-bio { font-size: 16px; line-height: 1.8; color: var(--tw-gray-700); max-width: 40em; }
.artist-works-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.artist-work-meta { margin-top: 8px; font-size: 13px; color: var(--tw-gray-500); }
.artist-cv-list { list-style: none; padding: 0; }
.artist-cv-list li { display: grid; grid-template-columns: 72px 1fr; gap: 16px; padding: 10px 0; border-bottom: 1px solid var(--tw-gray-100); font-size: 15px; }
.artist-promo-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.artist-cta { padding: 88px 0; background: var(--tw-black); color: var(--tw-white); text-align: center; }

@media (max-width: 900px) {
  .artists-grid { grid-template-columns: repeat(2, 1fr); }
  .artist-works-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 560px) {
  .artists-grid { grid-template-columns: 1fr 1fr; gap: 20px 12px; }
  .artist-works-grid, .artist-promo-grid { grid-template-columns: 1fr; }
}
```

빈 섹션(배열 length 0)은 JS에서 DOM을 아예 안 넣으므로 “빈 칸” CSS는 불필요.

- [ ] **Step 2: Commit** (사용자 요청 시에만)

```bash
git add css/style.css
git commit -m "style(artists): add artist grid and detail styles"
```

---

### Task 5: `js/artists.js` 공통 로더 + 홈/목록 렌더

**Files:**
- Create: `js/artists.js`

- [ ] **Step 1: 스크립트 작성**

```javascript
/* THEWEAVE — artists.js */
(function () {
  function esc(s) {
    return String(s || '')
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function publishedSorted(artists) {
    return (artists || [])
      .filter(function (a) { return a && a.published === true; })
      .sort(function (a, b) { return (a.order || 0) - (b.order || 0); });
  }

  function cardHtml(a, withOneLiner) {
    var href = 'artist.html?id=' + encodeURIComponent(a.id || a.slug);
    var img = a.heroImage
      ? '<img src="' + esc(a.heroImage) + '" alt="' + esc(a.name) + '" loading="lazy">'
      : '';
    var one = (withOneLiner && a.oneLiner)
      ? '<p class="artist-card-oneliner">' + esc(a.oneLiner) + '</p>'
      : '';
    return (
      '<a class="artist-card-link reveal" href="' + href + '">' +
        '<div class="artist-card-img">' + img + '</div>' +
        '<h3 class="artist-card-name">' + esc(a.name) + '</h3>' +
        one +
      '</a>'
    );
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

  function renderGrid(grid, artists, withOneLiner) {
    var list = publishedSorted(artists);
    if (!list.length) {
      grid.innerHTML = '';
      return;
    }
    grid.innerHTML = list.map(function (a) { return cardHtml(a, withOneLiner); }).join('');
    observeReveal(grid);
  }

  function loadArtists() {
    return fetch('./data/artists.json')
      .then(function (res) {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return res.json();
      })
      .then(function (data) { return data.artists || []; });
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

  // Detail renderer attached in Task 6 — stub hook:
  window.THEWEAVE_ARTISTS = {
    loadArtists: loadArtists,
    publishedSorted: publishedSorted,
    esc: esc,
    observeReveal: observeReveal,
    initHomeOrList: initHomeOrList
  };

  initHomeOrList();
})();
```

- [ ] **Step 2: Commit** (사용자 요청 시에만)

```bash
git add js/artists.js
git commit -m "feat(artists): add artists.js grid renderer"
```

---

### Task 6: 홈 `#artists` + `artists.html` 목록 페이지

**Files:**
- Modify: `index.html`
- Create: `artists.html`

- [ ] **Step 1: `index.html` — Hero 다음, Magazine 앞에 섹션 삽입**

```html
<section class="artists-section artists-section--home" id="artists">
  <div class="container">
    <span class="section-label reveal">ARTIST</span>
    <div class="artists-grid" id="artists-grid"></div>
  </div>
</section>
```

`</body>` 직전 `main.js` 뒤에:

```html
<script src="js/artists.js"></script>
```

홈에는 한 줄 소개 없음 → `data-with-oneliner` 생략.

카피 금지: “함께하는 작가”, “더위브가 매니지먼트…”, “전체 보기”.

- [ ] **Step 2: `artists.html` 생성**

구조는 `about.html`과 동일한 nav/footer 뼈대. `body`에 `hero-page` 없음. Nav Artist에 `active`.

```html
<main>
  <header class="artists-page-header">
    <div class="container">
      <h1 class="reveal">Artist</h1>
    </div>
  </header>
  <section class="artists-section">
    <div class="container">
      <div class="artists-grid" id="artists-grid" data-with-oneliner="true"></div>
    </div>
  </section>
</main>
<script src="js/main.js"></script>
<script src="js/artists.js"></script>
```

- [ ] **Step 3: 로컬 서버로 확인**

```bash
npx --yes serve -l 5173
```

브라우저: `http://localhost:5173/` 와 `/artists.html`

Expected:

- 홈·목록에 작가 4명 (빈 슬롯 없음)
- 이미지/이름 클릭 시 `artist.html?id=...` 로 이동 (상세는 아직 비어 있어도 URL은 맞음)
- Nav Artist → 목록

- [ ] **Step 4: Commit** (사용자 요청 시에만)

```bash
git add index.html artists.html
git commit -m "feat(artists): add home grid and artists list page"
```

---

### Task 7: `artist.html` 상세 렌더

**Files:**
- Create: `artist.html`
- Modify: `js/artists.js` (detail init 추가)

- [ ] **Step 1: `artist.html` 뼈대**

```html
<main>
  <div id="artist-container">
    <div class="article-loading"><p>불러오는 중…</p></div>
  </div>
</main>
<script src="js/main.js"></script>
<script src="js/artists.js"></script>
```

Nav/footer는 다른 페이지와 동일. Artist 링크 `active` 가능.

- [ ] **Step 2: `js/artists.js`에 `initArtistDetail` 추가**

동작:

1. `#artist-container` 없으면 return
2. `URLSearchParams`의 `id` 없으면 `artists.html`로 이동
3. `loadArtists()` 후 `id` 또는 `slug` 매칭, `published !== true`면 not found
4. 섹션 렌더 순서: Hero → Intro(bio 있을 때만) → Works → CV/Exhibitions → Promo → CTA
5. 빈 배열 섹션은 출력하지 않음
6. `document.title = name + ' — THEWEAVE 더위브'`
7. CTA: `contact.html`
8. 뒤로: `artists.html`

핵심 렌더 스케치:

```javascript
function initArtistDetail() {
  var container = document.getElementById('artist-container');
  if (!container) return;
  var id = new URLSearchParams(window.location.search).get('id');
  if (!id) { window.location.href = 'artists.html'; return; }

  loadArtists().then(function (artists) {
    var a = artists.find(function (x) {
      return x.id === id || x.slug === id;
    });
    if (!a || a.published !== true) {
      container.innerHTML = '<!-- not found markup linking back to artists.html -->';
      return;
    }
    // build hero + optional sections + CTA using esc()
    container.innerHTML = html;
    observeReveal(container);
  }).catch(function () { /* error markup */ });
}

initArtistDetail();
```

`bio`는 `\n\n` 단락 분리 (magazine-article과 동일).

CV와 exhibitions는 같은 섹션 안에서 소제목으로 나눠도 되고, 두 블록을 연달아 렌더해도 된다. 둘 다 비면 섹션 전체 생략.

- [ ] **Step 3: 브라우저 확인**

- `artist.html?id=kang-minseong` → 이름·영문 표시
- 잘못된 id → not found + 목록 링크
- 문의하기 → contact
- ← Artist → artists.html

- [ ] **Step 4: Commit** (사용자 요청 시에만)

```bash
git add artist.html js/artists.js
git commit -m "feat(artists): add artist detail page renderer"
```

---

### Task 8: 소개·이력 텍스트 채우기

**Files:**
- Modify: `data/artists.json`
- Source (읽기 전용): `artist/*/소개/텍스트/*.docx` 및 소개 PDF

- [ ] **Step 1: 작가별 docx에서 소개 추출**

가능하면 Word/텍스트 추출 도구로 `oneLiner`(1문장) + `bio`(본문) + `cv`/`exhibitions` 채움.  
추출이 어려우면 소개 문서 요약을 수동으로 JSON에 기입.

- [ ] **Step 2: works/promo 메타 정리**

각 work에 `title`, `year`, `medium`, `size`가 비어 있지 않은지 확인 (모를 때만 빈 문자열 허용).

- [ ] **Step 3: JSON 재검증**

```bash
node -e "const d=require('./data/artists.json'); d.artists.forEach(a=>{if(!a.name||!a.heroImage) throw new Error(a.slug);}); console.log('content ok');"
```

- [ ] **Step 4: Commit** (사용자 요청 시에만)

```bash
git add data/artists.json
git commit -m "content(artists): fill bios, CV, and work metadata"
```

---

### Task 9: 통합 QA

**Files:** 없음 (검증만)

- [ ] **Step 1: 체크리스트**

- [ ] Nav 전 페이지에 Artist 있음, 클릭 시 `artists.html`
- [ ] 홈 `#artists`: ARTIST 라벨만, 여분 카피/전체보기/빈칸 없음
- [ ] 홈·목록 카드 클릭 → 올바른 상세
- [ ] 상세: Intro/Works/CV/Promo/CTA (데이터 있는 섹션만)
- [ ] `published: false`로 임시 바꾸면 홈·목록에서 사라짐 (검증 후 되돌림)
- [ ] 모바일 폭(~375px)에서 그리드 2열, 상세 가독성
- [ ] 콘솔 에러·깨진 이미지 없음

- [ ] **Step 2: 스펙 대조**

`docs/superpowers/specs/2026-11-16-artist-menu-design.md` 성공 기준 전부 충족 확인.

---

## Out of scope (후속)

- `admin.html` Artists 탭 CRUD
- 작품 단독 상세 URL
- `artist/` 원본 전체 업로드/최적화 파이프라인 자동화

---

## Self-review (plan vs spec)

| Spec 요구 | Task |
|-----------|------|
| Nav Artist | Task 1 |
| Home ARTIST + 그리드, 카피/전체보기/빈칸 없음 | Task 6 |
| 목록 artists.html | Task 6 |
| 상세 섹션 전체 | Task 7 |
| JSON + images/artists | Task 2–3 |
| 클릭 → 상세 | Task 5–7 |
| 4명 콘텐츠 | Task 3, 8 |
| Admin | Out of scope (명시) |
