import maya.cmds as cmds
import maya.mel as mel
import ntpath
import math
import os


class LightingClass:
    HDRIPath = ""
    modelName = ""
    diagonal = 0
    CurrentRig = ""
    
    @staticmethod
    def initLighting():
        LightingClass.HDRIPath = os.path.expanduser('~/maya/Turbosquid/CheckMate Tools For Maya/CM_Tools/hdri/')
        LightingClass.modelName = cmds.getAttr("CMSettings.ModelName")
        bbx = cmds.xform(LightingClass.modelName, bb = True, q = True)
        LightingClass.diagonal = math.sqrt((bbx[3] - bbx[0]) * (bbx[3] - bbx[0]) + (bbx[5] - bbx [2]) * (bbx[5] - bbx [2])) 
        LightingClass.diagonal = math.sqrt((bbx[4]-bbx[1]) * (bbx[4]-bbx[1]) + LightingClass.diagonal * LightingClass.diagonal)
        if cmds.getAttr("CMSettings.CurrentRig") != "None" or cmds.getAttr("CMSettings.CurrentRig") != "":
            LightingClass.CurrentRig = cmds.getAttr("CMSettings.CurrentRig")
        
        if cmds.getAttr("defaultRenderGlobals.currentRenderer") == "mentalRay" or cmds.getAttr("defaultRenderGlobals.currentRenderer") == "vray" and cmds.objExists("CMLightRig"):
            cmds.rowLayout("LightControlLayout", edit = True, visible = True)
            cmds.rowLayout("HDRIControlLayout", edit = True, visible = True)
            if cmds.getAttr("CMSettings.CurrentRig") == "Character":
                cmds.rowLayout("EyeLevelLayout", edit = True, visible = True)
        
        if cmds.objExists("EnvironmentBackground"):
            p = cmds.getAttr("EnvironmentBackground.fileTextureName")
            cmds.setAttr("EnvironmentBackground"+".fileTextureName", os.path.expanduser('~/maya/Turbosquid/CheckMate Tools For Maya/CM_Tools/hdri/') + ntpath.split(p)[1], type = "string")
        if cmds.objExists(""):
            p = cmds.getAttr("HDRIDomeTexture.fileTextureName")
            cmds.setAttr("HDRIDomeTexture.fileTextureName", os.path.expanduser('~/maya/Turbosquid/CheckMate Tools For Maya/CM_Tools/hdri/') + ntpath.split(p)[1], type = "string")
            p = cmds.getAttr("HDRIRefractionTexture.fileTextureName")
            cmds.setAttr("HDRIRefractionTexture.fileTextureName", os.path.expanduser('~/maya/Turbosquid/CheckMate Tools For Maya/CM_Tools/hdri/') + ntpath.split(p)[1], type = "string")
            
    @staticmethod
    def deleteLights():
        lights = ["CMKeyLight","CMFillLight","CMBackLight","CMKeySpec","CMFillSpec","CMSunLight","CMHiLight1","CMHiLight2","CMDomeLight","EnvironmentGamma","FoodCard",
                  "MRKeyLight","MRFillLight","MRBackLight","MRKeySpec","MRFillSpec","MRSunLight","MRHiLight1","MRHiLight2","MRHiLightTarget","MRPointTarget","MRDomeLight","MREnvironment","MREnvironmentShape"]
        
        for i in lights:
            if cmds.objExists(i):
                cmds.delete(i)
        
    @staticmethod
    def parentLights():
        if cmds.objExists("CMLightRig"):
            cmds.delete("CMLightRig")
        cmds.createNode( 'transform', n = "CMLightRig" )
        
        cmds.select("CMLightRig")
        cmds.addAttr(longName='LightIntensity', at ='float')
        cmds.setAttr("CMLightRig.LightIntensity", 1)
        cmds.addAttr(longName='HDRIIntensity', at ='float')
        cmds.setAttr("CMLightRig.HDRIIntensity", 1)
        cmds.addAttr(longName='EyeLevel', at ='float')
        cmds.setAttr("CMLightRig.EyeLevel", 92)
        cmds.select(all = True, deselect = True)
        
        
        lights = ["CMKeyLight","CMFillLight","CMBackLight","CMKeySpec","CMFillSpec","CMSunLight","CMHiLight1","CMHiLight2","CMHiLightTarget","CMPointTarget","CMDomeLight",
                  "FoodCard","FoodCardShader","FoodIlluminationShader", "LightBox", "LightBoxPlacer",
                    "MRKeyLight","MRFillLight","MRBackLight","MRKeySpec","MRFillSpec","MRSunLight","MRHiLight1","MRHiLight2","MRHiLightTarget","MRPointTarget","MRDomeLight","MREnvironment"]
        for i in lights:
            try:
                cmds.parent(i, "CMLightRig")
            except:
                pass
             
    @staticmethod
    def calcVector(v,lr, mul, normalize = True):
        f = [0,0,0]
        if normalize:
            mag = math.sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2])
        else:
            mag = 1
            lr = 1
            
        f[0] =  v[0]/mag * lr * mul
        f[1] =  v[2]/mag * lr * mul
        f[2] = -v[1]/mag * lr * mul
        return f
    
    @staticmethod
    def createVrayLight(lightName,Vector, sizeMul, lrMulti, intensity, diffuse, specular, reflections, Shadows = True, normalize = True):
        lightRadius = 1.1 * (LightingClass.diagonal)/(2.0 * math.tan(math.radians(0.5 * 26.991)))
        rigMulti = cmds.floatField("LightIntensityField", query = True, value = True)
        if cmds.objExists(lightName) == False:
            Vec = LightingClass.calcVector(Vector, lightRadius, lrMulti, normalize)
            cmds.createNode( 'transform', n = lightName )
            cmds.shadingNode("VRayLightRectShape", asLight = True, p = lightName, name = lightName + "Shape")
            cmds.setAttr(lightName+".translateX", Vec[0])
            cmds.setAttr(lightName+".translateY", Vec[1])
            cmds.setAttr(lightName+".translateZ", Vec[2])
            cmds.setAttr(lightName+"Shape.intensityMult", intensity * rigMulti)
            cmds.setAttr(lightName+"Shape.subdivs", 24)
            cmds.setAttr(lightName+"Shape.invisible", True)
            cmds.setAttr(lightName+"Shape.uSize", lightRadius * sizeMul[0])
            cmds.setAttr(lightName+"Shape.vSize", lightRadius * sizeMul[1])
            
            if LightingClass.CurrentRig != "Character":
                if lightName == "CMSunLight":
                    cmds.aimConstraint(LightingClass.modelName, lightName, aimVector=(0, 0, -1))
                else:
                    cmds.aimConstraint(cmds.getAttr("CMSettings.ModelName"), lightName, aimVector=(0, 0, -1))
            else:
                if lightName == "CMHiLight1" or lightName == "CMHiLight2":
                    cmds.aimConstraint("CMHiLightTarget", lightName, aimVector=(0, 0, -1))
                else:
                    cmds.aimConstraint("CMPointTarget", lightName, aimVector=(0, 0, -1))

                cmds.setAttr(lightName+"Shape.affectDiffuse", diffuse)
                cmds.setAttr(lightName+"Shape.affectSpecular", specular)
                cmds.setAttr(lightName+"Shape.affectReflections", reflections)
                cmds.setAttr(lightName+"Shape.shadows", Shadows)
    
    @staticmethod
    def createMRLight(lightName, Vector, sizeMul, lrMulty, intensity, diffuse, specular, Shadows = True, normalize = True):
        lightName = "MR"+lightName 
        lightRadius = 1.1 * (LightingClass.diagonal)/(2.0 * math.tan(math.radians(0.5 * 26.991)))
        if cmds.objExists(lightName) == False:
            Vec = LightingClass.calcVector(Vector, lightRadius, lrMulty, normalize)
            cmds.createNode( 'transform', n = lightName )
            cmds.shadingNode("spotLight", asLight = True, p = lightName, name = lightName + "Shape")
            #Set the position of the light
            cmds.setAttr(lightName+".translateX", Vec[0])
            cmds.setAttr(lightName+".translateY", Vec[1])
            cmds.setAttr(lightName+".translateZ", Vec[2])
            #Hotspot and falloff
            cmds.setAttr(lightName+".coneAngle", 43)
            cmds.setAttr(lightName+".penumbraAngle", 45)
            #Light characteristics
            cmds.setAttr(lightName+"Shape.emitSpecular", specular)
            cmds.setAttr(lightName+"Shape.emitDiffuse", diffuse)
            cmds.setAttr(lightName+"Shape.useRayTraceShadows", Shadows)
            #Shadow samples
            cmds.setAttr(lightName+"Shape.shadowRays", 16)
            #Set decay rate to linear
            cmds.setAttr(lightName+"Shape.decayRate", 1)
            #Set intensity
            cmds.setAttr(lightName+"Shape.intensity", intensity * 0.35 * (LightingClass.diagonal) * cmds.floatField("LightIntensityField", query = True, value = True))
            #Set the size of the light
            cmds.setAttr(lightName+".scaleX", lightRadius * sizeMul[0])
            cmds.setAttr(lightName+".scaleY", lightRadius * sizeMul[1])
            #Set the light to be a mr area light
            cmds.setAttr(lightName + "Shape.areaLight", 1)
            cmds.setAttr(lightName + "Shape.areaSamplingU", 5)
            cmds.setAttr(lightName + "Shape.areaSamplingV", 5)
            
            if LightingClass.CurrentRig != "Character":
                if lightName == "MRSunLight":
                    cmds.aimConstraint(LightingClass.modelName, lightName, aimVector=(0, 0, -1))
                else:
                    cmds.aimConstraint(cmds.getAttr("CMSettings.ModelName"), lightName, aimVector=(0, 0, -1))
            else:
                if lightName == "MRHiLight1" or lightName == "MRHiLight2":
                    cmds.aimConstraint("CMHiLightTarget", lightName, aimVector=(0, 0, -1))
                else:
                    cmds.aimConstraint("CMPointTarget", lightName, aimVector=(0, 0, -1))
            
    @staticmethod
    def makeThreePoint():
        LightingClass.createVrayLight("CMKeyLight",[-136.971,-178.896,117.97],[0.333,0.333], 3.6, 29,True,False,False,True,True)
        
        LightingClass.createVrayLight("CMFillLight",[182.496,-103.242,270.779],[0.4,0.4], 5,22,True,False,False,True,True)
        
        LightingClass.createVrayLight("CMBackLight",[18.546,216.322,270.258],[0.333,0.333], 5,22,True,False,False,True,True)
        
        LightingClass.createVrayLight("CMKeySpec",[-98.2,.35,60],[0.5,0.5], 1.9425,10,False,True,True,False,True)
        
        LightingClass.createVrayLight("CMFillSpec",[97,.326,106],[0.5,0.5], 2.847,10,False,True,True,False,True)
        
    @staticmethod
    def getShapes( xform ):
        if ( "transform" == cmds.nodeType(xform) ):
            shapes = cmds.listRelatives(xform, fullPath = True, shapes = True)
        return shapes
    
    @staticmethod
    def createGammaNode(NodeName, gamma, inp = "", output = "", color = []):
        try:cmds.delete(NodeName)
        except:pass
        
        cmds.shadingNode("gammaCorrect", asUtility = True, name = NodeName)
        cmds.setAttr(NodeName +".gammaX", gamma)
        cmds.setAttr(NodeName +".gammaY", gamma)
        cmds.setAttr(NodeName +".gammaZ", gamma)
        
        if  color == []:
            cmds.connectAttr( inp, output)
        else:
            cmds.setAttr( NodeName + ".value", color[0], color[1], color[2], type = "double3")
            cmds.connectAttr( inp, output)
    
    @staticmethod
    def UpdateDisplayLayer():
        cmds.select(cmds.listRelatives(cmds.ls(cameras = True, lights = True),parent = True))
        try:
            cmds.select("UserLights", add = True)
        except:
            pass
        try:
            cmds.select("CMLightRig", add = True)
        except:
            pass
        cmds.editDisplayLayerMembers( 'CM_Lights_and_Cameras', cmds.ls(selection = True) )
        
    @staticmethod
    def createLightRig(*args):
        cmds.undoInfo(openChunk = True)
        cmds.editRenderLayerGlobals( currentRenderLayer = "defaultRenderLayer")
        selection = cmds.textScrollList("CB_ScrollList", query = True, si = True)[0]
        LightingClass.CurrentRig = selection
        LightingClass.intensities = []
        cmds.setAttr("CMSettings.CurrentRig", selection, type = "string")
        cmds.button("LightingButton", edit = True, label = "Current rig: " + selection,  bgc = [0, 0.361, 0])
        selection = "".join(selection)
        LightingClass.deleteLights()
        if  selection == 'Product Shot':
            if cmds.getAttr("defaultRenderGlobals.currentRenderer") == "vray":
                LightingClass.createProductShotVray()
            elif cmds.getAttr("defaultRenderGlobals.currentRenderer") == "mentalRay":
                LightingClass.createProductShotMR()
            else:      
                print "light rig not found"
        
        elif    selection == "Outdoors MidDay":
            if cmds.getAttr("defaultRenderGlobals.currentRenderer") == "vray":
                LightingClass.createOutdoorsMidDayVray()
            elif cmds.getAttr("defaultRenderGlobals.currentRenderer") == "mentalRay":
                LightingClass.createOutdoorsMidDayMR()
            else:      
                print "light rig not found"
                        
        elif    selection == "Automotive Classic":
            if cmds.getAttr("defaultRenderGlobals.currentRenderer") == "vray":
                LightingClass.createAutomotiveClassicVray()
            elif cmds.getAttr("defaultRenderGlobals.currentRenderer") == "mentalRay":
                LightingClass.createAutomotiveClassicMR()
            else:      
                print "light rig not found"
                
        elif    selection == "Character":
            if cmds.getAttr("defaultRenderGlobals.currentRenderer") == "vray":
                LightingClass.createCharacterVray()
            elif cmds.getAttr("defaultRenderGlobals.currentRenderer") == "mentalRay":
                LightingClass.createCharacterMR()
            else:      
                print "light rig not found"
        
        elif    selection == "Food":
            if cmds.getAttr("defaultRenderGlobals.currentRenderer") == "vray":
                LightingClass.createFoodVray()
            elif cmds.getAttr("defaultRenderGlobals.currentRenderer") == "mentalRay":
                LightingClass.createFoodMR()
            else:      
                print "light rig not found"
        
        LightingClass.parentLights()
        
        cmds.editRenderLayerGlobals( currentRenderLayer = "defaultRenderLayer")
        if cmds.objExists("UserLights") and cmds.objExists("CMLightRig"):
            cmds.setAttr("UserLights.visibility", 0)
            cmds.setAttr("CMLightRig.visibility", 1)
        cmds.editRenderLayerGlobals( currentRenderLayer = "Product")
        if cmds.objExists("UserLights") and cmds.objExists("CMLightRig"):
            cmds.editRenderLayerAdjustment("UserLights.visibility")
            cmds.setAttr("UserLights.visibility", 1)
            cmds.editRenderLayerAdjustment("CMLightRig.visibility")
            cmds.setAttr("CMLightRig.visibility", 0)
        cmds.editRenderLayerGlobals( currentRenderLayer = "ContextSig")
        if cmds.objExists("UserLights") and cmds.objExists("CMLightRig"):
            cmds.editRenderLayerAdjustment("UserLights.visibility")
            cmds.setAttr("UserLights.visibility", 1)
            cmds.editRenderLayerAdjustment("CMLightRig.visibility")
            cmds.setAttr("CMLightRig.visibility", 0)
        cmds.editRenderLayerGlobals( currentRenderLayer = "defaultRenderLayer")
        
        
        Layers = cmds.ls(typ = "renderLayer")
        for i in Layers:
            if i == "defaultRenderLayer":
                continue
            cmds.editRenderLayerMembers(i , "CMLightRig")
        
        LightingClass.UpdateDisplayLayer()
        
        cmds.undoInfo(cck = True)    
        
    @staticmethod
    def createProductShotVray():
        spec = LightingClass.HDRIPath + "TSHero_HDRI_v9_Spec.exr"
        env = LightingClass.HDRIPath + "TSHero_HDRI_v9.exr"

        cmds.setAttr("vraySettings.cam_overrideEnvtex", 1)
        cmds.setAttr("vraySettings.cam_envtexBg", 1, 1, 1,type = "double3")

        lightlevel = cmds.floatField("LightIntensityField", query = True, value = True)
        d_lightlevel = cmds.floatField("HDRIIntensityField", query = True, value = True)
        
        try:cmds.delete("HDRIDomeTexture")
        except:pass
        try:cmds.delete("HDRIDomePlacer")
        except:pass
        cmds.shadingNode("file", asTexture = True, name = "HDRIDomeTexture" )
        cmds.setAttr("HDRIDomeTexture.fileTextureName", env, type = "string")
        cmds.setAttr( "HDRIDomeTexture.colorProfile", 2)
        cmds.shadingNode("VRayPlaceEnvTex", asUtility = True, name = "HDRIDomePlacer")
        cmds.connectAttr( "HDRIDomePlacer.outUV", "HDRIDomeTexture.uv")
        cmds.connectAttr( "HDRIDomeTexture.outColor", "vraySettings.cam_envtexGi", force = True)
        cmds.setAttr( "HDRIDomePlacer.mappingType", 2)
        cmds.setAttr( "HDRIDomeTexture.colorGain",  d_lightlevel*1, d_lightlevel*1, d_lightlevel*1, type = "double3")
        cmds.setAttr("HDRIDomePlacer.horRotation", -90)
        cmds.setAttr("HDRIDomePlacer.horFlip", True)
        
        try:cmds.delete("HDRIRefractionTexture")
        except:pass
        try:cmds.delete("HDRIRefractionPlacer")
        except:pass
        cmds.shadingNode("file", asTexture = True, name = "HDRIRefractionTexture" )
        cmds.setAttr("HDRIRefractionTexture.fileTextureName", env, type = "string")
        cmds.setAttr( "HDRIRefractionTexture.colorProfile", 2)
        cmds.shadingNode("VRayPlaceEnvTex", asUtility = True, name = "HDRIRefractionPlacer")
        cmds.connectAttr( "HDRIRefractionPlacer.outUV", "HDRIRefractionTexture.uv")
        cmds.connectAttr( "HDRIRefractionTexture.outColor", "vraySettings.cam_envtexReflect", force = True)
        cmds.setAttr("HDRIRefractionPlacer.mappingType", 2)
        cmds.setAttr( "HDRIRefractionTexture.colorGain",  d_lightlevel*1.5, d_lightlevel*1.5, d_lightlevel*1.5, type = "double3")
        cmds.setAttr("HDRIRefractionPlacer.horRotation", -90)
        cmds.setAttr("HDRIRefractionPlacer.horFlip", True)
        
        cmds.setAttr( "vraySettings.cam_envtexRefract",  1, 1, 1, type = "double3")
        
        LightingClass.makeThreePoint()
        
        cmds.rowLayout("LightControlLayout", edit = True, visible = True)
        cmds.rowLayout("HDRIControlLayout", edit = True, visible = True)
        cmds.rowLayout("EyeLevelLayout", edit = True, visible = False)
           
    @staticmethod
    def createOutdoorsMidDayVray():
        sun = LightingClass.HDRIPath + "glowCard_MidDaySun.png"
        env = LightingClass.HDRIPath + "HDRISky_midDay_001.exr" 
        
        lightlevel = cmds.floatField("LightIntensityField", query = True, value = True)
        d_lightlevel = cmds.floatField("HDRIIntensityField", query = True, value = True)
        
        cmds.setAttr("vraySettings.cam_overrideEnvtex", 1)
        cmds.setAttr("vraySettings.cam_envtexBg", 1, 1, 1,type = "double3")
        
        try:cmds.delete("HDRIDomeTexture")
        except:pass
        try:cmds.delete("HDRIDomePlacer")
        except:pass
        cmds.shadingNode("file", asTexture = True, name = "HDRIDomeTexture" )
        cmds.setAttr("HDRIDomeTexture.fileTextureName", env, type = "string")
        cmds.setAttr( "HDRIDomeTexture.colorProfile", 2)
        cmds.shadingNode("VRayPlaceEnvTex", asUtility = True, name = "HDRIDomePlacer")
        cmds.connectAttr( "HDRIDomePlacer.outUV", "HDRIDomeTexture.uv")
        cmds.connectAttr( "HDRIDomeTexture.outColor", "vraySettings.cam_envtexGi", force = True)
        cmds.setAttr( "HDRIDomePlacer.mappingType", 2)
        cmds.setAttr( "HDRIDomeTexture.colorGain",  d_lightlevel*1, d_lightlevel*1, d_lightlevel*1, type = "double3")
        cmds.setAttr("HDRIDomePlacer.horRotation", -150)
        cmds.setAttr("HDRIDomePlacer.horFlip", True)
        
        
        try:cmds.delete("HDRIRefractionTexture")
        except:pass
        try:cmds.delete("HDRIRefractionPlacer")
        except:pass
        cmds.shadingNode("file", asTexture = True, name = "HDRIRefractionTexture" )
        cmds.setAttr("HDRIRefractionTexture.fileTextureName", env, type = "string")
        cmds.setAttr( "HDRIRefractionTexture.colorProfile", 2)
        cmds.shadingNode("VRayPlaceEnvTex", asUtility = True, name = "HDRIRefractionPlacer")
        cmds.connectAttr( "HDRIRefractionPlacer.outUV", "HDRIRefractionTexture.uv")
        cmds.connectAttr( "HDRIRefractionTexture.outColor", "vraySettings.cam_envtexReflect", force = True)
        cmds.setAttr("HDRIRefractionPlacer.mappingType", 2)
        cmds.setAttr( "HDRIRefractionTexture.colorGain",  d_lightlevel*1.5, d_lightlevel*1.5, d_lightlevel*1.5, type = "double3")
        cmds.setAttr("HDRIRefractionPlacer.horRotation", -150)
        cmds.setAttr("HDRIRefractionPlacer.horFlip", True)
        
        #Create LightRig
        LightingClass.createVrayLight("CMSunLight", [-185.332,-0,307.441], [.0205,.0205], 3.6, 6, True, True, True, True)
        x = cmds.getAttr("CMSunLight.translateX")
        y = cmds.getAttr("CMSunLight.translateZ")
        radius = math.sqrt(x*x+y*y)
        cmds.setAttr("CMSunLight.translateX", x*math.cos(math.radians(30)))
        cmds.setAttr("CMSunLight.translateZ", radius*math.sin(math.radians(30)))
        cmds.setAttr("CMSunLight.useRectTex", True)
        
        
        if cmds.objExists("SunTexture") == False:
            cmds.shadingNode("file", asTexture = True, name = "SunTexture" )
            cmds.setAttr("SunTexture.fileTextureName", sun, type = "string")
            LightingClass.createGammaNode("SunGamma", 0.4545, "SunTexture.outColor", "SunGamma.value")
            cmds.connectAttr("SunGamma.outValue", "CMSunLightShape.rectTex")
        
        
        cmds.setAttr("CMSunLightShape.texResolution", 1024)
        cmds.setAttr("CMSunLightShape.noDecay", True)
        cmds.setAttr("CMSunLightShape.subdivs", 24)
        
        cmds.setAttr( "vraySettings.cam_envtexRefract",  1, 1, 1, type = "double3")
        
        cmds.rowLayout("LightControlLayout", edit = True, visible = True)
        cmds.rowLayout("HDRIControlLayout", edit = True, visible = True)
        cmds.rowLayout("EyeLevelLayout", edit = True, visible = False)

    @staticmethod
    def createAutomotiveClassicVray():
        spec = LightingClass.HDRIPath + "TSHero_HDRI_v9_Spec.exr"
        env = LightingClass.HDRIPath + "TSHero_CarClassic_002.exr"

        cmds.setAttr("vraySettings.cam_overrideEnvtex", 1)
        cmds.setAttr("vraySettings.cam_envtexBg", 1, 1, 1,type = "double3")

        lightlevel = cmds.floatField("LightIntensityField", query = True, value = True)
        d_lightlevel = cmds.floatField("HDRIIntensityField", query = True, value = True)
        
        try:cmds.delete("HDRIDomeTexture")
        except:pass
        try:cmds.delete("HDRIDomePlacer")
        except:pass
        cmds.shadingNode("file", asTexture = True, name = "HDRIDomeTexture" )
        cmds.setAttr("HDRIDomeTexture.fileTextureName", env, type = "string")
        cmds.setAttr( "HDRIDomeTexture.colorProfile", 2)
        cmds.shadingNode("VRayPlaceEnvTex", asUtility = True, name = "HDRIDomePlacer")
        cmds.connectAttr( "HDRIDomePlacer.outUV", "HDRIDomeTexture.uv")
        cmds.connectAttr( "HDRIDomeTexture.outColor", "vraySettings.cam_envtexGi", force = True)
        cmds.setAttr( "HDRIDomePlacer.mappingType", 2)
        cmds.setAttr( "HDRIDomeTexture.colorGain",  d_lightlevel*1, d_lightlevel*1, d_lightlevel*1, type = "double3")
        cmds.setAttr("HDRIDomePlacer.horRotation", -90)
        cmds.setAttr("HDRIDomePlacer.horFlip", True)
        
        try:cmds.delete("HDRIRefractionTexture")
        except:pass
        try:cmds.delete("HDRIRefractionPlacer")
        except:pass
        cmds.shadingNode("file", asTexture = True, name = "HDRIRefractionTexture" )
        cmds.setAttr("HDRIRefractionTexture.fileTextureName", env, type = "string")
        cmds.setAttr( "HDRIRefractionTexture.colorProfile", 2)
        cmds.shadingNode("VRayPlaceEnvTex", asUtility = True, name = "HDRIRefractionPlacer")
        cmds.connectAttr( "HDRIRefractionPlacer.outUV", "HDRIRefractionTexture.uv")
        cmds.connectAttr( "HDRIRefractionTexture.outColor", "vraySettings.cam_envtexReflect", force = True)
        cmds.setAttr("HDRIRefractionPlacer.mappingType", 2)
        cmds.setAttr( "HDRIRefractionTexture.colorGain",  d_lightlevel*1.5, d_lightlevel*1.5, d_lightlevel*1.5, type = "double3")
        cmds.setAttr("HDRIRefractionPlacer.horRotation", -90)
        cmds.setAttr("HDRIRefractionPlacer.horFlip", True)
        
        cmds.setAttr( "vraySettings.cam_envtexRefract",  1, 1, 1, type = "double3")
        
        LightingClass.makeThreePoint()
        
        cmds.rowLayout("LightControlLayout", edit = True, visible = True)
        cmds.rowLayout("HDRIControlLayout", edit = True, visible = True)
        cmds.rowLayout("EyeLevelLayout", edit = True, visible = False)
    
    @staticmethod
    def createCharacterVray():
        spec = LightingClass.HDRIPath + "TSHero_HDRI_v9_Spec.exr"
        env = LightingClass.HDRIPath + "TSHero_HDRI_v9.exr"
        
        cmds.setAttr("vraySettings.cam_overrideEnvtex", 1)
        cmds.setAttr("vraySettings.cam_envtexBg", 1, 1, 1,type = "double3")
        
        lightlevel = cmds.floatField("LightIntensityField", query = True, value = True)
        d_lightlevel = cmds.floatField("HDRIIntensityField", query = True, value = True)
        
        try:cmds.delete("HDRIDomeTexture")
        except:pass
        try:cmds.delete("HDRIDomePlacer")
        except:pass
        cmds.shadingNode("file", asTexture = True, name = "HDRIDomeTexture" )
        cmds.setAttr("HDRIDomeTexture.fileTextureName", env, type = "string")
        cmds.setAttr( "HDRIDomeTexture.colorProfile", 2)
        cmds.shadingNode("VRayPlaceEnvTex", asUtility = True, name = "HDRIDomePlacer")
        cmds.connectAttr( "HDRIDomePlacer.outUV", "HDRIDomeTexture.uv")
        cmds.connectAttr( "HDRIDomeTexture.outColor", "vraySettings.cam_envtexGi", force = True)
        cmds.setAttr( "HDRIDomePlacer.mappingType", 2)
        cmds.setAttr( "HDRIDomeTexture.colorGain",  d_lightlevel*1, d_lightlevel*1, d_lightlevel*1, type = "double3")
        cmds.setAttr("HDRIDomePlacer.horRotation", -90)
        cmds.setAttr("HDRIDomePlacer.horFlip", True)
        
        try:cmds.delete("HDRIRefractionTexture")
        except:pass
        try:cmds.delete("HDRIRefractionPlacer")
        except:pass
        cmds.shadingNode("file", asTexture = True, name = "HDRIRefractionTexture" )
        cmds.setAttr("HDRIRefractionTexture.fileTextureName", env, type = "string")
        cmds.setAttr( "HDRIRefractionTexture.colorProfile", 2)
        cmds.shadingNode("VRayPlaceEnvTex", asUtility = True, name = "HDRIRefractionPlacer")
        cmds.connectAttr( "HDRIRefractionPlacer.outUV", "HDRIRefractionTexture.uv")
        cmds.connectAttr( "HDRIRefractionTexture.outColor", "vraySettings.cam_envtexReflect", force = True)
        cmds.setAttr("HDRIRefractionPlacer.mappingType", 2)
        cmds.setAttr( "HDRIRefractionTexture.colorGain",  d_lightlevel*1.5, d_lightlevel*1.5, d_lightlevel*1.5, type = "double3")
        cmds.setAttr("HDRIRefractionPlacer.horRotation", -90)
        cmds.setAttr("HDRIRefractionPlacer.horFlip", True)
        
        cmds.setAttr( "vraySettings.cam_envtexRefract",  1, 1, 1, type = "double3")

        
        eye_h = cmds.floatField("EyeLevelField", query = True, value = True)
        
        print eye_h
        
        bbx = cmds.xform(LightingClass.modelName, bb = True, q = True)
        
        if not cmds.objExists("CMPointTarget"):
            cmds.createNode( 'transform', n = "CMPointTarget" )
        cmds.setAttr("CMPointTarget.translateX", 0)
        cmds.setAttr("CMPointTarget.translateY", bbx[4]*.83)
        cmds.setAttr("CMPointTarget.translateZ", 0)
        
        if not cmds.objExists("CMHiLightTarget"):
            cmds.createNode( 'transform', n = "CMHiLightTarget" )
        cmds.setAttr("CMHiLightTarget.translateX", 0)
        cmds.setAttr("CMHiLightTarget.translateY", bbx[4]*(eye_h/100))
        cmds.setAttr("CMHiLightTarget.translateZ", 0)
        
        LightingClass.createVrayLight("CMHiLight1", [-79.369,-65.894,(bbx[4] * (eye_h/100)) + 13.146], [.0138,.0138], 1, 1, False, True, True, True, False )
        LightingClass.createVrayLight("CMHiLight2", [ 79.369,-65.894,(bbx[4] * (eye_h/100)) + 13.146], [.0138,.0138], 1, 1, False, True, True, True, False)
        LightingClass.createVrayLight("CMKeyLight", [-267.372,-139.643,154.87], [.087115,.12172], .46814, 20, True, True, True, True, True)
        LightingClass.createVrayLight("CMFillLight", [266.63,-104.305,153.942], [.087115,.12172], .46814, 3 , True, True, True, True, True)
        LightingClass.createVrayLight("CMBackLight", [204.149,199.56,233.717], [.16567,0.12172], .509365, 10, False, True, True, True, True)
        
        cmds.rowLayout("LightControlLayout", edit = True, visible = True)
        cmds.rowLayout("HDRIControlLayout", edit = True, visible = True)
        cmds.rowLayout("EyeLevelLayout", edit = True, visible = True)
    
    @staticmethod
    def createFoodVray():
        env = LightingClass.HDRIPath + "turbosquid\\hdri\\" + "TSHero_HDRI_v9.exr"
        card = LightingClass.HDRIPath + "turbosquid\\hdri\\" + "10k_lightBox_001.hdr"
        
        cmds.setAttr("vraySettings.cam_overrideEnvtex", 1)
        cmds.setAttr("vraySettings.cam_envtexBg", 1, 1, 1,type = "double3")
        
        lightlevel = cmds.floatField("LightIntensityField", query = True, value = True)
        d_lightlevel = cmds.floatField("HDRIIntensityField", query = True, value = True)
        
        try:cmds.delete("HDRIDomeTexture")
        except:pass
        try:cmds.delete("HDRIDomePlacer")
        except:pass
        cmds.shadingNode("file", asTexture = True, name = "HDRIDomeTexture" )
        cmds.setAttr("HDRIDomeTexture.fileTextureName", env, type = "string")
        cmds.setAttr( "HDRIDomeTexture.colorProfile", 2)
        cmds.shadingNode("VRayPlaceEnvTex", asUtility = True, name = "HDRIDomePlacer")
        cmds.connectAttr( "HDRIDomePlacer.outUV", "HDRIDomeTexture.uv")
        cmds.connectAttr( "HDRIDomeTexture.outColor", "vraySettings.cam_envtexGi", force = True)
        cmds.setAttr( "HDRIDomePlacer.mappingType", 2)
        cmds.setAttr( "HDRIDomeTexture.colorGain",  d_lightlevel*1, d_lightlevel*1, d_lightlevel*1, type = "double3")
        cmds.setAttr("HDRIDomePlacer.horRotation", -90)
        cmds.setAttr("HDRIDomePlacer.horFlip", True)
        
        try:cmds.delete("HDRIRefractionTexture")
        except:pass
        try:cmds.delete("HDRIRefractionPlacer")
        except:pass
        cmds.shadingNode("file", asTexture = True, name = "HDRIRefractionTexture" )
        cmds.setAttr("HDRIRefractionTexture.fileTextureName", env, type = "string")
        cmds.setAttr( "HDRIRefractionTexture.colorProfile", 2)
        cmds.shadingNode("VRayPlaceEnvTex", asUtility = True, name = "HDRIRefractionPlacer")
        cmds.connectAttr( "HDRIRefractionPlacer.outUV", "HDRIRefractionTexture.uv")
        cmds.connectAttr( "HDRIRefractionTexture.outColor", "vraySettings.cam_envtexReflect", force = True)
        cmds.setAttr("HDRIRefractionPlacer.mappingType", 2)
        cmds.setAttr( "HDRIRefractionTexture.colorGain",  d_lightlevel*1.5, d_lightlevel*1.5, d_lightlevel*1.5, type = "double3")
        cmds.setAttr("HDRIRefractionPlacer.horRotation", -90)
        cmds.setAttr("HDRIRefractionPlacer.horFlip", True)
        
        cmds.setAttr( "vraySettings.cam_envtexRefract",  1, 1, 1, type = "double3")
        
        if cmds.objExists("FoodCardShader") == False:
            cmds.shadingNode("VRayMtl", asShader = True, name = "FoodCardShader")
        
        if cmds.objExists("LightBox") == False: 
            cmds.shadingNode("file", asTexture = True, name = "LightBox" )
            cmds.setAttr("LightBox.fileTextureName", card, type = "string")
            cmds.connectAttr("LightBox.outColor", "FoodCardShader.color")
            
        if cmds.objExists("LightBoxPlacer") == False:
            cmds.shadingNode("place2dTexture", asUtility = True, name = "LightBoxPlacer")
            cmds.setAttr("LightBoxPlacer.repeatU", 0.85)
            cmds.setAttr("LightBoxPlacer.repeatV", 0.85)
            cmds.connectAttr("LightBoxPlacer.outUV", "LightBox.uvCoord")

        LightingClass.createVrayLight("CMKeyLight", [-19.689,-26.109,17.161], [.4655,.6985], 2.1494, 8.5, True, True, True, True, True)
        LightingClass.createVrayLight("CMFillLight", [32.253,-5.525,3.095], [.4655,.6985], 1.913, 3, True, True, True, True, True)
        
        
        lightName = "CMDomeLight"
        if cmds.objExists(lightName) == False:
            Vec = LightingClass.calcVector([300,0,0], 1, 1, False)
            cmds.createNode( 'transform', n = lightName )
            cmds.shadingNode("VRayLightDomeShape", asLight = True, p = lightName, name = lightName + "Shape")
            cmds.setAttr(lightName+".translateX", Vec[0])
            cmds.setAttr(lightName+".translateY", Vec[1])
            cmds.setAttr(lightName+".translateZ", Vec[2])
            cmds.setAttr(lightName+"Shape.intensityMult", 1 * d_lightlevel)
            cmds.setAttr(lightName+"Shape.subdivs", 16)
            cmds.setAttr(lightName+"Shape.invisible", True)
            cmds.setAttr(lightName+"Shape.useDomeTex", True)
            cmds.setAttr(lightName+"Shape.domeSpherical", True)
            cmds.setAttr(lightName+"Shape.texResolution", 2048)
            cmds.connectAttr("HDRIDomeTexture.outColor", lightName + "Shape.domeTex")
            
            if LightingClass.CurrentRig != "Character":
                if lightName == "CMSunLight":
                    cmds.aimConstraint(LightingClass.modelName, lightName, aimVector=(0, 0, -1))
                else:
                    cmds.aimConstraint(cmds.getAttr("CMSettings.ModelName"), lightName, aimVector=(0, 0, -1))
            else:
                if lightName == "CMHiLight1" or lightName == "CMHiLight2":
                    cmds.aimConstraint("CMHiLightTarget", lightName, aimVector=(0, 0, -1))
                else:
                    cmds.aimConstraint("CMPointTarget", lightName, aimVector=(0, 0, -1))

                cmds.setAttr(lightName+"Shape.affectDiffuse", True)
                cmds.setAttr(lightName+"Shape.affectSpecular", True)
                cmds.setAttr(lightName+"Shape.affectReflections", True)
                cmds.setAttr(lightName+"Shape.shadows", True)
                
        if cmds.objExists("FoodCard") == False:
            lightRadius = 1.1 * (LightingClass.diagonal)/(2.0 * math.tan(math.radians(0.5 * 26.991)))
            cmds.polyPlane( name = "FoodCard", width = 3*lightRadius, height = 3*lightRadius )
            Vec = LightingClass.calcVector([-.764,18.137,9], lightRadius, 1.2, True)
            cmds.setAttr("FoodCard.translateX", Vec[0])
            cmds.setAttr("FoodCard.translateY", Vec[1])
            cmds.setAttr("FoodCard.translateZ", Vec[2])
            cmds.setAttr("FoodCard.rotateX", 105)
        
        if cmds.objExists("FoodCardSG") == False:
            SG = cmds.sets(renderable = True, noSurfaceShader = True, empty = True, name = 'FoodCardSG')   
            cmds.connectAttr(('FoodCardShader.outColor'),(SG + '.surfaceShader'),f=1)
            try:
                cmds.select(object)
                cmds.sets(cmds.ls(selection = True), forceElement = "FoodGroup", e = True)
            except:
                print "Failed to assign shader"
            cmds.setAttr("FoodCardShape.doubleSided", 0)
            cmds.setAttr("FoodCardShape.primaryVisibility", 0)
            cmds.setAttr("FoodCardShape.receiveShadows", 0)
            cmds.setAttr("FoodCardShape.castsShadows", 0)
        
        cmds.rowLayout("LightControlLayout", edit = True, visible = True)
        cmds.rowLayout("HDRIControlLayout", edit = True, visible = True)
        cmds.rowLayout("EyeLevelLayout", edit = True, visible = False)

    @staticmethod
    def ChangeLightIntensity(*args):
        cmds.undoInfo(ock = True)
        rigMulti = cmds.floatField("LightIntensityField", query = True, value = True)
        intensities = [["KeyLight",29],["FillLight",22],["BackLight",22],["KeySpec",10],["FillSpec",10],["SunLight",6],["HiLight1",1],["HiLight2",1],["DomeLight",1]]
        for i in intensities:
            #Adjust Vray Lights
            try:
                cmds.setAttr("CM"+ i[0] + "Shape.intensityMult", i[1] * rigMulti)
            except:
                pass
            
            #Adjust mental ray lights
            try:
                cmds.setAttr("MR"+ i[0] + "Shape.intensity", i[1] * rigMulti)
            except:
                pass
        
        #Save the current rig multiplier in the cm rig node
        try:
            cmds.setAttr("CMLightRig.LightIntensity", rigMulti)
        except:
            print "Could not find light rig"
        cmds.undoInfo(cck = True)
        
    @staticmethod
    def ChangeHDRIIntensity(*args):
        cmds.undoInfo(ock = True)
        rigMulti = cmds.floatField("HDRIIntensityField", query = True, value = True)
        try:
            cmds.setAttr( "HDRIDomeTexture.colorGain",  rigMulti*1, rigMulti*1, rigMulti*1, type = "double3")
            cmds.setAttr( "HDRIRefractionTexture.colorGain",  rigMulti*1.5, rigMulti*1.5, rigMulti*1.5, type = "double3")
            print "Vray HDRI intensity set"
        except:
            print "could not set vray HDRI values"
        
        try:
            cmds.setAttr( "EnvironmentBackground.colorGain",  rigMulti*1, rigMulti*1, rigMulti*1, type = "double3")
            print "MR HDRI intensity set"
        except:
            print "could not set MR HDRI values"
        
        try:
            cmds.setAttr("CMLightRig.HDRIIntensity", rigMulti)
        except:
            print "Could not find light rig"
        cmds.undoInfo(cck = True)
        
    @staticmethod
    def ChangeEyeLevel(*args):
        cmds.undoInfo(ock = True) 
        try:
            rigMulti = cmds.floatField("EyeLevelField", query = True, value = True)
            cmds.setAttr("CMHiLightTarget.translateY", rigMulti)
        except:
            print "Could not translate eye level"
        
        try:
            cmds.setAttr("CMLightRig.EyeLevel", rigMulti)
        except:
            print "Could not find light rig"
        
        cmds.undoInfo(cck = True)     
    
    @staticmethod
    def makeMRThreePoint():
        LightingClass.createMRLight("KeyLight",[-136.971,-178.896,117.97], [0.2985, 0.2985], 3.6, 11,     
                                    True,False,True,True)
        
        LightingClass.createMRLight("FillLight",[182.496,-103.242,270.779], [0.35, 0.35], 5, 8,       
                                    True,False,True,True)
        
        LightingClass.createMRLight("BackLight",[18.546,216.322,270.258], [0.2985,0.2985], 5, 8,         
                                    True,False,True,True)
        
        LightingClass.createMRLight("KeySpec",[-98.2,.35,60], [0.2985,0.2985], 1.9425, 2,                
                                    False,True,False,False)
        
        LightingClass.createMRLight("FillSpec",[97,.326,106], [0.2985,0.2985], 2.847, 2,                 
                                    False,True,False,False)
    
    @staticmethod
    def createProductShotMR():
        spec = LightingClass.HDRIPath + "TSHero_HDRI_v9_Spec.exr"
        env = LightingClass.HDRIPath + "TSHero_HDRI_v9.exr"
        
        
        #Create the IBL
        mel.eval("miCreateDefaultNodes")
        mel.eval("miCreateIbl")
        
        #Rename the IBL
        cmds.rename("mentalrayIbl1", "MREnvironment")
        
        #Assign the texture to the IBL
        cmds.setAttr("MREnvironmentShape.type", 1)
        cmds.setAttr("MREnvironmentShape"+".texture", env, type = "string")
        cmds.shadingNode("gammaCorrect", asUtility = True, n = "EnvironmentGamma")
        cmds.connectAttr("EnvironmentBackground.outColor", "EnvironmentGamma.value", f = True)
        cmds.connectAttr("EnvironmentGamma.outValue", "MREnvironmentShape.color", f = True)
        cmds.setAttr("EnvironmentGamma.gammaX",.454)
        cmds.setAttr("EnvironmentGamma.gammaY",.454)
        cmds.setAttr("EnvironmentGamma.gammaZ",.454)
        
        #Visibility settings of the IBL
        cmds.setAttr("MREnvironmentShape"+".primaryVisibility",0)
        cmds.setAttr("MREnvironmentShape"+".visibleInEnvironment",0)
        cmds.setAttr("MREnvironmentShape"+".visibleInRefractions",0)
        cmds.setAttr("MREnvironmentShape"+".visibleInReflections",0)
        cmds.setAttr("MREnvironmentShape"+".visibleInFinalGather",1)
        
        #Rotate the HDRI to shine light from the top
        cmds.setAttr("MREnvironment.rotateX", -90)
                
        #Light emission section
        #cmds.setAttr("MREnvironmentShape.enableEmitLight", 1)
        #cmds.floatSliderGrp("miEnvironmentLightingQualityCtrl", edit = True, value = 1)
        #mel.eval("miSetEnvironmentLightingQuality")
        
        
        LightingClass.makeMRThreePoint()
        
        cmds.rowLayout("LightControlLayout", edit = True, visible = True)
        cmds.rowLayout("HDRIControlLayout", edit = True, visible = True)
        cmds.rowLayout("EyeLevelLayout", edit = True, visible = False)

    @staticmethod
    def createOutdoorsMidDayMR():
        sun = LightingClass.HDRIPath + "glowCard_MidDaySun.png"
        env = LightingClass.HDRIPath + "HDRISky_midDay_001.exr" 
        
        lightlevel = cmds.floatField("LightIntensityField", query = True, value = True)
        d_lightlevel = cmds.floatField("HDRIIntensityField", query = True, value = True)
        
        #Create the IBL
        mel.eval("miCreateDefaultNodes")
        mel.eval("miCreateIbl")
        
        #Rename the IBL
        cmds.rename("mentalrayIbl1", "MREnvironment")
        
        #Assign the texture to the IBL
        cmds.setAttr("MREnvironmentShape.type", 1)
        cmds.setAttr("MREnvironmentShape"+".texture", env, type = "string")
        cmds.shadingNode("gammaCorrect", asUtility = True, n = "EnvironmentGamma")
        cmds.connectAttr("EnvironmentBackground.outColor", "EnvironmentGamma.value", f = True)
        cmds.connectAttr("EnvironmentGamma.outValue", "MREnvironmentShape.color", f = True)
        cmds.setAttr("EnvironmentGamma.gammaX",1)
        cmds.setAttr("EnvironmentGamma.gammaY",1)
        cmds.setAttr("EnvironmentGamma.gammaZ",1)
        
        #Visibility settings of the IBL
        cmds.setAttr("MREnvironmentShape"+".primaryVisibility",0)
        cmds.setAttr("MREnvironmentShape"+".visibleInEnvironment",0)
        cmds.setAttr("MREnvironmentShape"+".visibleInRefractions",0)
        cmds.setAttr("MREnvironmentShape"+".visibleInReflections",0)
        cmds.setAttr("MREnvironmentShape"+".visibleInFinalGather",1)
        
        #Rotate the HDRI to shine light from the top
        cmds.setAttr("MREnvironment.rotateX", -90)
        
        #Create LightRig
        LightingClass.createMRLight("SunLight", [-185.332,-0,307.441], [.0205,.0205], 3.6, 60, 
                                    True, True, True, True)
        x = cmds.getAttr("MRSunLight.translateX")
        y = cmds.getAttr("MRSunLight.translateZ")
        radius = math.sqrt(x*x+y*y)
        cmds.setAttr("MRSunLight.translateX", x*math.cos(math.radians(30)))
        cmds.setAttr("MRSunLight.translateZ", radius*math.sin(math.radians(30)))
        
        cmds.rowLayout("LightControlLayout", edit = True, visible = True)
        cmds.rowLayout("HDRIControlLayout", edit = True, visible = True)
        cmds.rowLayout("EyeLevelLayout", edit = True, visible = False)
    
    @staticmethod
    def createAutomotiveClassicMR():
        spec = LightingClass.HDRIPath + "TSHero_HDRI_v9_Spec.exr"
        env = LightingClass.HDRIPath + "TSHero_CarClassic_002.exr"
        
        #Create the IBL
        mel.eval("miCreateDefaultNodes")
        mel.eval("miCreateIbl")
        
        #Rename the IBL
        cmds.rename("mentalrayIbl1", "MREnvironment")
        
        #Assign the texture to the IBL
        cmds.setAttr("MREnvironmentShape.type", 1)
        cmds.setAttr("MREnvironmentShape"+".texture", env, type = "string")
        cmds.shadingNode("gammaCorrect", asUtility = True, n = "EnvironmentGamma")
        cmds.connectAttr("EnvironmentBackground.outColor", "EnvironmentGamma.value", f = True)
        cmds.connectAttr("EnvironmentGamma.outValue", "MREnvironmentShape.color", f = True)
        cmds.setAttr("EnvironmentGamma.gammaX",.454)
        cmds.setAttr("EnvironmentGamma.gammaY",.454)
        cmds.setAttr("EnvironmentGamma.gammaZ",.454)
        
        #Visibility settings of the IBL
        cmds.setAttr("MREnvironmentShape"+".primaryVisibility",0)
        cmds.setAttr("MREnvironmentShape"+".visibleInEnvironment",0)
        cmds.setAttr("MREnvironmentShape"+".visibleInRefractions",0)
        cmds.setAttr("MREnvironmentShape"+".visibleInReflections",0)
        cmds.setAttr("MREnvironmentShape"+".visibleInFinalGather",1)
        
        #Rotate the HDRI to shine light from the top
        cmds.setAttr("MREnvironment.rotateX", -90)
                
        #Light emission section
        #cmds.setAttr("MREnvironmentShape.enableEmitLight", 1)
        #cmds.floatSliderGrp("miEnvironmentLightingQualityCtrl", edit = True, value = 1)
        #mel.eval("miSetEnvironmentLightingQuality")
        
        
        LightingClass.makeMRThreePoint()
        
        cmds.rowLayout("LightControlLayout", edit = True, visible = True)
        cmds.rowLayout("HDRIControlLayout", edit = True, visible = True)
        cmds.rowLayout("EyeLevelLayout", edit = True, visible = False)

    @staticmethod
    def createCharacterMR():
        spec = LightingClass.HDRIPath + "TSHero_HDRI_v9_Spec.exr"
        env = LightingClass.HDRIPath + "TSHero_HDRI_v9.exr"
        
        lightlevel = cmds.floatField("LightIntensityField", query = True, value = True)
        d_lightlevel = cmds.floatField("HDRIIntensityField", query = True, value = True)
        
        #Create the IBL
        mel.eval("miCreateDefaultNodes")
        mel.eval("miCreateIbl")
        
        #Rename the IBL
        cmds.rename("mentalrayIbl1", "MREnvironment")
        
        #Assign the texture to the IBL
        cmds.setAttr("MREnvironmentShape.type", 1)
        cmds.setAttr("MREnvironmentShape"+".texture", env, type = "string")
        cmds.shadingNode("gammaCorrect", asUtility = True, n = "EnvironmentGamma")
        cmds.connectAttr("EnvironmentBackground.outColor", "EnvironmentGamma.value", f = True)
        cmds.connectAttr("EnvironmentGamma.outValue", "MREnvironmentShape.color", f = True)
        cmds.setAttr("EnvironmentGamma.gammaX",.454)
        cmds.setAttr("EnvironmentGamma.gammaY",.454)
        cmds.setAttr("EnvironmentGamma.gammaZ",.454)
        
        #Visibility settings of the IBL
        cmds.setAttr("MREnvironmentShape"+".primaryVisibility",0)
        cmds.setAttr("MREnvironmentShape"+".visibleInEnvironment",0)
        cmds.setAttr("MREnvironmentShape"+".visibleInRefractions",0)
        cmds.setAttr("MREnvironmentShape"+".visibleInReflections",0)
        cmds.setAttr("MREnvironmentShape"+".visibleInFinalGather",1)
        
        #Rotate the HDRI to shine light from the top
        cmds.setAttr("MREnvironment.rotateX", -90)
        
        eye_h = cmds.floatField("EyeLevelField", query = True, value = True)
                
        bbx = cmds.xform(LightingClass.modelName, bb = True, q = True)
        
        if not cmds.objExists("CMPointTarget"):
            cmds.createNode( 'transform', n = "CMPointTarget" )
        cmds.setAttr("CMPointTarget.translateX", 0)
        cmds.setAttr("CMPointTarget.translateY", bbx[4]*.83)
        cmds.setAttr("CMPointTarget.translateZ", 0)
        
        if not cmds.objExists("CMHiLightTarget"):
            cmds.createNode( 'transform', n = "CMHiLightTarget" )
        cmds.setAttr("CMHiLightTarget.translateX", 0)
        cmds.setAttr("CMHiLightTarget.translateY", bbx[4]*(eye_h/100))
        cmds.setAttr("CMHiLightTarget.translateZ", 0)
        
        LightingClass.createMRLight("HiLight1", [-79.369,-65.894,(bbx[4] * (eye_h/100)) + 13.146], [.0138,.0138], 1, 1, False, True, True, False )
        LightingClass.createMRLight("HiLight2", [ 79.369,-65.894,(bbx[4] * (eye_h/100)) + 13.146], [.0138,.0138], 1, 1, False, True, True, False)
        LightingClass.createMRLight("KeyLight", [-267.372,-139.643,154.87], [.087115,.12172], .46814, 16, True, True, True, True)
        LightingClass.createMRLight("FillLight", [266.63,-104.305,153.942], [.087115,.12172], .46814, 2.4 , True, True, True, True)
        LightingClass.createMRLight("BackLight", [204.149,199.56,233.717], [.16567,0.12172], .509365, 8, False, True, True, True)
        
        cmds.rowLayout("LightControlLayout", edit = True, visible = True)
        cmds.rowLayout("HDRIControlLayout", edit = True, visible = True)
        cmds.rowLayout("EyeLevelLayout", edit = True, visible = True)
    
    @staticmethod
    def createFoodMR():
        env = LightingClass.HDRIPath  + "TSHero_HDRI_v9.exr"
        card = LightingClass.HDRIPath  + "10k_lightBox_001.hdr"
        
        lightlevel = cmds.floatField("LightIntensityField", query = True, value = True)
        d_lightlevel = cmds.floatField("HDRIIntensityField", query = True, value = True)
        
        #Create the IBL
        mel.eval("miCreateDefaultNodes")
        mel.eval("miCreateIbl")
        
        #Rename the IBL
        cmds.rename("mentalrayIbl1", "MREnvironment")
        
        #Assign the texture to the IBL
        cmds.setAttr("MREnvironmentShape.type", 1)
        cmds.setAttr("MREnvironmentShape"+".texture", env, type = "string")
        cmds.shadingNode("gammaCorrect", asUtility = True, n = "EnvironmentGamma")
        cmds.connectAttr("EnvironmentBackground.outColor", "EnvironmentGamma.value", f = True)
        cmds.connectAttr("EnvironmentGamma.outValue", "MREnvironmentShape.color", f = True)
        cmds.setAttr("EnvironmentGamma.gammaX",.454)
        cmds.setAttr("EnvironmentGamma.gammaY",.454)
        cmds.setAttr("EnvironmentGamma.gammaZ",.454)
        
        #Visibility settings of the IBL
        cmds.setAttr("MREnvironmentShape"+".primaryVisibility",0)
        cmds.setAttr("MREnvironmentShape"+".visibleInEnvironment",0)
        cmds.setAttr("MREnvironmentShape"+".visibleInRefractions",0)
        cmds.setAttr("MREnvironmentShape"+".visibleInReflections",0)
        cmds.setAttr("MREnvironmentShape"+".visibleInFinalGather",1)
        
        #Rotate the HDRI to shine light from the top
        cmds.setAttr("MREnvironment.rotateX", -90)
            
        cmds.shadingNode("mia_material_x", asShader = True, name = "FoodCardShader")
        cmds.setAttr("FoodCardShader.diffuse", 0,0,0, type = "double3")
        cmds.setAttr("FoodCardShader.refl_color", 0,0,0, type = "double3")

        cmds.shadingNode("mia_light_surface", asShader = True , n = "FoodIlluminationShader")
        cmds.connectAttr("FoodIlluminationShader.outValue", "FoodCardShader.additional_color", f = True)        
        cmds.shadingNode("file", asTexture = True, name = "LightBox" )
        cmds.setAttr("LightBox.fileTextureName", card, type = "string")
        cmds.connectAttr("LightBox.outColor", "FoodIlluminationShader.color")
            
        cmds.shadingNode("place2dTexture", asUtility = True, name = "LightBoxPlacer")
        cmds.setAttr("LightBoxPlacer.repeatU", 0.85)
        cmds.setAttr("LightBoxPlacer.repeatV", 0.85)
        cmds.connectAttr("LightBoxPlacer.outUV", "LightBox.uvCoord")

        LightingClass.createMRLight("KeyLight", [-19.689,-26.109,17.161], [.4655,.6985], 2.1494, 8.5, True, True, True, True)
        LightingClass.createMRLight("FillLight", [32.253,-5.525,3.095], [.4655,.6985], 1.913, 3, True, True, True, True)
                
        lightRadius = 1.1 * (LightingClass.diagonal)/(2.0 * math.tan(math.radians(0.5 * 26.991)))
        cmds.polyPlane( name = "FoodCard", width = 3*lightRadius, height = 3*lightRadius )
        Vec = LightingClass.calcVector([-.764,18.137,9], lightRadius, 1.2, True)
        cmds.setAttr("FoodCard.translateX", Vec[0])
        cmds.setAttr("FoodCard.translateY", Vec[1])
        cmds.setAttr("FoodCard.translateZ", Vec[2])
        cmds.setAttr("FoodCard.rotateX", 105)
        
        if cmds.objExists("MRFoodCardSG") == False:
            SG = cmds.sets(renderable = True, noSurfaceShader = True, empty = True, name = 'MRFoodCardSG')   
            cmds.connectAttr(('FoodCardShader.outColor'),(SG + '.surfaceShader'),f=1)
            try:
                cmds.select(object)
                cmds.sets(cmds.ls(selection = True), forceElement = "FoodGroup", e = True)
            except:
                print "Failed to assign shader"

        cmds.setAttr("FoodCardShape.doubleSided", 0)
        cmds.setAttr("FoodCardShape.primaryVisibility", 0)
        cmds.setAttr("FoodCardShape.receiveShadows", 0)
        cmds.setAttr("FoodCardShape.castsShadows", 0)
        
        cmds.rowLayout("LightControlLayout", edit = True, visible = True)
        cmds.rowLayout("HDRIControlLayout", edit = True, visible = True)
        cmds.rowLayout("EyeLevelLayout", edit = True, visible = False)
