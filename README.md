# Progjar Stress Test
Fadhl Akmal Madany - 5025221028

Progjar C

## Summary
- `files` - File sample untuk testing. 
- `file_client_cli_stress_test.py` - Script utama stress test.
- `file_protocol.py` - Parsing request masuk dan mengarahkannya ke fungsi yang sesuai.
- `file_interface.py` - Implementasi operasi file (list, get, upload, hapus).
- `file_server_thread_pool.py` - Implementasi thread-based dari file server.
- `file_server_process_pool.py` - Implementasi process-based dari file server.
- `generate_files.py` - Utility untuk generate file stress test (10MB, 50MB, 100MB).
- `PROTOKOL.txt` - Dokumentasi protokol komunikasi client-server.
- `server1.py` hingga `server6.py` - Kombinasi server dengan konfigurasi berbeda. Server 1-3 didasari `file_server_thread_pool.py`, server 4-6 didasari `file_server_process_pool.py`.
- `stress-test-eda.ipynb` - Script untuk analisis data hasil stress test.

## How to run
### Generate Test Files
```bash
python3 generate_files.py
```

### Run Server
```bash
# Terminal 1
python3 server1.py

# Terminal 2
python3 server2.py

# Terminal 3
python3 server3.py

# Terminal 4
python3 server4.py

# Terminal 5
python3 server5.py

# Terminal 6
python3 server6.py
```

### Run Stress Test
```bash
python3 file_client_cli_stress_test.py
```

atau target server

```bash
# target server 1-3
python3 file_client_cli_stress_test.py --server-type thread
```

```bash
# target server 4-6
python3 file_client_cli_stress_test.py --server-type process
```
