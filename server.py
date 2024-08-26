import grpc
from concurrent import futures
import chat_pb2
import chat_pb2_grpc

class ChatService(chat_pb2_grpc.ChatServiceServicer):
    def __init__(self):
        self.messages = []

    def Chat(self, request_iterator, context):
        for req in request_iterator:
            self.messages.append((req.user,req.message))
            print(f"{req.user} : {req.message}")
        return chat_pb2.Empty()

    def broadcast_message(self, request, context):
        print('Broadcast message connected!')
        last_index = len(self.messages) - 1
        while True:
            if len(self.messages) > last_index:
                user = self.messages[last_index][0]
                message = self.messages[last_index][1]
                last_index += 1
                yield chat_pb2.ChatMessage(user=user, message=message)
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()