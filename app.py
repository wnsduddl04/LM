import pandas as pd
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="연맹원 군단별 나눔 현황판", page_icon="🛡️", layout="wide"
)


# 1. 데이터 불러오기 (한글 인코딩 자동 처리)
@st.cache_data
def load_data():
  try:
    df = pd.read_csv("members.csv", encoding="cp949")
  except:
    try:
      df = pd.read_csv("members.csv", encoding="utf-8")
    except:
      df = pd.read_csv("members.csv", encoding="latin1")
  return df


df = load_data()

# ------------------------------------------------------------------
# [필수 확인] 본인의 CSV 파일에 적힌 '실제 열 이름(컬럼명)'으로 수정해 주세요!
# ------------------------------------------------------------------
COL_NAME = "이름"  # 연맹원 이름이 있는 열 이름
COL_CORPS = "군단"  # 군단(1군단, 2군단 등)이 있는 열 이름
COL_STATUS = "활약도"  # 활약도/상태가 있는 열 이름
COL_ROLE = "직위"  # 직위가 있는 열 이름 (없다면 무시됨)

st.title("🛡️ 연맹원 군단별 나눔 현황판")
st.markdown("연맹원 명단과 나눔 현황을 실시간으로 확인하는 페이지입니다.")

# --- 전체 통계 ---
total_count = len(df)
st.markdown(f"**총 {total_count}명** 명단 관리")

# --- 상단 검색 및 버튼 UI ---
search_query = st.text_input(
    "🔍", placeholder="이름 또는 직위 검색...", label_visibility="collapsed"
)

st.markdown("---")

# 1. 군단 선택 버튼 (1군단~5군단 혹은 고유 군단만 깔끔하게 추출)
corps_list = ["전체"]
if COL_CORPS in df.columns:
  # 숫자나 긴 ID가 아닌 명확한 군단 그룹만 가져오도록 필터링 가능 (예시: '1군단' 등 포함된 경우)
  unique_corps = df[COL_CORPS].dropna().unique().tolist()
  # 만약 너무 많은 숫자가 뜬다면 1~5군단으로 고정하고 싶을 때 아래 주석 해제
  # unique_corps = ["1군단", "2군단", "3군단", "4군단", "5군단"]
  corps_list.extend([str(c) for c in unique_corps if len(str(c)) < 10])
else:
  corps_list.extend(["1군단", "2군단", "3군단", "4군단", "5군단"])

selected_corps = st.radio(
    "군단 선택", corps_list, horizontal=True, label_visibility="collapsed"
)

# 2. 활약도/상태 선택 버튼
status_list = ["전체 활약"]
if COL_STATUS in df.columns:
  unique_status = df[COL_STATUS].dropna().unique().tolist()
  status_list.extend([str(s) for s in unique_status if len(str(s)) < 15])

selected_status = st.radio(
    "활약도 선택", status_list, horizontal=True, label_visibility="collapsed"
)

st.markdown("---")

# --- 데이터 필터링 로직 ---
filtered_df = df.copy()

# 1. 검색어 필터
if search_query:
  condition = False
  if COL_NAME in filtered_df.columns:
    condition = condition | filtered_df[COL_NAME].astype(str).str.contains(
        search_query, na=False
    )
  if COL_ROLE in filtered_df.columns:
    condition = condition | filtered_df[COL_ROLE].astype(str).str.contains(
        search_query, na=False
    )
  if isinstance(condition, pd.Series):
    filtered_df = filtered_df[condition]

# 2. 군단 필터
if selected_corps != "전체" and COL_CORPS in filtered_df.columns:
  filtered_df = filtered_df[
      filtered_df[COL_CORPS].astype(str) == str(selected_corps)
  ]

# 3. 활약도 필터
if selected_status != "전체 활약" and COL_STATUS in filtered_df.columns:
  filtered_df = filtered_df[
      filtered_df[COL_STATUS].astype(str) == str(selected_status)
  ]

# --- 하단 통계 숫자 표시 ---
displayed_count = len(filtered_df)
st.markdown(
    f"**표시: {displayed_count}명** (전체 {total_count}명 중 필터링됨)"
)

# --- 결과 테이블 출력 ---
st.dataframe(filtered_df, use_container_width=True, hide_index=True)
