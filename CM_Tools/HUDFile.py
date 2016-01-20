import maya.cmds as cmds

import math


class HUDClass:
    def __init__(self):    
        self.functions = []
        
        if cmds.headsUpDisplay('SnapButton', exists = True):
            cmds.headsUpDisplay('SnapButton', rem = True)
        cmds.hudButton('SnapButton', s=7, b=5, vis = False, l='Snap Image', bw = 120, bsh ='roundRectangle' ) 
        
        
    def BindFunctions(self, functions):
        self.functions = functions
    
    #does not require undo
    def TurntableHelper(self, create = True):
        cmds.undoInfo(stateWithoutFlush = False)
        if(cmds.objExists("CMSettings")):
            if(cmds.getAttr("CMSettings.ModelName") != None):
                bbx = cmds.xform(cmds.getAttr("CMSettings.ModelName"), bb = True, q = True)
                diagonal = math.sqrt((bbx[3] - bbx[0])*(bbx[3] - bbx[0]) + (bbx[5] - bbx [2])*(bbx[5] - bbx [2])) 
                
                if create:
                    if not cmds.objExists("HelperCircleTop"):
                        cmds.circle( name = "HelperCircleTop", center = [0,bbx[4],0], radius = diagonal/2.0, nr = [0,1,0])
                    if not cmds.objExists("HelperCircleBot"):
                        cmds.circle( name = "HelperCircleBot", center = [0,bbx[1],0], radius = diagonal/2.0, nr = [0,1,0])
                else:
                    if cmds.objExists("HelperCircleTop"):
                        cmds.delete("HelperCircleTop")
                    if cmds.objExists("HelperCircleBot"):
                        cmds.delete("HelperCircleBot")
        cmds.undoInfo(stateWithoutFlush = True)
        
    def HUDInterface(self):
        SelectedTab = cmds.tabLayout( "TabLayout", query = True, st = True)
        
        #Get the persp panel
        perspPanel = cmds.getPanel( withLabel='Persp View')
        #change the view to the camera
        cmds.modelPanel( perspPanel, edit = True, camera = "persp")
        
        #When the Project tab is clicked
        if SelectedTab == "CMProjectLayout":
            cmds.hudButton("SnapButton", edit = True , vis = False)
            self.TurntableHelper(False)
            
        #When Image tab is clicked
        elif SelectedTab == "SnapShotTabLayout":     
            cmds.hudButton("SnapButton", edit = True, rc = self.functions[0] , label = "Snap Image", vis = True)
            self.TurntableHelper(False)
             
        #When the turntable tab is clicked
        elif SelectedTab == "TurntableCounterLayout":
            cmds.hudButton("SnapButton", edit = True , rc = self.functions[1], label = "Create Turntable", vis = True)
            self.TurntableHelper(True)
             
        #When the Renderer tab is clicked
        elif SelectedTab == "BatchRendererCounterLayout":
            cmds.hudButton("SnapButton", edit = True , vis = False)
            self.TurntableHelper(False)
             
            #cmds.text("BatchRendererCounter", edit = True, label = "Image to render = " + str(BatchRendererFile.BatchRendererClass.ChangeCounter()))