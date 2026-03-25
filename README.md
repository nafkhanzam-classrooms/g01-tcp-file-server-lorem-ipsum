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
Merupakan variabel global, server_socket adalah placeholder nanti akan diganti saat ada client masuk. 

### server-poll.py

### server-thread.py

## Screenshot Hasil
