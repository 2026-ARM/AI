# app/api/routes_quiz.py

from __future__ import annotations

from datetime import datetime
from uuid import uuid4, UUID

from fastapi import APIRouter, HTTPException, status

from app.schemas.quiz_schema import (
    QuizBatchRequest,
    QuizResponse,
    QuizContent,
    QuizType,
    MCQQuiz,
    DifficultyLevel
)
from app.schemas.common_schema import Metadata
from app.services.quiz_service import QuizService

router = APIRouter()


@router.post(
    "/quiz/batch",
    response_model=QuizResponse,
    status_code=status.HTTP_200_OK
)
async def generate_quizzes(
    request: QuizBatchRequest,
    document_id: str = None
) -> QuizResponse:
    """
    청크 목록으로부터 다양한 유형의 퀴즈를 생성합니다.
    
    지원 퀴즈 유형:
    - mcq: 객관식
    - code_error: 코드 오류 찾기
    - code_fill_blank: 코드 빈칸 채우기
    - ox: O/X 퀴즈
    
    Args:
        request: 청크 목록, 퀴즈 유형, 난이도 등
        document_id: 문서 ID (UUID 문자열)
    
    Returns:
        생성된 퀴즈 목록
    """
    try:
        if not document_id:
            document_id = str(uuid4())
        
        quiz_service = QuizService()
        start_time = datetime.utcnow()
        
        # 퀴즈 생성
        quiz_data_list = quiz_service.generate_quizzes(
            chunks=request.chunks,
            quiz_types=request.quiz_types,
            count_per_type=request.count_per_type,
            difficulty=request.difficulty
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # 메타데이터
        metadata = Metadata(
            processing_time=processing_time,
            model_name="gpt-4",
            language="ko",
            chunks_used=len(request.chunks)
        )
        
        # QuizContent 변환
        quizzes = [
            QuizContent(
                quiz_id=uuid4(),
                quiz_data=quiz_data,
                difficulty=request.difficulty or DifficultyLevel.MEDIUM,
                estimated_time=estimate_solving_time(quiz_data)
            )
            for quiz_data in quiz_data_list
        ]
        
        return QuizResponse(
            document_id=UUID(document_id),
            metadata=metadata,
            quizzes=quizzes,
            total_count=len(quizzes)
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


def estimate_solving_time(quiz_data) -> int:
    """
    퀴즈 유형별 예상 풀이 시간 추정 (초)
    """
    quiz_type = quiz_data.quiz_type if hasattr(quiz_data, 'quiz_type') else 'mcq'
    
    time_estimates = {
        QuizType.MCQ: 60,
        QuizType.CODE_ERROR: 120,
        QuizType.CODE_FILL_BLANK: 180,
        QuizType.OX: 30
    }
    
    return time_estimates.get(quiz_type, 60)
