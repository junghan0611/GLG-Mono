#!/usr/bin/env python3
"""
Nerd Fonts 패치 후 한글 bearing 재조정 스크립트

FontPatcher로 Nerd Fonts를 병합한 후, FontForge의 mergeFonts() 부작용으로
한글 글리프의 bbox 기반 중앙 정렬이 손상되어 겹침 현상이 발생합니다.
이 스크립트는 패치된 폰트의 한글 bearing을 재조정하여 문제를 해결합니다.

Usage:
    python fix_nf_korean_bearing.py [--dir build/nerd] [--verbose]

Options:
    --dir DIR       Nerd Fonts 폰트 디렉토리 (기본: build/nerd)
    --verbose       상세 로그 출력
    --help          도움말 표시
"""

import fontforge
import psMat
import sys
import os
from glob import glob
import argparse

from font_widths import restore_advance_widths, snapshot_widths


def fix_korean_bearing(font_path, verbose=False):
    """
    한글 글리프 bearing 재조정

    Args:
        font_path: 폰트 파일 경로
        verbose: 상세 로그 출력 여부

    Returns:
        (fixed_count, skipped_count, error_msg)
    """
    try:
        font = fontforge.open(font_path)
    except Exception as e:
        return (0, 0, f"Failed to open: {e}")

    try:
        # 반각 폭 확인 (숫자 '0' 기준)
        if 0x0030 not in font:
            return (0, 0, "Missing U+0030 (digit 0)")

        half_width = font[0x0030].width
        target_width = half_width * 2

        if verbose:
            print(f"    Half-width: {half_width}, Target full-width: {target_width}")

        fixed_count = 0
        skipped_count = 0

        for glyph in font.glyphs():
            # 한글 음절 (가-힣) + 한글 자모 (ㄱ-ㆎ) 범위만 처리
            if (0xAC00 <= glyph.unicode <= 0xD7A3 or
                0x3131 <= glyph.unicode <= 0x318E):

                # bbox 기반으로 전각 글리프 판단 (실제 글리프 크기가 반각보다 큰 경우)
                bbox = glyph.boundingBox()
                actual_width = bbox[2] - bbox[0]

                # 실제 글리프가 반각보다 크거나, 이미 전각 폭으로 설정된 경우
                if actual_width > half_width * 1.2 or glyph.width >= half_width:
                    # 현재 LSB/RSB 계산
                    current_lsb = bbox[0]
                    current_rsb = glyph.width - bbox[2]

                    # 중앙 정렬을 위한 offset 계산
                    offset = (target_width - actual_width) / 2 - bbox[0]

                    # bearing이 이미 중앙 정렬된 경우 (±2px 허용) skip
                    if abs(current_lsb - current_rsb) <= 2 and abs(glyph.width - target_width) <= 2:
                        skipped_count += 1
                        continue

                    # 변환 적용
                    glyph.transform(psMat.translate(offset, 0))
                    glyph.width = target_width
                    fixed_count += 1

                    if verbose:
                        new_bbox = glyph.boundingBox()
                        new_lsb = new_bbox[0]
                        new_rsb = glyph.width - new_bbox[2]
                        print(f"      U+{glyph.unicode:04X}: LSB {current_lsb:.1f}→{new_lsb:.1f}, RSB {current_rsb:.1f}→{new_rsb:.1f}")

        # 폰트 저장
        # generate() 는 TTF 왕복이므로 FontForge 가 hmtx 를 과압축한다.
        # 0 폭 글리프(결합 부호 등)가 반각 폭을 물려받지 않도록 저장 직후 되돌린다.
        widths = snapshot_widths(font)
        font.generate(font_path)
        font.close()
        restore_advance_widths(font_path, widths, quiet=not verbose)

        return (fixed_count, skipped_count, None)

    except Exception as e:
        font.close()
        return (0, 0, f"Processing error: {e}")


def fix_unicode_range(font_path, unicode_ranges, verbose=False):
    """
    특정 유니코드 범위의 bearing 재조정 (향후 확장용)

    Args:
        font_path: 폰트 파일 경로
        unicode_ranges: [(start, end, name), ...] 리스트
        verbose: 상세 로그 출력 여부

    Returns:
        (fixed_count, skipped_count, error_msg)
    """
    # TODO: 향후 다른 유니코드 범위 처리 추가
    # 예: 수학 기호, 이모지 등
    pass


def main():
    parser = argparse.ArgumentParser(
        description="Nerd Fonts 패치 후 한글 bearing 재조정",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 기본 사용
  python fix_nf_korean_bearing.py

  # 다른 디렉토리 지정
  python fix_nf_korean_bearing.py --dir build/nerd

  # 상세 로그 출력
  python fix_nf_korean_bearing.py --verbose

Note:
  이 스크립트는 FontPatcher로 Nerd Fonts를 병합한 후 실행해야 합니다.
  fontforge_script.py --nerd-font 옵션으로 빌드한 경우에는 불필요합니다.
        """
    )
    parser.add_argument(
        "--dir",
        default="build/nerd",
        help="Nerd Fonts 폰트 디렉토리 (기본: build/nerd)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="상세 로그 출력"
    )

    args = parser.parse_args()
    nf_dir = args.dir

    # 디렉토리 확인
    if not os.path.exists(nf_dir):
        print(f"❌ 오류: {nf_dir} 디렉토리가 없습니다.")
        print(f"   Nerd Fonts 패치를 먼저 실행하세요: task patch:nerd")
        return 1

    # 폰트 파일 찾기
    nf_fonts = glob(f"{nf_dir}/*.ttf")

    if not nf_fonts:
        print(f"❌ 오류: {nf_dir}에 폰트 파일이 없습니다.")
        return 1

    # 헤더 출력
    print("=" * 70)
    print("🔧 Nerd Fonts 한글 Bearing 재조정")
    print("=" * 70)
    print(f"디렉토리: {nf_dir}")
    print(f"대상 폰트: {len(nf_fonts)}개")
    print()

    # 각 폰트 처리
    total_fixed = 0
    total_skipped = 0
    success_count = 0
    error_count = 0

    for font_path in sorted(nf_fonts):
        basename = os.path.basename(font_path)
        print(f"처리 중: {basename}")

        fixed, skipped, error = fix_korean_bearing(font_path, verbose=args.verbose)

        if error:
            print(f"  ✗ 실패: {error}")
            error_count += 1
        else:
            print(f"  ✓ 완료: {fixed}개 수정, {skipped}개 건너뜀")
            total_fixed += fixed
            total_skipped += skipped
            success_count += 1

    # 결과 요약
    print()
    print("=" * 70)
    print("📊 처리 결과")
    print("=" * 70)
    print(f"성공: {success_count}/{len(nf_fonts)} 폰트")
    print(f"실패: {error_count}/{len(nf_fonts)} 폰트")
    print(f"총 수정된 글리프: {total_fixed}개")
    print(f"건너뛴 글리프: {total_skipped}개 (이미 중앙 정렬됨)")
    print()

    if error_count > 0:
        print("⚠️  일부 폰트 처리 실패. 로그를 확인하세요.")
        return 1

    if total_fixed == 0:
        print("ℹ️  수정된 글리프가 없습니다. (이미 bearing이 올바름)")
    else:
        print("✅ 한글 bearing 재조정 완료!")
        print()
        print("다음 단계:")
        print("  1. 검증: python test_korean_bearing_nf.py build/GLG-Mono-Regular.ttf build/nerd/GLG-MonoNF-Regular.ttf")
        print("  2. 또는: task verify:nerd")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
