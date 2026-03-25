[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/mRmkZGKe)
# Network Programming - Assignment G01

## Anggota Kelompok
|             Nama              |    NRP   | Kelas |
| ----------------------------- | -------- | ----- |
|Alfianz Rizqi Ilahi Loven Carry|5025241164|   C   |
|       Aqil Syafiq Dzaky       |5025241200|   C   |


## Daftar Isi
- [Link Youtube](#link-youtube)
- [Penjelasan Program](#penjelasan-program)
    - [client.py](#clientpy)
    - [server-sync.py](#server-syncpy)
    - [server-select.py](#server-selectpy)
    - [server-poll.py](#server-pollpy)
    - [server-thread.py](#server-threadpy)
- [Screenshot Hasil](#screenshot-hasil) 

## Link Youtube (Unlisted)
[Link Youtube](https://youtu.be/pMjJsdSQTks)
```

```

## Penjelasan Program

### client.py

```
import socket
import struct
import threading
import os
import sys
```
Dipakai untuk import fungsi-fungsi yang ada di Python. socket dan struct ini utama buat komunikasi client-server karena client juga pakai framing yang sama kayak server. threading dipakai biar client bisa nerima pesan dari server sambil tetap bisa input dari user. os dipakai untuk urusan folder/file, dan sys dipakai kalau mau ambil host atau port dari argumen terminal.

```
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000
BUFFER_SIZE = 4096
DOWNLOAD_DIR = "client_downloads"
```
Merupakan konstanta awal. `SERVER_HOST` sebagai alamat server tujuan client connect, default-nya 127.0.0.1 (localhost / komputer sendiri). `SERVER_PORT` sebagai port tujuan server. `BUFFER_SIZE` sebagai ukuran buffer, walaupun di kode ini sebenarnya belum kepakai. `DOWNLOAD_DIR` merupakan nama folder tempat file hasil download disimpan di client.

```
def recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data
```
Fungsi recv_exact berfungsi untuk menerima tepat n byte data dari socket. fungsi akan menerima data sejumlah n bytes sampai terpenuhi : misal 4 byte dan n = 2, maka recv pertama akan dapat 2 byte, recv kedua akan dapat 1 byte, dan recv ketiga akan dapat sisanya (1 byte).

```
def send_msg(sock, data: bytes):
    header = struct.pack(">I", len(data))
    sock.sendall(header + data)
```
Fungsinya sebagai pengirim pesan dengan format `[4 byte panjang data] + [isi data]` (length-prefix framing). misal aku ngirim hello maka yg ke send sebenernya header (mewakili 5 karena len 5) + isi (hello).

```
def recv_msg(sock):
    header = recv_exact(sock, 4)
    if not header:
        return None
    length = struct.unpack(">I", header)[0]
    return recv_exact(sock, length)
```
Fungsinya baca data dengan format yang `[4 byte panjang data] + [isi data]` dan juga logika yang sama.

```
def send_text(sock, text: str):
    send_msg(sock, text.encode("utf-8"))
```
Fungsinya buat kirim string teks ke socket

```
def recv_text(sock):
    data = recv_msg(sock)
    if data is None:
        return None
    return data.decode("utf-8", errors="replace")
```
Fungsinya buat menerima text dari socket lalu mengubahnya dari bytes ke string (setelah proses recv_msg).

```
def handle_server_messages(sock):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    while True:
        try:
            msg_type = recv_text(sock)
            if msg_type is None:
                print("\n[INFO] Server disconnected.")
                break
```
Fungsi ini buat handle semua pesan yang dikirim dari server ke client. Di awal, client bikin folder download dulu kalau belum ada. Lalu masuk ke loop terus-terusan untuk nerima pesan dari server. Pertama ambil tipe pesan (`msg_type)`, kalau gagal (None) berarti server disconnect, jadi tampilkan info dan berhenti.

```
            if msg_type == "TEXT":
                text = recv_text(sock)
                if text is None:
                    print("\n[INFO] Server disconnected.")
                    break
                print(f"\n{text}")
```
Kalau tipe pesan "TEXT", berarti server ngirim teks biasa. Client ambil isi teksnya, kalau gagal berarti koneksi putus. Kalau berhasil, langsung ditampilkan ke terminal.

```
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
```
Kalau tipe pesan "FILE", berarti server ngirim file. Pertama ambil nama file, kalau gagal tampilkan error dan berhenti. Lanjut ambil isi file dalam bentuk bytes pakai recv_msg. Kalau gagal, tampilkan error dan berhenti. Nama file diamankan pakai `basename`, lalu digabung ke folder download. Setelah itu file disimpan ke disk.alau berhasil, tampilkan info ke user kalau file sudah berhasil di-download.

```
            else:
                print(f"\n[WARN] Unknown message type from server: {msg_type}")

        except Exception as e:
            print(f"\n[ERROR] Receiver thread stopped: {e}")
            break
```
Kalau tipe pesan tidak dikenal, tampilkan warning. Kalau ada error saat menerima pesan (misalnya koneksi putus tiba-tiba), tampilkan error lalu hentikan thread receiver.

```
def main():
    host = SERVER_HOST
    port = SERVER_PORT

    if len(sys.argv) >= 2:
        host = sys.argv[1]
    if len(sys.argv) >= 3:
        port = int(sys.argv[2])

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
```
Fungsi main/utama di sini. Bagian ini berfungsi untuk menyiapkan semuanya di sisi client. Pertama, host dan port diambil dari konstanta awal. Kalau saat run program user ngasih argumen tambahan di terminal, maka host dan port bisa diganti dari sys.argv. Setelah itu client bikin folder download kalau belum ada, lalu membuat socket client yang nanti dipakai untuk connect ke server.

```
    try:
        sock.connect((host, port))
        print(f"[CONNECTED] {host}:{port}")
        print("Commands:")
        print("  /list")
        print("  /upload <filename>")
        print("  /download <filename>")
        print("  /quit")
        print("  anything else = chat message")
```
Bagian ini dipakai untuk connect ke server sesuai host dan port yang dipilih. Kalau berhasil connect, tampilkan status [CONNECTED], lalu tampilkan daftar command yang bisa dipakai user, seperti /list, /upload, /download, /quit, dan selain itu dianggap sebagai chat biasa.

```
        receiver = threading.Thread(
            target=handle_server_messages,
            args=(sock,),
            daemon=True
        )
        receiver.start()
```
Setelah connect, client membuat thread baru bernama `receiver` yang tugasnya menjalankan fungsi `handle_server_messages`. Thread ini dipakai supaya client bisa tetap menerima pesan atau file dari server sambil user tetap bisa input command dari terminal. Setelah dibuat, thread langsung dijalankan dengan `start()`.

```
        while True:
            user_input = input("> ").strip()
            if not user_input:
                continue

            if user_input == "/quit":
                print("[INFO] Closing connection...")
                break

            elif user_input == "/list":
                send_text(sock, "LIST")
```
Lalu client masuk ke loop utama untuk baca input user terus-menerus. Input dibaca dari terminal, lalu `di-strip()` supaya spasi di awal/akhir dibuang. Kalau input kosong, loop lanjut lagi tanpa melakukan apa-apa. Kalau user ngetik `/quit`, berarti client mau keluar. Maka tampilkan info kalau koneksi ditutup, lalu keluar dari loop. Kalau user ngetik /list, client kirim command "LIST" ke server. Nanti server yang akan handle daftar file yang ada.

```
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
```
Kalau input diawali `/upload` , berarti user mau upload file. Input dipisah jadi command dan nama file. Kalau nama file tidak ada, tampilkan error penggunaan lalu lanjut lagi. Ambil path file dari input user. Kalau file itu tidak ditemukan di client, tampilkan error lalu lanjut lagi. Kalau file ada, ambil nama file saja pakai `basename`, lalu buka file dalam mode binary dan baca semua isinya ke `file_data`. Setelah itu client kirim command `"UPLOAD"` ke server, lalu kirim nama file, lalu kirim isi file. Kalau sudah terkirim, tampilkan info kalau upload sudah dikirim beserta ukuran filenya.

```
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
```
Kalau input diawali `/download` , berarti user mau download file dari server. Input dipisah dulu. Kalau nama file tidak ada, tampilkan error penggunaan. Kalau nama file ada, client kirim command `"DOWNLOAD"` ke server, lalu kirim nama file yang mau diunduh. Nanti file hasilnya akan diterima oleh thread `handle_server_messages`. Kalau input bukan command yang dikenal, maka dianggap sebagai chat biasa. Client kirim command `"CHAT"` lalu kirim isi pesan user ke server.

```
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
```
Kalau user menekan `Ctrl+C`, tampilkan info kalau client dihentikan oleh user. Kalau ada error lain, tampilkan pesan error-nya. Terakhir, di bagian `finally`, socket client akan ditutup supaya koneksi selesai dengan rapi. Setelah itu tampilkan info kalau client sudah ditutup.


### server-sync.py
```
import socket
import struct
import os
```
Dipakai untuk import module yang dibutuhkan.

- `socket` dipakai untuk komunikasi jaringan client-server.
- `struct` dipakai untuk membungkus panjang data ke format biner 4 byte.
- `os` dipakai untuk urusan file dan folder, misalnya bikin folder, cek file, gabung path, dan ambil nama file aman.

```
HOST = "0.0.0.0"
PORT = 5000
SERVER_FILES_DIR = "server_files"
```
Merupakan konstanta awal, HOST sebagai tempat server bind (pakai 0.0.0.0 agar bisa diakses oleh device lain tidak local). PORT sebagai port tempat server nge-listen. SERVER_FILES_DIR merupakan nama folder tempat file disimpan deserver

```
def recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data
```
Merupakan fungsi yang memastikan bahwa data diterima sekaligus (sesuai besar datanya)

```
def send_msg(sock, data: bytes):
    header = struct.pack(">I", len(data))
    sock.sendall(header + data)
```
Merupakan fungsi yang dipakai untuk mengirim data dengan mengirim informasi panjang data terlebih dahulu.

```
def recv_msg(sock):
    header = recv_exact(sock, 4)
    if not header:
        return None
    length = struct.unpack(">I", header)[0]
    return recv_exact(sock, length)
```
Merupakan fungsi yang diapakai untuk menerima data, dengan menerima informasi panjang terlebih dahulu.

```
def send_text(sock, text: str):
    send_msg(sock, text.encode("utf-8"))
```
Merupakan fungsi untuk mengirim pesan dalam bentuk text.

```
def recv_text(sock):
    data = recv_msg(sock)
    if data is None:
        return None
    return data.decode("utf-8", errors="replace")
```

Merupakan fungsi yang dipakai untuk menerima pesan dalam bentuk text.

```
def safe_send_text(sock, text: str):
    try:
        send_text(sock, "TEXT")
        send_text(sock, text)
        return True
    except Exception:
        return False
```
Merupakan fungsi yang memastikan agar server tidak crash saat pesan rusak/gagal dikirim.

```
def safe_send_file(sock, filename: str, file_data: bytes):
    try:
        send_text(sock, "FILE")
        send_text(sock, filename)
        send_msg(sock, file_data)
        return True
    except Exception:
        return False
```
Merupakan fungsi yang dipakai untuk mengirim suatu file ke client melalui server.

```
def handle_client(client_sock, client_addr):
    print(f"[CONNECTED] {client_addr}")
    safe_send_text(client_sock, f"[SERVER] Connected as {client_addr}")
```
Merupakan fungsi yang memastikan client sudah connect dengan cara mengirim log ke pemegang server bahwa client terkoneksi. Fungsi ini juga akan memberi pesan sambutan kepada client.

```
    try:
        while True:
            command = recv_text(client_sock)
            if command is None:
                break
```
Merupakan fungsi untuk melayani client, dimana server akan menungggu perintah dari client dan selama client awal belum terputus, client lain harus menunggu untuk dilayani.

```
            if command == "LIST":
                files = os.listdir(SERVER_FILES_DIR)
                if not files:
                    response = "[SERVER] No files available."
                else:
                    response = "[SERVER FILES]\n" + "\n".join(files)
                safe_send_text(client_sock, response)
```

Merupakan fungsi `if` yang mendeteksi command `LIST`. Fungsi ini digunakan saat client ingin meminta daftar file yang ada di `server_file`.

```
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
                print(f"[UPLOAD] {client_addr} -> {safe_name}")
```

Merupakan fungsi `if` yang mendeteksi command `UPLOAD`. Fungsi ini digunakan untuk menerima file dari client ke server. Lalu saat menerima file, path dari file tersebut akan dibersihkan dahulu dengan `os.path.basename` yang berfungsi untuk mengambil path terakhir dari file. File kemudian disimpan dengan menggunakan `with open`. Server mengirim pemberitahuan ke client bahwa file berhasil di upload, dan dicatat log di terminal.

```
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
```

Merupakan fungsi `if` yang mendeteksi command `DOWNLOAD`. Fungsi ini digunakan untuk mengirim file dari server ke client. Sebelu mengirim server akan cek file yang diminta client benar - benar ada atau tidak. Jika file ada, server akan membuka file dengna `with open` dan mengirim ke client dengan `safe_send_file`. Jika berhasil, server mengirim pesan sukses ke client dan mencatat log di terminal server.

```
            elif command == "CHAT":
                text = recv_text(client_sock)
                if text is None:
                    break

                msg = f"[{client_addr}] {text}"
                print(msg)

                safe_send_text(client_sock, msg)
```
merupakan fungsi `if` yang mendeteksi command `CHAT`. 	

Alurnya:

- Server terima isi chat dari client
- Pesan diformat dengan alamat client
- Server print pesan itu di terminal
- Lalu server kirim balik pesan itu ke client yang sedang aktif (karna server-sync maka client akan menerima pesannya sendiri).

```
            else:
                safe_send_text(client_sock, f"[SERVER] Unknown command: {command}")
```
Merupakan fungsi `if` yang mendeteksi jika client tidak menggunakan command yang valid. Server akan mengirim pesan ke client bahwa command tidak valid.

```
    except Exception as e:
        print(f"[ERROR] {client_addr}: {e}")
```
Merupakan fungsi yang akan mengirim pesan eror ke terminal server jika terdeteksi ada kesalahan selama proses. 


```
    finally:
        try:
            client_sock.close()
        except Exception:
            pass
        print(f"[DISCONNECTED] {client_addr}")
```
Merupakan fungsi yang akan digunakan saat client terputus dari server. Server akan menutup socket client dan akan mencata log client disconnect.

```
def main():
    os.makedirs(SERVER_FILES_DIR, exist_ok=True)
```
Merupakan fungsi `main()`. `os.makedirs` memastikan bahwa file `server_files`sudah ada. Jika belum maka akan otomatis dibuat.

```
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen(5)
```
Bagian ini dipakai untuk setup socket server:
`AF_INET` = IPv4.
`SOCK_STREAM` = TCP.
`SO_REUSEADDR` = supaya port bisa dipakai ulang lebih cepat setelah server restart.
`bind()` = menempelkan server ke host dan port.
`listen(5)` = mulai mendengarkan koneksi masuk.

```
    print(f"[LISTENING - SYNC] {HOST}:{PORT}")
```

Bagian ini akan jadi penanda bahwa `server-sync` sudah aktif dan menunggu client masuk.

```
    try:
        while True:
            client_sock, client_addr = server_sock.accept()
            handle_client(client_sock, client_addr)
```

Bagian ini adalah loop utama untuk menerima client. Bagian `handle_client` hanya akan melayani satu client dalam satu Waktu.

```
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")
```
Bagian ini akan menuliskan pesan shutdown saat server dimatikan secara manual.

```
    finally:
        server_sock.close()
```

bagian ini menutup socket server agar resurcenya bersih.

```
if __name__ == "__main__":
    main()
```
Bagian ini adalah pola standar python agar fungsi `main()` langsung dijalankan saat program di jalankan.



### server-select.py

```
import socket
import select
import struct
import os
```
Dipakai untuk import fungsi fungsi yang ada di python. Socket dan Select adalah utama dari server ini karena menggunakan metode select. Dan os digunakan untuk urusan pengubahan folder

```
HOST = "0.0.0.0"
PORT = 5000
SERVER_FILES_DIR = "server_files"
```
Merupakan konstanta awal, HOST sebagai tempat server bind (pakai 0.0.0.0 agar bisa diakses oleh device lain tidak local). PORT sebagai port tempat server nge-listen. SERVER_FILES_DIR merupakan nama folder tempat file disimpan diserver

```
server_socket = None
input_sockets = []
client_states = {}  # sock -> {"addr": ..., "stage": ..., "command": ..., "filename": ...}
```
Merupakan variabel global, server_socket adalah placeholder nanti sebagai penerima koneksi. input_socket dan client_state ini berguna untuk list saat nanti select terjadi.

```
def recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data
```
Fungsi recv_exact berfungsi untuk menerima tepat n byte data dari socket. fungsi akan menerima data sejumlah n bytes sampai terpenuhi : misal 4 byte dan n = 2, maka recv pertama akan dapat 2 byte, recv kedua akan dapat 1 byte, dan recv ketiga akan dapat sisanya (1 byte).

```
def send_msg(sock, data: bytes):
    header = struct.pack(">I", len(data))
    sock.sendall(header + data)
```
Fungsinya sebagai pengirim pesan dengan format `[4 byte panjang data] + [isi data]` (length-prefix framing). misal aku ngirim hello maka yg ke send sebenernya header (mewakili 5 karena len 5) + isi (hello).

```
def recv_msg(sock):
    header = recv_exact(sock, 4)
    if not header:
        return None
    length = struct.unpack(">I", header)[0]
    return recv_exact(sock, length)
```
Fungsinya baca data dengan format yang `[4 byte panjang data] + [isi data]` dan juga logika yang sama.

```
def send_text(sock, text: str):
    send_msg(sock, text.encode("utf-8"))
```
Fungsinya buat kirim string teks ke socket

```
def recv_text(sock):
    data = recv_msg(sock)
    if data is None:
        return None
    return data.decode("utf-8", errors="replace")
```
Fungsinya buat menerima text dari socket lalu mengubahnya dari bytes ke string (setelah proses recv_msg).

```
def safe_send_text(sock, text: str):
    try:
        send_text(sock, "TEXT")
        send_text(sock, text)
        return True
    except Exception:
        return False
```
Fungsinya buat ngirim text ke client dengan aman, caranya : pertama server akan mengirim text dengan "TEXT" untuk memberi tahu kalau file yang berikutnya berbentu teks, lalu kedua dia baru akan mengirimkan teks aslinya. Jika terjadi kegagalan maka return False.

```
def safe_send_file(sock, filename: str, file_data: bytes):
    try:
        send_text(sock, "FILE")
        send_text(sock, filename)
        send_msg(sock, file_data)
        return True
    except Exception:
        return False
```
Fungsinya buat ngirim File ke client dengan aman, caranya mirip dengan sebelumnya namun bedanya sebelum ngirim file asli dia akan ngirim text berupa Judul file.

```
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
```
Fungsi ini digunakan untuk ngehapus in jejak client (jika dia keluar atau /quit) caranya dia ambil alamat client, apus semua dari select, dan state client, lalu print dan broadcast kalo addr itu left the chat.

```
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
```
Buat ngirim pesan ke semua client yang terhubung. Caranya loop semua client, jika ok maka kirim teksnya, jika not ok (gagal) maka hapus clien (brati dia udah disconnect).

```
def handle_list(sock):
    files = os.listdir(SERVER_FILES_DIR)
    if not files:
        response = "[SERVER] No files available."
    else:
        response = "[SERVER FILES]\n" + "\n".join(files)
    safe_send_text(sock, response)
```
Fungsinya buat ngehandle fungsi /list. cara : ambil semua list di dir, kalo ga nemuin files kirim no files available, kalo nemuin kita kirim semua nama files tadi.

```
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
    broadcast(f"[SERVER] {state[`addr`]} uploaded file: {safe_name}", exclude_sock=sock)
    print(f"[UPLOAD] {state[`addr`]} -> {safe_name}")
```
Fungsinya buat ngehandle fungsi /upload client. pertama, server ambil info client dulu, lalu ambil data nama file yang dikirim client, jika gagal disconnect. Selanjutnya ambil data file yang dikirim client, jika gagal disconnect. Lalu masukkan file ke path sesuai nama (misal nama 123.txt, maka jadi server_files/123.txt). Lalu simpan ke disk, dan beri feedback ke uploader, kasih info juga ke client lain.

```
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
        print(f"[DOWNLOAD] {client_states[sock][`addr`]} <- {safe_name}")
    else:
        disconnect_client(sock)
```
Fungsinya buat ngehandle /download client, pertama ambil nama file yang ingin diunduh dari client. lalu buat path ke dir untuk persiapan unduh. Jika file tidak ditemukan di server, maka return teks file not found, jika ada baca file dari disk lalu kirim ke client. Kalau gagal kirim disconnect, kalo berhasil feedback.

```
def handle_chat(sock):
    text = recv_text(sock)
    if text is None:
        disconnect_client(sock)
        return

    msg = f"[{client_states[sock][`addr`]}] {text}"
    print(msg)
    broadcast(msg)
```
Fungsinya buat handle chat (misal client isi teks gtu), ambil teks yang dikirim client lalu tampilkan ke server dan semua client dengan format `[(ip, port)] isi pesan`.

```
def main():
    global server_socket

    os.makedirs(SERVER_FILES_DIR, exist_ok=True)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    input_sockets.append(server_socket)

    print(f"[LISTENING - SELECT] {HOST}:{PORT}")
```
Fungsi main/utama disini, bagian diatas berfungs untuk menyiapkan segalanya : folder penyimpanan file, socket server, aktifkan reuse address, bind ke host dan port, Server nge-listen, ngemasukin server socket ke list, lalu feedback status saat ini (LISTENING).

```
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

```
Bagian ini merupakan lanjutan main, loop (selama true), periksa semua socket dalam input_socket pakai read_ready. loop semua socket yg ready. kalo seocket yg ready server_socket (artinya ada client baru) maka accept client, masukkan ke input_socket lalu simpat state client. terakhir tambahkan log di server lalu tampilkan sambutan ke client baru (Broadcast kalau client baru joined the chat).

```
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
```
Lanjutan dari loop diatas, kalo yg diterima bukan server socket maka masuk ke command list (tinggal satu satu masukin misal /LIST maka langsung menuju handle_list, jika /UPLOAD maka ke handle upload dst. Jika tidak ada yg sesuai return Uknown Command, dan jika command ga ada/none maka disconnect.

```
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")

    finally:
        for sock in list(input_sockets):
            try:
                sock.close()
            except Exception:
                pass

```
Terakhir di main berfungsi untuk menghandle keyboard interupt (misal press ctrl+C) maka tampilkan shutting down. Lalu finally semua socket ditutup saat server disconnect 


### server-poll.py

```
import socket
import select
import struct
import os
```
Dipakai untuk import fungsi fungsi yang ada di python. Socket dan Select adalah utama dari server ini karena menggunakan metode select. Dan os digunakan untuk urusan pengubahan folder

```
HOST = "0.0.0.0"
PORT = 5000
SERVER_FILES_DIR = "server_files"
```
Merupakan konstanta awal, HOST sebagai tempat server bind (pakai 0.0.0.0 agar bisa diakses oleh device lain tidak local). PORT sebagai port tempat server nge-listen. SERVER_FILES_DIR merupakan nama folder tempat file disimpan diserver

```
server_socket = None
poll_obj = None
fd_to_socket = {}
client_addrs = {}
```
Merupakan variabel global, server_socket adalah placeholder nanti sebagai penerima koneksi. poll_obj sebagai objek utama untuk poll nati, dan fd_to_socket serta client_addrs adalah list untuk menjalankan fungsi poll nanti.

```
def recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data
```
Fungsi recv_exact berfungsi untuk menerima tepat n byte data dari socket. fungsi akan menerima data sejumlah n bytes sampai terpenuhi : misal 4 byte dan n = 2, maka recv pertama akan dapat 2 byte, recv kedua akan dapat 1 byte, dan recv ketiga akan dapat sisanya (1 byte).

```
def send_msg(sock, data: bytes):
    header = struct.pack(">I", len(data))
    sock.sendall(header + data)
```
Fungsinya sebagai pengirim pesan dengan format `[4 byte panjang data] + [isi data]` (length-prefix framing). misal aku ngirim hello maka yg ke send sebenernya header (mewakili 5 karena len 5) + isi (hello).

```
def recv_msg(sock):
    header = recv_exact(sock, 4)
    if not header:
        return None
    length = struct.unpack(">I", header)[0]
    return recv_exact(sock, length)
```
Fungsinya baca data dengan format yang `[4 byte panjang data] + [isi data]` dan juga logika yang sama.

```
def send_text(sock, text: str):
    send_msg(sock, text.encode("utf-8"))
```
Fungsinya buat kirim string teks ke socket

```
def recv_text(sock):
    data = recv_msg(sock)
    if data is None:
        return None
    return data.decode("utf-8", errors="replace")
```
Fungsinya buat menerima text dari socket lalu mengubahnya dari bytes ke string (setelah proses recv_msg).

```
def safe_send_text(sock, text: str):
    try:
        send_text(sock, "TEXT")
        send_text(sock, text)
        return True
    except Exception:
        return False
```
Fungsinya buat ngirim text ke client dengan aman, caranya : pertama server akan mengirim text dengan "TEXT" untuk memberi tahu kalau file yang berikutnya berbentu teks, lalu kedua dia baru akan mengirimkan teks aslinya. Jika terjadi kegagalan maka return False.

```
def safe_send_file(sock, filename: str, file_data: bytes):
    try:
        send_text(sock, "FILE")
        send_text(sock, filename)
        send_msg(sock, file_data)
        return True
    except Exception:
        return False
```
Fungsinya buat ngirim File ke client dengan aman, caranya mirip dengan sebelumnya namun bedanya sebelum ngirim file asli dia akan ngirim text berupa Judul file.

```
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
```
Berfungsi memutus client dari server, dan hapus dia dari poll, hapus data dari dictionary, lalu tutup socket. Pertama ambil fd (file desciptor) dari socket. lalu Ambil alamat client dari dictionary. lalu `poll_obj.unregister(fd)` agar poll tidak mengecek socket ini lagi (kita unregister). `del fd_to_socket[fd]` lalu hapus fd dari map, `del client_addrs[fd]` hapus alamat client dari client_addrs, `sock.close()` terakhir tutup socket. Kalau ternyata alamat client ada kasih feedback ip ini has left the chat (dia keluar pakai /quit atau disconnect).

```
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
```
Berfungsi untuk mengirim message ke semua client. Pertama `dead_fds = []` pasang list client yang ingin di kirim, lalu loop semuanya. Lewati server socket, dan kalo ok maka kirim pesannya, kalau not ok masukkan fd ke daftar client mati. `for fd in dead_fds:` terakhir, disconnect semua client yang mati.

```
def handle_list(sock):
    files = os.listdir(SERVER_FILES_DIR)
    if not files:
        response = "[SERVER] No files available."
    else:
        response = "[SERVER FILES]\n" + "\n".join(files)
    safe_send_text(sock, response)
```
Fungsinya buat ngehandle fungsi /list. cara : ambil semua list di dir, kalo ga nemuin files kirim no files available, kalo nemuin kita kirim semua nama files tadi.

```
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
```
Fungsinya buat nge-handle fungsi /upload client. Pertama, server ambil nama file yang dikirim client, jika gagal disconnect. Selanjutnya server ambil isi file yang dikirim client, jika gagal disconnect. Lalu nama file diamankan dan dimasukkan ke path tujuan (misal 123.txt, maka jadi server_files/123.txt). Setelah itu file disimpan ke disk, server memberi feedback ke uploader, lalu kasih info juga ke client lain

```
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
```
Fungsinya buat nge-handle /download client. Pertama server ambil nama file yang mau diunduh, lalu buat path ke folder server. Kalau file tidak ada, server kirim pesan file not found. Kalau ada, file dibaca dari disk lalu dikirim ke client. Kalau gagal kirim maka disconnect, kalau berhasil server mencatat download di terminal.

```
def handle_chat(sock):
    text = recv_text(sock)
    if text is None:
        disconnect_client(sock)
        return

    msg = f"[{client_addrs[sock.fileno()]}] {text}"
    print(msg)
    broadcast(msg)

```
Fungsinya buat handle chat client. Server ambil teks dari client, kalau gagal disconnect. Lalu pesan diformat jadi [(ip, port)] isi pesan, ditampilkan ke server dan dikirim ke semua client.

```
def main():
    global server_socket

    os.makedirs(SERVER_FILES_DIR, exist_ok=True)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    input_sockets.append(server_socket)

    print(f"[LISTENING - SELECT] {HOST}:{PORT}")
```
Fungsi main/utama di sini. Bagian ini berfungsi untuk menyiapkan semuanya: mulai dari bikin folder penyimpanan file (kalau belum ada), membuat socket server (TCP), mengaktifkan reuse address biar port bisa dipakai lagi, bind ke host dan port, lalu server mulai listen. Setelah itu server socket dimasukkan ke list input_sockets supaya bisa dipantau oleh select, dan terakhir kasih feedback status kalau server sudah siap (LISTENING).

```
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
```
Bagian ini merupakan lanjutan main, masuk ke loop (selama true). Server akan terus ngecek semua socket dalam input_sockets pakai select, lalu ambil socket yang ready (read_ready). Loop semua socket yang ready. Kalau socket yang ready adalah server_socket, artinya ada client baru yang connect. Maka server akan accept client tersebut, lalu socket client dimasukkan ke input_sockets, dan state client disimpan. Terakhir, server print log kalau ada client baru, kirim pesan sambutan ke client tersebut, lalu broadcast ke client lain kalau ada user baru join (kecuali ke client itu sendiri).

```
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
```
Lanjutan dari loop di atas. Kalau socket yang ready bukan server_socket, berarti itu client yang sedang mengirim data. Server akan ambil command dari client. Kalau gagal (None), berarti client putus langsung disconnect. Kalau ada command, server akan cek satu-satu: LIST, masuk ke handle_list, UPLOAD ke handle_upload, DOWNLOAD ke handle_download, CHAT ke handle_chat. Kalau command tidak dikenal, server akan kirim pesan "Unknown command" ke client.

```
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")

    finally:
        for sock in list(input_sockets):
            try:
                sock.close()
            except Exception:
                pass
```
Terakhir di main, bagian ini berfungsi untuk handle KeyboardInterrupt (misal tekan Ctrl+C), maka server akan print "Shutting down...". Lalu di bagian finally, semua socket akan ditutup supaya resource dilepas dan server berhenti dengan rapi.

### server-thread.py
```
import socket
import struct
import threading
import os
```
Dipakai untuk import module yang dibutuhkan.

- socket dipakai untuk komunikasi jaringan client-server.
- struct dipakai untuk membungkus panjang data ke format biner 4 byte.
- threading dipakai agar server bisa melayani banyak client sekaligus dengan thread.
- os dipakai untuk urusan file dan folder, misalnya bikin folder, cek file, gabung path, dan ambil nama file aman.


```
HOST = "0.0.0.0"
PORT = 5000
BUFFER_SIZE = 4096
SERVER_FILES_DIR = "server_files"
```
Merupakan konstanta awal, `HOST` sebagai tempat server bind (pakai 0.0.0.0 agar bisa diakses oleh device lain tidak local). `PORT` sebagai port tempat server nge-listen. `BUFFER_SIZE` merupakan ukuran buffer data. `SERVER_FILES_DIR` merupakan nama folder tempat file disimpan di server.


```
clients = []
clients_lock = threading.Lock()
```
Merupakan variabel global tambahan pada `server-thread`. `clients` digunakan untuk menyimpan daftar client yang sedang terhubung. `clients_lock` digunakan untuk mengunci akses ke clients agar aman saat banyak thread berjalan bersamaan.

```
def recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data
```

Merupakan fungsi yang memastikan bahwa data diterima sekaligus (sesuai besar datanya).

```
def send_msg(sock, data: bytes):
    header = struct.pack(">I", len(data))
    sock.sendall(header + data)
```
Merupakan fungsi yang dipakai untuk mengirim data dengan mengirim informasi panjang data terlebih dahulu.

```
def recv_msg(sock):
    header = recv_exact(sock, 4)
    if not header:
        return None
    length = struct.unpack(">I", header)[0]
    return recv_exact(sock, length)
```

Merupakan fungsi yang dipakai untuk menerima data, dengan menerima informasi panjang terlebih dahulu.

```
def send_text(sock, text: str):
    send_msg(sock, text.encode("utf-8"))
```
Merupakan fungsi untuk mengirim pesan dalam bentuk text.

```
def recv_text(sock):
    data = recv_msg(sock)
    if data is None:
        return None
    return data.decode("utf-8", errors="replace")
```
Merupakan fungsi yang dipakai untuk menerima pesan dalam bentuk text.

```
def safe_send_text(sock, text: str):
    try:
        send_text(sock, "TEXT")
        send_text(sock, text)
        return True
    except Exception:
        return False
```
Merupakan fungsi yang memastikan agar server tidak crash saat pesan rusak/gagal dikirim.


```
def safe_send_file(sock, filename: str, file_data: bytes):
    try:
        send_text(sock, "FILE")
        send_text(sock, filename)
        send_msg(sock, file_data)
        return True
    except Exception:
        return False
```
Merupakan fungsi yang dipakai untuk mengirim suatu file ke client melalui server.

```
def broadcast(message: str, exclude_sock=None):
    dead_clients = []
```
Merupakan fungsi tambahan pada `server-thread` yang digunakan untuk mengirim pesan ke semua client yang sedang terhubung. `dead_clients` dipakai untuk menampung client yang gagal dikirimi pesan.

```
    with clients_lock:
        current_clients = list(clients)
```
Bagian ini digunakan untuk menyalin daftar client yang sedang aktif. `clients_lock` digunakan agar data clients tetap aman saat diakses banyak thread.

```
    for client_sock, client_addr in current_clients:
        if client_sock == exclude_sock:
            continue
        ok = safe_send_text(client_sock, message)
        if not ok:
            dead_clients.append((client_sock, client_addr))
```
Bagian ini digunakan untuk mengirim pesan ke semua client yang aktif. Jika `client_sock` sama dengan `exclude_sock`, maka client tersebut dilewati. Jika pengiriman gagal, client akan dimasukkan ke daftar `dead_clients`.

```
    if dead_clients:
        with clients_lock:
            for dc in dead_clients:
                if dc in clients:
                    clients.remove(dc)
                try:
                    dc[0].close()
                except Exception:
                    pass
```
Bagian ini digunakan untuk membersihkan client yang sudah mati atau gagal menerima pesan. Client tersebut akan dihapus dari daftar `clients` lalu socket-nya ditutup.

```
def handle_client(client_sock, client_addr):
    print(f"[CONNECTED] {client_addr}")
```
Merupakan fungsi yang akan dijalankan untuk setiap client yang connect. Saat client masuk, server akan mencatat log bahwa client tersebut sudah terhubung.

```
    with clients_lock:
        clients.append((client_sock, client_addr))
```
Bagian ini digunakan untuk menambahkan client yang baru masuk ke daftar `clients`. Karena daftar ini dipakai bersama oleh banyak thread, maka aksesnya harus dikunci dengan `clients_lock`.

```
    safe_send_text(client_sock, f"[SERVER] Connected as {client_addr}")
    broadcast(f"[SERVER] {client_addr} joined the chat.", exclude_sock=client_sock)
```
Fungsi ini juga akan memberi pesan sambutan kepada client yang baru masuk. Setelah itu server akan mengirim pesan broadcast ke client lain bahwa ada client baru yang join ke chat.

```
    try:
        while True:
            command = recv_text(client_sock)
            if command is None:
                break
```
Merupakan fungsi untuk melayani client, dimana server akan terus menunggu perintah dari client. Karena ini `server-thread`, setiap client ditangani di thread masing-masing sehingga banyak client bisa dilayani dalam waktu bersamaan.


```
            if command == "LIST":
                files = os.listdir(SERVER_FILES_DIR)
                if not files:
                    response = "[SERVER] No files available."
                else:
                    response = "[SERVER FILES]\n" + "\n".join(files)
                safe_send_text(client_sock, response)
```
Merupakan fungsi `if` yang mendeteksi command `LIST`. Fungsi ini digunakan saat client ingin meminta daftar file yang ada di `server_files`.

```
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
```
Merupakan fungsi `if` yang mendeteksi command `UPLOAD`. Fungsi ini digunakan untuk menerima file dari client ke server. Saat menerima file, path dari file tersebut akan dibersihkan dahulu dengan `os.path.basename` yang berfungsi untuk mengambil path terakhir dari file. File kemudian disimpan dengan menggunakan with open. Server mengirim pemberitahuan ke client bahwa file berhasil di upload, lalu server juga melakukan broadcast ke client lain bahwa ada file baru yang diupload. Setelah itu dicatat log di terminal.

```
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
```

Merupakan fungsi `if` yang mendeteksi command `DOWNLOAD`. Fungsi ini digunakan untuk mengirim file dari server ke client. Sebelum mengirim server akan cek file yang diminta client benar-benar ada atau tidak. Jika file ada, server akan membuka file dengan `with open` lalu mengirim ke client dengan `safe_send_file`. Jika berhasil, server mencatat log di terminal server.


```
            elif command == "CHAT":
                text = recv_text(client_sock)
                if text is None:
                    break

                msg = f"[{client_addr}] {text}"
                print(msg)
                broadcast(msg)
```
Merupakan fungsi `if` yang mendeteksi command `CHAT`.

Alurnya:
- Server terima isi chat dari client
- Pesan diformat dengan alamat client
- Server print pesan itu di terminal
- Lalu server mengirim pesan tersebut ke semua client yang sedang aktif dengan broadcast

```
            else:
                safe_send_text(client_sock, f"[SERVER] Unknown command: {command}")
```

Merupakan fungsi `if` yang mendeteksi jika client tidak menggunakan command yang valid. Server akan mengirim pesan ke client bahwa command tidak valid.

```
    except Exception as e:
        print(f"[ERROR] {client_addr}: {e}")
```

Merupakan fungsi yang akan mengirim pesan error ke terminal server jika terdeteksi ada kesalahan selama proses.

```
    finally:
        with clients_lock:
            if (client_sock, client_addr) in clients:
                clients.remove((client_sock, client_addr))
```
Bagian ini digunakan saat client terputus dari server. Client yang terputus akan dihapus dari daftar clients agar tidak dianggap masih aktif.

```
        try:
            client_sock.close()
        except Exception:
            pass
```
Bagian ini akan menutup socket client agar resource koneksi dibersihkan.

```
        broadcast(f"[SERVER] {client_addr} left the chat.")
        print(f"[DISCONNECTED] {client_addr}")
```
Setelah client keluar, server akan mengirim broadcast ke client lain bahwa client tersebut keluar dari chat. Lalu server juga akan mencatat log disconnect di terminal.

```
def main():
    os.makedirs(SERVER_FILES_DIR, exist_ok=True)
```
Merupakan fungsi `main()`. `os.makedirs` memastikan bahwa folder `server_files` sudah ada. Jika belum maka akan otomatis dibuat.

```
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen(5)
```

Bagian ini dipakai untuk setup socket server:
`AF_INET` = IPv4.
`SOCK_STREAM` = TCP.
`SO_REUSEADDR` = supaya port bisa dipakai ulang lebih cepat setelah server restart.
`bind()` = menempelkan server ke host dan port.
`listen(5)` = mulai mendengarkan koneksi masuk.

```
    print(f"[LISTENING] {HOST}:{PORT}")
```

Bagian ini akan jadi penanda bahwa `server-thread` sudah aktif dan menunggu client masuk.

```
    try:
        while True:
            client_sock, client_addr = server_sock.accept()
            t = threading.Thread(
                target=handle_client,
                args=(client_sock, client_addr),
                daemon=True
            )
            t.start()
```
Bagian ini adalah loop utama untuk menerima client. Saat ada client masuk, server akan membuat thread baru dengan `threading.Thread` lalu menjalankan `handle_client`. Karena itulah `server-thread` bisa melayani banyak client dalam satu waktu.

```
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")
```
Bagian ini akan menuliskan pesan shutdown saat server dimatikan secara manual.

```
    finally:
        server_sock.close()
```
Bagian ini menutup socket server agar resource-nya bersih.

```
if __name__ == "__main__":
    main()
```
Bagian ini adalah pola standar python agar fungsi `main()` langsung dijalankan saat program dijalankan.

## Screenshot Hasil

<img width="1920" height="658" alt="Screenshot 2026-03-25 235217" src="https://github.com/user-attachments/assets/1bb26b84-4ff8-453c-88d8-08442e3a4981" />
<img width="1888" height="586" alt="Screenshot 2026-03-25 235709" src="https://github.com/user-attachments/assets/9800d7bf-8f44-4f0a-b234-1d1a985485e8" />
<img width="1920" height="504" alt="Screenshot 2026-03-25 235230" src="https://github.com/user-attachments/assets/bec70973-3680-435b-b626-3e37724292fc" />

