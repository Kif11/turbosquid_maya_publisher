from maya import cmds as cmds

def isEmpty(mesh):
    try:
        numfaces = cmds.polyEvaluate(mesh,face=True)
    except IndexError:
        numfaces=0
        pass   
    return False or numfaces == 0

def isShaveMesh(mesh):
    attr = '%s.message' % mesh
    try:
        dest = cmds.connectionInfo(attr, destinationFromSource=True)[0].split('.')[1]
    except IndexError:
        dest=None
        pass   
    return False or dest == 'dn'
    