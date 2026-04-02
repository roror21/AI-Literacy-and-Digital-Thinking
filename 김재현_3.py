import tkinter as tk

def calculate_dues():
    try:
        # 입력값 가져오기
        total_amount = int(entry_total.get())
        people_count = int(entry_people.get())
        tip_percent = scale_tip.get()
        
        # 팁 포함 총 금액 계산
        total_with_tip = total_amount + (total_amount * tip_percent / 100)
        
        # 1인당 원금 계산
        raw_per_person = total_with_tip / people_count
        
        # 라디오 버튼 선택값에 따른 반올림 로직
        unit = round_var.get()
        if unit == 1:
            rounded_per_person = round(raw_per_person)
        elif unit == 10:
            rounded_per_person = round(raw_per_person, -1)
        elif unit == 100:
            rounded_per_person = round(raw_per_person, -2)
            
        # 실제 걷히는 총 금액과 오차 계산
        collected_total = rounded_per_person * people_count
        diff = collected_total - total_with_tip
        
        # 우측 결과창 업데이트 (상태를 normal로 바꾼 뒤 수정하고 다시 readonly로 변경)
        entry_per_person.config(state="normal")
        entry_per_person.delete(0, tk.END)
        entry_per_person.insert(0, str(int(rounded_per_person)))
        entry_per_person.config(state="readonly")
        
        entry_total_tip.config(state="normal")
        entry_total_tip.delete(0, tk.END)
        entry_total_tip.insert(0, str(int(total_with_tip)))
        entry_total_tip.config(state="readonly")
        
        # 오차에 따른 메시지 출력 분기
        if diff > 0:
            msg = f"남는 금액이 {int(diff)}원이고, 다음 모임 회비나 공용 금액으로 돌릴 수 있습니다."
        elif diff < 0:
            msg = f"{int(abs(diff))}원이 부족하니, 반올림 단위를 조정하거나 금액을 다시 확인하세요."
        else:
            msg = "반올림 후에도 정확히 일치합니다."
            
        label_msg.config(text=msg, fg="blue")
        
    except ValueError:
        # 숫자 이외의 값이 입력되었을 때의 예외 처리
        label_msg.config(text="모든 칸에 올바른 숫자를 입력하세요.", fg="red")

def clear_fields():
    # 모든 입력 및 출력 위젯 초기화
    entry_total.delete(0, tk.END)
    entry_people.delete(0, tk.END)
    scale_tip.set(10)
    round_var.set(1)
    
    entry_per_person.config(state="normal")
    entry_per_person.delete(0, tk.END)
    entry_per_person.config(state="readonly")
    
    entry_total_tip.config(state="normal")
    entry_total_tip.delete(0, tk.END)
    entry_total_tip.config(state="readonly")
    
    label_msg.config(text="")

# 메인 윈도우 설정
root = tk.Tk()
root.title("모임 회비 관리 계산기")
root.geometry("600x450")

# 상단 제목 및 설명 라벨
tk.Label(root, text="모임 회비 관리 계산기", font=("Arial", 16, "bold")).pack(pady=10)
tk.Label(root, text="총 금액, 인원 수, 팁 비율을 입력하여 1인당 부담할 금액을 계산합니다.").pack(pady=5)

# 중앙 데이터 입출력용 프레임 배치
main_frame = tk.Frame(root)
main_frame.pack(pady=10)

# 좌측 프레임: 입력부
left_frame = tk.Frame(main_frame)
left_frame.grid(row=0, column=0, padx=20, sticky="n")

tk.Label(left_frame, text="총 금액 (원)").pack(anchor="w", pady=5)
entry_total = tk.Entry(left_frame, width=20)
entry_total.pack(anchor="w")

tk.Label(left_frame, text="인원 수 (명)").pack(anchor="w", pady=5)
entry_people = tk.Entry(left_frame, width=20)
entry_people.pack(anchor="w")

tk.Label(left_frame, text="팁/서비스 비율 (%)").pack(anchor="w", pady=5)
scale_tip = tk.Scale(left_frame, from_=0, to=20, orient=tk.HORIZONTAL, length=150)
scale_tip.set(10)
scale_tip.pack(anchor="w")

# 우측 프레임: 출력부
right_frame = tk.Frame(main_frame)
right_frame.grid(row=0, column=1, padx=20, sticky="n")

tk.Label(right_frame, text="1인당 금액 (원)").pack(anchor="w", pady=5)
entry_per_person = tk.Entry(right_frame, width=20, state="readonly")
entry_per_person.pack(anchor="w")

tk.Label(right_frame, text="팁 포함 총 금액 (원)").pack(anchor="w", pady=5)
entry_total_tip = tk.Entry(right_frame, width=20, state="readonly")
entry_total_tip.pack(anchor="w")

# 하단 옵션 프레임: 반올림 단위 선택
option_frame = tk.Frame(root)
option_frame.pack(pady=10)

tk.Label(option_frame, text="반올림 단위:").pack(side=tk.LEFT, padx=10)
round_var = tk.IntVar(value=1)
tk.Radiobutton(option_frame, text="1원 단위", variable=round_var, value=1).pack(side=tk.LEFT)
tk.Radiobutton(option_frame, text="10원 단위", variable=round_var, value=10).pack(side=tk.LEFT)
tk.Radiobutton(option_frame, text="100원 단위", variable=round_var, value=100).pack(side=tk.LEFT)

# 최하단 프레임: 버튼 및 결과 메시지
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Clear", width=10, command=clear_fields).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Submit", width=10, bg="orange", fg="white", command=calculate_dues).pack(side=tk.LEFT, padx=10)

label_msg = tk.Label(root, text="")
label_msg.pack(pady=10)

root.mainloop()