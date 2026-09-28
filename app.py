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
      df = pd.read_csv("members.csv", encoding=encoding)
      # 모든 텍스트 열의 앞뒤 공백 제거
      for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()
      return df
    except:
      continue
  return pd.DataFrame()


df = load_data()

# 컬럼 이름 정의
COL_NAME = "이름"  # A열
COL_CORPS = "군단명"
COL_POWER = "전투력"
COL_STATUS = "접속률"  # 스크린샷 상 활약도/접속률 데이터가 들어있는 실제 컬럼명
COL_LEADER = "군단장"  # G열 ("팀장"이라고 적혀있는 곳)

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
  corps_list.extend([str(c) for c in unique_corps if str(c) != "nan" and str(c) != "None"])

selected_corps = st.radio(
    "군단 선택", corps_list, horizontal=True, label_visibility="collapsed"
)

# 2. 활약도(접속률) 선택 버튼 동적 생성
status_list = ["전체 활약"]
target_status_col = COL_STATUS if COL_STATUS in df.columns else "활약도"

if target_status_col in df.columns:
  raw_status = df[target_status_col].dropna().astype(str).tolist()
  unique_status = sorted(
      list(
          set(
              [
                  s.strip()
                  for s in raw_status
                  if s != "nan" and s != "None" and s != ""
              ]
          )
      )
  )
  status_list.extend(unique_status)
else:
  status_list.extend(["굉장한 활약"])

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

# 2. 군단 필터
if selected_corps != "전체" and COL_CORPS in filtered_df.columns:
  filtered_df = filtered_df[
      filtered_df[COL_CORPS].astype(str).str.strip()
      == str(selected_corps).strip()
  ]

# 3. 활약도(접속률) 필터
if selected_status != "전체 활약" and target_status_col in filtered_df.columns:
  filtered_df = filtered_df[
      filtered_df[target_status_col].astype(str).str.strip()
      == str(selected_status).strip()
  ]


# --- 💡 특정 군단 선택 시 [G열이 '팀장'인 행의 A열 이름] 및 [전체 전투력] 표시 ---
if selected_corps != "전체":
  st.markdown(f"### 🚩 [{selected_corps}] 현황 정보")

  # 해당 군단에 속한 전체 행들
  corps_all_df = df[df[COL_CORPS].astype(str).str.strip() == str(selected_corps).strip()]

  col1, col2 = st.columns(2)

  with col1:
    # G열(COL_LEADER) 값이 "팀장"인 행을 찾아서, 그 행의 A열(COL_NAME) 이름을 가져옴
    if COL_LEADER in df.columns and COL_NAME in df.columns:
      leader_rows = corps_all_df[
          corps_all_df[COL_LEADER].astype(str).str.strip() == "팀장"
      ]
      
      if not leader_rows.empty:
        leader_names = leader_rows[COL_NAME].dropna().astype(str).tolist()
        leader_str = ", ".join(sorted(list(set(leader_names)))) if leader_names else "팀장 지정 없음"
      else:
        leader_str = "등록된 팀장 없음"

      st.info(f"👑 **군단장 (팀장):** {leader_str}")
    else:
      st.info("👑 **군단장 (팀장):** 컬럼 설정을 확인해 주세요.")

  with col2:
    # 전투력 합계 계산
    if COL_POWER in df.columns:
      power_series = pd.to_numeric(
          corps_all_df[COL_POWER]
          .astype(str)
          .str.replace(",", "")
          .str.replace("만", ""),
          errors="coerce",
      ).fillna(0)
      total_power = power_series.sum()
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
