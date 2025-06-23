import socket
import threading

def receive_messages(client_socket):
    """Receive messages from server in separate thread"""
    while True:
        try:
            response = client_socket.recv(1024).decode('utf-8')
            if not response:
                break
            print(f"Server: {response.strip()}")
        except:
            break

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect(('localhost', 8080))
        print("Connected to server")
        
        # Start receiving thread
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.daemon = True
        receive_thread.start()
        
        # Send messages
        while True:
            message = input()
            if message.lower() == 'quit':
                break
            client_socket.send(message.encode('utf-8'))
            
    except Exception as e:
        print(f"Client error: {e}")
    finally:
        client_socket.close()
        print("Disconnected from server")

if __name__ == "__main__":
    main()
