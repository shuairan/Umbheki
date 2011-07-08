import os, sys
from umb.UmbPlugin import UmbPlugin
from yapsy.PluginManager import PluginManager
import UmbConfig
from UmbConfig import Action
import logging
import inspect
from pprint import pprint

PLUGIN_CATEGORY="umbplugin"
COREPLUGIN_CATEGORY="umbcoreplugin"

logger = logging.getLogger("Umbheki")

class Umbheki:
    
    def __init__(self):
        self.trigger = {}
        self.events = {}
        self.actions = UmbConfig.loadActions()
        logger.debug(self.actions)
        self.loadPlugins()
        
        print self.actions
        
    def loadPlugins(self):
        logger.debug("loading Plugins")

        self.pluginman = PluginManager(directories_list=[os.path.join(
                        os.path.dirname(os.path.abspath(__file__)),"../plugins")],
                        categories_filter={PLUGIN_CATEGORY:UmbPlugin},
                        plugin_info_ext="plugin")
        self.pluginman.collectPlugins()
        
        #install all default plugins
        for plugin_info in self.pluginman.getPluginsOfCategory(PLUGIN_CATEGORY):
            self.registerPlugin(plugin_info)
    
    
    def registerPlugin(self, plugin_info):
        logger.debug("Register plugin: %s" % plugin_info.name)
        plugin = plugin_info.plugin_object
        plugin.trigger = self.trigger    #give the plugin a reference to the trigger
        plugin.eventWatchdog = self.watchdog
        
        for name, value in inspect.getmembers(plugin):
            
            if inspect.ismethod(value) and getattr(value, '_triggerable', False):
                module = value.im_self.__class__.__name__
                triggerName = "%s.%s" % (module, name)
                self.trigger[triggerName] = value
                logger.info("  * New Trigger: %s " % triggerName)
                """
            @deprecated 
            elif inspect.ismethod(value) and getattr(value, '_event', False): 
                    module = value.im_self.__class__.__name__
                    eventName = "%s.%s" % (module, name)
                    self.events[eventName] = value
                    logger.debug("New Event: %s " %  eventName)
                    plugin.raiseEvent.stopped()
                    self.watchdog("VLC.stopped");
                """
            else:
                continue

    
    def callTrigger(self, cmd, args=None):
        """
        trigger function: call any trigger by passing the name of the trigger
        to this function
        """
               
        if self.trigger.has_key(cmd):
            try:
                if args is None:
                    self.trigger[cmd]()
                else:
                    self.trigger[cmd](args)
            except PluginException:
                print "Plugin Error!"
        else:
            logger.error("Trigger '%s' not found" % cmd)
    
    
    def getAction(self, event):
        logger.debug("Get Action: %s " % event);
        if event in self.actions:
            return self.actions[event]
        else:
            return None
    
    
    def watchdog(self, event, args=None):
        """
        will be called every time a event occures and has to react on that event by calling the specified triggers
        """
        
        logger = logging.getLogger("Umbheki Watchdog")
        logger.debug("event raised: '%s'" % event)
        
        action = self.getAction(event)
        if action is not None:
            for trigger in action.triggers:
                logger.debug("Trigger called '%s' args: %s " %(trigger.name, trigger.args))
                self.callTrigger(trigger.name, trigger.args);



class NotYetImplemented(Exception):
    def __init__(self):
        self.value = "Work in process!"

    def __str__(self):
        return repr(self.value)
    
    

class PluginException(Exception):
    def __init__(self):
        self.value = "Error in Plugin!"

    def __str__(self):
        return repr(self.value)

