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


# --- 이미지 파일 Base64 변환 함수 ---
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

# --- 🎨 삼국지 게임풍 테마 CSS ---
st.markdown(
    f"""
<style>
/* 1. 전체 앱 배경 */
.stApp {{
    background: linear-gradient(rgba(15, 23, 42, 0.4), rgba(15, 23, 42, 0.5)), {bg_style};
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    color: #ffffff;
}}

/* 2. 상단 메인 헤더 배너 스타일 */
.main-header {{
    background: rgba(15, 23, 42, 0.85);
    border: 2px solid rgba(212, 175, 55, 0.6);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 25px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(8px);
}}

.header-title {{
    color: #ffd700;
    font-size: 2.2rem;
    font-weight: 800;
    text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
    margin: 0;
}}

/* 3. 검색 결과 카드 박스 스타일 */
.search-result-box {{
    background: rgba(15, 23, 42, 0.95);
    border: 2px solid rgba(212, 175, 55, 0.7);
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.7);
    margin-bottom: 12px;
}}

/* 4. 라디오 버튼 내부 텍스트 크기 및 가독성 설정 */
div[data-testid="stRadio"] label p {{
    color: #ffffff !important;
    font-size: 1.15rem !important;
    font-weight: 800 !important;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9), 0 0 8px rgba(0, 0, 0, 0.8);
}}

/* 데이터프레임(표) 스타일 */
div[data-testid="stDataFrame"] {{
    background: rgba(15, 20, 32, 0.9);
    border-radius: 10px;
    border: 1px solid rgba(212, 175, 55, 0.3);
    padding: 8px;
}}

/* ==========================================
   📱 모바일 화면 최적화 (화면 너비 768px 이하)
   ========================================== */
@media screen and (max-width: 768px) {{
    .main-header {{
        padding: 12px;
        margin-bottom: 15px;
    }}
    
    .header-title {{
        font-size: 1.35rem !important;
    }}
    
    .main-header p {{
        font-size: 0.85rem !important;
    }}
    
    div[data-testid="stRadio"] label p {{
        font-size: 0.95rem !important;
    }}
    
    .filter-title {{
        font-size: 1rem !important;
    }}
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

total_count = len(df)

# --- 2. 상단 메인 헤더 영역 ---
col_logo, col_text = st.columns([1, 4])

with col_logo:
  if os.path.exists("assets/icon_warrior.png"):
    st.image("assets/icon_warrior.png", width=90)
  elif os.path.exists("assets/logo_moon.png"):
    st.image("assets/logo_moon.png", width=90)
  else:
    st.title("🛡️")

with col_text:
  st.markdown("""
        <div class="main-header">
            <h1 class="header-title">🌙 LUCKY MOON 럭키문 연맹</h1>
            <p style="color: #e2e8f0; font-size: 1.05rem; margin-top: 5px; margin-bottom: 0;">전투력별 군단 나눔 및 연맹원 실시간 관리 현황판</p>
        </div>
    """, unsafe_allow_html=True)


# --- 3. 검색 및 필터 UI ---
search_query = st.text_input(
    "🔍 연맹원 이름 검색",
    placeholder="찾고자 하는 주군의 이름을 적어주세요",
    label_visibility="collapsed",
)


# --- 4. 데이터 필터링 미리 계산 ---
filtered_df = df.copy()

if search_query and COL_NAME in filtered_df.columns:
  filtered_df = filtered_df[
      filtered_df[COL_NAME].astype(str).str.contains(search_query, na=False)
  ]


# --- 5. 헤더 바로 밑에 뜨는 실시간 검색 결과 카드 영역 ---
if search_query and search_query.strip():
  st.markdown(
      f"<h2 style='color: #ffd700; font-size: 1.4rem; text-shadow: 2px 2px 4px"
      f" rgba(0,0,0,0.8); margin-top: 10px;'>🔍 '{search_query}' 실시간 검색"
      " 결과</h2>",
      unsafe_allow_html=True,
  )

  if not filtered_df.empty:
    for _, row in filtered_df.iterrows():
      name = row.get(COL_NAME, "이름 없음")
      corps = row.get(COL_CORPS, "소속 없음")
      power = row.get(COL_POWER, "정보 없음")
      status = (
          row.get(COL_STATUS, "정보 없음")
          if COL_STATUS in df.columns
          else row.get("활약도", "정보 없음")
      )
      leader = (
          str(row.get(COL_LEADER, "")) if COL_LEADER in df.columns else ""
      )

      # 팀장 배지 HTML 생성
      leader_badge = (
          f'<span style="background-color: #d4af37; color: #0f172a; padding:'
          f' 2px 8px; border-radius: 6px; font-size: 0.85rem; font-weight:'
          f' bold; margin-left: 8px;">{leader}</span>'
          if leader and leader not in ["nan", "None", "", "일반"]
          else ""
      )

      # 박스 안으로 안전하게 들어가도록 Flexbox 하나로 통일된 HTML 카드 렌더링
      card_html = f"""
            <div class="search-result-box">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                    <div>
                        <span style="color: #ffffff; font-size: 1.25rem; font-weight: 900;">🛡️ {name}</span>
                        <span style="color: #ffd700; font-size: 1.1rem; font-weight: bold; margin-left: 8px;">[{corps}]</span>
                        {leader_badge}
                    </div>
                    <div>
                        <span style="color: #cbd5e0; font-size: 0.95rem;">전투력:</span> 
                        <span style="color: #4fe3c1; font-size: 1.1rem; font-weight: bold; margin-right: 8px;">{power}</span>
                        <span style="color: #cbd5e0; font-size: 0.95rem;">활약도:</span> 
                        <span style="color: #ffffff; font-size: 1.1rem; font-weight: bold;">{status}</span>
                    </div>
                </div>
            </div>
            """
      st.markdown(card_html, unsafe_allow_html=True)
  else:
    st.markdown(
        f"""
        <div class="search-result-box" style="border-color: #ef4444;">
            <div style="color: #ef4444; font-size: 1.1rem; font-weight: bold; text-align: center;">
                ❌ '{search_query}'에 해당하는 주군이 없습니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
  st.markdown("<br>", unsafe_allow_html=True)


# --- 6. 군단 및 활약도 선택 필터 ---
st.markdown(
    "<h3 style='color: #ffd700; margin-top: 10px; font-size: 1.3rem;"
    " text-shadow: 2px 2px 4px rgba(0,0,0,0.8);'>⚔️ 군단 및 활약도 선택</h3>",
    unsafe_allow_html=True,
)

col_f1, col_f2 = st.columns(2)

# 군단 필터
with col_f1:
  st.markdown(
      "<p class='filter-title' style='color:#ffd700; font-size:1.15rem;"
      " font-weight:800; margin-bottom:5px; text-shadow: 1px 1px 3px"
      " rgba(0,0,0,0.8);'>🚩 군단 필터</p>",
      unsafe_allow_html=True,
  )
  corps_list = ["전체"]
  if COL_CORPS in df.columns:
    unique_corps = df[COL_CORPS].dropna().unique().tolist()
    corps_list.extend(
        [str(c) for c in unique_corps if str(c) not in ["nan", "None"]]
    )
  selected_corps = st.radio(
      "군단 선택", corps_list, horizontal=True, label_visibility="collapsed"
  )

# 활약도 필터
with col_f2:
  st.markdown(
      "<p class='filter-title' style='color:#ffd700; font-size:1.15rem;"
      " font-weight:800; margin-bottom:5px; text-shadow: 1px 1px 3px"
      " rgba(0,0,0,0.8);'>🔥 활약도(접속률) 필터</p>",
      unsafe_allow_html=True,
  )
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

# --- 7. 최종 필터 적용 (군단 + 활약도) ---
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


# --- 8. 특정 군단 선택 시 요약 카드 ---
if selected_corps != "전체":
  st.markdown(
      f"<h2 style='color: #ffd700; font-size: 1.4rem; text-shadow: 2px 2px 4px"
      f" rgba(0,0,0,0.8);'>🚩 [{selected_corps}] 군단 현황 요약</h2>",
      unsafe_allow_html=True,
  )

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
        <div class="search-result-box">
            <div style="color: #cbd5e0; font-size: 1rem; font-weight: bold; margin-bottom: 6px;">👑 군단장 (팀장)</div>
            <div style="color: #ffd700; font-size: 1.4rem; font-weight: 800;">{leader_str}</div>
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
        <div class="search-result-box">
            <div style="color: #cbd5e0; font-size: 1rem; font-weight: bold; margin-bottom: 6px;">⚔️ 군단 총 전투력 (인원: {len(corps_all_df)}명)</div>
            <div style="color: #4fe3c1; font-size: 1.4rem; font-weight: 800;">{total_power_str}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

  st.markdown("<br>", unsafe_allow_html=True)


# --- 9. 결과 표 출력 ---
displayed_count = len(filtered_df)
search_msg = (
    f" (검색어: '{search_query}')"
    if (search_query and search_query.strip())
    else ""
  )

st.markdown(
    f"<p style='color: #ffffff; font-size: 1.05rem; text-shadow: 1px 1px 2px"
    f" rgba(0,0,0,0.8);'><b>표시 중인 주군{search_msg}:</b>"
    f" <span style='color:#ffd700; font-weight:bold;'>{displayed_count}명</span>"
    f" (전체 {total_count}명)</p>",
    unsafe_allow_html=True,
)

st.dataframe(filtered_df, use_container_width=True, hide_index=True)
