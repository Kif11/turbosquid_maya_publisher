import maya.cmds as cmds 

import ShadersFile

import math

reload(ShadersFile)

class RenderLayerManagerClass():
    
    #Helper functions
    @staticmethod
    def EditLayer(settings, layers, ChangeRenderLayer = True):
        for layer in layers:
            if ChangeRenderLayer:
                cmds.editRenderLayerGlobals( currentRenderLayer = layer)
            for i in settings:
                    if i[1] == "RemoveFromLayer":
                        cmds.editRenderLayerAdjustment(i[0], remove = True)
                    else:
                        try:
                            if i[1] == "double3":
                                cmds.editRenderLayerAdjustment(i[0])
                                cmds.setAttr(i[0], i[2], i[3], i[4], type = i[1] )
                            elif i[1] == "string":
                                cmds.editRenderLayerAdjustment(i[0])
                                cmds.setAttr( i[0], i[2], type = i[1] )
                            elif i[1] == "none":
                                cmds.editRenderLayerAdjustment(i[0])
                                cmds.setAttr( i[0], i[2] )
                        except:
                            pass
                    
              
        if ChangeRenderLayer:
            cmds.editRenderLayerGlobals( currentRenderLayer = "defaultRenderLayer")
        
    @staticmethod
    def MaterialOverrides(shaderGroup, layers):
        for i in layers:
            cmds.editRenderLayerGlobals(currentRenderLayer = i)
            try:
                cmds.select( clear=True )
                cmds.select(cmds.getAttr("CMSettings.ModelName"))
                cmds.sets(cmds.ls(selection = True), forceElement = shaderGroup, e = True, n = i + "WireSet")    
            except:
                print "Failed to assign shader"
            cmds.editRenderLayerGlobals(currentRenderLayer = "defaultRenderLayer")
    
    @staticmethod
    def CreateShadowPlane():
        #Get the bounding box of the group
        RenderLayerManagerClass.ShowModel(Visibility = True)
        bbx = cmds.xform(cmds.getAttr("CMSettings.ModelName"), bb = True, q = True)
        RenderLayerManagerClass.ShowModel(Visibility = False)
        
        #Get the x-z diagonal
        diagonal = math.sqrt((bbx[3] - bbx[0])*(bbx[3] - bbx[0]) + (bbx[5] - bbx [2])*(bbx[5] - bbx [2])) 
        diagonal = math.sqrt((bbx[4]-bbx[1])*(bbx[4]-bbx[1]) + diagonal*diagonal)
        
        #Check to see if the plane already exists
        if not cmds.objExists("ShadowPlane"):
            #create the shadow plane
            cmds.polyPlane( name = "ShadowPlane", width = 1.5*diagonal, height = 1.5*diagonal, subdivisionsX = 1, subdivisionsY = 1 )
            
        cmds.editRenderLayerGlobals(currentRenderLayer = "defaultRenderLayer")
        cmds.sets( "ShadowPlane", forceElement = "ShadowSG", e = True)
    
    @staticmethod
    def RenderSettingsMR():
        ShadersFile.ShaderClass.CreateMRShadowMat()
        
        RenderLayerManagerClass.CreateShadowPlane()
                    
        RenderLayerManagerClass.EditLayer(settings = [
                                                      ['miDefaultFramebuffer.contourEnable', "none", 1 ],
                                                      ['miDefaultFramebuffer.contourSamples', "none", 3 ],
                                                      ['miDefaultFramebuffer.contourFilterSupport', "none", 1 ],
                                                      ["miDefaultOptions.contourPriData","none", 1],
                                                      ["miDefaultOptions.miRenderUsing", "none", 2]
                                                      ],
                                          layers = ["Wireframe","Subdivision_0","Subdivision_1"]
                                          )        
                
    @staticmethod        
    def RenderSettingsVray():
        
        #Set file path names
        cmds.setAttr("vraySettings.fileNamePrefix", "<Scene>_<Layer>", type = "string")
        RenderLayerManagerClass.EditLayer(settings = [["vraySettings.fileNamePrefix", "string", "<Scene>_<Layer><Camera>"]], 
                                          layers = ["Product","Wireframe"])
        RenderLayerManagerClass.EditLayer(settings = [["vraySettings.fileNamePrefix", "string", "<Scene>_<Layer>"]], 
                                          layers = ["UVs"])
        
        #Set Sqr Resolution
        RenderLayerManagerClass.EditLayer(settings = [
                                                      ['vraySettings.width', "none", 1200 ],
                                                      ['vraySettings.height', "none", 1200 ],
                                                      ['vraySettings.aspectRatio', "none", 1 ],
                                                      ],
                                          layers = ["SQRSignature"]
                                          )
    
        ShadersFile.ShaderClass.CreateVrayShadowMat()
        
        RenderLayerManagerClass.CreateShadowPlane()
                
        cmds.editRenderLayerGlobals(currentRenderLayer = "defaultRenderLayer")
         
    @staticmethod
    def CreateRenderLayers():
        cmds.editRenderLayerGlobals( currentRenderLayer = "defaultRenderLayer")
        
        #******************************************************************
        Layers = ["Signature","SQRSignature", "ContextSig", "Product","Wireframe","Subdivision_0","Subdivision_1","UVs"]
        for i in Layers:
            if not cmds.objExists(i):
                cmds.createRenderLayer(n = i, g = True)
        
        cmds.setAttr("defaultRenderLayer.renderable", False)
        cmds.setAttr("persp.renderable", True)
        RenderLayerManagerClass.EditLayer(settings = [
                                                      ["persp.renderable", "none", False ]
                                                      ], 
                                                  layers = ["Signature","SQRSignature", "ContextSig", "Product", "Wireframe", "Subdivision_0", "Subdivision_1", "UVs"] )
        
        cmds.editRenderLayerGlobals( currentRenderLayer = "defaultRenderLayer")
    
    @staticmethod
    def SetImagePaths():
        #Set file path names
        cmds.setAttr("defaultRenderGlobals.imageFilePrefix", "<Scene>_<Layer>", type = "string")
        RenderLayerManagerClass.EditLayer(settings = [["defaultRenderGlobals.imageFilePrefix", "string", "<Scene>_<Layer><Camera>"]], 
                                          layers = ["Product","Wireframe"])
        RenderLayerManagerClass.EditLayer(settings = [["defaultRenderGlobals.imageFilePrefix", "string", "<Scene>_<Layer>"]], 
                                          layers = ["UVs"])
    
    @staticmethod
    def SetRenderLayers():
        RenderLayerManagerClass.ShowModel(Visibility = False)
        cmds.setAttr("defaultRenderGlobals.animation", False)
        
        try:
            #Set the resolution
            RenderLayerManagerClass.ChangeResolution(1480, 800)
            
            #Set the format to png
            RenderLayerManagerClass.ChangeFormat()
            
            #Set image output paths
            RenderLayerManagerClass.SetImagePaths()
            
            #Set Sqr Resolution
            RenderLayerManagerClass.EditLayer(settings = [
                                                          ['defaultResolution.width', "none", 1200 ],
                                                          ['defaultResolution.height', "none", 1200 ],
                                                          ['defaultResolution.deviceAspectRatio', "none", 1 ],
                                                          ],
                                              layers = ["SQRSignature"]
                                              )
            
            #Set the subdivision level in layers
            cmds.editRenderLayerGlobals( currentRenderLayer = "Subdivision_0")
            for mesh in cmds.listRelatives(cmds.getAttr("CMSettings.ModelName"), allDescendents = True):
                try:
                    RenderLayerManagerClass.EditLayer(settings = [[mesh + "Smooth.divisions", "none", 0]], 
                                                      layers = ["Subdivision_0"], ChangeRenderLayer = False)
                except:
                    pass
                
            #Set the subdivision level in layers
            cmds.editRenderLayerGlobals( currentRenderLayer = "Subdivision_1")
            for mesh in cmds.listRelatives(cmds.getAttr("CMSettings.ModelName"), allDescendents = True):
                try:
                    RenderLayerManagerClass.EditLayer(settings = [[mesh + "Smooth.divisions", "none", 1]], 
                                                      layers = ["Subdivision_1"], ChangeRenderLayer = False )
                except:
                    pass
            cmds.editRenderLayerGlobals( currentRenderLayer = "defaultRenderLayer")
                
            
            if cmds.getAttr("defaultRenderGlobals.currentRenderer") == "vray":
                RenderLayerManagerClass.RenderSettingsVray()
                #Set the wire frame materials
                RenderLayerManagerClass.MaterialOverrides("WireShaderSGVray", ["Wireframe", "Subdivision_0", "Subdivision_1"])
                
            elif cmds.getAttr("defaultRenderGlobals.currentRenderer") == "mentalRay":
                RenderLayerManagerClass.RenderSettingsMR()
                #Set the wire frame materials
                RenderLayerManagerClass.MaterialOverrides("WireShaderSGMR", ["Wireframe", "Subdivision_0", "Subdivision_1"])
                
            #Set the uv materials
            RenderLayerManagerClass.MaterialOverrides("UVShaderSG", ["UVs"])
            
            #Manage the scene elements
            RenderLayerManagerClass.ManageUserRig()
            
            RenderLayerManagerClass.ChangeFormat()
            
        except:
            raise
        
        finally:
            RenderLayerManagerClass.ShowModel(Visibility = True)
    
    @staticmethod
    def CreateShaders():
        if cmds.getAttr("defaultRenderGlobals.currentRenderer") == "vray":
            ShadersFile.ShaderClass.CreateVrayWireframeShader()
        
        elif cmds.getAttr("defaultRenderGlobals.currentRenderer") == "mentalRay":
            ShadersFile.ShaderClass.CreateMentalRayWireframeShader()
            
        ShadersFile.ShaderClass.CreateUVMaterial()
        
    @staticmethod
    def assignSnapShots(Camera):
            cmds.editRenderLayerGlobals( currentRenderLayer = "defaultRenderLayer")
            
            #Remove all cameras from the default renderlayer
            cmds.setAttr(Camera + ".renderable", False)
            
            #If the camera is a signature
            if cmds.getAttr(Camera + ".CMSignature"):
                #Make the camera renderable in the signature and the SQR signature layers, remove the mask for png images and make the background color 247    
                RenderLayerManagerClass.EditLayer(settings = [
                                                              [Camera + ".mask", "none", False ],
                                                              [Camera + ".renderable", "none", True ]
                                                              ], 
                                                  layers = ["Signature", "SQRSignature"] )
                
                #Make the camera renderable in the product layer
                RenderLayerManagerClass.EditLayer(settings = [
                                                              [Camera + ".renderable", "none", True ]
                                                              ], 
                                                  layers = ["ContextSig", "Subdivision_0", "Subdivision_1", "UVs"] )
                
                #Remove it from the wireframe layer
                RenderLayerManagerClass.EditLayer(settings = [
                                                              [Camera + ".renderable", "RemoveFromLayer" ]
                                                              ], 
                                                  layers = ["Product", "Wireframe"] )
                
            #If the camera is a product camera    
            else:
                #Remove the overrides in the signature layers    
                RenderLayerManagerClass.EditLayer(settings = [
                                                              [Camera + ".mask", "RemoveFromLayer" ],
                                                              [Camera + ".renderable", "RemoveFromLayer" ]
                                                              ], 
                                                  layers = ["Signature", "SQRSignature"] )
                #Remove it from the signature layers
                RenderLayerManagerClass.EditLayer(settings = [
                                                              [Camera + ".renderable", "RemoveFromLayer", True ]
                                                              ], 
                                                  layers = ["ContextSig", "Subdivision_0", "Subdivision_1", "UVs"] )
                
                #Make it renderable in the product layer
                if cmds.getAttr(Camera + ".CMRenderProductShot"):
                    RenderLayerManagerClass.EditLayer(settings = [
                                                                  [Camera + ".renderable", "none", True ]
                                                                  ], 
                                                      layers = ["Product"] )
                
                #Make it renderable in the wirframe layer
                if cmds.getAttr(Camera + ".CMRenderWireFrame"):
                    RenderLayerManagerClass.EditLayer(settings = [
                                                                  [Camera + ".renderable", "none", True ]
                                                                  ], 
                                                      layers = ["Wireframe"] )
    
    @staticmethod
    def assignTurntable(Camera):
        #Works differently from the snapshots since they don't have the distinction of signature
        #Get the name for the turntable layer
        RenderLayer = "Turntable" + Camera[-1]  
        
        #Create a new render layer for the turntable
        cmds.createRenderLayer( n = RenderLayer, g = True )
        
        
        RenderLayerManagerClass.EditLayer(settings = [
                                                      [Camera + ".renderable", "none", True ],
                                                      ["persp.renderable", "none", False ],
                                                      ["defaultRenderGlobals.animation", "none", True],
                                                      ["defaultRenderGlobals.startFrame", "none", cmds.getAttr(Camera + ".StartRange")],
                                                      ["defaultRenderGlobals.endFrame", "none", cmds.getAttr(Camera + ".StopRange")],
                                                      ["defaultRenderGlobals.outFormatControl", "none", 0],
                                                      ["defaultRenderGlobals.putFrameBeforeExt", "none", 1],
                                                      ["defaultRenderGlobals.periodInExt ", "none", 0],
                                                      ["defaultRenderGlobals.imageFilePrefix", "string", "<Camera>/<Scene>_<Layer>_"],
                                                      ["defaultRenderGlobals.extensionPadding", "none", 2]
                                                      ], 
                                          layers = [RenderLayer] )
        
        cmds.editRenderLayerGlobals( currentRenderLayer = RenderLayer)
        
        #If background objects exist render the turntable with the background else use the shadow plane if it exists
        if cmds.objExists("CMBackground"):
            cmds.editRenderLayerAdjustment("CMBackground.visibility")
            cmds.setAttr("CMBackground.visibility", 1)
            if cmds.objExists("ShadowPlane"):
                cmds.editRenderLayerAdjustment("ShadowPlane.visibility")
                cmds.setAttr("ShadowPlane.visibility", 0)
        
        #If userlights and light rig exist use the userlights for the turntable
        if cmds.objExists("UserLights") and cmds.objExists("CMLightRig"):
            cmds.editRenderLayerAdjustment("UserLights.visibility")
            cmds.setAttr("UserLights.visibility", 1)
            cmds.editRenderLayerAdjustment("CMLightRig.visibility")
            cmds.setAttr("CMLightRig.visibility", 0)
        
        
        RenderLayerManagerClass.EditLayer(settings = [["vraySettings.fileNamePrefix", "string", "<Camera>/<Scene>_<Layer>_"]],
                                            layers = [RenderLayer] )
    
    @staticmethod
    def ManageUserRig():
        cmds.editRenderLayerGlobals( currentRenderLayer = "defaultRenderLayer")
        #If the background exists make sure it is not visible in any layer except the product shots else use the shadow plane if it exists
        if cmds.objExists("CMBackground"):
            cmds.setAttr("CMBackground.visibility", 0)
        if cmds.objExists("ShadowPlane"):
            cmds.setAttr("ShadowPlane.visibility", 1)
        
        #If userlights exist and lightrig exists make the userlights invisible in all except the product shot and contex sig
        if cmds.objExists("UserLights") and cmds.objExists("CMLightRig"):
            cmds.setAttr("UserLights.visibility", 0)
            cmds.setAttr("CMLightRig.visibility", 1)
        
        #Modify the productshot and contextsig attributes
        layers = ["Product", "ContextSig"] 
        i = 0
        while(cmds.objExists("Turntable" + str(i))):
            layers.append("Turntable" + str(i))
            i = i + 1
        
        for i in layers:
            cmds.editRenderLayerGlobals( currentRenderLayer = i)
            #If background objects exist render the product shot with the background else use the shadow plane if it exists
            if cmds.objExists("CMBackground"):
                cmds.editRenderLayerAdjustment("CMBackground.visibility")
                cmds.setAttr("CMBackground.visibility", 1)
                if cmds.objExists("ShadowPlane"):
                    cmds.editRenderLayerAdjustment("ShadowPlane.visibility")
                    cmds.setAttr("ShadowPlane.visibility", 0)
            
            #If userlights and light rig exist use the userlights for the product shots and render the rest with the light rig
            if cmds.objExists("UserLights") and cmds.objExists("CMLightRig"):
                cmds.editRenderLayerAdjustment("UserLights.visibility")
                cmds.setAttr("UserLights.visibility", 1)
                cmds.editRenderLayerAdjustment("CMLightRig.visibility")
                cmds.setAttr("CMLightRig.visibility", 0)
        cmds.editRenderLayerGlobals( currentRenderLayer = "defaultRenderLayer")
        
    @staticmethod
    def SubdivisionLevelChanged(*args):
        cmds.editRenderLayerGlobals( currentRenderLayer = "defaultRenderLayer")
        for mesh in cmds.listRelatives(cmds.getAttr("CMSettings.ModelName"), allDescendents = True):
            try:
                cmds.setAttr(mesh + "Smooth.divisions", cmds.intSlider("SubdivisionLevel",query = True, value = True))
            except:
                pass    
    
    @staticmethod
    def ChangeFormat():
        cmds.setAttr("defaultRenderGlobals.imageFormat", 32)
        if cmds.objExists("vraySettings"):
            cmds.setAttr("vraySettings.imageFormatStr", "png", type = "string")
    
    @staticmethod
    def ChangeResolution(x,y):
        cmds.setAttr( "defaultResolution.lockDeviceAspectRatio", 0)
        cmds.setAttr( 'defaultResolution.aspectLock', 0)
        cmds.setAttr( 'defaultResolution.width' , x)
        cmds.setAttr( 'defaultResolution.height', y)
        cmds.setAttr( 'defaultResolution.deviceAspectRatio', float(x)/float(y))
        
        if cmds.objExists("vraySettings"): 
            try:
                cmds.setAttr("vraySettings.aspectLock", False)
                cmds.setAttr("vraySettings.width", x)
                cmds.setAttr("vraySettings.height", y)
                cmds.setAttr("vraySettings.aspectRatio", float(x)/float(y))    
            except:
                pass
    
    @staticmethod
    def ShowModel(Visibility):
        cmds.editRenderLayerGlobals(currentRenderLayer = "defaultRenderLayer")       
        cmds.setAttr( cmds.getAttr("CMSettings.ModelName") + ".visibility", Visibility)
    