
```python
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="수업 활동 점검 대시보드", layout="wide")

st.title("📊 수업 활동 점검 대시보드")

uploaded_file = st.file_uploader(
    "CSV 파일 업로드",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    st.subheader("업로드 데이터 미리보기")
    st.dataframe(df.head())

    # 컬럼 확인
    required_cols = [
        'student_id',
        'student_name',
        'class',
        'group',
        'submission_status',
        'score',
        'needs_support'
    ]

    missing = [col for col in required_cols if col not in df.columns]

    if missing:
        st.error(f"누락된 컬럼: {missing}")
        st.stop()

    # 이름 표시 옵션
    show_real_name = st.checkbox("학생 이름 표시", value=False)

    if show_real_name:
        df['display_name'] = df['student_name']
    else:
        df['display_name'] = df['student_id']

    # 필터
    selected_class = st.selectbox(
        "반 선택",
        ["전체"] + sorted(df['class'].unique().tolist())
    )

    if selected_class != "전체":
        df = df[df['class'] == selected_class]

    selected_group = st.selectbox(
        "모둠 선택",
        ["전체"] + sorted(df['group'].unique().tolist())
    )

    if selected_group != "전체":
        df = df[df['group'] == selected_group]

    # 제출 여부 계산
    total_students = len(df)
    submitted = len(df[df['submission_status'] == '제출'])
    not_submitted = len(df[df['submission_status'] == '미제출'])

    submission_rate = round((submitted / total_students) * 100, 1)

    avg_score = round(
        pd.to_numeric(df['score'], errors='coerce').mean(),
        1
    )

    # KPI
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("전체 학생", total_students)
    col2.metric("제출률", f"{submission_rate}%")
    col3.metric("평균 점수", avg_score)
    col4.metric("미제출", not_submitted)

    # 모둠별 그래프
    st.subheader("모둠별 평균 점수")

    group_score = (
        df.groupby('group')['score']
        .mean(numeric_only=True)
        .reset_index()
    )

    fig = px.bar(
        group_score,
        x='group',
        y='score',
        color='score'
    )

    st.plotly_chart(fig, use_container_width=True)

    # 미제출 목록
    st.subheader("미제출 학생")

    missing_df = df[df['submission_status'] == '미제출']

    st.dataframe(
        missing_df[['display_name', 'class', 'group']]
    )

    # 보완 필요 학생
    st.subheader("보완 필요 학생")

    support_df = df[df['needs_support'] == 'Y']

    st.dataframe(
        support_df[
            ['display_name', 'class', 'group', 'score']
        ]
    )

    # 회의용 요약
    st.subheader("회의용 요약")

    summary = f"""
    현재 제출률은 {submission_rate}%이며,
    평균 점수는 {avg_score}점입니다.
    미제출 학생은 {not_submitted}명입니다.
    """

    st.info(summary)
```
