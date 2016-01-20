import time


from maya import cmds as cmds
def isIdentity(transform):
    return cmds.xform(transform, query=True, matrix=True) == [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
        
        

def run(*args, **kwargs):
    """Selects all objects with non-zero transforms. An object has non-zero 
    transforms if its .translateX, .translateY, .translateZ, .rotateX, .rotateY 
    or .rotateZ attributes are not 0.0 or if its .scaleX, scaleY or .scaleZ 
    attributes are not 1.0.  
    ---
    Returns True or false, the number of objects with non-zero transforms
    and a list of all objects with non-zero transforms
    has_nonzerotransforms() -> boolean, int, list
    """
    t0=time.time()
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
        
    result = False
    err = list()
    identities = list()
    # checking all transforms is a bad idea
    # we need to check all parents of geomtry
    # transforms = cmds.listRelatives(cmds.ls(geometry=True, noIntermediate=True, long=True), parent=True)
    # fix a bug with animalfruit
    # transforms = cmds.listRelatives(cmds.ls(geometry=True, noIntermediate=True, long=True, allPaths=True), parent=True, fullPath=True)
    # transforms = cmds.listRelatives(cmds.ls(geometry=True, noIntermediate=True, long=True, allPaths=True), parent=True, fullPath=True)
    try:
        shapes = cmds.ls( type=('mesh', 'nurbsSurface', 'nurbsCurve', 'subdiv'), noIntermediate=True, long=True,  allPaths=True )
    except RuntimeError: 
        shapes = cmds.ls( type=('mesh', 'nurbsSurface', 'nurbsCurve'), noIntermediate=True, long=True,  allPaths=True )
    except TypeError:
        err.append(['# Warning: No renderable geometry in scene'])
        return result, len(err), err            
    try:
        transforms = cmds.listRelatives( shapes, parent=True, fullPath=True )
    except TypeError:
        err.append(['# Warning: No renderable geometry in scene'])   
        return result, len(err), err
    
    # and all root transforms
    # fix : this includes camera transforms 
    # transforms.extend(find_roots())
    for item in transforms:
        
        # ignore default objects
        if item in ['front', 'top', 'side', 'persp']:
            continue
        else:
            nonidentity = not isIdentity(item)
            if verbose:
                print '%s => %s' % (item, nonidentity)
        if nonidentity:
            identities.append(nonidentity)
            err.append(item)
        else:
            pass
    result = True in identities
    try:
        cmds.select(err)
    except TypeError:
        if verbose:
            print 'Nothing to select.'
    print '%-24s : %.6f seconds' % ('xforms.identity.run()', (float(time.time())-t0)) 
    return result, len(err), err
    
    


