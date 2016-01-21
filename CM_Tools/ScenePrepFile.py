import sys
import re
import logger
import maya.cmds as cmds
import maya.mel as mel

reload(logger)

from logger import Logger

log = Logger()

CM_SETTINGS = 'CMSettings'

class ScenePrep:

    def __init__(self, output_dir=''):

        log.info('Initializing scene prep class')

        # Theself.curselvariable is used to hold the model/selected meshes,
        # it is assigned only once in the model_selection
        self.cursel= []
        # Hold the model name
        self.group_name = ''
        # This is a bool to check if the model was already grouped at the time of prep
        self.already_grouped = False
        # This is to hold the project directory
        self.output_dir = output_dir

        if (cmds.window('GroupWindow', exists=True)):
                cmds.deleteUI('GroupWindow')

    def initialize_scene(self):

        log.info('Initializing scene')

        # Check to see if the scene is empty
        if self.empty_scene() == 0:
            return 0

        # Check to see if an object exists with the same name
        # if self.same_name() == 0:
        #     return 0

        # Get selection or use all scene geometry
        self.model_selection()

        # Get name if empty exit
        if self.get_group_name() == 0:
            return 0

        # Delete or group unselected objects
        self.manage_unselected()

        # Create a settings node if it doesn't exist
        self.create_settings_node()

    def prep_scene(self):

        # Group Objects with the retrieved name
        self.group_objects()

        # Group user lights for easy management
        # self.GroupUserLights()

        # For internal use makes the CM cameras undeleteable
        self.convert_cameras_to_startup()

        # Delete empty groups
        self.delete_empty_groups()

        # Center the main model
        # self.Center(self.group_name)

        # Delete empty display layers
        self.delete_empty_layers()

        # Create a new display layer for the model
        self.create_display_layers()

        # Set the resolution gate in all active viewports
        self.set_res_gate()

        # Apply smoothing to the main object
        # self.ApplySmooth()

        # Create the rotation animation for the turntable
        # self.CreateAnimation()

        log.info('Successfully preped scene')

    def empty_scene(self):
        log.info('Checking for empty scene')
        if cmds.ls(g = True) == []:
            cmds.confirmDialog(m = 'Scene contains no usable geometry')

    def same_name(self):
        cmds.textField('NameTextField', edit=True, text=re.sub('[^0-9a-zA-Z_]+', '_',
                        cmds.textField('NameTextField', query=True, text=True)))

        if cmds.objExists(cmds.textField('NameTextField', query=True, text=True)):
            cmds.confirmDialog(m='A node exists with the same name')

    def model_selection(self):
        # Model selection
        if cmds.checkBox("PrepCheckBox", query=True, value=True):
        # TODO(Kirill): Make to work with cli and ui
            # Get selected without the exception objects
            self.exception_objects()
            self.cursel = cmds.ls(sl=True)
        else:
            # Get all without the exception objects
            cmds.select(ado=True, hi=True)
            self.exception_objects()
            self.cursel = cmds.ls(sl=True)

    def get_group_name(self):
        # Check to see if the name is saved with the file
        if cmds.objExists('CMSettings'):
            self.group_name = cmds.getAttr('CMSettings.ModelName')
            if cmds.objExists(self.group_name):
                log.info('Group name from save')
                return 1

        # Check to see if the model is already grouped then use that name
        if self.selected_objects_grouped() != '':
            if cmds.textField('NameTextField',query=True, text=True) != '':
                # Rename the group if a name has been provided
                cmds.rename(self.group_name, cmds.textField('NameTextField',query=True, text=True))
                # Replace the name in cursel
                for x in range(len(self.cursel)):
                    if self.cursel[x] == self.group_name:
                        self.cursel[x] = cmds.textField('NameTextField',query=True, text=True)
                self.group_name = cmds.textField('NameTextField',query=True, text=True)
            log.info('Group name from model')
            return 1

        # Otherwise check the textfield
        if cmds.textField("NameTextField",query=True, text=True) != "":
            self.group_name = cmds.textField("NameTextField",query=True, text=True)
            log.info("Group name from field")

        if self.group_name == "":
            cmds.confirmDialog(m="Please enter a name for the model")
            return 0

    def create_settings_node(self):

        if not cmds.objExists(CM_SETTINGS):
            cmds.scriptNode(n = CM_SETTINGS)
            cmds.select(CM_SETTINGS)
            cmds.addAttr(longName='ModelName', dt='string')
            cmds.setAttr(CM_SETTINGS + '.ModelName', self.group_name, type = 'string')
            cmds.addAttr(longName='ProjectPath', dt='string')
            cmds.addAttr(longName='CurrentRig', dt='string')
            cmds.setAttr('CMSettings.CurrentRig', 'None', type = 'string')
            cmds.select(all=True, deselect=True)

    def manage_unselected(self):
        cmds.select(all=True)
        self.exception_objects()
        unselected = cmds.ls(sl=True)
        AllSceneObjects = []
        Selection = []
        def get_base_objects(obj, Input):
            if cmds.nodeType(obj)== "mesh":
                full_path = obj.split("|")
                if len(full_path) >1:
                    del full_path[-1]

                Input.append( "|".join(full_path))
            else:
                Children = cmds.listRelatives(obj, f =True)
                if Children is not None:
                    for c in Children:
                        if c is not None:
                            get_base_objects(c, Input)

        for s in unselected:
            get_base_objects(s, AllSceneObjects)
        for s in self.cursel:
            get_base_objects(s, Selection)

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

    def selected_objects_grouped(self):
        obj_parents = []
        current_parent = None
        same_parent_flag = False
        fixed_parent = ""
        full_path = ""
        for c in self.cursel:
            if cmds.listRelatives(c, p = True) == None:### Has no parents
                if cmds.nodeType(cmds.listRelatives(c, f = True)) == "mesh": ### is an object
                    self.already_grouped = False
                    return ""
                else:### is a group
                    for i in cmds.listRelatives(c, f = True, ad = True):
                        if cmds.nodeType(i) == "mesh":
                            obj_parents.append(cmds.listRelatives(c, f =True))
                            break
            else:
                obj_parents.append(cmds.listRelatives(c, f =True))
        for p in obj_parents:
            if p is not None:
                fixed_parent = "".join(obj_parents[0])
                fixed_parentList = fixed_parent.split("|")
                fixed_parent = fixed_parentList[1]
                full_path = "".join(p)
                full_pathList = full_path.split("|")
                current_parent = full_pathList[1]
                if (current_parent == fixed_parent):
                    same_parent_flag = True
                else:
                    same_parent_flag = False
        if same_parent_flag == True:
            log.info("Objects are grouped")
            ScenePrep.self.already_grouped = True
            self.group_name = current_parent
            return current_parent
        else:
            self.already_grouped = False
            log.info("Objects are not grouped")
            return ""

    def group_objects(self):
        if not self.already_grouped:
            if not cmds.objExists(self.group_name):
                cmds.group( em=True, name=self.group_name )
            for c in self.cursel:
                if c != self.group_name:
                    try:
                        cmds.parent(c, self.group_name)
                    except:
                        pass

    def exception_objects(self):
        vrayLightNodeTypes = ["VRayLightRectShape","VRayLightSphereShape","VRayLightDomeShape","VRayLightIESShape"]
        # Deselect Vray Lights
        for i in vrayLightNodeTypes:
            if cmds.ls(type = i) != []:
                transformList = cmds.listRelatives(cmds.ls(type = i), parent=True, fullPath=True)
                cmds.select(cmds.ls(type = i), deselect = True)
                cmds.select(transformList, deselect = True)

        # Deselect lights
        if cmds.ls(lights = True) != []:
            transformList = cmds.listRelatives(cmds.ls(lights = True), parent=True, fullPath=True)
            cmds.select(cmds.ls(lights = True), deselect = True)
            cmds.select(transformList, deselect = True)

        if cmds.ls(type = "mentalrayIblShape") != []:
            transformList = cmds.listRelatives(cmds.ls(type = "mentalrayIblShape"), parent=True, fullPath=True)
            cmds.select(cmds.ls(type = "mentalrayIblShape"), deselect = True)
            cmds.select(transformList, deselect = True)

        # Deselect Cameras
        if cmds.ls(cameras = True) != []:
            transformList = cmds.listRelatives(cmds.ls(cameras = True), parent=True, fullPath=True)
            cmds.select(cmds.ls(cameras = True), deselect = True)
            cmds.select(transformList, deselect = True)

        if cmds.objExists(CM_SETTINGS):
            cmds.select(CM_SETTINGS, deselect = True)
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
        if cmds.objExists(self.group_name+"_layer"):
            cmds.select(self.group_name+"_layer", deselect = True)

    def convert_cameras_to_startup(self):
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

    def delete_empty_groups(self):
        for a in cmds.ls():
            if cmds.nodeType(a) == 'transform':
                if cmds.listRelatives(a, c =True) == None:
                    cmds.delete(a)
        log.info('Empty groups deleted')

    def delete_empty_layers(self):
        for a in cmds.ls():
            if cmds.nodeType(a) == 'displayLayer':
                if a == 'defaultLayer':
                    continue
                try:
                    cmds.delete(a)
                except:
                    pass
        log.info('Empty layers deleted')

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

    def create_display_layers(self):
        cmds.select(self.group_name)
        layer_name = self.group_name + '_layer'
        if cmds.objExists(layer_name):
            cmds.delete(layer_name)
        cmds.createDisplayLayer(name = layer_name , nr = False)
        log.info('Primary display Layer Created')

        cmds.select(cmds.listRelatives(cmds.ls(cameras = True, lights = True),parent = True))
        try:
            cmds.select('UserLights', add = True)
        except:
            pass
        try:
            cmds.select('CMLightRig', add = True)
        except:
            pass
        layer_name = 'CM_Lights_and_Cameras'
        if cmds.objExists(layer_name):
            cmds.delete(layer_name)
        cmds.createDisplayLayer(name = layer_name , nr = False)
        log.info('%s layer created' % layer_name)

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

    def CreateAnimation(self):
        # Get the up axis
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

    def set_res_gate(self):
        """
        Set the resolution gate in all viewports
        """
        for i in range(1, 5):
            camera = cmds.modelEditor('modelPanel' + str(i), q=True, camera=True)
            cmds.camera(camera, edit=True, displayFilmGate=False, displayResolution=True, overscan=1.3)
            cmds.camera(camera, edit=True, filmFit='fill', displayGateMask=False)

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

    def create_project_directory(self):

        # While the user doesn't create a unique and valid project keep prompting him to do so
        while True:
            # Select the output directory
            self.output_dir = ''
            try:
                self.output_dir = cmds.fileDialog2(fm = 3, fileFilter = None, ds = 2, cap = "Please select a CM project directory")[0]
            except:
                print "No directory specified"
                #If no output directory is specified delete everything and exit
                self.Exit()
                sys.exit()
