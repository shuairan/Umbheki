def trigger(*args, **kwargs):
    """Decorator for event functions"""
    
    def decorate(func):
        setattr(func, '_triggerable', True)
        #print func.__name__
        return func

    return decorate(args[0], **kwargs)
    
def event(*args, **kwargs):
    """Decorator for event functions"""
    
    def decorate(func):
        setattr(func, '_event', True)
        #print func.__name__
        return func

    return decorate(args[0], **kwargs)

import warnings
def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""
    def new_func(*args, **kwargs):
        warnings.warn("Call to deprecated function %s." % func.__name__,
                      category=DeprecationWarning)
        return func(*args, **kwargs)
    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    new_func.__dict__.update(func.__dict__)
    return new_func
