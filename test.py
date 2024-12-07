import socket

HOST = '127.0.0.1'  # Server's hostname or IP address
PORT = 65434       # Server's port

# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Example: Send detected object data
object_id = "12345"  # Replace with actual detected object ID
message = f"Object ID: {object_id}"
client_socket.sendall(message.encode())

# Optionally, receive a response
response = client_socket.recv(1024)
print(f"Server response: {response.decode()}")

client_socket.close()
