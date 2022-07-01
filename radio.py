import time
import paramiko
from scp import SCPClient
import sys
from tqdm import tqdm #Library to show progress bar

#Ask for input of audio, frequency and time to play
isNotWav = True
while isNotWav:
	file = input('Filename (.wav only): ')
	if file[-4:] == '.wav':
		isNotWav = False
freq = input('Frequency to play at (1 d.p.): ')
timer = int(input('Amount of time to play (s): '))
print('')

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

ssh = createSSHClient('192.168.29.120', 22, 'root', 'kahaan16') #Create SSH Connection
scp = SCPClient(ssh.get_transport(), progress=progress) #Use connection to create SCPClient
session = getSession(ssh) #Create shell session

#Transfer file using SCPClient
print('Transferring File')
scp.put(file, recursive=True, remote_path='PiFmRds/src')
scp.close()

#Send command to play file
session.send('(cd PiFmRds/src && sudo ./pi_fm_rds -freq ' + freq +' -audio ' + file+')\n')

print('')
print('')
#Dummy loop with progress bar to let codee run for given time
for i in tqdm(range(timer)):
    time.sleep(1)

#Send KeyboardInturrupt Signal to shell
session.send('\x03')

#Close all the clients
session.close()
ssh.close()

print('')