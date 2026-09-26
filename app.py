import pandas as pd
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="연맹원 군단별 나눔 현황판", page_icon="🛡️", layout="wide"
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

# 💡 [디버깅용] 화면 상단에 현재 CSV 파일의 열(Column) 이름을 그대로 출력해 줍니다.
# (나중에 확인하셨으면 이 줄은 지우셔도 됩니다)
st.write("📂 **현재 읽어온 CSV 파일의 열 이름들:**", list(df.columns))

# 컬럼 이름 정의
COL_NAME = "이름"
COL_CORPS = "군단명"
COL_POWER = "전투력"
COL_STATUS = (  # 혹시 파일에 '활약도' 대신 다른 이름으로 되어 있다면 여기서 수정 가능합니다
    "활약도"
)

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

# 1. 군단 선택 버튼
corps_list = ["전체"]
if COL_CORPS in df.columns:
  unique_corps = df[COL_CORPS].dropna().unique().tolist()
  corps_list.extend([str(c) for c in unique_corps])

selected_corps = st.radio(
    "군단 선택", corps_list, horizontal=True, label_visibility="collapsed"
)

# 2. 활약도 선택 버튼 (강제로라도 데이터를 추출해 버튼을 만듭니다)
status_list = ["전체 활약"]
if COL_STATUS in df.columns:
  # 혹시 공백이나 빈 값이 섞여있어도 버튼이 나오도록 처리
  unique_status = df[COL_STATUS].dropna().unique().tolist()
  status_list.extend([str(s) for s in unique_status if str(s).strip() != ""])
else:
  # 만약 '활약도' 열을 아예 못 찾을 때를 대비한 안전 장치
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
