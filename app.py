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

# 컬럼 이름 정의 (CSV 구조에 맞게 매핑)
COL_NAME = "이름"
COL_CORPS = "군단명"
COL_POWER = "전투력"
COL_STATUS = "활약도"
# G열에 해당하는 군단장(팀장) 컬럼명 (실제 CSV의 G열 헤더 이름과 일치해야 합니다. 예: "군단장" 또는 "팀장")
COL_LEADER = "군단장"

# 제목 설정
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

# 2. 활약도 선택 버튼 ('상당한 활약' 제외)
status_list = ["전체 활약"]
if COL_STATUS in df.columns:
  unique_status = df[COL_STATUS].dropna().unique().tolist()
  unique_status = [
      s for s in unique_status if "상당한 활약" not in str(s)
  ]
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


# --- 💡 특정 군단 선택 시 [팀장 정보] 및 [전체 전투력] 강조 표시 ---
if selected_corps != "전체":
  st.markdown(f"### 🚩 [{selected_corps}] 현황 정보")

  # 해당 군단에 속한 전체 행들 (검색어나 활약도 필터가 걸리기 전 기준)
  corps_all_df = df[df[COL_CORPS].astype(str) == str(selected_corps)]

  col1, col2 = st.columns(2)

  with col1:
    # 팀장(군단장) 정보 추출 (중복 제거 후 표시)
    if COL_LEADER in df.columns:
      leaders = corps_all_df[COL_LEADER].dropna().unique().tolist()
      leader_str = (
          ", ".join(str(l) for l in leaders) if leaders else "등록된 팀장 없음"
      )
      st.info(f"👑 **군단장 (팀장):** {leader_str}")
    else:
      st.info(
          "👑 **군단장 (팀장):** CSV 파일에 '군단장' 컬럼을 확인해 주세요."
      )

  with col2:
    # 전투력 합계 계산
    if COL_POWER in df.columns:
      # 숫자로 변환 가능한 값만 골라서 합산 (콤마나 문자열 제거 처리)
      power_series = pd.to_numeric(
          corps_all_df[COL_POWER]
          .astype(str)
          .str.replace(",", "")
          .str.replace("만", ""),
          errors="coerce",
      ).fillna(0)
      total_power = power_series.sum()

      # 보기 좋게 억/만 단위나 콤마 포맷으로 표시
      st.success(
          f"⚔️ **군단 총 전투력:** {int(total_power):,} (인원: {len(corps_all_df)}명)"
      )
    else:
      st.success(f"⚔️ **군단 인원:** {len(corps_all_df)}명")

  st.markdown("---")


# --- 하단 통계 숫자 표시 ---
displayed_count = len(filtered_df)
st.markdown(
    f"**표시: {displayed_count}명** (전체 {total_count}명 중 필터링됨)"
)

# --- 결과 테이블 출력 ---
st.dataframe(filtered_df, use_container_width=True, hide_index=True)
