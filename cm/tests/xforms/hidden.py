import time

#local application/library specific imports
from maya import cmds as cmds
from maya import mel as mel

def run(*args, **kwargs):
    """Finds and  unhide all hidden objects.
    ---
    Check if visibility attribute is off on all DAG nodes 
    Selects all and shows all hidden objects.
    Returns True if scene contains invisible objects
    and a list of all invisible objects
    
    has_hiddenobjects() -> boolean, int, list
    """
    
    valid_kwargs = ['verbose']
    for k, v in kwargs.iteritems():
        if k not in valid_kwargs:
            raise TypeError("Invalid keyword argument %s" % k)  
    
    result = False
    err = list()
    verbose = False

    # verbose defaults to False if verbose option not set in menu 
    # or specified in cmdline
    try:
        verbose = kwargs['verbose']
    except KeyError:
    	verbose = False
    	if cmds.optionVar(exists='checkmateVerbosity'):
    		verbose = cmds.optionVar(query='checkmateVerbosity')
    else:
        pass    
    t0=time.time()

    # list all DAG nodes
    cmds.ls(dag=True)
    
    invisibleobjects=list()
    ignorelist = [u'persp',
                  u'perspShape',
                  u'top',
                  u'topShape',
                  u'front',
                  u'frontShape',
                  u'side',
                  u'sideShape']
    for i in range(0,100):
        ignorelist.append('CM_Camera_'+ str(i))
        ignorelist.append('CM_Camera_'+ str(i) + "Shape")
        ignorelist.append('CM_Turntable_Camera_'+ str(i))
        ignorelist.append('CM_Turntable_Camera_'+ str(i) + "Shape")

    for node in cmds.ls(dag=True):
        if verbose: 
            print node
        if node in ignorelist:
            pass
        else:
            attr = '%s.visibility' % node
            if not (cmds.getAttr(attr)):
            	result = True
                invisibleobjects.append(node)
                
    print '%-24s : %.6f seconds' % ('xforms.hidden.run()', (float(time.time())-t0)) 
    # fix
    if result:
        cmds.select(invisibleobjects)
        cmds.showHidden(invisibleobjects, above=True)
    
    return result, len(invisibleobjects), invisibleobjects

