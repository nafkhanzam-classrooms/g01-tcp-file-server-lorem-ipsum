import socket
import struct
import threading
import os
import sys

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000
BUFFER_SIZE = 4096
DOWNLOAD_DIR = "client_downloads"


def recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data


def send_msg(sock, data: bytes):
    header = struct.pack(">I", len(data))
    sock.sendall(header + data)


def recv_msg(sock):
    header = recv_exact(sock, 4)
    if not header:
        return None
    length = struct.unpack(">I", header)[0]
    return recv_exact(sock, length)


def send_text(sock, text: str):
    send_msg(sock, text.encode("utf-8"))


def recv_text(sock):
    data = recv_msg(sock)
    if data is None:
        return None
    return data.decode("utf-8", errors="replace")


def handle_server_messages(sock):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    while True:
        try:
            msg_type = recv_text(sock)
            if msg_type is None:
                print("\n[INFO] Server disconnected.")
                break

            if msg_type == "TEXT":
                text = recv_text(sock)
                if text is None:
                    print("\n[INFO] Server disconnected.")
                    break
                print(f"\n{text}")

            elif msg_type == "FILE":
                filename = recv_text(sock)
                if filename is None:
                    print("\n[ERROR] Failed to receive filename.")
                    break

                file_data = recv_msg(sock)
                if file_data is None:
                    print("\n[ERROR] Failed to receive file data.")
                    break

                save_path = os.path.join(DOWNLOAD_DIR, os.path.basename(filename))
                with open(save_path, "wb") as f:
                    f.write(file_data)

                print(f"\n[DOWNLOAD OK] File saved to: {save_path}")

            else:
                print(f"\n[WARN] Unknown message type from server: {msg_type}")

        except Exception as e:
            print(f"\n[ERROR] Receiver thread stopped: {e}")
            break


def main():
    host = SERVER_HOST
    port = SERVER_PORT

    if len(sys.argv) >= 2:
        host = sys.argv[1]
    if len(sys.argv) >= 3:
        port = int(sys.argv[2])

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((host, port))
        print(f"[CONNECTED] {host}:{port}")
        print("Commands:")
        print("  /list")
        print("  /upload <filename>")
        print("  /download <filename>")
        print("  /quit")
        print("  anything else = chat message")

        receiver = threading.Thread(
            target=handle_server_messages,
            args=(sock,),
            daemon=True
        )
        receiver.start()

        while True:
            user_input = input("> ").strip()
            if not user_input:
                continue

            if user_input == "/quit":
                print("[INFO] Closing connection...")
                break

            elif user_input == "/list":
                send_text(sock, "LIST")

            elif user_input.startswith("/upload "):
                parts = user_input.split(maxsplit=1)
                if len(parts) < 2:
                    print("[ERROR] Usage: /upload <filename>")
                    continue

                filepath = parts[1]
                if not os.path.isfile(filepath):
                    print(f"[ERROR] File not found: {filepath}")
                    continue

                filename = os.path.basename(filepath)
                with open(filepath, "rb") as f:
                    file_data = f.read()

                send_text(sock, "UPLOAD")
                send_text(sock, filename)
                send_msg(sock, file_data)

                print(f"[UPLOAD SENT] {filename} ({len(file_data)} bytes)")

            elif user_input.startswith("/download "):
                parts = user_input.split(maxsplit=1)
                if len(parts) < 2:
                    print("[ERROR] Usage: /download <filename>")
                    continue

                filename = parts[1]
                send_text(sock, "DOWNLOAD")
                send_text(sock, filename)

            else:
                send_text(sock, "CHAT")
                send_text(sock, user_input)

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        try:
            sock.close()
        except Exception:
            pass
        print("[INFO] Client closed.")


if __name__ == "__main__":
    main()