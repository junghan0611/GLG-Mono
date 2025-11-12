#!/bin/env python3

import configparser
import glob
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from fontTools import merge, ttLib, ttx
from ttfautohint import options, ttfautohint

# iniファイルを読み込む
settings = configparser.ConfigParser()
settings.read("build.ini", encoding="utf-8")

FONT_NAME = settings.get("DEFAULT", "FONT_NAME")
try:
    NEW_FONT_NAME = settings.get("DEFAULT", "NEW_FONT_NAME")
except (configparser.NoOptionError, configparser.NoSectionError):
    NEW_FONT_NAME = FONT_NAME
FONTFORGE_PREFIX = settings.get("DEFAULT", "FONTFORGE_PREFIX")
FONTTOOLS_PREFIX = settings.get("DEFAULT", "FONTTOOLS_PREFIX")
BUILD_FONTS_DIR = settings.get("DEFAULT", "BUILD_FONTS_DIR")
HALF_WIDTH_12 = int(settings.get("DEFAULT", "HALF_WIDTH_12"))
FULL_WIDTH_35 = int(settings.get("DEFAULT", "FULL_WIDTH_35"))
WIDTH_35_STR = settings.get("DEFAULT", "WIDTH_35_STR")
CONSOLE_STR = settings.get("DEFAULT", "CONSOLE_STR")


def main():
    # 第一引数を取得
    # 特定のバリエーションのみを処理するための指定
    specific_variant = sys.argv[1] if len(sys.argv) > 1 else None

    edit_fonts(specific_variant)


def edit_fonts(specific_variant: str):
    """フォントを編集する"""

    if specific_variant is None:
        specific_variant = ""

    # ファイルをパターンで指定
    file_pattern = f"{FONTFORGE_PREFIX}{FONT_NAME}{specific_variant}*-eng.ttf"
    filenames = glob.glob(f"{BUILD_FONTS_DIR}/{file_pattern}")
    # ファイルが見つからない場合はエラー
    if len(filenames) == 0:
        print(f"Error: {file_pattern} not found")
        return
    paths = [Path(f) for f in filenames]
    for path in paths:
        print(f"edit {str(path)}")
        style = path.stem.split("-")[1]
        variant = path.stem.split("-")[0].replace(f"{FONTFORGE_PREFIX}{FONT_NAME}", "")
        add_hinting(str(path), str(path).replace(".ttf", "-hinted.ttf"), variant, style)
        merge_fonts(style, variant)
        fix_font_tables(style, variant)

    # 一時ファイルを削除
    # スタイル部分以降はワイルドカードで指定
    for filename in glob.glob(
        f"{BUILD_FONTS_DIR}/{FONTTOOLS_PREFIX}{FONT_NAME}{specific_variant}*"
    ):
        os.remove(filename)
    for filename in glob.glob(
        f"{BUILD_FONTS_DIR}/{FONTFORGE_PREFIX}{FONT_NAME}{specific_variant}*"
    ):
        os.remove(filename)


def add_hinting(input_font_path, output_font_path, variant, style):
    """フォントにヒンティングを付ける"""
    if "Italic" not in style:
        width_variant = "35" if WIDTH_35_STR in variant else "normal"
        ctrl_file = [
            "-m",
            f"hinting_post_process/{width_variant}-{style}-ctrl.txt",
        ]
    else:
        ctrl_file = []

    args = ctrl_file + [
        "-l",
        "6",
        "-r",
        "45",
        "-D",
        "latn",
        "-f",
        "none",
        "-S",
        "-W",
        "-X",
        "13-",
        "-I",
        input_font_path,
        output_font_path,
    ]
    options_ = options.parse_args(args)
    # Remove epoch option for ttfautohint 1.8.3/1.8.4 compatibility
    if hasattr(options_, 'epoch'):
        delattr(options_, 'epoch')
    ttfautohint(**options_)


