# NCDL 연구실 홈페이지

중앙대학교 Neuromorphic Computing & Device Lab 홈페이지입니다.
GitHub Pages로 무료 호스팅하고, 학교 도메인(예: `ncdl.cau.ac.kr`)을 연결해서 씁니다.

**내용 수정은 `data` 폴더의 `.yml` 파일만 고치면 됩니다.** HTML·CSS는 건드릴 필요가 없습니다.
GitHub 웹사이트에서 파일을 열고 연필 아이콘(Edit)으로 고친 뒤 **Commit changes**를 누르면 1~2분 뒤 사이트에 반영됩니다.

---

## 1. 폴더 구조

```
data/               ← 여기만 수정하면 됩니다
  site.yml            연구실 이름, 소개 문구, 연락처, 모집 배너
  members.yml         교수 소개, 학생, 졸업생
  publications.yml    논문(journal), 학회(conference), 특허(patents)
  research.yml        연구 분야 설명
  news.yml            소식
  join.yml            대학원생·인턴 모집 안내
images/
  brand/              NCDL 로고, CAU 심볼
  people/             구성원 사진
  research/           논문 그림 (Selected work)
  research/diagrams/  연구 분야 개념도 (SVG)
assets/             디자인 파일 (CSS, JS, 글꼴) — 보통 수정 불필요
*.html              페이지 틀 — 보통 수정 불필요
scripts/pubbot.py   논문 자동화 봇 (GitHub Actions가 실행)
.github/            논문 추가 양식, 자동화 설정
```

---

## 2. 홈페이지 켜기 (처음 한 번)

이 저장소: `jungyeopoh/NCDL_homepage` (Public)

1. 저장소 **Settings → Pages**
2. Source: **Deploy from a branch**, Branch: **main** / **/(root)** → **Save**
3. 1~2분 뒤 **https://jungyeopoh.github.io/NCDL_homepage/** 에서 확인

> 나중에 학생에게 관리를 넘기려면 무료 **Organization**(예: `cau-ncdl`)을 만들고 저장소를 옮기거나,
> 저장소 **Settings → Collaborators** 에서 학생 GitHub 계정을 추가하면 같이 수정할 수 있습니다.

---

## 3. 학교 도메인 연결하기

원리: 학교 DNS에 "`ncdl.cau.ac.kr` 은 `jungyeopoh.github.io` 로 가라"는 **CNAME 레코드**를 하나 등록하면,
학교 주소로 접속했을 때 GitHub에 있는 홈페이지가 학교 주소 그대로 뜹니다.
이 등록은 학교 정보통신 부서만 할 수 있으므로 **요청 메일 한 통**이 필요합니다.

### 3-1. (권장) GitHub에서 도메인 인증 값 받기
도메인 탈취를 막기 위해 GitHub가 권장하는 단계입니다.

1. GitHub 오른쪽 위 프로필 사진 → **Settings**(개인 설정) → 왼쪽 **Pages**
2. **Add a domain** → `ncdl.cau.ac.kr` 입력
3. 화면에 나오는 **TXT 레코드 이름과 값**을 복사해 둡니다
   (이름은 `_github-pages-challenge-jungyeopoh.ncdl.cau.ac.kr` 형태)

### 3-2. 학교에 DNS 등록 요청
먼저 **학과(부) 행정실**에 연구실 홈페이지 도메인 신청 절차를 물어보면 담당 부서를 바로 알려줍니다.
(cau.ac.kr 도메인은 중앙대 정보통신 부서 인프라팀에서 관리합니다.)

요청 메일 예시:

```
제목: [DNS 등록 요청] 연구실 홈페이지 서브도메인 ncdl.cau.ac.kr

안녕하세요. 창의ICT공과대학 융합공학부 오정엽 교수입니다.
연구실 홈페이지를 GitHub Pages로 운영하고자 아래와 같이 DNS 레코드 등록을 요청드립니다.

1. CNAME 레코드
   - 호스트: ncdl.cau.ac.kr
   - 값: jungyeopoh.github.io.

2. TXT 레코드 (GitHub 도메인 소유 인증용)
   - 호스트: _github-pages-challenge-jungyeopoh.ncdl.cau.ac.kr
   - 값: (GitHub에서 받은 값)

참고: HTTPS 인증서는 GitHub가 Let's Encrypt로 자동 발급합니다.
cau.ac.kr 에 CAA 레코드가 설정되어 있다면 letsencrypt.org 발급 허용이 필요할 수 있습니다.

감사합니다.
오정엽 드림 (내선 5559)
```

