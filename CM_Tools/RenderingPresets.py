import maya.cmds as cmds


class RenderingPresetsClass:
    
    @staticmethod
    def HighQualityBtn(*args):
        cmds.undoInfo(openChunk = True)
        
        if cmds.getAttr("defaultRenderGlobals.currentRenderer") == "vray":
            RenderingPresetsClass.HighQualityVray()
        elif cmds.getAttr("defaultRenderGlobals.currentRenderer") == "mentalRay":
            RenderingPresetsClass.HighQualityMR()
            
        cmds.undoInfo(closeChunk = True)
        
    @staticmethod
    def MedQualityBtn(*args):
        cmds.undoInfo(openChunk = True)
        
        if cmds.getAttr("defaultRenderGlobals.currentRenderer") == "vray":
            RenderingPresetsClass.MedQualityVray()
        elif cmds.getAttr("defaultRenderGlobals.currentRenderer") == "mentalRay":
            RenderingPresetsClass.MedQualityMR()
            
        cmds.undoInfo(closeChunk = True)
    
    @staticmethod
    def LowQualityBtn(*args):
        cmds.undoInfo(openChunk = True)
        
        if cmds.getAttr("defaultRenderGlobals.currentRenderer") == "vray":
            RenderingPresetsClass.LowQualityVray()
        elif cmds.getAttr("defaultRenderGlobals.currentRenderer") == "mentalRay":
            RenderingPresetsClass.LowQualityMR()
            
        cmds.undoInfo(closeChunk = True)
    
    @staticmethod
    def HighQualityVray():
        try:
            cmds.setAttr("vraySettings.ddisplac_maxSubdivs", 4)
            cmds.setAttr("vraySettings.globopt_render_viewport_subdivision", 1)
            cmds.setAttr("vraySettings.giOn", True)
            cmds.setAttr("vraySettings.imap_showCalcPhase", True)
            cmds.setAttr("vraySettings.primaryEngine", 0)
            cmds.setAttr("vraySettings.secondaryEngine", 3)
            cmds.setAttr("vraySettings.imap_currentPreset", 4)
            cmds.setAttr("vraySettings.subdivMaxRate", 4)
            cmds.setAttr("vraySettings.dmcs_adaptiveMinSamples", 16)
            cmds.setAttr("vraySettings.dmcs_subdivsMult", 2)
            cmds.setAttr("vraySettings.sys_rayc_dynMemLimit", 4000)
            cmds.setAttr("vraySettings.sys_regsgen_xc", 64)
            cmds.setAttr("vraySettings.cmap_gamma", 2.2)
            cmds.setAttr("vraySettings.cmap_subpixelMapping", 1)
            cmds.setAttr("vraySettings.cmap_affectBackground", 0)
            cmds.setAttr("vraySettings.aaFilterOn", 1)
            cmds.setAttr("vraySettings.aaFilterType", 5)
            cmds.setAttr("vraySettings.dmcs_timeDependent", 1)
            cmds.setAttr("vraySettings.dmcLockThreshold", 1)
            cmds.setAttr("vraySettings.vfbOn", 1)

            
            for i in cmds.ls(type = "locator"):
                try:cmds.setAttr(i + ".subdivs", 24)
                except:pass
            
            
        except:
            pass
        
    @staticmethod
    def MedQualityVray():
        try:
            cmds.setAttr("vraySettings.ddisplac_maxSubdivs", 4)
            cmds.setAttr("vraySettings.globopt_render_viewport_subdivision", 1)
            cmds.setAttr("vraySettings.giOn", True)
            cmds.setAttr("vraySettings.imap_showCalcPhase", True)
            cmds.setAttr("vraySettings.primaryEngine", 0)
            cmds.setAttr("vraySettings.secondaryEngine", 3)
            cmds.setAttr("vraySettings.imap_currentPreset", 3)
            cmds.setAttr("vraySettings.subdivMaxRate", 2)
            cmds.setAttr("vraySettings.dmcs_adaptiveMinSamples", 8)
            cmds.setAttr("vraySettings.dmcs_subdivsMult", 1)
            cmds.setAttr("vraySettings.sys_rayc_dynMemLimit", 4000)
            cmds.setAttr("vraySettings.sys_regsgen_xc", 64)
            cmds.setAttr("vraySettings.cmap_gamma", 2.2)
            cmds.setAttr("vraySettings.cmap_subpixelMapping", 1)
            cmds.setAttr("vraySettings.cmap_affectBackground", 0)
            cmds.setAttr("vraySettings.aaFilterOn", 1)
            cmds.setAttr("vraySettings.aaFilterType", 5)
            cmds.setAttr("vraySettings.dmcs_timeDependent", 1)
            cmds.setAttr("vraySettings.dmcLockThreshold", 1)
            cmds.setAttr("vraySettings.vfbOn", 1)
            

        except:
            pass

        for i in cmds.ls(type = "locator"):
            try:cmds.setAttr(i + ".subdivs", 12)
            except:pass
        
    @staticmethod
    def LowQualityVray():
        try:
            cmds.setAttr("vraySettings.ddisplac_maxSubdivs", 4)
            cmds.setAttr("vraySettings.globopt_render_viewport_subdivision", 1)
            cmds.setAttr("vraySettings.giOn", True)
            cmds.setAttr("vraySettings.imap_showCalcPhase", True)
            cmds.setAttr("vraySettings.primaryEngine", 0)
            cmds.setAttr("vraySettings.secondaryEngine", 3)
            cmds.setAttr("vraySettings.imap_currentPreset", 1)
            cmds.setAttr("vraySettings.subdivMaxRate", 2)
            cmds.setAttr("vraySettings.dmcs_adaptiveMinSamples", 4)
            cmds.setAttr("vraySettings.dmcs_subdivsMult", 0.5)
            cmds.setAttr("vraySettings.sys_rayc_dynMemLimit", 4000)
            cmds.setAttr("vraySettings.sys_regsgen_xc", 64)
            cmds.setAttr("vraySettings.cmap_gamma", 2.2)
            cmds.setAttr("vraySettings.cmap_subpixelMapping", 1)
            cmds.setAttr("vraySettings.cmap_affectBackground", 0)
            cmds.setAttr("vraySettings.aaFilterOn", 1)
            cmds.setAttr("vraySettings.aaFilterType", 5)
            cmds.setAttr("vraySettings.dmcs_timeDependent", 1)
            cmds.setAttr("vraySettings.dmcLockThreshold", 1)
            cmds.setAttr("vraySettings.vfbOn", 1)

            
            for i in cmds.ls(type = "locator"):
                try:cmds.setAttr(i + ".subdivs", 8)
                except:pass
        except:
            pass

    @staticmethod
    def HighQualityMR():
        cmds.setAttr("defaultRenderGlobals.enableDefaultLight", 0)
        cmds.setAttr("miDefaultOptions.filter", 3)
        cmds.setAttr("miDefaultOptions.filterWidth", 0.75)
        cmds.setAttr("miDefaultOptions.filterHeight", 0.75)
        cmds.setAttr("miDefaultOptions.finalGather", True)
        cmds.setAttr("miDefaultOptions.finalGatherPresampleDensity", 1.5)
        cmds.setAttr("miDefaultOptions.finalGatherRays", 500)
        cmds.setAttr("miDefaultOptions.finalGatherPoints", 30)
        cmds.setAttr("miDefaultOptions.finalGatherTraceDiffuse", 2)

    @staticmethod
    def MedQualityMR():
        cmds.setAttr("defaultRenderGlobals.enableDefaultLight", 0)
        cmds.setAttr("miDefaultOptions.filter", 2)
        cmds.setAttr("miDefaultOptions.filterWidth", 0.5)
        cmds.setAttr("miDefaultOptions.filterHeight", 0.5)
        cmds.setAttr("miDefaultOptions.finalGather", True)
        cmds.setAttr("miDefaultOptions.finalGatherPresampleDensity", 0.8)
        cmds.setAttr("miDefaultOptions.finalGatherRays", 250)
        cmds.setAttr("miDefaultOptions.finalGatherPoints", 30)
        cmds.setAttr("miDefaultOptions.finalGatherTraceDiffuse", 2)
        
    @staticmethod
    def LowQualityMR():
        cmds.setAttr("defaultRenderGlobals.enableDefaultLight", 0)
        cmds.setAttr("miDefaultOptions.filter", 0)
        cmds.setAttr("miDefaultOptions.filterWidth", 0.5)
        cmds.setAttr("miDefaultOptions.filterHeight", 0.5)
        cmds.setAttr("miDefaultOptions.finalGather", True)
        cmds.setAttr("miDefaultOptions.finalGatherPresampleDensity", 0.4)
        cmds.setAttr("miDefaultOptions.finalGatherRays", 150)
        cmds.setAttr("miDefaultOptions.finalGatherPoints", 30)
        cmds.setAttr("miDefaultOptions.finalGatherTraceDiffuse", 2)