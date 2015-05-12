from common import *
import plugin

from bottle import route, run, template, error, response

import StringIO
import sys

import json
import traceback

import os
if os.name == "nt":
    import subprocess

"""
TODO:

Stop logging
HTTP response codes
API key auth - sha256 and passlib.utils.consteq
"""

def launch_httpGui(app2):
    """Systray entry http GUI launch function."""
    httpGuiUrl = "http://" + app2["plugins"]["http"].conf['host'] + ":" + app2["plugins"]["http"].conf['port']
    if os.name == "nt":  # windows
        subprocess.call(["cmd", "/c", "start", httpGuiUrl])
    else:
        os.system(httpGuiUrl)  # untested, probably wrong

@route('/<plugin>/<method>/<args:path>.json')
def call_plugin(plugin, method, args):

    try:
        
        params = args.split(" ")
    
        if plugin not in app['plugins']:
            raise Exception("Plugin " + plugin + " not allowed")
        if not app['plugins'][plugin].running and params[0] != 'start':
            raise Exception("Plugin " + plugin + " not started")
    
        if method == 'start': method = 'start2'
    
        # reply before being blocked by non threaded start
        # TODO : recreate thread for the start command and delete when stop
        #if not app['plugins'][plugin].running and method == 'start2':
        #    # TODO:
        #    return template('{"result":'+json.dumps({'reply':True, 'prints':'Restarting '+plugin+''})+',"error":'+json.dumps(None)+',"id":1}')
        
        # reply before closing connection
        #if plugin == 'httpnew' and method == 'restart':
        #    # TODO:
        #    return template('{"result":'+json.dumps({'reply':True, 'prints':'Restarting rpc'})+',"error":'+json.dumps(None)+',"id":1}')
    
        # can't call private/protected methods
        if method[0] == '_':
            if app['debug']: print "RPC - forbidden cmd :", "/" + "/".join([plugin, method, arg1]) + ".json"
            raise Exception('Method "' + method + '" not allowed')
    
        """
        # help asked on a method
        if 'help' in params:
            params.remove('help')
            params.insert(0, method)
            method = 'help'
    
        # help thrown due to incorrect use of method
        if method in app['plugins'][plugin].helps and len(params) not in range(app['plugins'][plugin].helps[method][0], app['plugins'][plugin].helps[method][1]+1):
            params.insert(0, method)
            method = 'help'
        """
    
        if app['debug']: print "HTTP - executing cmd :", plugin, method, params
    
        # capture stdout
        capture = StringIO.StringIO()
        #sys.stdout = capture
    
        try:
            methodRpc = getattr(app['plugins'][plugin], '_rpc')
            result = methodRpc(method, *params)
        except AttributeError, e:
            if app['debug']: traceback.print_exc()
            raise Exception('Method "' + method + '" not supported by plugin "' + plugin + '"')
        #except Exception, e:
        #    if app['debug']: traceback.print_exc()
        #    return template('Exception : ' + str(e))
    
        # restore stdout
        sys.stdout = sys.__stdout__
        prints = capture.getvalue()
        capture.close()
    
        #if result is None:
        #    result = 'No data'
    
    except Exception, e:
        response.status = 500
        return {"error": {"code": 1, "message": str(e)}}
        
    return {"result":result}

class pluginHttp(plugin.PluginThread):
    name = 'http'
    options = [
        {'start':    ['Launch at startup', 1]},
        {'host':        ['Listen on ip', '127.0.0.2', '<ip>']},
        {'port':        ['Listen on port', '8080', '<port>']},
        # TODO: Figure out what the defaults should be for IP/port
    ]
    systrayEntry = ('httpGui', None, launch_httpGui)  # menu icons should somehow be possible via the middle option

    def pStatus(self):
        if self.running:
            return "Plugin " + self.name + " running"

    def pStart(self):
        if app['debug']:
            print "Starting HTTP server..."
        
        run(host=self.conf['host'], port=int(self.conf['port']))
        
        # TODO
        return True

    def pStop(self):
        if app['debug']: print "Plugin stop :", self.name
        
        # TODO
        
        print "Plugin %s stopped" %(self.name)
        return True

    def pSend(self, args):
        # TODO
        return False
