import io
import pandas as pd
import streamlit as st

# 1. 웹페이지 제목 설정
st.set_page_config(
    page_title="연맹원 군단별 나눔 현황", page_icon="🛡️", layout="wide"
)

st.title("🛡️ 연맹원 군단별 나눔 현황판")
st.markdown("연맹원 명단과 나눔 현황을 실시간으로 확인하는 페이지입니다.")

# --- [추가된 부분] 원래 화면을 해치지 않는 깔끔한 업로드/다운로드 영역 ---
col1, col2 = st.columns([2, 1])
with col1:
  # 엑셀 파일 업로드 (기본 members.xlsx 또는 엑셀 파일 선택)
  uploaded_file = st.file_uploader(
      "📁 엑셀 파일 업로드 (변경하려면 파일을 올려주세요)",
      type=["xlsx", "xls"],
  )

# 2. 데이터 불러오기 함수 (캐시를 사용하여 빠르게 로드)
@st.cache_data(ttl=10)  # 10초마다 데이터 새로고침
def load_data(file):
  try:
    if file is not None:
      df = pd.read_excel(file)
    else:
      # 업로드된 파일이 없으면 기존 로컬 파일 읽기 시도 (.xlsx 우선, 없으면 .csv)
      try:
        df = pd.read_excel("members.xlsx")
      except FileNotFoundError:
        df = pd.read_csv("members.csv")
    return df
  except Exception:
    return None


df = load_data(uploaded_file)

if df is not None and not df.empty:
  # --- [추가된 부분] 현재 데이터 엑셀 다운로드 버튼 (오른쪽 배치) ---
  with col2:
    st.write("")  # 간격 맞추기용
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
      df.to_excel(writer, index=False, sheet_name="나눔현황")
    excel_data = output.getvalue()

    st.download_button(
        label="📥 현재 현황 엑셀 다운로드",
        data=excel_data,
        file_name="연맹원_나눔현황.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

  st.markdown("---")

  # 3. 검색 및 필터 기능 추가
  search_name = st.text_input("🔍 연맹원 이름 검색", "")
  if search_name:
    df = df[df["이름"].str.contains(search_name, na=False)]

  # 4. 군단별로 섹션을 나눠서 보여주기
  if "군단명" in df.columns:
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
    st.error("⚠️ 데이터에 '군단명' 열(column)이 존재하지 않습니다.")
else:
  st.warning(
      "⚠️ 엑셀 파일(`.xlsx`)을 찾을 수 없거나 데이터가 비어 있습니다. 파일을"
      " 확인해주세요!"
  )