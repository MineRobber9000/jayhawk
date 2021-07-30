from jayhawk.dispatch import *
from socketserver import ThreadingTCPServer
from signal import signal, SIGINT
from threading import Event

def on_interrupt(signum, frame):
	"""Signal handler. Stops all servers."""
	print("on_interrupt")
	for server in servers: server.__shutdown_request = True

def install_signal_handler():
	"""Installs on_interrupt as the SIGINT handler."""
	signal(SIGINT,on_interrupt)

# A list of servers that on_interrupt is responsible for.
servers = set()

def serve(handler,server_address=("0.0.0.0",300),server_cls=ThreadingTCPServer,timeout_interval=0.5,ret=False):
	"""Serves SpartanRequestDispatcher subclass handler at server_address, using server_cls with a timeout of timeout_interval.
           If you want to handle the running of the server yourself, pass ret=True."""
	server = server_cls(server_address,handler)
	servers.add(server)
	server.timeout = timeout_interval
	if ret:
		# For convenience sake, monkey-patch in a non-blocking shutdown() and add a join() method for if you need it.
		def __shutdown():
			server.__shutdown_request=True
		server.shutdown = __shutdown
		def __join():
			server.__is_shut_down.wait()
		server.join = __join
		return server
	else:
		server.serve_forever()

def serve_directory(dir,server_address=("0.0.0.0",300),server_cls=ThreadedTCPServer,timeout_interval=0.5,ret=False):
	"""Convenience function. Makes a subclass of FileBasedSpartanHandler with the root attribute set to dir, and passes it to serve."""
	handler = type("DirectoryServer",(FileBasedSpartanHandler,),{"root":dir})
	return serve(handler,server_address,server_cls,timeout_interval,ret)
