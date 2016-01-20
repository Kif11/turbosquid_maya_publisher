import os
import tempfile

def read():
    result = False
    Lrequires = []
    Lwarnings = []
    Lerrors = []
    
    scriptEditorLog = os.path.join(tempfile.gettempdir(), 'scriptEditor.log')
    print 'read error log from ', scriptEditorLog
    
    try:
        openfile = open(scriptEditorLog, 'r')
    except IOError:
        print 'can\'t find the error log'
        pass
        #return result, Lrequires, Lwarnings, Lerrors
        
    lines = openfile.readlines()
    # check for requires statements in the log
    requires = map((lambda x: 'requires' in x), lines)  
    if True in requires:
        # find all True in requires append the lines with corresponding index to list 
        i = -1
        try:
            while True:
                i = requires.index(True, i+1)
                Lrequires.append(lines[i])
                #print '\t', lines[i]
        # stop when we reach the end of the list
        except ValueError:
                pass                  
    warnings = map((lambda x: 'Warning:' in x), lines)
    if True in warnings:
        result = True
        i = -1
        try:
            while True:
                i = warnings.index(True, i+1)
                Lwarnings.append(lines[i])
                #print '\t', lines[i]
        # stop when we reach the end of the list
        except ValueError:
                pass
                
    errors = map((lambda x: 'Error:' in x), lines)
    if True in errors:    
        result = True
        i = -1
        try:
            while True:
                i = errors.index(True, i+1)
                Lerrors.append(lines[i])
        except ValueError:
                pass
    # close the log file
    openfile.close() 
    # os.remove(scriptEditorLog)
    print 'results of read error log are'
    print result, Lrequires, Lwarnings, Lerrors
    print 'return the results'
    return result, Lrequires, Lwarnings, Lerrors

if __name__ == '__main__' :
    read()