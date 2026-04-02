import streamlit as st

# 페이지 기본 설정 (이모티콘 사용 금지 규칙 적용)
st.set_page_config(page_title="모임 회비 관리 계산기")

# 상단 제목 및 설명
st.markdown("## 모임 회비 관리 계산기")
st.write("총 금액, 인원 수, 팁 비율을 입력하여 1인당 부담할 금액을 계산합니다.")
st.markdown("---")

# 화면을 2개의 컬럼으로 분할하여 배치
col1, col2 = st.columns(2)

with col1:
    # 사용자 입력부
    # min_value를 설정하여 음수 입력을 방지
    total_amount = st.number_input("총 금액 (원)", min_value=0, value=100000, step=1000)
    people_count = st.number_input("인원 수 (명)", min_value=1, value=4, step=1)
    tip_percent = st.slider("팁/서비스 비율 (%)", min_value=0, max_value=20, value=10)

with col2:
    # 반올림 단위 선택부
    round_unit_str = st.radio(
        "반올림 단위 선택",
        ("1원 단위", "10원 단위", "100원 단위")
    )

st.markdown("---")

# 계산 실행 버튼
if st.button("계산하기", use_container_width=True):
    # 단위 문자열을 실제 정수형 단위로 변환
    if round_unit_str == "1원 단위":
        unit = 1
    elif round_unit_str == "10원 단위":
        unit = 10
    else:
        unit = 100

    # 1. 팁 포함 총 금액 계산
    total_with_tip = total_amount + (total_amount * tip_percent / 100)
    
    # 2. 1인당 원금 계산
    raw_per_person = total_with_tip / people_count
    
    # 3. 반올림 로직 적용
    if unit == 1:
        rounded_per_person = round(raw_per_person)
    elif unit == 10:
        rounded_per_person = round(raw_per_person, -1)
    elif unit == 100:
        rounded_per_person = round(raw_per_person, -2)
        
    # 4. 실제 걷히는 금액과 오차 계산
    collected_total = rounded_per_person * people_count
    diff = collected_total - total_with_tip
    
    # 결과 출력 (웹 화면에 텍스트 표시)
    st.markdown("### 계산 결과")
    
    # 컬럼을 나누어 나란히 텍스트로 표시
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.markdown(f"**1인당 금액:** {int(rounded_per_person)} 원")
    with res_col2:
        st.markdown(f"**팁 포함 총 금액:** {int(total_with_tip)} 원")
        
    st.markdown("---")
    
    # 오차에 따른 메시지 출력 (이모티콘 없이 HTML 태그로 색상만 적용)
    if diff > 0:
        msg = f"남는 금액이 {int(diff)}원이고, 다음 모임 회비나 공용 금액으로 돌릴 수 있습니다."
        st.markdown(f"<span style='color:blue; font-weight:bold;'>{msg}</span>", unsafe_allow_html=True)
    elif diff < 0:
        msg = f"{int(abs(diff))}원이 부족하니, 반올림 단위를 조정하거나 금액을 다시 확인하세요."
        st.markdown(f"<span style='color:red; font-weight:bold;'>{msg}</span>", unsafe_allow_html=True)
    else:
        msg = "반올림 후에도 정확히 일치합니다."
        st.markdown(f"<span style='color:green; font-weight:bold;'>{msg}</span>", unsafe_allow_html=True)