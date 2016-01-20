import maya.cmds as cmds
import maya.mel as mel


import zipfile
import os

import SnapShotFile
import TurntableFile
import ShadersFile

    
class ExportClass:
    @staticmethod            
    def CreateArchive(*args):
        cmds.confirmDialog(m = "This action will create a copy of the scene in the temp dir")
            
        ExportTypes = cmds.textScrollList("ExportTextScrollList", query = True, si = True)
        
        for Type in ExportTypes:
            if Type == "ma" or Type == "mb":
                #Save the file copy in the new path
                if Type == "ma":
                    cmds.file( save = True, type='mayaAscii' )
                else:
                    cmds.file( save = True, type='mayaBinary' )
                
                cmds.editRenderLayerGlobals( currentRenderLayer = "defaultRenderLayer")
                
                ShadersFile.ShaderClass.DeleteWireframeShader()
                ShadersFile.ShaderClass.DeleteUVMat()
                if not cmds.objExists("ShadowPlane"):
                    ShadersFile.ShaderClass.DeleteVrayShadowMat()
                    ShadersFile.ShaderClass.DeleteMRShadowMat()
                    
                ModelName = cmds.getAttr("CMSettings.ModelName")
                
                ProjectPath = cmds.getAttr("CMSettings.ProjectPath")
                
                try:cmds.delete("CMSettings")
                except:pass
                
                if cmds.objExists("RWSPlane"):
                    cmds.delete("RWSPlane")
                if cmds.objExists("RWSTexture"):
                    cmds.delete("RWSTexture")
                if cmds.objExists("RWSTexturePlacer"):
                    cmds.delete("RWSTexturePlacer")
                if cmds.objExists("RWSShader"):
                    cmds.delete("RWSShader")
                if cmds.objExists("RWSShaderSG"):
                    cmds.delete("RWSShaderSG")
                
                try:cmds.delete("CMBackground")
                except:pass
                
                SceneParts = ["ShadowPlane", "CMLightRig", "UserLights", "CMBackground"]
                for i in SceneParts:
                    if (not cmds.checkBox( i + "CheckBox", query = True, value = True)) and cmds.objExists(i):
                        if i == "ShadowPlane": 
                            ShadersFile.ShaderClass.DeleteVrayShadowMat()
                            ShadersFile.ShaderClass.DeleteMRShadowMat()
                        if i == "CMLightRig":
                            try: cmds.delete("EnvironmentGamma")
                            except:pass
                        try:cmds.delete(i)
                        except:pass
                    
                #Delete all animations
                try:cmds.cutKey(ModelName)
                except:pass
                
                for mesh in cmds.listRelatives(ModelName, children = True):
                    try:cmds.setAttr(mesh + "Smooth.divisions", 0)
                    except:pass
                    try:cmds.delete(mesh + "Smooth")
                    except:pass
            
                
                #Move the persp to the signatures place
                for i in range(0,len(SnapShotFile.SnapShotClass.SnapShots)):
                    if cmds.getAttr(SnapShotFile.SnapShotClass.SnapShots[i].Camera+'.CMSignature') == True:
                            SnapShotFile.SnapShotClass.SnapShots[i].CopyCameraInfo()
                
                cmds.editRenderLayerGlobals( currentRenderLayer = "defaultRenderLayer")
                
                try:cmds.delete("Signature")
                except:pass
                
                try:cmds.delete("SQRSignature")
                except:pass
                
                try:cmds.delete("ContextSig")
                except:pass
                
                try:cmds.delete("Product")
                except:pass
                
                for i in TurntableFile.TurntableClass.Turntables:
                    try:cmds.delete(i.RenderLayer)
                    except:pass
                
                try:cmds.delete("Wireframe")
                except:pass
                
                try:cmds.delete("Subdivision_0")
                except:pass
                
                try:cmds.delete("Subdivision_1")
                except:pass
                
                try:cmds.delete("UVs")
                except:pass
                
                mel.eval("BakeAllNonDefHistory;")
                #cmds.delete(all = True, constructionHistory = True)
                
                #Delete all cameras
                for i in SnapShotFile.SnapShotClass.SnapShots:
                    cmds.camera(i.Camera, edit = True, startupCamera = False)
                
                for i in TurntableFile.TurntableClass.Turntables:
                        cmds.camera(i.Camera, edit = True, startupCamera = False)
                
                CameraList = SnapShotFile.SnapShotClass.SnapShots
                for i in CameraList:
                    if cmds.getAttr(i.Camera + ".CMSignature"):
                        cmds.setAttr(i.Camera + ".backgroundColor", 0.968627, 0.968627, 0.968627, type = "double3")
                        cmds.rename(i.Camera, ModelName + "Camera")
                        try:cmds.delete(i.Camera + "_ImagePlane")
                        except:pass
                    else:
                        cmds.delete(i.Camera)
                
                CameraList = TurntableFile.TurntableClass.Turntables
                for i in TurntableFile.TurntableClass.Turntables:
                    cmds.delete(i.Camera)
                
                try:cmds.delete("CMForegroundPlane")
                except:pass
                try:cmds.delete("CMBackgroundPlane")
                except:pass
                    
                cmds.select(all = True)
                cmds.editDisplayLayerMembers(ModelName + "_layer", cmds.ls(selection = True), noRecurse = True  )
                cmds.displaySmoothness(divisionsU = 1,divisionsV = 1, pointsWire = 8, pointsShaded = 2, polygonObject = 2)
                for mesh in cmds.ls(sl = True):
                        try: 
                            cmds.setAttr(mesh + ".renderSmoothLevel", 1)
                        except:
                            pass
                
                #Save the file
                if Type == "ma":
                    cmds.file( rename = ProjectPath + "/temp/" + "/CM_" + ModelName + ".ma" )
                    cmds.file( save = True, type='mayaAscii' )
                else:
                    cmds.file( rename = ProjectPath + "/temp/" + "/CM_" + ModelName + ".mb" )
                    cmds.file( save = True, type='mayaBinary' )
                
                #Create the zip file
                if Type == "ma":
                    zipf = zipfile.ZipFile(ProjectPath + "/" + ModelName + '_ma.zip', 'w')
                else:
                    zipf = zipfile.ZipFile(ProjectPath + "/" + ModelName + '_mb.zip', 'w')
                    
                
                #write to the zip file
                if Type == "ma":
                    zipf.write(ProjectPath + "/temp/" + "CM_" + ModelName + ".ma", os.path.basename(ProjectPath + "/temp/" + "CM_" + ModelName + ".ma"))                
                else:
                    zipf.write(ProjectPath + "/temp/" + "CM_" + ModelName + ".mb", os.path.basename(ProjectPath + "/temp/" + "CM_" + ModelName + ".mb"))                
                
                    
                
                ##### Get textures ####
                def GetTextures():
                    Textures = []
                    
                    for i in cmds.ls(textures = True):
                        try:
                            Textures.append(cmds.getAttr(i + ".fileTextureName"))
                        except:
                            pass
                    #Remove duplicates    
                    return list(set(Textures))
                
                for i in GetTextures():
                    try:
                        zipf.write(i, os.path.basename(i))
                    except:
                        print "Could not write file ", i , " to zip"
                zipf.close()
                
            else:            
                #Create the export file
                try:
                    fileName = cmds.file(ProjectPath+ "/Temp/" + "CM_" + ModelName, exportAll = True, type = Type )
                except:
                    print "Failed to export scene in format :" , Type
                    continue
                
                #Create the zip file
                zipf = zipfile.ZipFile(ProjectPath + "/" + ModelName + '_' + Type +'.zip', 'w')
                
                #Iges format returns a wrong path fix it 
                if not os.path.exists(fileName):
                    Name, fileExtension = os.path.splitext(fileName)
                    if fileExtension == ".iges":
                        fileName = Name + ".igs"
                
                #Write the file into the zip
                try:
                    zipf.write(fileName, os.path.basename(fileName))
                except:
                    print "Could not write the format:", Type, " to zip file"
                
                #Write the textures in the zip
                for i in GetTextures():
                    try:
                        zipf.write(i, os.path.basename(i))
                    except:
                        pass
                zipf.close()
        
        cmds.displaySmoothness(divisionsU = 0,divisionsV = 0, pointsWire = 4, pointsShaded = 1, polygonObject = 1)
        
        #Save the file
        fileName = cmds.file(l = True, q = True)
        fileName = fileName[0]
        Extension = os.path.splitext(fileName)[1]
        if Extension == '.ma':            
            cmds.file( save = True, type='mayaAscii' )
        elif Extension == '.mb':
            cmds.file( save = True, type='mayaBinary' )
        elif Extension == "":
            cmds.file( save = True, type='mayaAscii' )
        
        cmds.confirmDialog(m = "The orginal file has been saved in the project folder")
        
        #Check to see if the window exists if it does delete it
        if cmds.dockControl("CMMainDock", exists = True):
            try:
                cmds.deleteUI("CMMainDock")
            except:
                print "Could not delete Main Dock"
        elif cmds.window("CMMainWindow", exists = True):
            try:
                cmds.deleteUI("CMMainWindow")
            except:
                print "Could not delete Main Window"
        
        if cmds.headsUpDisplay('SnapButton', exists = True):
            cmds.headsUpDisplay('SnapButton', rem = True)
        
        cmds.select(cmds.listRelatives(cmds.ls(cameras = True, lights = True),parent = True))
        try:
            cmds.select("UserLights", add = True)
        except:
            pass
        try:
            cmds.select("CMLightRig", add = True)
        except:
            pass
        try:
            cmds.editDisplayLayerMembers( 'CM_Lights_and_Cameras', cmds.ls(selection = True) )
        except:
            pass