import base64
from datetime import datetime
import io
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

# --- 🎨 삼국지 게임풍 테마 CSS (마우스 오버 툴팁 포함) ---
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

/* 5. 팝오버 버튼 가시성 확보 */
button[data-testid="stPopoverButton"] {{
    background-color: rgba(15, 23, 42, 0.95) !important;
    border: 2px solid rgba(212, 175, 55, 0.9) !important;
    color: #ffd700 !important;
    font-weight: bold !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
}}
button[data-testid="stPopoverButton"]:hover {{
    background-color: rgba(30, 41, 59, 1) !important;
    border-color: #ffd700 !important;
    color: #ffffff !important;
}}

/* 6. 활약도 필터 마우스 오버 툴팁 (메모 박스 스타일) */
.tooltip-container {{
    position: relative;
    display: inline-block;
    cursor: pointer;
    color: #ffd700;
    font-weight: 800;
    font-size: 1.15rem;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
}}

.tooltip-container .tooltip-text {{
    visibility: hidden;
    width: 270px;
    background-color: rgba(15, 23, 42, 0.95);
    color: #e2e8f0;
    text-align: left;
    border-radius: 8px;
    border: 1.5px solid rgba(212, 175, 55, 0.8);
    padding: 10px 12px;
    position: absolute;
    z-index: 99;
    bottom: 125%;
    left: 0;
    font-size: 0.85rem;
    font-weight: normal;
    box-shadow: 0 4px 16px rgba(0,0,0,0.8);
    opacity: 0;
    transition: opacity 0.2s;
    line-height: 1.5;
}}

