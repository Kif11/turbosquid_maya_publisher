import maya.cmds as cmds

def SetWireframeRender(Name):
    
    try:cmds.delete("WireShader")
    except:pass
    
    try:cmds.delete("WireShaderSG")
    except:pass
    
    try:cmds.delete("WireSet")
    except:pass
    
    try:cmds.delete("WireMap")
    except:pass
    
    try:cmds.delete("WirePlacer")
    except:pass
    
    
    
    material = cmds.shadingNode('lambert', asShader = True, name='WireShader')
    SG = cmds.sets(renderable = True, noSurfaceShader = True, empty = True, name = 'WireShaderSG')   
    cmds.connectAttr((material + '.outColor'),(SG + '.surfaceShader'),f=1)
    
    try:
        cmds.select(Name)
        cmds.sets(cmds.ls(selection = True), forceElement = SG, name = "WireSet")
        print "created wire set"
    except:
        print "Failed to create wire set"
    
    cmds.setAttr("WireShader.color", 0.34902, 0.34902, 0.34902, type = "double3")
    
    try:
        cmds.setAttr("miDefaultOptions.miRenderUsing", 2)
    except:
        print "miDefaultOptions.miRenderUsing, attribute was not found"
        
    cmds.setAttr("miDefaultFramebuffer.contourEnable", 1)
    cmds.setAttr("miDefaultOptions.contourPriData", 1)
    cmds.setAttr("miDefaultFramebuffer.contourSamples", 10)
    cmds.setAttr("miDefaultFramebuffer.contourFilterSupport", 2)
    
    cmds.setAttr("WireShaderSG.miContourEnable", 1)
    cmds.setAttr("WireShaderSG.miContourWidth", 0.85)
    cmds.setAttr("WireShaderSG.miContourColor", 0, 0, 0, type = "double3")

def SetWireframeRenderVray(Name):
    try:cmds.delete("WireShader")
    except:pass
    
    try:cmds.delete("WireShaderSG")
    except:pass
    
    try:cmds.delete("WireSet")
    except:pass
    
    try:cmds.delete("WireMap")
    except:pass
    
    try:cmds.delete("WirePlacer")
    except:pass
    
    material = cmds.shadingNode('VRayMtl', asShader = True, name='WireShader')
    cmds.shadingNode("VRayEdges", asTexture = True, name = "WireMap")
    cmds.shadingNode("place2dTexture", asUtility = True, name = "WirePlacer")
    cmds.connectAttr("WirePlacer.outUV", "WireMap.uv")
    cmds.connectAttr("WirePlacer.outUvFilterSize", "WireMap.uvFilterSize")
    cmds.connectAttr("WireMap.outColor", "WireShader.color")

    SG = cmds.sets(renderable = True, noSurfaceShader = True, empty = True, name = 'WireShaderSG')   
    cmds.connectAttr((material + '.outColor'),(SG + '.surfaceShader'),f=1)
    
    try:
        cmds.select(clear = True)
        cmds.select(Name)
        cmds.sets(cmds.ls(selection = True), forceElement = SG, name = "WireSet")
        print "created wire set"
    except:
        print "Failed to create wire set"
    
    cmds.setAttr("WireMap.edgesColor", 0.0196078, 0.0196078, 0.0196078, type = "double3")
    cmds.setAttr("WireMap.backgroundColor", 0.34902, 0.34902, 0.34902, type = "double3")
    cmds.setAttr("WireMap.pixelWidth", 0.85)

    
