import socket
import time
import os
import sys

def wait_for_db():
    host = "db"
    port = 5432
    print(f"Aguardando banco de dados em {host}:{port}...")
    while True:
        try:
            with socket.create_connection((host, port), timeout=1):
                print("Banco de dados está pronto!")
                break
        except (socket.timeout, ConnectionRefusedError):
            print("Banco ainda não está pronto, aguardando 1 segundo...")
            time.sleep(1)

if __name__ == "__main__":
    wait_for_db()
