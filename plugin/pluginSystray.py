import common
import plugin

import os
import time

if os.name == "nt":
    import winsystray as ossystray

icon = "plugin/systrayicon.ico"
hover_text = "NMControl"

class pluginSystray(plugin.PluginThread):
    name = 'systray'
    options = {
        'start':    ['Launch at startup', 1],
    }
    sti = None

    def gather_entries(self):
        entries = []
        for plugin in self.app["plugins"]:
            try:
                entries.append(self.app["plugins"][plugin].systrayEntry)
            except AttributeError:
                pass
        return tuple(entries)

    def pStart(self):
        if self.sti:
            return
        if self.app['debug']: print "Systray.py: Plugin %s parent start" %(self.name)
        self.menu_options = self.gather_entries()
        try:
            self.sti = ossystray.SysTrayIcon(icon, hover_text, self.menu_options, on_quit=self.do_quit, default_menu_index=None)
        except NameError:
            # bail without systray for GUI people
            import __main__
            if "nmcontrolwin.pyw" in __main__.__file__:
                raise Exception("Systray start failed. Get details by running from the command line.\n" +
                                "Note: Windows systray needs Python Win32 Extensions.")
            
            return
        self.sti.app = self.app
        self.halted = 0
        self.running = 1
        while self.running:
            self.sti.pump()
            time.sleep(0.01)
        self.sti.do_quit()
        self.halted = 1

    def pStop(self, arg = []):
        if common.app['debug']: print "Plugin %s parent stop" %(self.name)
        if not self.running:
            return True
        while not self.halted:
            self.running = False
            time.sleep(0.001)
        return True

    def do_quit(self, sti):
        if common.app['debug']: print "Systray.py: do_quit"
        common.app['plugins']['main'].stop()  # will bail if already shutting down
