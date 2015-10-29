import socket
import threading

class ChatRoom(object):
    def __init__(self):
        self.cv = threading.Condition()
        self.pending = []
        self.clients = {}
        threading.Thread(target=self.run_room).start()
    
    def _critical_section(f):
        def inner(self, *args, **kwargs):
            self.cv.acquire()
            try: 
                rval = f(self, *args, **kwargs)
                self.cv.notify()
            finally:
                self.cv.release()
            return rval
        return inner

    def run_room(self):
        self.cv.acquire()
        while 1:
            self.cv.wait()
            for name in self.clients.keys():
                try:
                    for mesg in self.pending:
                        self.clients[name].sendall(mesg)
                except:
                    del self.clients[name]
            self.pending[:] = []

    @_critical_section
    def add_client(self, name, client):
        self.clients[name] = client
        client.sendall('Members: {}\n'.format(', '.join(self.clients.keys())))
        self.pending.append(name + ' has joined\n')
    
    @_critical_section
    def enqueue_message(self, mesg):
        self.pending.append(mesg)


class ChatServer(object):
    def __init__(self, host, port):
        self.rooms = {}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host,port))
        s.listen(1)
        while 1:
            conn, addr = s.accept()
            t = threading.Thread(target=self.serve_client, args=(conn,))
            t.daemon = True
            t.start()
    
    def serve_client(self, conn):
        try:
            conn.sendall("Enter your name: ")
            cname = conn.recv(1024).rstrip()
            conn.sendall("Rooms: {}\n".format(', '.join(self.rooms.keys())))
            conn.sendall("Name a Room to join/create: ")
            roomname = conn.recv(1024).rstrip()

            if roomname not in self.rooms.keys():
                self.rooms[roomname] = ChatRoom()
            room = self.rooms[roomname]
            room.add_client(cname, conn)
        except:
            return

        while 1:
            mesg = conn.recv(4096)
            if not mesg:  
                room.enqueue_message(cname + ' has left\n')
                break
            room.enqueue_message(cname + ': ' + mesg.rstrip() + '\n')


if __name__ == "__main__":
    print 'Starting Server...'
    ChatServer('127.0.0.1', 8060)
