import socket
import select
import struct
import os

HOST = "0.0.0.0"
PORT = 5000
SERVER_FILES_DIR = "server_files"

server_socket = None
input_sockets = []
client_states = {}  # sock -> {"addr": ..., "stage": ..., "command": ..., "filename": ...}


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


def disconnect_client(sock):
    addr = client_states.get(sock, {}).get("addr")
    if sock in input_sockets:
        input_sockets.remove(sock)
    if sock in client_states:
        del client_states[sock]
    try:
        sock.close()
    except Exception:
        pass

    if addr:
        print(f"[DISCONNECTED] {addr}")
        broadcast(f"[SERVER] {addr} left the chat.", exclude_sock=sock)


def broadcast(message: str, exclude_sock=None):
    dead = []

    for sock in list(client_states.keys()):
        if sock == exclude_sock:
            continue
        ok = safe_send_text(sock, message)
        if not ok:
            dead.append(sock)

    for sock in dead:
        disconnect_client(sock)


def handle_list(sock):
    files = os.listdir(SERVER_FILES_DIR)
    if not files:
        response = "[SERVER] No files available."
    else:
        response = "[SERVER FILES]\n" + "\n".join(files)
    safe_send_text(sock, response)


def handle_upload(sock):
    state = client_states[sock]

    filename = recv_text(sock)
    if filename is None:
        disconnect_client(sock)
        return

    file_data = recv_msg(sock)
    if file_data is None:
        disconnect_client(sock)
        return

    safe_name = os.path.basename(filename)
    save_path = os.path.join(SERVER_FILES_DIR, safe_name)

    with open(save_path, "wb") as f:
        f.write(file_data)

    safe_send_text(sock, f"[SERVER] Upload success: {safe_name} ({len(file_data)} bytes)")
    broadcast(f"[SERVER] {state['addr']} uploaded file: {safe_name}", exclude_sock=sock)
    print(f"[UPLOAD] {state['addr']} -> {safe_name}")


def handle_download(sock):
    filename = recv_text(sock)
    if filename is None:
        disconnect_client(sock)
        return

    safe_name = os.path.basename(filename)
    file_path = os.path.join(SERVER_FILES_DIR, safe_name)

    if not os.path.isfile(file_path):
        safe_send_text(sock, f"[SERVER] File not found: {safe_name}")
        return

    with open(file_path, "rb") as f:
        file_data = f.read()

    ok = safe_send_file(sock, safe_name, file_data)
    if ok:
        print(f"[DOWNLOAD] {client_states[sock]['addr']} <- {safe_name}")
    else:
        disconnect_client(sock)


def handle_chat(sock):
    text = recv_text(sock)
    if text is None:
        disconnect_client(sock)
        return

    msg = f"[{client_states[sock]['addr']}] {text}"
    print(msg)
    broadcast(msg)


def main():
    global server_socket

    os.makedirs(SERVER_FILES_DIR, exist_ok=True)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    input_sockets.append(server_socket)

    print(f"[LISTENING - SELECT] {HOST}:{PORT}")

    try:
        while True:
            read_ready, _, _ = select.select(input_sockets, [], [])

            for sock in read_ready:
                if sock == server_socket:
                    client_sock, client_addr = server_socket.accept()
                    input_sockets.append(client_sock)
                    client_states[client_sock] = {
                        "addr": client_addr
                    }

                    print(f"[CONNECTED] {client_addr}")
                    safe_send_text(client_sock, f"[SERVER] Connected as {client_addr}")
                    broadcast(f"[SERVER] {client_addr} joined the chat.", exclude_sock=client_sock)

                else:
                    command = recv_text(sock)
                    if command is None:
                        disconnect_client(sock)
                        continue

                    if command == "LIST":
                        handle_list(sock)

                    elif command == "UPLOAD":
                        handle_upload(sock)

                    elif command == "DOWNLOAD":
                        handle_download(sock)

                    elif command == "CHAT":
                        handle_chat(sock)

                    else:
                        safe_send_text(sock, f"[SERVER] Unknown command: {command}")

    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")

    finally:
        for sock in list(input_sockets):
            try:
                sock.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()