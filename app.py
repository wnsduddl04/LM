import pandas as pd
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="연맹원 군단별 나눔 현황판", page_icon="🛡️", layout="wide"
)

# 1. 데이터 불러오기 (한글 인코딩 오류 방지)
@st.cache_data
def load_data():
  try:
    df = pd.read_csv("members.csv", encoding="cp949")
  except:
    df = pd.read_csv("members.csv", encoding="utf-8")
  return df


df = load_data()

# -------------------------------------------------------------
# [안내] 본인 CSV 파일의 컬럼명에 맞춰 아래 이름을 수정해 주세요!
# 예: 군단 컬럼이 '군단', 활약도 컬럼이 '활약도', 이름이 '이름'인 경우
# -------------------------------------------------------------
COL_CORPS = "군단"  # 예: 1군단, 2군단 ...
COL_NAME = "이름"  # 연맹원 이름
COL_STATUS = "활약도"  # 예: 굉장, 매우, 활약, 저조 등
COL_ROLE = "직위"  # 직위 (검색용)

# 상단 타이틀
st.title("🛡️ 연맹원 군단별 나눔 현황판")
st.markdown("연맹원 명단과 나눔 현황을 실시간으로 확인하는 페이지입니다.")

# --- 전체 통계 계산 ---
total_count = len(df)
# 만약 군단이 '1군단', '2군단' 형태로 적혀있다면 아래처럼 계산 가능
corps_counts = (
    df[COL_CORPS].value_counts().to_dict()
    if COL_CORPS in df.columns
    else {}
)

st.markdown(
    f"**총 {total_count}명** · 1~5군단 각 "
    f"{corps_counts.get('1군단', total_count//5)}명"
)

# --- 검색바 & 필터 버튼 UI 구현 ---
col_search, col_filters = st.columns([1, 2])

with col_search:
  search_query = st.text_input(
      "🔍", placeholder="이름 또는 직위 검색...", label_visibility="collapsed"
  )

# Streamlit의 라디오 버튼이나 selectbox를 가로형 버튼 느낌으로 구현
st.markdown("---")

# 1단차 필터: 군단 선택 (전체, 1군단~5군단)
corps_options = ["전체", "1군단", "2군단", "3군단", "4군단", "5군단"]
selected_corps = st.radio(
    "군단 선택", corps_options, horizontal=True, label_visibility="collapsed"
)

# 2단차 필터: 활약도 선택 (전체 활약, 굉장, 매우, 활약, 저조 등)
status_options = ["전체 활약", "★★★ 굉장", "★★ 매우", "★ 활약", "✕ 저조"]
selected_status = st.radio(
    "활약도 선택",
    status_options,
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown("---")

# --- 데이터 필터링 로직 ---
filtered_df = df.copy()

# 1. 검색어 필터 (이름 또는 직위)
if search_query:
  filtered_df = filtered_df[
      filtered_df[COL_NAME].str.contains(search_query, na=False)
      | filtered_df[COL_ROLE].str.contains(search_query, na=False)
  ]

# 2. 군단 필터
if selected_corps != "전체":
  filtered_df = filtered_df[filtered_df[COL_CORPS] == selected_corps]

# 3. 활약도 필터
if selected_status != "전체 활약":
  # 예: '★★★ 굉장'에서 별이나 텍스트를 추출해서 매칭
  keyword = selected_status.split(" ")[
      -1
  ]  # '굉장', '매우', '활약', '저조' 만 추출
  filtered_df = filtered_df[
      filtered_df[COL_STATUS].str.contains(keyword, na=False)
  ]

# --- 하단 통계 숫자 표시 (표시: X명, 상태별 인원) ---
displayed_count = len(filtered_df)

# 활약도별 카운트 계산 (데이터에 컬럼이 존재할 경우)
if COL_STATUS in df.columns:
  cnt_great = len(
      df[df[COL_STATUS].str.contains("굉장", na=False)]
  )  # 굉장한 활약 수
  cnt_very = len(df[df[COL_STATUS].str.contains("매우", na=False)])  # 매우 활약 수
  cnt_active = len(
      df[df[COL_STATUS].str.contains("활약", na=False)]
      - df[df[COL_STATUS].str.contains("매우|굉장", na=False)]
  )  # 일반 활약 수 (필요시 조정)
  cnt_low = len(df[df[COL_STATUS].str.contains("저조", na=False)])  # 저조 수
else:
  cnt_great, cnt_very, cnt_active, cnt_low = 0, 0, 0, 0

st.markdown(
    f"**표시: {displayed_count}명** &nbsp;&nbsp;|&nbsp;&nbsp; 굉장한 활약: <span"
    f' style="color:green; font-weight:bold;">{cnt_great}</span>'
    f" &nbsp;&nbsp; 매우 활약: <span"
    f' style="color:blue; font-weight:bold;">{cnt_very}</span>'
    f" &nbsp;&nbsp; 활약: <span"
    f' style="color:orange; font-weight:bold;">{cnt_active}</span>'
    f" &nbsp;&nbsp; 저조: <span"
    f' style="color:red; font-weight:bold;">{cnt_low}</span>',
    unsafe_allow_html=True,
)

# --- 결과 테이블(또는 카드 형태) 출력 ---
st.dataframe(filtered_df, use_container_width=True)
