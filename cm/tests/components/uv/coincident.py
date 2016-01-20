import time


from maya import cmds as cmds
from maya import mel as mel

import cm.tests.shapes.mesh

def run(*args, **kwargs):
    """Detect overlapping UV faces. This test finds faces that have uvs at the 
    (exact) same positions as another face. This test does not find faces that 
    only partially overlap.
    ---
    7. Detect overlapping UV faces. Show/Highlight them.
    polyListComponentConversion is expensive. 2do: look for alternative
    
    keyword arguments:
    - verbose (boolean) 
    - selected (boolean)
    - precision (int]
    """
    t0 = float(time.time())
    batch = cmds.about(batch=True)
    
    # set up keyword arguments
    valid_kwargs = ['verbose', 'selected', 'precision']
    for k, v in kwargs.iteritems():
        if k not in valid_kwargs:
            raise TypeError("Invalid keyword argument %s" % k)  
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
    try:
        selected = kwargs['selected']
    except KeyError:
        	selected = False
    else:
        pass  
        
    try:
        selected = kwargs['precision']
    except KeyError:
        	precision = 6
    else:
        pass  
    
    # set up return values    
    result = False
    sel = list()
     
    Lobjects = []
    Lvertices = []
    uvfaces = []   
    if selected:
        #meshes = cmds.ls(typ='mesh', selection=True, noIntermediate=True)
        meshes = [x for x in cmds.ls(typ='mesh', selection=True, noIntermediate=True) if not cm.tests.shapes.mesh.isEmpty(x)]
    else:    
        #meshes = cmds.ls(typ='mesh', noIntermediate=True)
        meshes = [x for x in cmds.ls(typ='mesh', noIntermediate=True) if not cm.tests.shapes.mesh.isEmpty(x)]
        
    # put a progress bar in 
    if not batch:
        try:
            gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
        except RuntimeError:
            pass
        
    
    if not len(meshes):
        return (False, 0, [], 0, [])
    if not batch:
        cmds.progressBar(
            gMainProgressBar, 
            edit=True, 
            beginProgress=True, 
            isInterruptable=True, 
            status='checking for overlapping UVs...', 
            maxValue=len(meshes) )
                	
    for mesh in meshes:
        if not batch:
            if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True ) :
                break
            cmds.progressBar(gMainProgressBar, edit=True, step=1)
        
        # The dictionary with position: [index,]  needs to be cleared for each mesh
        Dindex = {} 
        # as does the dict with Duplicates
        Ddups = {}
         
        if verbose:
            print 'testing %s' % mesh
    
        uvsets = cmds.polyUVSet(mesh, query=True, allUVSets=True)
        for uvset in uvsets:
            # uvset = [u'map'][0]
            # get the number of uvs in the set
            numuvs = cmds.polyEvaluate(mesh,uvSetName=set, uvcoord=True )
            for i in range(numuvs):
                # get the UV positions of each UV
                # and store the indices per position in a list
                u,v = cmds.polyEditUV('%s.map[%d]' % (mesh,i), query=True)
                t = (round(u, precision), round(v, precision))
                if verbose:
                    pass #print i, t     
                if t in Dindex.keys():
                    Dindex[t].append(i)
                else:
                    Dindex[t] = [i]            
                   
            Ddups = dict((k, v) for k, v in Dindex.iteritems() if len(v) > 1)
            if verbose:
                print 'Ddups : ', Ddups        
            numberofdups = len(Ddups.keys())
            # this is the filtered version of the dict and looks like
            # {(1.0, 0.0, -1.0): [2, 3]}
            if numberofdups:
                # fail the test
                result = True
                if verbose:
                    print '%s has %d sets of duplicates' % (mesh, numberofdups)
                    print Ddups
                # increment object count and add parent of mesh to list of objects     
                Lobjects.append(cmds.listRelatives(mesh, parent=True))
                
                for v in Ddups.values():
                    Ltmpvtx = []
                    # every entry in the dic has at least >1 vertices
                    for vtx in v:
                        Ltmpvtx.append('%s.map[%d]' % (mesh, vtx))
                    # 
                    Lvertices.extend(Ltmpvtx)
            
                # flatten the list
                #sel = [item for item in Lvertices]
                #if verbose:
                #    print '#'*80
                #    print 'sel:'
                #    print sel
                #    print '#'*80
            try:
                # polyListComponentConversion is expensive. 2do: look for alternative
                uvfaces = cmds.polyListComponentConversion(sel, internal=True, fv=True, fe=True, fuv=True, fvf=True, tf=True)
            except TypeError:
                if verbose:
                    print 'nothing to select for overlapping UV faces'
            # flatten the list of UV faces
            uvfaces = cmds.ls(uvfaces, flatten=True)
            
            if verbose:
                print 'uv faces : ', uvfaces
    if not batch:
        # kill the progressBar
        cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
        
    try:
        cmds.select(uvfaces)
    except TypeError:
        if verbose:
            print 'Nothing to select'
    # print execution time
    print '%-24s : %.6f seconds' % ('uv.coincident.run()', (float(time.time())-t0))    
    return (result, len(uvfaces), uvfaces, len(Lvertices), Lvertices)

