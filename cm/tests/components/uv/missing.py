import time


from maya import cmds as cmds
import cm.tests.shapes.mesh

def run():
    """Detect faces without uvs.  
    ---
    Show associated geometry for missingUVS
    returns True/False, the number of isolated vertices and a list of the isolated vertices
    has_unmappedfaces() -> (boolean, int, [mesh:v[id],])
    """
    t0 = float(time.time())
    verbose = cmds.optionVar(query='checkmateVerbosity')
    result=False
    # meshes = cmds.ls(type='mesh')
    meshes = [x for x in cmds.ls(typ='mesh', noIntermediate=True) if not cm.tests.shapes.mesh.isEmpty(x)]
    try:
        cmds.select(meshes)
    except TypeError:
    	print "# Warning: No meshes in scene"
    cmds.selectType( pf=True ) 
    cmds.polySelectConstraint(
        mode=3, # all and next
        type=0x0008, # faces
        textured=2, # unmapped
        )
    sel=cmds.ls(sl=True, fl=True)
    result =  (len(sel) > 0) or False
    cmds.polySelectConstraint(disable=True)
    try:
        cmds.select(sel)
    except TypeError:
    	pass 
    # print execution time
    print '%-24s : %.6f seconds' % ('uv.missing.run()', (float(time.time())-t0))
    return (result, len(sel), sel)



