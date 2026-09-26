import pandas as pd
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="연맹원 군단별 나눔 현황판", page_icon="🛡️", layout="wide"
)

# 1. 데이터 불러오기 (인코딩 자동 예외처리)


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

# 컬럼명이 없을 경우를 대비한 안전 장치 (실제 파일 컬럼에 맞춤)
columns = list(df.columns)
COL_NAME = columns[0] if len(columns) > 0 else "이름"
COL_CORPS = columns[1] if len(columns) > 1 else "군단"
COL_STATUS = columns[2] if len(columns) > 2 else "상태"

st.title("🛡️ 연맹원 군단별 나눔 현황판")
st.markdown("연맹원 명단과 나눔 현황을 실시간으로 확인하는 페이지입니다.")

# --- 전체 통계 ---
total_count = len(df)
st.markdown(f"**총 {total_count}명** 명단 관리 페이지")

# --- 검색 및 버튼 UI ---
search_query = st.text_input(
    "🔍", placeholder="이름 검색...", label_visibility="collapsed"
)

st.markdown("---")

# 군단 선택 버튼
corps_list = ["전체"]
if COL_CORPS in df.columns:
  unique_corps = df[COL_CORPS].dropna().unique().tolist()
  corps_list.extend([str(c) for c in unique_corps])
else:
  corps_list.extend(["1군단", "2군단", "3군단", "4군단", "5군단"])

selected_corps = st.radio(
    "군단 선택", corps_list, horizontal=True, label_visibility="collapsed"
)

# 상태 선택 버튼
status_list = ["전체 상태"]
if COL_STATUS in df.columns:
  unique_status = df[COL_STATUS].dropna().unique().tolist()
  status_list.extend([str(s) for s in unique_status])

selected_status = st.radio(
    "상태 선택", status_list, horizontal=True, label_visibility="collapsed"
)

st.markdown("---")

# --- 데이터 필터링 ---
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

# 3. 상태 필터
if selected_status != "전체 상태" and COL_STATUS in filtered_df.columns:
  filtered_df = filtered_df[
      filtered_df[COL_STATUS].astype(str) == str(selected_status)
  ]

# --- 하단 통계 숫자 표시 ---
displayed_count = len(filtered_df)
st.markdown(
    f"**표시된 인원: {displayed_count}명** (전체 {total_count}명 중)"
)

# --- 결과 테이블 출력 ---
st.dataframe(filtered_df, use_container_width=True, hide_index=True)
