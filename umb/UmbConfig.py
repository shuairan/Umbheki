import xml.dom.minidom
from pprint import pprint
import logging

logger = logging.getLogger("UmbConfig")

def loadActions(file='config.xml'):
    cfg = xml.dom.minidom.parse(file)
    
    actionList = {}
    
    actions = cfg.getElementsByTagName('action')
    
    for action in actions:
        action_enabled = action.getAttribute('enabled')
        event = action.getAttribute('event');
        triggers = action.getElementsByTagName('trigger');
        
        if not event in actionList:
            logger.debug("New Action for: %s "% event)
            actionList[event] = Action()
        
        for trigger in triggers:
            triggerName = trigger.getAttribute('name');
            trigger_enabled = trigger.getAttribute('enabled')
            args = trigger.getAttribute('args');
            
            logger.debug("Adding Trigger '%s' to Action '%s' with args %s " % (triggerName, event, args))
            condition = trigger.getElementsByTagName('condition');
            
            cond = Condition(condition[0])
            
            if args is "":
                args = None
            newTrigger = Trigger(triggerName,args,cond)
            if action_enabled is 'false' or trigger_enabled is 'false':
                newTrigger.deactivate()
            
            actionList[event].addTrigger(newTrigger)

    return actionList;
    

class Action:
    def __init__(self):
        self.triggers = [];
        self.activated = True
        
    """ Todo: Add support for arguments"""
    def addTrigger(self, trigger):
        self.triggers.append(trigger)

    def getTrigger(self, name):
        for trigger in self.triggers:
            if trigger.name is name:
                return trigger
        
        return None


class Trigger:
    def __init__(self, name, args=None, condition = None):
        self.name = name
        self.args = args
        self.condition = condition
        self.enabled = True
    
    @deprecated
    def hasCondition(self):
        if self.condition is not None: 
            return True
    
    def checkCondition(self, args):
        if self.condition is None:
            #no condition
            return True
        else:
            return self.condition.check(args)
        
    def activate(self):
        self.enabled = True
    
    def deactivate(self):
        self.enabled = False
    
        
class Condition:
    def __init__(self, xmldom):
        self.arg = xmldom.getAttribute('arg');
        self.value = xmldom.getAttribute('value');
        
        if xmldom.hasAttribute('eval'):
            self.evaluate = xmldom.getAttribute('eval');
        else:
            self.evaluate = "{arg} is " + self.value
        
        logger.debug("EVALUATE %s " % self.evaluate)
        
    def check(self, arguments):
        logger.debug("Checking condition for: '%s'?" %(self.arg))
        logger.debug(arguments)
        
        if self.arg in arguments: 
            value = arguments[self.arg]
            eval_condition = self.evaluate.format(arg=value)
            logger.debug("evaluation: '%s' " % self.evaluate.format(arg=self.arg))
            logger.debug("evaluation: '%s' " % eval_condition)
            if eval (eval_condition):
                logger.debug("Condition is True!")
                return True
        
        return False
