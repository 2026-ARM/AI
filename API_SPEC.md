# API 응답 구조 정의 (FEAT #5)

## 📋 개요

AI 결과를 백엔드에서 쉽게 사용할 수 있는 JSON 구조로 반환합니다.
모든 응답은 **BaseResponse** 구조를 상속하며, `document_id`, `metadata`, `created_at`을 포함합니다.

---

## 🏗️ 공통 응답 구조

### BaseResponse (모든 AI 응답의 기본)

```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-03-28T12:00:00Z",
  "metadata": {
    "processing_time": 2.5,
    "model_name": "gpt-4",
    "language": "ko",
    "chunks_used": 10
  },
  "extra": {}
}
```

### Metadata 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `processing_time` | float | 처리 시간 (초) |
| `model_name` | string | 사용된 AI 모델명 (기본: gpt-4) |
| `language` | string | 문서 언어 (기본: ko) |
| `chunks_used` | int | 처리에 사용된 청크 수 |

---

## 📝 1. SummaryResponse (요약)

**엔드포인트**: `POST /ai/summary/summarize`

### Request

```json
{
  "chunks": ["청크 텍스트 1", "청크 텍스트 2", ...]
}
```

### Response

```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-03-28T12:00:00Z",
  "metadata": {
    "processing_time": 2.5,
    "model_name": "gpt-4",
    "language": "ko",
    "chunks_used": 10
  },
  "summary": {
    "text": "이 문서의 핵심 내용은...",
    "key_points": [
      "포인트 1",
      "포인트 2",
      "포인트 3"
    ],
    "original_length": 5000,
    "summary_length": 500,
    "compression_ratio": 90.0
  },
  "extra": {}
}
```

### Summary 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `text` | string | 요약 텍스트 |
| `key_points` | string[] | 주요 포인트 (최대 5개) |
| `original_length` | int | 원본 문자 수 |
| `summary_length` | int | 요약 문자 수 |
| `compression_ratio` | float | 압축률 (%) |

---

## 🎯 2. QuizResponse (퀴즈)

**엔드포인트**: `POST /ai/quiz/batch`

### Request

```json
{
  "chunks": ["청크 텍스트 1", "청크 텍스트 2"],
  "quiz_types": ["mcq", "code_error", "code_fill_blank", "ox"],
  "count_per_type": 3,
  "difficulty": null
}
```

### Response

```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-03-28T12:00:00Z",
  "metadata": {
    "processing_time": 3.2,
    "model_name": "gpt-4",
    "language": "ko",
    "chunks_used": 15
  },
  "quizzes": [
    {
      "quiz_id": "550e8400-e29b-41d4-a716-446655440001",
      "quiz_data": {
        "quiz_type": "mcq",
        "question": "다음 중 정답은?",
        "options": ["옵션 1", "옵션 2", "옵션 3"],
        "correct_option_index": 1,
        "explanation": "정답은..."
      },
      "difficulty": "medium",
      "estimated_time": 60
    }
  ],
  "total_count": 1,
  "extra": {}
}
```

### 퀴즈 유형별 구조

#### 2.1 MCQ (객관식)

