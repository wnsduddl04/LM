import pandas as pd
import streamlit as st
import io

# 1. 웹페이지 제목 설정
st.set_page_config(page_title="연맹원 군단별 나눔 현황", page_icon="🛡️", layout="wide")

st.title("🛡️ 연맹원 군단별 나눔 현황판")
st.markdown("연맹원 명단과 나눔 현황을 확인하고 데이터를 관리하는 페이지입니다.")

# 사이드바에 파일 업로드 및 다운로드 기능 배치
st.sidebar.header("📁 데이터 관리")

# 엑셀 파일 업로드 기능 (.xlsx 또는 .xls)
uploaded_file = st.sidebar.file_uploader("엑셀 파일 업로드 (members.xlsx)", type=["xlsx", "xls"])

# 2. 데이터 불러오기 로직
@st.cache_data(ttl=10)
def load_data(file):
    try:
        if file is not None:
            # 업로드된 엑셀 파일 읽기
            df = pd.read_excel(file)
        else:
            # 업로드된 파일이 없으면 기존 로컬 members.csv 파일 읽기 시도
            df = pd.read_csv("members.csv")
        return df
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
        return None

df = load_data(uploaded_file)

if df is not None and not df.empty:
    # 3. 엑셀 다운로드 기능
    st.sidebar.markdown("---")
    # DataFrame을 Excel 바이너리 데이터로 변환
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='나눔현황')
    excel_data = output.getvalue()

    st.sidebar.download_button(
        label="📥 현재 현황 엑셀 다운로드",
        data=excel_data,
        file_name="연맹원_나눔현황_백업.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # 4. 검색 및 필터 기능 추가
    search_name = st.text_input("🔍 연맹원 이름 검색", "")
    if search_name:
        df = df[df['이름'].str.contains(search_name, na=False)]

    # 5. 군단별로 섹션을 나눠서 보여주기
    if '군단명' in df.columns:
        군단_목록 = df['군단명'].unique()
        
        for 군단 in 군단_목록:
            st.subheader(f"⚔️ {군단}")
            # 해당 군단에 속한 사람들만 필터링
            군단_df = df[df['군단명'] == 군단]
            
            # 표 형태로 깔끔하게 출력 (인덱스 숨기기)
            st.dataframe(군단_df, use_container_width=True, hide_index=True)
            
            # 구분선
            st.markdown("---")
    else:
        st.error("⚠️ 업로드된 데이터에 '군단명' 열(column)이 존재하지 않습니다. 파일을 확인해주세요.")
else:
    st.warning("⚠️ 엑셀 파일을 업로드하거나 `members.csv` 파일을 준비해주세요!")