.tooltip-container:hover .tooltip-text {{
    visibility: visible;
    opacity: 1;
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
}}
</style>
""",
    unsafe_allow_html=True,
)

# 세션 상태 초기화
if "uploader_key" not in st.session_state:
  st.session_state.uploader_key = 0


# --- 📁 데이터 및 파일 관리 팝오버 메뉴 ---
with st.popover("📁 데이터 및 파일 관리"):
  st.markdown("### 📊 연맹원 명단 현황판 관리 (.xlsx)")

  uploaded_file = st.file_uploader(
      "현황판 엑셀 업로드 (members.xlsx)",
      type=["xlsx", "xls"],
      key=f"uploader_{st.session_state.uploader_key}",
  )

  if uploaded_file is not None:
    try:
      with open("members.xlsx", "wb") as f:
        f.write(uploaded_file.getbuffer())

      st.session_state.uploader_key += 1
      st.success(
          "✨ 데이터가 서버에 영구 갱신(저장)되었습니다! 새로고침해도 유지됩니다."
      )
      st.rerun()
    except Exception as e:
      st.error(f"❌ 파일 저장 오류: {e}")

  temp_df = None
  try:
    if os.path.exists("members.xlsx"):
      temp_df = pd.read_excel("members.xlsx")
    elif os.path.exists("members.csv"):
      temp_df = pd.read_csv("members.csv")
  except Exception:
    temp_df = None

  if temp_df is not None and not temp_df.empty:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
      temp_df.to_excel(writer, index=False, sheet_name="나눔현황")
    excel_data = output.getvalue()

    st.download_button(
        label="📥 현재 현황 엑셀 다운로드 (.xlsx)",
        data=excel_data,
        file_name="members.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

  st.markdown("---")

  st.markdown("### 🛠️ 서책계산기 매크로 파일 (ZIP 압축 배포)")
  st.markdown(
      '<p style="color: #cbd5e0; font-size: 0.85rem;">압축을 풀어서'
      " 사용하시면 보안 경고 없이 편리하게 실행됩니다.</p>",
      unsafe_allow_html=True,
  )

  zip_path = "assets/서책계산기.zip"
  if os.path.exists(zip_path):
    with open(zip_path, "rb") as f:
      zip_bytes = f.read()
    st.download_button(
        label="📥 서책계산기 다운로드 (서책계산기.zip)",
        data=zip_bytes,
        file_name="서책계산기.zip",
        mime="application/zip",
    )
  else:
    st.warning("⚠️ `assets/서책계산기.zip` 파일을 찾을 수 없습니다.")

  st.markdown("---")

  st.markdown("### 📋 서책 상담 양식 파일 (.xlsx)")
  consult_path = "assets/서책상담.xlsx"
  if os.path.exists(consult_path):
    with open(consult_path, "rb") as f:
      consult_bytes = f.read()
    st.download_button(
        label="📥 서책 상담 양식 다운로드 (서책상담.xlsx)",
        data=consult_bytes,
        file_name="서책상담.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    )
  else:
    st.warning("⚠️ `assets/서책상담.xlsx` 파일을 찾을 수 없습니다.")


# --- 1. 데이터 불러오기 및 파일 수정 시각 추출 ---
@st.cache_data(ttl=5)
def load_data():
  try:
    if os.path.exists("members.xlsx"):
      df = pd.read_excel("members.xlsx")
    elif os.path.exists("members.csv"):
      for encoding in ["utf-8-sig", "cp949", "utf-8", "latin1"]:
        try:
          df = pd.read_csv("members.csv", encoding=encoding)
          break
        except Exception:
          continue
    else:
      return pd.DataFrame(), ""

    for col in df.select_dtypes(include=["object"]).columns:
      df[col] = df[col].astype(str).str.strip()

    target_file = (
        "members.xlsx" if os.path.exists("members.xlsx") else "members.csv"
    )
    m_time = os.path.getmtime(target_file)
    update_time_str = datetime.fromtimestamp(m_time).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    return df, update_time_str
  except Exception:
    return pd.DataFrame(), ""


df, update_time = load_data()

# 컬럼 정의
COL_NAME = "이름"
COL_CORPS = "군단명"
COL_POWER = "전투력"
COL_STATUS = "접속률"
COL_LEADER = "군단장"
COL_LOCATION = "배치지역"  # D열 배치지역

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

time_str = (
    f" | <span style='color: #4fe3c1;'>최종 갱신: {update_time}</span>"
    if update_time
    else ""
)

with col_text:
  st.markdown(
      f"""
        <div class="main-header">
            <h1 class="header-title">🌙 LUCKY MOON 럭키문 연맹</h1>
            <p style="color: #e2e8f0; font-size: 1.05rem; margin-top: 5px; margin-bottom: 0;">전투력별 군단 나눔 및 연맹원 실시간 관리 현황판{time_str}</p>
        </div>
    """,
      unsafe_allow_html=True,
  )


# --- 3. 검색 및 필터 UI (이름 또는 배치지역 검색) ---
search_query = st.text_input(
    "🔍 연맹원 이름 또는 배치지역 검색",
    placeholder="주군의 이름이나 배치지역(예: E99)을 적어주세요",
    label_visibility="collapsed",
)


# --- 4. 데이터 필터링 미리 계산 (이름 + 배치지역 동시 검색) ---
filtered_df = df.copy()

if search_query and search_query.strip():
  q = search_query.strip()
  cond = pd.Series(False, index=filtered_df.index)

  if COL_NAME in filtered_df.columns:
    cond = cond | filtered_df[COL_NAME].astype(str).str.contains(
        q, case=False, na=False
    )
  if COL_LOCATION in filtered_df.columns:
    cond = cond | filtered_df[COL_LOCATION].astype(str).str.contains(
        q, case=False, na=False
    )

  filtered_df = filtered_df[cond]


# --- 5. 헤더 바로 밑에 뜨는 실시간 검색 결과 카드 영역 (배치지역 강조) ---
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
      location = (
          str(row.get(COL_LOCATION, ""))
          if COL_LOCATION in df.columns
          else ""
      )

      leader_badge = (
          f'<span style="background-color: #d4af37; color: #0f172a; padding:'
          f' 2px 8px; border-radius: 6px; font-size: 0.85rem; font-weight:'
          f' bold; margin-left: 8px;">{leader}</span>'
          if leader and leader not in ["nan", "None", "", "일반"]
          else ""
      )

      location_display = (
          f'<span style="color: #ff8c00; font-size: 1.35rem; font-weight: 900;'
          f' text-shadow: 0 0 8px rgba(255,140,0,0.6); margin-left: '
          f'20px;">📍 {location}</span>'
          if location and location not in ["nan", "None", ""]
          else ""
      )

      card_html = (
          '<div class="search-result-box"><div style="display: flex;'
          " justify-content: space-between; align-items: center; flex-wrap:"
          ' wrap; gap: 10px;"><div><span style="color: #ffffff; font-size:'
          f' 1.25rem; font-weight: 900;">🛡️ {name}</span><span style="color:'
          ' #ffd700; font-size: 1.1rem; font-weight: bold; margin-left:'
          f' 8px;">[{corps}]</span>{leader_badge}{location_display}</div><div><span'
          ' style="color: #cbd5e0; font-size: 0.95rem;">전투력:</span> <span'
          ' style="color: #4fe3c1; font-size: 1.1rem; font-weight: bold;'
          f' margin-right: 8px;">{power}</span><span style="color: #cbd5e0;'
          ' font-size: 0.95rem;">활약도:</span> <span style="color: #ffffff;'
          f' font-size: 1.1rem; font-weight: bold;">{status}</span></div></div></div>'
      )
      st.markdown(card_html, unsafe_allow_html=True)
  else:
    st.markdown(
        """
        <div class="search-result-box" style="border-color: #ef4444;">
            <div style="color: #ef4444; font-size: 1.1rem; font-weight: bold; text-align: center;">
                ❌ 검색 결과가 없습니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
  st.markdown("<br>", unsafe_allow_html=True)


# --- 6. 군단, 배치지역 및 활약도 선택 필터 ---
st.markdown(
    "<h3 style='color: #ffd700; margin-top: 10px; font-size: 1.3rem;"
    " text-shadow: 2px 2px 4px rgba(0,0,0,0.8);'>⚔️ 연맹원 정렬 및 필터</h3>",
    unsafe_allow_html=True,
)

