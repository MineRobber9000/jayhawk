import sys
sys.path.append("../")
import jayhawk

class EchoServer(jayhawk.SpartanRequestDispatcher):
	"""An echo server for Spartan. Takes input and spits it back out."""
	def handle_request(self,host,path,data=b''):
		self.response_code(2,"text/gemini")
		if data:
			self.wfile.write(bytes(f"You sent {data!r}.\r\n","utf-8"))
		self.wfile.write(bytes("=: / Type in some text and I'll send it back to you.\r\n","utf-8"))

if __name__=="__main__":
	# Install jayhawk's signal handler
	jayhawk.install_signal_handler()
	# Tell jayhawk to serve our echo server on port 3000
	jayhawk.serve(EchoServer,("localhost",3000))
