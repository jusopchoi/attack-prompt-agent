import streamlit as st
import pandas as pd
import json
from attack_agent import generate_attack_prompts, load_taxonomy, load_strategy, create_workflow_image
import os
from dotenv import load_dotenv
import traceback
import logging

# Load environment variables
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="공격 프롬프트 생성 시스템",
    page_icon="⚠️",
    layout="wide"
)

st.title("공격 프롬프트 생성 시스템")

# Load data
@st.cache_data
def load_data():
    taxonomy = load_taxonomy()
    strategy = load_strategy()
    return taxonomy, strategy

taxonomy_data, strategy_data = load_data()

# Sidebar for input
with st.sidebar:
    st.header("입력 설정")
    
    # Taxonomy selection
    taxonomy_options = list(taxonomy_data.keys())
    selected_taxonomy = st.selectbox(
        "Taxonomy 선택",
        options=taxonomy_options
    )
    
    # Strategy selection
    strategy_options = strategy_data.iloc[:, 0].tolist()  # 첫 번째 컬럼을 전략으로 사용
    selected_strategy = st.selectbox(
        "전략 선택",
        options=strategy_options
    )
    
    # Generate button
    if st.button("프롬프트 생성"):
        with st.spinner("프롬프트 생성 중..."):
            result = generate_attack_prompts(selected_taxonomy, selected_strategy)
            st.session_state["result"] = result

# Main content
if "result" in st.session_state:
    result = st.session_state["result"]
    
    # Display results
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("생성된 프롬프트")
        st.text_area("", result["prompt"], height=200)
    
    with col2:
        st.subheader("평가 결과")
        st.metric("Judge Score", f"{result['score']:.2f}")
        st.metric("성공 여부", "성공" if result["success"] else "실패")

# Display taxonomy and strategy information
st.header("Taxonomy 정보")
st.json(taxonomy_data[selected_taxonomy])

st.header("선택된 전략")
st.write(selected_strategy)

# Add custom taxonomy input
st.header("커스텀 Taxonomy 입력")
custom_taxonomy = st.text_area("새로운 Taxonomy 입력 (JSON 형식)", height=200)

if st.button("커스텀 Taxonomy로 생성"):
    try:
        custom_data = json.loads(custom_taxonomy)
        with st.spinner("커스텀 Taxonomy로 프롬프트 생성 중..."):
            result = generate_attack_prompts(
                json.dumps(custom_data, ensure_ascii=False),
                selected_strategy
            )
            st.session_state["result"] = result
    except json.JSONDecodeError:
        st.error("올바른 JSON 형식으로 입력해주세요.")

# 워크플로우 이미지 표시
st.header("에이전트 워크플로우")
create_workflow_image()

# 파일 업로드 섹션
st.header("파일 업로드")
taxonomy_file = st.file_uploader("Taxonomy Seed JSON 파일 업로드", type=['json'])
strategy_file = st.file_uploader("Strategy CSV 파일 업로드", type=['csv'])

if taxonomy_file is not None:
    try:
        # JSON 파싱
        taxonomy_content = taxonomy_file.getvalue().decode('utf-8')
        uploaded_taxonomy = json.loads(taxonomy_content)
        
        # taxonomy 데이터 유효성 검사
        if not isinstance(uploaded_taxonomy, dict):
            st.error("Taxonomy 데이터는 JSON 객체여야 합니다.")
            st.stop()
        
        # 업로드된 taxonomy를 기존 데이터에 추가
        taxonomy_data.update(uploaded_taxonomy)
        st.success("Taxonomy 데이터가 성공적으로 업로드되었습니다.")
        
        # 전략 파일 처리
        if strategy_file is not None:
            try:
                uploaded_strategy = pd.read_csv(strategy_file)
                strategy_data = pd.concat([strategy_data, uploaded_strategy], ignore_index=True)
                st.success(f"전략 {len(uploaded_strategy)}개가 추가되었습니다.")
            except Exception as e:
                st.error("전략 파일 로드 중 오류가 발생했습니다.")
        
        # 페이지 새로고침
        st.experimental_rerun()
        
    except json.JSONDecodeError:
        st.error("JSON 파일 형식이 올바르지 않습니다.")
    except Exception as e:
        st.error("파일 처리 중 오류가 발생했습니다.")

# 사이드바에 택소노미와 전략 선택 옵션 추가
st.sidebar.title("설정")

# 택소노미 선택
taxonomy_options = list(taxonomy_data.keys())
selected_taxonomy = st.sidebar.selectbox(
    "택소노미 선택",
    options=taxonomy_options
)

# 전략 선택
strategy_options = strategy_data.iloc[:, 0].tolist()  # 첫 번째 컬럼을 전략으로 사용
selected_strategy = st.sidebar.selectbox(
    "전략 선택",
    options=strategy_options
) 