import maya.cmds as cmds

import subprocess
import os


class RenderUVClass:
    
    UVSelection = []
    
    @staticmethod
    def RenderUVS():
        import ntpath
        cmds.editRenderLayerGlobals(currentRenderLayer = "defaultRenderLayer")
        
        for i in RenderUVClass.UVSelection:
            #Get the textures for the object
            texture = RenderUVClass.GetTextures(i)
            if texture == []:
                continue
            
            for j in range(len(texture)):
                if ntpath.split(texture[j])[1] != "ash_uvgrid.jpg":
                    texture = texture[j]
                    break
            
            ext = os.path.splitext(texture)[1]
            if ext == ".psd":
                cmds.psdExport( psdFileName = texture, outFileName = cmds.getAttr("CMSettings.ProjectPath") + "/temp/" + cmds.getAttr("CMSettings.ModelName") + "_UVTemplate.jpg", format = "jpg" )
                texture = cmds.getAttr("CMSettings.ProjectPath") + "/temp/" + cmds.getAttr("CMSettings.ModelName") + "_UVTemplate.jpg"
            
            cmds.select(i)
               
            #Clean up the names
            first = -1
            last  = 0
            l = 0 
            for c in i:
                if c == '|' and first == -1:
                    first = l 
                elif c=='|' and first != -1:
                    last = l
                l += 1
        
            if first != -1:
                i = i[:first] + i[last+1:]
            
            if os.path.exists(os.environ['CM_TOOLS'] + "/Imaging/ResizeForUVs.exe"):
                program = os.environ['CM_TOOLS'] + "/Imaging/ResizeForUVs.exe"
            elif os.path.exists(os.environ['CM_TOOLS'] + "/Imaging/ResizeForUVs"):
                program =os.path.exists(os.environ['CM_TOOLS'] + "/Imaging/ResizeForUVs")
                
            argument1 = texture
            argument2 = cmds.getAttr("CMSettings.ProjectPath") + "/temp/" + cmds.getAttr("CMSettings.ModelName") + "_TempTex.png"
            size = subprocess.Popen([program, argument1, argument2],creationflags=subprocess.SW_HIDE, shell=True, stdout=subprocess.PIPE).communicate()[0]
            w, h = size.split(" ")
            
            #Create the UV template of the same size
            uvTemplate = cmds.getAttr("CMSettings.ProjectPath") + "/temp/" + cmds.getAttr("CMSettings.ModelName") + "_UV_"+ i +".png"
            cmds.uvSnapshot(antiAliased=True, fileFormat = "png", name = uvTemplate, overwrite = True, xResolution = int(w), yResolution = int(h)) 
            
            
            if os.path.exists(os.environ['CM_TOOLS'] + "/Imaging/OverlayImages.exe"):
                program = os.environ['CM_TOOLS'] + "/Imaging/OverlayImages.exe"
            elif os.path.exists(os.environ['CM_TOOLS'] + "/Imaging/OverlayImages"):
                program = os.environ['CM_TOOLS'] + "/Imaging/OverlayImages"
            
            argument1 = cmds.getAttr("CMSettings.ProjectPath") + "/temp/" + cmds.getAttr("CMSettings.ModelName") + "_TempTex.png"
            argument2 = uvTemplate
            argument3 = cmds.getAttr("CMSettings.ProjectPath") + "/images/" + cmds.getAttr("CMSettings.ModelName") + "_UV_"+ i +".png"
            
            subprocess.call([program, argument1, argument2, argument3],creationflags=subprocess.SW_HIDE, shell=True)    
      
    @staticmethod
    def SelectObjectsForUV(*args):
        if cmds.window("SelWindow", query = True, exists = True):
            cmds.deleteUI("SelWindow")
            
        ################################### User Interface Selection Window ################################        
        cmds.window("SelWindow", title="Object Selection", iconName='Short Name', widthHeight=(300,100) )
        cmds.rowColumnLayout(numberOfRows=3 , rowHeight=[(1, 40), (2, 20), (3, 40)] )
        cmds.text(label = "Select the objects for the UV overlay renders", align = "center")
        cmds.text(label = "")
        cmds.rowColumnLayout(numberOfColumns = 3, columnWidth=[(1, 100), (2, 100), (3, 100)])
        cmds.text(label = "")
        cmds.button( label='Done' , command = RenderUVClass.DoneButton)
        cmds.text(label = "")
        cmds.showWindow()
    
    @staticmethod
    def DoneButton(*args):
        if cmds.window("SelWindow", query = True, exists = True):
            cmds.deleteUI("SelWindow")
        
        RenderUVClass.UVSelection = cmds.ls(selection = True)
        if RenderUVClass.UVSelection == []:
            cmds.confirmDialog(m = "No objects were selected")
        
        else:
            Shapes = []
            for i in RenderUVClass.UVSelection:
                if ( "transform" ==  cmds.nodeType(i) ):
                    # If given node is not a transform, assume it is a shape
                    # and pass it through
                    relatives = cmds.listRelatives( i, fullPath = True, shapes = True)
                    if relatives != None:
                        for j in range(len(relatives)):
                            Shapes.append(relatives[j])
                else:
                    Shapes.append(i)      
            RenderUVClass.UVSelection = Shapes
            
            #Render the UV template
            RenderUVClass.RenderUVS()
            
            cmds.confirmDialog(m = "File saved in images folder")
    
    @staticmethod
    def GetTextures(ShapeNode):
        # Get shading engine off the shape node.
        shadingEngine = cmds.listConnections(ShapeNode, type = "shadingEngine")
        if shadingEngine == None:
            return []
        textures = []
        for sengine in shadingEngine:
            # Get the surfaceShader from the shading engine
            shaders = cmds.listConnections(sengine + ".surfaceShader")
            if shaders == None:
                shaders = cmds.listConnections(sengine + ".miMaterialShader")
            print shaders
            # Get the texture connections from the shader
            # Add a checker texture (or any other texture2d) to the lambert1.color and it will be found.
            temp = cmds.listConnections( shaders, t = "texture2d" )
            
            if temp != None:
                for File in temp:
                    try:
                        if File != "CheckerMap":
                            textures.append(cmds.getAttr(File + ".fileTextureName"))
                    except:
                        print "Could not find texture name for : ", File
        return textures      
    