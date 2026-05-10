import streamlit as st
import pandas as pd

def load_data(file):
    """
    업로드된 CSV 파일을 읽어 Pandas DataFrame으로 반환하는 함수
    """
    return pd.read_csv(file)

def preview_data(df, title):
    """
    데이터프레임의 상위 5개 행을 제목과 함께 표 형태로 출력하는 함수
    """
    st.subheader(title)
    st.dataframe(df.head())

def merge_datasets(df1, df2, how):
    """
    두 데이터프레임을 '고객ID'를 기준으로 지정된 방식(how)에 따라 병합하는 함수
    """
    # 두 데이터프레임 모두에 '고객ID' 컬럼이 존재해야 병합 가능
    if '고객ID' in df1.columns and '고객ID' in df2.columns:
        merged_df = pd.merge(df1, df2, on='고객ID', how=how)
        return merged_df
    else:
        st.error("오류: 병합을 위한 공통 기준 컬럼('고객ID')이 존재하지 않습니다.")
        return None

def calculate_vip_avg_order(df):
    """
    병합된 데이터에서 VIP 고객의 평균 주문 금액을 계산하는 함수
    """
    # 필요한 컬럼이 병합된 결과에 모두 존재하는지 확인
    if '등급' in df.columns and '주문금액' in df.columns:
        # 등급이 VIP인 데이터만 필터링
        vip_df = df[df['등급'] == 'VIP']
        
        if not vip_df.empty:
            # 평균 주문 금액 계산 (결측치는 pandas mean()에서 자동 제외됨)
            avg_amount = vip_df['주문금액'].mean()
            return avg_amount
        else:
            return 0
    else:
        return 0

def main():
    # 페이지 기본 설정 (이모티콘 제외)
    st.set_page_config(page_title="데이터 병합 프로그램")
    
    # 1. 파일 업로드 영역
    col1, col2 = st.columns(2)
    with col1:
        file1 = st.file_uploader("첫 번째 파일 (고객 데이터) 업로드", type=["csv"])
    with col2:
        file2 = st.file_uploader("두 번째 파일 (주문 데이터) 업로드", type=["csv"])

    # 두 파일이 모두 업로드되었을 때만 진행
    if file1 is not None and file2 is not None:
        st.markdown("---")
        
        # 데이터 로드
        df_customers = load_data(file1)
        df_orders = load_data(file2)
        
        # 2. 데이터 미리보기 영역
        preview_data(df_customers, "첫 번째 파일 미리보기")
        preview_data(df_orders, "두 번째 파일 미리보기")
        
        st.markdown("---")
        
        # 3. 조인(Join) 방식 선택 라디오 버튼
        join_method = st.radio(
            "병합(Join) 방식을 선택하세요",
            ("inner", "left", "right", "outer"),
            horizontal=True
        )
        
        # 4. 병합 실행 버튼
        if st.button("병합 실행"):
            st.markdown("---")
            
            # 병합 로직 실행
            merged_df = merge_datasets(df_customers, df_orders, join_method)
            
            if merged_df is not None:
                # 5. 결과 표시 영역
                st.subheader(f"병합 결과 ({join_method} Join)")
                st.dataframe(merged_df)
                
                # 행 개수 및 결측치 계산
                total_rows = len(merged_df)
                total_nulls = merged_df.isnull().sum().sum()
                
                st.write(f"**전체 행 개수:** {total_rows}개")
                st.write(f"**전체 결측치 개수:** {total_nulls}개")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # VIP 평균 주문 금액 계산 및 출력
                st.subheader("VIP 고객 평균 주문 금액")
                vip_avg = calculate_vip_avg_order(merged_df)
                
                if vip_avg > 0:
                    # 금액을 통화 형식(천단위 콤마, 소수점 둘째자리)으로 포맷팅
                    st.write(f"결과: {vip_avg:,.2f}원")
                else:
                    st.write("결과: 계산할 VIP 데이터가 없거나 금액을 확인할 수 없습니다.")

if __name__ == "__main__":
    main()