from common import *
import rpcClient
import ConfigParser, StringIO
import time

class backendData():
	def __init__(self, conf):
		self.conf = conf

	rpc = None
	blockchainCurrent = False

	def _loadRPCConfig(self):
		conf = ConfigParser.SafeConfigParser()
		ini_str = '[r]\n' + open(self.conf).read()
		ini_fp = StringIO.StringIO(ini_str)
		conf.readfp(ini_fp)

		host = '127.0.0.1'
		port = 8336
		user = ''
		password = ''

		if conf.has_option('r', 'rpchost'):
			host = conf.get('r', 'rpchost')
		if conf.has_option('r', 'rpcport'):
			port = conf.get('r', 'rpcport')
		if conf.has_option('r', 'rpcuser'):
			user = conf.get('r', 'rpcuser')
		if conf.has_option('r', 'rpcpassword'):
			password = conf.get('r', 'rpcpassword')
		
		self.rpc = rpcClient.rpcClientNamecoin(host, port, user, password)
	
	def checkBlockchainCurrent(self):
		if self.blockchainCurrent:
			return None, self.blockchainCurrent
		
		error, blockcount = self._rpcSend(["getblockcount"])
		if error:
		    return error, blockcount
		error, blockhash = self._rpcSend(["getblockhash", blockcount])
		if error:
		    return error, blockhash
		error, block = self._rpcSend(["getblock", blockhash])
		if error:
		    return error, block
		
		if block["time"] > time.time() - 200000:
		    self.blockchainCurrent = True
		else:
		    self.blockchainCurrent = False
		
		return None, self.blockchainCurrent
		
	
	def getAllNames(self):
		error, isCurrent = self.checkBlockchainCurrent()
		if error:
			return error, isCurrent
		if not isCurrent:
			if app['debug']: print "BackendDataNamecoin: Incomplete Blockchain"
			return True, "Incomplete Blockchain Detected"
		datas = {}
		error, data = self._rpcSend(["name_filter", app['plugins']['data'].conf['name_filter']])
		for name in data:
			datas[name['name']] = name
		return error, datas

	def getName(self, name):
		error, isCurrent = self.checkBlockchainCurrent()
		if error:
			return error, isCurrent
		if not isCurrent:
			if app['debug']: print "BackendDataNamecoin: Incomplete Blockchain"
			return True, "Incomplete Blockchain Detected"
		return self._rpcSend(["name_show", name])
	
	def _rpcSend(self, rpcCmd):
		if app['debug']: print "BackendDataNamecoin:", rpcCmd
		if self.rpc is None:
			self._loadRPCConfig()
		return self.rpc.sendJson(rpcCmd)
	
