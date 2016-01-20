from maya import cmds as cmds
from maya import mel as mel




def run(*args, **kwargs):
    """ prepare the scene for the tests
    converts scene to use centimeters
    set the grid to the default
    
    """
    valid_kwargs = ['verbose']
    for k, v in kwargs.iteritems():
        if k not in valid_kwargs:
            raise TypeError("Invalid keyword argument %s" % k)
    # verbose defaults to False if verbose option not set in menu or set 
    # as cmdline argument
     
    try:
        verbose = kwargs['verbose']
    except KeyError:
        verbose = False 
    	if cmds.optionVar(exists='checkmateVerbosity'):
    		verbose = cmds.optionVar(query='checkmateVerbosity')
    else:
        verbose = False       
    batch = cmds.about(batch=True)    
    # get the name of the script Editor's output control
    from maya import mel as mel
    # Turn off Echo All Commands in the Script Editor  
    # Disable Stack Tracevin the Script Editor  
    # Turn off Line Numbers in errors in the Script Editor  
    # Reset the grid
    # Set the background color
    # Turn off the heads-up displays
    # Switch to wrireframe mode
    # Close all windows (except main)
    # Close ChannelBox, Attribute Editor and Outliner ()
    
    if not batch:
        try:
            gCommandReporter = mel.eval("proc string f(string $g){return $g;}f($gCommandReporter);")
        except RuntimeError:
            gCommandReporter = ''
            pass
        try:
            cmds.cmdScrollFieldReporter(gCommandReporter, 
                edit=True, 
                echoAllCommands=False,
                lineNumbers=True,
                stackTrace=True,
                suppressResults=False,
                suppressInfo=False,
                suppressWarnings=False,
                suppressErrors=False,
                suppressStackTrace=False,
                )
        except RuntimeError:
            if verbose:
                print 'No Script Editor'
            pass
    
    # convert scene to cm to fix crashes in nearestnormal
    cmds.currentUnit(linear='cm')
