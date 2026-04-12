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
    사용자 선택 조건에 따라 산점도와 추세선을 렌더링하는 함수
    """
    st.subheader("산점도 시각화 결과")
    
    # '선택 안 함'일 경우 색상 변수를 None으로 처리
    color = None if color_col == "선택 안 함" else color_col
    
    # 체크박스 상태에 따라 회귀선(Ordinary Least Squares) 표시 여부 결정
    trendline = "ols" if show_trendline else None

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
    # 페이지 기본 설정 (이모티콘 없음)
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