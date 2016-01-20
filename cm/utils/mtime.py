def get():
    from maya import cmds as cmds
    import os
    import time
    from datetime import datetime
    f = cmds.file(q=True, sn=True)
    t= os.path.getmtime(f)
    dt = datetime.fromtimestamp(t)
    df = dt.strftime("%Y-%m-%d %H:%M:%S")
    return df