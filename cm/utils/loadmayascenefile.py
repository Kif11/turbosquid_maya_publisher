""" This module provides the loadmayascenefile function that can be run from a 
commandline. It opens a scene, creates and optionally displays a .html 
report. 

The cm package should be installed in Maya's python site-packages, so that 
mayapy has acces to it.

Examples: 
mayapy -m cm.utils.loadmayascenefile -q ./foo.ma
mayapy -m cm.utils.loadmayascenefile -r ./foo.ma
"""

# standard library imports
import os
import sys
import getopt
import re
import tempfile

# related third party imports

# local application/library specific imports
import maya.standalone
import cm
import cm.utils
import cm.report.report as report

maya.standalone.initialize( name='python' )
from maya import cmds as cmds

def main(argv):
    """ Load a maya scene file
    argumments
    -h/help
    -v/verbose
    -r/render 
    -q/quiet  
    """
    # default settings
    _render = False
    _quiet = False
    
    try:                                
        opts, args = getopt.getopt(argv, 
            "hvrq", 
            ["help", "verbose", "render", "quiet"]) 
    except getopt.GetoptError:           
        usage()                          
        sys.exit(2)                     
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-v", "--verbose"):
            _verbose = True
            print 'verbose is ', _verbose and "ON" or "OFF"

        elif opt in ("-r", "--render"):
            _render = True
            print 'Batch rendering is ',  _render and "ON" or "OFF"
            
        elif opt in ("-q", "--quiet"):
            _quiet = True
            print 'Show html report is ', _quiet and "OFF" or "ON"
            
    scenefile = "".join(args)
    cmds.file(scenefile, force=True, open=True)
    r=report.Report('current', render=_render)
    r.writeHTML()
    if not _quiet:
        r.showHTML()
    quit()
    
def usage():
    print 'Usage: %s [ <options> ] \n\
    \n\
    <options> are any of :\n\
    -h/--help           help (this message)\n\
    -v/--verbose        verbose\n\
    -r/--render         enable hardware render\n\
    -q/--quiet          don\'t show reports' % sys.argv[0]
        
if __name__ == "__main__":
    print 'running %s in batch mode' % sys.argv[0]
    print sys.argv[0:]
    main(sys.argv[1:]) 

