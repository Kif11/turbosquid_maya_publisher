import maya.cmds as cmds
import maya.mel as mel

import os

import ScreenCapture
import RenderLayerManagerFile

reload(ScreenCapture)

class SnapShotClass:
    SnapShots = []

    #Helper functions
    @staticmethod
    def GetActiveCamera():
        print "Retrieving the active camera"
        #Get the persp panel
        perspPanel = cmds.getPanel( withLabel='Persp View')

        #Get the active camera in the panel
        ActiveCamera = cmds.modelPanel( perspPanel, query = True, camera = True)

        print "Active camera: " + ActiveCamera
        return ActiveCamera

    @staticmethod
    def SetActiveCamera(Camera):
        print "Setting the active camera"
        #Get the persp panel
        perspPanel = cmds.getPanel( withLabel='Persp View')

        #Get the active camera in the panel
        cmds.modelPanel( perspPanel, edit = True, camera = Camera)
        print Camera + " is set as the active camera in the perspView"

    @staticmethod
    def GetSignatureSnapShot():
        print "Retrieving the signature camera"
        if SnapShotClass.SnapShots != []:
            for i in SnapShotClass.SnapShots:
                if cmds.getAttr(i.Camera + ".CMSignature"):
                    print i.Camera + " is the signature camera"
                    return i
    #Helper functions end

    @staticmethod
    def DeleteAllSnapshots(*args):
        check = cmds.confirmDialog( title='Snapshot reset', message='Are you sure you want to delete all snapshots?', button=['Delete','Cancel'], defaultButton='Delete', cancelButton='Cancel', dismissString='Cancel' )
        if check == "Delete":
            for i in range(len(SnapShotClass.SnapShots)):
                SnapShotClass.SnapShots[0].deleteSnapShot()


    #Class begin
    def __init__(self, Index, Signature):
        print "Initializing a snapshot with Index: " + str(Index)
        self.Camera = "shot_" + str(Index)
        self.Snap   = cmds.getAttr("CMSettings.ProjectPath") + "/temp/" + "CM_Snap_Preview_" + str(Index) + ".jpg"

        #UI elements
        self.Image  = "CM_Image_Control_" + str(Index)
        self.Separator = "CMSep" +  str(Index)
        self.PopUp = "CMPopUp" + str( Index )
        self.SigButton = "CMSigButton" + str(Index)
        self.LabelText = "CMLabelText" + str(Index)
        self.ImageRowLayout = "CMImageRowLayout" + str(Index)
        self.ImageColLayout = "CMImageColLayout" + str(Index)
        self.SnapSwitch = "CMSnapSwitch" + str(Index)
        self.WireSwitch = "CMWireSwitch" + str(Index)
        self.SwitchLayout = "CMSwitchLayout" + str(Index)

        #Index variable
        self.CurrentIndex = Index
        self.Signature = Signature

    #Control function, calls create camera create UI and initializes objects, it is invoked from the ui button

    @staticmethod
    def CreateSnapshot(createCamera = True, *args):
        print "Creating a snapshot"
        cmds.undoInfo(openChunk = True, infinity = True)#, length = 200)

        RenderLayerManagerFile.RenderLayerManagerClass.ShowModel(Visibility = False)

        #Get the length of the list and use that as the index for the next snap
        Index = len( SnapShotClass.SnapShots )

        cmds.editRenderLayerGlobals(currentRenderLayer = "defaultRenderLayer")

        #Create snapshot variable and append it to the list, if it is the first snap make it the signature
        SnapShotClass.SnapShots.append( SnapShotClass( Index, not len( SnapShotClass.SnapShots ) ))

        #Create the camera object, if it doesn't already exist
        if createCamera:
            try:
                SnapShotClass.SnapShots[Index].CreateCamera()
            except:
                cmds.confirmDialog(m = "Could not create camera in createsnapshot")
                print

        #if it is the first cam update the sqr shot
        if len( SnapShotClass.SnapShots ) == 1:
            try:
                SnapShotClass.SetSqrCamera()
            except:
                cmds.confirmDialog(m = "Failed to set the square camera in createsnapshot")

        RenderLayerManagerFile.RenderLayerManagerClass.ShowModel(Visibility = True)

        try:
            RenderLayerManagerFile.RenderLayerManagerClass.ManageUserRig()
        except:
            cmds.confirmDialog(m = "Failed to set the user rigs in createsnapshot")

        #Create the UI for the snap
        SnapShotClass.SnapShots[Index].CreateUI()

        #Hide all the cameras
        for i in cmds.ls(cameras = True):
            try:
                cmds.setAttr(i + ".visibility", False)
            except:pass

        SnapShotClass.UpdateDisplayLayer()

        cmds.undoInfo(closeChunk = True)
        print "Snapshot created successfully"

    def CreateCamera(self):
        print "Creating new camera"
        #Create Camera
        cmds.select(None)

        #Copy from the current active camera
        cmds.duplicate( self.GetActiveCamera(), name = self.Camera)
        try:cmds.delete(self.Camera + "|CMForegroundPlane")
        except:pass
        try:cmds.delete(self.Camera + "|CMBackgroundPlane")
        except:pass
        for i in SnapShotClass.SnapShots:
            try:cmds.delete(self.Camera + "|" + i.Camera + "_ImagePlane")
            except:pass

        #Make the camera startup so that the user may not delete it directly
        #Enable the resolution gate
        cmds.camera(self.Camera, edit = True, startupCamera = True, displayResolution = True)

        #Make the camera hidden
        cmds.setAttr(self.Camera + ".visibility", False)

        #Add render attributes
        try:
            cmds.select(self.Camera)
            cmds.addAttr(longName='CMRenderProductShot', attributeType='bool', defaultValue = True)
            cmds.addAttr(longName='CMRenderWireFrame', attributeType='bool', defaultValue = True)
            cmds.addAttr(longName='CMSignature', attributeType='bool', defaultValue = self.Signature)
            cmds.select(None)
        except:
            pass

        #Default values
        cmds.setAttr(self.Camera + '.CMRenderProductShot', True)
        cmds.setAttr(self.Camera + '.CMRenderWireFrame', True)
        cmds.setAttr(self.Camera + '.CMSignature', self.Signature)

        #Assign the foreground plane to this camera if it is the signature camera
        if self.Signature:
            SnapShotClass.UpdateImagePlane("CMForegroundPlane", self.Camera)


        #Create the background plane for the camera
        CopyPlane = cmds.duplicate("CMBackgroundPlane")
        CopyPlane = cmds.rename(CopyPlane, self.Camera + "_ImagePlane")
        SnapShotClass.UpdateImagePlane(CopyPlane, self.Camera, False)
        cmds.setAttr(CopyPlane  +".sizeX", 50)
        cmds.setAttr(CopyPlane  +".sizeY", 50)

        #Adjust render layer adjustments
        RenderLayerManagerFile.RenderLayerManagerClass.assignSnapShots(self.Camera)
        print "Camera created"

    def CreateUI(self):
        print "Creating snap UI"
        if cmds.image(self.Image, query = True, exists = True):
            return 0

        #Deletes the buffer separator
        try:cmds.deleteUI("BufferSS")
        except:pass

        #Create Preview
        if not os.path.exists(self.Snap):
            ReturnCamera = SnapShotClass.GetActiveCamera()
            SnapShotClass.SetActiveCamera(self.Camera)
            ScreenCapture.ScreenCapture(self.Snap, [296,160])
            SnapShotClass.SetActiveCamera(ReturnCamera)

        #Create a layout for the image and it's controls
        cmds.rowLayout(self.ImageRowLayout, p = "SnapShotLayout", numberOfColumns = 2)
        cmds.button(self.SigButton, p = self.ImageRowLayout, bgc = [0.361 + 0.639 * self.Signature,
                                                                 0.361 + 0.639 * self.Signature,
                                                                 0.361 - 0.361 * self.Signature],
                    label = "", w = 10, h = 180, c = self.MarkSignature )

        #Holds the label and the image
        cmds.columnLayout(self.ImageColLayout, p = self.ImageRowLayout)

        #The label of the image
        if not self.Signature:
            cmds.text(self.LabelText, p = self.ImageColLayout,bgc = [0.361, 0.361, 0.361], label = "Image " + str(self.CurrentIndex), w = 296, h = 20, font = "boldLabelFont")
        else:
            cmds.text(self.LabelText, p = self.ImageColLayout,bgc = [0.361, 0.361, 0.361], label = "Signature", w = 296, h = 20, font = "boldLabelFont")

        #Create preview image on window
        cmds.image(self.Image, image = self.Snap, p = self.ImageColLayout, w = 296)

        #Layout for the switch buttons
        cmds.rowLayout(self.SwitchLayout, p = "SnapShotLayout", numberOfColumns = 2)

        #Button to switch snap on/off in the render
        if cmds.getAttr(self.Camera + ".CMRenderProductShot"):
            cmds.button(self.SnapSwitch, c = self.SnapSwitchFunc, bgc = [0.361, 0.361, 0.361], label = "Render Shot", p = self.SwitchLayout, w = 154)
        else:
            cmds.button(self.SnapSwitch, c = self.SnapSwitchFunc, bgc = [1, 0, 0], label = "Exclude Shot", p = self.SwitchLayout, w = 154)

        #Button to switch wire on/off in the render
        if cmds.getAttr(self.Camera + ".CMRenderWireFrame"):
            cmds.button(self.WireSwitch, c = self.WireSwitchFunc, bgc = [0.361, 0.361, 0.361], label = "Render Wire", p = self.SwitchLayout, w = 154)
        else:
            cmds.button(self.WireSwitch, c = self.WireSwitchFunc, bgc = [1, 0, 0], label = "Exclude Wire", p = self.SwitchLayout, w = 154)


        #Seperator between image previews
        cmds.separator( self.Separator, w = 296, h = 10, p = "SnapShotLayout")

        #Create popupMenu for images
        cmds.popupMenu( self.PopUp, parent = self.Image )
        cmds.menuItem( label='Edit Current Camera', p = self.PopUp, c = self.ChangePersp )
        cmds.menuItem( label='Delete Camera' , p = self.PopUp, c = self.deleteSnapShot )
        cmds.menuItem( label='Make Signature', p = self.PopUp, c = self.MarkSignature )
        cmds.menuItem( label='Copy Camera Information', p = self.PopUp, c = self.CopyCameraInfo )
        cmds.menuItem( divider = True, p = self.PopUp)
        cmds.menuItem( divider = True, p = self.PopUp)
        cmds.menuItem( label='Delete all snapshots', p = self.PopUp, c = SnapShotClass.DeleteAllSnapshots )


        if len(SnapShotClass.SnapShots) > 5:
            cmds.text("SnapCounter", edit = True, label = "Image Count = " + str(len(SnapShotClass.SnapShots)), bgc = [0, 0.361, 0])
        else:
            cmds.text("SnapCounter", edit = True, label = "Image Count = " + str(len(SnapShotClass.SnapShots)) + ", Min required are 6", bgc = [0.361, 0, 0])

        if len(SnapShotClass.SnapShots) == 1:
            cmds.separator("BufferSS", h = 400, style = "none", p = "SnapShotLayout")
        elif len(SnapShotClass.SnapShots) == 2:
            cmds.separator("BufferSS", h = 200, style = "none", p = "SnapShotLayout")
        else:
            cmds.separator("BufferSS", h = 10, style = "none", p = "SnapShotLayout")
        print "Snap UI created"

    def deleteSnapShot( self, *args ):
        print "Deleting snapshot"
        import threading
        import maya.utils as utils

        cmds.undoInfo(openChunk = True)

        try:
            RenderLayerManagerFile.RenderLayerManagerClass.ShowModel(Visibility = False)

            SnapShotClass.UpdateImagePlane("CMForegroundPlane", "persp")

            #Call the destroy function from the snapshot class to remove the class objects
            SnapShotClass.SnapShots.pop( self.CurrentIndex ).destroy()

            #Update all names
            for i in range( self.CurrentIndex, len( SnapShotClass.SnapShots )):
                SnapShotClass.SnapShots[i].UpdateIndex( i )

            #Check to see if there is a signature image in the current list
            SignatureFound = False
            for i in SnapShotClass.SnapShots:
                if cmds.getAttr(i.Camera +'.CMSignature'):
                    SignatureFound = True
                    SnapShotClass.UpdateImagePlane("CMForegroundPlane", i.Camera)

            #If not make the first image the signature
            if not SignatureFound and cmds.objExists("shot_0"):
                cmds.setAttr('shot_0.CMSignature', True)
                SnapShotClass.UpdateImagePlane("CMForegroundPlane", "shot_0")
                #Adjust render layer adjustments
                RenderLayerManagerFile.RenderLayerManagerClass.assignSnapShots("shot_0")



            #Wait for the function to complete otherwise a memory error will crash maya
            threading.Thread(target=utils.executeDeferred(SnapShotClass.RecreateUI)).start()

            RenderLayerManagerFile.RenderLayerManagerClass.ShowModel(Visibility = True)
        except:
            raise

        finally:
            cmds.undoInfo(closeChunk = True)
        print "Snapshot deleted"

    def destroy(self):
        print "Snapshot destroy begin"
        try:cmds.camera(self.Camera, edit = True, startupCamera = False)
        except:pass

        #change the view to the camera
        if SnapShotClass.GetActiveCamera() == self.Camera:
            SnapShotClass.SetActiveCamera("persp")

        try:
            cmds.delete(self.Camera)
        except:
            print "Could not remove camera"

        #Delete associated Image File
        try:
            os.remove(self.Snap)
        except:
            print "Could not remove preview Image"
        print "Snapshot destroy end"

    def UpdateIndex(self, NewIndex):
        print "Updating snap index"
        if NewIndex != self.CurrentIndex :
            cmds.camera(self.Camera, edit = True, startupCamera = False)
            cmds.rename( self.Camera, "shot_" + str( NewIndex ) )
            cmds.rename( self.Camera + "_ImagePlane", "shot_" + str( NewIndex ) + "_ImagePlane" )
            self.Camera = "shot_" + str( NewIndex )
            cmds.camera(self.Camera, edit = True, startupCamera = True)

            try:
                os.rename(self.Snap, cmds.getAttr("CMSettings.ProjectPath") + "/temp/" + "CM_Snap_Preview_" + str(NewIndex) + ".jpg")
                self.Snap = cmds.getAttr("CMSettings.ProjectPath") + "/temp/" + "CM_Snap_Preview_" + str(NewIndex) + ".jpg"
            except:
                pass

            self.CurrentIndex = NewIndex
        print "Updated snap index"

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

    def MarkSignature(self, *args):
        print "Marking signature"
        cmds.undoInfo(openChunk = True)

        #Remove previous signature
        for i in range(0, len(SnapShotClass.SnapShots)):
            if cmds.getAttr(SnapShotClass.SnapShots[i].Camera+'.CMSignature'):
                cmds.setAttr(SnapShotClass.SnapShots[i].Camera+'.CMSignature', False)
                RenderLayerManagerFile.RenderLayerManagerClass.assignSnapShots(SnapShotClass.SnapShots[i].Camera)
                cmds.text( SnapShotClass.SnapShots[i].LabelText, edit = True, label = "Image " + str( SnapShotClass.SnapShots[i].CurrentIndex ),bgc = [0.361, 0.361, 0.361] )
                cmds.button( SnapShotClass.SnapShots[i].SigButton, edit = True, bgc = [0.361, 0.361, 0.361] )

        #Assign new signature
        for i in range(0, len(SnapShotClass.SnapShots)):
            if i == self.CurrentIndex:
                cmds.setAttr(self.Camera+'.CMSignature', True)
                cmds.text( self.LabelText, edit = True, label = "Signature", bgc = [0.361, 0.361, 0.361])
                cmds.button( self.SigButton, edit = True, bgc = [1, 1, 0] )
                SnapShotClass.UpdateImagePlane("CMForegroundPlane", self.Camera)
                RenderLayerManagerFile.RenderLayerManagerClass.assignSnapShots(self.Camera)

                self.SetSqrCamera()

        cmds.undoInfo(closeChunk = True)
        print "Marked signature"

    def SnapSwitchFunc(self, *args):
        print "Switching snapshot"
        cmds.undoInfo(openChunk = True)

        if cmds.getAttr(self.Camera+'.CMRenderProductShot'):
            cmds.button( self.SnapSwitch, edit = True, bgc = [1 , 0 , 0], label = "Exclude Shot" )
            cmds.setAttr( self.Camera + ".CMRenderProductShot", False)
            RenderLayerManagerFile.RenderLayerManagerClass.EditLayer(
                                                      settings = [[self.Camera + ".renderable", "RemoveFromLayer", False ]],
                                                      layers = ["Product", "ContextSig"])
        else:
            cmds.button( self.SnapSwitch, edit = True, bgc = [0.361, 0.361, 0.361], label = "Render Shot" )
            cmds.setAttr( self.Camera + ".CMRenderProductShot", True)
            RenderLayerManagerFile.RenderLayerManagerClass.assignSnapShots(self.Camera)

        cmds.undoInfo(closeChunk = True)
        print "Switched snapshot"

    def WireSwitchFunc(self, *args):
        print "Wire switching"
        cmds.undoInfo(openChunk = True)

        if cmds.getAttr(self.Camera+'.CMRenderWireFrame'):
            cmds.button( self.WireSwitch, edit = True, bgc = [1 , 0 , 0], label = "Exclude Wire" )
            cmds.setAttr( self.Camera + ".CMRenderWireFrame", False)
            RenderLayerManagerFile.RenderLayerManagerClass.EditLayer(
                                                      settings = [[self.Camera + ".renderable", "RemoveFromLayer", False ]],
                                                      layers = ["Wireframe", "Subdivision_0", "Subdivision_1"])
        else:
            cmds.button( self.WireSwitch, edit = True, bgc = [0.361, 0.361, 0.361], label = "Render Wire" )
            cmds.setAttr( self.Camera + ".CMRenderWireFrame", True)
            RenderLayerManagerFile.RenderLayerManagerClass.assignSnapShots(self.Camera)

        cmds.undoInfo(closeChunk = True)
        print "Wire switched"

    def CopyCameraInfo(self, *args):
        print "Copying camera info"
        cmds.undoInfo(openChunk = True)
        try:
            cmds.setAttr( "persp.translateX" , cmds.getAttr(self.Camera + ".translateX"))
            cmds.setAttr( "persp.rotateX" , cmds.getAttr(self.Camera + ".rotateX"))
            cmds.setAttr( "persp.translateY" , cmds.getAttr(self.Camera + ".translateY"))
            cmds.setAttr( "persp.rotateY" , cmds.getAttr(self.Camera + ".rotateY"))
            cmds.setAttr( "persp.translateZ" , cmds.getAttr(self.Camera + ".translateZ"))
            cmds.setAttr( "persp.rotateZ" , cmds.getAttr(self.Camera + ".rotateZ"))
        except:
            print "Could not copy information to persp camera"
        cmds.undoInfo(closeChunk = True)
        print "Camera info copied"
    @staticmethod
    def SetSqrCamera():
        import subprocess
        print "Setting square camera"
        cmds.editRenderLayerGlobals(currentRenderLayer = "defaultRenderLayer")

        Snap = SnapShotClass.GetSignatureSnapShot()

        if os.path.exists(os.environ['CM_TOOLS'] + "Imaging/GetObjPixelDimension.exe"):
            program = os.environ['CM_TOOLS'] + "Imaging/GetObjPixelDimension.exe"
        elif os.path.exists(os.environ['CM_TOOLS'] + "Imaging/GetObjPixelDimension"):
            program = os.environ['CM_TOOLS'] + "Imaging/GetObjPixelDimension"
        print "Getpixeldimensions application path:" + program


        oldCamera = SnapShotClass.GetActiveCamera()

        SnapShotClass.SetActiveCamera(Snap.Camera)

        #Hide all objects except the main model
        cmds.hide( allObjects=True )
        cmds.showHidden( cmds.getAttr("CMSettings.ModelName") )

        #Remove the film and resolution gate
        cmds.camera( Snap.Camera, edit = True, displayFilmGate = False, displayResolution = False, overscan = 1.3)
        cmds.camera( Snap.Camera, edit = True, filmFit = "fill", displayGateMask = False)

        #get the screenshot path
        imgp = cmds.getAttr("CMSettings.ProjectPath") + "/temp/SQRImageTest" + ".png"

        #Capture the screen shot
        ScreenCapture.ScreenCapture(imgp, [1480,800], 0)
        print "Screen shot captured"

        #Unhide all
        cmds.showHidden(allObjects = True)
        cmds.hide(cmds.ls(cameras = True))

        #Activate the resolution gate
        cmds.camera( Snap.Camera, edit = True, displayFilmGate = False, displayResolution = True, overscan = 1.3)
        cmds.camera( Snap.Camera, edit = True, filmFit = "fill", displayGateMask = False)

        SnapShotClass.SetActiveCamera(oldCamera)

        #Run the image processor
        size = subprocess.Popen([program, imgp],creationflags=subprocess.SW_HIDE, shell=True, stdout=subprocess.PIPE).communicate()[0]
        w, h = size.split(" ")
        w = int(w)
        h = int(h)

        print "Pixel size calculated to be: w = " + str(w) + ", h = " + str(h)

        fl1 = cmds.getAttr(Snap.Camera + "Shape.focalLength")
        cmds.editRenderLayerGlobals(currentRenderLayer = "SQRSignature")
        for j in SnapShotClass.SnapShots:
            if not cmds.getAttr(j.Camera+'.CMSignature'):
                cmds.editRenderLayerAdjustment(j.Camera + "Shape.focalLength", remove = True)
        cmds.editRenderLayerAdjustment(Snap.Camera + "Shape.focalLength")

        if (w > h):
            cmds.setAttr(Snap.Camera + "Shape.focalLength", fl1*0.6685 )
        elif (h >= w):
            cmds.setAttr(Snap.Camera + "Shape.focalLength", fl1*1.2285 )

        cmds.editRenderLayerGlobals(currentRenderLayer = "defaultRenderLayer")
        print "Square camera set"

    @staticmethod
    def CreateImagePlanes():
        print "Creating image planes"
        try:
            cameraName = SnapShotClass.GetSignatureSnapShot().Camera
        except:
            cameraName = "persp"

        def CreateImagePlane(imagePlaneName, size, offset, depth):
            if cmds.objExists(imagePlaneName) and cmds.listRelatives(imagePlaneName,parent = True) != cameraName:
                try :cmds.delete(imagePlaneName)
                except:pass

            if not cmds.objExists(imagePlaneName):
                temp = cmds.createNode("imagePlane")

                temp = cmds.rename(temp, imagePlaneName+"Shape")
                cmds.rename(cmds.listRelatives(temp, p = True), imagePlaneName)

                cmds.setAttr(imagePlaneName +".translateX", 0)
                cmds.setAttr(imagePlaneName +".translateY", 0)
                cmds.setAttr(imagePlaneName +".translateZ", -1)
                cmds.setAttr(imagePlaneName +".rotateX", 0 )
                cmds.setAttr(imagePlaneName +".rotateY", 0 )
                cmds.setAttr(imagePlaneName +".rotateZ", 0 )
                cmds.setAttr(imagePlaneName +".scaleX", 0 )
                cmds.setAttr(imagePlaneName +".scaleY", 0 )
                cmds.setAttr(imagePlaneName +".scaleZ", 0 )


                imagePlaneName = temp

                mel.eval( 'cameraImagePlaneUpdate "%s" "%s";' % (cameraName + "Shape", imagePlaneName) )
                cmds.parent(imagePlaneName,cameraName)

            cmds.setAttr(imagePlaneName +".sizeX", size[0])
            cmds.setAttr(imagePlaneName +".sizeY", size[1])
            cmds.setAttr(imagePlaneName +".offsetX", offset[0])
            cmds.setAttr(imagePlaneName +".offsetY", offset[1])
            cmds.setAttr(imagePlaneName +".depth", depth )

            return imagePlaneName

        shapeForeground = CreateImagePlane("CMForegroundPlane", size = [0.0, 0.0], offset = [0.480, 0.350], depth = 1)

        cameraName = "persp"
        shapeBackground = CreateImagePlane("CMBackgroundPlane", size = [50, 50], offset = [0, 0], depth = 8000)

        if cmds.getAttr("defaultRenderGlobals.currentRenderer") == "mentalRay":
            try:
                cmds.setAttr( shapeBackground + ".miDeriveFromMaya", 0 )
                cmds.setAttr( shapeBackground + ".miVisible", 1 )
                i = 0
                while(cmds.objExists( "shot_" + str(i) + "_ImagePlane")):
                        try:cmds.setAttr( "shot_" + str(i) + "_ImagePlane" + ".miDeriveFromMaya", 0 )
                        except:pass
                        cmds.setAttr( "shot_" + str(i) + "_ImagePlane" + ".miVisible", 1 )
                        i = i + 1
            except:
                pass

        subLayers = ["Subdivision_0", "Subdivision_1"]
        for i in range(0,len(subLayers)):
            cmds.editRenderLayerGlobals( currentRenderLayer = subLayers[i])
            #Adjustments for the foreground plane
            cmds.editRenderLayerAdjustment( shapeForeground + ".imageName" )
            cmds.setAttr(shapeForeground + ".imageName", os.environ['CM_TOOLS'] + "Imaging/Txt_-_Subdivision_Lv_" + str(i) + "-b.png", type = "string")
            cmds.editRenderLayerAdjustment(shapeForeground + ".sizeX")
            cmds.editRenderLayerAdjustment(shapeForeground + ".sizeY")
            cmds.setAttr(shapeForeground + ".sizeX", 0.435)
            cmds.setAttr(shapeForeground + ".sizeY", 0.035)
            if cmds.getAttr("defaultRenderGlobals.currentRenderer") == "mentalRay":
                try:
                    cmds.editRenderLayerAdjustment(shapeForeground + ".miDeriveFromMaya")
                    cmds.editRenderLayerAdjustment(shapeForeground + ".miVisible")
                    cmds.setAttr( shapeForeground + ".miDeriveFromMaya", 0 )
                    cmds.setAttr( shapeForeground + ".miVisible", 1 )
                except:
                    pass

        wireLayers = ["Subdivision_0", "Subdivision_1", "Wireframe", "UVs"]
        for layer in wireLayers:
            cmds.editRenderLayerGlobals( currentRenderLayer = layer)

            #Adjustments for the background plane
            cmds.editRenderLayerAdjustment( shapeBackground + ".imageName" )
            cmds.setAttr(shapeBackground + ".imageName", os.environ['CM_TOOLS'] + "WireColor" + ".jpg", type = "string")


        sigLayers = ["Signature", "SQRSignature"]
        for layer in sigLayers:
            cmds.editRenderLayerGlobals( currentRenderLayer = layer)

            cmds.editRenderLayerAdjustment( shapeBackground + ".imageName" )
            cmds.setAttr(shapeBackground + ".imageName", os.environ['CM_TOOLS'] + "SignatureColor.jpg", type = "string")

        cmds.editRenderLayerGlobals( currentRenderLayer = "defaultRenderLayer")
        print "Image planes created"

    @staticmethod
    def UpdateImagePlane(imagePlaneName, cameraName, updateSize = True):
        print "Updating image planes"
        def BreakPreviousConnection():
            for i in cmds.ls(cameras = True):
                ConnectedPlanes = cmds.listConnections( i + ".imagePlane" , c = True)
                if ConnectedPlanes != None:
                    for j in range(len(ConnectedPlanes)):
                        if ConnectedPlanes[j] == imagePlaneName:
                            try:
                                cmds.disconnectAttr(imagePlaneName + "Shape.message", ConnectedPlanes[j-1])
                            except:
                                print "Not Connected"
                            return

        BreakPreviousConnection()

        try:
            mel.eval( 'cameraImagePlaneUpdate "%s" "%s";' % (cameraName + "Shape", imagePlaneName + "Shape") )
        except:
            pass

        try:
            cmds.parent(imagePlaneName,cameraName)
        except:
            pass

        cmds.setAttr(imagePlaneName +".translateX", 0)
        cmds.setAttr(imagePlaneName +".translateY", 0)
        cmds.setAttr(imagePlaneName +".translateZ", -1)
        cmds.setAttr(imagePlaneName +".rotateX", 0 )
        cmds.setAttr(imagePlaneName +".rotateY", 0 )
        cmds.setAttr(imagePlaneName +".rotateZ", 0 )
        cmds.setAttr(imagePlaneName +".scaleX", 0 )
        cmds.setAttr(imagePlaneName +".scaleY", 0 )
        cmds.setAttr(imagePlaneName +".scaleZ", 0 )

        if updateSize:
            subLayers = ["Subdivision_0", "Subdivision_1"]
            for i in range(0,len(subLayers)):
                cmds.editRenderLayerGlobals( currentRenderLayer = subLayers[i])
                cmds.editRenderLayerAdjustment(imagePlaneName + ".sizeX")
                cmds.editRenderLayerAdjustment(imagePlaneName + ".sizeY")
                cmds.setAttr(imagePlaneName + ".sizeX", 0.435)
                cmds.setAttr(imagePlaneName + ".sizeY", 0.035)
            cmds.editRenderLayerGlobals( currentRenderLayer = "defaultRenderLayer")
            cmds.setAttr(imagePlaneName + ".sizeX", 0.0)
            cmds.setAttr(imagePlaneName + ".sizeY", 0.0)
        print "Updated imageplanes"

    @staticmethod
    def RecreateUI():
        print "Recreating UI"

        #Delete the entire layout
        cmds.deleteUI("SnapShotLayout")

        #Start over
        cmds.columnLayout( "SnapShotLayout", p = "SnapShotScrollLayout", adjustableColumn = True )

        #Create the separator
        cmds.separator("BufferSS", h = 600, p = "SnapShotLayout", style = "none")

        #Clear snapshot list
        SnapShotClass.SnapShots = []

        #Create new snaps
        i = 0
        while(cmds.objExists("shot_" + str(i))):
            SnapShotClass.SnapShots.append( SnapShotClass( i, cmds.getAttr("shot_" + str(i) + ".CMSignature")))
            SnapShotClass.SnapShots[i].CreateUI()
            i = i + 1

        #Adjust the counter
        if len(SnapShotClass.SnapShots) > 5:
            cmds.text("SnapCounter", edit = True, label = "Image Count = " + str(len(SnapShotClass.SnapShots)), bgc = [0, 0.361, 0])
        else:
            cmds.text("SnapCounter", edit = True, label = "Image Count = " + str(len(SnapShotClass.SnapShots)) + ", Min required are 6", bgc = [0.361, 0, 0])

        #Update the buffer separator
        if len(SnapShotClass.SnapShots) == 0:
            cmds.separator("BufferSS", edit = True, h = 600)
        elif len(SnapShotClass.SnapShots) == 1:
            cmds.separator("BufferSS", edit = True, h = 400)
        elif len(SnapShotClass.SnapShots) == 2:
            cmds.separator("BufferSS", edit = True, h = 200)
        else:
            cmds.separator("BufferSS", edit = True, h = 10)
        print "UI recreated for snapshots"

    @staticmethod
    def UpdatePaths():
        print "Updating paths"
        try:
            Camera = SnapShotClass.GetSignatureSnapShot().Camera
        except:
            Camera = "persp"

        subLayers = ["Subdivision_0", "Subdivision_1"]
        for i in range(0,len(subLayers)):
            cmds.editRenderLayerGlobals( currentRenderLayer = subLayers[i])
            #Adjustments for the foreground plane
            cmds.setAttr(Camera + "|CMForegroundPlane" + ".imageName", os.environ['CM_TOOLS'] + "Imaging/Txt_-_Subdivision_Lv_" + str(i) + "-b.png", type = "string")

        cameraObjects = ["persp|CMBackgroundPlane"]
        i = 0
        while(cmds.objExists("shot_" + str(i) + "|shot_" + str(i) + "_ImagePlane")):
            cameraObjects.append("shot_" + str(i) + "|shot_" + str(i) + "_ImagePlane")
            i = i + 1

        wireLayers = ["Subdivision_0", "Subdivision_1", "Wireframe", "UVs"]
        for layer in wireLayers:
            cmds.editRenderLayerGlobals( currentRenderLayer = layer)
            for i in cameraObjects:
                cmds.setAttr(i + ".imageName", os.environ['CM_TOOLS'] + "WireColor" + ".jpg", type = "string")


        sigLayers = ["Signature", "SQRSignature"]
        for layer in sigLayers:
            cmds.editRenderLayerGlobals( currentRenderLayer = layer)
            for i in cameraObjects:
                cmds.setAttr(i + ".imageName", os.environ['CM_TOOLS'] + "SignatureColor" + ".jpg", type = "string")
        print "Paths updated"

    def RefreshImage( self, *args ):
        print "Refreshing Image"
        cmds.undoInfo(openChunk = True)
        cmds.hudButton("SnapButton", edit = True, label = "Snap Image", rc = SnapShotClass.CreateSnapshot)
        #If the active cam is not the current cam exit the function

        if self.GetActiveCamera() != self.Camera + "Shape":
            return 0

        #remove the old image
        os.remove( self.Snap)

        #Create new Preview
        ScreenCapture.ScreenCapture( self.Snap, [296,160] )

        #Create preview image on window
        cmds.image( self.Image, edit = True, image = self.Snap )

        if cmds.getAttr(self.Camera + ".CMSignature"):
            self.SetSqrCamera()

        SnapShotClass.SetActiveCamera("persp")
        cmds.undoInfo(closeChunk = True)
        print "Image refreshed"

    def ChangePersp(self, *args):
        cmds.undoInfo(openChunk = True)

        SnapShotClass.SetActiveCamera(self.Camera)

        cmds.hudButton("SnapButton", edit = True , label = "Update Image", rc = self.RefreshImage)

        cmds.undoInfo(closeChunk = True)
