# GLG-Mono

> **힣's Monospace Font for 8-Layer Ecosystem**

GLG-Mono는 지식 관리와 AI 협업을 위한 한글 프로그래밍 폰트입니다. IBM Plex Mono(영문)와 IBM Plex Sans KR(한글)을 결합하여, 터미널과 에디터에서 완벽한 유니코드 지원을 제공합니다.

## 이름의 의미

### 힣 (U+D7A3) - Hangul Syllable Hih
- 한글 유니코드의 마지막 글자
- "나를 버리기 위함" - 에고 없는 글쓰기
- 정규표현식 `[가-힣]`의 끝 경계

### GLG - Giggling Language Glyph
- QWERTY 자판에서 "힣" = "glg"
- 영어 의미: "얼빠지게 웃는다" (giggling)
- 모두의 힣 - 웃는 얼굴로 글쓰기

자세한 철학과 배경은 [`docs/PHILOSOPHY.org`](docs/PHILOSOPHY.org)를 참조하세요.

## 주요 특징

### 1. 유니코드 완전성
- **87% → 100% 커버리지**: 지식 관리에 필요한 모든 기호 지원
- **Denote 파일명 시스템**: 파일명에 메타데이터를 담는 시스템 완벽 지원
  ```
  § ¶ † ‡ № ⓕ ↔ → ⊢ ∉ © ¬ ¢ ¤ µ ¥ £ ¡ ¿
  ```
- **Programming Ligatures**: cashpw 스타일 유니코드 리가처
  ```
  λ ƒ ∘ ∅ ℤ ℝ 𝔹 𝕥 𝕗 ∈ ∉ ∧ ∨ ∀ ∃
  ```
- **수학 및 논리 기호**: 타입 시스템, 함수형 프로그래밍, 논리 연산
- **한글 고어**: ㅹ ㆅ ㅺ ㉼ ㉽
- **CJK 괄호**: 『』 《》 〈〉 ｢｣

### 2. 8-Layer 생태계 통합
GLG-Mono는 다층 지식 관리 시스템의 핵심 도구입니다:

```
Layer 7: Knowledge Publishing  → Digital Garden (notes.junghanacs.com)
Layer 6: Agent Orchestration   → meta-config
Layer 5a: Migration            → memex-kb
Layer 5b: Life Timeline        → memacs-config
Layer 4: AI Memory             → claude-config (PARA + Denote)
Layer 3: Knowledge Management  → Org-mode 1,400+ files + Zotero 156k+ lines
Layer 2: Development           → doomemacs-config
Layer 1: Infrastructure        → nixos-config
```

모든 레이어에서 단일 폰트로 일관된 타이포그래피를 제공합니다.

### 3. TUI 터미널 최적화
- **단일 폰트 완결성**: Emacs와 달리 터미널은 폰트 폴백이 제한적
- **AI 에이전트 협업**: Claude Code 등 터미널 기반 AI 도구 최적화
- **Console 모드**: 화살표 등 기호를 반각으로 표시
- **Nerd Fonts 지원**: Powerline 기호, devicons 등 개발 아이콘

### 4. 기술적 차별화
- **한글 글리프 베어링 수정**: 겹침 없는 정확한 렌더링 (LSB/RSB 0-2px)
- **웹폰트 지원**: WOFF2 포맷으로 Digital Garden 통합
- **전체 세트 기본 제공**: Normal, Console, 35, 35Console 모두 포함
- **8가지 웨이트**: Thin ~ Bold, 각각 Regular/Italic

## 폰트 패밀리

| 폰트 패밀리 | 문자 폭 비율 | 설명 |
|------------|-------------|------|
| **GLG-Mono** | 반각 1:전각 2 | 표준 버전. ASCII는 IBM Plex Mono, 한글/일본어는 IBM Plex Sans 사용 |
| **GLG-Mono Console** | 반각 1:전각 2 | 콘솔 최적화. 화살표 등 기호를 반각으로 표시. 터미널 환경 추천 |
| **GLG-Mono 35** | 반각 3:전각 5 | 영문 확대 버전. 영문이 많은 코드에 적합 |
| **GLG-Mono 35 Console** | 반각 3:전각 5 | 35 + 콘솔 모드 조합 |

