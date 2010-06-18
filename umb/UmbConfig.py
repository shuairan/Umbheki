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
            logger.debug("Adding Trigger '%s' to Action '%s' " % (triggerName, name))
            actionList[name].addTrigger(triggerName);

    return actionList;

class Action:
    def __init__(self):
        self.trigger = {};

    def addTrigger(self, trigger, *args):
        self.trigger = trigger;
