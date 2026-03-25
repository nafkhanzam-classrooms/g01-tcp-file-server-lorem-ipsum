import socket
import select
import struct
import os

HOST = "0.0.0.0"
PORT = 5000
SERVER_FILES_DIR = "server_files"

server_socket = None
poll_obj = None
fd_to_socket = {}
client_addrs = {}


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
    fd = sock.fileno()
    addr = client_addrs.get(fd)

    try:
        poll_obj.unregister(fd)
    except Exception:
        pass

    if fd in fd_to_socket:
        del fd_to_socket[fd]
    if fd in client_addrs:
        del client_addrs[fd]

    try:
        sock.close()
    except Exception:
        pass

    if addr:
        print(f"[DISCONNECTED] {addr}")
        broadcast(f"[SERVER] {addr} left the chat.", exclude_fd=fd)


def broadcast(message: str, exclude_fd=None):
    dead_fds = []

    for fd, sock in list(fd_to_socket.items()):
        if sock == server_socket:
            continue
        if fd == exclude_fd:
            continue

        ok = safe_send_text(sock, message)
        if not ok:
            dead_fds.append(fd)

    for fd in dead_fds:
        sock = fd_to_socket.get(fd)
        if sock:
            disconnect_client(sock)


def handle_list(sock):
    files = os.listdir(SERVER_FILES_DIR)
    if not files:
        response = "[SERVER] No files available."
    else:
        response = "[SERVER FILES]\n" + "\n".join(files)
    safe_send_text(sock, response)


def handle_upload(sock):
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
    broadcast(f"[SERVER] {client_addrs[sock.fileno()]} uploaded file: {safe_name}", exclude_fd=sock.fileno())
    print(f"[UPLOAD] {client_addrs[sock.fileno()]} -> {safe_name}")


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
        print(f"[DOWNLOAD] {client_addrs[sock.fileno()]} <- {safe_name}")
    else:
        disconnect_client(sock)


def handle_chat(sock):
    text = recv_text(sock)
    if text is None:
        disconnect_client(sock)
        return

    msg = f"[{client_addrs[sock.fileno()]}] {text}"
    print(msg)
    broadcast(msg)


def main():
    global server_socket, poll_obj

    os.makedirs(SERVER_FILES_DIR, exist_ok=True)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    poll_obj = select.poll()
    poll_obj.register(server_socket.fileno(), select.POLLIN)

    fd_to_socket[server_socket.fileno()] = server_socket

    print(f"[LISTENING - POLL] {HOST}:{PORT}")

    try:
        while True:
            events = poll_obj.poll()

            for fd, event in events:
                sock = fd_to_socket.get(fd)
                if sock is None:
                    continue

                if sock == server_socket:
                    client_sock, client_addr = server_socket.accept()
                    fd_to_socket[client_sock.fileno()] = client_sock
                    client_addrs[client_sock.fileno()] = client_addr
                    poll_obj.register(client_sock.fileno(), select.POLLIN)

                    print(f"[CONNECTED] {client_addr}")
                    safe_send_text(client_sock, f"[SERVER] Connected as {client_addr}")
                    broadcast(f"[SERVER] {client_addr} joined the chat.",
                              exclude_fd=client_sock.fileno())

                elif event & select.POLLIN:
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

                elif event & (select.POLLHUP | select.POLLERR | select.POLLNVAL):
                    disconnect_client(sock)

    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")

    finally:
        for sock in list(fd_to_socket.values()):
            try:
                sock.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()