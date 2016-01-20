import time
import os

from maya import cmds as cmds

def find_missinglinks():
    """File Links - missing texture paths/dlls
   
    find_missinglinks() -> string
    """
    t0 = float(time.time())
    filenodes = cmds.ls(type='file')
    err = dict()
    for filenode in filenodes:
        plug = filenode+'.fileTextureName'
        filetexturename = cmds.getAttr(plug)
        if os.path.exists(filetexturename) and os.path.isfile(filetexturename):
            pass
        else:
            # print filenode, filetexturename
            result=True  
            err[filenode]=filetexturename
    #print '%-24s : %.6f seconds' % ('scene.missing.missingfileLinks()', (float(time.time())-t0)) 
    return err
    
def run(*args, **kwargs):
    """ Report missing texture files. Missing texture files are those files 
    whose names the file nodes in the scene use as values for their 
    .fileTextureName/.ftn attribute. If Maya cannot find such a file, this tests 
    reports it as missing. This test currently ignores mentalrayIblShape 
    node's .texture attribute 
    
    Fix: report gives the node type instead of the node name. 
    ---
    9. File Links - missing texture paths/dlls
    returns True/False and a dict with filenode: filetexturename pairs
    
    has_missingfiles() -> boolean, int, dict
    """
    
    
    t0 = float(time.time())
    import os
    valid_kwargs = ['batch', 'verbose']
    for k, v in kwargs.iteritems():
        if k not in valid_kwargs:
            raise TypeError("Invalid keyword argument %s" % k)
    try:
        batch = kwargs['batch']
    except KeyError:
        # default to True, to disable UI 
        batch = True       
    
    try:
        verbose = kwargs['verbose']
    except KeyError:
    	verbose = False
    	if cmds.optionVar(exists='checkmateVerbosity'):
    		verbose = cmds.optionVar(query='checkmateVerbosity')
        else:
            verbose = False 
        
    result = False
    err = find_missinglinks()
    result = len(err) > 0
    if verbose:
        format = "%-20s ->  %s"
        print "# Errors #"
        for  k, v in err.iteritems():
            print format % (k, v)
    if result and not batch:
        missingfilesUI(err)
    print '%-24s : %.6f seconds' % ('scene.missing.run()', (float(time.time())-t0)) 
    return (result, len(err), err)