# Artist 메뉴 설계

날짜: 2026-11-16  
상태: 설계 확정 (구현 전)

## 목적

더위브 사이트에 **Artist** 메뉴를 추가한다.  
공개 로스터(컬렉터·방문객)와 매니지먼트 작가 포트폴리오(소개·이력·작품)를 함께 담는다.

## 범위 (1차)

포함:

- Nav **Artist** → 작가 목록 → 작가 상세
- 홈 `#artists` 그리드 (등록 작가 전부, 아래로 확장)
- 상세: 소개, 작품, CV/전시, 스튜디오·홍보 갤러리, 문의 CTA
- `data/artists.json` + 공통 템플릿 (매거진 패턴)
- 웹용 선별 이미지 `images/artists/{slug}/`
- 이후 `admin.html` Artists 탭 (1차는 JSON 직접 편집 가능)

제외:

- 작품 단독 상세 페이지
- 홈의 “함께하는 작가” / “더위브가 매니지먼트하는 작가들” 카피
- 홈의 “전체 보기” 링크
- 빈 슬롯·“새 작가…” 플레이스홀더

## 정보 구조

```
Nav: About · Artist · Services · Magazine · 문의하기

Home (#artists)
  └ 카드(이미지|이름) 클릭 → artist.html?id={slug}

Artist (artists.html)
  └ 카드 클릭 → artist.html?id={slug}

Artist Detail (artist.html)
  └ 문의 CTA → contact.html
```

1차 작가 (소스: `artist/` 폴더):

- 강민성
- 제시카 위
- 진환민
- 허승희

## 시각 방향

**에디토리얼 그리드 (A)** — 대표작 큰 이미지 + 이름. 기존 블랙/화이트 + 오렌지 포인트, Pretendard, 여백 중심.

### Home `#artists`

- 섹션 라벨: `ARTIST` 만 표시
- `published: true` 작가만 렌더
- 그리드: 데스크톱 4열 / 태블릿 2열 / 모바일 1~2열
- 작가 추가 시 다음 칸·다음 줄로 자연 배치 (빈 칸 없음)
- 이미지 또는 이름 클릭 → 상세
- “전체 보기” 없음

### `artists.html`

- 페이지 타이틀: Artist
- 동일 에디토리얼 그리드 (대표작 + 이름 + 한 줄 소개)
- Nav Artist의 랜딩

### `artist.html?id={slug}`

세로 스크롤 섹션:

1. Hero — 이름, 영문, 한 줄 소개, 뒤로(Artist 목록)
2. Intro — 본문
3. Works — 작품 그리드 (제목·연도·매체·크기 메타)
4. CV / Exhibitions — 연도별 목록
5. Studio / Press — 홍보·스튜디오 이미지
6. CTA — 문의하기 → `contact.html`

## 데이터 모델

파일: `data/artists.json`

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
      "works": [
        {
          "title": "",
          "year": "",
          "medium": "",
          "size": "",
          "image": "images/artists/kang-minseong/works/01.jpg"
        }
      ],
      "cv": [{ "year": "", "text": "" }],
      "exhibitions": [{ "year": "", "title": "", "venue": "" }],
      "promo": [{ "image": "", "caption": "" }],
      "order": 1,
      "published": true
    }
  ]
}
```

규칙:

- 목록·홈은 `published === true` 만, `order` 오름차순
- `artist/` 원본은 보관용, 사이트에는 선별본만 `images/artists/` 사용
- 상세는 `magazine-article.html`과 같이 쿼리 `?id=` 로 JSON의 `id`/`slug`를 매칭해 로드

## 구현 파일

| 파일 | 역할 |
|------|------|
| `artists.html` | 목록 |
| `artist.html` | 상세 템플릿 |
| `data/artists.json` | 데이터 |
| `images/artists/{slug}/` | 웹 이미지 |
| `index.html` | Nav + `#artists` 섹션 |
| `about.html`, `services.html`, `contact.html`, `magazine-article.html` 등 | Nav에 Artist 링크 |
| `css/style.css` | Artist 스타일 |
| `js/artists.js` | 홈·목록·상세 렌더 (`main.js`는 nav 등 공통 유지) |
| `admin.html` | (후속) Artists 편집 탭 |

기존 디자인 시스템(컬러 변수, Pretendard, nav/footer)을 그대로 따른다. 카드 스타일은 매거진/서비스와 맞추되, 홈 Artist는 이미지+이름 중심으로 카피를 최소화한다.

## 콘텐츠 파이프라인 (1차)

1. `artist/{작가}/소개/텍스트`에서 소개·이력 정리 → JSON
2. `작품 이미지`에서 대표작·작품 그리드용 선별 → `images/artists/{slug}/`
3. `홍보`에서 스튜디오/프레스 소수 선별 → `promo`
4. `published: true`로 공개

## 후속 (Admin)

매거진 admin과 같은 UX로 Artists 탭:

- 목록 CRUD, 공개/정렬
- 필드 편집 (bio, works, cv, exhibitions, promo)
- 이미지 경로 입력 (업로드는 정적 호스팅 제약에 맞게 경로 지정 방식 우선)

## 성공 기준

- Nav Artist로 목록 진입 가능
- 홈·목록에서 이미지/이름 클릭 시 해당 상세로 이동
- 상세에 소개·작품·이력·홍보·문의가 모두 노출
- 작가 추가 시 JSON(+이미지)만으로 홈/목록에 빈 칸 없이 추가 표시
- 모바일에서도 그리드·상세 가독성 유지
