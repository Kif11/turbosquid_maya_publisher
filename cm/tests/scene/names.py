
# standard library imports
import re
import os
import sys
import time
import getpass
from functools import partial

# related third party imports

#local application/library specific imports
from maya import cmds as cmds
from maya import mel as mel



def texturefilenames():
    files = cmds.ls(typ='file')
    Dtfn = {}
    for file in files:
        Dtfn[file] =    cmds.getAttr('%s.fileTextureName' %file)
    return Dtfn
    
    
def fix_defaultnames(objectswithdefaultnames):
    """Find objects with names that Maya uses when the user creates an object 
    and fails to rename it. 
    ---
    Naming (detect default names). 
    Open list window with object names for review.
    fix_defaultobjectnames(list) create a UI for renaming objects with 
    invalid (default) names.
    """
    verbose = cmds.optionVar(query='checkmateVerbosity')
    
    if cmds.window('showObjectNamesWin', exists=True):
        cmds.deleteUI('showObjectNamesWin')
    win = cmds.window('showObjectNamesWin', 
        width =340, 
        height=400, 
        title="Objects with default names")
    cmds.scrollLayout(childResizable=True)
    cmds.columnLayout(adjustableColumn=True)
    numitems = 0
    for item in objectswithdefaultnames:
        if numitems < 500:
            numitems = numitems + 1
            # cmds.button(label='select', command='cmds.select(\'%s\')' % item)
            cmds.nameField(object=item, 
                receiveFocusCommand='cmds.select(\'%s\')' % item)
        else :
            break
    cmds.showWindow(win)
    
    
def run(*arg, **kwargs):
    """ Detect default names.
    ---
    Open list window with 
    object names for review.
    has_defaultnames() -> boolean, int, list
    """
        
    t0 = float(time.time())
    
    valid_kwargs = ['verbose', 'type']
    for k, v in kwargs.iteritems():
        if k not in valid_kwargs:
            raise TypeError("Invalid keyword argument %s" % k)  
    
    try:
        verbose = kwargs['verbose']
    except KeyError:
    	verbose=False
    	if cmds.optionVar(exists='checkmateVerbosity'):
    		verbose = cmds.optionVar(query='checkmateVerbosity')
    else:
        verbose=False
    
    try:
        type = kwargs['type']
    except KeyError:
    	type = None
    else:
        pass
    
    numberofobjects = 0    
    result = False
    err = None
    ignore = ['persp', 'top', 'front', 'side', 'lambert1', 'particleCloud1']
    names= ['Box', 'Char', 'Circle', 'Cylinder', 'Plane', 'Sphere', 'Text_', 'ambientLight', 'annotation',
    'areaLight',  'blinn', 'phongE', 'phong', 'rampShader', 'nurbsCube', 'camera', 'curve', 'directionalLight', 
    'effector', 'file', 'fluid', 'group', 'ikHandle1', 'joint', 'lambert', 'locator', 'null', 'nurbsCircle', 
    'nurbsCone', 'nurbsCube', 'nurbsCylinder1 nurbsPlane', 'nurbsSphere', 'nurbsSquare', 'nurbsTorus', 'ocean',
     'particle', 'pCone', 'pCube', 'pCylinder', 'pHelix1 pPipe', 'pPlane', 'pPrism', 'pPyramid', 'pSolid', 'pSphere', 
     'pTorus', 'plane', 'pointLight', 'polySurface', 'Rectangle', 'shotFar', 'shotMid', 'shotNear', 'spotLight', 
     'stereoCamera', 'strokeBrush', 'subdivCone', 'subdivCube1', 'subdivCylinder', 'subdivPlane', 'subdivSphere', 'subdivTorus', 'volumeLight', 'Object']

    defaultnames = dict()
    foundnames = dict()
    foundnodes = dict()
    #foundnodes = {'a': ['b','c']}
    
    if type == 'materials':
        nodes = [x for x in cmds.ls(materials=True) if not x in ignore]
    elif type == 'textures':
        nodes = [x for x in cmds.ls(type='file') if not x in ignore]
    elif type == None:
        nodes = [x for x in cmds.ls(transforms=True) if not x in ignore]

    if cmds.text("NameText", q = True, exists = True):
        cmds.deleteUI("NameText")
    if cmds.separator("SepNameText", q = True, exists = True):
        cmds.deleteUI("SepNameText")
        
    cmds.text("NameText", p = "ReviewLayout", label = " Please rename the following nodes")
    cmds.separator("SepNameText")
    for node in nodes:
        for name in names:
            # match one or more numbers at the end of the name
            exp = ''.join([name, "\d+$"])
            if (re.compile(exp).match(node)) and  True or False:
                result=True
                numberofobjects += 1
                #Name Field
                cmds.nameField( node + "Text", p = "ReviewLayout", object = node, enable = True, rfc = partial(cmds.select, node))
                #print node
                # count the found name
                #countnames[name] = countnames.get(name, 0) + 1
                if foundnames.get(name):
                    foundnames.get(name).append(node)
                else:
                    foundnames[name] = [node,]
                    #foundnames[name] = foundnames.get(name, 0) + 1
                # print 'node : %s -> %s' % (node, name)
                # if there is an entry for node in found nodes, append the name to the list of names for node
                if foundnodes.get(node):
                    foundnodes.get(node).append(name)
                else:
                    foundnodes[node] = [name,]
    if numberofobjects == 0:
        cmds.deleteUI("NameText")
        cmds.deleteUI("SepNameText")
    for k, v in foundnames.iteritems():
        if verbose:
            print '%s  -> found %s' % (k, len(v))
        cmds.select(v, add=True)
    print '%-24s : %.6f seconds' % ('scene.names.run()', (float(time.time())-t0)) 
    return result, numberofobjects, foundnames

        

