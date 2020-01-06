from hackingtools.core import Logger, Utils, Config
if Utils.amIdjango(__name__):
	from .library.core import hackingtools as ht
else:
	import hackingtools as ht
import os

import socket, sys

config = Config.getConfig(parentKey='modules', key='ht_banner_grabber')
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'output'))

class StartModule():

	def __init__(self):
		pass

	def help(self):
		Logger.printMessage(message=ht.getFunctionsNamesFromModule('ht_banner_grabber'), debug_module=True)

	def grabPortBanner(self, ip, port):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			s.connect(( str(ip) , int(port) ))
			s.settimeout(1)
			banner = s.recv(1024)
			return banner.decode().strip()
		except:
			return ''