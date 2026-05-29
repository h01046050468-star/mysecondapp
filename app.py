Python
import streamlit as st
import pandas as pd
import numpy as np

# 1. 페이지 기본 설정
st.set_page_config(page_title="수업 활동 점검 대시보드", layout="wide")

st.title("📊 수업 활동 점검 대시보드")
st.caption("학생들의 활동 결과를 분석하고 회의용 요약을 제공합니다.")
st.markdown("---")

# 2. 사이드바 - 파일 업로드 및 필터
with st.sidebar:
    st.header("⚙️ 설정 및 업로드")
    uploaded_file = st.file_uploader("활동 결과 CSV 파일을 업로드하세요.", type=["csv"])
    
    st.markdown("---")
    st.subheader("🔒 개인정보 보호")
    mask_name = st.checkbox("학생 이름 마스킹 (student_id 표시)")
    
    st.markdown("---")
    st.subheader("🔍 필터")
    selected_class = st.selectbox("학급(반) 선택", ["전체", "1반", "2반", "3반"])
    selected_group = st.multiselect("모둠 선택", ["1모둠", "2모둠", "3모둠", "4모둠", "5모둠"])

# 3. 데이터 로드 및 대시보드 표시 (파일이 없을 경우 가상 데이터 생성)
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    st.info("💡 샘플 데이터로 대시보드를 시연 중입니다. 실제 데이터를 보시려면 왼쪽에서 CSV 파일을 업로드해주세요.")
    # 테스트용 가상 데이터 생성
    np.random.seed(42)
    df = pd.DataFrame({
        'student_id': [f"2026_{i:02d}" for i in range(1, 31)],
        'name': [f"학생{i}" for i in range(1, 31)],
        'class': np.random.choice(["1반", "2반", "3반"], 30),
        'group': np.random.choice(["1모둠", "2모둠", "3모둠", "4모둠", "5모둠"], 30),
        'submitted': np.random.choice(["Y", "N"], 30, p=[0.8, 0.2]),
        'score': np.random.randint(50, 101, 30)
    })
    # 미제출자는 점수 0점 처리
    df.loc[df['submitted'] == 'N', 'score'] = 0

# 이름 마스킹 처리 적용
if mask_name:
    df['display_name'] = df['student_id']
else:
    df['display_name'] = df['name']

# 필터링 적용
filtered_df = df.copy()
if selected_class != "전체":
    filtered_df = filtered_df[filtered_df['class'] == selected_class]
if selected_group:
    filtered_df = filtered_df[filtered_df['group'].isin(selected_group)]

# 4. 메인 대시보드 레이아웃
# [상단] 주요 지표 (Metrics)
total_students = len(filtered_df)
submitted_count = len(filtered_df[filtered_df['submitted'] == 'Y'])
submission_rate = (submitted_count / total_students * 100) if total_students > 0 else 0
avg_score = filtered_df[filtered_df['submitted'] == 'Y']['score'].mean() if submitted_count > 0 else 0
not_submitted_count = total_students - submitted_count

col1, col2, col3 = st.columns(3)
col1.metric(label="✅ 제출률", value=f"{submission_rate:.1f}%", delta=f"{submitted_count}/{total_students} 명")
col2.metric(label="💯 제출자 평균 점수", value=f"{avg_score:.1f}점")
col3.metric(label="⚠️ 미제출 학생 수", value=f"{not_submitted_count}명", delta_color="inverse")

st.markdown("---")

# [중단] 시각화 및 테이블
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("👥 모둠별 평균 점수 현황")
    group_chart_data = filtered_df.groupby('group')['score'].mean().reset_index()
    st.bar_chart(data=group_chart_data, x='group', y='score', color="#1E3A8A")

with col_right:
    st.subheader("🚨 미제출 / 보완 필요 대상 (70점 미만)")
    need_attention = filtered_df[(filtered_df['submitted'] == 'N') | (filtered_df['score'] < 70)]
    display_cols = ['class', 'group', 'display_name', 'submitted', 'score']
    
    if not need_attention.empty:
        st.dataframe(need_attention[display_cols].reset_index(drop=True), use_container_width=True)
    else:
        st.success("모든 학생이 과제를 제출했고, 보완이 필요한 학생이 없습니다!")

st.markdown("---")

# [하단] 회의용 요약 브리핑 (향후 기능 선구현)
st.subheader("📝 교과협의회용 요약 브리핑 리포트")
summary_text = f"""[수업 활동 점검 브리핑]
- 대상: {selected_class if selected_class != '전체' else '전체 학급'}
- 총원 {total_students}명 중 {submitted_count}명 제출 완료 (제출률 {submission_rate:.1f}%)
- 과제 제출자 평균 점수는 {avg_score:.1f}점입니다.
- 현재 미제출 학생은 총 {not_submitted_count}명이며, 보완이 필요한 학생들에 대한 피드백 예정입니다.
- 모둠별 참여도 분석 결과, 평균 점수가 가장 낮은 모둠은 [{group_chart_data.loc[group_chart_data['score'].idxmin(), 'group'] if not group_chart_data.empty else '없음'}] 입니다."""

st.code(summary_text, language="markdown")
if st.button("📋 브리핑 문구 복사하기"):
    st.toast("클립보드 기능은 구현 단계에서 st.code의 우측 상단 복사 버튼을 이용해주세요!")
