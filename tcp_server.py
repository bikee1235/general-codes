import socket
import threading
import time
from datetime import datetime

class TCPServer:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []
        self.running = False

    def handle_client(self, client_socket, client_address):
        """Handle individual client connection in separate thread"""
        print(f"[{datetime.now()}] New connection from {client_address}")
        
        try:
            # Send welcome message
            welcome_msg = f"Welcome to TCP Server! Connected from {client_address}\n"
            client_socket.send(welcome_msg.encode('utf-8'))
            
            while self.running:
                try:
                    # Receive data from client
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    
                    message = data.decode('utf-8').strip()
                    print(f"[{client_address}] Received: {message}")
                    
                    # Handle different commands
                    if message.lower() == 'quit':
                        break
                    elif message.lower() == 'time':
                        response = f"Server time: {datetime.now()}\n"
                    elif message.lower() == 'clients':
                        response = f"Connected clients: {len(self.clients)}\n"
                    else:
                        response = f"Echo: {message}\n"
                    
                    client_socket.send(response.encode('utf-8'))
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Error handling client {client_address}: {e}")
                    break
                    
        except Exception as e:
            print(f"Error with client {client_address}: {e}")
        finally:
            # Clean up client connection
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            client_socket.close()
            print(f"[{datetime.now()}] Connection closed: {client_address}")

    def start(self):
        """Start the TCP server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"TCP Server started on {self.host}:{self.port}")
            print("Waiting for connections...")
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    client_socket.settimeout(30)  # 30 second timeout
                    
                    self.clients.append(client_socket)
                    
                    # Create new thread for each client
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        print(f"Socket error: {e}")
                        
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop the TCP server"""
        print("Shutting down server...")
        self.running = False
        
        # Close all client connections
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        self.clients.clear()
        
        # Close server socket
        if self.server_socket:
            self.server_socket.close()
        
        print("Server stopped")

if __name__ == "__main__":
    server = TCPServer('localhost', 8080)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nReceived interrupt signal")
        server.stop()
