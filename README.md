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
  people/             구성원 사진
  research/           연구 분야 그림
assets/             디자인 파일 (CSS, JS, 글꼴) — 보통 수정 불필요
*.html              페이지 틀 — 보통 수정 불필요
```

---

## 2. GitHub에 처음 올리기 (10분)

1. GitHub에 로그인 → 오른쪽 위 **+** → **New repository**
2. Repository name에 **`내아이디.github.io`** 를 그대로 입력 (예: 아이디가 `jyoh` 이면 `jyoh.github.io`)
   - **Public** 선택 → **Create repository**
3. 새 저장소 화면에서 **uploading an existing file** 클릭
4. 이 압축 파일을 푼 폴더 **안의 내용 전부**(index.html, data, assets, images 등)를 드래그해서 올리고 **Commit changes**
   - `.nojekyll` 파일은 숨김 파일이라 안 보일 수 있습니다. 같이 올라가면 좋지만, 빠져도 사이트는 동작합니다.
5. 저장소 **Settings → Pages** 에서
   - Source: **Deploy from a branch**
   - Branch: **main** / **/(root)** → **Save**
6. 1~2분 뒤 `https://내아이디.github.io` 로 접속해서 확인

> 이미 `내아이디.github.io` 저장소를 개인 홈페이지로 쓰고 있다면, 저장소 이름을 `ncdl` 등으로 만들어도 됩니다.
> 이 경우 학교 도메인을 연결하기 전까지 주소는 `https://내아이디.github.io/ncdl/` 이 되고, 사이트는 그대로 잘 동작합니다.
>
> 나중에 학생에게 관리를 넘기려면, 개인 계정 대신 무료 **Organization**(예: `cau-ncdl`)을 만들고 저장소를 `cau-ncdl.github.io` 로 만드는 방법도 좋습니다. 학생을 멤버로 추가하면 같이 수정할 수 있습니다.

---

## 3. 학교 도메인 연결하기

원리: 학교 DNS에 "`ncdl.cau.ac.kr` 은 `내아이디.github.io` 로 가라"는 **CNAME 레코드**를 하나 등록하면,
학교 주소로 접속했을 때 GitHub에 있는 홈페이지가 학교 주소 그대로 뜹니다.
이 등록은 학교 정보통신 부서만 할 수 있으므로 **요청 메일 한 통**이 필요합니다.

### 3-1. (권장) GitHub에서 도메인 인증 값 받기
도메인 탈취를 막기 위해 GitHub가 권장하는 단계입니다.

1. GitHub 오른쪽 위 프로필 사진 → **Settings**(개인 설정) → 왼쪽 **Pages**
2. **Add a domain** → `ncdl.cau.ac.kr` 입력
3. 화면에 나오는 **TXT 레코드 이름과 값**을 복사해 둡니다
   (이름은 `_github-pages-challenge-내아이디.ncdl.cau.ac.kr` 형태)

### 3-2. 학교에 DNS 등록 요청
먼저 **학과(부) 행정실**에 연구실 홈페이지 도메인 신청 절차를 물어보면 담당 부서를 바로 알려줍니다.
(cau.ac.kr 도메인은 중앙대 정보통신 부서 인프라팀에서 관리합니다.)

요청 메일 예시:

```
제목: [DNS 등록 요청] 연구실 홈페이지 서브도메인 ncdl.cau.ac.kr

안녕하세요. ICT공과대학 융합공학부 오정엽 교수입니다.
연구실 홈페이지를 GitHub Pages로 운영하고자 아래와 같이 DNS 레코드 등록을 요청드립니다.

1. CNAME 레코드
   - 호스트: ncdl.cau.ac.kr
   - 값: 내아이디.github.io.

2. TXT 레코드 (GitHub 도메인 소유 인증용)
   - 호스트: _github-pages-challenge-내아이디.ncdl.cau.ac.kr
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
- **대안 1: 리다이렉트(전달) 요청** — `ncdl.cau.ac.kr` 접속 시 `https://내아이디.github.io` 로 넘겨달라고 요청. 주소창에는 github.io 주소가 보이지만 학교 주소로 들어올 수 있습니다.
- **대안 2: 학과 홈페이지 교수 소개란에 링크** 등록.

---

## 4. 자주 하는 수정

### 논문 추가
`data/publications.yml` 의 `journal:` 바로 아래, **맨 위에** 복사해서 추가합니다.
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
- 교수 이름은 자동으로 굵게 표시됩니다.
- MoS2, Bi2O2Se 같은 화학식 숫자는 자동으로 아래첨자로 바뀝니다.
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

- [ ] **주소**: 기존 사이트에는 `162 Heukseok-ro` 로 되어 있었는데, 중앙대 서울캠퍼스 주소는 `흑석로 84` 입니다. `data/site.yml` 에 84로 넣어 두었으니 맞는지 확인해 주세요.
- [ ] **연구 분야 설명** (`research.yml`): 기존 논문 제목을 바탕으로 쓴 초안입니다.
- [ ] **교수 소개 문단** (`members.yml` 의 `bio`): 기존 학력·경력으로 쓴 초안입니다.
- [ ] **모집 안내의 지원 사항** (`join.yml` 의 `we_offer`): 실제 처우에 맞게 수정해 주세요.
- [ ] **소식 날짜** (`news.yml`): 논문 권호로 추정한 값입니다.
- [ ] **DOI 링크**: `publications.yml` 의 `link:` 에 넣으면 제목이 링크가 됩니다.
- [ ] **사진**: 교수 사진, 연구 그림(`images/research/`, `research.yml` 의 `image:`).
- [ ] **Google Scholar 주소**: `site.yml` 의 `links:` 에 넣으면 People 페이지에 표시됩니다.

---

글꼴: Pretendard, Archivo (SIL Open Font License 1.1) / YAML 파서: js-yaml (MIT)
