import pandas as pd
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="LM 연맹원 전투력별 군단 나눔 현황판",
    page_icon="🛡️",
    layout="wide",
)


# 1. 데이터 불러오기
@st.cache_data
def load_data():
  for encoding in ["cp949", "utf-8", "latin1"]:
    try:
      return pd.read_csv("members.csv", encoding=encoding)
    except:
      continue
  return pd.DataFrame()


df = load_data()

# 컬럼 이름 정의
COL_NAME = "이름"
COL_CORPS = "군단명"
COL_POWER = "전투력"
COL_STATUS = "활약도"

# 제목 변경 적용
st.title("🛡️ LM 연맹원 전투력별 군단 나눔 현황판")
st.markdown("연맹원 명단과 나눔 현황을 실시간으로 확인하는 페이지입니다.")

# --- 전체 통계 ---
total_count = len(df)
st.markdown(f"**총 {total_count}명** 명단 관리")

# --- 검색 및 버튼 UI ---
search_query = st.text_input(
    "🔍", placeholder="이름 검색...", label_visibility="collapsed"
)

st.markdown("---")

# 1. 군단 선택 버튼
corps_list = ["전체"]
if COL_CORPS in df.columns:
  unique_corps = df[COL_CORPS].dropna().unique().tolist()
  corps_list.extend([str(c) for c in unique_corps])

selected_corps = st.radio(
    "군단 선택", corps_list, horizontal=True, label_visibility="collapsed"
)

# 2. 활약도 선택 버튼
status_list = ["전체 활약"]
if COL_STATUS in df.columns:
  unique_status = df[COL_STATUS].dropna().unique().tolist()
  status_list.extend([str(s) for s in unique_status if str(s).strip() != ""])
else:
  status_list.extend(["★★★ 굉장", "★★ 매우", "★ 활약", "✕ 저조"])

selected_status = st.radio(
    "활약도 선택", status_list, horizontal=True, label_visibility="collapsed"
)

st.markdown("---")

# --- 데이터 필터링 로직 ---
filtered_df = df.copy()

# 1. 검색어 필터
if search_query and COL_NAME in filtered_df.columns:
  filtered_df = filtered_df[
      filtered_df[COL_NAME].astype(str).str.contains(search_query, na=False)
  ]

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
