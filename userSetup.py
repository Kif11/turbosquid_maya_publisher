import maya.cmds as cmds
import maya.mel
import os
import CM_Tools

def createShelf():
     iconPath = os.path.abspath(os.path.join(os.path.dirname(CM_Tools.__file__),".."))+"/Icons/"
     gShelfTopLevel = maya.mel.eval('global string $gShelfTopLevel; $temp = $gShelfTopLevel;')
     cmShelf = gShelfTopLevel + '|TurboSquid'
     if cmds.shelfLayout(cmShelf, exists=True):
          cmds.deleteUI(cmShelf)
     if not cmds.shelfLayout(cmShelf, exists=True):
        cmds.setParent(gShelfTopLevel)
        cmds.shelfLayout('TurboSquid')
     else:
        cmds.setParent(cmShelf)
     if not cmds.shelfButton('CheckMate', exists=True):
        checkMateButton = cmds.shelfButton('CheckMate',
            label='CheckMate',
             parent = 'TurboSquid',
            annotation='Run the CheckMate tools on the current scene',
            image1 = iconPath + 'CheckMatePro.png',
            command='from CM_Tools import SystemFile;reload(SystemFile);SystemFile.SystemClass()'
                    )
        print checkMateButton
     cmds.shelfTabLayout(gShelfTopLevel, e=True, st='TurboSquid')
     cmds.saveAllShelves(gShelfTopLevel)
    
maya.utils.executeDeferred(createShelf)
