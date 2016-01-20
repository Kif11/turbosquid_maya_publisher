import maya.cmds as cmds

#Method is not meant to be undone does not change anything
def ScreenCapture(filename,resolution, color = 0.361):
	cmds.undoInfo(stateWithoutFlush = False)
	try:
		oldFormat = cmds.getAttr("defaultRenderGlobals.imageFormat")
		
		cmds.setAttr("defaultRenderGlobals.imageFormat", 32)
		
		#Store the current display colors
		colors = [cmds.displayRGBColor("background", query = True), 
				cmds.displayRGBColor("backgroundTop", query = True), 
				cmds.displayRGBColor("backgroundBottom", query = True)]
		
		#To make the UI prettier
		cmds.displayRGBColor("background", color, color, color)
		cmds.displayRGBColor("backgroundTop", color, color, color)
		cmds.displayRGBColor("backgroundBottom", color, color, color)
		
		#Take a snap for the UI
		cmds.playblast(frame=0,fmt="image",viewer=0,fp=4,orn=0,p=100,wh=resolution,ifz=0,fo=1,offScreen=1,cf=filename)
		
		#Revert to the old colors
		cmds.displayRGBColor("background", colors[0][0], colors[0][1], colors[0][2])
		cmds.displayRGBColor("backgroundTop", colors[1][0], colors[1][1], colors[1][2])
		cmds.displayRGBColor("backgroundBottom", colors[2][0], colors[2][1], colors[2][2])
	
		cmds.setAttr("defaultRenderGlobals.imageFormat", oldFormat)
		
	except:
		pass
	cmds.undoInfo(stateWithoutFlush = True)
	
