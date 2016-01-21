import maya.cmds as cmds
import maya.mel as mel

import ntpath
import subprocess
import shutil
import sys
import os


class ProjectClass:
    
    def __init__(self):
        print "Initializing project class"
        self.ModelName = ""
        self.projectDir = ""
        self.textures = []
        
    def OpenProjectInBrowser(self, *args):
        subprocess.Popen('explorer "{0}"'.format(os.path.normpath(self.projectDir)))
    
    def create_projectDirectories(self):
        print "Creating directory"
        #While the user doesn't create a unique and valid project keep prompting him to do so
        while True:
            #Select the output directory 
            self.projectDir = ""
            try:
                self.projectDir = cmds.fileDialog2(fm = 3, fileFilter = None, ds = 2, cap = "Please select a CM project directory")[0]
            except:      
                print "No directory specified"
                #If no output directory is specified delete everything and exit
                cmds.undoInfo(closeChunk = True)
                cmds.delete("CMSettings")
                sys.exit()
            
            #Create the #main project directory
            if not os.path.exists( self.projectDir + "/CM_" + self.ModelName ):
                os.makedirs( self.projectDir + "/CM_" + self.ModelName )
                #Update the output directory
                self.projectDir = self.projectDir + "/CM_" + self.ModelName
                break
            else:
                cmds.confirmDialog(m = "Directory already exists")
            
        #Create the project path attribute
        cmds.setAttr("CMSettings.ProjectPath", self.projectDir,type = "string")
        
        if not os.path.exists(self.projectDir + "/temp"):
            os.makedirs(self.projectDir + "/temp")
        if not os.path.exists(self.projectDir + "/images"):
            os.makedirs(self.projectDir + "/images")
    
    def SaveScene(self):
        #Save the file copy in the new path
        fileName = cmds.file(l = True, q = True)
        fileName = fileName[0]
        Extension = os.path.splitext(fileName)[1]
        if Extension == '.ma':            
            cmds.file( rename = self.projectDir + "/Orignal_" + self.ModelName + ".ma" )
            cmds.file( save = True, type='mayaAscii' )
        elif Extension == '.mb':
            cmds.file( rename = self.projectDir + "/Orignal_" + self.ModelName + ".ma" )
            cmds.file( save = True, type='mayaBinary' )
        elif Extension == "":
            cmds.file( rename = self.projectDir + "/Orignal_" + self.ModelName + ".ma" )
            cmds.file( save = True, type='mayaAscii' )
        if Extension == '.ma':            
            cmds.file( rename = self.projectDir + "/CM_" + self.ModelName + ".ma" )
            cmds.file( save = True, type='mayaAscii' )
        elif Extension == '.mb':
            cmds.file( rename = self.projectDir + "/CM_" + self.ModelName + ".ma" )
            cmds.file( save = True, type='mayaBinary' )
        elif Extension == "":
            cmds.file( rename = self.projectDir + "/CM_" + self.ModelName + ".ma" )
            cmds.file( save = True, type='mayaAscii' )
    
    def create_project(self):
        print "Creating new project"
        self.ModelName = cmds.getAttr("CMSettings.ModelName")
        
        self.create_projectDirectories()
        
        self.SaveScene()
        
        #Set the project to the scene folder
        mel.eval('setProject "' + os.path.normpath(self.projectDir).replace("\\",'/') + '"')
        
        #Collect the textures in the folder
        self.CollectTextures()
        
        return self.projectDir
        
    def OpenProject(self):
        print "Opening project"
        self.ModelName = cmds.getAttr("CMSettings.ModelName")
        
        #Update path
        storedPath = os.path.normpath(cmds.getAttr("CMSettings.ProjectPath")).lower()
        FilePath = os.path.normpath(ntpath.split(cmds.file(query = True, exn = True))[0]).lower()
        
        #Update the path
        if storedPath != FilePath:
            cmds.setAttr("CMSettings.ProjectPath", FilePath, type = "string")
        
        self.projectDir = cmds.getAttr("CMSettings.ProjectPath")
        
        
        #Set the project
        mel.eval('setProject "' + os.path.normpath(self.projectDir).replace("\\",'/') + '"')
        
        #Collect the textures in the folder
        self.CollectTextures()
        
        if not os.path.exists(self.projectDir + "/temp"):
            os.makedirs(self.projectDir + "/temp")
        if not os.path.exists(self.projectDir + "/images"):
            os.makedirs(self.projectDir + "/images")
        
    def CollectTextures(self):
        #Set the texture paths        
        Textures = cmds.ls(textures = True)
        
        for i in Textures:
            try:
                src = cmds.getAttr(i + ".fileTextureName")
            except:
                continue
            
            des = self.projectDir + "/" + os.path.split(src)[1]
                        
            try:
                shutil.copy( src, des )
            except:
                pass
            try:
                cmds.setAttr(i + ".fileTextureName", os.path.split(src)[1], type = "string" )
            except:
                print "Failed to set attribute"
            
    