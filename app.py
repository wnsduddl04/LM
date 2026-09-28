import base64
import os
import pandas as pd
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="LM 럭키문 연맹 - 군단 현황판",
    page_icon="🛡️",
    layout="wide",
)


# --- 이미지 파일 Base64 변환 함수 (CSS 배경 적용용) ---
def get_image_base64(file_path):
  if os.path.exists(file_path):
    with open(file_path, "rb") as f:
      data = f.read()
    return base64.b64encode(data).decode()
  return ""


bg_base64 = get_image_base64("assets/bg_palace.webp")
bg_style = (
    f"url('data:image/webp;base64,{bg_base64}')"
    if bg_base64
    else "url('https://raw.githubusercontent.com/7aab/your-repo/main/assets/bg_palace.webp')"
)

# --- 🎨 삼국지 게임 감성 고급 커스텀 CSS ---
st.markdown(
    f"""
<style>
/* 1. 전체 앱 배경 (궁궐 배경 + 어두운 반투명 오버레이) */
.stApp {{
    background: linear-gradient(rgba(12, 16, 26, 0.82), rgba(12, 16, 26, 0.88)), {bg_style};
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    color: #e0e6ed;
}}

/* 2. 메인 헤더 배너 스타일 */
.main-header {{
    background: rgba(20, 27, 45, 0.75);
    border: 1px solid rgba(212, 175, 55, 0.4);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 25px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(8px);
}}

.header-title {{
    color: #ffd700;
    font-size: 2.2rem;
    font-weight: 800;
    text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
    margin: 0;
}}

/* 3. 현황 정보 카드 (군단장 & 전투력) */
.stat-card {{
    background: rgba(25, 33, 52, 0.85);
    border: 1px solid #d4af37;
    border-radius: 10px;
    padding: 15px 20px;
    box-shadow: inset 0 0 15px rgba(212, 175, 55, 0.15);
}}

.stat-label {{
    color: #a0aec0;
    font-size: 0.9rem;
    font-weight: bold;
    margin-bottom: 5px;
}}

.stat-value {{
    color: #ffffff;
    font-size: 1.5rem;
    font-weight: 800;
}}

/* 4. 라디오 버튼 및 입력창 다크 게임 스타일 */
div[data-baseweb="radio"] {{
    background-color: rgba(18, 24, 38, 0.8);
    padding: 10px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}}

/* 5. 데이터프레임(표) 스타일 */
div[data-testid="stDataFrame"] {{
    background: rgba(15, 20, 32, 0.85);
    border-radius: 10px;
    border: 1px solid rgba(212, 175, 55, 0.3);
    padding: 8px;
}}
</style>
""",
    unsafe_allow_html=True,
)


# --- 1. 데이터 불러오기 ---
@st.cache_data
def load_data():
  for encoding in ["utf-8-sig", "cp949", "utf-8", "latin1"]:
    try:
      df = pd.read_csv("members.csv", encoding=encoding)
      for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()
      return df
    except Exception:
      continue
  return pd.DataFrame()


df = load_data()

# 컬럼 정의
COL_NAME = "이름"
COL_CORPS = "군단명"
COL_POWER = "전투력"
COL_STATUS = "접속률"
COL_LEADER = "군단장"

# --- 2. 상단 상단 메인 헤더 영역 ---
col_logo, col_text = st.columns([1, 4])

with col_logo:
  if os.path.exists("assets/icon_warrior.png"):
    st.image("assets/icon_warrior.png", width=110)
  elif os.path.exists("assets/logo_moon.png"):
    st.image("assets/logo_moon.png", width=110)
  else:
    st.title("🛡️")

with col_text:
  st.markdown("""
        <div class="main-header">
            <h1 class="header-title">🌙 LUCKY MOON 럭키문 연맹</h1>
            <p style="color: #cbd5e0; margin-top: 5px; margin-bottom: 0;">전투력별 군단 나눔 및 연맹원 실시간 관리 현황판</p>
        </div>
    """, unsafe_allow_html=True)

