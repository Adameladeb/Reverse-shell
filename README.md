# Reverse Shell 🐚

A powerful and feature-rich reverse shell script for remote command execution and file transfer. Take control of remote machines with ease!

## Features

- Execute commands on the remote machine
- Capture and transfer screenshots 📸
- Upload files to the remote machine 💾
- Download files from the remote machine 📥
- Change directory on the remote machine
- Works with Ngrok for remote access outside the network

## Requirements

- Python 3.x
- PIL library (for screenshot feature)
- Ngrok (for remote access)

## Usage

1. Clone the repository:

```bash
git clone https://github.com/Adameladeb/Reverse-shell.git
```
Start the listener on your local machine:

```bash
python listener.py
```
Connect to the remote machine using the client script:

```bash
python client.py
```

Use the following commands in the listener shell:
exit - Terminate the connection
screenshot - Capture and receive a screenshot 📸
upload - Upload files to the remote machine 💾
download - Download files from the remote machine 📥
cd <directory> - Change directory on the remote machine

Examples
 
  
 ```bash
  Shell> ls
```

  
