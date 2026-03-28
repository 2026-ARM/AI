# app/services/preprocess_service.py

from __future__ import annotations

import re


def remove_page_numbers(text: str) -> str:
    """
    줄 전체가 숫자로만 이루어진 경우 페이지 번호로 간주하고 제거합니다.
    예)
    1
    2
    15
    """
    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()

        # 숫자만 있는 줄 제거
        if re.fullmatch(r"\d+", stripped):
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def normalize_special_characters(text: str) -> str:
    """
    PDF 추출 시 자주 포함되는 특수 공백/제어문자를 정리합니다.
    """
    replacements = {
        "\xa0": " ",   # non-breaking space
        "\u200b": "",  # zero-width space
        "\ufeff": "",  # BOM
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def normalize_whitespace(text: str) -> str:
    """
    연속된 공백/탭을 하나의 공백으로 정리합니다.
    단, 줄바꿈은 여기서 건드리지 않습니다.
    """
    lines = text.splitlines()
    normalized_lines = []

    for line in lines:
        # 탭/여러 공백 -> 한 칸
        normalized = re.sub(r"[ \t]+", " ", line).strip()
        normalized_lines.append(normalized)

    return "\n".join(normalized_lines)


def normalize_newlines(text: str) -> str:
    """
    과도한 줄바꿈을 정리합니다.
    3개 이상 연속 줄바꿈은 2개로 줄여 문단 구분만 유지합니다.
    """
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_text(text: str) -> str:
    """
    전체 전처리 파이프라인
    """
    text = normalize_special_characters(text)
    text = remove_page_numbers(text)
    text = normalize_whitespace(text)
    text = normalize_newlines(text)
    return text