total_count = len(df)

# --- 3. 검색 및 필터 UI ---
search_query = st.text_input(
    "🔍 연맹원 이름 검색",
    placeholder="장수 이름을 입력하세요...",
    label_visibility="collapsed",
)

st.markdown("### ⚔️ 군단 및 활약도 선택")

col_f1, col_f2 = st.columns(2)

with col_f1:
  st.caption("🚩 군단 필터")
  corps_list = ["전체"]
  if COL_CORPS in df.columns:
    unique_corps = df[COL_CORPS].dropna().unique().tolist()
    corps_list.extend(
        [str(c) for c in unique_corps if str(c) not in ["nan", "None"]]
    )
  selected_corps = st.radio(
      "군단 선택", corps_list, horizontal=True, label_visibility="collapsed"
  )

with col_f2:
  st.caption("🔥 활약도(접속률) 필터")
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
                    if s not in ["nan", "None", ""]
                ]
            )
        )
    )
    status_list.extend(unique_status)
  selected_status = st.radio(
      "활약도 선택", status_list, horizontal=True, label_visibility="collapsed"
  )

st.markdown("---")

# --- 4. 데이터 필터링 ---
filtered_df = df.copy()

if search_query and COL_NAME in filtered_df.columns:
  filtered_df = filtered_df[
      filtered_df[COL_NAME].astype(str).str.contains(search_query, na=False)
  ]

if selected_corps != "전체" and COL_CORPS in filtered_df.columns:
  filtered_df = filtered_df[
      filtered_df[COL_CORPS].astype(str).str.strip()
      == str(selected_corps).strip()
  ]

if selected_status != "전체 활약" and target_status_col in filtered_df.columns:
  filtered_df = filtered_df[
      filtered_df[target_status_col].astype(str).str.strip()
      == str(selected_status).strip()
  ]


# --- 5. 특정 군단 선택 시 요약 카드 (전투력 로고 이미지 적용) ---
if selected_corps != "전체":
  st.markdown(f"## 🚩 [{selected_corps}] 군단 현황 요약")

  corps_all_df = df[
      df[COL_CORPS].astype(str).str.strip() == str(selected_corps).strip()
  ]
  card_col1, card_col2 = st.columns(2)

  with card_col1:
    leader_str = "등록된 팀장 없음"
    if COL_LEADER in df.columns and COL_NAME in df.columns:
      leader_rows = corps_all_df[
          corps_all_df[COL_LEADER].astype(str).str.strip() == "팀장"
      ]
      if not leader_rows.empty:
        leader_names = leader_rows[COL_NAME].dropna().astype(str).tolist()
        leader_str = (
            ", ".join(sorted(list(set(leader_names))))
            if leader_names
            else "팀장 지정 없음"
        )

    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-label">👑 군단장 (팀장)</div>
            <div class="stat-value" style="color: #ffd700;">{leader_str}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

  with card_col2:
    total_power_str = "0"
    if COL_POWER in df.columns:
      power_series = pd.to_numeric(
          corps_all_df[COL_POWER]
          .astype(str)
          .str.replace(",", "")
          .str.replace("만", ""),
          errors="coerce",
      ).fillna(0)
      total_power = power_series.sum()
      total_power_str = f"{int(total_power):,}"

    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-label">⚔️ 군단 총 전투력 (인원: {len(corps_all_df)}명)</div>
            <div class="stat-value" style="color: #4fe3c1;">{total_power_str}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

  st.markdown("<br>", unsafe_allow_html=True)


# --- 6. 결과 표 출력 ---
displayed_count = len(filtered_df)
st.markdown(
    f"**표시 중인 장수:** <span style='color:#ffd700; font-weight:bold;'>{displayed_count}명</span>"
    f" (전체 {total_count}명)",
    unsafe_allow_html=True,
)

st.dataframe(filtered_df, use_container_width=True, hide_index=True)
