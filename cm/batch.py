""" This module provides the batch function that can be run from a commandline. 
It finds scenes and launches mayapy as a subprocess to load scene files and 
create a report. 

The cm package should be installed in Maya's python site-packages, so that 
mayapy has acces to it.

Example: 
mayapy -m cm.batch ./
"""
# standard library imports
import os
import sys
import getopt
import re
import subprocess
import platform
import tempfile

# related third party imports

# local application/library specific imports
import cm
import cm.utils

def main(argv):  

    _verbose = False
    global _sub 
    _sub = False
       
    if platform.system() == 'Darwin':
        mayapy = 'mayapy'
    elif platform.system() == 'Windows':
        mayapy = 'mayapy.exe'
  
    searchpath = os.curdir # default to currrent dir in case no dir specified   
    try:                                
        opts, args = getopt.getopt(argv, "vsd:rq", ["verbose", "sub", "dir=", "render", "quiet"]) 
    except getopt.GetoptError:           
        usage()                          
        sys.exit(2)  
        
    # by default 
    # don't print verbose messages
    _verbose= False
    # do not hw render snapshots
    _render = False
    # shpw reports
    _quiet = False
    # do not search subdirectories
    _sub = False
    # don't look for directories
    _dir = None
                            
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-v", "--verbose"):
            _verbose = True
            print 'Verbose is ', _verbose and "ON" or "OFF"
            
        elif opt in ("-s", "--sub"):
            _sub = True
            print 'Include subdirectories is ', _sub and "ON" or "OFF"
            
        elif opt in ("-d", "--dir"):
            _dir = True
            searchpath = arg
            print 'Searching %s\n' % searchpath

        elif opt in ("-r", "--render"):
            _render = True
            print 'Batch rendering is ', _render and "ON" or "OFF"
            
        elif opt in ("-q", "--quiet"):
            _quiet = True
            print 'Show html report is ', _quiet and "OFF" or "ON"
            
    scenefiles = []
    # match filenames ending in .ma or .mb
    exp = ".*\.m[a-b]$"    
    if _sub:
        for root, dirs, files in os.walk(searchpath):
            for f in files:
                if (re.compile(exp).match(f)) and  True or False:
                    scenefiles.append(os.path.join(root, f))
    else:
        files = os.listdir(searchpath)
        for f in files:
            if (re.compile(exp).match(f)) and  True or False:
                scenefiles.append(os.path.join(searchpath, f))    

    print scenefiles or 'no scene files found in %s' % searchpath
    
    scriptpath =  'cm.utils.loadmayascenefile'
    
    _renderopt = _render and '-r' or None
    _quietopt = _quiet and '-q' or None
    _diropt = _dir and '-d' or None
    
    
    for scenefile in scenefiles:
        
        #cmd = ''.join([mayapy,  ' ',  '-m', ' ', scriptpath, ' ', _renderopt, ' ', _quietopt, ' ', scenefile])
        #print "We're goint to try to run: "
        #print cmd
        
        if _renderopt and _quietopt:
            p = subprocess.call([mayapy, "-m", scriptpath, _renderopt, _quietopt, scenefile])
        elif _quietopt:
            p = subprocess.call([mayapy, "-m", scriptpath, _quietopt, scenefile])
        elif _renderopt:
            p = subprocess.call([mayapy, "-m", scriptpath, _renderopt, scenefile])
        else:
            p = subprocess.call([mayapy, "-m", scriptpath, scenefile])
       
    return 0
                     
def usage():
    print 'Usage: %s [ <options> ] \n\
    \n\
    <options> are any of :\n\
    -h/--help           help (this message)\n\
    -d/--dir directory  directory\n\
    -v/--verbose        verbose\n\
    -s/--sub            include subdirectories\n\
    -r/--render         enable hardware render\n\
    -q/--quiet          don\'t show reports' % sys.argv[0]
    
if __name__ == "__main__":
    print 'running %s in standalone mode' % sys.argv[0]
    main(sys.argv[1:])

else:
    print 'this module should be run in standalone mode'
