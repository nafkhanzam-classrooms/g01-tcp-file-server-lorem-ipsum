[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/mRmkZGKe)
# Network Programming - Assignment G01

## Anggota Kelompok
|             Nama              |    NRP   | Kelas |
| ----------------------------- | -------- | ----- |
|Alfianz Rizqi Ilahi Loven Carry|5025241164|   C   |
|       Aqil Syafiq Dzaky       |5025241200|   C   |


## Link Youtube (Unlisted)
Link ditaruh di bawah ini
```

```

## Penjelasan Program

### client.py

### server-sync.py

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

### server-poll.py

### server-thread.py

## Screenshot Hasil
