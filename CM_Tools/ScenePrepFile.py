import maya.cmds as cmds
import sys


class ScenePrepClass:
    #The cursel variable is used to hold the model/selected meshes, it is assigned only once in the ModelSelection
    Cursel = []
    #GroupName is used to hold the model name
    GroupName = ""
    #This is a bool to check if the model was already grouped at the time of prep
    alreadyGrouped = False
    #This is to hold the project directory
    OutputDir = ""
    
    def __init__(self):
        print "Initializing scene prep class"
        
        if (cmds.window("GroupWindow", exists=True)):
                cmds.deleteUI("GroupWindow")
    
    def InitializeScene(self):
        print "Initializing scene"
        #Check to see if the scene is empty
        if self.EmptyScene() == 0:
            return 0
        
        #Check to see if an object exists with the same name
        if self.SameName() == 0:
            return 0
        
        #Get selection or use all scene geometry
        self.ModelSelection()
             
        #Get name if empty exit
        if self.GetGroupName() == 0:
            return 0
        
        #Delete or group unselected objects
        self.ManageUnselectedObjects()
        
        #Create a settings node if it doesn't exist
        self.CreateSettingsNode()
                
    def PrepScene(self):
        
        #Delete animation
        self.DeleteAnimation()
        
        #Group Objects with the retrieved name
        self.GroupObjects()
        
        #Group user lights for easy management
        self.GroupUserLights()
        
        #For internal use makes the CM cameras undeleteable
        self.ConvertCamerasToStartUp()
        
        #Delete empty groups
        self.DeleteEmptyGroups()
        
        #Center the main model
        self.Center(ScenePrepClass.GroupName)
        
        #Delete empty display layers
        self.DeleteEmptyLayers()
        
        #Create a new display layer for the model
        self.CreateDisplayLayers()    
        
        #Set the resolution gate in all active viewports
        self.SetResGate()
        
        #Apply smoothing to the main object
        self.ApplySmooth()
        
        #Create the rotation animation for the turntable
        self.CreateAnimation()
        
        print "Successfully preped scene"
        #Returns 1 on successful execution
        return 1
        
    def EmptyScene(self):
        print "Checking for empty scene"
        if cmds.ls(g = True) == []:
            cmds.confirmDialog(m = "Scene contains no usable geometry")
            return 0
    
    def SameName(self):
        import re
        cmds.textField("NameTextField",edit = True, text = re.sub('[^0-9a-zA-Z_]+', '_', cmds.textField("NameTextField",query = True, text = True)))
        if cmds.objExists(cmds.textField("NameTextField",query = True, text = True)):
            cmds.confirmDialog(m = "A node exists with the same name")
            return 0
    
    def ModelSelection(self):
        #####Model selection#######
        if cmds.checkBox("PrepCheckBox", query = True, value = True):
            #Get selected without the exception objects
            self.ExceptionObjects()
            ScenePrepClass.Cursel = cmds.ls(sl = True)
        else:
            #Get all without the exception objects
            cmds.select(ado = True, hi = True)
            self.ExceptionObjects()
            ScenePrepClass.Cursel = cmds.ls(sl = True)
    
    def GetGroupName(self):
        #Check to see if the name is saved with the file
        if cmds.objExists("CMSettings"):
            ScenePrepClass.GroupName = cmds.getAttr("CMSettings.ModelName")
            if cmds.objExists(ScenePrepClass.GroupName):
                print "Group name from save"
                return 1
        
        #Check to see if the model is already grouped then use that name#
        if self.SelectedObjectsAreGrouped() != "":
            if cmds.textField("NameTextField",query = True, text = True) != "":
                #Rename the group if a name has been provided
                cmds.rename(ScenePrepClass.GroupName, cmds.textField("NameTextField",query = True, text = True))
                #Replace the name in cursel
                for x in range(len(ScenePrepClass.Cursel)):
                    if ScenePrepClass.Cursel[x] == ScenePrepClass.GroupName:
                        ScenePrepClass.Cursel[x] = cmds.textField("NameTextField",query = True, text = True)
                #
                ScenePrepClass.GroupName = cmds.textField("NameTextField",query = True, text = True)
            print "Group name from model"
            return 1
        
        #otherwise check the textfield
        if cmds.textField("NameTextField",query = True, text = True) != "":
            ScenePrepClass.GroupName = cmds.textField("NameTextField",query = True, text = True)
            print "Group name from field"
        
        if ScenePrepClass.GroupName == "":
            cmds.confirmDialog(m = "Please enter a name for the model")
            return 0
    
    def CreateSettingsNode(self):
        if not cmds.objExists("CMSettings"):
            cmds.scriptNode(n = "CMSettings")
            cmds.select("CMSettings")
            cmds.addAttr(longName='ModelName', dt ='string')
            cmds.setAttr("CMSettings.ModelName", ScenePrepClass.GroupName,type = "string")
            cmds.addAttr(longName='ProjectPath', dt ='string')
            cmds.addAttr(longName='CurrentRig', dt ='string')
            cmds.setAttr("CMSettings.CurrentRig", "None", type = "string")
            cmds.select(all = True, deselect = True)
    
    def ManageUnselectedObjects(self):
        cmds.select(all = True)
        self.ExceptionObjects()
        UnSelectedObjects = cmds.ls(sl = True)
        AllSceneObjects = []
        Selection = []
        def GetBaseObjects(obj, Input):
            if cmds.nodeType(obj)== "mesh":
                FullPath = obj.split("|")
                if len(FullPath) >1:
                    del FullPath[-1]
                
                Input.append( "|".join(FullPath))
            else:
                Children = cmds.listRelatives(obj, f =True)
                if Children is not None:
                    for c in Children:
                        if c is not None:
                            GetBaseObjects(c, Input)
        
        for s in UnSelectedObjects:        
            GetBaseObjects(s, AllSceneObjects)
        for s in ScenePrepClass.Cursel:        
            GetBaseObjects(s, Selection)
        
        for i in Selection:
            try:
                AllSceneObjects.remove(i)
            except:
                pass
         
        if AllSceneObjects == []:
            return 0
        else:
            check = cmds.confirmDialog( title='group', message='Would you like to delete or group as background the unselected objects?', button=['Delete','Group'], defaultButton='Delete', cancelButton='Group', dismissString='Group' )
            if check == "Delete":
                for a in AllSceneObjects:
                    try:
                        cmds.delete(a)
                    except:
                        pass
                print "Unselected objects have been deleted"
                
            elif check == "Group":    
                if not cmds.objExists("CMBackground"):
                    cmds.group( em=True, name = "CMBackground" )    
                    
                for a in AllSceneObjects:
                    try:
                        cmds.parent(a, "CMBackground", relative=True)
                    except:
                        pass
                print "Unselected objects have been grouped and layered"

    def SelectedObjectsAreGrouped(self):
        ObjParents = []
        CurrentParent = None
        SameParentFlag = False
        FixedParent = ""
        FullPath =""
        for c in ScenePrepClass.Cursel:
            if cmds.listRelatives(c, p = True) == None:### Has no parents
                if cmds.nodeType(cmds.listRelatives(c, f = True)) == "mesh": ### is an object
                    ScenePrepClass.alreadyGrouped = False
                    return ""
                else:### is a group
                    for i in cmds.listRelatives(c, f = True, ad = True):
                        if cmds.nodeType(i) == "mesh":
                            ObjParents.append(cmds.listRelatives(c, f =True))
                            break
            else:
                ObjParents.append(cmds.listRelatives(c, f =True))
        for p in ObjParents:
            if p is not None:
                FixedParent = "".join(ObjParents[0])
                FixedParentList = FixedParent.split("|")
                FixedParent = FixedParentList[1]
                FullPath = "".join(p)
                FullPathList = FullPath.split("|")
                CurrentParent = FullPathList[1]
                if (CurrentParent == FixedParent):
                    SameParentFlag = True
                else:
                    SameParentFlag = False
        if SameParentFlag == True:
            print "Objects are grouped"
            ScenePrepClass.alreadyGrouped = True
            ScenePrepClass.GroupName = CurrentParent
            return CurrentParent
        else:
            ScenePrepClass.alreadyGrouped = False
            print "Objects are not grouped"
            return ""

    def GroupObjects(self):
        if not ScenePrepClass.alreadyGrouped:
            if not cmds.objExists(ScenePrepClass.GroupName):
                cmds.group( em=True, name=ScenePrepClass.GroupName )
            for c in ScenePrepClass.Cursel:
                if c != ScenePrepClass.GroupName:
                    try:
                        cmds.parent(c, ScenePrepClass.GroupName)
                    except:
                        pass
                    
    def ExceptionObjects(self):
        vrayLightNodeTypes = ["VRayLightRectShape","VRayLightSphereShape","VRayLightDomeShape","VRayLightIESShape"]
        #Deselect Vray Lights
        for i in vrayLightNodeTypes:
            if cmds.ls(type = i) != []:
                transformList = cmds.listRelatives(cmds.ls(type = i), parent=True, fullPath=True)
                cmds.select(cmds.ls(type = i), deselect = True)
                cmds.select(transformList, deselect = True)
            
        #Deselect lights
        if cmds.ls(lights = True) != []:
            transformList = cmds.listRelatives(cmds.ls(lights = True), parent=True, fullPath=True)
            cmds.select(cmds.ls(lights = True), deselect = True)
            cmds.select(transformList, deselect = True)
        
        if cmds.ls(type = "mentalrayIblShape") != []:
            transformList = cmds.listRelatives(cmds.ls(type = "mentalrayIblShape"), parent=True, fullPath=True)
            cmds.select(cmds.ls(type = "mentalrayIblShape"), deselect = True)
            cmds.select(transformList, deselect = True)
        
        #Deselect Cameras
        if cmds.ls(cameras = True) != []:
            transformList = cmds.listRelatives(cmds.ls(cameras = True), parent=True, fullPath=True)
            cmds.select(cmds.ls(cameras = True), deselect = True)
            cmds.select(transformList, deselect = True)
        
        if cmds.objExists("CMSettings"):
            cmds.select("CMSettings", deselect = True)
        if cmds.objExists("CMLightRig"):
            cmds.select("CMLightRig", deselect = True)
        if cmds.objExists("CMPointTarget"):
            cmds.select("CMPointTarget", deselect = True)
        if cmds.objExists("CMHiLightTarget"):
            cmds.select("CMHiLightTarget", deselect = True)
        if cmds.objExists("ShadowPlane"):
            cmds.select("ShadowPlane", deselect = True)
        if cmds.objExists("RWSPlane"):
            cmds.select("RWSPlane", deselect = True)
        if cmds.objExists("FoodCard"):
            cmds.select("FoodCard", deselect = True)
        if cmds.objExists("CMBackground"):
            cmds.select("CMBackground", deselect = True)
        if cmds.objExists("UserLights"):
            cmds.select("UserLights", deselect = True)
        if cmds.objExists(ScenePrepClass.GroupName+"_layer"):
            cmds.select(ScenePrepClass.GroupName+"_layer", deselect = True)
           
    def ConvertCamerasToStartUp(self):
        #Convert the snapshot cameras to startup
        i = 0
        while(cmds.objExists( "shot_" + str(i))):
            cmds.camera("shot_" + str(i), edit = True, startupCamera = True)      
            i = i + 1
            
        #Convert the turntable cameras to startup
        i = 0
        while(cmds.objExists( "CM_Turntable_Camera_" + str(i) )):
            cmds.camera("CM_Turntable_Camera_" + str(i), edit = True, startupCamera = True)  
            i = i + 1
        
    def GroupUserLights(self):
        transformList = []
        
        vrayLightNodeTypes = ["VRayLightRectShape","VRayLightSphereShape","VRayLightDomeShape","VRayLightIESShape"]
        #Deselect Vray Lights
        for i in vrayLightNodeTypes:
            #Vray lights are locator types
            if cmds.ls(type = i) != []:
                transformList = transformList + cmds.listRelatives(cmds.ls(type = i), parent=True, fullPath=True)
        
        #Normal lights
        if cmds.ls(lights = True) != []:
            transformList = transformList + cmds.listRelatives(cmds.ls(lights = True), parent=True, fullPath=True)
        
        #Mental ray IBL light
        if cmds.ls(type = "mentalrayIblShape") != []:
            transformList = transformList +  cmds.listRelatives(cmds.ls(type = "mentalrayIblShape"), parent=True, fullPath=True)
        
        #CM light rig lights
        lights = ["CMKeyLight","CMFillLight","CMBackLight","CMKeySpec","CMFillSpec","CMSunLight","CMHiLight1","CMHiLight2","CMDomeLight","MREnvironment"]
         
        for i in lights:
            try:transformList.remove(i)
            except:pass
            try:transformList.remove("MR" + i)
            except:pass
            try:transformList.remove("|CMLightRig|MR" + i)
            except:pass
            try:transformList.remove("|CMLightRig|" + i)
            except:pass
             
        if (not cmds.objExists("UserLights")) and (transformList != []):
            cmds.group( em=True, name = "UserLights" )  
            try:
                cmds.parent(transformList, "UserLights", relative=True)
            except:
                pass    
        elif cmds.objExists("UserLights") and (transformList != []):
            try:
                cmds.parent(transformList, "UserLights", relative=True)
            except:
                pass    
    
    def DeleteEmptyGroups(self):
        for a in cmds.ls():
            if cmds.nodeType(a) == "transform":
                if cmds.listRelatives(a, c =True) == None:
                    cmds.delete(a)
        print "Empty groups deleted"
        
    def DeleteEmptyLayers(self):
        for a in cmds.ls():
            if cmds.nodeType(a) == "displayLayer":
                if a == "defaultLayer":
                    continue
                try:
                    cmds.delete(a)
                except:
                    pass
        print "Empty layers deleted"
    
    def DeleteUnselectedGroups(self):
        cmds.select(cmds.ls(g = True),ado = True)
        UnSelGrps = cmds.ls(sl = True, transforms = True)
        def GroupOrNot(obj):
            if cmds.nodeType(obj) == "transform":
                if cmds.listRelatives(obj, c =True) == None:
                    cmds.delete(obj)
                else:
                    child = cmds.listRelatives(obj, f =True)
                    for c in child:
                        GroupOrNot(c)
            else:
                pass
        for u in UnSelGrps:
            GroupOrNot(u)
        print "Unselected groups deleted"
    
    def CreateDisplayLayers(self):
        cmds.select(ScenePrepClass.GroupName)
        LayerName = ScenePrepClass.GroupName + "_layer"
        if cmds.objExists(LayerName):
            cmds.delete(LayerName)
        cmds.createDisplayLayer(name = LayerName , nr = False)
        print "Primary display Layer Created"
        
        cmds.select(cmds.listRelatives(cmds.ls(cameras = True, lights = True),parent = True))
        try:
            cmds.select("UserLights", add = True)
        except:
            pass
        try:
            cmds.select("CMLightRig", add = True)
        except:
            pass
        LayerName = "CM Lights and Cameras"
        if cmds.objExists(LayerName):
            cmds.delete(LayerName)
        cmds.createDisplayLayer(name = LayerName , nr = False)
        print "Lights and cameras layer Created"

    def Center(self, groupName):
        cmds.xform(groupName,cp =True)
        GroupCenter = cmds.objectCenter(groupName, gl = True)
        cmds.move(-GroupCenter[0],-GroupCenter[1],-GroupCenter[2], groupName, relative = True )
        
        if cmds.objExists("CMBackground"):
            cmds.move(-GroupCenter[0],-GroupCenter[1],-GroupCenter[2], "CMBackground", relative = True )
        if cmds.objExists("UserLights"):
            cmds.move(-GroupCenter[0],-GroupCenter[1],-GroupCenter[2], "UserLights", relative = True )
            
        try:cmds.makeIdentity(groupName, apply = True)
        except:print "Could not reset transforms"
        
        if GroupCenter == cmds.objectCenter(groupName, gl = True):
            pass
        else:
            GroupCenterChk= cmds.objectCenter(groupName, gl = True)
            if GroupCenter[0]== - GroupCenterChk[0] and GroupCenter[1]== - GroupCenterChk[1] and GroupCenter[2]== - GroupCenterChk[2]:
                print "Objects are centered"
                pass
            else:
                self.Center(groupName)
                print "Objects are centered"
            
        bbx = cmds.xform(groupName, bb = True, q = True)
        if bbx[1]<0:
            cmds.move(0,-bbx[1],0, groupName)
            if cmds.objExists("CMBackground"):
                cmds.move(0,-bbx[1],0, "CMBackground", relative = True )
            if cmds.objExists("UserLights"):
                cmds.move(0,-bbx[1],0, "UserLights", relative = True )
            
        else:
            pass
        try:cmds.makeIdentity(groupName, apply = True)
        except:print "Could not reset transform"
        
    def DeleteAnimation(self):
        checkAnim = cmds.confirmDialog( title='Delete animation', message='The tools require that any animation on the model be deleted, press ok to delete the animation and proceed', button=['Ok','Cancel'], defaultButton='Ok', cancelButton='Cancel', dismissString='Cancel' )
        if checkAnim == 'Cancel':
            sys.exit()
        elif checkAnim == 'ok':
            cmds.cutKey(cmds.select(cmds.ls(geometry = True), ado=True, hi = True), s=True)#delete key command
    
    def CreateAnimation(self):
        import maya.mel as mel
        # get the up axis:
        axis =  cmds.upAxis(query=True, axis=True)
        cmds.currentTime( 0 )
        
        if axis == 'y':     
            cmds.setKeyframe( cmds.getAttr("CMSettings.ModelName"), attribute='rotateY', itt = 'linear', ott = 'linear' )
            cmds.currentTime( 36 )
            cmds.rotate( 0, 360, 0, cmds.getAttr("CMSettings.ModelName"))
            cmds.setKeyframe( cmds.getAttr("CMSettings.ModelName"), attribute='rotateY', itt = 'linear', ott = 'linear' )
            
        if axis == 'z':     
            cmds.setKeyframe( cmds.getAttr("CMSettings.ModelName"), attribute='rotateZ', itt = 'linear', ott = 'linear' )
            cmds.currentTime( 36 )
            cmds.rotate(0, 0, 360, cmds.getAttr("CMSettings.ModelName"))
            cmds.setKeyframe( cmds.getAttr("CMSettings.ModelName"), attribute='rotateZ', itt = 'linear', ott = 'linear' )
        
        
        cmds.currentTime( 0 )
        mel.eval("setPlaybackRangeToMinMax;")
    
    def SetResGate(self):
        #Set the resolution gate in all viewports
        for i in range(1,5):
            camera = cmds.modelEditor ( "modelPanel" + str(i), q = True, camera = True )
            cmds.camera( camera, edit = True, displayFilmGate = False, displayResolution = True, overscan = 1.3)
            cmds.camera( camera, edit = True, filmFit = "fill", displayGateMask = False)
    
    def ApplySmooth(self):
        cmds.displaySmoothness(divisionsU = 0, divisionsV = 0, pointsWire = 4, pointsShaded = 1, polygonObject = 1)
        
        for mesh in cmds.listRelatives(cmds.getAttr("CMSettings.ModelName"), allDescendents = True, type = "mesh"):
            #If the mesh is an intermediate object ignore it
            try:
                if cmds.getAttr( mesh + ".intermediateObject"):
                    continue;
            except:
                pass
            
            #Try to delete smooth on the current mesh
            try:
                cmds.setAttr(mesh + "Smooth.divisions", 0)
                cmds.delete(mesh + "Smooth")
            except:pass
            
            #Try to apply smooth on the mesh
            try:
                Smooth = cmds.polySmooth(mesh, dv = 0)
                cmds.rename(Smooth, mesh+"Smooth")
            except:pass
            
    def CreateProjectDirectory(self):
        #While the user doesn't create a unique and valid project keep prompting him to do so
        while True:
            #Select the output directory 
            ScenePrepClass.OutputDir = ""
            try:
                ScenePrepClass.OutputDir = cmds.fileDialog2(fm = 3, fileFilter = None, ds = 2, cap = "Please select a CM project directory")[0]
            except:      
                print "No directory specified"
                #If no output directory is specified delete everything and exit
                self.Exit()
                sys.exit()