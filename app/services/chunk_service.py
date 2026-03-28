# app/services/chunk_service.py

from __future__ import annotations

from typing import Dict, List


class ChunkService:
    def __init__(self, max_length: int = 1500, overlap: int = 200) -> None:
        if max_length <= 0:
            raise ValueError("max_length must be positive")
        if overlap < 0:
            raise ValueError("overlap cannot be negative")
        self.max_length = max_length
        self.overlap = min(overlap, max_length)
        # Split priority: paragraph -> line -> sentence -> word -> char
        self.separators = ["\n\n", "\n", ". ", " ", ""]

    def chunk_text(self, text: str) -> List[Dict]:
        """
        재귀적으로 텍스트를 분할하고 overlap을 적용해 청크를 생성합니다.
        """
        if not text:
            return []

        raw_chunks = self._recursive_split(text, self.separators)
        final_chunks: List[Dict] = []
        current_text = ""

        for part in raw_chunks:
            if not part:
                continue
            if len(current_text) + len(part) <= self.max_length:
                current_text += part
                continue

            if current_text:
                final_chunks.append(self._format_chunk(len(final_chunks) + 1, current_text))

            overlap_start = current_text[-self.overlap:] if current_text else ""
            current_text = overlap_start + part

            while len(current_text) > self.max_length:
                emit_text = current_text[: self.max_length]
                final_chunks.append(self._format_chunk(len(final_chunks) + 1, emit_text))
                overlap_start = emit_text[-self.overlap:] if self.overlap else ""
                current_text = overlap_start + current_text[self.max_length :]

        if current_text:
            final_chunks.append(self._format_chunk(len(final_chunks) + 1, current_text))

        return final_chunks

    def _recursive_split(self, text: str, separators: List[str]) -> List[str]:
        if len(text) <= self.max_length or not separators:
            return [text]

        sep = separators[0]
        next_separators = separators[1:]

        if sep == "":
            return [text[i : i + self.max_length] for i in range(0, len(text), self.max_length)]

        parts = text.split(sep)
        results: List[str] = []

        for i, part in enumerate(parts):
            content = part + (sep if i < len(parts) - 1 else "")
            if not content:
                continue
            if len(content) <= self.max_length:
                results.append(content)
            else:
                results.extend(self._recursive_split(content, next_separators))

        return results

    def _format_chunk(self, index: int, text: str) -> Dict:
        normalized = text.strip()
        return {
            "chunk_index": index,
            "text": normalized,
            "length": len(normalized),
        }


def chunk_text(text: str, max_length: int = 1500, overlap: int = 200) -> List[Dict]:
    return ChunkService(max_length=max_length, overlap=overlap).chunk_text(text)
