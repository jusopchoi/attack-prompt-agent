import streamlit as st
import json
from attack_agent import run_attack_workflow, load_taxonomy_seed, load_strategy, create_workflow_image
import os
import traceback
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="공격 프롬프트 생성 시스템",
    page_icon="🎯",
    layout="wide"
)

st.title("공격 프롬프트 생성 시스템")

# 워크플로우 이미지 표시
st.header("에이전트 워크플로우")
create_workflow_image()

# 사이드바 설정
st.sidebar.header("설정")
taxonomy_file = st.sidebar.file_uploader("Taxonomy Seed JSON 파일 업로드", type=['json'])
strategy_file = st.sidebar.file_uploader("Strategy CSV 파일 업로드", type=['csv'])

# 메인 콘텐츠 영역
if taxonomy_file is not None:
    try:
        # 파일 내용 로깅
        taxonomy_content = taxonomy_file.getvalue().decode('utf-8')
        logger.info(f"Taxonomy file content: {taxonomy_content[:200]}...")  # 처음 200자만 로깅
        
        taxonomy_data = json.loads(taxonomy_content)
        
        # taxonomy 데이터 유효성 검사
        if not isinstance(taxonomy_data, dict):
            st.error("Taxonomy 데이터는 JSON 객체여야 합니다.")
            st.stop()
            
        if "targets" not in taxonomy_data:
            st.error("Taxonomy 데이터에 'targets' 필드가 없습니다.")
            st.stop()
            
        if not isinstance(taxonomy_data["targets"], list):
            st.error("'targets' 필드는 배열이어야 합니다.")
            st.stop()
            
        if not taxonomy_data["targets"]:
            st.error("'targets' 배열이 비어있습니다.")
            st.stop()
            
        # 유효한 데이터인 경우에만 표시
        st.json(taxonomy_data)
        
        strategies = []
        if strategy_file is not None:
            try:
                strategies = load_strategy(strategy_file)
                logger.info(f"Loaded {len(strategies)} strategies")
                st.sidebar.write(f"전략 {len(strategies)}개 로드됨")
            except Exception as e:
                logger.error(f"Strategy loading error: {str(e)}")
                st.error(f"전략 파일 로드 중 오류 발생: {str(e)}")
        
        if st.button("공격 프롬프트 생성"):
            logger.info("공격 프롬프트 생성 버튼 클릭됨")
            with st.spinner("공격 프롬프트 생성 중..."):
                targets = taxonomy_data["targets"]
                logger.info(f"처리할 목표 수: {len(targets)}")
                
                for target in targets:
                    try:
                        logger.info(f"목표 처리 시작: {target}")
                        st.subheader(f"목표: {target}")
                        
                        # 전략이 있는 경우 선택 가능하게
                        selected_strategy = None
                        if strategies:
                            # 전략 목록을 문자열로 변환하여 표시
                            strategy_options = [f"{i+1}. {s.get('name', '')} - {s.get('description', '')}" 
                                             for i, s in enumerate(strategies)]
                            selected_option = st.selectbox(
                                "공격 전략 선택",
                                strategy_options,
                                key=f"strategy_{target}"
                            )
                            # 선택된 전략의 인덱스 찾기
                            selected_index = strategy_options.index(selected_option)
                            selected_strategy = strategies[selected_index]
                            logger.info(f"선택된 전략: {selected_strategy}")
                        
                        logger.info(f"워크플로우 실행 시작: {target}")
                        result = run_attack_workflow(target, selected_strategy)
                        logger.info(f"워크플로우 결과: {result}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("생성된 공격 프롬프트:")
                            st.write(result["attack_prompt"])
                        with col2:
                            st.write("평가 결과:")
                            st.write(result["judge_evaluation"])
                        
                        st.divider()
                    except Exception as e:
                        error_msg = f"목표 '{target}' 처리 중 오류 발생: {str(e)}\n{traceback.format_exc()}"
                        logger.error(error_msg)
                        st.error(error_msg)
                        continue
    except json.JSONDecodeError as e:
        error_msg = f"잘못된 JSON 파일입니다: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
    except Exception as e:
        error_msg = f"오류가 발생했습니다: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        st.error(error_msg)
else:
    st.info("시작하려면 taxonomy seed JSON 파일을 업로드해주세요.") 