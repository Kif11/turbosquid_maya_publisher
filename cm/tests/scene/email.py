import re
import os

from maya import cmds as cmds

def run(*args, **kwargs):
    """This tests finds an email address in a file called README.txt or
    some variation thereof. The test fails if it can find an email 
    adress in a README in the same directory as the scene file
    ---
    valid_email()-> boolean, string
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
    else:
        pass                   
    result = False
    email = ''
    filename = cmds.file(query=True, sn=True, shn=False)
    (dir) = os.path.dirname(filename) 
    # try a number of variations of the readmes
    readme = ''    
    for i  in ['README.txt', 'README', 'readme.txt', 'readme' ]:
        path = os.path.join(dir, i)
        # print path
        if  os.path.isfile(path):
            print 'found ', os.path.abspath(path)
            readme = path
            break
        else:
            continue
    if not os.path.isfile(readme) : 
        if verbose:
            print 'there is no readme', readme 
        return False, None, None
    else:
        try: 
            input = open(readme,'r')
        except IOError:
            print "Can't open %s for read" % readme
            return True, None
        while 1:
            line = input.readline()
            print line
            if '@' in line:
                words = line.split()
                for word in words:
                    word = word.replace('<', '')
                    word = word.replace('>', '')
                    # print word
                    #m = re.match("^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$", word)
                    m = re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", word)
                    if m != None:
                        result = True
                        email = m.group()
            if not line:
                break
            pass
        input.close()
        
    return result, email, os.path.abspath(path)