### 옵션 변형
- **NF** 접미사: Nerd Fonts 포함 (예: GLG-MonoConsoleNF)
- **HS** 접미사: 전각 공백 가시화 해제 (Hidden Space)

각 패밀리당 16개 파일 (8 웨이트 × 2 스타일) 제공.

## 다운로드 및 설치

### 릴리스에서 다운로드
릴리스 페이지의 Assets에서 원하는 버전을 선택하세요:

- `GLG-Mono_vx.x.x.zip` - 기본 버전
- `GLG-Mono_NF_vx.x.x.zip` - Nerd Fonts 포함
- `GLG-Mono_HS_vx.x.x.zip` - 전각 공백 가시화 해제

### 설치 방법

**Linux:**
```bash
mkdir -p ~/.local/share/fonts/GLG-Mono
unzip GLG-Mono_*.zip -d ~/.local/share/fonts/GLG-Mono
fc-cache -fv
```

**macOS:**
```bash
# 방법 1: Finder에서 더블클릭
# 방법 2: 명령줄
cp *.ttf ~/Library/Fonts/
```

**Windows:**
1. 다운받은 ZIP 압축 해제
2. TTF 파일 선택 → 우클릭 → "설치"

## 빌드 방법

### 요구사항
- Python 3.x
- FontForge (Python 바인딩 포함)
- Python 패키지: `fontTools`, `ttfautohint`
- Task (선택사항, 권장): https://taskfile.dev

### 빌드 시스템

**NixOS 사용자:**
```bash
nix-shell  # 자동으로 모든 의존성 로드
```

**Taskfile 사용 (권장):**
```bash
# 빠른 테스트 빌드 (Regular 웨이트만)
task quick              # 1:2 비율
task quick:35           # 3:5 비율
task quick:nerd         # Nerd Fonts

# 전체 빌드 (모든 웨이트)
task build              # 기본 1:2
task build:console      # 콘솔 모드
task build:nf           # Nerd Fonts
task build:console-nf35 # 콘솔 + 3:5 + Nerd Fonts

# 빌드 + 후처리 (완성 폰트)
task full               # 기본 + 35
task full:all           # 모든 변형
task full:nerd          # Nerd Fonts 변형

# 유틸리티
task check              # 빌드된 폰트 확인
task verify             # 한글/일본어 글리프 존재 확인
task clean              # 빌드 디렉토리 삭제
```

**스크립트 직접 실행:**
```bash
# 1단계: FontForge (폰트 병합)
python fontforge_script.py --debug --console --nerd-font

# 2단계: FontTools (힌팅 및 최종화)
python fonttools_script.py

# 결과 확인
ls -lh build/GLG-Mono*.ttf
```

자세한 빌드 옵션은 `Taskfile.yml` 참조.

## 프로젝트 계보

```
IBM Plex (2017, IBM)
  ├─ IBM Plex Mono (영문 고정폭)
  ├─ IBM Plex Sans JP (일본어)
  └─ IBM Plex Sans KR (한글)
    ↓
PlemolJP (2021, Yuko OTAWARA)
  - 일본어 프로그래밍 폰트
    ↓
PlemolKR (2024, soomtong)
  - 한글 프로그래밍 폰트
    ↓
GLG-Mono (2025, junghan0611)
  - 지식 관리 & AI 협업 폰트
  - 유니코드 완전성
  - 8-Layer 생태계 통합
```

모든 기여자에게 감사드립니다.

## 라이선스

- **폰트 파일**: SIL Open Font License 1.1
- **빌드 스크립트**: MIT License

자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 관련 링크

- **Digital Garden**: https://notes.junghanacs.com (힣's 디지털 가든)
- **프로젝트 철학**: [docs/PHILOSOPHY.org](docs/PHILOSOPHY.org)
- **빌드 가이드**: [docs/BUILD.md](docs/BUILD.md) (예정)
- **PlemolJP**: https://github.com/yuru7/PlemolJP
- **PlemolKR**: https://github.com/soomtong/PlemolKR
- **IBM Plex**: https://github.com/IBM/plex

## 기여

이슈와 풀 리퀘스트는 언제나 환영합니다.

프로젝트 철학과 코딩 가이드는 [`CLAUDE.md`](CLAUDE.md)를 참조하세요.

---

**"모두의 힣"** - 웃는 얼굴로 코딩하세요 🙂
