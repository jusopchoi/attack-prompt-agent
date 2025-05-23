import streamlit as st
import json
from attack_agent import run_attack_workflow, load_taxonomy_seed, load_strategy, create_workflow_image
import os

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
        taxonomy_data = json.load(taxonomy_file)
        st.json(taxonomy_data)
        
        strategies = []
        if strategy_file is not None:
            strategies = load_strategy(strategy_file)
            st.sidebar.write(f"전략 {len(strategies)}개 로드됨")
        
        if st.button("공격 프롬프트 생성"):
            with st.spinner("공격 프롬프트 생성 중..."):
                for target in taxonomy_data.get("targets", []):
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
                    
                    result = run_attack_workflow(target, selected_strategy)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("생성된 공격 프롬프트:")
                        st.write(result["attack_prompt"])
                    with col2:
                        st.write("평가 결과:")
                        st.write(result["judge_evaluation"])
                    
                    st.divider()
    except json.JSONDecodeError:
        st.error("잘못된 JSON 파일입니다. 올바른 taxonomy seed JSON 파일을 업로드해주세요.")
    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")
else:
    st.info("시작하려면 taxonomy seed JSON 파일을 업로드해주세요.") 