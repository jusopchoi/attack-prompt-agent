# 공격 프롬프트 생성 에이전트 시스템

이 프로젝트는 LangGraph를 기반으로 한 공격 프롬프트 생성 에이전트 시스템입니다.

## 기능

- Taxonomy 기반 공격 프롬프트 생성
- Universal Judge를 활용한 ASR 평가
- 전략 기반 프롬프트 생성
- 커스텀 Taxonomy 입력 지원
- Streamlit 기반 사용자 인터페이스

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 환경 변수 설정:
`.env` 파일을 생성하고 다음 내용을 추가:
```
OPENAI_API_KEY=your_api_key_here
```

## 사용 방법

1. Streamlit 앱 실행:
```bash
streamlit run app.py
```

2. 웹 브라우저에서 `http://localhost:8501` 접속

3. 사이드바에서:
   - Taxonomy 선택
   - 전략 선택
   - "프롬프트 생성" 버튼 클릭

4. 커스텀 Taxonomy 사용:
   - 하단의 텍스트 영역에 JSON 형식으로 새로운 Taxonomy 입력
   - "커스텀 Taxonomy로 생성" 버튼 클릭

## 프로젝트 구조

- `app.py`: Streamlit UI
- `attack_agent.py`: LangGraph 기반 에이전트 시스템
- `data/`: Taxonomy 및 전략 데이터
  - `taxonomy_seed.json`: 기본 Taxonomy 데이터
  - `strategy.csv`: 공격 전략 데이터

## 구현된 기능

- [x] Taxonomy 기반 프롬프트 생성
- [x] Universal Judge 평가
- [x] 전략 기반 생성
- [x] 커스텀 Taxonomy 입력
- [x] 실패 시 재시도 로직
- [x] Streamlit UI 