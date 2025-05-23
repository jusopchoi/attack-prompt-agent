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
    try:
        taxonomy = load_taxonomy()
        strategy = load_strategy()
        return taxonomy, strategy
    except Exception as e:
        logger.error(f"데이터 로드 중 오류 발생: {str(e)}")
        st.error("데이터 로드 중 오류가 발생했습니다.")
        return {}, pd.DataFrame()

taxonomy_data, strategy_data = load_data()

# Sidebar for input
with st.sidebar:
    st.header("입력 설정")
    
    # Taxonomy selection
    taxonomy_options = list(taxonomy_data.keys())
    selected_taxonomy = st.selectbox(
        "Taxonomy 선택",
        options=taxonomy_options,
        key="taxonomy_select"
    )
    
    # Strategy selection
    strategy_options = strategy_data.iloc[:, 0].tolist() if not strategy_data.empty else []
    selected_strategy = st.selectbox(
        "전략 선택",
        options=strategy_options,
        key="strategy_select"
    )
    
    # Generate button
    if st.button("프롬프트 생성"):
        with st.spinner("프롬프트 생성 중..."):
            try:
                result = generate_attack_prompts(selected_taxonomy, selected_strategy)
                st.session_state["result"] = result
            except Exception as e:
                logger.error(f"프롬프트 생성 중 오류 발생: {str(e)}")
                st.error("프롬프트 생성 중 오류가 발생했습니다.")

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
if selected_taxonomy in taxonomy_data:
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
    except Exception as e:
        logger.error(f"커스텀 Taxonomy 처리 중 오류 발생: {str(e)}")
        st.error("커스텀 Taxonomy 처리 중 오류가 발생했습니다.")

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
        logger.info("Taxonomy 파일 내용 로드됨")
        
        uploaded_taxonomy = json.loads(taxonomy_content)
        logger.info("Taxonomy JSON 파싱 성공")
        
        # taxonomy 데이터 유효성 검사
        if not isinstance(uploaded_taxonomy, dict):
            logger.error("Taxonomy 데이터가 딕셔너리 형식이 아님")
            st.error("Taxonomy 데이터는 JSON 객체여야 합니다.")
            st.stop()
        
        # 업로드된 taxonomy를 기존 데이터에 추가
        taxonomy_data.update(uploaded_taxonomy)
        logger.info(f"Taxonomy 데이터 업데이트 완료: {len(uploaded_taxonomy)} 항목 추가")
        st.success("Taxonomy 데이터가 성공적으로 업로드되었습니다.")
        
        # 전략 파일 처리
        if strategy_file is not None:
            try:
                uploaded_strategy = pd.read_csv(strategy_file)
                logger.info(f"전략 파일 로드 성공: {len(uploaded_strategy)} 행")
                
                if not strategy_data.empty:
                    strategy_data = pd.concat([strategy_data, uploaded_strategy], ignore_index=True)
                else:
                    strategy_data = uploaded_strategy
                    
                logger.info(f"전략 데이터 업데이트 완료: 총 {len(strategy_data)} 행")
                st.success(f"전략 {len(uploaded_strategy)}개가 추가되었습니다.")
            except Exception as e:
                logger.error(f"전략 파일 처리 중 오류 발생: {str(e)}")
                st.error("전략 파일 로드 중 오류가 발생했습니다.")
        
        # 페이지 새로고침
        st.experimental_rerun()
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON 파싱 오류: {str(e)}")
        st.error("JSON 파일 형식이 올바르지 않습니다.")
    except Exception as e:
        logger.error(f"파일 처리 중 오류 발생: {str(e)}\n{traceback.format_exc()}")
        st.error("파일 처리 중 오류가 발생했습니다. 로그를 확인해주세요.") 