# app/services/summary_service.py

from __future__ import annotations

import importlib
import os
from typing import List

load_dotenv = None
if importlib.util.find_spec("dotenv") is not None:
    dotenv = importlib.import_module("dotenv")
    load_dotenv = getattr(dotenv, "load_dotenv", None)

if load_dotenv is not None:
    load_dotenv()

from openai import OpenAI


class SummaryService:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")

        self.client = OpenAI(api_key=api_key)
        self.model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")

    def summarize_chunks(self, chunks: List[str]) -> str:
        """
        청크 목록을 입력받아 GPT를 사용하여 요약을 생성합니다.
        """
        if not chunks:
            raise ValueError("요약할 텍스트가 없습니다. 빈 청크 목록을 전달하셨습니다.")

        # 빈 문자열과 공백만 있는 청크 제거
        filtered_chunks = [chunk.strip() for chunk in chunks if isinstance(chunk, str) and chunk.strip()]
        if not filtered_chunks:
            raise ValueError("요약할 텍스트가 없습니다. 청크에 유효한 텍스트가 포함되어 있는지 확인하세요.")

        # 청크들을 하나의 텍스트로 결합
        combined_text = "\n\n".join(filtered_chunks)

        # 프롬프트 구성
        prompt = f"""
다음 텍스트를 읽고 주요 내용을 한국어로 요약해주세요.
요약에는 핵심 포인트와 중요한 세부 내용을 포함하고, 가능한 한 간결하고 명확하게 작성하세요.

텍스트:
{combined_text}

요약:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "당신은 전문적인 요약 작성자입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            summary = response.choices[0].message.content.strip()
            return summary
        except Exception as e:
            raise RuntimeError(f"요약 생성 중 오류가 발생했습니다: {e}")