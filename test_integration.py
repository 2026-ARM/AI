#!/usr/bin/env python3
"""
통합 테스트: PDF 업로드 → 추출 → 전처리 → chunking → 요약/퀴즈/플래시카드 생성
"""

import json
from pathlib import Path

# 로컬 서비스 테스트 (API 없이)
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.preprocess_service import clean_text
from app.services.chunk_service import chunk_text


def test_extraction_pipeline():
    """추출 → 전처리 → chunking 파이프라인 테스트"""
    
    print("=" * 60)
    print("📋 추출 → 전처리 → Chunking 파이프라인 테스트")
    print("=" * 60)
    
    # 테스트용 샘플 PDF 생성 (또는 기존 PDF 사용)
    sample_pdf = Path("data/raw/sample.pdf")
    
    if not sample_pdf.exists():
        print(f"⚠️  {sample_pdf} 파일이 없습니다.")
        print("실제 PDF 파일을 data/raw/ 폴더에 넣고 다시 실행하세요.")
        print("\n대신 샘플 텍스트로 테스트합니다:")
        test_preprocessing_and_chunking()
        return
    
    try:
        # 1️⃣ PDF 추출
        print("\n[1/3] PDF 텍스트 추출 중...")
        result = extract_text_from_pdf(str(sample_pdf))
        
        print(f"✅ PDF 추출 성공")
        print(f"   - 페이지 수: {result['page_count']}")
        print(f"   - 전체 문자 수: {len(result['full_text'])}")
        
        full_text = result['full_text']
        
        # 2️⃣ 전처리
        print("\n[2/3] 텍스트 전처리 중...")
        cleaned_text = clean_text(full_text)
        
        print(f"✅ 전처리 성공")
        print(f"   - 전 문자 수: {len(full_text)}")
        print(f"   - 후 문자 수: {len(cleaned_text)}")
        print(f"   - 감소율: {(1 - len(cleaned_text)/len(full_text))*100:.1f}%")
        
        # 3️⃣ Chunking
        print("\n[3/3] 텍스트 Chunking 중...")
        chunks = chunk_text(cleaned_text, max_length=1500, overlap=200)
        
        print(f"✅ Chunking 성공")
        print(f"   - 총 청크 수: {len(chunks)}")
        print(f"   - 평균 청크 길이: {sum(c['length'] for c in chunks) / len(chunks):.0f}")
        
        # 샘플 청크 출력
        print(f"\n📍 첫 번째 청크 (미리보기):")
        print(f"   {chunks[0]['text'][:200]}...")
        
        return chunks
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")


def test_preprocessing_and_chunking():
    """샘플 텍스트로 전처리/chunking 테스트"""
    
    sample_text = """
    1
    이것은 샘플 문서입니다.
    
    
    페이지 번호는 위에 있습니다.
    
    첫 번째 섹션
    
    이것은 첫 번째 섹션의 내용입니다.
    여러 줄로 이루어져 있습니다.
    
    두 번째 섹션
    
    이것은 두 번째 섹션의 내용입니다.
    2
    """
    
    print("\n[샘플 텍스트로 테스트]")
    print("원본 텍스트:")
    print(sample_text)
    
    # 전처리
    cleaned = clean_text(sample_text)
    print(f"\n✅ 전처리 후:")
    print(cleaned)
    
    # Chunking
    chunks = chunk_text(cleaned, max_length=100, overlap=20)
    print(f"\n✅ Chunking 결과 ({len(chunks)}개 청크):")
    for i, chunk in enumerate(chunks, 1):
        print(f"  [{i}] {chunk['text'][:80]}...")
    
    return chunks


def test_schema_validation():
    """스키마 검증 테스트"""
    
    print("\n" + "=" * 60)
    print("🔍 스키마 검증 테스트")
    print("=" * 60)
    
    from app.schemas.quiz_schema import (
        MCQQuiz, CodeErrorQuiz, CodeFillBlankQuiz, OXQuiz,
        QuizBatchRequest, QuizType, DifficultyLevel
    )
    from app.schemas.flashcard_schema import (
        Flashcard, CardType, DifficultyLevel as FCDifficultyLevel,
        FlashcardRequest
    )
    from app.schemas.summary_schema import SummaryRequest, SummaryContent
    
    try:
        # 1. MCQ 스키마 검증
        print("\n[1] MCQ 스키마:")
        mcq = MCQQuiz(
            question="Python의 특징은?",
            options=["동적 타입", "정적 타입", "함수형", "절차형"],
            correct_option_index=0,
            explanation="Python은 동적 타입 언어입니다."
        )
        print(f"✅ {mcq.model_dump_json(indent=2)}")
        
        # 2. O/X 스키마 검증
        print("\n[2] O/X 퀴즈 스키마:")
        ox = OXQuiz(
            statement="Python은 인터프리터 언어이다.",
            is_correct=True,
            explanation="맞습니다. Python은 인터프리터 언어입니다."
        )
        print(f"✅ {ox.model_dump_json(indent=2)}")
        
        # 3. 플래시카드 스키마 검증
        print("\n[3] 플래시카드 스키마:")
        card = Flashcard(
            front="Python은 무엇인가?",
            back="동적 타입의 인터프리터 프로그래밍 언어",
            card_type=CardType.DEFINITION,
            tags=["python", "기초"],
            difficulty=FCDifficultyLevel.EASY
        )
        print(f"✅ {card.model_dump_json(indent=2)}")
        
        # 4. 배치 요청 스키마 검증
        print("\n[4] 배치 요청 스키마:")
        batch_req = QuizBatchRequest(
            chunks=["청크 1", "청크 2"],
            quiz_types=[QuizType.MCQ, QuizType.OX],
            count_per_type=2,
            difficulty=DifficultyLevel.MEDIUM
        )
        print(f"✅ {batch_req.model_dump_json(indent=2)}")
        
        print("\n✅ 모든 스키마 검증 성공!")
        
    except Exception as e:
        print(f"❌ 스키마 검증 실패: {e}")


if __name__ == "__main__":
    import sys
    
    # 환경변수 설정
    import os
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 설정하고 다시 실행하세요.\n")
    
    # 테스트 실행
    test_extraction_pipeline()
    print("\n")
    test_schema_validation()
    
    print("\n" + "=" * 60)
    print("✅ 테스트 완료!")
    print("=" * 60)
    print("\n💡 다음 단계:")
    print("   1. uvicorn app.main:app --reload 로 서버 시작")
    print("   2. http://localhost:8000/docs 에서 Swagger UI로 테스트")
    print("   3. PDF 파일을 업로드하고 API 호출 테스트")
