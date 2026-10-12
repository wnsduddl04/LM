import io
import pandas as pd
import streamlit as st

# 1. 웹페이지 제목 설정
st.set_page_config(
    page_title="연맹원 군단별 나눔 현황", page_icon="🛡️", layout="wide"
)

st.title("🛡️ 연맹원 군단별 나눔 현황판")
st.markdown("연맹원 명단과 나눔 현황을 실시간으로 확인하는 페이지입니다.")

# 📁 데이터 관리 버튼 (팝오버 메뉴형태로 업로드/다운로드 제공)
with st.popover("📁 데이터 관리 (CSV 업로드 / 다운로드)"):
  st.markdown("### 데이터 관리")

  # CSV 파일 업로드 기능
  uploaded_file = st.file_uploader(
      "CSV 파일 업로드 (members.csv)", type=["csv"]
  )

  st.markdown("---")

  # 현재 데이터 다운로드 버튼을 위한 데이터 준비
  try:
    if uploaded_file is not None:
      temp_df = pd.read_csv(uploaded_file)
    else:
      temp_df = pd.read_csv("members.csv")
  except Exception:
    temp_df = None

  if temp_df is not None and not temp_df.empty:
    # CSV 다운로드 변환
    csv_data = temp_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 현재 현황 CSV 다운로드",
        data=csv_data,
        file_name="members.csv",
        mime="text/csv",
    )


# 2. 데이터 불러오기 함수 (캐시를 사용하여 빠르게 로드)
@st.cache_data(ttl=10)  # 10초마다 데이터 새로고침
def load_data(file):
  try:
    if file is not None:
      df = pd.read_csv(file)
    else:
      df = pd.read_csv("members.csv")
    return df
  except FileNotFoundError:
    return None


df = load_data(uploaded_file)

if df is not None and not df.empty:
  # 3. 검색 및 필터 기능 추가
  search_name = st.text_input("🔍 연맹원 이름 검색", "")
  if search_name:
    df = df[df["이름"].str.contains(search_name, na=False)]

  # 4. 군단별로 섹션을 나눠서 보여주기
  군단_목록 = df["군단명"].unique()

  for 군단 in 군단_목록:
    st.subheader(f"⚔️ {군단}")
    # 해당 군단에 속한 사람들만 필터링
    군단_df = df[df["군단명"] == 군단]

    # 표 형태로 깔끔하게 출력 (인덱스 숨기기)
    st.dataframe(군단_df, use_container_width=True, hide_index=True)

    # 구분선
    st.markdown("---")
else:
  st.warning(
      "⚠️ `members.csv` 파일을 찾을 수 없거나 데이터가 비어 있습니다. 데이터를"
      " 확인해주세요!"
  )