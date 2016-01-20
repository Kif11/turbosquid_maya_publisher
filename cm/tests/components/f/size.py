import time

from maya import cmds as cmds
import cm.tests.shapes.mesh

def run(*args, **kwargs):
    """Ngons or n-sided faces are faces with more 
    than 4 edges. This test will fail if any polygonal object contains such a 
    face. The test will also fail if more than 10% of all faces are triangles.
    ---
    Detect Ngons? How many? Show/Highlight them. 
    returns True/False and the number of nsided faces in the scene and a list of all n-sided faces
    has_ngons() -> boolean, int, list, dict, list
    return (result, len(sel), sel, polyStats, err)
    """
    t0 = float(time.time())
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
    result=False
    err = list()
    polyStats = {'vertexComponent': 0, 
        'shell': 0, 
        'triangle': 0, 
        'faceComponent': 0, 
        'vertex': 0, 
        'face': 0, 
        'triangleComponent': 0, 
        'edge': 0, 
        'uvcoord': 0, 
        'uvComponent': 0, 
        'edgeComponent': 0,
        'tris': 0,
        'quads': 0,
        'n-sided': 0,
        }
            
    meshes = cmds.ls(type='mesh', noIntermediate=True)
    meshes = [x for x in cmds.ls(typ='mesh', noIntermediate=True, long=True) if not cm.tests.shapes.mesh.isEmpty(x)]

    try:
        cmds.select(meshes)
    except TypeError:
    	print "# Warning: No meshes in scene"
    	err.append(['#Warning: No meshes in scene'])
        return (False, 0, [], polyStats, err)
    polyStats = cmds.polyEvaluate(meshes)
    scene_faces = polyStats['face']
    # selection constraint on mode 3 (all and next) 0x0008(mesh) size 3 (nsided)
    cmds.selectType( pf=True ) 
    cmds.polySelectConstraint(mode=3, type=0x0008, size=3)
    cmds.polySelectConstraint( m=3, t=8, sz=3 )
    sel=cmds.ls(sl=True, fl=True)
    cmds.polySelectConstraint(disable=True)
    result =  (len(sel) > 0) or False
    
    # tri/quad/n-sided 
    # Tris
    cmds.select([x for x in cmds.ls(typ='mesh', noIntermediate=True, long=True) if not cm.tests.shapes.mesh.isEmpty(x)])
    cmds.selectType( pf=True )
    cmds.polySelectConstraint( mode=3, type=8, size=1 ) # to get triangles
    scene_triangles = len(cmds.ls(selection=True, flatten=True))
    cmds.polySelectConstraint(disable=True)
    polyStats['tris'] = scene_triangles
    # Quads
    cmds.select([x for x in cmds.ls(typ='mesh', noIntermediate=True, long=True) if not cm.tests.shapes.mesh.isEmpty(x)])
    cmds.selectType( pf=True )
    cmds.polySelectConstraint( mode=3, type=8, size=2 )
    scene_quads=len(cmds.ls(selection=True, flatten=True))
    polyStats['quads']=scene_quads
    # N-sided
    cmds.select([x for x in cmds.ls(typ='mesh', noIntermediate=True, long=True) if not cm.tests.shapes.mesh.isEmpty(x)])
    cmds.selectType( pf=True )
    if verbose: print 'line 461'
    cmds.polySelectConstraint( mode=3, type=8, size=3 ) # to get ngons
    scene_nsided = len(cmds.ls(selection=True, flatten=True))
    sel=cmds.ls(sl=True, fl=True)
    if verbose: print 'line 465'
    cmds.polySelectConstraint(disable=True)
    result =  (len(sel) > 0) or False
    polyStats['n-sided']=scene_nsided
    if verbose: print 'line 469'
    if verbose:
        print polyStats
    
    if verbose:
        for k,v in polyStats.iteritems():
            print k,v
    err = list()        
    
    # if more than 10% of faces are triangles
    try:
        trifaceratio = float(scene_triangles)/float(scene_faces)
    except ZeroDivisionError:
        trifaceratio = 0.0
    if float(scene_triangles)/float(scene_faces) > 0.1 :
        err.append(['# FAIL: %.2f percent of faces are triangles #' % (trifaceratio*100.0)])
        result = True
    # if there are n-sided faces in the scene
    if int(scene_nsided) > 1 :
        err.append(['# FAIL: %d faces are n-sided #' % int(scene_nsided)  ]) 
        result = True
        	           
    print '%-24s : %.6f seconds' % ('f.size.run()', (float(time.time())-t0)) 
    return (result, len(sel), sel, polyStats, err)

