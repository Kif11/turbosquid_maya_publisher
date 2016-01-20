import maya.cmds as cmds

import functools
import ScreenCapture
import os

class SubdivisionTextClass:
    
    subColor = "b"
    subBox = ""
    ImagePath = ""
    Camera = ""
    
    @staticmethod
    def UpdateSubSnap():
        perspPanel = cmds.getPanel( withLabel='Persp View')
        
        oldCamera = cmds.modelPanel( perspPanel, query = True, camera = True)

        def ChangeCamera():
            
            cmds.modelPanel( perspPanel, edit = True, camera = "persp")
            SubdivisionTextClass.Camera = "persp" 
            
            #change the view to the camera
            i = 0
            while cmds.objExists("shot_" + str(i)):
                if cmds.getAttr("shot_" + str(i) + ".CMSignature"):
                    SubdivisionTextClass.Camera = "shot_" + str(i) 
                    cmds.modelPanel( perspPanel, edit = True, camera = "shot_" + str(i))
                i = i + 1
        
        def CreateSnap():
            #Create a snapshot from the signature image                
            SubdivisionTextClass.ImagePath = cmds.getAttr("CMSettings.ProjectPath") + "/temp/" + cmds.getAttr("CMSettings.ModelName") + "_Subdivision_Temp_0" + ".png"
            
            cmds.editRenderLayerGlobals( currentRenderLayer = "Subdivision_0")
            ScreenCapture.ScreenCapture(SubdivisionTextClass.ImagePath, [740,400])
            cmds.editRenderLayerGlobals( currentRenderLayer = "defaultRenderLayer")
            
            #Return the camera to whatever it was
            cmds.modelPanel( perspPanel, edit = True, camera = oldCamera)
        
        ChangeCamera()
        
        CreateSnap()
        
        if cmds.picture("BasePicture", query = True, exists = True):
            cmds.picture( "BasePicture", edit = True, image = SubdivisionTextClass.ImagePath )
            
    @staticmethod
    def modifySubdivisions(*args):
        if cmds.objExists("CMForegroundPlane"):
            if cmds.window("SubdivisionsTextWindow", query = True, exists = True):
                cmds.deleteUI("SubdivisionsTextWindow")
            
            SubdivisionTextClass.UpdateSubSnap()
    
            if os.path.exists(SubdivisionTextClass.ImagePath):
                
                cmds.window( "SubdivisionsTextWindow", title = "Subdivisions Text" )
                cmds.formLayout("SubWriterLayout", numberOfDivisions=100, w = 740, h = 400)
                cmds.picture( "BasePicture", image = SubdivisionTextClass.ImagePath )
                
                cmds.editRenderLayerGlobals( currentRenderLayer = "Subdivision_0")
                SubdivisionTextClass.subColor = cmds.getAttr("CMForegroundPlane.imageName")[-5]
                cmds.editRenderLayerGlobals( currentRenderLayer = "defaultRenderLayer")
                
                
                cmds.window( "SubdivisionsTextWindow", edit = True, w = 740, h = 400)
                
                #Create popupMenu for images 
                cmds.popupMenu( "SubdivisionPopUp", parent = "BasePicture" )
                cmds.menuItem( label='TopLeft'    , p = "SubdivisionPopUp", c = functools.partial(SubdivisionTextClass.ChangePos,  "lt") )  
                cmds.menuItem( label='TopRight'   , p = "SubdivisionPopUp", c = functools.partial(SubdivisionTextClass.ChangePos,  "rt") ) 
                cmds.menuItem( label='BottomLeft' , p = "SubdivisionPopUp", c = functools.partial(SubdivisionTextClass.ChangePos,  "lb") ) 
                cmds.menuItem( label='BottomRight', p = "SubdivisionPopUp", c = functools.partial(SubdivisionTextClass.ChangePos,  "rb") )
                cmds.menuItem( label='ToggleColor', p = "SubdivisionPopUp", c = SubdivisionTextClass.toggleSubdivisionColour )
                cmds.showWindow("SubdivisionsTextWindow")
        else:
            cmds.confirmDialog(m = "The signature camera must be created before running this tool")
            
    @staticmethod
    def ChangePos(clo, *args):
        if clo[0] == "r":
            cmds.setAttr("CMForegroundPlane.offsetX", 0.485)
        elif clo[0] == "l":
            cmds.setAttr("CMForegroundPlane.offsetX", -0.485)
        if clo[1] == "t":
            cmds.setAttr("CMForegroundPlane.offsetY", 0.352)
        elif clo[1] == "b":
            cmds.setAttr("CMForegroundPlane.offsetY", -0.352)
        
        SubdivisionTextClass.UpdateSubSnap()
               
    @staticmethod
    def toggleSubdivisionColour(*args):
        if SubdivisionTextClass.subColor == "b":
            SubdivisionTextClass.subColor = "w"
        else:
            SubdivisionTextClass.subColor = "b"
            
        ##Layer management##
        subLayers = ["Subdivision_0", "Subdivision_1"]
        for i in range(0,len(subLayers)):
            cmds.editRenderLayerGlobals( currentRenderLayer = subLayers[i])
            if SubdivisionTextClass.subColor == "w":
                cmds.setAttr("CMForegroundPlane.imageName", os.path.expanduser('~/maya/Turbosquid/CheckMate Tools For Maya/CM_Tools/') + "Imaging/Txt_-_Subdivision_Lv_" + str(i) + "-w.png", type = "string")
            else:
                cmds.setAttr("CMForegroundPlane.imageName", os.path.expanduser('~/maya/Turbosquid/CheckMate Tools For Maya/CM_Tools/') + "Imaging/Txt_-_Subdivision_Lv_" + str(i) + "-b.png", type = "string")
                
                
        cmds.editRenderLayerGlobals( currentRenderLayer = "defaultRenderLayer" )
        
        SubdivisionTextClass.UpdateSubSnap()