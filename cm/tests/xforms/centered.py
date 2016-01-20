import time

from maya import cmds as cmds
import cm.utils.roots


def run(*args, **kwargs):
    """This test determines if objects at the top of the hierarchy are centered 
    at the world origin. Precision is 0.001. This test will only work as expected
    for objects that are perfectly symmetrical. Visual inspection is recommended 
    for organic models. 
    ---
    For each root level node, find the bounding box and determine if 
    the bounding box center in x and z == 0 (for a scene where upAxis == y)
    the bounding box center in x and y == 0 (for a scene where upAxis == z)
    
    Returns True/False, the number of off-center objects and a list
    
    Set Floor to True to test for objects proper positioned on the floor 
    Which is (y = 0) if y-up or (z = 0) if z-up 
    
    Arguments
        -verbose boolean # print messages
        -floor boolean # include testing for minY == 0
        
    is_centeredatorigin(verbose=boolean, floor=boolean) -> boolean, int, list 
    """
    
    t0=time.time()
    valid_kwargs = ['verbose', 'floor']
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
        
    try:
        floor = kwargs['floor']
    except KeyError:
        floor = False
        pass
       
    # get the up axis:
    axis =  cmds.upAxis(query=True, axis=True) 
    # find all the root transforms in the scene
    # ignore cameras
    Lignore = cmds.listRelatives(cmds.ls(cameras=True),parent=True)
    # ignore lights
    try:
        Lignore.extend(cmds.listRelatives(cmds.ls(lights=True),parent=True)) 
    except TypeError:
        pass
    
    transforms = [x for x in cm.utils.roots.get() if not x in Lignore]
    
    # temporarily make everything in the ignorelist Lignore invisble
    for x in Lignore :
        cmds.setAttr('%s.visibility' % x, 0)
    
    
    for transform in transforms:
        if verbose:
            print transform
        (bbMinX, bbMinY, bbMinZ, 
            bbMaxX, bbMaxY, bbMaxZ) = cmds.exactWorldBoundingBox(transform, ignoreInvisible=True)
        if verbose:
            print 'bbMinX: %f\nbbMinY: %f\nbbMinZ: %f\nbbMaxX: %f\nbbMaxY: %f\nbbMaxZ: %f\n ' % (bbMinX, bbMinY, bbMinZ, bbMaxX, bbMaxY, bbMaxZ)   
        if axis == 'y':
            centerX = round(( bbMaxX + bbMinX ) / 2.0, 3)
            centerZ =  round(( bbMaxZ + bbMinZ ) / 2.0, 3)
            if (floor and bbMinY !=0) or centerX != 0 or centerZ !=0:
                result = True
                err.append(transform)
            if verbose:
                print  'floor:%s\nbbMinY:%f\ncenterX:%f\ncenterZ:%f' % (floor, bbMinY, centerX,  centerZ)   
        if axis == 'z':
            centerX = ( bbMaxX + bbMinX ) / 2.0
            centerY = ( bbMaxY + bbMinZ ) / 2.0
            if (floor and bbMinZ !=0) or centerX != 0 or bbMinX != 0:
                err.append(transform)
                result = True
            if verbose:
                print (floor, bbMinZ, centerX, bbMinX)
    if len(err):
        cmds.select(err) 
        
    # make everything in the ignorelist Lignore visible again
    
    for x in Lignore :
        cmds.setAttr('%s.visibility' % x, 1 )
    # hide default cameras
    cmds.hide([u'front', u'persp', u'side', u'top'])
    print '%-24s : %.6f seconds' % ('xforms.centered.run()', (float(time.time())-t0)) 
    return result, len(err), err


