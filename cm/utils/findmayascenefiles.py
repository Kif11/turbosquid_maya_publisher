import os
import sys
import getopt
import re
import subprocess

def main(argv):  
    """ find maya scene files in direcory
    """
    
    global _verbose 
    _verbose = False
    global _sub 
    _sub = False
    
    print "fuuuuuk.."
#    if os.name == 'mac' :
#        sys.path.append('/Applications/Autodesk/maya2011/Maya.app/Contents/bin/')         
#        mayapy = '/Applications/Autodesk/maya2011/Maya.app/Contents/bin/mayapy'
#        scriptpath = "/Users/michiel/Documents/checkmate/scripts/loadmayascenefile.py"
#    if os.name == 'nt':
#        mayapy = 'mayapy.exe'
#        scriptpath = 'Y:\\Documents\\checkmate\\scripts\\loadmayascenefile.py'
#    
    scriptpath = '' 
    print 'script path:', scriptpath

    searchpath = os.curdir    
    try:                                
        opts, args = getopt.getopt(argv, "vsd:", ["verbose", "sub", "dir=", ]) 
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
            
        elif opt in ("-s", "--sub"):
            _sub = True
            print 'include subdirectories is ', _sub and "ON" or "OFF"
            
        elif opt in ("-d", "--dir"):
            searchpath = arg
            print 'Searching %s\n' % searchpath

    scenefiles = []
    exp = ".*\.m[a-b]$"    
    if _sub:
        for root, dirs, files in os.walk(searchpath):
            for f in files:
                if (re.compile(exp).match(f)) and  True or False:
                    #print '%s' %  os.path.join(root, f)
                    scenefiles.append(os.path.join(root, f))
    else:
        files = os.listdir(searchpath)
        for f in files:
            if (re.compile(exp).match(f)) and  True or False:
                #print '%s' % os.path.join(searchpath, f)
                scenefiles.append(os.path.join(searchpath, f))    

    print scenefiles
    
    
    for scenefile in scenefiles:
        # p = subprocess.Popen(["ls", "-al", scenefile], bufsize=0)  
        #p = subprocess.Popen([mayapy,  "/Users/michiel/Documents/checkmate/scripts/loadmayascenefile.py", "-v", scenefile], bufsize=-1)
        print mayapy,  scriptpath, "-v", scenefile
        p = subprocess.call([mayapy,  scriptpath, "-v", scenefile])
        
    return 0
                     
def usage():
    print 'Usage: sys.argv[0] [ <options> ] \n\
    \n\
    <options> are any of :\n\
    -d --dir     dir\n\
    -v --verbose verbose\n\
    -s --sub     subdir\n'
    
if __name__ == "__main__":
    print 'running in standalone mode'
    main(sys.argv[1:])
    