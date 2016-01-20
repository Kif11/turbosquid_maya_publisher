# standard library imports
import re
import os
import sys
import time
import getpass


# related third party imports

#local application/library specific imports
from maya import cmds as cmds
from maya import mel as mel

import cm.tests.shapes.mesh

def run(*args, **kwargs):
    """Detect flipped (reversed) normals. Find polygon objects with 
    normals that point away from the camera as long as that camera is outside 
    the object. Any objects found should be subject to a visual inspection.
    The test is unable to determine the proper normal direction for flat 
    objects. This test may give seemingly false positives if a node's parent 
    transforms are scaled by a negative value. 
    ---
    To fix a scene, run [Polygons] Normals->Reverse
    return result, 
        len(nonconformingfaces), 
        len(reversedmeshes) nonconformingfaces, 
        reversedmeshes,  
        err
    has_flippednormals([verbose=boolean]) -> boolean, int, int, list, list list
    """
    t0 = float(time.time())
    valid_kwargs = ['verbose', 'diag']
    for k, v in kwargs.iteritems():
        if k not in valid_kwargs:
            raise TypeError("Invalid keyword argument %s" % k)  
    result = False
    err = list()
    verbose = False
    batch = cmds.about(batch=True)
    # verbose defaults to False if verbose option not set in menu 
    # or specified in cmdline
    try:
        verbose = kwargs['verbose']
        print 'verbose is:', verbose
    except KeyError:
    	verbose = False
    	if cmds.optionVar(exists='checkmateVerbosity'):
    		verbose = cmds.optionVar(query='checkmateVerbosity')
        
    try:
        diag = kwargs['diag']
    except KeyError:
    	diag = False

    # require OpenMaya for vector math
    import maya.OpenMaya as om

    result=False
    # meshes = cmds.ls(type='mesh')
    meshes = [x for x in cmds.ls(typ='mesh', noIntermediate=True) if not cm.tests.shapes.mesh.isEmpty(x)]
    cmds.select(clear=True)
    
    # make sure undo is on
    cmds.undoInfo( state=True, infinity=True )
    # set up necessary plug-ins
    if not cmds.pluginInfo('nearestPointOnMesh', query=True, loaded=True):
        try:
           cmds.loadPlugin('nearestPointOnMesh')
        except NameError:
            pass
    err = list()
    nonconformingfaces= list()
    reversedmeshes = list()
    if not batch:
        # put a progress bar in 
        try:
            gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
        except RuntimeError:
            pass
        
    if len(meshes) < 1:
        err.append(['#Warning: No meshes in scene'])
        return result, 0, 0, [], [],  err
    
    if not batch:
        try:
            cmds.progressBar(
                gMainProgressBar, 
                edit=True, 
                beginProgress=True, 
                isInterruptable=True, 
                status='checking for reversed normals...', 
                maxValue=len(meshes) )
        except UnboundLocalError: 
            pass
    for mesh in meshes:
        if not batch:
            if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True ) :
                break
            cmds.progressBar(gMainProgressBar, edit=True, step=1)
        
        
        if verbose:
            print mesh
        # unlock normals, not spec'd but should be in here
        cmds.polyNormalPerVertex(mesh, ufn=True)
        
        # first check that all normals are conformed 
        # this requires undo 
        # if conform gives a selection, we know that not all normals conform
        cmds.select(mesh, replace = True)
        faces = cmds.polyListComponentConversion(toFace=True)
        
        # polyNormal will select and reverse the nonconforming faces or do 
        # nothing
        # deselect the mesh, keep only faces, if any
        try:
        	cmds.polyNormal(faces, normalMode=2, userNormalMode=0, ch=0)
        except TypeError:
        	pass

        cmds.select(mesh, deselect=True)
        try:
            selection = cmds.ls(selection=True, flatten=True)
        except TypeError:
            pass
        ########################################################################
        # if we have selected faces, we can stop at this point, because it is 
        # not clear what the right 
        # orientation of the normals is, assume the selection is correct
        # and is only faces (needs additional check)
        if len(cmds.ls(selection=True, flatten=True)):
            
            result = True          
            nonconformingfaces.extend(selection)
            
            # should probably reverse the faces again
            cmds.polyNormal(selection, normalMode=0, userNormalMode=0, ch=0)
            # continue with the next loop
            
            continue
        # only continue if there are no nonconforming normals, 
        # we now only have an objects that is completely reversed 
        else:
            # find a point that is guaranteed to be outside the object
            if verbose:
                print 'checking mes:h %s' % mesh
            p = cmds.exactWorldBoundingBox(mesh)
            
            point = tuple([
                (p[3] + 0.1), 
                (p[4] + 1.0), 
                (p[5] + 0.1)])
            if verbose:
                print point
            if diag:
                cmds.spaceLocator(p=point)
            # the result of nearestPointOnMesh is a nearestPointOnMesh node
            nearestnode = cmds.nearestPointOnMesh(mesh, inPosition=point)
            if verbose:
                print nearestnode
            # get the normal, face index and position at the nearest point
            # getattr resuturns a list of tuples, take the first index 
            nearestnormal = cmds.getAttr('%s.normal' % nearestnode)[0]
            if verbose:
                print 'nearest normal: ', nearestnormal
            nearestposition = cmds.getAttr('%s.position' % nearestnode)[0]
            if verbose:
                print 'nearest position: ', nearestposition
            if diag:
                cmds.spaceLocator(p=nearestposition)
            nearestfaceindex = cmds.getAttr('%s.nearestFaceIndex' % nearestnode)
            face = '%s.f[%d]' % (mesh, nearestfaceindex)  
            cmds.select(face) 
            if verbose:
                print 'face: %s' % face        
            cmds.delete(nearestnode)
            # select the nearest face (is this really necessary?)
            # cmds.select('%s.f[%s]' % (mesh,nearestfaceindex))
            # figure out the direction which the facenormal should be looking 
            # (should be toward point)
            # the differnce between point and nearestposition is a vector
            delta = ((point[0] - nearestposition[0]), 
                    (point[1] - nearestposition[1]),
                    (point[2] - nearestposition[2]))
            # to avoid selecting a point at which the normal is difficult to determine
            # find the centroid of the face and use that to find the direction and use the normal of the face,
            # not the normal at the nearest point
            (label, num, nearestnormalX, nearestnormalY, nearestnormalZ) = cmds.polyInfo(face,fn=True)[0].split()
             
            # there's no need to normalize it
            
            facenormal = om.MVector(float(nearestnormalX), float(nearestnormalY), float(nearestnormalZ) )
            direction = om.MVector(delta[0], delta[1], delta[2])
            if verbose:
                print 'facenormal :', facenormal
                print 'direction  :', direction
            # Calculate dot product as an indication of how similar the two 
            # vectors are. acosd(dot) gives the angle between the two, 0 means 
            # identitcal, -1 means they're at a 180 degree angle
            # positive values mean the face normal is looking out, 
            # negative means the normal is reversed
            dot = facenormal*direction
            if verbose:
                print 'dot: %f5.2' % dot
            
            if dot > 0:
                pass
            else:
                reversedmeshes.append(mesh)
                result = True          
                err.append('# FAIL : %s has reversed normals #' % mesh)
                
    # kill the progressBar
    if not batch:
        cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
    
    # turn off selection constraints
    cmds.polySelectConstraint(disable=True)
    # to make it easy to fix the scene select everything that is reversed
    
    cmds.select(clear=True)
    try:
        cmds.select(nonconformingfaces, add=True)
    except TypeError: 
        pass
    try:
        cmds.select(reversedmeshes, add=True)
    except TypeError:
        pass     
    # print execution time
    print '%-24s : %.6f seconds' % ('f.normals.run()', (float(time.time())-t0))
    return result, len(nonconformingfaces), len(reversedmeshes), nonconformingfaces, reversedmeshes,  err

