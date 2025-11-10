#!/usr/bin/env python3
"""
500 < width < 1000 범위의 글리프들을 확인하는 스크립트
"""
import fontforge

def check_width_range(font_path):
    """폰트 파일에서 500-1000 범위 width 글리프 확인"""
    font = fontforge.open(font_path)

    affected_glyphs = []
    korean_glyphs = []
    japanese_glyphs = []
    other_glyphs = []

    for glyph in font.glyphs():
        if 500 < glyph.width < 1000:
            unicode_val = glyph.unicode
            glyph_info = {
                'name': glyph.glyphname,
                'unicode': f"U+{unicode_val:04X}" if unicode_val > 0 else "N/A",
                'width': glyph.width,
                'char': chr(unicode_val) if unicode_val > 0 else ""
            }

            # 한글 범위: 0xAC00-0xD7A3 (11,172 글자)
            if 0xAC00 <= unicode_val <= 0xD7A3:
                korean_glyphs.append(glyph_info)
            # 일본어 히라가나/카타카나: 0x3040-0x30FF
            elif 0x3040 <= unicode_val <= 0x30FF:
                japanese_glyphs.append(glyph_info)
            # 일본어 한자: 0x4E00-0x9FFF
            elif 0x4E00 <= unicode_val <= 0x9FFF:
                japanese_glyphs.append(glyph_info)
            else:
                other_glyphs.append(glyph_info)

            affected_glyphs.append(glyph_info)

    font.close()

    return {
        'total': len(affected_glyphs),
        'korean': korean_glyphs,
        'japanese': japanese_glyphs,
        'other': other_glyphs
    }

def main():
    # IBM Plex Sans KR 확인
    print("=" * 70)
    print("IBM Plex Sans KR (한글)")
    print("=" * 70)
    kr_result = check_width_range('source/IBM-Plex-Sans-KR/unhinted/IBMPlexSansKR-Regular.ttf')

    print(f"\n총 영향받는 글리프: {kr_result['total']}개")
    print(f"- 한글: {len(kr_result['korean'])}개")
    print(f"- 일본어: {len(kr_result['japanese'])}개")
    print(f"- 기타: {len(kr_result['other'])}개")

    if kr_result['korean']:
        print("\n[한글 샘플 10개]")
        for g in kr_result['korean'][:10]:
            print(f"  {g['char']:2s} {g['unicode']:8s} {g['name']:30s} width={g['width']}")

    if kr_result['other']:
        print("\n[기타 글리프 전체]")
        for g in kr_result['other']:
            print(f"  {g['char']:2s} {g['unicode']:8s} {g['name']:30s} width={g['width']}")

    # IBM Plex Sans JP 확인
    print("\n" + "=" * 70)
    print("IBM Plex Sans JP (일본어)")
    print("=" * 70)
    jp_result = check_width_range('source/IBM-Plex-Sans-JP/unhinted/IBMPlexSansJP-Regular.ttf')

    print(f"\n총 영향받는 글리프: {jp_result['total']}개")
    print(f"- 한글: {len(jp_result['korean'])}개")
    print(f"- 일본어: {len(jp_result['japanese'])}개")
    print(f"- 기타: {len(jp_result['other'])}개")

    if jp_result['other']:
        print("\n[기타 글리프 전체]")
        for g in jp_result['other']:
            print(f"  {g['char']:2s} {g['unicode']:8s} {g['name']:30s} width={g['width']}")

if __name__ == '__main__':
    main()