### 3-3. 등록 완료 연락을 받으면
1. 저장소 **Settings → Pages → Custom domain** 에 `ncdl.cau.ac.kr` 입력 → **Save**
2. DNS 확인이 끝나면 **Enforce HTTPS** 체크 (인증서 발급에 수십 분~하루 걸릴 수 있음)
3. `https://ncdl.cau.ac.kr` 접속 확인

> ⚠️ Custom domain은 **학교 DNS 등록이 끝난 뒤에** 입력하세요. 먼저 입력하면 `github.io` 주소도 학교 주소로 넘어가서 한동안 사이트가 안 열립니다.

### 학교가 외부 CNAME 등록을 안 해주는 경우
- **대안 1: 리다이렉트(전달) 요청** — `ncdl.cau.ac.kr` 접속 시 `https://jungyeopoh.github.io/NCDL_homepage/` 로 넘겨달라고 요청. 주소창에는 github.io 주소가 보이지만 학교 주소로 들어올 수 있습니다.
- **대안 2: 학과 홈페이지 교수 소개란에 링크** 등록.

---

## 4. 자주 하는 수정

### 논문 추가·상태 변경 — 자동화 (휴대폰으로도 가능)

GitHub 저장소의 **Issues → New issue** 에서 양식을 고르고 제출하면, 1~2분 안에 봇이 홈페이지를 고치고 결과를 댓글로 알려줍니다.
GitHub 앱(휴대폰)에서도 똑같이 됩니다. **저장소 주인 계정으로 올린 것만** 처리됩니다.

| 하고 싶은 것 | 양식 | 넣을 것 |
| --- | --- | --- |
| 게재된 논문 추가 | 📄 논문 추가 | 상태 `Published` + **DOI만** → 제목·저자·저널·권호·링크 자동, 번호 자동, News 자동 |
| 준비 중·투고·심사 중 논문 추가 | 📄 논문 추가 | 상태 + 제목 + 저자 (+ 투고 저널) → Publications 맨 위 **In progress** 에 배지와 함께 표시 |
| 상태 바꾸기 (투고 → 심사 중 → 수정 → 게재) | 🔄 논문 상태 변경 | 제목 일부 + 새 상태. `Published` + DOI 를 넣으면 Journal 목록으로 자동 이동 |

- 상태 종류: `In preparation` → `Submitted` → `Under review` → `Revision` → `Accepted` → `Published`
- 공동 1저자(†)·교신저자(*) 표시, IF 메모는 자동으로 알 수 없으니 필요하면 `data/publications.yml` 에서 다듬어 주세요.
- 잘못 처리되면 봇이 이유를 댓글로 남깁니다. 이슈 본문을 Edit 으로 고친 뒤 댓글 `/retry`.
- ⚠️ 저장소가 공개라 `publications.yml` 은 누구나 볼 수 있습니다. 투고 전 논문 제목은 공개해도 되는 수준으로 적으세요.

### 새 논문 자동 확인 (매주 월요일)

`data/site.yml` 의 `automation.orcid` 에 ORCID iD 를 넣으면, 매주 월요일 오전 OpenAlex 에서 교수님 논문을 검색해
홈페이지에 없는 논문이 있으면 **"새 논문 후보" 이슈**를 만들어 알려줍니다. 이슈에 댓글로:

- `/approve` → 전부 추가 · `/approve 1 3` → 골라서 추가 · `/ignore` → 앞으로 제외

(Actions 탭 → Check new papers → Run workflow 로 바로 돌려볼 수도 있습니다.)

### 직접 고치기

`data/publications.yml` 의 `journal:` 바로 아래, **맨 위에** 복사해서 추가해도 됩니다.
```yaml
journal:
  - no: 26
    year: 2026
    title: "논문 제목"
    authors: "Gildong Hong†, Jungyeop Oh*"
    venue: "Nature Electronics"
    detail: "9, 123 (2026)"
    note: "IF 40.0, JCR top 1%"
    link: "https://doi.org/10.xxxx/xxxxx"
    selected: true      # 홈 화면에 띄우고 싶을 때만
```
- 교수 이름은 자동으로 굵게, MoS2·Bi2O2Se 같은 화학식 숫자는 자동으로 아래첨자로 표시됩니다.
- 학회 발표는 `conference:`, 특허는 `patents:` 에 같은 방식으로. 비어 있으면 탭이 자동으로 숨겨집니다.

