import maya.cmds as cmds
import math

class spaceDivision:
    
    
    def __init__(self, volume ):
        self.spaceCoordinates = volume 
        self.isFree = True
        self.spaceIsEmpty()
        
    def spaceIsEmpty(self):
        volume = self.spaceCoordinates
        for mesh in cmds.listRelatives(NormalClass.modelName, children = True):
            print mesh
            print volume
            nearestnode = cmds.nearestPointOnMesh("pCone1", ip = [(volume[3]+volume[0])/2,(volume[4]+volume[1])/2,(volume[5]+volume[2])/2])
            nearestposition = cmds.getAttr('%s.position' % nearestnode)[0]
            print nearestposition
            cmds.delete(nearestnode)
            if nearestposition[0] < volume[3] and nearestposition > volume[0] and nearestposition[1] < volume[4] and nearestposition > volume[1] and nearestposition[2] < volume[5] and nearestposition > volume[2]:
                self.isFree = False
                break
        
            
    def createBox(self):
        volume = self.spaceCoordinates
        self.box = cmds.polyCube(width = math.fabs(volume[3]-volume[0]), depth = math.fabs(volume[5]-volume[2]), height = math.fabs(volume[4]-volume[1]))
        cmds.move( (volume[3]+volume[0])/2, (volume[4]+volume[1])/2, (volume[5]+volume[2])/2, self.box, absolute=False )
        
    
    def deleteBox(self):
        if not self.isFree:
            cmds.delete(self.box)
    
class NormalClass:
    
    divisionList = []
    deletionList = []
    modelName = ""
    
    
    def __init__(self):
        # set up necessary plug-ins
        if not cmds.pluginInfo('nearestPointOnMesh', query=True, loaded=True):
            try:
                cmds.loadPlugin('nearestPointOnMesh')
            except NameError:
                pass
            
    def DivideSpace(self, volume, subDivisionLevel):
        mean = [(volume[3]+volume[0])/2,
                      (volume[4]+volume[1])/2,
                      (volume[5]+volume[2])/2]
        
        sd = []
        sd.append(spaceDivision([mean[0], mean[1], mean[2], volume[3], volume[4], volume[5]]))
        sd.append(spaceDivision([volume[0], mean[1], mean[2], mean[0] , volume[4], volume[5]]))
        sd.append(spaceDivision([mean[0], volume[1], mean[2], volume[3], mean[1], volume[5]]))
        sd.append(spaceDivision([volume[0], volume[1], mean[2], mean[0] , mean[1], volume[5]]))
        
        sd.append(spaceDivision([mean[0], mean[1], volume[2], volume[3], volume[4], mean[2]]))
        sd.append(spaceDivision([volume[0], mean[1], volume[2], mean[0] , volume[4], mean[2]]))
        sd.append(spaceDivision([mean[0], volume[1], volume[2], volume[3], mean[1], mean[2]]))
        sd.append(spaceDivision([volume[0], volume[1], volume[2], mean[0] , mean[1], mean[2]]))
        
        if subDivisionLevel == 0:
            NormalClass.divisionList = NormalClass.divisionList + sd
            for i in NormalClass.divisionList:
                i.createBox()
                i.deleteBox()
             
        else:
            for i in sd:
                self.DivideSpace(i.spaceCoordinates, subDivisionLevel - 1)
            
    def useVolume(self, modelName):
        NormalClass.modelName = modelName
        bbx = cmds.xform(modelName, bb = True, q = True)
        
        self.DivideSpace(bbx, 1)
        

    
Tester = NormalClass()
Tester.useVolume("pCone1")