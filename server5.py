from socket import *
import socket
import threading
import logging
import time
import sys
from concurrent.futures import ProcessPoolExecutor


from file_protocol import  FileProtocol
fp = FileProtocol()


def ProcessTheClient(connection, address):
    buffer = ''
    while True:
        data = connection.recv(1024*1024)
        if data:
            buffer += data.decode()
            if "\r\n\r\n" in buffer:
                hasil = fp.proses_string(buffer.strip())
                hasil=hasil+"\r\n\r\n"
                connection.sendall(hasil.encode())
                break
        else:
            break
    connection.close()


class Server:
    def __init__(self,ipaddress='0.0.0.0',port=8889,workers=1):
        self.ipinfo=(ipaddress,port)
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.executor = ProcessPoolExecutor(max_workers=workers)
        
    def run(self):
        try:
            logging.warning(f"server berjalan di ip address {self.ipinfo}")
            self.my_socket.bind(self.ipinfo)
            self.my_socket.listen(1)
            
            while True:
                connection, client_address = self.my_socket.accept()
                logging.warning(f"connection from {client_address}")
                
                self.executor.submit(ProcessTheClient, connection, client_address)
                
        except KeyboardInterrupt:
            logging.warning("Server shutting down")
        except Exception as e:
            logging.error(f"Server error: {e}")
        finally:
            self.my_socket.close()
            self.executor.shutdown(wait=False)
            logging.warning("Server stopped")


def main():
    svr = Server(ipaddress='0.0.0.0',port=46670,workers=5)
    svr.run()


if __name__ == "__main__":
    main()

