import time
import os
from maya import cmds as cmds
from maya import mel as mel


def snapshots(*args, **kwargs):
    """ in GUI mode, renders snapshots of the model views
    returns reportsDir
    render_snapshots() -> string
    """
    t0 = float(time.time())
    try:
        verbose = kwargs['verbose']
    except KeyError:
    	verbose=False
    	if cmds.optionVar(exists='checkmateVerbosity'):
    		verbose = cmds.optionVar(query='checkmateVerbosity')
    else:
        pass
        
    #check that we;re running in GUI mode
    if cmds.about(batch=True):
        print 'You can\'t create a render view in batch mode'
        return 1
    # turn off the heads-up diplay
    cmds.headsUpDisplay(layoutVisibility=False )
    
    # clear selection
    cmds.select(clear=True)
    
    _userWorkspaceDir = cmds.internalVar(userWorkspaceDir=True)       
    scene = cmds.file(query=True, sn=True, shn=True) or 'unknown.mb'
    (root, ext) = os.path.splitext(scene)
    fullscenepath = cmds.file(query=True, sn=True, shn=False) or 'unknown.mb'
    fullscenedirname = os.path.dirname(fullscenepath)
    if fullscenedirname == '':
            fullscenedirname = os.path.join(_userWorkspaceDir, 'reports')
            
    reportname = ''.join([root, ext.replace('.','_')])
    img_dir = os.path.join(fullscenedirname,reportname)

        
    # before we render, save render globals presets
    cmds.nodePreset(save=('defaultRenderQuality', "ttRestorePreviousDefaultRenderViewPreset"))
    cmds.nodePreset(save=('defaultRenderGlobals', "ttRestorePreviousDefaultRenderViewPreset"))
    cmds.nodePreset(save=('defaultResolution', "ttRestorePreviousDefaultRenderViewPreset"))

    # override the user settings
    cmds.setAttr("defaultRenderGlobals.imageFormat",32)
    ext = ".png"
    # set resolution ot 320x240
    cmds.setAttr("defaultResolution.width", 320)
    cmds.setAttr("defaultResolution.height", 240)
    cmds.setAttr('defaultResolution.deviceAspectRatio', (float(320)/float(240)))
    
    # set file format to png
    cmds.setAttr("defaultRenderGlobals.imageFormat", 32)
    ext = '.png'

    # bring up the render view
    if not cmds.window('renderViewWindow', exists=True):
        cmds.RenderViewWindow()
    
    # cameras to render
    cameras = ['top', 'front', 'side', 'persp']
    
    for camera in cameras :          
        mel.eval(''.join(['renderWindowRenderCamera snapshot renderView ', camera]))
        image = ''.join([camera, ext])
        # we can get the path from the report class instance
        imagepath = os.path.join(img_dir, image)
        if verbose:
            print 'imagepath : %s ' % imagepath
        #delete the images before saving
        cmds.sysFile(imagepath, delete=True )    
        cmds.renderWindowEditor('renderView', edit=True, writeImage=imagepath)
    
    # restore the node presets    
    # globalsNodes = cmds.renderer( 'mayaSoftware', query=True, globalsNodes=True)
    try:
        cmds.nodePreset(load=('defaultRenderQuality', "ttRestorePreviousDefaultRenderViewPreset"))
    except  LockedAttrError:
        print 'Cannot restore defaultRenderQuality to defaults'
    try:
        cmds.nodePreset(load=('defaultRenderGlobals', "ttRestorePreviousDefaultRenderViewPreset"))
    except LockedAttrError:
        print 'Cannot restore defaultRenderGlobals to defaults'
    try:
        cmds.nodePreset(load=('defaultResolution', "ttRestorePreviousDefaultRenderViewPreset"))
    except LockedAttrError:
        print 'Cannot restore defaultRenderGlobals to defaults'
    # turn the heads-up diplay back on
    cmds.headsUpDisplay(layoutVisibility=True )

    print '%-24s : %.6f seconds' % ('render.snapshots()', (float(time.time())-t0)) 
    return img_dir

def hw(*args, **kwargs):
    t0 = float(time.time())
    try:
        verbose = kwargs['verbose']
    except KeyError:
    	verbose=False
    	if cmds.optionVar(exists='checkmateVerbosity'):
    		verbose = cmds.optionVar(query='checkmateVerbosity')
    else:
        pass

    scenefilename = cmds.file(query=True, sn=True, shn=True)
    root, ext = os.path.splitext(scenefilename)
    fullscenepath = cmds.file(query=True, sn=True, shn=False)
    fullscenedirname = os.path.dirname(fullscenepath)
    reportname = ''.join([root, ext.replace('.','_')])
    img_dir = os.path.join(fullscenedirname,reportname)

    print "save HW rendered images to : %s" % img_dir
        
    # before we render, save render globals presets
    cmds.nodePreset(save=('defaultRenderQuality', "ttRestorePreviousDefaultRenderViewPreset"))
    cmds.nodePreset(save=('defaultRenderGlobals', "ttRestorePreviousDefaultRenderViewPreset"))
    cmds.nodePreset(save=('defaultResolution', "ttRestorePreviousDefaultRenderViewPreset"))

    # override the user settings
    cmds.setAttr("defaultRenderGlobals.imageFormat",32)
    ext = ".png"
    # set resolution ot 320x240
    cmds.setAttr("defaultResolution.width", 640)
    cmds.setAttr("defaultResolution.height", 480)
    cmds.setAttr('defaultResolution.deviceAspectRatio', (float(320)/float(240)))
    
    # set file format to png
    cmds.setAttr("defaultRenderGlobals.imageFormat", 32)
    ext = '.png'
    cmds.setAttr("defaultRenderGlobals.outFormatControl", 0) # default name.ext
    cmds.setAttr("defaultRenderGlobals.animation", False)
    
    # cmds.setAttr('defaultRenderGlobals.imageFilePrefix', "../<Camera>", type="string")
    cmds.setAttr('defaultRenderGlobals.imageFilePrefix', "<Camera>", type="string")
    
    cmds.workspace(fileRule=["images", img_dir])
    print 'save rendered images to : %s' % img_dir
    cmds.hwRender(currentFrame=True, cam='top', edgeAntiAliasing=[2,4], fullRenderSupport=True)
    cmds.hwRender(currentFrame=True, cam='persp', edgeAntiAliasing=[2,16], fullRenderSupport=True)
    cmds.hwRender(currentFrame=True, cam='front', edgeAntiAliasing=[2,16], fullRenderSupport=True)
    cmds.hwRender(currentFrame=True, cam='side', edgeAntiAliasing=[2,16], fullRenderSupport=True)
    
    # move rendererd images from the default project images dir to the report dir
    sourcedir = os.path.join(cmds.workspace( q=True, rd=True ), cmds.workspace(fileRuleEntry="images"))
    targetdir = img_dir
    print 'from : ', sourcedir
    print 'to   : ', targetdir
    
    #for img in ['side.png', 'front.png', 'persp.png', 'top.png'] :
    #    os.rename(os.path.join(sourcedir, img),  os.path.join(targetdir, img))

 
    print '%-24s : %.6f seconds' % ('render.hw()', (float(time.time())-t0)) 
    return img_dir

