import streamlit as st
import plotly.express as px
import pandas as pd

def load_text_file(uploaded_file):
    """
    업로드된 텍스트 파일을 읽어서 문자열로 반환하는 함수
    """
    # 텍스트 파일을 utf-8 인코딩으로 디코딩하여 읽음
    return uploaded_file.getvalue().decode("utf-8")

def analyze_sentiment(text):
    """
    간단한 키워드 사전을 기반으로 텍스트 내의 긍정/부정 단어를 추출하는 함수
    """
    # 초보자 수준에 맞춘 간단한 감성 키워드 사전
    positive_keywords = ["편해", "강하", "오래가", "만족", "깔끔", "좋아", "뛰어납", "똑똑", "추천", "괜찮"]
    negative_keywords = ["무거워", "아픕", "소음", "어렵", "개선", "불편", "별로", "나쁩", "단점"]

    found_positive = []
    found_negative = []

    # 텍스트에 긍정 키워드가 포함되어 있는지 검사
    for word in positive_keywords:
        if word in text:
            # 발견된 단어와 텍스트 내 등장 횟수를 저장
            count = text.count(word)
            for _ in range(count):
                found_positive.append(word)

    # 텍스트에 부정 키워드가 포함되어 있는지 검사
    for word in negative_keywords:
        if word in text:
            count = text.count(word)
            for _ in range(count):
                found_negative.append(word)

    return found_positive, found_negative

def calculate_score(pos_list, neg_list):
    """
    긍정/부정 단어의 개수를 바탕으로 비율을 계산하는 함수
    """
    pos_count = len(pos_list)
    neg_count = len(neg_list)
    total_count = pos_count + neg_count

    # 분석할 감성 단어가 없는 경우 예외 처리
    if total_count == 0:
        return 0, 0

    pos_ratio = (pos_count / total_count) * 100
    neg_ratio = (neg_count / total_count) * 100

    return pos_ratio, neg_ratio

def draw_pie_chart(pos_ratio, neg_ratio):
    """
    Plotly를 사용하여 한글 깨짐 없이 원형 그래프를 그리는 함수
    """
    # Plotly Express에 입력할 데이터프레임 생성
    data = pd.DataFrame({
        "감성": ["긍정", "부정"],
        "비율": [pos_ratio, neg_ratio]
    })

    # 원형 그래프 생성 (색상 지정 포함)
    fig = px.pie(
        data, 
        values="비율", 
        names="감성", 
        title="감성 분석 결과",
        color="감성",
        color_discrete_map={"긍정": "royalblue", "부정": "darkorange"}
    )
    
    # 생성된 그래프를 화면에 출력
    st.plotly_chart(fig, use_container_width=True)

def main():
    # 1. 페이지 기본 설정
    st.set_page_config(page_title="감성 분석 프로그램")
    st.title("텍스트 감성 분석 및 시각화")
    st.markdown("---")

    # 2. 파일 업로드 영역
    st.subheader("1. 텍스트 파일 업로드")
    uploaded_file = st.file_uploader("분석할 텍스트 파일(.txt)을 업로드하세요", type=["txt"])

    if uploaded_file is not None:
        # 파일 내용 읽기
        text_content = load_text_file(uploaded_file)
        
        # 3. 파일 내용 보기 영역
        st.subheader("2. 파일 내용 보기")
        st.text_area("원본 텍스트", value=text_content, height=150, disabled=True)
        st.markdown("---")

        # 4. 감성 단어 영역 (분석 실행)
        pos_words, neg_words = analyze_sentiment(text_content)
        
        st.subheader("3. 감성 단어 추출 결과")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<span style='color:royalblue; font-weight:bold;'>[긍정 단어]</span>", unsafe_allow_html=True)
            st.write(", ".join(pos_words) if pos_words else "없음")
        with col2:
            st.markdown("<span style='color:darkorange; font-weight:bold;'>[부정 단어]</span>", unsafe_allow_html=True)
            st.write(", ".join(neg_words) if neg_words else "없음")
        
        st.markdown("---")

        # 5. 감성 점수 계산 영역
        st.subheader("4. 감성 점수 계산")
        pos_ratio, neg_ratio = calculate_score(pos_words, neg_words)
        
        if pos_ratio == 0 and neg_ratio == 0:
            st.warning("분석할 수 있는 감성 키워드가 텍스트에 존재하지 않습니다.")
        else:
            st.write(f"긍정 비율: {pos_ratio:.1f}% / 부정 비율: {neg_ratio:.1f}%")
            
            # 지배적인 감성에 따른 요약 메시지 출력
            if pos_ratio > neg_ratio:
                st.markdown("<span style='color:royalblue; font-weight:bold;'>요약: 전반적으로 긍정적인 반응이 우세합니다.</span>", unsafe_allow_html=True)
            elif neg_ratio > pos_ratio:
                st.markdown("<span style='color:darkorange; font-weight:bold;'>요약: 전반적으로 부정적인 반응이 우세합니다.</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span style='font-weight:bold;'>요약: 긍정과 부정 반응이 팽팽합니다.</span>", unsafe_allow_html=True)

            st.markdown("---")

            # 6. 시각화 영역
            st.subheader("5. 시각화")
            draw_pie_chart(pos_ratio, neg_ratio)

if __name__ == "__main__":
    main()