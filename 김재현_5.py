import streamlit as st
import pandas as pd
import plotly.express as px

def load_data(file):
    """
    업로드된 CSV 파일을 읽어 Pandas DataFrame으로 반환하는 함수
    """
    return pd.read_csv(file)

def render_preview(df):
    """
    데이터프레임의 상위 5개 행을 화면에 표 형태로 출력하는 함수
    """
    st.subheader("원본 데이터 미리보기")
    st.dataframe(df.head())

def draw_plot(df, x_col, y_col, color_col, show_trendline):
    """
    사용자 선택 조건에 따라 산점도와 추세선을 렌더링하고 각종 예외를 처리하는 함수
    """
    st.subheader("산점도 시각화 결과")
    
    # 1. 예외 처리: X축과 Y축이 동일한 변수일 경우 차트 렌더링 중단
    if x_col == y_col:
        st.markdown("<span style='color:red; font-weight:bold;'>경고: X축과 Y축에 동일한 변수가 선택되었습니다. 서로 다른 변수를 선택해주세요.</span>", unsafe_allow_html=True)
        return

    # '선택 안 함'일 경우 색상 변수를 None으로 처리
    color = None if color_col == "선택 안 함" else color_col
    
    # X축과 Y축 데이터가 모두 숫자형(Numeric)인지 검사
    is_x_numeric = pd.api.types.is_numeric_dtype(df[x_col])
    is_y_numeric = pd.api.types.is_numeric_dtype(df[y_col])

    trendline = None
    
    # 2. 예외 처리: 추세선 표시는 요청되었으나 숫자가 아닌 데이터가 포함된 경우
    if show_trendline:
        if is_x_numeric and is_y_numeric:
            trendline = "ols"
        else:
            # 문자가 섞여 있으면 앱이 멈추지 않도록 추세선을 생략하고 텍스트 경고 메시지 출력
            st.markdown("<span style='color:orange; font-weight:bold;'>주의: 추세선(회귀선)은 X축과 Y축이 모두 '숫자' 데이터일 때만 표시됩니다. 추세선을 생략하고 산점도만 출력합니다.</span>", unsafe_allow_html=True)

    # Plotly Express를 이용한 산점도 생성
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color,
        trendline=trendline,
        title=f"{x_col}와(과) {y_col}의 관계"
    )
    
    # 생성된 그래프를 Streamlit 화면에 출력
    st.plotly_chart(fig, use_container_width=True)

def main():
    # 페이지 기본 설정
    st.set_page_config(page_title="변수 관계 시각화 프로그램")
    
    st.title("데이터 산점도 및 추세선 시각화")
    st.markdown("---")

    # 1. 상단: CSV 파일 업로드 위젯
    uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

    if uploaded_file is not None:
        # 데이터 로드
        df = load_data(uploaded_file)
        
        # 2. 중단: 데이터 미리보기
        render_preview(df)
        st.markdown("---")
        
        # 3. 하단 제어부: 변수 동적 할당용 위젯
        st.subheader("산점도 대상 컬럼 선택")
        
        # 데이터프레임의 컬럼명을 리스트로 추출
        columns = df.columns.tolist()
        
        # 색상 범주는 선택하지 않을 수 있으므로 기본 옵션 추가
        color_options = ["선택 안 함"] + columns

        col1, col2 = st.columns(2)
        with col1:
            x_col = st.selectbox("X축 (설명 변수)", columns, index=0)
        with col2:
            # 기본적으로 두 번째 컬럼이 Y축에 지정되도록 인덱스 설정
            default_y_index = 1 if len(columns) > 1 else 0
            y_col = st.selectbox("Y축 (반응 변수)", columns, index=default_y_index)
            
        color_col = st.selectbox("색상으로 구분할 범주 컬럼 (선택)", color_options)
        show_trendline = st.checkbox("추세선(회귀선) 표시")
        
        st.markdown("---")
        
        # 4. 최하단 출력부: 조건부 시각화 실행
        draw_plot(df, x_col, y_col, color_col, show_trendline)

if __name__ == "__main__":
    main()