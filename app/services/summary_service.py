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

    def summarize_chunks(self, chunks: List[str]) -> str:
        """
        청크 목록을 입력받아 GPT를 사용하여 요약을 생성합니다.
        """
        if not chunks:
            return "요약할 내용이 없습니다."

        # 청크들을 하나의 텍스트로 결합
        combined_text = "\n\n".join(chunks)

        # 프롬프트 구성
        prompt = f"""
다음 텍스트를 읽고 주요 내용을 요약해주세요. 요약은 한국어로 작성하며, 핵심 포인트와 중요한 세부 사항을 포함하세요.

텍스트:
{combined_text}

요약:
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # 또는 gpt-4
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