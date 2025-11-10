#!/usr/bin/env python3
"""
한글 글리프의 bearing 검증 스크립트
"""
import fontforge

def verify_bearing(font_path, glyph_list):
    """특정 글리프들의 bearing 확인"""
    font = fontforge.open(font_path)

    results = []
    for unicode_val in glyph_list:
        if unicode_val in font:
            glyph = font[unicode_val]
            bbox = glyph.boundingBox()
            lsb = bbox[0]
            rsb = glyph.width - bbox[2]
            diff = abs(lsb - rsb)

            results.append({
                'char': chr(unicode_val),
                'unicode': f"U+{unicode_val:04X}",
                'width': glyph.width,
                'lsb': f"{lsb:.2f}",
                'rsb': f"{rsb:.2f}",
                'diff': f"{diff:.2f}",
                'status': '✓' if diff < 3 else '✗'
            })

    font.close()
    return results

def main():
    # 테스트할 한글 글리프
    test_chars = [
        0xAC00,  # 가
        0xAC01,  # 각
        0xAC07,  # 갇
        0xD7A3,  # 힣
        0x3131,  # ㄱ
        0x3134,  # ㄴ
        0x3137,  # ㄷ
    ]

    print("=" * 70)
    print("한글 Bearing 검증: GLG-Mono-Regular.ttf")
    print("=" * 70)

    results = verify_bearing('build/GLG-Mono-Regular.ttf', test_chars)

    print(f"\n{'문자':^4s} {'Unicode':^8s} {'Width':^6s} {'LSB':^8s} {'RSB':^8s} {'차이':^8s} {'상태':^4s}")
    print("-" * 70)

    for r in results:
        print(f"{r['char']:^4s} {r['unicode']:^8s} {r['width']:^6d} "
              f"{r['lsb']:^8s} {r['rsb']:^8s} {r['diff']:^8s} {r['status']:^4s}")

    # 통계
    perfect = sum(1 for r in results if float(r['diff']) == 0)
    good = sum(1 for r in results if float(r['diff']) < 3)
    total = len(results)

    print("\n" + "=" * 70)
    print(f"결과: {good}/{total}개 양호 (차이 < 3px)")
    print(f"      {perfect}/{total}개 완벽 (차이 = 0px)")
    print("=" * 70)

if __name__ == '__main__':
    main()