def merge_fonts(style, variant):
    """フォントを結合する"""
    eng_font_path = f"{BUILD_FONTS_DIR}/{FONTFORGE_PREFIX}{FONT_NAME}{variant}-{style}-eng-hinted.ttf"
    jp_font_path = (
        f"{BUILD_FONTS_DIR}/{FONTFORGE_PREFIX}{FONT_NAME}{variant}-{style}-jp.ttf"
    )
    # vhea, vmtxテーブルを削除
    jp_font_object = ttLib.TTFont(jp_font_path)
    if "vhea" in jp_font_object:
        del jp_font_object["vhea"]
    if "vmtx" in jp_font_object:
        del jp_font_object["vmtx"]
    jp_font_object.save(jp_font_path)
    # フォントを結合
    merger = merge.Merger()
    merged_font = merger.merge([eng_font_path, jp_font_path])
    merged_font.save(
        f"{BUILD_FONTS_DIR}/{FONTTOOLS_PREFIX}{FONT_NAME}{variant}-{style}_merged.ttf"
    )


def fix_font_tables(style, variant):
    """フォントテーブルを編集する"""

    input_font_name = f"{FONTTOOLS_PREFIX}{FONT_NAME}{variant}-{style}_merged.ttf"
    output_name_base = f"{FONTTOOLS_PREFIX}{FONT_NAME}{variant}-{style}"

    # variant에서 "Console" 제거 (GLG-Mono-Regular.ttf 형식)
    # 35는 유지 (GLG-Mono35-Regular.ttf)
    output_variant = variant.replace("Console", "")
    completed_name_base = f"{NEW_FONT_NAME.replace(' ', '')}{output_variant}-{style}"

    # OS/2, post テーブルのみのttxファイルを出力
    xml = dump_ttx(input_font_name, output_name_base)
    # OS/2 テーブルを編集
    fix_os2_table(xml, style, flag_35=WIDTH_35_STR in variant)
    # post テーブルを編集
    fix_post_table(xml, flag_35=WIDTH_35_STR in variant)
    # name テーブルを編集
    fix_name_table(xml, style, variant)

    # ttxファイルを上書き保存
    xml.write(
        f"{BUILD_FONTS_DIR}/{output_name_base}.ttx",
        encoding="utf-8",
        xml_declaration=True,
    )

    # ttxファイルをttfファイルに適用
    ttx.main(
        [
            "-o",
            f"{BUILD_FONTS_DIR}/{output_name_base}_os2_post.ttf",
            "-m",
            f"{BUILD_FONTS_DIR}/{input_font_name}",
            f"{BUILD_FONTS_DIR}/{output_name_base}.ttx",
        ]
    )

    # ファイル名を変更
    os.rename(
        f"{BUILD_FONTS_DIR}/{output_name_base}_os2_post.ttf",
        f"{BUILD_FONTS_DIR}/{completed_name_base}.ttf",
    )


def dump_ttx(input_name_base, output_name_base) -> ET:
    """OS/2, post テーブルのみのttxファイルを出力"""
    ttx.main(
        [
            "-t",
            "OS/2",
            "-t",
            "post",
            "-t",
            "name",
            "-f",
            "-o",
            f"{BUILD_FONTS_DIR}/{output_name_base}.ttx",
            f"{BUILD_FONTS_DIR}/{input_name_base}",
        ]
    )

    return ET.parse(f"{BUILD_FONTS_DIR}/{output_name_base}.ttx")


def fix_os2_table(xml: ET, style: str, flag_35: bool = False):
    """OS/2 テーブルを編集する"""
    # xAvgCharWidthを編集
    # タグ形式: <xAvgCharWidth value="1000"/>
    if flag_35:
        x_avg_char_width = FULL_WIDTH_35
    else:
        x_avg_char_width = HALF_WIDTH_12
    xml.find("OS_2/xAvgCharWidth").set("value", str(x_avg_char_width))

    # fsSelectionを編集
    # タグ形式: <fsSelection value="00000000 11000000" />
    # スタイルに応じたビットを立てる
    fs_selection = None
    if style == "Regular":
        fs_selection = "00000001 01000000"
    elif style == "Italic":
        fs_selection = "00000001 00000001"
    elif style == "Bold":
        fs_selection = "00000001 00100000"
    elif style == "BoldItalic":
        fs_selection = "00000001 00100001"

    if fs_selection is not None:
        xml.find("OS_2/fsSelection").set("value", fs_selection)

    # panoseを編集
    # タグ形式:
    # <panose>
    #   <bFamilyType value="2" />
    #   <bSerifStyle value="11" />
    #   <bWeight value="6" />
    #   <bProportion value="9" />
    #   <bContrast value="6" />
    #   <bStrokeVariation value="3" />
    #   <bArmStyle value="0" />
    #   <bLetterForm value="2" />
    #   <bMidline value="0" />
    #   <bXHeight value="4" />
    # </panose>
    if style == "Regular" or style == "Italic":
        bWeight = 5
    else:
        bWeight = 8
    if flag_35:
        panose = {
            "bFamilyType": 2,
            "bSerifStyle": 11,
            "bWeight": bWeight,
            "bProportion": 3,
            "bContrast": 5,
            "bStrokeVariation": 2,
            "bArmStyle": 3,
            "bLetterForm": 0,
            "bMidline": 2,
            "bXHeight": 3,
        }
    else:
        panose = {
            "bFamilyType": 2,
            "bSerifStyle": 11,
            "bWeight": bWeight,
            "bProportion": 9,
            "bContrast": 5,
            "bStrokeVariation": 2,
            "bArmStyle": 3,
            "bLetterForm": 0,
            "bMidline": 2,
            "bXHeight": 3,
        }

    for key, value in panose.items():
        xml.find(f"OS_2/panose/{key}").set("value", str(value))


