import maya.cmds as cmds

from functools import partial


import UIFile
import ProjectFile
import ScenePrepFile
import DescriptionToolFile
import RWSToolFile
import cm.ui.shelf 
import RenderLayerManagerFile
import SubdivisionTextFile
import RenderingPresets
import LightingPresets
import RenderUVFile
import ExportFile
import SnapShotFile
import TurntableFile

reload(ExportFile)
reload(RenderUVFile)
reload(cm.ui.shelf )
reload(LightingPresets)
reload(RenderingPresets)
reload(SubdivisionTextFile)
reload(RenderLayerManagerFile)
reload(SnapShotFile)
reload(TurntableFile)
reload(RWSToolFile)
reload(DescriptionToolFile)
reload(ProjectFile)
reload(ScenePrepFile)
reload(UIFile)

class SystemClass:
    
    def __init__(self):
        print "System-File Begin"
        self.UI = UIFile.UIClass()
        self.Prep = ScenePrepFile.ScenePrepClass()
        self.Project = ProjectFile.ProjectClass()
        self.Description = DescriptionToolFile.DescriptionToolClass()
        self.RWSTool = RWSToolFile.RWSToolClass()
        
        self.rcscript = -1
        
        #CMSettings is the test object if it exists it means the scene has been prepared before
        
        #Check to see if the model name stored with the file exists and try to fix it if it doesn't
        self.CheckModelNameExists()
        
        #Create the UI
        self.UI.CreateBaseUI()
        
        #Populate the snapshot layout    
        self.UI.CreateSnapUIs()
        
        #Populate the turntable layout
        self.UI.CreateTurntableUIs()
        
        #Script jobs for undo and redo
        self.UndoScript = cmds.scriptJob(ro = False, event = ["Undo", partial(self.OnUndoRedo, True)], kws = True, p = "TabLayout" )
        self.RedoScript = cmds.scriptJob(ro = False, event = ["Redo", partial(self.OnUndoRedo, False)], kws = True, p = "TabLayout" )
        
        #Show the basic UI or complete UI depending on if the scene has been prepared
        self.UI.ShowOnlyBasicUI()
        
        #Bind UI buttons to their corresponding buttons
        self.UI.BindUI(
                       [
                        self.Project.OpenProjectInBrowser, 
                        self.Prepare, 
                        self.RWSTool.start, 
                        cm.ui.shelf.createOptionsWindow, 
                        self.Description.CreateDescription,
                        ExportFile.ExportClass.CreateArchive,
                        self.AboutBox
                        ],
                       
                       [
                        RenderLayerManagerFile.RenderLayerManagerClass.SubdivisionLevelChanged,
                        RenderingPresets.RenderingPresetsClass.LowQualityBtn, 
                        RenderingPresets.RenderingPresetsClass.MedQualityBtn, 
                        RenderingPresets.RenderingPresetsClass.HighQualityBtn,
                        LightingPresets.LightingClass.createLightRig,
                        LightingPresets.LightingClass.ChangeLightIntensity,
                        LightingPresets.LightingClass.ChangeHDRIIntensity,
                        LightingPresets.LightingClass.ChangeEyeLevel,
                        SubdivisionTextFile.SubdivisionTextClass.modifySubdivisions, 
                        RenderUVFile.RenderUVClass.SelectObjectsForUV
                        ]
                       )
        
        #Open the project
        if cmds.objExists("CMSettings"):
            self.Project.OpenProject()
            
            self.Prep.GroupUserLights()
            
            LightingPresets.LightingClass.initLighting()
            
            SnapShotFile.SnapShotClass.UpdatePaths()
            
            #Adjust the visibility of the background objects
            RenderLayerManagerFile.RenderLayerManagerClass.ManageUserRig()
            
            #if self.rcscript == -1:
            self.rcscript = cmds.scriptJob(kws = True, ac = ["defaultRenderGlobals.currentRenderer", self.RendererChanged], ro = True, p = "TabLayout")
            
    #Create new project it is bound to the prep scene button
    def Prepare(self, *args):
        cmds.undoInfo(openChunk = True)
        
        #Get model name 
        if self.Prep.InitializeScene() == 0:
            cmds.undoInfo(closeChunk = True)
            return 0

        #Get project path and set project
        self.Project.CreateProject()
        
        #Prepare the scene
        self.Prep.PrepScene()
        
        #Show the complete UI 
        self.UI.ShowOnlyBasicUI()
        
        #Populate the snapshot layout    
        self.UI.CreateSnapUIs()
        
        #Populate the turntable layout
        self.UI.CreateTurntableUIs()
        
        #Create render layers
        RenderLayerManagerFile.RenderLayerManagerClass.CreateRenderLayers()
        
        #Create shaders
        RenderLayerManagerFile.RenderLayerManagerClass.CreateShaders()
        
        #Set Render layers
        RenderLayerManagerFile.RenderLayerManagerClass.SetRenderLayers()
        
        #Create the image plane
        SnapShotFile.SnapShotClass.CreateImagePlanes()
                
        #Adjust the visibility of the background objects
        RenderLayerManagerFile.RenderLayerManagerClass.ManageUserRig()
        
        #Initialize the lighting class
        LightingPresets.LightingClass.initLighting()
        
        #if using mental ray prompt user to provide background to the matte shader
        if cmds.getAttr("defaultRenderGlobals.currentRenderer") == "mentalRay":
            cmds.confirmDialog(m = "Mental ray requires that the background be set for the MR matte shader, please assign it a background to avoid anomalies in the context/product shots")
        
        #Script job for renderer change
        #if self.rcscript == -1:
        self.rcscript = cmds.scriptJob(kws = True, ac = ["defaultRenderGlobals.currentRenderer", self.RendererChanged], ro = True, p = "TabLayout")
        
        cmds.undoInfo(closeChunk = True)
    
    def CheckModelNameExists(self):
        print "Checking if CMSettings node exists and if the model it points to exists"
        if cmds.objExists("CMSettings"):
            print "CMSettings node exists"
            if not cmds.objExists(cmds.getAttr("CMSettings.ModelName")):
                cmds.confirmDialog(m = "The tool could not locate the mesh. Attempting to get name from model")
                #Check to see if the model is already grouped then use that name#
                testName = self.Prep.SelectedObjectsAreGrouped()
                if  testName != "":
                    cmds.setAttr("CMSettings.ModelName", testName, type = "string")
                    cmds.confirmDialog(m = "Group found")
                    return True
                else:
                    cmds.delete("CMSettings")
                    cmds.confirmDialog(m = "Could not get a model name, please reprepare the scene")
                    return False
        else:
            print "Model found"
    
    def RendererChanged(self):
        drg = cmds.getAttr("defaultRenderGlobals.currentRenderer")
        
        #Create shaders
        RenderLayerManagerFile.RenderLayerManagerClass.CreateShaders()
        
        #if vray is the active
        if drg == "vray":
            self.UI.RigUIVisibility(True)
            cmds.scriptJob(kws = True, ie = RenderLayerManagerFile.RenderLayerManagerClass.SetRenderLayers, ro = True, p = "TabLayout")
        
        #if mental ray is the active
        if drg == "mentalRay":
            self.UI.RigUIVisibility(True)
            cmds.scriptJob(kws = True, ie = RenderLayerManagerFile.RenderLayerManagerClass.SetRenderLayers, ro = True, p = "TabLayout")
            cmds.confirmDialog(m = "Mental ray requires that the background be set for the MR matte shader, please assign it a background to avoid anomalies in the context/product shots")            
        
        #Recreate the image plane
        SnapShotFile.SnapShotClass.CreateImagePlanes()
        
        #Script job for renderer change
        cmds.scriptJob(kws = True, ac = ["defaultRenderGlobals.currentRenderer", self.RendererChanged], ro = True, p = "TabLayout")
    
    def OnUndoRedo(self, Undo):
        self.UI.ShowOnlyBasicUI()
        
        self.UI.CreateSnapUIs()
        
        self.UI.CreateTurntableUIs()
        
        self.UI.UpdateRenderingTab()
    
    def AboutBox(self, *args):
        import os
        
        def GoToWebsite(site):
            cmds.launch( webPage = site)
        
        if cmds.window("AboutWindow", exists = True):
            cmds.deleteUI("AboutWindow")
        cmds.window("AboutWindow")
        cmds.rowLayout("MainLayout", nc = 3, cw3 = [10, 80, 200], rat = [[1, "top", 0],[2, "top", 0],[3, "top", 0]])
        cmds.columnLayout("EmptyColumn", p = "MainLayout")
        cmds.columnLayout("ImageColumn", p = "MainLayout")
        cmds.columnLayout("TextColumn", p = "MainLayout")
        
        cmds.separator(h = 30, p = "TextColumn")
        cmds.text(label = "TurboSquid CheckMate and Publishing Tools for Maya, v1.22", p = "TextColumn")
        cmds.separator(h = 55, p = "TextColumn")
        cmds.text(label = "Created by Titan Software Solutions", p = "TextColumn")
        cmds.separator(h = 55, p = "TextColumn")
        cmds.text(label = "Special thanks to Ashraf Aiad for the use of his UV texture templates", p = "TextColumn")
        
        cmds.separator(h = 10, p = "ImageColumn")
        cmds.iconTextButton(image = os.path.expanduser('~/maya/Turbosquid/CheckMate Tools For Maya/CM_Tools/') + "Logos/CheckMate.png", p = "ImageColumn", c = partial(GoToWebsite, "http://www.turbosquid.com"))
        cmds.separator(h = 20, p = "ImageColumn")
        cmds.iconTextButton(image = os.path.expanduser('~/maya/Turbosquid/CheckMate Tools For Maya/CM_Tools/') + "Logos/TSS.png", p = "ImageColumn", c = partial(GoToWebsite, "http://www.titansoftwaresolutions.net"))
        cmds.separator(h = 20, p = "ImageColumn")
        cmds.iconTextButton(image = os.path.expanduser('~/maya/Turbosquid/CheckMate Tools For Maya/CM_Tools/') + "Logos/PixelCG.png", p = "ImageColumn", c = partial(GoToWebsite, "http://www.pixelcg.com/blog"))
        cmds.separator(h = 10, p = "ImageColumn")
        cmds.showWindow("AboutWindow")
        
    def ResetSnaps(self, *args):
        checkSelect = cmds.confirmDialog( title='Delete animation', message='Are you sure you want to delete all snapshots?', button=['Delete', "Cancel"], defaultButton='Delete', cancelButton='Cancel', dismissString='Cancel' )
        if checkSelect == "Delete":
            for i in range(len(SnapShotFile.SnapShotClass.SnapShots)):
                SnapShotFile.SnapShotClass.SnapShots[0].deleteSnapShot()
        
    def ResetTurntables(self, *args):
        checkSelect = cmds.confirmDialog( title='Delete animation', message='Are you sure you want to delete all snapshots?', button=['Delete', "Cancel"], defaultButton='Delete', cancelButton='Cancel', dismissString='Cancel' )
        if checkSelect == "Delete":
            for i in range(len(TurntableFile.TurntableClass.Turntables)):
                TurntableFile.TurntableClass.Turntables[0].deleteTurntable()