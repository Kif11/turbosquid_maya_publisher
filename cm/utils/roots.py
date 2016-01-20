import time 
from maya import cmds as cmds

def get():
    """ find all root nodes (nodes that are parents but not children)
    ex. cmds.select(find_root_transforms())
    find_roots() -> list
    """
    t0 = float(time.time())
    # transforms to ignore
    ignore = [u'front', u'persp', u'side', u'top']
    # transforms we'll consider
    transforms = [x for x in cmds.ls(transforms=True) if not x in ignore]
    print '%-24s : %.6f seconds' % ('roots.get()', (float(time.time())-t0)) 
    return  [x for x in transforms if not (cmds.listRelatives(x, parent=True))]

