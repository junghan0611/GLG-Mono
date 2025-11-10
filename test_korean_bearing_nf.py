#!/usr/bin/env python3
"""
Nerd Fonts 빌드에서 한글 bearing 검증

두 폰트의 한글 글리프 bearing을 비교하여
Nerd Fonts 병합 후에도 bearing이 올바르게 유지되는지 확인
"""

import fontforge
import sys

def check_bearing(font_path, font_label):
    """폰트의 한글 bearing 확인"""
    font = fontforge.open(font_path)
    target_width = font[0x3042].width  # 전각 폭 (히라가나 'あ')

    print(f"\n{'='*60}")
    print(f"{font_label}: {font_path}")
    print(f"{'='*60}")
    print(f"Target width (전각): {target_width}")
    print()

    # 테스트 한글 글리프
    test_glyphs = [
        (0xAC00, '가'),
        (0xAC01, '각'),
        (0xB098, '나'),
        (0xB2E4, '다'),
        (0xB77C, '라'),
        (0xD558, '하'),
        (0xD7A3, '힣'),
    ]

    print(f"{'Char':<6} {'Unicode':<10} {'Width':<8} {'LSB':<8} {'RSB':<8} {'Actual':<8} {'Status':<10}")
    print("-" * 70)

    results = []
    for code, char in test_glyphs:
        if code not in font:
            print(f"{char:<6} U+{code:04X}    <missing>")
            continue

        glyph = font[code]
        bbox = glyph.boundingBox()

        # bbox: (xmin, ymin, xmax, ymax)
        lsb = bbox[0]  # Left Side Bearing
        rsb = glyph.width - bbox[2]  # Right Side Bearing
        actual_width = bbox[2] - bbox[0]  # 실제 글리프 폭

        # bearing 차이 계산 (좌우 균형)
        bearing_diff = abs(lsb - rsb)
        status = "✓ OK" if bearing_diff <= 2 else f"✗ {bearing_diff:.0f}px"

        print(f"{char:<6} U+{code:04X}    {glyph.width:<8.0f} {lsb:<8.1f} {rsb:<8.1f} {actual_width:<8.1f} {status:<10}")

        results.append({
            'char': char,
            'code': code,
            'width': glyph.width,
            'lsb': lsb,
            'rsb': rsb,
            'actual': actual_width,
            'diff': bearing_diff
        })

    font.close()
    return results

def main():
    if len(sys.argv) < 3:
        print("Usage: python test_korean_bearing_nf.py <font1> <font2>")
        print("Example: python test_korean_bearing_nf.py build/GLG-MonoConsole-Regular.ttf build/GLG-MonoConsoleNF-Regular.ttf")
        sys.exit(1)

    font1_path = sys.argv[1]
    font2_path = sys.argv[2]

    print("\n" + "="*70)
    print("Nerd Fonts 빌드 한글 Bearing 검증")
    print("="*70)

    results1 = check_bearing(font1_path, "Non-NF (기본)")
    results2 = check_bearing(font2_path, "NF (Nerd Fonts)")

    print(f"\n{'='*70}")
    print("비교 결과")
    print(f"{'='*70}")

    all_match = True
    for r1, r2 in zip(results1, results2):
        diff_lsb = abs(r1['lsb'] - r2['lsb'])
        diff_rsb = abs(r1['rsb'] - r2['rsb'])
        max_diff = max(diff_lsb, diff_rsb)

        status = "✓ 일치" if max_diff <= 2 else f"✗ 차이 {max_diff:.1f}px"
        if max_diff > 2:
            all_match = False

        print(f"{r1['char']} (U+{r1['code']:04X}): LSB 차이 {diff_lsb:.1f}px, RSB 차이 {diff_rsb:.1f}px - {status}")

    print(f"\n{'='*70}")
    if all_match:
        print("✓ 모든 한글 글리프의 bearing이 일치합니다!")
        print("  Nerd Fonts 병합 후에도 한글 겹침이 발생하지 않습니다.")
    else:
        print("✗ 일부 글리프에서 bearing 차이가 발견되었습니다.")
        print("  fix_korean_bearing_after_merge() 함수를 확인하세요.")
    print(f"{'='*70}\n")

    return 0 if all_match else 1

if __name__ == "__main__":
    sys.exit(main())
