from jayhawk.dispatch import *
from socketserver import ThreadingMixIn, TCPServer
from signal import signal, SIGINT
from threading import Event

def on_interrupt(signum, frame):
	for server in servers: server.stop.set()
signal(SIGINT,on_interrupt)

class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    pass

servers = set()

def serve_directory(dir,server_address=("0.0.0.0",300),server_cls=ThreadedTCPServer,timeout_interval=0.5):
	handler = type("DirectoryServer",(FileBasedSpartanHandler,),{"root":dir})
	server = server_cls(server_address,handler)
	servers.add(server)
	server.stop = Event()
	server.timeout = timeout_interval
	while not server.stop.is_set(): server.handle_request()
	server.server_close()
	servers.remove(server)