def fix_post_table(xml: ET, flag_35):
    """post テーブルを編集する"""
    # isFixedPitchを編集
    # タグ形式: <isFixedPitch value="0"/>
    is_fixed_pitch = 0 if flag_35 else 1
    xml.find("post/isFixedPitch").set("value", str(is_fixed_pitch))


def fix_name_table(xml: ET, style: str, variant: str):
    """name テーブルを編集する
    何故か謎の内容の著作権フィールドが含まれてしまうので、削除する。
    また、フォント名を明示的に設定する。
    """
    parent = xml.find("name")
    
    # 著作権フィールド(nameID=0)에서 FONT_NAME이 포함되지 않은 항목 삭제
    for element in parent.findall("namerecord[@nameID='0']"):
        if FONT_NAME not in element.text:
            parent.remove(element)
    
    # フォント名を生成 (fontforge_script.pyのedit_meta_dataと同じロジック)
    # GLG-Mono (간결한 형식)
    font_family = NEW_FONT_NAME
    if variant != "":
        # Console 제거, 35만 추가 (GLG-Mono, GLG-Mono 35)
        if "35" in variant:
            font_family += " 35"
        # Console variant는 기본이므로 family name에 추가하지 않음
    
    if style == "Regular" or style == "Italic" or style == "Bold" or style == "BoldItalic":
        font_weight = style
        if style == "BoldItalic":
            font_weight = "Bold Italic"
    else:
        font_weight = style
        if "Italic" in style:
            font_weight = font_weight.replace("Italic", " Italic")
    
    font_family_name = font_family
    font_subfamily_name = font_weight
    full_font_name = f"{font_family} {font_weight}"
    postscript_name = f"{font_family}-{font_weight}".replace(" ", "")
    
    # nameID 1: Font Family name
    update_name_records(parent, 1, font_family_name)
    
    # nameID 2: Font Subfamily name
    update_name_records(parent, 2, font_subfamily_name)
    
    # nameID 4: Full font name
    update_name_records(parent, 4, full_font_name)
    
    # nameID 6: PostScript name
    update_name_records(parent, 6, postscript_name)
    
    # nameID 16, 17: Typographic Family/Subfamily name (Regular/Italic/Bold/BoldItalic以外の場合)
    if style != "Regular" and style != "Italic" and style != "Bold" and style != "BoldItalic":
        update_name_records(parent, 16, font_family)
        update_name_records(parent, 17, font_weight)


def update_name_records(parent: ET.Element, name_id: int, text: str):
    """nameテーブルの特定nameIDのレコードを更新または作成する"""
    # 既存のレコード 찾기
    existing_records = parent.findall(f"namerecord[@nameID='{name_id}']")
    
    if existing_records:
        # 既存レコードの値を更新
        for record in existing_records:
            record.text = text
    else:
        # 新しいレコードを作成 (Windows Unicode, English US)
        # platformID=3 (Windows), platEncID=1 (Unicode BMP), langID=0x409 (English US)
        new_record = ET.SubElement(parent, "namerecord")
        new_record.set("nameID", str(name_id))
        new_record.set("platformID", "3")
        new_record.set("platEncID", "1")
        new_record.set("langID", "0x409")
        new_record.text = text


if __name__ == "__main__":
    main()
