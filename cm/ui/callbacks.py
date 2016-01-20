from maya import cmds as cmds

def verbosityCB():
    if not cmds.optionVar(exists='checkmateVerbosity'):
        cmds.optionVar(iv=('checkmateVerbosity', 0))
    verbose = not cmds.optionVar( query='checkmateVerbosity' )
    cmds.optionVar(iv=('checkmateVerbosity', verbose))
    if verbose:
        print "Verbose feedback is ON"
    else:
        print 'Verbose feedback is OFF'
    cmds.menuItem('verbosityItem', edit=True, checkBox=cmds.optionVar(query='checkmateVerbosity'))  

def includesubdirCB():
    if not cmds.optionVar(exists='includeSubDir'):
        cmds.optionVar(iv=('includeSubDir', 0))
    includesubdir = not cmds.optionVar( query='includeSubDir' )
    cmds.optionVar(iv=('includeSubDir', includesubdir))
    if includesubdir:
        print "Include Sub-directory is ON"
    else:
        print 'Include Sub-directory is OFF'
    cmds.menuItem('includesubdirItem', edit=True, checkBox=cmds.optionVar(query='includeSubDir'))  
     