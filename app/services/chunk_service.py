# app/services/chunk_service.py

from __future__ import annotations

import re
from typing import Dict, List


class ChunkService:
    def __init__(self, max_length: int = 1500, overlap: int = 1) -> None:
        if max_length <= 0:
            raise ValueError("max_length must be positive")
        if overlap < 0:
            raise ValueError("overlap cannot be negative")

        self.max_length = max_length
        self.overlap = overlap
        self._use_paragraphs = True

    def chunk_text(self, text: str) -> List[Dict]:
        """
        텍스트를 문단/줄 단위로 분할하고 overlap 단위로 청크를 생성합니다.
        """
        if not text:
            return []

        units = self._split_text_into_units(text)
        chunks: List[str] = []
        current_units: List[str] = []

        for unit in units:
            candidate = self._join_units(current_units + [unit])
            if len(candidate) <= self.max_length:
                current_units.append(unit)
                continue

            if current_units:
                chunks.append(self._join_units(current_units))

            if len(unit) > self.max_length:
                chunks.extend(self._split_long_unit(unit))
                current_units = []
            else:
                overlap_units = current_units[-self.overlap :] if self.overlap else []
                current_units = overlap_units + [unit]

        if current_units:
            chunks.append(self._join_units(current_units))

        chunks = self._merge_short_chunks(chunks)
        return [self._format_chunk(i + 1, chunk) for i, chunk in enumerate(chunks)]

    def _merge_short_chunks(self, chunks: List[str], min_length: int = 200) -> List[str]:
        merged: List[str] = []

        for chunk in chunks:
            if merged and len(chunk) < min_length:
                if len(merged[-1]) + len(chunk) + 2 <= self.max_length:
                    merged[-1] = f"{merged[-1]}\n\n{chunk}"
                    continue
            merged.append(chunk)

        return merged

    def _split_text_into_units(self, text: str) -> List[str]:
        paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", text) if paragraph.strip()]
        if len(paragraphs) > 1:
            self._use_paragraphs = True
            return paragraphs

        self._use_paragraphs = False
        return [line.strip() for line in text.splitlines() if line.strip()]

    def _join_units(self, units: List[str]) -> str:
        return "\n\n".join(units) if self._use_paragraphs else "\n".join(units)

    def _split_long_unit(self, unit: str) -> List[str]:
        if self._use_paragraphs:
            lines = [line.strip() for line in unit.splitlines() if line.strip()]
            if len(lines) > 1:
                return self._split_long_text_by_lines(lines)

        if "\n" in unit:
            lines = [line.strip() for line in unit.splitlines() if line.strip()]
            return self._split_long_text_by_lines(lines)

        return [unit[i : i + self.max_length].strip() for i in range(0, len(unit), self.max_length)]

    def _split_long_text_by_lines(self, lines: List[str]) -> List[str]:
        chunks: List[str] = []
        current = ""

        for line in lines:
            part = line + "\n"
            if len(current) + len(part) <= self.max_length:
                current += part
                continue

            if current.strip():
                chunks.append(current.strip())

            if len(part) > self.max_length:
                for i in range(0, len(part), self.max_length):
                    chunks.append(part[i : i + self.max_length].strip())
                current = ""
            else:
                current = part

        if current.strip():
            chunks.append(current.strip())

        return chunks

    def _format_chunk(self, index: int, text: str) -> Dict:
        normalized = text.strip()
        return {
            "chunk_index": index,
            "text": normalized,
            "length": len(normalized),
        }


def chunk_text(text: str, max_length: int = 1500, overlap: int = 1) -> List[Dict]:
    return ChunkService(max_length=max_length, overlap=overlap).chunk_text(text)
