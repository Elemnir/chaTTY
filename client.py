import argparse, socket, sys, threading

def writer(conn):
    for line in conn.makefile():
        sys.stdout.write(line)

def reader(conn):
    line = sys.stdin.readline()
    while line:
        conn.sendall(line)
        line = sys.stdin.readline()

def client(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))
    t = threading.Thread(target=reader, args=(s,))
    t.daemon = True
    t.start()
    writer(s)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host")
    parser.add_argument("port", type=int)
    args = parser.parse_args()
    client(args.host, args.port)
