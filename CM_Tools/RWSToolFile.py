import maya.cmds as cmds
from functools import partial
import csv
import os


class RWSToolClass:
    
    def __init__(self):
        print "Initializing RWS tool"
        self.Path = os.environ['CM_TOOLS'] + "RWS Data/"
        self.ParentSelection = ""
        self.ChildSelection = ""
    
    def CreateUI(self):
        if cmds.window("RWSWindow", q = True, exists = True):
            cmds.deleteUI("RWSWindow")
    
        cmds.window("RWSWindow", h = 200, w = 140)
        cmds.columnLayout("RWSLayout", p = "RWSWindow")
        cmds.text(label = "Select a category", p = "RWSLayout")
        cmds.rowLayout("RWSCategoryLayout", p = "RWSLayout", nc = 2)
        
        #For parent category
        cmds.textScrollList("RWSParentSelect", p = "RWSCategoryLayout", h = 200, w = 120)
        
        #For Child category
        cmds.textScrollList("RWSChildSelect", p = "RWSCategoryLayout", h = 200, w = 120, visible = False)
        
        #Dimensions
        cmds.rowLayout("DimensionLayout", p = "RWSLayout", nc = 4, visible = False)
        
        cmds.text(label = "Width", p = "DimensionLayout")
        cmds.floatField("RWSYfield", p = "DimensionLayout")
        cmds.text(label = "Height", p = "DimensionLayout")
        cmds.floatField("RWSZfield", p = "DimensionLayout")
        
        
    def start(self, *args):
        if cmds.ls(sl = True) == [] and (not cmds.objExists("CMSettings")):
            cmds.confirmDialog(m = "Please select the mesh/meshes you want to review")
            return 0 
        
        parent = os.listdir(self.Path)
        
        self.CreateUI()
        
        #For parent category
        cmds.textScrollList("RWSParentSelect", edit = True, append = parent, sc = self.SelectedParent)
        
        
        cmds.showWindow("RWSWindow")
        
    
    def SelectedParent(self, *args):
        self.ParentSelection = cmds.textScrollList( "RWSParentSelect", query = True, si = True)[0]
        
        if os.path.exists(self.Path + self.ParentSelection + "/" + self.ParentSelection + ".csv"):
            csvFile = open(self.Path + self.ParentSelection + "/" + self.ParentSelection + ".csv", 'rb')
            spamReader = csv.reader(csvFile, delimiter = ',')
            #Create a list 
            List = []
            for row in spamReader:
                List.append(row)
                print row
            
            #Create another list from the first element of the list
            parent = []
            for i in List:
                parent.append(i[0])
                print parent
                
            cmds.textScrollList("RWSChildSelect",edit = True, removeAll = True)
            cmds.textScrollList("RWSChildSelect",edit = True, append = parent, sc = partial(self.SelectedChild, List), visible = True)
            
            
    def SelectedChild(self, List, *args):
        self.ChildSelection = cmds.textScrollList( "RWSChildSelect", query = True, si = True)[0]
        
        print List
        
        Dimensions = []
        for i in List:
            if i[0] == self.ChildSelection:
                try:Dimensions.append(i[0])
                except:pass
                try:Dimensions.append(i[1])
                except:pass
                try:Dimensions.append(i[2])
                except:pass
        
        cmds.rowLayout("DimensionLayout", edit = True, visible = True)
           
        try:cmds.floatField("RWSYfield", edit = True, v = float(Dimensions[1]))
        except:cmds.floatField("RWSYfield", edit = True, v = 0)
        try:cmds.floatField("RWSZfield", edit = True, v = float(Dimensions[2]))
        except:cmds.floatField("RWSZfield", edit = True, v = 0)
        
        self.CreateImagePlane()
        
        
        
    def CreateImagePlane(self):
        print self.ChildSelection
        print self.ParentSelection
        
        Texture = self.Path + self.ParentSelection + "/" + self.ChildSelection + ".png"
        
        if os.path.exists(Texture):
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
                
            cmds.polyPlane(name = "RWSPlane",width = cmds.floatField("RWSYfield", query = True, v = True), height = cmds.floatField("RWSZfield", query = True, v = True) , subdivisionsX = 1, subdivisionsY = 1  )
            cmds.rotate(90, 0, 0, "RWSPlane" )
            
            cmds.setAttr("RWSPlaneShape.castsShadows", 0)
            cmds.setAttr("RWSPlaneShape.receiveShadows", 0)
            cmds.setAttr("RWSPlaneShape.motionBlur", 0)
            cmds.setAttr("RWSPlaneShape.primaryVisibility", 0)
            cmds.setAttr("RWSPlaneShape.smoothShading", 0)
            cmds.setAttr("RWSPlaneShape.visibleInReflections", 0)
            cmds.setAttr("RWSPlaneShape.visibleInRefractions", 0)
            cmds.setAttr("RWSPlaneShape.doubleSided", 0)
            
            if cmds.objExists("CMSettings"):
                ModelName = cmds.getAttr("CMSettings.ModelName")
            else:
                ModelName = cmds.ls(sl = True)
                
            
            bbx = cmds.xform(ModelName, bb = True, q = True)
            zMove = -(bbx[5]-bbx[2])/2
            yMove = cmds.floatField("RWSZfield", query = True, v = True)/20
            cmds.move(0, yMove, zMove ,"RWSPlane")
            material = cmds.shadingNode('lambert', asShader=1, name='RWSShader')
            SG = cmds.sets(renderable=1, noSurfaceShader=1, empty=1, name = 'RWSShaderSG')   
            cmds.connectAttr((material + '.outColor'),(SG + '.surfaceShader'),f=1)
            
            cmds.shadingNode("file", asTexture = True, name = "RWSTexture" )
            cmds.setAttr("RWSTexture.fileTextureName", Texture, type = "string")
            cmds.shadingNode("place2dTexture", asUtility = True, name = "RWSTexturePlacer")
            cmds.connectAttr( "RWSTexturePlacer.outUV", "RWSTexture.uv")
            cmds.connectAttr( "RWSTexturePlacer.outUvFilterSize", "RWSTexture.uvFilterSize")
            cmds.connectAttr(  "RWSTexture.outColor", "RWSShader.color", force = True)
             
            try:
                cmds.select("RWSPlane")
                cmds.sets(cmds.ls(selection = True), forceElement = 'RWSShaderSG', e = True)
            except:
                print "Failed to assign shader"
            
            cmds.select(None)