from yapsy.IPlugin import IPlugin
from decorator import *

from pprint import pprint
import logging
import sys
import new

logger = logging.getLogger("Plugin")

class UmbPlugin(IPlugin):
    """
    default class of Umbheki Plugins
    """
    events = []
    event_args = None
    
    def __init__(self):
        IPlugin.__init__(self)
        self.name = self.__class__.__name__
        self.logger = logging.getLogger("Plugin:%s" % self.name)
        self.raiseEvent = EventRaiser(  self,
                                        self.events,
                                        self.event_args,
                                        self.logger)
        
        self.trigger = None
     
    #def raiseEvent(self, name, eventList, logger, watchdog):
        """dummy, will be set to a new EventRaiser in __init__"""
        #pass
    
    def eventWatchdog(self, event, *args):
        """
        DO NOT USE AND NOT OVERWRITE! 
        this function will be overwritten with Umbheki.watchdog
        """
        print "OLD"
    
    def callTrigger(self, cmd, *args):
        """
        trigger function: call any trigger by passing the name of the trigger
        to this function
        """
        if self.trigger.has_key(cmd):
            self.trigger[cmd](args)
        else:
            self.logger.error("Trigger '%s' not found" % cmd)
            

class EventRaiser(object):
    """
    EventRaiser object
    """
    
    def __init__(self, parent, eventList, eventArgs, logger):
        self.parent = parent
        self.logger = logger
        self.name = self.parent.name

        self.event_args = {}
        if eventArgs is not None:
            self.event_args = dict(zip(map( lambda x:self.name+"."+x, eventArgs.keys()), eventArgs.values()))

        self.createEventMethods(eventList)
        
        
    def __call__(self, eventName=None, *args):
        """
        raise an event. Three ways to raise:
            1. call self.raiseEvent() in the event function in your plugin
            2. call self.raiseEvent("PLUGINNAME.EVENTNAME")
            3. call self.raiseEvent.EVENTNAME() for events from event list
        """
        if eventName is None:   
            """"@deprecated: you should raise with eventName!"""
            eventmethod = sys._getframe(1).f_code.co_name
            eventName = "%s.%s" % (self.name, eventmethod)
            
        
        self.logger.debug("Event called: %s " % eventName)
        if len(args): 
            self.logger.debug(args)
            args = self.createEventArgumentList(eventName, args)
            
        self.parent.eventWatchdog(eventName, args)

    def createEventArgumentList(self, eventName, arguments):
        """
        maps the argument list (from 'event_args' in the plugin) 
           to the arguments that came as parameter in the event call, creates a dictionary:
           
        """
        eventargs = self.event_args[eventName]
        if  len(arguments) and len(eventargs):
            argList = dict(zip(map(lambda x:self.name+"."+x, eventargs), arguments))
            #rest of unnamed arguments:
            #rest = arguments[len(eventargs):]
            #argList = argMap, rest
        else:
            argList = arguments
            
        return argList

    def createEventMethods(self, eventList):
        """
        add the event methods to the instance of this class for every 
        methodname from eventList
        """
        for newEventMethod in eventList:
            self.logger.debug("EventMethod '%s.%s' registered" % (self.name,
                                                                newEventMethod))
            eventName = "%s.%s" % (self.name, newEventMethod)
            self.addMethod(newEventMethod, eventName)
                                                    
    def addMethod(self, method, args):
        """
        add a new method to the instance of this class
        """
        self.__setattr__(method, new.instancemethod(self.__call__,
                                                    args,
                                                    self.__class__))
