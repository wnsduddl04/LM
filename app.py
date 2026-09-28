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
      # 텍스트 컬럼들의 앞뒤 공백 제거 (활약도나 군단명 필터 오작동 방지)
      for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()
      return df
    except:
      continue
  return pd.DataFrame()


df = load_data()

# 컬럼 이름 정의
COL_NAME = "이름"
COL_CORPS = "군단명"
COL_POWER = "전투력"
COL_STATUS = "활약도"
COL_LEADER = "군단장"  # G열 (실제 팀장/군단장 이름이 들어있는 열)

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
  corps_list.extend([str(c) for c in unique_corps if str(c) != "nan"])

selected_corps = st.radio(
    "군단 선택", corps_list, horizontal=True, label_visibility="collapsed"
)

# 2. 활약도 선택 버튼 ('상당한 활약' 제외)
status_list = ["전체 활약"]
if COL_STATUS in df.columns:
  unique_status = df[COL_STATUS].dropna().unique().tolist()
  unique_status = [
      s
      for s in unique_status
      if "상당한 활약" not in str(s) and str(s) != "nan"
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

# 3. 활약도 필터 (공백 및 정확한 값 매칭 처리)
if selected_status != "전체 활약" and COL_STATUS in filtered_df.columns:
  filtered_df = filtered_df[
      filtered_df[COL_STATUS].astype(str).str.strip()
      == str(selected_status).strip()
  ]


# --- 💡 특정 군단 선택 시 [실제 팀장 이름] 및 [전체 전투력] 강조 표시 ---
if selected_corps != "전체":
  st.markdown(f"### 🚩 [{selected_corps}] 현황 정보")

  # 해당 군단에 속한 전체 행들
  corps_all_df = df[df[COL_CORPS].astype(str) == str(selected_corps)]

  col1, col2 = st.columns(2)

  with col1:
    # G열(군단장)에 적힌 실제 유저 이름을 가져오도록 수정
    if COL_LEADER in df.columns:
      # '팀장'이라는 글자 자체이거나 빈 값이면 제외하고 실제 이름만 추출
      raw_leaders = corps_all_df[COL_LEADER].dropna().astype(str).tolist()
      valid_leaders = [
          l
          for l in raw_leaders
          if l != "팀장" and l != "nan" and l.strip() != ""
      ]

      if valid_leaders:
        leader_str = ", ".join(sorted(list(set(valid_leaders))))
      else:
        # 혹시 G열에 별도의 이름이 없고 '팀장'이라고만 적혀있다면 행의 '이름'을 띄워주거나 안내
        leader_str = "등록된 군단장 이름 확인 필요"

      st.info(f"👑 **군단장 (팀장):** {leader_str}")
    else:
      st.info("👑 **군단장 (팀장):** '군단장' 컬럼이 없습니다.")

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
