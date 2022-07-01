import scapy.all as scapy
import socket

#Get localhost IP
IP = socket.gethostbyname_ex(socket.gethostname())[2][1]
print('Your IP Address: ' + IP)
print('')

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
                return ip

        return 'NOT FOUND'

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

print('')
print('Raspberry Pi IP: ' + raspAdd)