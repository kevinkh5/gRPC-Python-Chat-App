import tkinter as tk
from tkinter import font
import threading
import grpc
import chat_pb2
import chat_pb2_grpc

with grpc.insecure_channel('localhost:50051') as channel:
    root = tk.Tk()
    root.title("Simple Chat App")
    stub = chat_pb2_grpc.ChatServiceStub(channel)
    user_name = ""

    def listen_for_messages():
        # gRPC 서버로부터 스트리밍 타입으로 계속해서 Response를 받음
        # 쓰레드를 활용하여 해당 함수를 비동기호출 하면서 실시간으로 Response를 받을 수 있음
        for req in stub.broadcast_message(chat_pb2.Empty()):
            print(f"{req.user} : {req.message}\n")
            chat_display.config(state=tk.NORMAL)
            chat_display.insert(tk.END, f"{req.user}: {req.message}\n")  # 메시지 채팅 창에 출력
            chat_display.config(state=tk.DISABLED)

    receive_thread = threading.Thread(target=listen_for_messages) # 리스닝 쓰레드 생성
    def enter_chat():
        global user_name
        user_name = name_input.get()  # 이름 입력받기
        if user_name.strip():  # 이름이 비어있지 않으면
            name_frame.pack_forget()  # 이름 입력 창 숨기기
            chat_frame.pack(fill="both", expand=True)  # 채팅 창 보이기
            stub.Chat(generate_requests("님이 입장하셨습니다", user_name))
            receive_thread.start() # 이름 입력 후 리스닝 쓰레드 시작
        else:
            error_label.config(text="Please enter a valid name.")  # 이름이 비어있다면 오류 메시지

    def generate_requests(msg,user_name):
        yield chat_pb2.ChatMessage(user=user_name,message=msg)

    def send_message():
        # 서버로 메시지를 스트림 타입으로 Request를 보냄
        # 이때는 클라이언트 스트리밍으로 yield로 반환해서 서버측에 보내야함.
        # 따라서 generate_requests() 함수를 통해 서버측에 Request 전송
        message = message_input.get()
        stub.Chat(generate_requests(message, user_name))
        message_input.set("")  # 메시지 입력란 비우기

    ################################## tkinter UI
    # 이름 입력 화면
    name_frame = tk.Frame(root, height=200, width=268)  # height와 width를 사용해 프레임 크기 조정
    name_frame.pack_propagate(False)  # 자식 위젯의 크기에 따라 프레임 크기 변경하지 않도록 설정
    name_frame.pack(padx=20, pady=20, fill="both", expand=True)  # 프레임 여백 설정
    name_label = tk.Label(name_frame, text="Enter your name:")
    name_label.pack(pady=10)
    name_input = tk.Entry(name_frame)
    name_input.pack(pady=5)
    enter_button = tk.Button(name_frame, text="Enter Chat", command=enter_chat)
    enter_button.pack(pady=10)
    name_input.bind("<Return>", lambda event: enter_button.invoke())
    error_label = tk.Label(name_frame, text="", fg="red")
    error_label.pack(pady=5)

    # 채팅 화면
    chat_frame = tk.Frame(root)
    custom_font = font.Font(family="Helvetica", size=22)
    chat_display = tk.Text(chat_frame, state=tk.DISABLED,
                           font=custom_font, height=20, width=20)
    chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    message_input = tk.StringVar()
    message_entry = tk.Entry(chat_frame, textvariable=message_input)
    message_entry.pack(padx=10, pady=5, fill=tk.X)
    send_button = tk.Button(chat_frame, text="Send", command=send_message)
    send_button.pack(pady=5)
    message_entry.bind("<Return>", lambda event: send_button.invoke())

    # 메인 루프 실행
    root.mainloop()
    receive_thread.join()  # 현재 실행 중인 스레드가 종료될 때까지 기다리기(종료 시점 제어 및 자원관리 목적)