col_f1, col_f2 = st.columns(2)

with col_f1:
  st.markdown(
      "<p style='color:#ffd700; font-size:1.15rem; font-weight:800;"
      " margin-bottom:5px; text-shadow: 1px 1px 3px rgba(0,0,0,0.8);'>🚩"
      " 군단 필터</p>",
      unsafe_allow_html=True,
  )

  corps_list = ["전체"]
  if COL_CORPS in df.columns:
    raw_corps = df[COL_CORPS].dropna().astype(str).tolist()
    cleaned_corps = []
    for c in raw_corps:
      c_str = c.strip()
      if c_str not in ["nan", "None", ""] and c_str not in cleaned_corps:
        cleaned_corps.append(c_str)

    preferred_order = ["1군단", "2군단", "3군단", "4군단", "5군단"]
    sorted_corps = []

    for p in preferred_order:
      if p in cleaned_corps:
        sorted_corps.append(p)
        cleaned_corps.remove(p)

    sorted_corps.extend(sorted(cleaned_corps))
    corps_list.extend(sorted_corps)

  selected_corps = st.radio(
      "군단 선택",
      corps_list,
      horizontal=True,
      label_visibility="collapsed",
      key="corps_radio",
  )

  # --- D열(배치지역)에 내용이 있을 때만 동적으로 생성되는 배치지역 필터 ---
  has_location_data = False
  location_list = ["전체 지역"]
  if COL_LOCATION in df.columns:
    raw_locs = df[COL_LOCATION].dropna().astype(str).tolist()
    cleaned_locs = []
    for l in raw_locs:
      l_str = l.strip()
      if (
          l_str
          and l_str not in ["nan", "None", ""]
          and l_str not in cleaned_locs
      ):
        cleaned_locs.append(l_str)

    if cleaned_locs:
      has_location_data = True
      location_list.extend(sorted(cleaned_locs))

  selected_location = "전체 지역"
  if has_location_data:
    st.markdown(
        "<p style='color:#ff8c00; font-size:1.1rem; font-weight:800;"
        " margin-top:15px; margin-bottom:5px; text-shadow: 1px 1px 3px"
        " rgba(0,0,0,0.8);'>📍 배치지역 필터</p>",
        unsafe_allow_html=True,
    )
    selected_location = st.radio(
        "배치지역 선택",
        location_list,
        horizontal=True,
        label_visibility="collapsed",
        key="location_radio",
    )

with col_f2:
  st.markdown(
      """
    <div class="tooltip-container">
        🔥 활약도(접속률) 필터 ⓘ
        <span class="tooltip-text">
            <b>[활약도 기준 안내]</b><br>
            • <b>굉장한 활약</b>: 7일 내 7일 접속<br>
            • <b>매우 활약</b>: 7일 내 5일 이상 접속<br>
            • <b>활약</b>: 7일 내 3일 이상 접속<br>
            • <b>활약 저조</b>: 7일 내 1일 이상 접속<br>
            • <b>미활약</b>: 7일 내 접속<br>
            • <b>활약 매우 저조</b>: 7일 이상 미접속
        </span>
    </div>
    """,
      unsafe_allow_html=True,
  )

  status_list = ["전체 활약"]
  target_status_col = COL_STATUS if COL_STATUS in df.columns else "활약도"
  if target_status_col in df.columns:
    raw_status = df[target_status_col].dropna().astype(str).tolist()
    cleaned_status = []
    for s in raw_status:
      s_str = s.strip()
      if s_str not in ["nan", "None", ""] and s_str not in cleaned_status:
        cleaned_status.append(s_str)

    status_order = [
        "굉장한 활약",
        "굉장한활약",
        "매우 활약",
        "매우활약",
        "활약",
        "활약 저조",
        "활약저조",
        "미활약",
        "활약 매우 저조",
        "활약매우저조",
    ]
    sorted_status = []

    for s in status_order:
      if s in cleaned_status:
        sorted_status.append(s)
        cleaned_status.remove(s)

    sorted_status.extend(sorted(cleaned_status))
    status_list.extend(sorted_status)

  selected_status = st.radio(
      "활약도 선택",
      status_list,
      horizontal=True,
      label_visibility="collapsed",
      key="status_radio",
  )

st.markdown("---")

# --- 7. 최종 필터 적용 (군단 + 배치지역 + 활약도) ---
if selected_corps != "전체" and COL_CORPS in filtered_df.columns:
  filtered_df = filtered_df[
      filtered_df[COL_CORPS].astype(str).str.strip()
      == str(selected_corps).strip()
  ]

if (
    has_location_data
    and selected_location != "전체 지역"
    and COL_LOCATION in filtered_df.columns
):
  filtered_df = filtered_df[
      filtered_df[COL_LOCATION].astype(str).str.strip()
      == str(selected_location).strip()
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