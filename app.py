import pandas as pd
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="연맹원 군단별 나눔 현황판", page_icon="🛡️", layout="wide"
)


# 1. 데이터 불러오기 (한글 인코딩 방지)
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
# 💡 [중요] CSV 파일의 실제 열 이름(제목)에 맞게 설정했습니다!
# ------------------------------------------------------------------
COL_NAME = "이름"  # 이름 열
COL_CORPS = "군단명"  # 군단 열 (표에서 '군단명'으로 확인됨)
COL_POWER = "전투력"  # 전투력 열
COL_STATUS = "활약도"  # 활약도 또는 상태 열 (만약 다른 이름이면 이 부분을 수정하세요)

st.title("🛡️ 연맹원 군단별 나눔 현황판")
st.markdown("연맹원 명단과 나눔 현황을 실시간으로 확인하는 페이지입니다.")

# --- 전체 통계 ---
total_count = len(df)
st.markdown(f"**총 {total_count}명** 명단 관리")

# --- 검색 및 버튼 UI ---
search_query = st.text_input(
    "🔍", placeholder="이름 검색...", label_visibility="collapsed"
)

st.markdown("---")

# 1. 군단 선택 버튼 (데이터에 있는 군단명들을 자동으로 읽어와서 버튼 생성)
corps_list = ["전체"]
if COL_CORPS in df.columns:
  unique_corps = df[COL_CORPS].dropna().unique().tolist()
  corps_list.extend([str(c) for c in unique_corps])
else:
  corps_list.extend(["1군단", "2군단", "3군단", "4군단", "5군단"])

selected_corps = st.radio(
    "군단 선택", corps_list, horizontal=True, label_visibility="collapsed"
)

# 2. 활약도/상태 선택 버튼 (만약 열이 존재하면 해당 값들로 버튼 생성, 없으면 임시 생성)
status_list = ["전체 활약"]
if COL_STATUS in df.columns:
  unique_status = df[COL_STATUS].dropna().unique().tolist()
  status_list.extend([str(s) for s in unique_status])
else:
  # 활약도 열이 없을 경우를 대비한 예시 (필요시 수정)
  status_list.extend(["굉장한 활약", "매우 활약", "활약", "저조"])

selected_status = st.radio(
    "활약도 선택", status_list, horizontal=True, label_visibility="collapsed"
)

st.markdown("---")

# --- 데이터 필터링 로직 ---
filtered_df = df.copy()

# 1. 검색어 필터 (이름 기준)
if search_query and COL_NAME in filtered_df.columns:
  filtered_df = filtered_df[
      filtered_df[COL_NAME].astype(str).str.contains(search_query, na=False)
  ]

# 2. 군단 필터 (선택한 군단과 일치하는 데이터만 추출)
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
