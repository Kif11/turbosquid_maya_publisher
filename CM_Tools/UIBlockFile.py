import maya.cmds as cmds

class UIBlockClass():
    #input format [types,label,sepStyle,name], parent
    def __init__(self, Parent, Configuration):
        self.Parent = Parent
        self.Configuration = Configuration
        self.CreateUIBlock()
    
    def CreateUIBlock(self):
        for i in self.Configuration:
            if i[0] == "text":
                if i[2] != "DoNotCreate":cmds.separator(i[3] + "TSep" ,p = self.Parent, w = 309, h = 15, style = i[2], hr = True)
                cmds.text( i[3] + "Text", p = self.Parent, label = i[1],font = "boldLabelFont")
            elif i[0] == "button":
                if i[2] != "DoNotCreate":cmds.separator( i[3] + "BSep", p = self.Parent, w = 309, h = 15, style = i[2], hr = True)
                cmds.button(i[3] + "Button", p = self.Parent, label = i[1])
            elif i[0] == "checkbox":
                if i[2] != "DoNotCreate":cmds.separator( i[3] + "CSep", p = self.Parent, w = 309, h = 15, style = i[2], hr = True)
                cmds.checkBox(i[3] + "CheckBox", p = self.Parent, label = i[1], align='right')
            elif i[0] == "textfield":
                if i[1] != "DoNotCreate":cmds.separator( i[2] + "nSep", p = self.Parent, w = 309, h = 15, style = i[1], hr = True)
                cmds.textField(i[2] + "TextField", p = self.Parent)
            elif i[0] == "textscrolllist":
                if i[2] != "DoNotCreate":cmds.separator( i[3] + "nSep", p = self.Parent, w = 309, h = 15, style = i[2], hr = True)
                cmds.textScrollList(i[3] + "TextScrollList", p = self.Parent,  numberOfRows = i[1], allowMultiSelection = i[4],append = i[5], selectItem = i[6], showIndexedItem = i[7], h = i[8] )

    def ChangeBlockVisibility(self, Visibility):
        for i in self.Configuration:
            if i[0] == "text":
                if i[2] != "DoNotCreate":cmds.separator(i[3] + "TSep", edit = True, visible = Visibility)
                cmds.text( i[3] + "Text", edit = True, visible = Visibility)
            elif i[0] == "button":
                if i[2] != "DoNotCreate":cmds.separator( i[3] + "BSep", edit = True, visible = Visibility)
                cmds.button(i[3] + "Button", edit = True, visible = Visibility)
            elif i[0] == "checkbox":
                if i[2] != "DoNotCreate":cmds.separator( i[3] + "CSep", edit = True, visible = Visibility)
                cmds.checkBox(i[3] + "CheckBox", edit = True, visible = Visibility)
            elif i[0] == "textfield":
                if i[1] != "DoNotCreate":cmds.separator( i[2] + "nSep", edit = True, visible = Visibility)
                cmds.textField(i[2] + "TextField", edit = True, visible = Visibility)
            elif i[0] == "textscrolllist":
                if i[2] != "DoNotCreate":cmds.separator( i[3] + "nSep", edit = True, visible = Visibility)
                cmds.textScrollList(i[3] + "TextScrollList", edit = True, visible = Visibility )
        
    