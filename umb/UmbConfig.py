import xml.dom.minidom
from pprint import pprint
import logging

logger = logging.getLogger("UmbConfig")

def loadActions(file='config.xml'):
    cfg = xml.dom.minidom.parse(file)
    
    actionList = {}
    
    actions = cfg.getElementsByTagName('action')
    
    for action in actions:
        name = action.getAttribute('name');
        triggers = action.getElementsByTagName('trigger');
        
        if not name in actionList:
            logger.debug("New Action for: %s "% name)
            actionList[name] = Action()
        
        for trigger in triggers:
            triggerName = trigger.getAttribute('name');
            args = trigger.getAttribute('args');
            logger.debug("Adding Trigger '%s' to Action '%s' with args %s " % (triggerName, name, args))
            actionList[name].addTrigger(triggerName, args);

    return actionList;
    

class Action:
    def __init__(self):
        self.triggers = [];

    """ Todo: Add support for arguments"""
    def addTrigger(self, trigger, args=None):
        self.triggers.append(Trigger(trigger,args))

    def getTrigger(self, name):
        for trigger in self.triggers:
            if trigger.name is name:
                return trigger
        
        return None


class Trigger:
    def __init__(self, name, args=None):
        self.name = name
        self.args = args