```json
{
  "quiz_type": "mcq",
  "question": "다음 중 정답은?",
  "options": ["선택지1", "선택지2", "선택지3"],
  "correct_option_index": 1,
  "explanation": "정답 설명"
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `question` | string | 질문 |
| `options` | string[] | 선택지 (2-5개) |
| `correct_option_index` | int | 정답 선택지 인덱스 (0부터) |
| `explanation` | string | 해설 (선택사항) |

#### 2.2 Code Error (코드 오류 찾기)

```json
{
  "quiz_type": "code_error",
  "question": "다음 코드의 오류를 찾으세요",
  "code": "def hello()\n  print('hello')",
  "error_description": "함수 정의 시 콜론(:)이 누락됨",
  "error_line_number": 1,
  "hint": "Python 함수는 def 다음에 콜론을 붙여야 합니다",
  "explanation": "Python 함수 정의 문법 설명"
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `question` | string | 문제 설명 |
| `code` | string | 오류가 있는 코드 |
| `error_description` | string | 오류 설명 |
| `error_line_number` | int | 오류 줄 번호 (선택사항) |
| `hint` | string | 힌트 (선택사항) |
| `explanation` | string | 해설 (선택사항) |

#### 2.3 Code Fill Blank (코드 빈칸 채우기)

```json
{
  "quiz_type": "code_fill_blank",
  "question": "빈칸을 채워 올바른 코드를 완성하세요",
  "code_with_blanks": "def add(a, b):\n  return ___",
  "solutions": ["a + b"],
  "difficulty": "easy",
  "language": "python",
  "hint": "두 수를 더하는 연산자를 사용하세요",
  "explanation": "Python에서 덧셈은 + 연산자를 사용합니다"
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `question` | string | 문제 설명 |
| `code_with_blanks` | string | 빈칸이 있는 코드 (`___`로 표시) |
| `solutions` | string[] | 정답 (복수 가능) |
| `difficulty` | string | 난이도 (easy/medium/hard) |
| `language` | string | 프로그래밍 언어 |
| `hint` | string | 힌트 (선택사항) |
| `explanation` | string | 해설 (선택사항) |

#### 2.4 OX Quiz (O/X 퀴즈)

```json
{
  "quiz_type": "ox",
  "statement": "Python에서 리스트는 변경 불가능한 자료구조이다",
  "is_correct": false,
  "explanation": "Python의 리스트는 변경 가능(mutable)한 자료구조입니다"
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `statement` | string | 참/거짓 명제 |
| `is_correct` | bool | 정답 (true=O, false=X) |
| `explanation` | string | 해설 (선택사항) |

### Quiz 통합 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `quiz_id` | UUID | 퀴즈 고유 ID |
| `quiz_data` | Object | 퀴즈 데이터 (타입별) |
| `difficulty` | string | 난이도 (easy/medium/hard) |
| `estimated_time` | int | 예상 풀이 시간 (초) |

---

## 📇 3. FlashcardResponse (플래시카드)

**엔드포인트**: `POST /ai/flashcards/generate`

### Request

```json
{
  "chunks": ["청크 텍스트 1", "청크 텍스트 2"],
  "card_types": ["concept", "definition", "example"],
  "count": 20,
  "difficulty": null
}
```

### Response

```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-03-28T12:00:00Z",
  "metadata": {
    "processing_time": 2.8,
    "model_name": "gpt-4",
    "language": "ko",
    "chunks_used": 12
  },
  "flashcard_set": {
    "flashcard_id": "550e8400-e29b-41d4-a716-446655440002",
    "cards": [
      {
        "front": "Python의 리스트란?",
        "back": "순서가 있는 변경 가능한 컬렉션",
        "card_type": "definition",
        "tags": ["python", "자료구조"],
        "difficulty": "easy",
        "hint": "배열과 비슷합니다",
        "related_page": 15,
        "related_section": "자료구조"
      },
      {
        "front": "리스트 선언 예시",
        "back": "my_list = [1, 2, 3, 4, 5]",
        "card_type": "example",
        "tags": ["python", "문법"],
        "difficulty": "easy",
        "hint": "대괄호를 사용합니다",
        "related_page": 15,
        "related_section": "리스트"
      }
    ],
    "total_cards": 2,
    "categories": {
      "python": 2,
      "자료구조": 1,
      "문법": 1
    }
  },
  "extra": {}
}
```

### Flashcard 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `front` | string | 앞면 (질문/단어) |
| `back` | string | 뒷면 (답변/정의) |
| `card_type` | string | 카드 유형 (concept/definition/example/q_and_a) |
| `tags` | string[] | 태그 (주제 분류) |
| `difficulty` | string | 난이도 (easy/medium/hard) |
| `hint` | string | 힌트 (선택사항) |
| `related_page` | int | 관련 페이지 (선택사항) |
| `related_section` | string | 관련 섹션 (선택사항) |

### FlashcardSet 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `flashcard_id` | UUID | 플래시카드 세트 ID |
| `cards` | Flashcard[] | 카드 목록 |
| `total_cards` | int | 전체 카드 수 |
| `categories` | Dict | 카테고리별 카드 수 |

---

## 🔄 데이터 흐름

```
사용자 (PDF 업로드)
    ↓
백엔드 (파일 저장)
    ↓
PDF 텍스트 추출 (PyMuPDF)
    ↓
전처리 (Upstage Layout Analysis / Docling)
    ↓
청킹 (Chunk Service)
    ↓
AI 처리 (GPT-4)
    ├─ 요약 → SummaryResponse
    ├─ 퀴즈 → QuizResponse
    └─ 플래시카드 → FlashcardResponse
    ↓
DB 저장
    ↓
프론트엔드 반환 (JSON)
```

---

## ✅ 구현 체크리스트

- [x] **common_schema.py**: BaseResponse, Metadata 정의
- [x] **summary_schema.py**: SummaryResponse 확장
- [x] **quiz_schema.py**: QuizResponse + 4가지 퀴즈 유형
- [x] **flashcard_schema.py**: FlashcardResponse
- [x] **routes_summary.py**: 요약 API 업데이트
- [x] **routes_quiz.py**: 퀴즈 API 신규 작성
- [x] **routes_flashcard.py**: 플래시카드 API 신규 작성
- [x] **main.py**: 라우트 등록 및 health check 추가
- [ ] **quiz_service.py**: 퀴즈 생성 로직 (다음 단계)
- [ ] **flashcard_service.py**: 플래시카드 생성 로직 (다음 단계)
- [ ] **통합 테스트**: 전체 흐름 검증

---

## 🔗 참고

- 브랜치: `feat/#5-response-schema`
- 이슈: #5
- 모든 응답은 ISO 8601 형식의 타임스탐프 포함
- 모든 ID는 UUID v4 형식 사용
