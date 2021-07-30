from socketserver import StreamRequestHandler

class SpartanRequestDispatcher(StreamRequestHandler):
	def handle(self):
		"""Handles incoming connections. To handle Spartan requests, see SpartanRequestDispatcher.handle_request."""
		try:
			request_line = self.rfile.readline().decode("ascii")
			assert request_line.endswith("\r\n"), "Request line must end in CRLF"
			parts = request_line.strip().split()
			assert len(parts)==3, "Invalid request line"
			host, path, content_length = parts
			if (content_length:=int(content_length))>0:
				data = self.rfile.read(content_length)
			else:
				data = b''
			self.handle_request(host,path,data)
		except AssertionError as e:
			self.response_code(4,e.args[0])
	def handle_request(self,host,path,data=b''):
		"""Handles incoming Spartan requests. Use this to handle requests as they come in."""
		self.response_code(5,"Request handler not implemented")
	def response_code(self,code,argument):
		"""Writes a response code with argument. (MIME type for 2, absolute path for 3, error messages for 4 and 5)"""
		response_code = f"{code!s} {argument}\r\n"
		self.wfile.write(bytes(response_code,"ascii"))

import os.path, shutil, mimetypes
from urllib.parse import unquote

class FileBasedSpartanHandler(SpartanRequestDispatcher):
	OVERRIDE_MIMETYPES = {
		".gmi": "text/gemini"
	}
	def handle_request(self,host,path,data=b''):
		"""Serve file at root/host/path. Includes methods for avoiding path traversal."""
		if data:
			self.response_code(4,"Uploads are not accepted.")
			return
		if not hasattr(self,"root"):
			self.response_code(5,"Server is unable to handle requests at this time due to misconfiguration.")
			return
		self.root = os.path.abspath(self.root)
		if not (prefix:=os.path.abspath(os.path.join(self.root,host))).startswith(self.root):
			self.response_code(4,"Cowardly refusing to serve file outside of root.")
			return
		if not (filepath:=os.path.abspath(os.path.join(prefix,unquote(path.lstrip("/"))))).startswith(prefix):
			self.response_code(4,"Cowardly refusing to serve file outside of root.")
			return
		if not os.path.exists(filepath):
			self.response_code(4,"Not Found")
			return
		if os.path.isdir(filepath):
			if os.path.exists(os.path.join(filepath,"index.gmi")):
				filepath = os.path.join(filepath,"index.gmi")
			else:
				self.response_code(5,"Cowardly refusing to generate folder listing.")
				return
		ext = os.path.splitext(filepath)[1]
		mimetype = mimetypes.guess_type(filepath,False)
		if ext in self.OVERRIDE_MIMETYPES:
			mimetype = self.OVERRIDE_MIMETYPES[ext]
		mimetype = mimetype or "application/octet-stream"
		with open(filepath,"rb") as f:
			self.response_code(2,mimetype)
			shutil.copyfileobj(f,self.wfile)
