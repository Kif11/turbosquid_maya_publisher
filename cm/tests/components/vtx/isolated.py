import time

from maya import cmds as cmds
import cm.tests.shapes.mesh

def run():
    """Detect Isolated Vertices. Isolated vertices are the result of deleting 
    edges with Delete rather than with the Delete Edge/Vertex. Using Delete 
    leaves the vertices in place that connected the deleted edge(s). This test 
    ignores vertices on borders, where having such vertices is not a problem.
    ---
    returns True/False, the number of isolated vertices and a list of the 
    isolated vertices
    has_isolatedvertices2() -> (boolean, int, list)
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
        type=0x0001, # vertices
        where=2, # inside
        order=2, # neighbours
        orderbound=[2,2] # min and max neighbours
        )
    sel=cmds.ls(sl=True, fl=True)
    cmds.polySelectConstraint(disable=True)
    result =  (len(sel) > 0) or False
    print '%-24s : %.6f seconds' % ('vtx.isolated.run()', (float(time.time())-t0)) 
    return (result, len(sel), sel)


def degenerate():
    """Detect Isolated Vertices. Isolated vertices are vertices that are not 
    connected to another vertex by two edges.
    --
    returns True/False, the number of isolated vertices and a list of the 
    isolated vertices
    has_isolatedvertices() -> (boolean, int, [mesh:v[id],])
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
        type=0x0001, # vertices
        where=2, # inside
        order=2, # neighbours
        orderbound=[0,1] # min and max neighbours
        )
    sel=cmds.ls(sl=True, fl=True)
    cmds.polySelectConstraint(disable=True)
    result =  (len(sel) > 0) or False
    print '%-24s : %.6f seconds' % ('isolated.run()', (float(time.time())-t0)) 
    return (result, len(sel), sel)
    
    
if __name__ == '__main__':
    run()

