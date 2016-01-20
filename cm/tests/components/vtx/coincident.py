import time


from maya import cmds as cmds
from maya import mel as mel

import cm.tests.shapes.mesh

def run(*args, **kwargs):
    """Detect Coincident (overlapping) Vertices. Finds vertices that are part
    of the same mesh that have the same xyz world space coordinates. 
    ---
    Detect Coincident (overlapping) Vertices? How many? Show/Highlight 
    them.
    Find vertices that have the same xyz world space coordinates.
    Returns :
    - True/False, 
    - number of coincident vertices, 
    - number of objects with coincident vertices, 
    - coincident vertices, 
    - objects with coincident vertices
    
    Arguments :
    - verbose 
    has_coincidentvertices2([verbose=True/False]) -> boolean, int, int, list, list
    """
    # keep time
    t0 = float(time.time())
    # check for invalid keyword argument
    valid_kwargs = ['verbose']
    for k, v in kwargs.iteritems():
        if k not in valid_kwargs:
            raise TypeError("Invalid keyword argument %s" % k)
    # verbose defaults to False if verbose option not set in menu or set 
    # as cmdline argument
     
    try:
        verbose = kwargs['verbose']
    except KeyError:
        verbose = False 
    	if cmds.optionVar(exists='checkmateVerbosity'):
    		verbose = cmds.optionVar(query='checkmateVerbosity')
        else:
            verbose = False
    else:
        pass     
    # set defaults for return values  
    result = False 
    err = []
    Lvertices = []
    Lobjects = []
    
    # only consider polygonal meshes, ignore construction history
    # meshes = cmds.ls(typ='mesh', noIntermediate=True)
    meshes = [x for x in cmds.ls(typ='mesh', noIntermediate=True) if not cm.tests.shapes.mesh.isEmpty(x)]
    
    # make sure there are meshes in the scene
    if not len(meshes):
    	print "# Warning: No meshes in scene"
        return False, 0, 0, [], []
                
    batch = cmds.about(batch=True)
    if not batch:
        # put a progress bar in 
        gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
    
        cmds.progressBar(
            gMainProgressBar, 
            edit=True, 
            beginProgress=True, 
            isInterruptable=True, 
            status='checking for overlapping vertices...', 
            maxValue=len(meshes) )

    for mesh in meshes:
        
        if not batch:
            if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True ) :
                break
            cmds.progressBar(gMainProgressBar, edit=True, step=1)
        
        if verbose:
            print mesh
            
        numverts = int(cmds.polyEvaluate(mesh, v=1))
#        if verbose:
#            print '%s has %d vertices' % (mesh, numverts)
        
        # store vertex positions and indices in a dict
        # in the form {(x,y,z):[index,], }
        Dindex = {}
        Ddups = {}
        for i in range(numverts):
            #t = tuple(cmds.xform('%s.vtx[%d]' % (mesh, i), query=True, worldSpace=True, translation=True))
            # pointPosition is twice as fast as xform
            t = tuple(cmds.pointPosition('%s.vtx[%d]' % (mesh, i)))
            if t in Dindex.keys():
                Dindex[t].append(i)
            else:
                Dindex[t] = [i]
#            if verbose:
#                 print 'Dindex :', len(Dindex.keys())
#                 print 'Ddups :', len(Ddups.keys())
                 
            # we now have something like
            # {(-1.0, 0.0, 1.0): [1], (-1.0, 0.0, -1.0): [0], (1.0, 0.0, -1.0): [2, 3]}        
        
        # find vertex positions that are duplicates
        Ddups = dict((k, v) for k, v in Dindex.iteritems() if len(v) > 1)
#        if verbose:
#            print 'Ddups : ', Ddups        
        numberofdups = len(Ddups.keys())
        # this is the filtered version of the dict and looks like
        # {(1.0, 0.0, -1.0): [2, 3]}
        if numberofdups > 0:
            # fail the test
            result = True
#            if verbose:
#                print '%s has %d sets of duplicates' % (mesh, numberofdups)
            
            # increment object count and add parent of mesh to list of objects     
            Lobjects.append(cmds.listRelatives(mesh, parent=True))
            
            for v in Ddups.values():
                Ltmpvtx = []
                # every entry in the dic has at least >1 vertices
                for vtx in v:
                    Ltmpvtx.append('%s.vtx[%d]' % (mesh, vtx))
                # 
                Lvertices.extend(Ltmpvtx)
        
            # flatten the list
            sel = [item for sublist in Lvertices for item in sublist]
    
    if not batch:
        # kill the progressBar
        cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
        
    # select the overlapping vertices
    try:
        cmds.select(Lvertices)
    except TypeError:
#        if verbose:
#            print 'Nothing to select'
        pass
    # print execution time
    print '%-24s : %.6f seconds' % ('vtx.coincident.run()', (float(time.time())-t0))
    return result, len(Lvertices), len(Lobjects), Lvertices, Lobjects

