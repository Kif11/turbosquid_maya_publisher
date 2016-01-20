# standard library imports

import time

# related third party imports

#local application/library specific imports
from maya import cmds as cmds
from maya import mel as mel

# Utility function to help find hierarchies
def find_transformbytype(nodetype):
    try:
        L = cmds.listRelatives(cmds.ls(type=nodetype), parent=True)
    except TypeError:
        L = []
    return L
# Utility
def find_transformswithoutparents():
    # transforms to ignore
    ignore = find_transformbytype('camera')
    ignore.extend(find_transformbytype('light'))
    # transforms we'll consider
    transforms = [x for x in cmds.ls(transforms=True) if not x in ignore]
    return  [x for x in transforms if not (cmds.listRelatives(x, parent=True))]
         
# find out if the scene has hierarchy 
def run():
    """ This test fails if the number of top-level transforms is more than 1. 
    For each top level node in the scene hierarchy, it returns the number of 
    nodes of each nodetype that are its children. 
    ---
    run() -> boolean, dict
    """
    t0 = time.time()
    D = {}
    result = False
    for root in find_transformswithoutparents():
        d = {}
        l = cmds.listRelatives(root, allDescendents=True, fullPath=True)
        if l:
            for i in l:
                    nodetype = cmds.nodeType(i)
                    d[nodetype] = d.get(nodetype, 0) + 1
            D[root] = d
    if len(D.keys()) > 1:
        result = True
    print '%-24s : %.6f seconds' % ('xforms.hierarchy.run()', time.time()-t0)
    return result, D
        


