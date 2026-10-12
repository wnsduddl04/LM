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

# --- 📁 데이터 관리 팝오버 메뉴 (엑셀/CSV 업로드 및 다운로드) ---
with st.popover("📁 데이터 관리 (업로드 / 다운로드)"):
  st.markdown("### 📊 데이터 관리 메뉴")
  uploaded_file = st.file_uploader(
      "새로운 데이터 파일 업로드 (csv)", type=["csv"]
  )

  st.markdown("---")

  # 현재 데이터 다운로드 준비
  try:
    if uploaded_file is not None:
      temp_df = pd.read_csv(uploaded_file)
    else:
      for encoding in ["utf-8-sig", "cp949", "utf-8", "latin1"]:
        try:
          temp_df = pd.read_csv("members.csv", encoding=encoding)
          break
        except Exception:
          temp_df = None
  except Exception:
    temp_df = None

  if temp_df is not None and not temp_df.empty:
    csv_data = temp_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 현재 현황 파일 다운로드",
        data=csv_data,
        file_name="members.csv",
        mime="text/csv",
    )


# --- 1. 데이터 불러오기 ---
@st.cache_data
def load_data(file):
  for encoding in ["utf-8-sig", "cp949", "utf-8", "latin1"]:
    try:
      if file is not None:
        df = pd.read_csv(file, encoding=encoding)
      else:
        df = pd.read_csv("members.csv", encoding=encoding)

      for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()
      return df
    except Exception:
      continue
  return pd.DataFrame()


df = load_data(uploaded_file)

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
  elif os.path.