from maya import cmds as cmds

def find_objects():
    """returns a list of transform nodes
    find_objects() -> list
    """
    return cmds.ls(transforms=True)
    
def find_parents():
    """ finds all transforms in the scene that are parents of a transforms
    Note that excluding the default nodes [u'front', u'persp', u'side', u'top'] may not
    be desirable if parenting an object to the default nodes is allowed
    find_parents -> list
    """
    t0 = float(time.time())
    # all transforms
    alltransforms = cmds.ls(transforms=True)
    # transforms to ignore
    ignore = [u'front', u'persp', u'side', u'top']
    # transforms we'll consider
    #transforms = [x for x in alltransforms if not x in ignore]
    transforms = alltransforms
    # get a list of all the parent of the items in the list
    L = map(lambda x : (cmds.listRelatives(x, parent=True)) , transforms )
    # some transforms have no parent, and listRelatives gives None
    # remove the None entries, leaving a list of transforms that are parents
    # listRelatives also return a list, not a string so take [0]
    parents = [x[0] for x in L if x != None]
    print '%-24s : %.6f seconds' % (inspect.getframeinfo(inspect.currentframe())[2], (float(time.time())-t0)) 
    return parents

def find_children():
    """ finds all transforms in the scene that are children of a transform 
    """
    t0 = float(time.time())
    # all transforms
    alltransforms = cmds.ls(transforms=True)
    # transforms to ignore
    ignore = [u'front', u'persp', u'side', u'top']
    # transforms we'll consider
    # transforms = [x for x in alltransforms if not x in ignore]
    transforms = alltransforms
    # get a list of all the children of the items in the list
    L0 = map(lambda x : (cmds.ls(x, type='transform')) , transforms)
    L = map(lambda x : (cmds.listRelatives(x, children=True, type='transform')) , transforms)
    # Ll is a list of lists
    Lf = [x for x in L if x != None]
    # flatten the list
    children = [item for sublist in Lf for item in sublist]
    return children

def find_roots():
    """ find all root nodes (nodes that are parents but not children)
    ex. cmds.select(find_root_transforms())
    find_roots() -> list
    """
    t0 = float(time.time())
    # transforms to ignore
    ignore = [u'front', u'persp', u'side', u'top']
    # transforms we'll consider
    transforms = [x for x in cmds.ls(transforms=True) if not x in ignore]
    print '%-24s : %.6f seconds' % (inspect.getframeinfo(inspect.currentframe())[2], (float(time.time())-t0)) 
    return  [x for x in transforms if not (cmds.listRelatives(x, parent=True))]

def texturefilenames():
    files = cmds.ls(typ='file')
    Dtfn = {}
    for file in files:
        Dtfn[file] =    cmds.getAttr('%s.fileTextureName' %file)
    return Dtfn
    