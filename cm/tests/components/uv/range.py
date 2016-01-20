import time

from maya import cmds as cmds
import cm.tests.shapes.mesh

def minmaxUV(mesh):
    """
    minmaxUV(string) -> float, float, float, float
    """
    sel =  cmds.ls(cmds.polyListComponentConversion(mesh, toUV=True), flatten=True)
    cmds.select(sel, replace=True)
    (minU, maxU), (minV, maxV) = cmds.polyEvaluate(boundingBoxComponent2d=True)
    return round(minU, 3), round(maxU, 3), round(minV, 3), round(maxV, 3)

def run():
    """
    This test checks if the UVs fit with the 0:1 range. 
    Objects with UVs that have UV coordinates < 0 or > 1  fail. 
    ---
    UVbbox -> boolean list
    """
    t0 = time.time()
    result = False
    D = {}
    meshes = [x for x in cmds.ls(typ='mesh', noIntermediate=True) if not cm.tests.shapes.mesh.isEmpty(x)]
    for mesh in meshes:
        (minU, maxU, minV, maxV) = minmaxUV(mesh)
        if minU < 0 or maxU > 1 or minV < 0 or maxV > 1:
            result =True
            D[mesh] = minmaxUV(mesh)
    print '%-24s : %.6f seconds' % ('uv.range.run()', (float(time.time())-t0)) 
    return result, D