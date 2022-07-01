#Suppress Scapy warnings and deprercation warnings
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

import warnings
from cryptography.utils import CryptographyDeprecationWarning
warnings.filterwarnings('ignore', category=CryptographyDeprecationWarning)

#Import required libraries
import time
import paramiko
from scp import SCPClient
import sys
from tqdm import tqdm
import scapy.all as scapy
import socket

#Function to Creaete SSHClient to communicate with Pi
def createSSHClient(server, port, user, password):
	client = paramiko.SSHClient()
	client.load_system_host_keys()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.connect(server, port, user, password)

	return client

#Function to create a session and interact with a shell using the SSHClient
def getSession(client):
	transport = client.get_transport()
	session = transport.open_session()
	session.setblocking(0) # Set to non-blocking mode
	session.get_pty()
	session.invoke_shell()

	return session

#Function to define a progress indicator for SCP transfers
def progress(filename, size, sent):
	sys.stdout.write("%s\'s progress: %.2f%%   \r" % (filename.decode('ascii'), float(sent)/float(size)*100))

#Function to transfer file
def transferMusic(client, file, path):
	scp = SCPClient(client.get_transport(), progress=progress) #Use connection to create SCPClient
	print('Transferring File')
	scp.put(file, recursive=True, remote_path=path)
	scp.close()
	print('')

#Function to play music
def playMusic(client, file, freq, timer):
	session = getSession(client) #Create shell session

	#Send command to play file
	session.send('(cd PiFmRds/src && sudo ./pi_fm_rds -freq ' + freq +' -audio ' + file+')\n')
	print('')

	#Dummy loop with progress bar to let music play for given time
	for i in tqdm(range(timer)):
		time.sleep(1)

	session.send('\x03') #Send KeyboardInturrupt Signal to shell

	session.close() #Close session

#A class for the Arp-Scan
class scan:

	#Method to scan and output all devices on network taken from https://stackoverflow.com/questions/59589190/python-arp-scanner
	def Arp(self, ip):
		self.ip = ip
		print(ip)
		arp_r = scapy.ARP(pdst=ip)
		br = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')
		request = br/arp_r
		answered, unanswered = scapy.srp(request, timeout=1)
		print('\tIP\t\t\t\t\tMAC')
		print('_' * 37)
		for i in answered:
			ip, mac = i[1].psrc, i[1].hwsrc
			print(ip, '\t\t' + mac)
			print('-' * 37)

	#Method to find any RaspBerry Pi on network
	def RaspArp(self, ip):
		self.ip = ip
		arp_r = scapy.ARP(pdst=ip)
		br = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')
		request = br/arp_r
		answered, unanswered = scapy.srp(request, timeout=1)

		for i in answered:
			ip, mac = i[1].psrc, i[1].hwsrc
			if mac.startswith('b8:27:eb'):
				print('Found!')
				return ip

		return 'NOT FOUND'

#Function to get the Raspberry Pi's IP
def getRaspIP():

	#Get localhost IP
	ipList = socket.gethostbyname_ex(socket.gethostname())

	try:
		IP = ipList[2][1]
	except:
		print(ipList)
		print('Error finding IP')
		quit()

	print('Your IP Address: ' + IP)
	print('')

	arp = scan() #Create an instance of the class

	#Scan network for RaspBerry Pi upto 10 times
	for i in range(10):
		raspAdd = arp.RaspArp(IP+'/24')
		if raspAdd == 'NOT FOUND':
			print('Not found, trying again...')
			print('')
			continue
		else:
			break
	
	return raspAdd

#Main Function
def main():
	print('')
	print('Finding Raspbery Pi...')
	print('')

	raspAdd = getRaspIP() #Get RaspBerry PI IP Address
	pwd = '<password>' #Set Password
	
	#Quit if no Raspberry Pis found
	if raspAdd == 'NOT FOUND':
		print('No RaspberryPis on network')
		quit()

	print('')
	print('Raspberry Pi IP: ' + raspAdd)
	print('Connecting...')
	ssh = createSSHClient(raspAdd, 22, 'root', pwd) #Create SSH Client
	print('Connected!')
	print('')

	#Ask for input of audio, frequency and time to play
	isNotWav = True
	while isNotWav:
		file = input('Enter filename (.wav only): ')
		if file[-4:] == '.wav':
			isNotWav = False
	freq = input('Frequency to play at (1 d.p.): ')
	timer = int(input('Amount of time to play (s): '))
	print('')

	transferMusic(ssh, file, 'PiFmRds/src') #Transfer music using client and filename

	print('')
	stopper = input('Press enter to start broadcasting file... ') #Stopper so user can play file at right time
	print('')
	playMusic(ssh, file, freq, timer) #Play the file remotely

	ssh.close() #Close SSH Connection
	print('')

if __name__ == '__main__':
	main()
