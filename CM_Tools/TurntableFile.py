import maya.cmds as cmds

import os

import ScreenCapture

import RenderLayerManagerFile

class TurntableClass:
    
    Turntables = []
    
    def __init__(self, Index):
        self.Snap   = cmds.getAttr("CMSettings.ProjectPath") + "/temp/" + "CM_Turntable_Preview_" + str(Index) + ".jpg"
        
        self.RenderLayer = "Turntable" + str(Index)
        self.Camera = "Turntable_" + str(Index)
        self.Image  = "CM_TT_Image_Control_" + str(Index)
        self.Separator = "TTSep" +  str(Index)
        self.PopUp = "TTPopUp" + str( Index )
        self.LabelText = "TTLabelText" + str(Index)
        self.RangeText = "TTRangeText" + str(Index)
        self.RangeLayout = "TTRangeLayout" + str(Index)
        self.MinField = "TTMinField" + str(Index)
        self.MaxField = "TTMaxField" + str(Index)
        self.Switch = "TTSwitch" + str(Index)
        self.CurrentIndex = Index
    
    @staticmethod
    def DeleteAllSnapshots(*args):
        check = cmds.confirmDialog( title='Turntable reset', message='Are you sure you want to delete all turntables?', button=['Delete','Cancel'], defaultButton='Delete', cancelButton='Cancel', dismissString='Cancel' )    
        if check == "Delete":
            for i in range(len(TurntableClass.Turntables)):
                TurntableClass.Turntables[0].deleteTurntable()
    
    @staticmethod
    def CreateTurntable(createCamera = True, *args):
        
        cmds.undoInfo(openChunk = True)
        
        Index = len( TurntableClass.Turntables )
        
        TurntableClass.Turntables.append( TurntableClass( Index ))
        
        if createCamera:
            TurntableClass.Turntables[Index].CreateCamera()
        
        #Create render layer adjustments
        RenderLayerManagerFile.RenderLayerManagerClass.assignTurntable(TurntableClass.Turntables[Index].Camera)
        
        TurntableClass.Turntables[Index].CreateUI()
        
        #Hide all the cameras
        for i in cmds.ls(cameras = True):
            try:
                cmds.setAttr(i + ".visibility", False)
            except:pass
        
        TurntableClass.UpdateDisplayLayer()
        
        cmds.undoInfo(closeChunk = True)
    
    
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
    def GetActiveCamera():
        #Get the persp panel
        perspPanel = cmds.getPanel( withLabel='Persp View')
        
        #Get the active camera in the panel
        ActiveCamera = cmds.modelPanel( perspPanel, query = True, camera = True)
        
        return ActiveCamera
    
    @staticmethod
    def SetActiveCamera(Camera):
        #Get the persp panel
        perspPanel = cmds.getPanel( withLabel='Persp View')
        
        #Get the active camera in the panel
        cmds.modelPanel( perspPanel, edit = True, camera = Camera)
    
    @staticmethod
    def RecreateUI():
            
        #Delete the entire layout
        cmds.deleteUI("TurnTableLayout")
         
        #Start over
        cmds.columnLayout( "TurnTableLayout", p = "TurnTableScrollLayout", adjustableColumn = True )
         
        #Create the separator
        cmds.separator("BufferTT", h = 600, p = "TurnTableLayout", style = "none")
         
        #Clear turntable list
        TurntableClass.Turntables = []
         
        #Create new snaps
        i = 0
        while(cmds.objExists("Turntable_" + str(i))):
            TurntableClass.Turntables.append( TurntableClass( i ))
            TurntableClass.Turntables[i].CreateUI()
            i = i + 1
         
        #Adjust the counter
        if len(TurntableClass.Turntables) > 0:
            cmds.text("TurntableCounter", edit = True, label = "Turntable Count = " + str(len(TurntableClass.Turntables)), bgc = [0, 0.361, 0])
        else:
            cmds.text("TurntableCounter", edit = True, label = "Turntable Count = " + str(len(TurntableClass.Turntables)) + ", Min required is 1", bgc = [0.361, 0, 0])
         
        #Update the buffer separator
        if len(TurntableClass.Turntables) == 0:
            cmds.separator("BufferTT", edit = True, h = 600)
        elif len(TurntableClass.Turntables) == 1:
            cmds.separator("BufferTT", edit = True, h = 400)
        elif len(TurntableClass.Turntables) == 2:
            cmds.separator("BufferTT", edit = True, h = 200)
        else:
            cmds.separator("BufferTT", edit = True, h = 10)
    
    def CreateCamera(self):
        print "Creating camera"
        
        #Array to store all objects in the scene
        cmds.select(None)
        
        #Copy from the current active camera
        cmds.duplicate( self.GetActiveCamera(), name = self.Camera)
        try:cmds.delete(self.Camera + "|CMForegroundPlane")
        except:pass
        try:cmds.delete(self.Camera + "|CMBackgroundPlane")
        except:pass
        i = 0
        while(cmds.objExists("shot_" + str(i))):
            try:cmds.delete(self.Camera + "|" + "shot_" + str(i) + "_ImagePlane")
            except:pass
            i = i + 1
        
        
        #Make the camera startup so that the user may not delete it directly
        #Enable the resolution gate
        cmds.camera(self.Camera, edit = True, startupCamera = True, displayResolution = True)
        
        #Make the camera hidden
        cmds.setAttr(self.Camera + ".visibility", False)
        
        #Add the attributes to define range and renderability
        cmds.select(self.Camera)
        cmds.addAttr(longName = 'CMRenderable', attributeType = 'bool', defaultValue = True)
        cmds.addAttr(longName = 'StartRange', attributeType = 'short', defaultValue = 0, min = 0, max = 35)
        cmds.addAttr(longName = 'StopRange' , attributeType = 'short', defaultValue = 35, min = 0, max = 35)
        cmds.select(None)
         
    def CreateUI(self):      

        #Deletes the buffer separator
        try:cmds.deleteUI("BufferTT")
        except:pass
        
        #Create Previews
        if not os.path.exists(self.Snap):
            ScreenCapture.ScreenCapture( self.Snap, [309,160]) 
        
        #Create a TextLabel for the turntable
        cmds.text(self.LabelText, p = "TurnTableLayout", label = "Turntable " + str( self.CurrentIndex ), bgc = [0.361, 0.361, 0.361] , w = 309, h = 20, font = "boldLabelFont")
            
        #Create preview image on window
        cmds.image(self.Image, image = self.Snap, p = "TurnTableLayout")
        cmds.button(self.Switch, c = self.SwitchTT, bgc = [0.361, 0.361, 0.361], label = "Included in next rendering", p = "TurnTableLayout")
        cmds.text(self.RangeText, w = 309, p = "TurnTableLayout", label = "From frame                                   To frame    ")
        cmds.rowLayout( self.RangeLayout, w = 309, numberOfColumns = 2, p = "TurnTableLayout")
        cmds.intField( self.MinField, w = 154, min = 0, max = 35, v = cmds.getAttr(self.Camera + ".StartRange") , p = self.RangeLayout, cc = self.Range )
        cmds.intField( self.MaxField, w = 154, min = 0, max = 35, v = cmds.getAttr(self.Camera + ".StopRange"), p = self.RangeLayout, cc = self.Range)
        
        cmds.separator( self.Separator, w = 309, h = 10, p = "TurnTableLayout")
        
        #Create popupMenu for images     
        cmds.popupMenu( self.PopUp, parent = self.Image )
        cmds.menuItem( label = 'Edit Current Camera', p = self.PopUp, c = self.ChangePersp )
        cmds.menuItem( label = 'Delete Camera' , p = self.PopUp, c = self.deleteTurntable )
        cmds.menuItem( label='Copy Camera Information', p = self.PopUp, c = self.CopyCameraInfo )
        cmds.menuItem( divider = True, p = self.PopUp)
        cmds.menuItem( divider = True, p = self.PopUp)
        cmds.menuItem( label='Delete all turntables', p = self.PopUp, c = TurntableClass.DeleteAllSnapshots )
        
        #Update the counter
        if len(TurntableClass.Turntables) > 0:
            cmds.text("TurntableCounter", edit = True, label = "Turntable Count = " + str(len(TurntableClass.Turntables)), bgc = [0, 0.361, 0])
        else:
            cmds.text("TurntableCounter", edit = True, label = "Turntable Count = " + str(len(TurntableClass.Turntables)) + ", Min required is 1", bgc = [0.361, 0, 0])
        
        #Update the buffer separator
        if len(TurntableClass.Turntables) == 1:
            cmds.separator("BufferTT", h = 400, p = "TurnTableLayout", style = "none")
        elif len(TurntableClass.Turntables) == 2:
            cmds.separator("BufferTT", h = 200, p = "TurnTableLayout", style = "none")
        else:
            cmds.separator("BufferTT", h = 10 , p = "TurnTableLayout", style = "none")
        
    def Update(self, NewIndex):
        if NewIndex != self.CurrentIndex : 
            #Rename camera
            cmds.camera(self.Camera, edit = True, startupCamera = False)     
            
            cmds.rename( self.Camera, "Turntable_" + str( NewIndex ) )
            self.Camera = "Turntable_" + str( NewIndex ) 
            
            cmds.camera(self.Camera, edit = True, startupCamera = True)
            
            #Rename render layer
            cmds.rename( self.RenderLayer, "Turntable" + str(NewIndex))
            self.RenderLayer = "Turntable" + str(NewIndex)
            
            #Rename associated preview file
            os.rename( self.Snap, cmds.getAttr("CMSettings.ProjectPath") + "/temp/" + "CM_Turntable_Preview_" + str(NewIndex) + ".jpg" )
            
            self.CurrentIndex = NewIndex
     
    def deleteTurntable( self, *args ): 
        
        import threading
        import maya.utils as utils
        
        cmds.undoInfo(openChunk = True)
        
        #Call the destroy function from the turntable class to remove the class objects
        TurntableClass.Turntables.pop( self.CurrentIndex ).destroy()
            
        #Update all names 
        for i in range( self.CurrentIndex, len( TurntableClass.Turntables )):
            TurntableClass.Turntables[i].Update( i )
        
        #Wait for the function to complete otherwise a memory error will crash maya
        threading.Thread(utils.executeDeferred(TurntableClass.RecreateUI)).start()
        
        cmds.undoInfo(closeChunk = True)
        
    def destroy(self):
        try:cmds.camera(self.Camera, edit = True, startupCamera = False)
        except:pass
        
        #change the view to the camera
        if TurntableClass.GetActiveCamera() == self.Camera:
            TurntableClass.SetActiveCamera("persp")
        
        try:cmds.delete(self.Camera)
        except:pass
        
        print self.RenderLayer
        cmds.editRenderLayerGlobals( currentRenderLayer = "defaultRenderLayer")
        try:cmds.delete(self.RenderLayer)
        except:print "Couldn't delete render layer"
        
        #Delete associated Image File
        try:
            os.remove(self.Snap)
        except:
            print "Could not remove preview Image"     
    
    def RefreshImage( self ):
        cmds.undoInfo(openChunk = True)
        cmds.hudButton("SnapButton", edit = True, label = "Create Turntable", rc = TurntableClass.CreateTurntable)
        #If the active cam is not the current cam exit the function
        if self.GetActiveCamera() != self.Camera + "Shape":
            return 0
        
        #remove the old image
        os.remove( self.Snap) 
 
        #Create new Preview
        ScreenCapture.ScreenCapture( self.Snap, [309,160] ) 

        #Create preview image on window
        cmds.image( self.Image, edit = True, image = self.Snap )
        
        TurntableClass.SetActiveCamera("persp")
        cmds.undoInfo(closeChunk = True)
            
    def ChangePersp(self, *args):
        cmds.undoInfo(openChunk = True)    
        
        TurntableClass.SetActiveCamera(self.Camera)

        cmds.hudButton("SnapButton", edit = True , label = "Update Image", rc = self.RefreshImage)
        
        cmds.undoInfo(closeChunk = True)
        
    def SwitchTT(self, *args):
        cmds.undoInfo(openChunk = True)
        
        lastState = cmds.getAttr(self.Camera +".CMRenderable")
        if lastState: Label = "Excluded from rendering" 
        else: Label = "Included in rendering"
        
        cmds.setAttr(self.Camera +".CMRenderable", not lastState)
        cmds.button( self.Switch, edit = True, bgc = [0.361 + 0.639*lastState , 0.361 - 0.361*lastState , 0.361 - 0.361*lastState], label = Label )
        cmds.text(self.RangeText, edit = True, vis = not lastState)
        cmds.rowLayout( self.RangeLayout, edit = True, vis = not lastState)
        
        #Change the renderability in the render layer
        RenderLayerManagerFile.RenderLayerManagerClass.EditLayer([[self.Camera + ".renderable","none",not lastState]], [self.RenderLayer])
        
        cmds.undoInfo(closeChunk = True)
        
    def Range(self, *args):
        cmds.undoInfo(openChunk = True)
        #Get the value
        minVal = cmds.intField(self.MinField, query = True, v = True)
        maxVal = cmds.intField(self.MaxField, query = True, v = True)
                
        #To keep them from overlapping
        if minVal > maxVal :
            minVal = maxVal
        
        #Assign the new value for the minVal
        cmds.intField(self.MinField, edit = True, v = minVal)
        
        cmds.setAttr(self.Camera + ".StartRange", minVal)
        cmds.setAttr(self.Camera + ".StopRange", maxVal)
        
        cmds.editRenderLayerGlobals( currentRenderLayer = self.RenderLayer)
        cmds.setAttr("defaultRenderGlobals.startFrame", minVal)
        cmds.setAttr("defaultRenderGlobals.endFrame", maxVal)
        cmds.editRenderLayerGlobals( currentRenderLayer = "defaultRenderLayer")
        
        cmds.undoInfo(closeChunk = True)
        
    def CopyCameraInfo(self, *args):
        cmds.undoInfo(openChunk = True)
        try:
            print self.Camera + ".transform"
            print cmds.getAttr(self.Camera + ".translate")
            cmds.setAttr( "persp.translateX" , cmds.getAttr(self.Camera + ".translateX"))
            cmds.setAttr( "persp.rotateX" , cmds.getAttr(self.Camera + ".rotateX"))
            cmds.setAttr( "persp.translateY" , cmds.getAttr(self.Camera + ".translateY"))
            cmds.setAttr( "persp.rotateY" , cmds.getAttr(self.Camera + ".rotateY"))
            cmds.setAttr( "persp.translateZ" , cmds.getAttr(self.Camera + ".translateZ"))
            cmds.setAttr( "persp.rotateZ" , cmds.getAttr(self.Camera + ".rotateZ"))
        except:
            print "Could not copy information to persp camera"
        cmds.undoInfo(closeChunk = True)