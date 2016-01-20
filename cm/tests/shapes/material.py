import time

from maya import cmds as cmds
import cm.tests.shapes.mesh

def getShader(*args, **kwargs):
    """ Return the material the given object is using. works in simple cases, may fail when using render layers and renders that 
    assume a different connection than the simple:  shape.instObjGroups -> shadingEngine.dagSetMembers shader.outColor -> shadingEngine.surfaceShader   
    
    ignores per-face materials, render passes, render layers 
    
    Connections for mr materials to shadingEngine.miMaterialShader like mrshader.message -> shadingEngine.miMaterialShader, for example mia_material_x2.message" "mia_material_x2SG1.miMaterialShader ARE taken into account. Switching the renderer will affect the results; mr materials 
    are not rendered by the Maya SW and HW renderer, and mr uses .miMaterialShader rather than .surfaceShader
    
    Used in test 15. Textures/Materials included  
    """    
    
    from maya import cmds as cmds
    verbose = cmds.optionVar(query='checkmateVerbosity')
    
    object = args[0]
    #object =  'pTorusShape1'
    material = None
    SG = ''
    parent = cmds.listRelatives(object, parent=True)[0]
    L = cmds.listHistory(object, future = True)
    if verbose:
        print object, L
        print '#'*10
    try:
        # find nodes of type shdingEngine in L
        SG = dict(zip(map(cmds.nodeType, L), L))['shadingEngine']
    except KeyError:
        pass # material = None  
        
    renderer = cmds.getAttr('defaultRenderGlobals.currentRenderer')
    
    if SG:
        if renderer == 'mentalRay':
            plug = SG+'.miMaterialShader'
            plug2 = SG+'.surfaceShader'
        else:
            plug = SG+'.surfaceShader'
            plug2 = SG+'.miMaterialShader'
    
        # print  'object: %s -> material: %s ' % (object, SG)
        try:
            material = cmds.listConnections(plug)[0] 
        except TypeError:
            try:
                material = cmds.listConnections(plug2)[0] 
            except TypeError:
                material =''
            pass
            
    if verbose:
        print  '%s -> %s ' % (parent , material)
    return (parent , material)


def run():
    """ find objects with no or default material 
    ---
    run -> boolean, list, list
    """
    t0 = time.time()
    result = False
    d = dict()
    objectswithoutmaterials = []
    objectswithdefaultmaterials = []
    meshes = [x for x in cmds.ls(typ='mesh', noIntermediate=True) if not cm.tests.shapes.mesh.isEmpty(x)]
    surfaces = cmds.ls(type='nurbsSurface', noIntermediate=True)
    subdivs = cmds.ls(type='subdiv', noIntermediate=True)
    geo = []
    geo.extend(meshes)
    geo.extend(surfaces)
    geo.extend(subdivs)

    for shape in geo:
        (node, material) = getShader(shape, verbose=False)
        d[node] = material
    for (k, v) in d.iteritems():
        if v == None:
            objectswithoutmaterials.append(k)
        if v == 'lambert1':
            objectswithdefaultmaterials.append(k)
    if len(objectswithoutmaterials):
        result = True
    if len(objectswithdefaultmaterials):
        result = True
    print '%-24s : %.6f seconds' % ('material.run()', (float(time.time())-t0))
    return  result, objectswithoutmaterials, objectswithdefaultmaterials    