### 학생 추가
1. 사진을 `images/people/` 에 올립니다 (Add file → Upload files). 정사각형, 파일명은 영문 (`gildong-hong.jpg`)
2. `data/members.yml` 의 `ms: []` 를 아래처럼 바꿉니다.
```yaml
ms:
  - name: "Gildong Hong"
    name_ko: "홍길동"
    photo: "gildong-hong.jpg"
    email: "gildong@cau.ac.kr"
    since: "2026"
    education: "B.S. Electrical Engineering, Chung-Ang University"
    interests: "Memristor, Reservoir computing"
```
- 박사과정 `phd`, 석박통합 `integrated`, 학부연구생 `interns`, 포닥 `postdocs`, 졸업생 `alumni`.
- 학생이 한 명도 없으면 "첫 구성원을 모집 중" 안내가 대신 표시됩니다.
- **교수 사진**: `images/people/` 에 올리고 `professor:` 의 `photo:` 에 파일명 입력.

### 소식 추가
`data/news.yml` **맨 위에** 추가합니다. 홈 화면에는 최신 5개가 나옵니다.
```yaml
- date: "2026.11.21"
  tag: "Award"
  text: "홍길동 학생이 OOO 학회에서 우수 포스터상을 받았습니다."
```

### 모집 배너 끄기/켜기
`data/site.yml` 에서 `recruiting: false` / `true`

### 디자인 바꾸기 (색상·로고·첫 화면 사진)

`data/site.yml` 의 `design:` 에서:
```yaml
design:
  theme: "paper"       # 본문 바탕: paper (밝은 회녹색) / white (흰 바탕) / navy (메뉴까지 남색)
  logo: "brand/ncdl-logo.png"   # images/ 폴더 기준 로고 파일
  hero_image: ""       # images/ 폴더에 올린 사진 → 홈 첫 화면 배경 (크로스바 어레이 그림 대신)
```
- 홈 첫 화면은 남색 바탕에 멤리스터 크로스바 어레이 그림입니다 (`assets/js/site.js` 의 `heroArray`).
  실험실·웨이퍼 사진을 쓰고 싶으면 `hero_image` 에 파일명을 넣으면 사진으로 바뀝니다.
- 세부 색상은 `assets/css/style.css` 맨 위 `:root` 값으로 바꿀 수 있습니다.

### 메뉴 이름·순서 바꾸기
`assets/js/site.js` 맨 위 `NAV` 목록을 수정합니다.

---

## 5. YAML 작성 규칙 (오류가 나면 여기부터 확인)

- 들여쓰기는 **스페이스 2칸** (탭 키 X)
- `이름:` 뒤에는 **한 칸 띄우기** → `name: "홍길동"`
- 글자에 `:` `#` `"` 가 들어가면 전체를 큰따옴표로 감싸기
- 목록 항목은 `- ` 로 시작
- 형식이 틀리면 사이트에 **몇 번째 줄이 잘못됐는지** 빨간 안내가 뜹니다. 그 줄을 고치면 됩니다.

---

## 6. 내 컴퓨터에서 미리보기 (선택)

HTML 파일을 더블클릭하면 데이터 파일을 못 읽어서 내용이 안 보입니다. 폴더에서 터미널을 열고:
```
python3 -m http.server 8000
```
→ 브라우저에서 `http://localhost:8000`

---

## 7. 올리기 전에 확인할 것

- [ ] **연구 분야 설명** (`research.yml`): 교수님 설명과 논문을 바탕으로 쓴 초안입니다 (왜 / 무엇을 / 전략).
- [ ] **학부연구생 한글 이름** (`members.yml` 의 `name_ko`): 비워 두었습니다.
- [ ] **교수 소개 문단** (`members.yml` 의 `bio`): 기존 학력·경력으로 쓴 초안입니다.
- [ ] **모집 안내의 지원 사항** (`join.yml` 의 `we_offer`): 실제 처우에 맞게 수정해 주세요.
- [ ] **소식 날짜** (`news.yml`): 논문 권호로 추정한 값입니다.
- [ ] **DOI 링크**: `publications.yml` 의 `link:` 에 넣으면 제목이 링크가 됩니다.
- [ ] **학생 사진**: `images/people/` 에 올리고 `photo:` 에 파일명 입력 (없으면 이니셜 표시).
- [ ] **Google Scholar 주소**: `site.yml` 의 `links:` 에 넣으면 People 페이지에 표시됩니다.

---

글꼴: Pretendard, Archivo (SIL Open Font License 1.1) / YAML 파서: js-yaml (MIT)
