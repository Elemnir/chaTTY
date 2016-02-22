import argparse, shlex, socket, subprocess, threading

def connection(conn, shprog):
    f = conn.makefile()
    subprocess.call(shlex.split(shprog), stdin=f, stdout=f, stderr=f)

def serve(host, port, shprog):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host,port))
    s.listen(1)
    while 1:
        conn, addr = s.accept()
        t = threading.Thread(target=connection, args=(conn, shprog))
        t.daemon = True
        t.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int)
    parser.add_argument("cmd")
    args=parser.parse_args()
    serve("0.0.0.0", args.port, args.cmd)
