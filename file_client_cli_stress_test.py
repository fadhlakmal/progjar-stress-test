import argparse
import socket
import json
import base64
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor

server_address=('0.0.0.0',7777)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        logging.warning(f"sending message ")
        sock.sendall(command_str.encode())
        # Look for the response, waiting until socket is done (no more data)
        data_received="" #empty string
        while True:
            #socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
            data = sock.recv(1024*1024)
            if data:
                #data is not empty, concat with previous content
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                # no more data, stop the process by break
                break
        # at this point, data_received (string) will contain all data coming from the socket
        # to be able to use the data_received as a dict, need to load it using json.loads()
        hasil = json.loads(data_received)
        logging.warning("data received from server:")
        return hasil
    except:
        logging.warning("error during data receiving")
        return False


def remote_list():
    command_str=f"LIST" +"\r\n\r\n"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        return True
    else:
        print("Gagal")
        return False

def remote_get(filename=""):
    command_str=f"GET {filename}" +"\r\n\r\n"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        #proses file dalam bentuk base64 ke bentuk bytes
        namafile= hasil['data_namafile']
        isifile = base64.b64decode(hasil['data_file'])
        fp = open(namafile,'wb+')
        fp.write(isifile)
        fp.close()
        return True
    else:
        print("Gagal")
        return False

def remote_delete(filename=""):
    command_str=f"HAPUS {filename}" +"\r\n\r\n"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        return True
    else:
        print("Gagal")
        return False

def remote_upload(filename=""):
    try:
        with open(f"{filename}", 'rb') as fp:
            isifile = base64.b64encode(fp.read()).decode()
        
        command_str = f"UPLOAD {filename} {isifile}"+"\r\n\r\n"
        hasil = send_command(command_str)
        if hasil['status'] == 'OK':
            return True
        else:
            print("Gagal", hasil['data'])
            return False
    except Exception as e:
        print(hasil)
        return False


def stress_test(server_type='thread'):
    workers = [1, 5, 20]
    files = ['file_10mb.dat', 'file_50mb.dat', 'file_100mb.dat']
    operations = ['upload', 'download']
    
    server_ports = {
        'thread': {
            1: 46666,  # server1.py - 1 worke
            5: 46667,  # server2.py - 5 worker
            50: 46668  # server3.py - 50 worker
        },
        'process': {
            1: 46669,  # server4.py - 1 worker
            5: 46670,  # server5.py - 5 worker
            50: 46671  # server6.py - worker
        }
    }
    
    results = []
    
    print(f"{'No':4} | {'Operation':8} | {'Volume':10} | {'Client Workers':14} | {'Server Type':11} | {'Server Workers':14} | {'Time (s)':10} | {'Throughput (B/s)':15} | {'Success':8} | {'Failed':8}")
    print("-" * 140)
    
    count = 1
    for operation in operations:
        for file in files:
            file_size_mb = int(file.split('_')[1].split('mb')[0])
            file_size = file_size_mb * 1024 * 1024

            for client_worker_count in workers:
                for server_worker_count in [1, 5, 50]:
                    print(f"Running test: {operation} of {file} with {client_worker_count} client workers and {server_worker_count} {server_type} server workers")
                    
                    global server_address
                    
                    try:
                        port = server_ports[server_type][server_worker_count]
                        server_address = ('localhost', port)
                    except KeyError:
                        print(f"Invalid server type or worker count: {server_type}, {server_worker_count}")
                        continue
                    
                    successes = 0
                    failures = 0
                    
                    catat_awal = time.perf_counter()
                    
                    with ThreadPoolExecutor(max_workers=client_worker_count) as executor:
                        futures = []
                        
                        for i in range(client_worker_count):
                            if operation == 'upload':
                                futures.append(executor.submit(remote_upload, file))
                            else:  # download
                                futures.append(executor.submit(remote_get, file))
                        
                        for future in futures:
                            try:
                                if future.result():
                                    successes += 1
                                else:
                                    failures += 1
                            except Exception as e:
                                print(f"Error in worker: {str(e)}")
                                failures += 1
                    
                    catat_akhir = time.perf_counter()
                    total_time = catat_akhir - catat_awal
                    
                    throughput = (file_size * successes) / total_time if total_time > 0 else 0
                    
                    result = {
                        'No': count,
                        'Operation': operation,
                        'Volume': file_size_mb,
                        'Client Workers': client_worker_count,
                        'Server Type': server_type,
                        'Server Workers': server_worker_count,
                        'Total Time': total_time,
                        'Throughput': throughput,
                        'Success': successes,
                        'Failed': failures
                    }
                    results.append(result)
                    
                    print(f"{count:4} | {operation:8} | {file:10} | {client_worker_count:14} | {server_type:11} | {server_worker_count:14} | {total_time:10.2f} | {throughput:15.2f} | {successes:8} | {failures:8}")
                    
                    count += 1
                    time.sleep(2)
    
    return results


if __name__=='__main__':
    logging.basicConfig(level=logging.ERROR)
    
    parser = argparse.ArgumentParser(description='File transfer stress test client')
    parser.add_argument('--server-type', type=str, choices=['thread', 'process'], default='thread', 
                       help='Type of server (thread or process)')
    args = parser.parse_args()
    
    results = stress_test(server_type=args.server_type)
    
    import csv
    with open('stress_test_results.csv', 'a', newline='') as csvfile:
        fieldnames = ['No', 'Operation', 'Volume', 'Client Workers', 
                     'Server Type', 'Server Workers', 'Total Time', 'Throughput', 'Success', 'Failed']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    
    print("Stress test completed. Results saved to stress_test_results.csv")