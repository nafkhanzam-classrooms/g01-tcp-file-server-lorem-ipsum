[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/mRmkZGKe)
# Network Programming - Assignment G01

## Anggota Kelompok
|             Nama              |    NRP   | Kelas |
| ----------------------------- | -------- | ----- |
|Alfianz Rizqi Ilahi Loven Carry|5025241164|   C   |
|       Aqil Syafiq Dzaky       |5025241200|   C   |


## Daftar Isi

## Link Youtube (Unlisted)
Link ditaruh di bawah ini
```

```

## Penjelasan Program

### client.py

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

### server-thread.py

## Screenshot Hasil
