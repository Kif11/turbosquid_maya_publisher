import time

from maya import cmds as cmds

def run(*args, **kwargs):
    """Check for construction history
    has_history([item]) -> boolean, int, list 
    """
    t0 = float(time.time())
    batch=cmds.about(batch=True)
    valid_kwargs = ['verbose']
    for k, v in kwargs.iteritems():
        if k not in valid_kwargs:
            raise TypeError("Invalid keyword argument %s" % k)  
    # verbose defaults to False 
    verbose = False
    # unless set in menu or specified in cmdline
    try:
        verbose = kwargs['verbose']
    except KeyError:
    	verbose = False
    	if cmds.optionVar(exists='checkmateVerbosity'):
    		verbose = cmds.optionVar(query='checkmateVerbosity')
    else:
        pass  
    if args:
        nodes = args
    else:
        nodes = cmds.ls(geometry=True)
    if verbose:
        print nodes    
    result = False
    err = []
    type(err)
    for node in nodes:
        nodetype = cmds.nodeType(node)
        if verbose:
            print '%s -> %s' % (node, nodetype)
        if nodetype == 'mesh':
            plug = ''.join([node,'.inMesh'])
            history = cmds.connectionInfo(plug, isDestination=True)
            if history:
                try:
                    err.extend([node]) 
                except AttributeError:
                    err = [node,]
        elif nodetype == 'nurbsCurve':
            plug = ''.join([node,'.create'])
            history = cmds.connectionInfo(plug, isDestination=True)
            if history:
                try:
                    err.extend([node]) 
                except AttributeError:
                    err = [node,]
        elif nodetype == 'nurbsSurface':
            plug = ''.join([node,'.create'])
            history = cmds.connectionInfo(plug, isDestination=True)
            if history:
                try:
                    err.extend([node]) 
                except AttributeError:
                    err = [node,]
        elif nodetype == 'subdiv':
            plug = ''.join([node,'.create'])
            history = cmds.connectionInfo(plug, isDestination=True)
            if history:
                try:
                    err.extend([node]) 
                except AttributeError:
                    err = [node,]
        else :
            if verbose:
                print '%s is not a valid geometry type' % node
    if len(err) and True or False:
        result=True
        if not batch:
            cmds.select(err)
    print '%-24s : %.6f seconds' % ('history.run()', (float(time.time())-t0)) 
    return result, len(err), err
    
