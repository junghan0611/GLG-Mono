#!/usr/bin/env python3
"""
한글 글리프 완전 검증: 원본과 비교하여 실제 변환 확인
"""
import fontforge
import sys

def analyze_glyph(font, unicode_val):
    """글리프의 상세 정보 추출"""
    if unicode_val not in font:
        return None

    glyph = font[unicode_val]
    bbox = glyph.boundingBox()

    # bbox가 비어있으면 건너뜀
    if bbox[2] - bbox[0] == 0:
        return None

    return {
        'char': chr(unicode_val),
        'unicode': f"U+{unicode_val:04X}",
        'width': glyph.width,
        'bbox_xmin': bbox[0],
        'bbox_xmax': bbox[2],
        'bbox_width': bbox[2] - bbox[0],
        'lsb': bbox[0],
        'rsb': glyph.width - bbox[2],
    }

def compare_fonts(original_path, built_path, test_chars):
    """원본과 빌드된 폰트 비교"""
    print("=" * 80)
    print("한글 글리프 완전 검증: 원본 vs 빌드")
    print("=" * 80)

    original = fontforge.open(original_path)
    built = fontforge.open(built_path)

    print(f"\n원본 폰트: {original_path}")
    print(f"빌드 폰트: {built_path}\n")

    results = []
    issues = []

    for unicode_val in test_chars:
        orig = analyze_glyph(original, unicode_val)
        new = analyze_glyph(built, unicode_val)

        if not orig or not new:
            continue

        # 변환 검증
        bearing_diff = abs(new['lsb'] - new['rsb'])

        # 예상 변환 계산 (892 → 1000 → 1056)
        # bbox 기반 중앙 정렬이면:
        # offset = (1056 - bbox_width) / 2 - orig_bbox_xmin
        expected_offset = (1056 - orig['bbox_width']) / 2 - orig['bbox_xmin']
        actual_offset = new['bbox_xmin'] - orig['bbox_xmin']
        offset_diff = abs(expected_offset - actual_offset)

        result = {
            'char': orig['char'],
            'unicode': orig['unicode'],
            'orig_width': orig['width'],
            'new_width': new['width'],
            'orig_lsb': orig['lsb'],
            'orig_rsb': orig['rsb'],
            'new_lsb': new['lsb'],
            'new_rsb': new['rsb'],
            'bearing_diff': bearing_diff,
            'bbox_width': orig['bbox_width'],
            'expected_offset': expected_offset,
            'actual_offset': actual_offset,
            'offset_diff': offset_diff,
        }

        results.append(result)

        # 문제 탐지
        problems = []
        if new['width'] != 1056:
            problems.append(f"width={new['width']} (예상: 1056)")
        if bearing_diff > 5:
            problems.append(f"bearing 비대칭 {bearing_diff:.1f}px")
        if offset_diff > 5:
            problems.append(f"offset 불일치 {offset_diff:.1f}px")

        if problems:
            issues.append({
                'char': orig['char'],
                'unicode': orig['unicode'],
                'problems': problems
            })

    original.close()
    built.close()

    # 결과 출력
    print("=" * 80)
    print("변환 결과 상세")
    print("=" * 80)
    print(f"\n{'문자':<4s} {'Unicode':<10s} {'원본W':<8s} {'새W':<8s} "
          f"{'원LSB':<8s} {'원RSB':<8s} {'새LSB':<8s} {'새RSB':<8s} {'차이':<8s}")
    print("-" * 80)

    for r in results:
        print(f"{r['char']:<4s} {r['unicode']:<10s} "
              f"{r['orig_width']:<8.0f} {r['new_width']:<8.0f} "
              f"{r['orig_lsb']:<8.1f} {r['orig_rsb']:<8.1f} "
              f"{r['new_lsb']:<8.1f} {r['new_rsb']:<8.1f} "
              f"{r['bearing_diff']:<8.1f}")

    print("\n" + "=" * 80)
    print("변환 검증")
    print("=" * 80)
    print(f"\n{'문자':<4s} {'Unicode':<10s} {'BBox폭':<8s} "
          f"{'예상이동':<10s} {'실제이동':<10s} {'차이':<8s} {'상태':<6s}")
    print("-" * 80)

    for r in results:
        status = "✓" if r['offset_diff'] < 3 else "✗"
        print(f"{r['char']:<4s} {r['unicode']:<10s} "
              f"{r['bbox_width']:<8.1f} "
              f"{r['expected_offset']:<10.1f} {r['actual_offset']:<10.1f} "
              f"{r['offset_diff']:<8.1f} {status:<6s}")

    # 문제 요약
    if issues:
        print("\n" + "=" * 80)
        print("⚠️  발견된 문제")
        print("=" * 80)
        for issue in issues:
            print(f"\n{issue['char']} {issue['unicode']}:")
            for problem in issue['problems']:
                print(f"  - {problem}")
    else:
        print("\n" + "=" * 80)
        print("✅ 모든 글리프 정상 변환!")
        print("=" * 80)

    # 통계
    perfect_bearing = sum(1 for r in results if r['bearing_diff'] < 1)
    good_bearing = sum(1 for r in results if r['bearing_diff'] < 3)
    perfect_offset = sum(1 for r in results if r['offset_diff'] < 1)
    good_offset = sum(1 for r in results if r['offset_diff'] < 3)
    total = len(results)

    print(f"\n통계:")
    print(f"  Bearing 중앙 정렬: {good_bearing}/{total} 양호 (<3px), {perfect_bearing}/{total} 완벽 (<1px)")
    print(f"  Offset 정확도: {good_offset}/{total} 양호 (<3px), {perfect_offset}/{total} 완벽 (<1px)")
    print(f"  Width 변환: {sum(1 for r in results if r['new_width'] == 1056)}/{total} 성공 (1056)")

    return len(issues) == 0

def main():
    # 테스트할 한글 글리프
    test_chars = [
        0xAC00,  # 가
        0xAC01,  # 각
        0xAC04,  # 간
        0xAC07,  # 갇
        0xAC08,  # 갈
        0xD7A3,  # 힣
        0x3131,  # ㄱ
        0x3134,  # ㄴ
        0x3137,  # ㄷ
    ]

    original_path = 'source/IBM-Plex-Sans-KR/unhinted/IBMPlexSansKR-Regular.ttf'
    built_path = 'build/GLG-MonoConsole-Regular.ttf'

    success = compare_fonts(original_path, built_path, test_chars)

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
