import socket
import struct
import threading
import os

HOST = "0.0.0.0"
PORT = 5000
BUFFER_SIZE = 4096
SERVER_FILES_DIR = "server_files"

clients = []
clients_lock = threading.Lock()


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


def safe_send_text(sock, text: str):
    try:
        send_text(sock, "TEXT")
        send_text(sock, text)
        return True
    except Exception:
        return False


def safe_send_file(sock, filename: str, file_data: bytes):
    try:
        send_text(sock, "FILE")
        send_text(sock, filename)
        send_msg(sock, file_data)
        return True
    except Exception:
        return False


def broadcast(message: str, exclude_sock=None):
    dead_clients = []

    with clients_lock:
        current_clients = list(clients)

    for client_sock, client_addr in current_clients:
        if client_sock == exclude_sock:
            continue
        ok = safe_send_text(client_sock, message)
        if not ok:
            dead_clients.append((client_sock, client_addr))

    if dead_clients:
        with clients_lock:
            for dc in dead_clients:
                if dc in clients:
                    clients.remove(dc)
                try:
                    dc[0].close()
                except Exception:
                    pass


def handle_client(client_sock, client_addr):
    print(f"[CONNECTED] {client_addr}")

    with clients_lock:
        clients.append((client_sock, client_addr))

    safe_send_text(client_sock, f"[SERVER] Connected as {client_addr}")
    broadcast(f"[SERVER] {client_addr} joined the chat.", exclude_sock=client_sock)

    try:
        while True:
            command = recv_text(client_sock)
            if command is None:
                break

            if command == "LIST":
                files = os.listdir(SERVER_FILES_DIR)
                if not files:
                    response = "[SERVER] No files available."
                else:
                    response = "[SERVER FILES]\n" + "\n".join(files)
                safe_send_text(client_sock, response)

            elif command == "UPLOAD":
                filename = recv_text(client_sock)
                if filename is None:
                    break

                file_data = recv_msg(client_sock)
                if file_data is None:
                    break

                safe_name = os.path.basename(filename)
                save_path = os.path.join(SERVER_FILES_DIR, safe_name)

                with open(save_path, "wb") as f:
                    f.write(file_data)

                safe_send_text(
                    client_sock,
                    f"[SERVER] Upload success: {safe_name} ({len(file_data)} bytes)"
                )
                broadcast(
                    f"[SERVER] {client_addr} uploaded file: {safe_name}",
                    exclude_sock=client_sock
                )
                print(f"[UPLOAD] {client_addr} -> {safe_name}")

            elif command == "DOWNLOAD":
                filename = recv_text(client_sock)
                if filename is None:
                    break

                safe_name = os.path.basename(filename)
                file_path = os.path.join(SERVER_FILES_DIR, safe_name)

                if not os.path.isfile(file_path):
                    safe_send_text(client_sock, f"[SERVER] File not found: {safe_name}")
                    continue

                with open(file_path, "rb") as f:
                    file_data = f.read()

                ok = safe_send_file(client_sock, safe_name, file_data)
                if ok:
                    print(f"[DOWNLOAD] {client_addr} <- {safe_name}")
                else:
                    break

            elif command == "CHAT":
                text = recv_text(client_sock)
                if text is None:
                    break

                msg = f"[{client_addr}] {text}"
                print(msg)
                broadcast(msg)

            else:
                safe_send_text(client_sock, f"[SERVER] Unknown command: {command}")

    except Exception as e:
        print(f"[ERROR] {client_addr}: {e}")

    finally:
        with clients_lock:
            if (client_sock, client_addr) in clients:
                clients.remove((client_sock, client_addr))

        try:
            client_sock.close()
        except Exception:
            pass

        broadcast(f"[SERVER] {client_addr} left the chat.")
        print(f"[DISCONNECTED] {client_addr}")


def main():
    os.makedirs(SERVER_FILES_DIR, exist_ok=True)

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen(5)

    print(f"[LISTENING] {HOST}:{PORT}")

    try:
        while True:
            client_sock, client_addr = server_sock.accept()
            t = threading.Thread(
                target=handle_client,
                args=(client_sock, client_addr),
                daemon=True
            )
            t.start()

    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")

    finally:
        server_sock.close()


if __name__ == "__main__":
    main()