import time
import inspect

from maya import cmds as cmds

def run():
    """Measure the scene bounding box for geometric objects in centimeters.
     ---
     units, bounding box, center and dimensions for scene
     sceneboundingbox() -> (string, 
            float, float, float, 
            float, float, float, 
            float, float, float, 
            float, float, float)
     """
    t0 = float(time.time())
    verbose = cmds.optionVar(query='checkmateVerbosity')
    
    units = cmds.currentUnit(query=True, linear=True)
    if units != 'cm' :
        cmds.currentUnit(linear='cm')
    	#raise InvalidLinearUnits, "current linear unit is not centimeters"
    transforms = cmds.ls(transforms=True)
    geometry =   cmds.ls(geometry=True)
    try:
    	bbox = cmds.exactWorldBoundingBox(geometry) 
    except TypeError:
        return (units, 
            0, 0, 0, 
            0, 0, 0, 
            0, 0, 0, 
            0, 0, 0)
    
    (bbMinX, bbMinY, bbMinZ, 
        bbMaxX, bbMaxY, bbMaxZ) = cmds.exactWorldBoundingBox(geometry)
    width = bbMaxX - bbMinX
    height = bbMaxY - bbMinY
    depth = bbMaxZ - bbMinZ
    centerX = ( bbMaxX + bbMinX ) / 2.0
    centerY = ( bbMaxY + bbMinY ) / 2.0
    centerZ = ( bbMaxZ + bbMinZ ) / 2.0
    print '%-24s : %.6f seconds' % ('stats.bbox.run()', 
        float(time.time())-t0
    ) 
    return (units, 
            bbMinX, bbMinY, bbMinZ, 
            bbMaxX, bbMaxY, bbMaxZ, 
            centerX, centerY, centerZ, 
            width, height, depth)
