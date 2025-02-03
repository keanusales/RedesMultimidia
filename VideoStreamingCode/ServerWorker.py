from threading import Thread, Event
from random import randint
import socket

from debugpy.launcher.debuggee import describe

from VideoStream import VideoStream
from RtpPacket import RtpPacket

class ServerWorker:
	SETUP = "SETUP"
	PLAY = "PLAY"
	PAUSE = "PAUSE"
	TEARDOWN = "TEARDOWN"
	DESCRIBE = "DESCRIBE"
	
	INIT = 0
	READY = 1
	PLAYING = 2
	state = INIT

	OK_200 = 0
	FILE_NOT_FOUND_404 = 1
	CON_ERR_500 = 2
	NOT_VALID_STATE = 455

	RESOURCES_PATH = "./resources/"

	clientInfo = {}

	def __init__(self, clientInfo: dict):
		self.clientInfo = clientInfo
		
	def run(self):
		Thread(target = self.recvRtspRequest).start()
	
	def recvRtspRequest(self):
		"""Receive RTSP request from the client."""
		connSocket = self.clientInfo["rtspSocket"][0]
		while True:            
			data = connSocket.recv(256)
			if data:
				strData = bytes.decode(data)
				print("Data received:\n" + strData)
				self.processRtspRequest(strData)

	def processRtspRequest(self, data: str):
		"""Process RTSP request sent from the client."""
		# Get the request type
		request = data.split("\n")
		line1 = request[0].split(" ")
		requestType = line1[0]
		
		# Get the media file name
		filename = line1[1]
		
		# Get the RTSP sequence number 
		seq = request[1].split(" ")
		
		# Process SETUP request
		if requestType == self.SETUP:
			if self.state == self.INIT:
				# Update state
				print("processing SETUP\n")
				
				try:
					self.clientInfo["videoStream"] = VideoStream(self.RESOURCES_PATH + filename)
					self.state = self.READY
				except IOError as e:
					print("File not found: %s" % e)
					self.replyRtsp(self.FILE_NOT_FOUND_404, seq[1])
				
				# Generate a randomized RTSP session ID
				self.clientInfo["session"] = randint(100000, 999999)
				
				# Send RTSP reply
				self.replyRtsp(self.OK_200, seq[1])
				
				# Get the RTP/UDP port from the last line
				self.clientInfo["rtpPort"] = request[2].split(" ")[3]
		
		# Process PLAY request 		
		elif requestType == self.PLAY:
			if self.state == self.READY:
				print("processing PLAY\n")
				self.state = self.PLAYING
				
				# Create a new socket for RTP/UDP
				self.clientInfo["rtpSocket"] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				
				self.replyRtsp(self.OK_200, seq[1])
				
				# Create a new thread and start sending RTP packets
				self.clientInfo["event"] = Event()
				self.clientInfo["worker"] = Thread(target = self.sendRtp) 
				self.clientInfo["worker"].start()
		
		# Process PAUSE request
		elif requestType == self.PAUSE:
			if self.state == self.PLAYING:
				print("processing PAUSE\n")
				self.state = self.READY
				
				self.clientInfo["event"].set()
			
				self.replyRtsp(self.OK_200, seq[1])
		
		# Process TEARDOWN request
		elif requestType == self.TEARDOWN:
			print("processing TEARDOWN\n")

			if "event" in self.clientInfo:
				self.clientInfo["event"].set()
			
			self.replyRtsp(self.OK_200, seq[1])
			
			# Close the RTP socket
			if "rtpSocket" in self.clientInfo:
				self.clientInfo["rtpSocket"].close()

		elif requestType == self.DESCRIBE:
			print("processing DESCRIBE\n")
			if self.state == self.INIT:
				self.replyRtsp(self.NOT_VALID_STATE, seq[1])
			else:
				self.replyRtsp(self.OK_200, seq[1], describe=True)
			
	def sendRtp(self):
		"""Send RTP packets over UDP."""
		while True:
			self.clientInfo["event"].wait(0.05) 
			
			# Stop sending if request is PAUSE or TEARDOWN
			if self.clientInfo["event"].isSet(): 
				break 
				
			data = self.clientInfo["videoStream"].nextFrame()
			if data: 
				frameNumber = self.clientInfo["videoStream"].frameNbr()
				try:
					address = self.clientInfo["rtspSocket"][1][0]
					port = int(self.clientInfo["rtpPort"])
					self.clientInfo["rtpSocket"].sendto(self.makeRtp(data, frameNumber), (address,port))
				except:
					print("Connection Error")

	def makeRtp(self, payload: bytes, frameNbr: int):
		"""RTP-packetize the video data."""
		version = 2
		padding = 0
		extension = 0
		cc = 0
		marker = 0
		pt = 26 # MJPEG type
		seqnum = frameNbr
		ssrc = 0 
		
		rtpPacket = RtpPacket()
		
		rtpPacket.encode(version, padding, extension, cc, seqnum, marker, pt, ssrc, payload)
		
		return rtpPacket.getPacket()

	def replyRtsp(self, code: int, seq, describe=False):
		"""Send RTSP reply to the client."""
		if code == self.OK_200:
			reply = f"RTSP/1.0 200 OK\nCSeq: {seq}\nSession: {self.clientInfo['session']}"
			if describe:
				sdp = f"v=0\n" \
					  f"s=RTSP Session\n" \
					  f"m=video {self.clientInfo['rtpPort']} RTP/AVP 26\n" \
					  f"c=IN IP4 {self.clientInfo['rtspSocket'][1][0]}\n" \
					  f"t=0 0\n" \
					  f"a=eTag:{self.clientInfo['session']}\n"
				reply += f"\nContent-Base: {self.clientInfo["videoStream"].filename.split("/")[-1]}\nContent-Type: application/sdp\nContent-Length: {len(sdp)}\n\n{sdp}"
			connSocket = self.clientInfo["rtspSocket"][0]
			connSocket.send(reply.encode("utf-8"))

		# Error messages
		elif code == self.FILE_NOT_FOUND_404:
			print("404 NOT FOUND")
		elif code == self.CON_ERR_500:
			print("500 CONNECTION ERROR")
		elif code == self.NOT_VALID_STATE:
			print("455 METHOD NOT VALID IN THIS STATE")