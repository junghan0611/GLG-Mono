# GLG-Mono

[![License: OFL-1.1](https://img.shields.io/badge/License-OFL--1.1-blue.svg)](https://opensource.org/licenses/OFL-1.1)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 힣이 직접 쓰고 고치는 한글 프로그래밍 폰트

터미널과 에디터에서 한글·라틴·코딩 기호를 한 벌로 쓰기 위한 고정폭 폰트입니다. IBM Plex Mono가
라틴과 코딩 기호를, IBM Plex Sans KR이 한글을 맡고, 한자는 IBM Plex Sans JP에서 가져옵니다.

[릴리스](https://github.com/junghan0611/GLG-Mono/releases) · [로드맵](ROADMAP.md) · [설계와 작업 규칙](AGENTS.md) · [다음 작업](NEXT.md)

## 이름

> 폰트는 단순한 도구가 아니다. 존재의 표현이다.

**힣 (U+D7A3)** — 한글 유니코드의 마지막 음절. `[가-힣]`의 끝 경계이자, "에고를 내려놓음".
힣은 나를 버리기 위함이고, 잘 쓰려는 나를 내려놓고 갈겨 쓰기 위한 이름이다. 모두의 힣이다.

**GLG** — 쿼티 자판에서 "힣"을 친 모양. 웃으며 코딩한다는 뜻의 giggling.

## 무엇이고, 무엇이 아닌가

GLG-Mono는 **힣의 작업 환경을 위한 폰트**입니다. 어떤 표준을 대표하지 않고, 정본 한자 목록을
주장하지 않으며, "완전한 CJK 폰트"를 목표로 하지 않습니다. 대신 세 가지를 지킵니다.

1. 지금 어떤 코드포인트를 지원하는지 **정확한 cmap으로 공개**한다
2. 각 글리프가 **어느 소스에서 왔는지** 추적한다
3. **선언하지 않은 문자가 빌드에 섞이지 않게** 한다

지원하지 않는 한자는 결함이 아닙니다. 힣이 쓰지 않는 한자일 뿐입니다. 필요해지면 seed에
코드포인트를 넣고 그것을 그릴 donor를 명시적으로 연결하면 됩니다.

![GLG-Mono terminal sample](assets/glg-mono-terminal.png)

## 지금 배포되는 것 — v1.0.0

현재 릴리스는 **PlemolJP 포크에서 이어받은 v1 산출물**입니다. 위의 계약은 아직 적용되지
않았습니다. 실측값(GLG-Mono-Regular.ttf):

| 항목 | 값 |
|---|---:|
| 전체 글리프 | 35,402 |
| 매핑된 코드포인트 | 27,846 |
| 한글 음절 | 11,172 (전체) |
| 한자 | 13,022 |

v1은 상위 폰트에서 한자와 가나를 **의도 없이 통째로 물려받았고**, 반대로 IBM Plex Sans KR이 가진
한국어 문자 163자를 흘리고 있습니다 — `￦`(U+FFE6), `㈜`(U+321C), 원문자 한글, `㎧`·`㎩` 같은 단위
기호가 여기 포함됩니다. 이걸 고치는 것이 v2입니다.

### 릴리스 자산

| 자산 | 내용 |
|---|---|
| `GLG-Mono_v1.0.0.zip` | 데스크톱 TTF |
| `GLG-MonoNF_v1.0.0.zip` | Nerd Fonts 포함 TTF |
| `GLG-Mono-WebFonts_v1.0.0.zip` | 웹폰트 묶음 |
| `GLG-Mono-{Regular,Bold,Italic,BoldItalic}.woff2` | 개별 WOFF2 (2.6–2.8 MB) |

### 설치

```bash
# Linux
mkdir -p ~/.local/share/fonts/GLG-Mono
unzip GLG-Mono_*.zip -d ~/.local/share/fonts/GLG-Mono
fc-cache -fv

# macOS — TTF 더블클릭, 또는
cp *.ttf ~/Library/Fonts/

# Windows — TTF 선택 → 우클릭 → 설치
```

## 다음 — v2 cmap 계약 (진행 중)

v2는 폰트의 지원 범위를 **정확한 Unicode cmap**으로 공개하고, 코드포인트마다 소유 레이어를
붙이며, 선언되지 않은 문자를 빌드에서 막습니다. 이맥스가 유니코드 범위로 폰트를 고르기 때문에,
지원 범위 자체가 제품 인터페이스입니다.

레이어 소유권 (위가 이김):

```text
custom adjustments
> IBM Plex Mono        — 라틴, 코딩 기호
> IBM Plex Sans KR     — 한글과 KR이 가진 모든 한국어 문자
> IBM Plex Sans JP     — 한자 seed만
> Hack                 — 보충 글리프
> Nerd Fonts           — NF 변형에만
```

한자는 Source Han Sans KR 2.005의 BMP 한자 8,567자를 **seed**로 삼습니다. 표준이 아니라 재현
가능하게 고정한 출발 목록입니다. JP donor가 실제로 그릴 수 있는 7,936자를 폰트가 주장하고, 나머지
631자는 다른 폰트로 fallback됩니다.

게이트는 단순합니다. 빌드마다 네 집합을 뽑고 `missing == 0`, `unexpected == 0`을 요구합니다.

계약과 검증 기준은 [`AGENTS.md`](AGENTS.md)에 둡니다.

## 웹폰트

`task web:build`가 face당 두 조각(`core`/`jp`)으로 WOFF2 8개를 만들고, `task web:verify`가 커버리지·
기하·힌팅·메트릭·셰이핑·라이선스·결정성을 검증합니다.

이 2단 구성은 **검증된 실험 baseline이지 최종 배포 계약이 아닙니다.** 한자 한 글자 때문에 ~2 MB
`jp` face를 통째로 받는 문제가 있어, 웹은 Han/가나를 싣지 않고 브라우저 fallback에 넘기는 4-face
구성으로 재설계 중입니다. 설계와 게이트는 [`AGENTS.md`](AGENTS.md), 다음 구현 순서는
[`NEXT.md`](NEXT.md)에 둡니다.

릴리스의 WOFF2 4종은 현재 v1 전체 face입니다.

## 빌드

NixOS flake가 FontForge·fontTools·ttfautohint·Task를 모두 제공합니다. **모든 빌드는 dev shell
안에서** 실행합니다.

```bash
nix develop

task                 # 전체 태스크 목록
task quick           # 빠른 검증 빌드 (Regular만, ~3분)
task full            # 데스크톱 전체 빌드
task full:nerd       # Nerd Fonts 포함 (1시간 이상)
task web:all         # 웹폰트 빌드 + 검증

task verify          # 한글/한자 글리프 확인
task verify:widths   # combining mark advance 0 회귀 가드 (필수)
task verify:bearing  # NF 패치 후 한글 bearing 확인
```

### 폰트 패밀리

| 패밀리 | 폭 비율 | 용도 |
|---|---|---|
| GLG-Mono | 1:2 (528:1056) | 기본 |
| GLG-MonoConsole | 1:2 | 터미널 정렬 최적화 (권장) |
| GLG-Mono35 | 3:5 (600:1000) | 라틴 문자를 넓게 |
| GLG-Mono35Console | 3:5 | 넓은 라틴 + 콘솔 |

각 패밀리는 8 weight × 2 style = 16벌. `NF` 접미사는 Nerd Fonts 포함, `HS`는 전각 공백 숨김입니다.

## 구성과 출처

글리프 레이어와 그 출처:

| 레이어 | 소스 | 라이선스 |
|---|---|---|
| 라틴 · 코딩 기호 | IBM Plex Mono | OFL 1.1 |
| 한글 | IBM Plex Sans KR | OFL 1.1 |
| 한자 | IBM Plex Sans JP | OFL 1.1 |
| 보충 글리프 | Hack (Source Foundry) | MIT + Bitstream Vera |
| 아이콘 (NF 변형) | Nerd Fonts | MIT |

IBM Plex, Hack, Nerd Fonts, PlemolJP — 네 건의 저작권이 폰트 nameID 0에 그대로 남아 있습니다.
레퍼토리를 다시 짜도 법적 출처는 지워지지 않습니다.

### 계보

```text
IBM Plex (2017, IBM)
  → PlemolJP (2021, yuru7)      — 일본어 프로그래밍 폰트
  → PlemolKR (2024, soomtong)   — 한국어 프로그래밍 폰트
  → GLG-Mono (2025, junghan0611)
```

이 저장소는 PlemolJP의 포크입니다. IBM Plex Sans JP가 들어있고 v1 빌드가 그 위에 구성된 이유가
그것입니다. 빌드 구조 역시 PlemolJP에서 계승했지만, 이 저장소의 빌드 스크립트는 MIT입니다 —
폰트(OFL 1.1)와 코드(MIT)는 다른 층위입니다. 상위 프로젝트는 2025-06 이후 갱신되지 않았고, 우리는
따라가지 않습니다.

## 라이선스

- **폰트 파일**: [SIL Open Font License 1.1](https://opensource.org/licenses/OFL-1.1)
- **빌드 스크립트**: [MIT License](https://opensource.org/licenses/MIT)

## 링크

- 변경 기록: [`CHANGELOG.md`](CHANGELOG.md)
- 디지털 가든: https://notes.junghanacs.com
- IBM Plex: https://github.com/IBM/plex
- PlemolJP: https://github.com/yuru7/PlemolJP
- PlemolKR: https://github.com/soomtong/PlemolKR

---

**"모두의 힣"** — Code with a smile 🙂
