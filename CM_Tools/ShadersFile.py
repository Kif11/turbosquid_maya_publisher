import maya.cmds as cmds
import maya.mel as mel
import LightingPresets
import os

class ShaderClass:
    @staticmethod
    def DeleteWireframeShader():
        layers = ["Wireframe", "Subdivision_0", "Subdivision_1"]
        for i in layers:
            cmds.editRenderLayerGlobals(currentRenderLayer = i)
            try:cmds.sets(clear = i + "WireSet")
            except:pass
            
        ShaderObjects = ["WireShader","WireSet","WireMap","WirePlacer","ContourShader"]
        for i in ShaderObjects:
            if cmds.objExists(i + "Vray"):
                cmds.delete(i + "Vray")
            if cmds.objExists(i + "MR"):
                cmds.delete(i + "MR")
    
    @staticmethod
    def DeleteVrayShadowMat():
        checkList = ["ShadowSG","Shadow_Matte","Shadow_Base","Opac_comp","Comp_tex", "Gradient_tex", "Gradient_clip","Shadow_AO","Contact_AO","ShadowLight","ShadowLightReverse","GradientBlend","ShadowLightCondition","ShadowLightReReverse","DirtBlend"]
        for i in checkList:
            try:
                cmds.delete(i)
            except:
                pass
    
    @staticmethod
    def DeleteMRShadowMat():
        checkList = ["ScreenA","ScreenB","ScreenAXB","ScreenOut","EnvironmentBackground", "MR_Background_Switcher", "ShadowSG","Shadow_Matte","Shadow_Base","Opac_comp","Comp_tex", "Gradient_tex", "Gradient_texCorrect", "GradientClipCorrect", "Gradient_clip","Shadow_AO","Contact_AO","ShadowLight","ShadowLightReverse","GradientBlend","ShadowLightCondition","ShadowLightReReverse","DirtBlend"]
        for i in checkList:
            try:
                cmds.delete(i)
            except:
                pass
    
    @staticmethod
    def DeleteUVMat():
        try:
            cmds.delete("UVShader")
        except:
            pass
        
        try:
            cmds.delete("UVShaderSG")
        except:
            pass
        
        try:
            cmds.delete("CheckerMap")
        except:
            pass
        
        try:
            cmds.delete("TexturePlacer")
        except:
            pass
    
    @staticmethod
    def CreateVrayWireframeShader():
        
        ShaderClass.DeleteWireframeShader()
        
        material = cmds.shadingNode('VRayMtl', asShader = True, name='WireShaderVray')
        cmds.shadingNode("VRayEdges", asTexture = True, name = "WireMapVray")
        cmds.shadingNode("place2dTexture", asUtility = True, name = "WirePlacerVray")
        cmds.connectAttr("WirePlacerVray.outUV", "WireMapVray.uv")
        cmds.connectAttr("WirePlacerVray.outUvFilterSize", "WireMapVray.uvFilterSize")
        cmds.connectAttr("WireMapVray.outColor", "WireShaderVray.color")
        
        if not cmds.objExists("WireShaderSGVray"):
            cmds.sets(renderable = True, noSurfaceShader = True, empty = True, name = 'WireShaderSGVray')   
        cmds.connectAttr((material + '.outColor'),('WireShaderSGVray.surfaceShader'),f=1)
        
        cmds.setAttr("WireMapVray.edgesColor", 0.0196078, 0.0196078, 0.0196078, type = "double3")
        cmds.setAttr("WireMapVray.backgroundColor", 0.34902, 0.34902, 0.34902, type = "double3")
        cmds.setAttr("WireMapVray.pixelWidth", 0.85)
    
    @staticmethod
    def CreateMentalRayWireframeShader():
        
        ShaderClass.DeleteWireframeShader()
        
        material = cmds.shadingNode('blinn', asShader = True, name='WireShaderMR')
        if not cmds.objExists("WireShaderSGMR"):
            cmds.sets(renderable = True, noSurfaceShader = True, empty = True, name = 'WireShaderSGMR')   
        cmds.connectAttr((material + '.outColor'),('WireShaderSGMR.surfaceShader'),f=1)
        
        cmds.shadingNode("contour_shader_simple", asShader = True, name = "ContourShaderMR")
        cmds.connectAttr("ContourShaderMR.outValue", "WireShaderSGMR.miContourShader")
        cmds.setAttr("ContourShaderMR.width", 0.05)
        
        cmds.setAttr("WireShaderMR.color", 0.482, 0.482, 0.482, type = "double3")
        cmds.setAttr("WireShaderMR.reflectivity", 0)
        cmds.setAttr("WireShaderSGMR.miContourEnable", 1)
        cmds.setAttr("WireShaderSGMR.miContourWidth", 0.5)
        cmds.setAttr("WireShaderSGMR.miContourColor", 0, 0, 0, type = "double3")    
    
    @staticmethod
    def CreateVrayShadowMat():
        if cmds.getAttr("defaultRenderGlobals.currentRenderer") == "vray":
            diagonal = LightingPresets.LightingClass.diagonal
            
            checkList = ["ScreenA","ScreenB","ScreenAXB","ScreenOut","EnvironmentBackground", "MR_Background_Switcher", "ShadowSG","Shadow_Matte","Shadow_Base","Opac_comp","Comp_tex", "Gradient_tex", "Gradient_clip","Shadow_AO","Contact_AO","ShadowLight","ShadowLightReverse","GradientBlend","ShadowLightCondition","ShadowLightReReverse","DirtBlend"]
            for i in checkList:
                try:
                    cmds.delete(i)
                except:
                    pass
            
            cmds.shadingNode("ramp", asTexture = True, name = "Gradient_tex")
            cmds.setAttr("Gradient_tex.type", 4)
            cmds.setAttr("Gradient_tex.colorEntryList[0].position", 0.686469)
            cmds.setAttr("Gradient_tex.colorEntryList[1].position", 0)
            cmds.setAttr("Gradient_tex.colorEntryList[0].color", 0, 0, 0 ,type = "double3") 
            cmds.setAttr("Gradient_tex.colorEntryList[1].color", 1, 1, 1 ,type = "double3" )
            
            def createBaseMaterials():
                cmds.shadingNode("VRayMtlWrapper", asShader = True, name = "Shadow_Matte" )
                cmds.shadingNode("VRayMtl", asShader = True, name = "Shadow_Base")
                cmds.setAttr( "Shadow_Matte.generateGI", 1)
                cmds.setAttr( "Shadow_Matte.receiveGI", 1)
                cmds.setAttr( "Shadow_Matte.generateCaustics", 0)
                cmds.setAttr( "Shadow_Matte.receiveCaustics", 0)
                cmds.setAttr( "Shadow_Matte.matteSurface", 1)
                cmds.setAttr( "Shadow_Matte.alphaContribution", 0)
                cmds.setAttr( "Shadow_Matte.matteForSecondaryRays", 1)
                cmds.setAttr( "Shadow_Matte.shadows", 1)
                cmds.setAttr( "Shadow_Matte.affectAlpha", 1)
                cmds.setAttr( "Shadow_Matte.shadowTintColor", 0, 0, 0, type = "double3")
                cmds.setAttr( "Shadow_Matte.alphaContribution", -1)
                
                cmds.setAttr( "Shadow_Base.color", 0, 0, 0, type = "double3")
                
                cmds.connectAttr( "Shadow_Base.outColor", "Shadow_Matte.baseMaterial")
            
            def createPrimaryLayer():
                cmds.shadingNode("layeredTexture", asShader = True, name = "Opac_comp")
                cmds.connectAttr("Opac_comp.outColor", "Shadow_Base.opacityMap", force = True)
                
            def createShadowLight():
                cmds.shadingNode("surfaceLuminance", asUtility = True, name = "ShadowLight")
                cmds.shadingNode("blendColors", asUtility = True, name = "GradientBlend")
                cmds.shadingNode("blendColors", asUtility = True, name = "DirtBlend")
                cmds.shadingNode("ramp", asTexture = True, name = "Gradient_clip")
                cmds.setAttr("Gradient_clip.type", 4)
                cmds.setAttr("Gradient_clip.colorEntryList[0].position", 0.706271)
                cmds.setAttr("Gradient_clip.colorEntryList[1].position", 0)
                cmds.setAttr("Gradient_clip.colorEntryList[2].color", 0.89, 0.89, 0.89, type = "double3") 
                cmds.setAttr("Gradient_clip.colorEntryList[2].position", 0.458746)
                cmds.setAttr("Gradient_clip.colorEntryList[0].color", 0, 0, 0 ,type = "double3")
                cmds.setAttr("Gradient_clip.colorEntryList[1].color", 1, 1, 1 ,type = "double3")

                
                cmds.shadingNode("reverse", asUtility = True, name = "ShadowLightReverse")
                cmds.shadingNode("condition", asUtility = True, name = "ShadowLightCondition")
                cmds.shadingNode("reverse", asUtility = True, name = "ShadowLightReReverse")
                
                cmds.setAttr("ShadowLightCondition.operation", 2)
                
                cmds.connectAttr("ShadowLight.outValue", "ShadowLightCondition.firstTerm")
                
                cmds.connectAttr("ShadowLight.outValue", "ShadowLightReverse.input.inputX")
                cmds.connectAttr("ShadowLight.outValue", "ShadowLightReverse.input.inputY")
                cmds.connectAttr("ShadowLight.outValue", "ShadowLightReverse.input.inputZ")
                
                cmds.connectAttr("ShadowLightReverse.output","ShadowLightCondition.colorIfTrue")
                
                cmds.setAttr("ShadowLightCondition.colorIfFalseR",0)
                cmds.setAttr("ShadowLightCondition.colorIfFalseG",0)
                cmds.setAttr("ShadowLightCondition.colorIfFalseB",0)
                
                cmds.connectAttr("ShadowLightCondition.outColor", "ShadowLightReReverse.input")
                
                cmds.connectAttr("ShadowLightReReverse.output.outputX", "GradientBlend.blender")
                cmds.connectAttr("ShadowLightReReverse.output.outputX", "DirtBlend.blender")
                
                mel.eval("vray addAttributesFromGroup ShadowLight vray_surface_luminance 1;")
                cmds.setAttr("ShadowLight.vrayLuminanceMode", 3)
                cmds.setAttr("ShadowLight.vrayLuminanceGIContrib", True)
            
            def createScreenShader(inputA, inputB):
                cmds.shadingNode("reverse", asUtility = True, name = "ScreenA")
                cmds.shadingNode("reverse", asUtility = True, name = "ScreenB")
                cmds.shadingNode("reverse", asUtility = True, name = "ScreenOut")
                cmds.shadingNode("multiplyDivide", asUtility = True, name = "ScreenAXB")
                
                cmds.connectAttr(inputA + ".outColor", "ScreenA.input", force = True)
                cmds.connectAttr(inputB + ".output", "ScreenB.input", force = True)
                cmds.connectAttr("ScreenA.output","ScreenAXB.input1", force = True)
                cmds.connectAttr("ScreenB.output","ScreenAXB.input2", force = True)
                cmds.connectAttr("ScreenAXB.output","ScreenOut.input", force = True)
                
                
            def createCompTexLayer():
                cmds.shadingNode("multiplyDivide", asUtility = True, name = "Comp_tex")
                cmds.shadingNode("VRayDirt", asShader = True, name = "Shadow_AO")
                cmds.shadingNode("VRayDirt", asShader = True, name = "Contact_AO")
                
                cmds.setAttr( "Shadow_AO.blackColor",  1, 1, 1, type = "double3")
                cmds.setAttr( "Shadow_AO.whiteColor",  0, 0, 0, type = "double3")
                cmds.setAttr( "Shadow_AO.radius", 2.5*diagonal)
                cmds.setAttr( "Shadow_AO.subdivs", 16)
                cmds.setAttr( "Shadow_AO.distribution", 10)
         
                cmds.setAttr( "Contact_AO.blackColor",  1, 1, 1, type = "double3")
                cmds.setAttr( "Contact_AO.whiteColor",  0, 0, 0, type = "double3")
                cmds.setAttr( "Contact_AO.radius", 0.25*diagonal)
                cmds.setAttr( "Contact_AO.subdivs", 16)
                cmds.setAttr( "Contact_AO.distribution", 1)
            
            createBaseMaterials()
            createPrimaryLayer()
            createShadowLight()
            createCompTexLayer()
            
            cmds.connectAttr("Comp_tex.output", "Opac_comp.inputs[0].color", force = True)
            cmds.connectAttr("Gradient_tex.outColor", "Opac_comp.inputs[1].color", force = True)
            cmds.setAttr("Opac_comp.inputs[0].blendMode", 6)
            
            cmds.connectAttr("Shadow_AO.outColor", "DirtBlend.color1")
            cmds.connectAttr("Gradient_clip.outColor", "GradientBlend.color1")
            
            cmds.setAttr("DirtBlend.color2", 1,1,1, type = "double3")
            cmds.setAttr("GradientBlend.color2", 1,1,1, type = "double3")
            
            createScreenShader("Contact_AO", "DirtBlend")
            cmds.connectAttr("GradientBlend.output", "Comp_tex.input1", force = True)
            cmds.connectAttr("ScreenOut.output", "Comp_tex.input2", force = True)
            
            
            SG = cmds.sets(renderable = True, noSurfaceShader = True, empty = True, name = 'ShadowSG')   
            cmds.connectAttr(("Shadow_Matte" + '.outColor'),(SG + '.surfaceShader'),f=1)
    
    @staticmethod
    def CreateMRShadowMat():
        if cmds.getAttr("defaultRenderGlobals.currentRenderer") == "mentalRay":
            diagonal = LightingPresets.LightingClass.diagonal
            
            checkList = ["ScreenA","ScreenB","ScreenAXB","ScreenOut","EnvironmentBackground", "MR_Background_Switcher", "ShadowSG","Shadow_Matte","Shadow_Base","Opac_comp","Comp_tex", "Gradient_tex", "Gradient_clip","Shadow_AO","Contact_AO","ShadowLight","ShadowLightReverse","GradientBlend","ShadowLightCondition","ShadowLightReReverse","DirtBlend"]
            for i in checkList:
                try:
                    cmds.delete(i)
                except:
                    pass
            
            cmds.shadingNode("ramp", asTexture = True, name = "Gradient_tex")
            cmds.setAttr("Gradient_tex.type", 4)
            cmds.setAttr("Gradient_tex.colorEntryList[0].position", 0.686469)
            cmds.setAttr("Gradient_tex.colorEntryList[1].position", 0)
            cmds.setAttr("Gradient_tex.colorEntryList[0].color", 0, 0, 0 ,type = "double3") 
            cmds.setAttr("Gradient_tex.colorEntryList[1].color", 1, 1, 1 ,type = "double3" )
            
            def createBaseMaterials():
                cmds.shadingNode("mip_matteshadow", asShader = True, name = "Shadow_Matte" )
                cmds.shadingNode("reverse", asUtility = True, name = "Shadow_Base")
                
                cmds.setAttr( "Shadow_Matte.ao_samples", 128)
                cmds.setAttr( "Shadow_Matte.catch_shadows", 0)
                cmds.setAttr( "Shadow_Matte.catch_indirect", 1)
                
                cmds.connectAttr( "Shadow_Base.output", "Shadow_Matte.ao_dark")
                
            def createPrimaryLayer():
                cmds.shadingNode("layeredTexture", asShader = True, name = "Opac_comp")
                cmds.connectAttr("Opac_comp.outColor", "Shadow_Base.input")
                
            def createShadowLight():
                cmds.shadingNode("surfaceLuminance", asUtility = True, name = "ShadowLight")
                cmds.shadingNode("blendColors", asUtility = True, name = "GradientBlend")
                cmds.shadingNode("blendColors", asUtility = True, name = "DirtBlend")
                cmds.shadingNode("ramp", asTexture = True, name = "Gradient_clip")
                cmds.setAttr("Gradient_clip.type", 4)
                cmds.setAttr("Gradient_clip.colorEntryList[0].position", 0.706271)
                cmds.setAttr("Gradient_clip.colorEntryList[1].position", 0)
                cmds.setAttr("Gradient_clip.colorEntryList[2].color", 0.89, 0.89, 0.89, type = "double3") 
                cmds.setAttr("Gradient_clip.colorEntryList[2].position", 0.458746)
                cmds.setAttr("Gradient_clip.colorEntryList[0].color", 0, 0, 0 ,type = "double3")
                cmds.setAttr("Gradient_clip.colorEntryList[1].color", 1, 1, 1 ,type = "double3")

                
                cmds.connectAttr("ShadowLight.outValue", "GradientBlend.blender")
                cmds.connectAttr("ShadowLight.outValue", "DirtBlend.blender")
            
            def createScreenShader(inputA, inputB):
                cmds.shadingNode("reverse", asUtility = True, name = "ScreenA")
                cmds.shadingNode("reverse", asUtility = True, name = "ScreenB")
                cmds.shadingNode("reverse", asUtility = True, name = "ScreenOut")
                cmds.shadingNode("multiplyDivide", asUtility = True, name = "ScreenAXB")
                
                cmds.connectAttr(inputA + ".outValue", "ScreenA.input", force = True)
                cmds.connectAttr(inputB + ".output", "ScreenB.input", force = True)
                cmds.connectAttr("ScreenA.output","ScreenAXB.input1", force = True)
                cmds.connectAttr("ScreenB.output","ScreenAXB.input2", force = True)
                cmds.connectAttr("ScreenAXB.output","ScreenOut.input", force = True)
            
            def createCompTexLayer():
                cmds.shadingNode("multiplyDivide", asUtility = True, name = "Comp_tex")
                cmds.shadingNode("mib_amb_occlusion", asShader = True, name = "Shadow_AO")
                cmds.shadingNode("mib_amb_occlusion", asShader = True, name = "Contact_AO")
                
                cmds.setAttr( "Shadow_AO.dark",  1, 1, 1, type = "double3")
                cmds.setAttr( "Shadow_AO.bright",  0, 0, 0, type = "double3")
                cmds.setAttr( "Shadow_AO.max_distance", 0.625*diagonal)
                cmds.setAttr( "Shadow_AO.samples", 32)
                cmds.setAttr( "Shadow_AO.spread", 1)
         
                cmds.setAttr( "Contact_AO.dark",  1, 1, 1, type = "double3")
                cmds.setAttr( "Contact_AO.bright",  0, 0, 0, type = "double3")
                cmds.setAttr( "Contact_AO.max_distance", 0.06*diagonal)
                cmds.setAttr( "Contact_AO.samples", 32)
                cmds.setAttr( "Contact_AO.spread", 1)
            
            def CreatebackgroundSwitcher():
                cmds.shadingNode("mip_rayswitch_environment", asShader = True, name = "MR_Background_Switcher")
                cmds.shadingNode("file", asTexture = True, name = "EnvironmentBackground")
                
                cmds.connectAttr( "MR_Background_Switcher.outValue", "Shadow_Matte.background")
                cmds.connectAttr( "EnvironmentBackground.outColor", "MR_Background_Switcher.environment")
                
                try:
                    cmds.setAttr("EnvironmentBackground.fileTextureName", os.path.expanduser('~/maya/Turbosquid/CheckMate Tools For Maya/CM_Tools/hdri/') + "TSHero_HDRI_v9.exr", type = "string")
                except:
                    print "could not open the hdri file"
                cmds.setAttr("MR_Background_Switcher.background", 1, 1, 1, type = "double3")

                
            createBaseMaterials()
            createPrimaryLayer()
            createShadowLight()
            createCompTexLayer()
            CreatebackgroundSwitcher()
            
            cmds.connectAttr("Comp_tex.output", "Opac_comp.inputs[0].color", force = True)
            
            cmds.shadingNode("gammaCorrect", asUtility = True, name = "Gradient_texCorrect")
            cmds.connectAttr("Gradient_tex.outColor", "Gradient_texCorrect.value")
            cmds.connectAttr("Gradient_texCorrect.outValue", "Opac_comp.inputs[1].color")
            cmds.setAttr("Gradient_texCorrect.gammaX", 0.4545)
            cmds.setAttr("Gradient_texCorrect.gammaY", 0.4545)
            cmds.setAttr("Gradient_texCorrect.gammaZ", 0.4545)
            
            cmds.setAttr("Opac_comp.inputs[0].blendMode", 6)
            
            cmds.connectAttr("Shadow_AO.outValue", "DirtBlend.color1")
            
            cmds.shadingNode("gammaCorrect", asUtility = True, name = "GradientClipCorrect")
            cmds.connectAttr("Gradient_clip.outColor", "GradientClipCorrect.value")
            cmds.connectAttr("GradientClipCorrect.outValue", "GradientBlend.color1")
            cmds.setAttr("GradientClipCorrect.gammaX", 0.4545)
            cmds.setAttr("GradientClipCorrect.gammaY", 0.4545)
            cmds.setAttr("GradientClipCorrect.gammaZ", 0.4545)
            
            cmds.setAttr("DirtBlend.color2", 1,1,1, type = "double3")
            cmds.setAttr("GradientBlend.color2", 1,1,1, type = "double3")
            
            createScreenShader("Contact_AO", "DirtBlend")
            cmds.connectAttr("GradientBlend.output", "Comp_tex.input1", force = True)
            cmds.connectAttr("ScreenOut.output", "Comp_tex.input2", force = True)
            
            SG = cmds.sets(renderable = True, noSurfaceShader = True, empty = True, name = 'ShadowSG')   
            cmds.connectAttr(("Shadow_Matte" + '.message'),(SG + '.miMaterialShader'),f=1)
            
            sigLayers = ["Signature", "SQRSignature"]
            for i in sigLayers:
                cmds.editRenderLayerGlobals( currentRenderLayer = i)
                cmds.editRenderLayerAdjustment("MR_Background_Switcher.background")
                cmds.setAttr("MR_Background_Switcher.background", 0.968627, 0.968627, 0.968627, type ="double3")
            subLayers = ["Subdivision_0","Subdivision_1","Wireframe", "UVs"]
            for i in subLayers:
                cmds.editRenderLayerGlobals( currentRenderLayer = i)
                cmds.editRenderLayerAdjustment("MR_Background_Switcher.background")
                cmds.setAttr("MR_Background_Switcher.background", 0.220, 0.290, 0.361, type ="double3")
            
    @staticmethod
    def CreateUVMaterial():
        try:
            cmds.delete("UVShader")
        except:
            pass
        
        try:
            cmds.delete("UVShaderSG")
        except:
            pass
        
        try:
            cmds.delete("CheckerMap")
        except:
            pass
        
        try:
            cmds.delete("TexturePlacer")
        except:
            pass
        
        material = cmds.shadingNode('lambert', asShader=1, name='UVShader')
        SG = cmds.sets(renderable=1, noSurfaceShader=1, empty=1, name = 'UVShaderSG')   
        cmds.connectAttr((material + '.outColor'),(SG + '.surfaceShader'),f=1)
        
        cmds.shadingNode("file", asTexture = True, name = "CheckerMap" )
        cmds.setAttr("CheckerMap.fileTextureName", os.environ['CM_TOOLS'] + "ash_uvgrid.jpg", type = "string")
       
        cmds.connectAttr(  "CheckerMap.outColor", "UVShader.color", force = True)
    
    