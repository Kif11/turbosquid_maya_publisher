import maya.cmds as cmds

import subprocess
import os

class DescriptionToolClass:
    
    def __init__(self):
        print "Initializing description tool"
        self.ModelName = ""
        self.projectDir = ""
    
    def CreateDescription(self,*args):
        #Get the model name and the project directory
        self.ModelName = cmds.getAttr("CMSettings.ModelName")
        self.projectDir = cmds.getAttr("CMSettings.ProjectPath")
        
        #Get the documents directory and the process
        if os.path.exists(os.environ['CM_TOOLS'] + "/Imaging/GetImageSize.exe"):
            ImageSizeProcess = os.environ['CM_TOOLS'] + "/Imaging/GetImageSize.exe"
        elif os.path.exists(os.environ['CM_TOOLS'] + "/Imaging/GetImageSize"):
            ImageSizeProcess = os.environ['CM_TOOLS'] + "/Imaging/GetImageSize"
        
        import ntpath
        
        if cmds.window("DescriptionWindow", query = True, exists = True):
            cmds.deleteUI("DescriptionWindow")
        
        #Create the base UI for the description tool
        cmds.window("DescriptionWindow", title = "Model Description", w = 500, h = 600)    
        cmds.formLayout("CMDescriptionLayout", p = "DescriptionWindow")
        cmds.rowLayout("DesRowLayout", p = "CMDescriptionLayout", nc = 3, h = 40)
        
        #Get the model elements
        cmds.select(self.ModelName, hierarchy = True)
        PolyCount = cmds.polyEvaluate(cmds.ls(selection = True, g = True), f = True)
        TriCount = cmds.polyEvaluate(cmds.ls(selection = True, g = True), t = True)
        VertexCount = cmds.polyEvaluate(cmds.ls(selection = True, g = True), v = True)
        
        #Get Maya version
        version = cmds.about(version = True)
        
        #Get Current renderer
        CurRenderer = cmds.getAttr("defaultRenderGlobals.currentRenderer") 
        
        ##### Get textures ####
        def GetTextures():
            Textures = []
            
            for i in cmds.ls(textures = True):
                try:
                    if i != "CheckerMap":
                        Textures.append(cmds.getAttr(i + ".fileTextureName"))
                except:
                    pass
            #Remove duplicates    
            return list(set(Textures))
        
        Textures = GetTextures()
        
        #Get the texture sizes
        Output = "*************************** Textures *****************************\r\n"
        if Textures == []:
            Output = ""
        for i in range(0,len(Textures)):
            try:
                src = Textures[i]
                ext = os.path.splitext(src)[1]
                if ext == ".psd":
                    cmds.psdExport( psdFileName = src, outFileName = self.projectDir + "/Temp/" + self.ModelName + "_PSD.jpg", format = "jpg" )
                    w, h = subprocess.Popen([ImageSizeProcess, src],creationflags=subprocess.SW_HIDE, shell=True, stdout=subprocess.PIPE).communicate()[0].split(" ")
                    Output = Output + " Texture:" + ntpath.basename(src) + ", Size:" + str(w) + "x" + str(h) + "\r\n"
                else:
                    w, h = subprocess.Popen([ImageSizeProcess, src],creationflags=subprocess.SW_HIDE, shell=True, stdout=subprocess.PIPE).communicate()[0].split(" ")
                    Output = Output + " Texture:" + ntpath.basename(src) + ", Size:" + str(w) + "x" + str(h) + "\r\n"
            except:
                pass
        
        #Get the bounding box of the model
        bbx = cmds.xform(self.ModelName, bb = True, q = True)
        
        #Create the static Description field
        cmds.scrollField("ScrollFieldStats", p = "CMDescriptionLayout", h = 127, editable = False, text = 
                                                                            "*************************** Model Data ***************************\r\n"+
                                                                            " Model Name    :" + self.ModelName + "\r\n"+
                                                                            " Poly Count    :" + str(PolyCount) + "\r\n"+
                                                                            " Tri Count     :" + str(TriCount)  + "\r\n"+
                                                                            " Vertex Count  :" + str(VertexCount)  + "\r\n"+
                                                                            " Renderer      :" + CurRenderer    + "\r\n"+
                                                                            " Maya Version  :" + version        + "\r\n"+
                                                                            Output+
                                                                            "***************************    Units    **************************\r\n"+
                                                                            " Units Used:" + cmds.currentUnit( query=True, linear=True )        + "\r\n"+
                                                                            " Model Size:" + "Length: "+ str(round((bbx[3] - bbx[0]),2)) + ", Width:" + str(round((bbx[5] - bbx [2]),2)) + ", Height:" +  str(round((bbx[4]-bbx[1]),2)) + "\r\n"+
                                                                            "*************************** Description **************************"
                                                                            )
        
        
        DesText = ""
        if os.path.exists(self.projectDir+ "/" + self.ModelName + "_Description.txt"):
            File = open(self.projectDir+ "/" + self.ModelName + "_Description.txt","r")
            
            l = 0 
            for line in File:
                if l > 11 + len(Textures):
                    DesText = DesText + line
                l += 1
                
            File.close()
        
        
        def OnKeyPress(*args):
            cmds.text("DesSaved", edit = True, label = "")
            
        #Create the custom description field
        cmds.scrollField("ScrollFieldDes", p = "CMDescriptionLayout", text = DesText, keyPressCommand = OnKeyPress)
        if DesText == "":
            cmds.scrollField("ScrollFieldDes", edit = True, text = "Write the model description here")
        
        
        cmds.formLayout( "CMDescriptionLayout", edit=True,
                         attachForm=[("ScrollFieldStats", 'top', 5), ("ScrollFieldStats", 'left', 5), ("ScrollFieldStats", 'right', 5), 
                         ("ScrollFieldDes", 'left', 5), ("ScrollFieldDes", 'right', 5),
                         ("DesRowLayout", 'left', 5), ("DesRowLayout", 'right', 5), ("DesRowLayout", 'bottom', 5)],
                         attachNone= [("ScrollFieldStats", 'bottom'),("DesRowLayout", 'top')],
                         attachControl = [("ScrollFieldDes", 'bottom', 5, "DesRowLayout"),("ScrollFieldDes", 'top', 5, "ScrollFieldStats")] 
                         )
        
        def SaveButton(*args):
            File = open(self.projectDir+ "/" + self.ModelName + "_Description.txt", "w")
            File.write( cmds.scrollField("ScrollFieldStats", query = True, text = True) + "\r\n" + cmds.scrollField("ScrollFieldDes", query = True, text = True))
            File.close()
            cmds.text("DesSaved", edit = True, label = "    File saved")
        
        #Create the save button
        cmds.button(p="DesRowLayout", label = "Save", w = 100, c = SaveButton)
        cmds.text("DesSaved", p = "DesRowLayout", label = "")
        #Show the window
        cmds.showWindow("DescriptionWindow")