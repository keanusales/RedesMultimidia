from ServerWorker import ServerWorker
from argparse import ArgumentParser
import socket

class Server:
	def __init__(self):
		parser = ArgumentParser()
		parser.add_argument("server_port", nargs = 1,
			type = int, help = "Desired server port number")
		self.args = parser.parse_args()
		self.main()

	def main(self):
		rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		rtspSocket.bind(('', self.args.server_port))
		rtspSocket.listen(5)        

		# Receive client info (address,port) through RTSP/TCP session
		while True:
			clientInfo = {}
			clientInfo['rtspSocket'] = rtspSocket.accept()
			ServerWorker(clientInfo).run()		

if __name__ == "__main__": Server()