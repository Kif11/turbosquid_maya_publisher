import time
import inspect


from maya import cmds as cmds
import cm.tests.shapes.mesh

def run(*args, **kwargs):
    """Show Poly and Vertex count for entire scene.
    This test returns the results of the polyEvaluate command. The results may 
    not match those of the Poly Count head-up display. That is not an error. 
    The heads-up display only shows the count for what can be seen in the 
    viewport, which gives different results than this test if not all objects 
    are visible. 
    ---
    This test will fail if the inspector fails to enter the correct <em>expected</em> face and poly count. 
    Show proper Poly and Vertex count for entire scene
    Returns False and None if the number of faces and vertices in the scene 
    matches the face and vertex arguments. I the arguments do not match, 
    return True and an error message.
    disabling the face/vertex count is done as follows:
    polyvertexcount(faces=0, vertices=0)
    Keyword arguments:
    faces -- number of faces, return False if not matched
    vertices -- number of vertices, return False if not matched
    verbose -- print stats
    
    polyvertexcount([faces=int], [vertices=int], [verbose=boolean]) -> boolean, dict , string
    """
    t0 = float(time.time())
    valid_kwargs = ['faces','vertices', 'verbose']
    for k, v in kwargs.iteritems():
        if k not in valid_kwargs:
            raise TypeError("Invalid keyword argument %s" % k)  
    
    result = False
    err = []
    verbose = False
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
        'edgeComponent': 0}
    
    # ignore empty meshes from Shave and a Haircut for example, 
    # that cause Maya to crash
    meshes = [x for x in cmds.ls(typ='mesh', noIntermediate=True) if not cm.tests.shapes.mesh.isEmpty(x)]
    try:
        cmds.select(meshes)
    except TypeError:
    	print "# Warning: No meshes in scene"
    	
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

    # meshes = cmds.ls(typ='mesh', noIntermediate=True)
    meshes = [x for x in cmds.ls(typ='mesh', noIntermediate=True) if not cm.tests.shapes.mesh.isEmpty(x)]
    if not meshes:
    	result = False
    	err = [['Scene contains no polygon meshes'],]
    	return result, polyStats, err
    
    polyStats = cmds.polyEvaluate(meshes)
    # Prompt for face count if not provided    
    try:
        faces = kwargs['faces']
    except KeyError:
        cmds.promptDialog(message='number of faces')
        try: 
        	faces = int(cmds.promptDialog(query=True, text=True))
        except ValueError:
        	err = '# Error: not a valid face count #'
        	result = None
        	return result, err
        if verbose:
            print faces
    # prompt for vertext count if not provided
    try:
        vertices = kwargs['vertices']
    except KeyError:
        cmds.promptDialog(message='number of vertices')
        try: 
        	vertices = int(cmds.promptDialog(query=True, text=True))
        except ValueError:
        	err = '# Error: not a valid vertex count #'
        	result = None
        	return result, err
        if verbose:
            print vertices
    if verbose:
        for k,v in polyStats.iteritems():
            print k,v

    scene_vertices = polyStats['vertex']
    #scene_vertexcomponent = polyStats['vertexComponent']
    #scene_shells = polyStats['shell']
    #scene_triangles = polyStats['triangle']
    #scene_facecomponents = polyStats['faceComponent']
    scene_faces = polyStats['face']
    #scene_trianglecomponent = polyStats['triangleComponent']
    #scene_edges = polyStats['edge']
    #scene_uvcoords = polyStats['uvcoord']
    #scene_uvcomponents = polyStats['uvComponent']
    #scene_edgecomponents = polyStats['edgeComponent']
    
    # if the face count is wrong
    if faces != 0 and scene_faces != faces:
        result=True
        err.append(['# FAIL: Scene face count: %s (provided)is not %s (found)#' % (scene_faces, faces)])
        
    # if the vertex count is wrong
    if vertices !=0 and scene_vertices != vertices:
        result=True
        err.append(['# FAIL: Scene vertex count: %s (provided) is not %s (found)#' % (scene_vertices, vertices)])   
    # print execution time
    print '%-24s : %.6f seconds' % ('stats.poly.run()', (float(time.time())-t0))    
    return result, polyStats, err
