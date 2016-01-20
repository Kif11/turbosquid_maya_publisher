import maya.cmds as cmds
import os

import UIBlockFile
import HUDFile
import SnapShotFile
import TurntableFile

reload(TurntableFile)
reload(SnapShotFile)
reload(UIBlockFile)
reload(HUDFile)

class UIClass:
    #Variables to store the name of our base 
    MainWindow = "CMMainWindow"
    MainDock = "CMMainDock"
    
    
    def __init__(self):
        print "Initializing UI class"
        self.CleanUp()
    
    def CleanUp(self):
        print "UI cleaning up"
        #Check to see if the window exists if it does delete it
        if cmds.dockControl(UIClass.MainDock, exists = True):
            try:
                cmds.deleteUI(UIClass.MainDock)
            except:
                print "Could not delete Main Dock"
        elif cmds.window(UIClass.MainWindow, exists = True):
            try:
                cmds.deleteUI(UIClass.MainWindow)
            except:
                print "Could not delete Main Window"
        
        if cmds.headsUpDisplay('SnapButton', exists = True):
            cmds.headsUpDisplay('SnapButton', rem = True)
        print "UI clean up complete"
        
    def BindUI(self, ProjectFunctions, RenderingFunctions):
        cmds.button("BrowserButton", edit = True, c = ProjectFunctions[0])
        cmds.button("PrepButton", edit = True, c = ProjectFunctions[1])
        cmds.button("SRTButton", edit = True, c = ProjectFunctions[2])
        cmds.button("CRTButton", edit = True, c = ProjectFunctions[3])
        cmds.button("DescriptionButton", edit = True, c = ProjectFunctions[4])
        cmds.button("ExportButton", edit = True, c = ProjectFunctions[5])
        cmds.button("AboutButton", edit = True, c = ProjectFunctions[6])
        
        cmds.intSlider("SubdivisionLevel", edit = True, cc = RenderingFunctions[0])
        cmds.button("RenderQualityLow" , edit = True,c = RenderingFunctions[1])
        cmds.button("RenderQualityMed" , edit = True,c = RenderingFunctions[2])
        cmds.button("RenderQualityHigh", edit = True,c = RenderingFunctions[3])
        cmds.button("LightingButton", edit = True,c = RenderingFunctions[4])
        cmds.floatField("LightIntensityField", edit = True,cc = RenderingFunctions[5])
        cmds.floatField("HDRIIntensityField", edit = True,cc = RenderingFunctions[6])
        cmds.floatField("EyeLevelField", edit = True,cc = RenderingFunctions[7])
        cmds.button("PlaceText", edit = True,c = RenderingFunctions[8])
        cmds.button("SelectObj", edit = True,c = RenderingFunctions[9])
    
    def CreateCleanUpScriptJobs(self):
        print "Creating cleanup scriptjobs"
        cmds.scriptJob( ro = True, e = ["NewSceneOpened", self.CleanUp])
        cmds.scriptJob( ro = True, e = ["SceneOpened", self.CleanUp])
        print "Created cleanup scriptjobs"
        
    def CreateBaseUI(self, *args):    
        print "Creating the base UI"
        self.CleanUp()
        
        #For when the scene exits
        self.CreateCleanUpScriptJobs()
        
        #Creating the main window    
        cmds.window(UIClass.MainWindow, rtf = True, s = True )
        
        #Create a tab layout this will be the parent layout for all other layouts
        cmds.tabLayout("TabLayout")
        
        #Create the project tab UI elements
        self.CreateProjectTab("TabLayout")
        
        #Create the Snapshot tab UI
        self.CreateSnapShotTab()
        
        #Create the turntable tab UI
        self.CreateTurntableTab()
        
        #Create the rendering tab UI
        self.CreateRenderingTab()
        
        #Create HUD interface
        self.HUD = HUDFile.HUDClass()
        
        #Bind to hud function
        self.HUD.BindFunctions([SnapShotFile.SnapShotClass.CreateSnapshot, TurntableFile.TurntableClass.CreateTurntable])
        
        #Attach the tabs to the tablayout
        cmds.tabLayout( "TabLayout", edit=True, w = 354, tabLabel =  [("CMProjectLayout", 'Project'), ("SnapShotTabLayout", 'SnapShots'), ("TurntableCounterLayout", "Turntables"), ("BatchRendererCounterLayout", "Render setup")], cc = self.HUD.HUDInterface )
        
        #Show the window
        cmds.showWindow(UIClass.MainWindow)
        
        print "Base UI created"
        
        try:
            #Dock the window
            cmds.dockControl( UIClass.MainDock, label = "CheckMate Tools", area = "left", content = UIClass.MainWindow, allowedArea = ["right", "left"]) 
        except RuntimeError, e: 
            print "Failed to dock window", e
            
        
    def CreateProjectTab(self, ParentLayout):
        print "Creating the project tab"
        cmds.formLayout( "CMProjectLayout" , p = "TabLayout", numberOfDivisions=100)  
        cmds.columnLayout("ProjectColLayout", p = "CMProjectLayout", adjustableColumn = True)
        
        self.OpenInBrowserBlock = UIBlockFile.UIBlockClass("ProjectColLayout", [
                                             ["button", "Open Project in browser", "none", "Browser"],
                                             ])
        
        self.ScenePrepBlock = UIBlockFile.UIBlockClass("ProjectColLayout", [
                                             ["text", "Scene preparation", "single", "Prep"],
                                             ["textfield", "single", "Name"],
                                             ["button", "Prep Scene", "DoNotCreate", "Prep"],
                                             ["checkbox", "Use selection", "DoNotCreate", "Prep"]
                                             ])
        
        self.ScaleReviewBlock = UIBlockFile.UIBlockClass("ProjectColLayout", [
                                                          ["text", "Scale review tool", "single", "SRT"],
                                                          ["button", "Scale review tool", "single", "SRT"]
                                                          ])
        
        self.CheckmateReviewBlock = UIBlockFile.UIBlockClass("ProjectColLayout", [
                                                              ["text", "Checkmate review tools", "single", "CRT"],
                                                              ["button", "Checkmate review tools", "single", "CRT"]
                                                              ])
        
        self.DescriptionBlock = UIBlockFile.UIBlockClass("ProjectColLayout", [
                                                              ["text", "Project description", "single", "Description"],
                                                              ["button", "Write description", "single", "Description"]
                                                              ])
        
        
        
        fileName = cmds.file(l = True, q = True)
        fileName = fileName[0]
        Extension = os.path.splitext(fileName)[1]
        if Extension == '.ma':
            fileType = "ma"
        elif Extension == '.mb':
            fileType = "mb"
        elif Extension == "":
            fileType = "ma"
        ExportTypes = [fileType, "STL_DCE", "DXF_DCE", "FBX export"]
        self.ExportBlock = UIBlockFile.UIBlockClass("ProjectColLayout", [
                                                              ["text", "Package scene", "single", "Export"],
                                                              ["text", "Select export formats", "single", "Format"],
                                                              ["textscrolllist", 5, "DoNotCreate", "Export", True, ExportTypes, ExportTypes, 4, 70],
                                                              ["checkbox", "Export Shadow Plane", "DoNotCreate", "ShadowPlane"],
                                                              ["checkbox", "Export Light Rig", "DoNotCreate", "CMLightRig"],
                                                              ["checkbox", "Export User Lights", "DoNotCreate", "UserLights"],
                                                              ["checkbox", "Export Background", "DoNotCreate", "CMBackground"],
                                                              ["button", "Export and archive", "DoNotCreate", "Export"]
                                                              ])
        
        self.AboutBlock = UIBlockFile.UIBlockClass("CMProjectLayout", [
                                               ["button", "About", "DoNotCreate", "About"]
                                               ])
        
        cmds.formLayout( "CMProjectLayout", edit=True, attachForm=[("ProjectColLayout", 'top', 5), ("ProjectColLayout", 'left', 5), ("ProjectColLayout", 'right', 5), 
                                                                   ("AboutButton", 'left', 5), ("AboutButton", 'bottom', 5), ("AboutButton", 'right', 5) ],
                                                                   attachNone= ("AboutButton", 'top'), attachControl = [("ProjectColLayout", 'bottom', 5, "AboutButton")] )
        print "Created project tab"
        
    def CreateSnapShotTab(self):
        print "Creating SnapshotTab"
        cmds.formLayout( "SnapShotTabLayout", p = "TabLayout", numberOfDivisions=100)
        cmds.scrollLayout( "SnapShotScrollLayout", p = "SnapShotTabLayout")
        cmds.text("SnapCounter" , p = "SnapShotTabLayout", bgc = [0.361, 0, 0], label = "Image Count = 0" + ", Min required are 6"  , w = 296, h = 20, font = "boldLabelFont")
        cmds.formLayout( "SnapShotTabLayout", edit=True, attachForm=[("SnapShotScrollLayout", 'top', 5), 
                                                                  ("SnapShotScrollLayout", 'left', 5), 
                                                                  ("SnapShotScrollLayout", 'right', 5), 
                                                                  ("SnapCounter", 'left', 5), 
                                                                  ("SnapCounter", 'bottom', 5), 
                                                                  ("SnapCounter", 'right', 5) ], 
                        attachControl=[("SnapShotScrollLayout", 'bottom', 5, "SnapCounter")], attachNone=("SnapCounter", 'top') )
        
        cmds.columnLayout( "SnapShotLayout", p = "SnapShotScrollLayout", adjustableColumn = True )
        cmds.separator("BufferSS", h = 600, p = "SnapShotLayout", style = "none")
        print "Created SnapshotTab"
        
    def CreateTurntableTab(self):
        print "Creating the turntable tab"
        cmds.formLayout( "TurntableCounterLayout", p = "TabLayout", numberOfDivisions=100)
        cmds.scrollLayout( "TurnTableScrollLayout" , p = "TurntableCounterLayout")
        cmds.columnLayout( "TurnTableLayout", p = "TurnTableScrollLayout", adjustableColumn = True )
        cmds.text("TurntableCounter", p = "TurntableCounterLayout", bgc = [0.361, 0, 0], label = "Turntable Count = 0"  + ", Min required is 1"  , w = 309, h = 20, font = "boldLabelFont")
        cmds.formLayout( "TurntableCounterLayout", edit=True, attachForm=[("TurnTableScrollLayout", 'top', 5), ("TurnTableScrollLayout", 'left', 5), ("TurnTableScrollLayout", 'right', 5), 
                                                                     ("TurntableCounter", 'left', 5), ("TurntableCounter", 'bottom', 5), ("TurntableCounter", 'right', 5) ],
                         attachControl=[("TurnTableScrollLayout", 'bottom', 5, "TurntableCounter")], attachNone=("TurntableCounter", 'top') )
        cmds.separator("BufferTT", h = 600, p = "TurnTableLayout", style = "none")
        print "Created the turntable tab"
    
    def CreateRenderingTab(self):
        print "Creating the rendering tab"
        cmds.formLayout( "BatchRendererCounterLayout", p = "TabLayout", numberOfDivisions=100)
        cmds.scrollLayout( "BatchRendererScrollLayout", p = "BatchRendererCounterLayout")
        cmds.columnLayout( "BatchRendererLayout", p = "BatchRendererScrollLayout", adjustableColumn = True )
        cmds.text("BatchRendererCounter", p = "BatchRendererCounterLayout", bgc = [0.361, 0.361, 0.361], label = "Image to render = 0"  , w = 309, h = 20, font = "boldLabelFont")
        cmds.formLayout( "BatchRendererCounterLayout", edit=True, attachForm=[("BatchRendererScrollLayout", 'top', 5), ("BatchRendererScrollLayout", 'left', 5), ("BatchRendererScrollLayout", 'right', 5), ("BatchRendererCounter", 'left', 5), ("BatchRendererCounter", 'bottom', 5), ("BatchRendererCounter", 'right', 5) ], attachControl=[("BatchRendererScrollLayout", 'bottom', 5, "BatchRendererCounter")], attachNone=("BatchRendererCounter", 'top') )
        
        #Rendering Presets heading
        cmds.separator(p = "BatchRendererLayout", w = 309, h = 15, style = "single", hr = True)
        cmds.text(p = "BatchRendererLayout", label = "Settings",font = "boldLabelFont")
        cmds.separator(p = "BatchRendererLayout", w = 309, h = 15, style = "single", hr = True)
        
        #Quality preset button
        
        cmds.text(p = "BatchRendererLayout", label = "Subdivision level")
        cmds.separator(p = "BatchRendererLayout", w = 309, h = 10, style = "none")
        cmds.intSlider("SubdivisionLevel", p = "BatchRendererLayout", minValue = 0, maxValue = 2, value = 0)
        cmds.separator(p = "BatchRendererLayout", w = 309, h = 10, style = "none")
        
        cmds.text("RenderQualityText",p = "BatchRendererLayout", label = "Rendering quality presets")
        cmds.separator("RenderQualitySep1",p = "BatchRendererLayout", w = 309, h = 10, style = "none")
        
        cmds.rowLayout("RenderQualityLayout", nc = 5, p = "BatchRendererLayout")
        cmds.button("RenderQualityLow", label = "Low", p = "RenderQualityLayout" , w = 100, h = 25, bgc = [0.361, 0.361, 0.361] )
        cmds.button("RenderQualityMed", label = "Medium", p = "RenderQualityLayout", w = 100, h = 25, bgc = [0.361, 0.361, 0.361] )
        cmds.button("RenderQualityHigh", label = "High", p = "RenderQualityLayout" , w = 100, h = 25, bgc = [0.361, 0.361, 0.361] )
        cmds.separator("RenderQualitySep",p = "BatchRendererLayout", w = 309, h = 10, style = "none")
        
        #Lighting Presets heading
        cmds.separator("LightSep1",p = "BatchRendererLayout", w = 309, h = 15, style = "single", hr = True)
        cmds.text("LightText1", p = "BatchRendererLayout", label = "Lighting Presets",font = "boldLabelFont")
        cmds.separator("LightSep2", p = "BatchRendererLayout", w = 309, h = 15, style = "single", hr = True)
        
        #Light rig scrolllist
        RigTypes = ["Product Shot", "Outdoors MidDay", "Automotive Classic", "Character", "Food"]
        cmds.text("LightText2", p = "BatchRendererLayout", label = "Select Light Rig",font = "boldLabelFont")
        cmds.separator("LightSep3", h = 10, style = "none",p = "BatchRendererLayout")
        cmds.textScrollList("CB_ScrollList", p = "BatchRendererLayout",  numberOfRows = 5, allowMultiSelection = False, h = 70,
            append = RigTypes,
            selectItem = RigTypes[0], showIndexedItem=4 )
        
        #Create light rig button
        cmds.button("LightingButton", p = "BatchRendererLayout", label = "Create Light Rig", h = 25)    
        
        if cmds.objExists("CMLightRig") and cmds.objExists("CMSettings"):
            if cmds.getAttr("CMSettings.CurrentRig") != None:
                cmds.button("LightingButton", edit = True, label = "Current rig: " + cmds.getAttr("CMSettings.CurrentRig"),  bgc = [0, 0.361, 0])        
        
        if cmds.getAttr("defaultRenderGlobals.currentRenderer") != "vray" and cmds.getAttr("defaultRenderGlobals.currentRenderer") != "mentalRay":
            self.RigUIVisibility(False)
        
        if cmds.objExists("CMLightRig"):
            values = [cmds.getAttr("CMLightRig.LightIntensity"), cmds.getAttr("CMLightRig.HDRIIntensity"), cmds.getAttr("CMLightRig.EyeLevel")]
        else:
            values = [1,1,92]
            
        if cmds.objExists("CMLightRig") and (cmds.getAttr("defaultRenderGlobals.currentRenderer") == "vray" or cmds.getAttr("defaultRenderGlobals.currentRenderer") == "mentalRay"):
            visibility = True
        else:
            visibility = False
        
        #create row layout
        cmds.rowLayout("LightControlLayout", nc = 3, p = "BatchRendererLayout", visible= visibility)
            
        #3-point light intensity
        cmds.text(p = "LightControlLayout", label = "Light Intensity multiplier  ",font = "boldLabelFont")
        cmds.floatField("LightIntensityField", minValue = 0, p = "LightControlLayout", value = values[0] )
        
        #create row layout
        cmds.rowLayout("HDRIControlLayout", nc = 3, p = "BatchRendererLayout", visible= visibility)
        
        #HDRI light intensity
        cmds.text(p = "HDRIControlLayout", label = "HDRI Intensity multiplier  ",font = "boldLabelFont")
        cmds.floatField("HDRIIntensityField", minValue = 0, p = "HDRIControlLayout", value = values[1] )
        
        #create row layout
        cmds.rowLayout("EyeLevelLayout", nc = 3, p = "BatchRendererLayout", visible= visibility)
        
        #Eye Level
        cmds.text(p = "EyeLevelLayout", label = "Character Eye Level  ",font = "boldLabelFont")
        cmds.floatField("EyeLevelField", minValue = 0, p = "EyeLevelLayout", value = values[2] )
        
        #Subdivision Placement heading
        cmds.separator(p = "BatchRendererLayout", w = 309, h = 15, style = "single", hr = True)
        cmds.text("CB_Heading_hsub", p = "BatchRendererLayout", label = "Wireframe settings",font = "boldLabelFont")
        cmds.separator(p = "BatchRendererLayout", w = 309, h = 15, style = "single", hr = True)
        
        #modify subdivisions button
        cmds.button("PlaceText", label = "Subdivision text placement", p = "BatchRendererLayout" , w = 309, h = 25, bgc = [0, 0.361, 0] )
        cmds.separator(p = "BatchRendererLayout", w = 309, h = 10, style = "none")
        
        #Rendering UVs heading
        cmds.separator(p = "BatchRendererLayout", w = 309, h = 15, style = "single", hr = True)
        cmds.text("CB_Heading_hUV", p = "BatchRendererLayout", label = "Rendering UVs",font = "boldLabelFont")
        cmds.separator(p = "BatchRendererLayout", w = 309, h = 15, style = "single", hr = True)
        
        #UV select button
        cmds.button("SelectObj", label = "Render UV templates", p = "BatchRendererLayout" , w = 309, h = 25, bgc = [0, 0.361, 0] )
        
        if cmds.getAttr("defaultRenderGlobals.currentRenderer") != "vray" and cmds.getAttr("defaultRenderGlobals.currentRenderer") != "mentalRay":
            cmds.separator("BottomSPace", p = "BatchRendererLayout", w = 309, h = 300, style = "none")
        else:
            cmds.separator("BottomSPace", p = "BatchRendererLayout", w = 309, h = 200, style = "none")
        print "Created the rendering tab"
        
    def CreateSnapUIs(self):
        if cmds.objExists("CMSettings"):
            SnapShotFile.SnapShotClass.RecreateUI()
    
    def CreateTurntableUIs(self):
        if cmds.objExists("CMSettings"):
            TurntableFile.TurntableClass.RecreateUI()
         
    def ShowOnlyBasicUI(self):
        Check = cmds.objExists("CMSettings")
        
        if cmds.getAttr("defaultRenderGlobals.currentRenderer") == "vray" or cmds.getAttr("defaultRenderGlobals.currentRenderer") == "mentalRay":
            self.RigUIVisibility(True)
        
        HideBlocks = [self.OpenInBrowserBlock,         
                     self.DescriptionBlock,
                     self.ExportBlock]
        
        for i in HideBlocks:
            i.ChangeBlockVisibility(Check)
        
        self.ScenePrepBlock.ChangeBlockVisibility(not Check)
        
        if not Check:
            cmds.tabLayout("TabLayout", edit = True, tv = False, st = "CMProjectLayout")
        else:
            cmds.tabLayout("TabLayout", edit = True, tv = True)

    def RigUIVisibility(self, Visibility):
        #Lighting Presets heading
        cmds.separator("LightSep1",edit = True, visible = Visibility, hr = True)
        cmds.text("LightText1",edit = True, visible = Visibility)
        cmds.separator("LightSep2",edit = True, visible = Visibility, hr = True)
        
        cmds.rowLayout("RenderQualityLayout", edit = True, visible = Visibility )
        cmds.button("RenderQualityLow", edit = True, visible = Visibility )
        cmds.button("RenderQualityMed", edit = True, visible = Visibility )
        cmds.button("RenderQualityHigh", edit = True, visible = Visibility )
        cmds.separator("RenderQualitySep", edit = True, visible = Visibility, hr = True )
        cmds.text("RenderQualityText",edit = True, visible = Visibility)
        cmds.separator("RenderQualitySep1",edit = True, visible = Visibility, hr = True)
        
        #Light rig scrolllist
        cmds.text("LightText2",edit = True, visible = Visibility)
        cmds.separator("LightSep3",edit = True, visible = Visibility, hr = True)
        cmds.textScrollList("CB_ScrollList",edit = True, visible = Visibility)
        
        cmds.button("LightingButton", edit = True, visible = Visibility)        
   
    def UpdateRenderingTab(self):
        #Update the smooth slider
        for mesh in cmds.listRelatives(cmds.getAttr("CMSettings.ModelName"), allDescendents = True, type = "mesh"):
            #Try to retrieve smooth level on the current mesh
            try:
                cmds.intSlider("SubdivisionLevel", edit = True, value = cmds.getAttr(mesh + "Smooth.divisions"))
                break
            except:pass
            
        #Update light rig button
        if not cmds.objExists("CMLightRig"):
            cmds.button("LightingButton", edit = True, label = "Create Light Rig", bgc = [0.361, 0.361, 0.361])
        else:
            cmds.button("LightingButton", edit = True, label = "Current rig: " + cmds.getAttr("CMSettings.CurrentRig"),  bgc = [0, 0.361, 0])

        
        if cmds.objExists("CMLightRig"):
            values = [cmds.getAttr("CMLightRig.LightIntensity"), cmds.getAttr("CMLightRig.HDRIIntensity"), cmds.getAttr("CMLightRig.EyeLevel")]
        else:
            values = [1,1,92]
            
        if cmds.objExists("CMLightRig") and (cmds.getAttr("defaultRenderGlobals.currentRenderer") == "vray" or cmds.getAttr("defaultRenderGlobals.currentRenderer") == "mentalRay"):
            visibility = True
        else:
            visibility = False
        
        #3-point light intensity
        cmds.rowLayout("LightControlLayout", edit = True, visible= visibility)
        cmds.floatField("LightIntensityField", edit = True, value = values[0] )
        
        #HDRI light intensity
        cmds.rowLayout("HDRIControlLayout", edit = True, visible= visibility)
        cmds.floatField("HDRIIntensityField", edit = True, value = values[1] )
        
        #Eye Level
        cmds.rowLayout("EyeLevelLayout", edit = True, visible= visibility)
        cmds.floatField("EyeLevelField", edit = True, value = values[2] )
            