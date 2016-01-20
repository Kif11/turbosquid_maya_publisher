import time

from maya import cmds as cmds
import cm.tests.shapes.mesh


def run(*args, **kwargs):
    """8a. Extra. Find faces with 0 surface area. These look like edges, 
    but cause shading problems  
    ---
    returns True/False, the number of 0 area faces
    and a list of faces.
    has_zeroareafaces -> (boolean, int, [mesh:f[id],])
    """
    t0 = float(time.time())
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
        verbose = False
    
    result=False
    meshes = cmds.ls(type='mesh', noIntermediate=True, long=True)
    if verbose: print 'before: ',  meshes
    meshes = [x for x in meshes if not cm.tests.shapes.mesh.isEmpty(x)]
    if verbose: print 'after :', meshes
    try:
        cmds.select(meshes)
    except TypeError:
    	print "# Warning: No meshes in scene"
    if verbose: print 'line 805'	
    cmds.selectType( pf=True ) 
    if verbose: print 'line 807'	
    cmds.polySelectConstraint(
        mode=3, # all and next
        type=0x0008, # faces
        geometricarea=True,
        geometricareabound = [0.0, 0.00001], # zero area
        )
    if verbose: print 'line 814'	
    
    sel=cmds.ls(sl=True, fl=True)
    result =  (len(sel) > 0) or False
    cmds.polySelectConstraint(disable=True)
    try:
        cmds.select(sel)
    except TypeError:
    	pass 
    print '%-24s : %.6f seconds' % ('f.area.run()', (float(time.time())-t0)) 
    return (result, len(sel), sel)
    
 