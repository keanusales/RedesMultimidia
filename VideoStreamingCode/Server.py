import sys, socket

from ServerWorker import ServerWorker

class Server:
	def __init__(self):
		try:
			self.SERVER_PORT = int(sys.argv[1])
		except:
			print("[Usage: Server.py Server_port]\n")

		self.main()

	def main(self):
		rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		rtspSocket.bind(('localhost', self.SERVER_PORT))
		rtspSocket.listen(5)

		addr, port = rtspSocket.getsockname()
		print(f"### SERVIDOR INICIALIZADO EM {f"{addr}:{port}"} ###\n")
		# Receive client info (address,port) through RTSP/TCP session
		while True:
			clientInfo = {}
			client_socket, client_addr = rtspSocket.accept()
			print(f"Cliente conectado: {client_socket}-{client_addr}")
			clientInfo['rtspSocket'] = (client_socket, client_addr)
			ServerWorker(clientInfo).run()		

if __name__ == "__main__": Server()