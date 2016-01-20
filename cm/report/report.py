""" report
"""

# standard library imports
import os
import time
import getpass
import re

# related third party imports

# local application/library specific imports
from maya import cmds as cmds
import cm.tests.components.f.area; reload(cm.tests.components.f.area)
import cm.tests.components.f.lamina; reload(cm.tests.components.f.lamina)
import cm.tests.components.f.normals; reload(cm.tests.components.f.normals)
import cm.tests.components.f.size; reload(cm.tests.components.f.size)

import cm.tests.components.uv.coincident; reload(cm.tests.components.uv.coincident)
import cm.tests.components.uv.missing; reload(cm.tests.components.uv.missing)
import cm.tests.components.uv.range; reload(cm.tests.components.uv.range)

import cm.tests.components.vtx.coincident; reload(cm.tests.components.vtx.coincident)
import cm.tests.components.vtx.isolated; reload(cm.tests.components.vtx.isolated)

import cm.tests.scene.email; reload(cm.tests.scene.email)
import cm.tests.scene.missing; reload(cm.tests.scene.missing)
import cm.tests.scene.names; reload(cm.tests.scene.names)
import cm.tests.scene.missing; reload(cm.tests.scene.missing)

import cm.tests.shapes.history; reload(cm.tests.shapes.history)
import cm.tests.shapes.material; reload(cm.tests.shapes.material)
import cm.tests.shapes.mesh; reload(cm.tests.shapes.mesh)

import cm.tests.xforms.centered; reload(cm.tests.xforms.centered)
import cm.tests.xforms.hidden; reload(cm.tests.xforms.hidden)
import cm.tests.xforms.hierarchy; reload(cm.tests.xforms.hierarchy)
import cm.tests.xforms.identity; reload(cm.tests.xforms.identity)

import cm.stats.bbox; reload(cm.stats.bbox)
import cm.stats.poly; reload(cm.stats.poly)

import cm.utils.render; reload(cm.utils.render)
import cm.utils.find; reload(cm.utils.find)
import cm.utils.mtime; reload(cm.utils.mtime)
import cm.utils.setup; reload(cm.utils.setup)
import cm.utils.open; reload(cm.utils.open)
import cm.utils.errorlog; reload(cm.utils.errorlog)

class Report(object):
    def __init__(self, *args, **kwargs):
        self.start = time.time()
        self._dorender=True # render snapshot or do hw renders by default
        try:
            self._dorender = kwargs['render']
        except KeyError:
            	self._dorender=True
        
        # check for email in README
        self.results_valid_email = cm.tests.scene.email.run()
        if args[0] == 'current':
            #self.results_log = cm.utils.errorlog.read()
            self.results_log = [False, [], [], []]
            #print self.results_log
        elif args[0] == 'open':
            self.results_log = cm.utils.open.fileWithLog()
        
        _userWorkspaceDir = cmds.internalVar(userWorkspaceDir=True)
        self.title = ''
        
        self.scene = cmds.file(query=True, sn=True, shn=True) or 'unknown.mb'
        # 'scene.ma'
        (self.root, self.ext) = os.path.splitext(self.scene) 
        # Result: (u'scene', u'.ma') # 
        self.fullscenepath = cmds.file(query=True, sn=True, shn=False) or 'unknown.mb'
        # Result: /Users/michiel/Documents/maya/projects/checkMateTests/scenes/scene.ma # 
        self.fullscenedirname = os.path.dirname(self.fullscenepath)
        # Result: /Users/michiel/Documents/maya/projects/checkMateTests/scenes # 
        if self.fullscenedirname == '':
            self.fullscenedirname = os.path.join(_userWorkspaceDir, 'reports')
            # Result: /Users/michiel/Documents/maya/projects/reports # 
        self.reportname = ''.join([self.root, self.ext.replace('.','_')])  
        # changed in 0.5 user request to use same directiry as scene file
        #self.report_dir = os.path.join(_userWorkspaceDir, 'reports', self.root)
        # use same direcrory as scene
        self.report_dir =  os.path.join(self.fullscenedirname, self.reportname)
        # make sure this directory exists
        if not os.path.exists(self.report_dir):
            cmds.sysFile(self.report_dir, makeDir=True)
            
        self.htmlfile = ''.join([self.report_dir, '/', self.root, self.ext.replace('.', '_'), '.html'])
       
        self.img_dir = self.report_dir
        # self.img_dir = ''.join([self.report_dir, '/', self.fullroot, self.ext.replace('.', '_')])
        # make sure this directory exists
        if not os.path.exists(self.img_dir):
            cmds.sysFile(self.img_dir, makeDir=True)
        self.url = 'file://%s' % self.htmlfile        
        
        
        self.maya_version = (''.join([cmds.about(application=True), ' ',
            cmds.about(version=True), ' ',
            cmds.about(operatingSystem=True), ' ',
            cmds.about(operatingSystemVersion=True), ' ']))
                    
        try:
            self.mtime = cm.utils.mtime.get()
        except OSError:
            self.mtime = None
            pass

        
        self.creation_date = time.strftime("%Y-%m-%d %H:%M:%S")
        self.user = self.user = getpass.getuser()

        
        # before we do anything, to the scene, set the linear units to centimeters
        cm.utils.setup.run()
        # get the results of the tests
        # make sure to perform the tests in order if something needs to be fixed 
        # 
        self.results_history = cm.tests.shapes.history.run()
        # delete all history
        if self.results_history[0]:
            cmds.delete(all=True,constructionHistory=True)
            
        self.results_zeroareafaces = cm.tests.components.f.area.run()
        # delete zero area faces before proceeding with normals test
        try:
            cmds.delete(self.results_zeroareafaces[2])
        except TypeError:
            pass
        
        
        self.results_ngons = cm.tests.components.f.size.run()
        
        self.results_centeredatorigin = cm.tests.xforms.centered.run()
        self.results_nonzerotransforms = cm.tests.xforms.identity.run()
        self.results_polyvertexcount = cm.stats.poly.run(faces=0, vertices=0, verbose=False)
        self.results_sceneboundingbox = cm.stats.bbox.run()
        self.results_flippednormals = cm.tests.components.f.normals.run()
        self.results_isolatedvertices2 = cm.tests.components.vtx.isolated.run()
        self.results_coincidentvertices2 = cm.tests.components.vtx.coincident.run()
        self.results_laminafaces = cm.tests.components.f.lamina.run()
        self.results_defaultnames = cm.tests.scene.names.run()
        self.results_nohierarchy = cm.tests.xforms.hierarchy.run()
        self.results_hiddenobjects = cm.tests.xforms.hidden.run()
        self.results_missingfiles = cm.tests.scene.missing.run()
        self.results_nomaterial = cm.tests.shapes.material.run()
        self.results_defaulttexturenames = cm.tests.scene.names.run(type='textures')
        self.results_defaultmaterialnames = cm.tests.scene.names.run(type='materials')
        
        self.results_missinguvmaps =cm.tests.components.uv.missing.run()
        self.results_overlappinguvs = cm.tests.components.uv.coincident.run()
        self.results_uvbbox = cm.tests.components.uv.range.run()

        # get the compound results of tests with subtests
        self.results_centeredandnonzerotransforms = self.results_centeredatorigin[0] or self.results_nonzerotransforms[0]
        self.results_namingorganization = self.results_defaultnames[0] or self.results_nohierarchy[0]
        self.results_uvquality = self.results_missinguvmaps[0] or self.results_overlappinguvs[0] or self.results_uvbbox[0]
        self.ftime = time.strftime('%H:%M:%S', time.gmtime(float(time.time())-self.start))
        print '%-24s : %s' % ('TOTAL', self.ftime)
        
    def txt2html(self, text):
        """convert to html entities"""
        D = {"&": "&amp;", '"': "&quot;", "'": "&apos;", ">": "&gt;", "<": "&lt;",}
        return "".join(D.get(c,c) for c in text)
  
  
      
    def writeHTML(self, *args, **kwargs):
        """ write a .html report
        attempts to open the file
        returns path to the file
        
        writeHTML() -> path
        """
        
        valid_kwargs = ['verbose']
        for k, v in kwargs.iteritems():
            if k not in valid_kwargs:
                raise TypeError("Invalid keyword argument %s" % k)  
        result = False
        err = list()
        verbose = False
        # verbose defaults to False if verbose option not set in menu 
        # or specified in cmdline
        try:
            verbose = kwargs['verbose']
        except KeyError:
            	if cmds.optionVar(exists='tsVerbosity'):
            		verbose = cmds.optionVar(query='tsVerbosity')
        else:
            pass  

        output = ''
        
        # render the snapshots
        if cmds.about(batch=True):
            if self._dorender:
                print 'We\'re in batch mode and render is HW'
                try:
                    cm.utils.render.hw()
                except IOError:
                    print 'failed to perform hw render'
            else:
                pass
            
        else:
            try:
                cm.utils.render.snapshots()
            except IOError:
                print 'failed to render snapshots'        
            
        # write the html file    
        try:
            output = open(self.htmlfile, 'w')
        except IOError:
            print 'Can\'t open %s for write' % self.htmlfile
    

        output.write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">""")
        output.write("""<html xmlns="http://www.w3.org/1999/xhtml">""")
        output.write("""<head>""")
        output.write("""<meta content="text/html; charset=ISO-8859-1" http-equiv="content-type" />""")
        output.write('<title>%s</title>' % self.title)           
        output.write("""<link href="https://www.turbosquid.com/CSS/v32/Global.gz.css" rel="stylesheet" type="text/css" title="styles" />""")
        output.write("""</head>""")
        output.write("""<body>""")
        output.write("""<div id="page-container" style="width: 996px;">""")
        output.write("""<div style="padding: 22px;" id="page-content-inner">""")
        output.write("""<h1>Check-Mate Report for %s</h1>""" % (self.scene))
        # write the first table
        # DATA
        heading = 'About this report'
        t = {'Maya Version': self.maya_version,
            'Maya Path': self.fullscenepath,
            'Scene Modified': self.mtime,
            'Created On': self.creation_date,
            'Created By': self.user,
         }
        heading = '<h2>%s</h2>' % heading
        help = '<p></p>'
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % k)
            table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % t[k])
            table += '        </tr>\n'
        
        table += '    </tbody>\n'
        table += '</table>\n'      
        output.write(heading) 
        output.write(help)  
        output.write(table) 
        ############################################################################
        # 0
        heading = 'Test Results'
        heading = '<h2>%s</h2>' % heading
        table = '<table style=\"text-align: left; width: 100%;" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        # table += '<caption>Overall test results. [Click on links for test details]<br /> </caption>\n'
        table += '    <tbody>\n'
        table += '        <tr>\n'   
        table += '            <th style=\"vertical-align: top; text-align: center; width: 20%%\"></th>\n'
        table += '            <th style=\"vertical-align: top; white-space: nowrap; width: 80%%\">Test</th>\n'
        table += '        </tr>\n'
        
        tests = {'010No Personal Contact Info in readme' : ['#personal', self.results_valid_email[0] and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>'],
                '020No Errors on Opening': ['#errorsonopen', self.results_log[0] and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>'],
                '030Centered and Oriented to Grid' :  ['#notcentered', self.results_centeredandnonzerotransforms and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>'], 
                '040Polycount' : ['#polyvertexcount', self.results_polyvertexcount[0] and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>'], 
                '050Real World Scale' : ['#sceneboundingbox', '-'],
                '060No Ngons - # of Ngons/# of Quads/# of Tris': ['#ngons', self.results_ngons[0] and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>'],
                '070Z-Fighting/Artifacting': ['#artifacting', '-'],
                '080No Zero Area Faces': ['#zerofaces', self.results_zeroareafaces[0] and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>'],
                '081No Reversed Faces': ['#flippednormals', self.results_flippednormals[0] and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>'],
                '090No Isolated Vertices - # of': ['#isolatedvertices', self.results_isolatedvertices2[0] and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>'],
                '100No Overlapping Vertices - # of': ['#coincidentvertices', self.results_coincidentvertices2[0] and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>'],
                '110No Overlapping Faces - # of': ['#laminafaces', self.results_laminafaces[0] and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>'],
                '120Naming/Organization  - non-descriptive names also no hierachy': ['#namingorganization', self.results_namingorganization and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>'], 
                '130History Clear': ['#history', self.results_history[0] and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>'],
                '140No Extra Elements Present in Renders': ['#hiddenobjects', self.results_hiddenobjects[0] and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>'],
                '150Textures/Materials included': ['#missingfiles', self.results_missingfiles[0] and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>'],
                '150Objects with no or default material': ['#nomaterial', self.results_nomaterial[0] and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>'],
                '160Textures Zipped with Model': ['#textureszipped', '-'],
                '170Textures Named - descriptively': ['#texturesnamed', self.results_defaulttexturenames[0] and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>'],
                '180Materials Named - descriptively': ['#materialsnamed', self.results_defaultmaterialnames[0] and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>'],
                '190UV Quality - no stretching, no obvious seams, no flipped or overlapping (stacked) UV\'s': ['#uvquality', self.results_uvquality and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>'],
                   
        }
        for k in sorted(tests.keys()):
            table += '        <tr>\n'
            table += '            <td style="vertical-align: top; text-align: center; padding-right: 20px;">%s</td>\n' % tests[k][1]
            table += '            <td style="vertical-align: top;"><a href="%s">%s</a></td>\n' % (tests[k][0], re.sub('[0-9]', '', k))
            table += '        </tr>\n'
        
        table += '    </tbody>\n'
        table += '</table>\n'
        output.write(heading)   
        output.write(table) 
          
        ############################################################################    
        heading = 'Screenshots'
#        t = {'top': ''.join([self.imgdir, '/', 'top.png']),
#            'persp': ''.join([self.imgdir, '/', 'persp.png']),
#            'front': ''.join([self.imgdir, '/' 'front.png']),
#            'side': ''.join([self.imgdir, '/' 'side.png']),
#            
#            }
        t = {'top': 'top.png',
            'persp': 'persp.png',
            'front': 'front.png',
            'side':  'side.png',
            
            }
        anchor = '<a name=\"%s\">%s</a>' % ('render','')
        heading = '<h2>%s</h2>' % heading
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s</td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; white-space: nowrap;\"> <img style=\"width: 320px; height: 240px;\" alt=\"front\" src=\"%s\" /> </td>\n' % t[k])
            table += '        </tr>\n'
        
        table += '    </tbody>\n'
        table += '</table>\n'      
        output.write(anchor) 
        output.write(heading)   
        output.write(table) 
        ############################################################################
        # 1. No Personal Contact Info in readme
        anchor = '<a name=\"%s\">%s</a>' % ('personal','')
        heading = '<h2>%s</h2>' % '1.  No Personal Contact Info in readme'
        (status,email, file) = self.results_valid_email
        help = ''.join(['<p>', cm.tests.scene.email.run.__doc__.split('---')[0], '</p>'])
        t = {
            '1Result' :  status and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>',
            '2Contact' : '<a href=\"mailto:%s\"> %s </a>' % (email,email),
            '3File' : '%s' % (file)
            }
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % (t[k]))
            table += '        </tr>\n'
        
        table += '    </tbody>\n'
        table += '</table>\n'
        #paragraph = '<p>This is a visual inspection. No automated test exists.</p>'
        output.write(anchor) 
        output.write(heading) 
        output.write(help)
        output.write(table) 

        # '2.  No Errors on Opening'
        (status, requires, warnings, errors) = self.results_log
        anchor = '<a name=\"%s\">%s</a>' % ('errorsonopen','')
        heading = '<h2>%s</h2>' % '2.  No Errors on Opening'
        paragraph = '<p>This secton contains elements from the Script Editor output. A scene will pass this test if the test is run in interactive mode on the current scene, since the scene file is already loaded.</p>'
        t = {
            '01Result' :  status and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>',
            '02Requires' : ''.join([x.replace(';\n', '<br/>\n') for x in requires]),
            '03Warnings' : ''.join([x.replace('\n', '<br/>\n') for x in warnings]),
            '04Errors' : ''.join([x.replace('\n', '<br/>\n') for x in errors]),
            }
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % (t[k]))
            table += '        </tr>\n'
        
        table += '    </tbody>\n'
        table += '</table>\n'
        output.write(anchor) 
        output.write(heading) 
        output.write(paragraph) 
        output.write(table)
        
        # '3.  Centered and Oriented to Grid'
        anchor = '<a name=\"%s\">%s</a>' % ('errorsonopen','')
        heading = '<h2>%s</h2>' % '3.  Centered and Oriented to Grid'
        help = '<p>This test has two parts. 3a Centered, which should be verified visually, and 3b which checks for non-zero transformations. The test passses if Translate XYZ and RotateXYZ are all 0.0 and ScaleXYX are all 1.0 </p>'
        output.write(anchor) 
        output.write(heading) 
        output.write(help) 
       
        # '3a.  Centered'
        #(status, number, selection) = checkmate.is_centeredatorigin()
        (status, number, selection) = self.results_centeredatorigin
        # fix need to generalize
        try: 
            totalgeometryobjects = len(cmds.listRelatives(cmds.ls(geometry=True, noIntermediate=True), parent=True))
        except TypeError: 
            totalgeometryobjects = 0
 
        heading = '3a.  Centered'
        help = ''.join(['<p>', cm.tests.xforms.centered.run.__doc__.split('---')[0], '</p>'])
        
        t = {
            '2Number of objects' : '%d of %d (%.2f%%)' % (number, totalgeometryobjects, (float(number)/float(totalgeometryobjects or 1))*100.0),
            '1Result' :  status and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>',
            '3Selection' : ''.join([x+'<br/>' for x in selection]),
            }
        selection = ''.join(['cmds.select(', str(selection), ')'])
        anchor = '<a name=\"%s\">%s</a>' % ('notcentered','') 
        heading = '<h2>%s</h2>' % heading
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % t[k])
            table += '        </tr>\n'
        
        table += '    </tbody>\n'
        table += '</table>\n'
        output.write(anchor)      
        output.write(heading)
        output.write(help)   
        output.write(table) 
        
        # 3b
        #(status, number, selection) = checkmate.has_nonzerotransforms()
        (status, number, selection) = self.results_nonzerotransforms
        # totalgeometryobjects = len(cmds.listRelatives(cmds.ls(geometry=True, noIntermediate=True), parent=True))
        heading = '3b. Non-zero transforms'
        help = ''.join(['<p>', cm.tests.xforms.identity.run.__doc__.split('---')[0], '</p>'])
        selection = ''.join(['cmds.select(', str(selection), ')'])
        t = {
            '2Number of objects' : '%d of %d (%.2f%%)' % (number, totalgeometryobjects, (float(number)/float(totalgeometryobjects or 1))*100.0),
            '1Result' :  status and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>',
            '3Selection' : selection,
            }
        
        anchor = '<a name=\"%s\">%s</a>' % ('nonzerotransforms','')
        heading = '<h2>%s</h2>' % heading
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % t[k])
            table += '        </tr>\n'
        
        table += '    </tbody>\n'
        table += '</table>\n'
        output.write(anchor)        
        output.write(heading)   
        output.write(help)
        output.write(table) 
        
        # '04.  Polycount'
        #(status, Dpolycount, Lerr) = checkmate.polyvertexcount(vertices=0, faces=0, verbose=False)
        (status, Dpolycount, Lerr) = self.results_polyvertexcount
        heading = '04.  Polycount'
        help = '<p></p>' 
        help = ''.join(['<p>', cm.stats.poly.run.__doc__.split('---')[0], '</p>'])
        s = ''
        for e in ["".join([err,'<br />']) for sublist in Lerr for err in sublist] :
            s = ''.join([s, e])
        t = {
            #'Number' :  len(Dpolycount.keys()),
            '00Result' :  status and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>',
            #'VertexComponent' : Dpolycount['vertexComponent'],
            '06Shell' : Dpolycount['shell'],
            '04Triangle' : Dpolycount['triangle'],
            #'FaceComponent' : Dpolycount['faceComponent'],
            '01Vertex' : Dpolycount['vertex'],
            '03Face' : Dpolycount['face'],
            #'TriangleComponent' : Dpolycount['triangleComponent'],
            '02Edge' : Dpolycount['edge'],
            '05UVcoord' : Dpolycount['uvcoord'],
            #'UVcomponent' : Dpolycount['uvComponent'],
            #'EdgeComponent' : Dpolycount['edgeComponent'],
            #'08Tris' : '%d of %d (%.2f%%)' % (Dpolycount['tris'], Dpolycount['face'], float(Dpolycount['tris'])/float(Dpolycount['face'])*100.0),
            #'09Quads' : '%d of %d (%.2f%%)' % (Dpolycount['quads'], Dpolycount['face'], float(Dpolycount['quads'])/float(Dpolycount['face'])*100.0),
            #'10N-Sided' : '%d of %d (%.2f%%)' % (Dpolycount['n-sided'], Dpolycount['face'], float(Dpolycount['n-sided'])/float(Dpolycount['face'])*100.0),
            '07Errors:' : s,
            }
        
        selection = ''.join(['cmds.select(', str(selection), ')'])
        anchor = '<a name=\"%s\">%s</a>' % ('polyvertexcount','')
        heading = '<h2>%s</h2>' % heading
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % t[k])
            table += '        </tr>\n'
        
        table += '    </tbody>\n'
        table += '</table>\n'      
        output.write(anchor) 
           
        output.write(heading)   
        output.write(help)
        output.write(table) 

        # '05.  Real World Scale'
        (units, bbMinX, bbMinY, bbMinZ, bbMaxX, bbMaxY, bbMaxZ, centerX, centerY, centerZ, width, height, depth) = self.results_sceneboundingbox
        heading = '05.  Real World Scale'
        help = ''.join(['<p>', cm.stats.bbox.run.__doc__.split('---')[0], '</p>'])
        t = {
            # prefix labels with ints to do an alphanumeric sort, the numbers 
            # are removed  with re.sub('[0-9]', '', k) later
            '4Min' : ('%12.3f %12.3f %12.3f ' % (bbMinX, bbMinY, bbMinZ)).replace(' ', '&nbsp;'),
            '5Max' : ('%12.3f %12.3f %12.3f ' % (bbMaxX, bbMaxY, bbMaxZ)).replace(' ', '&nbsp;'),
            '6Center' : ('%12.3f %12.3f %12.3f ' % (centerX, centerY, centerZ)).replace(' ', '&nbsp;'),
            '1Width': ('%12.3f %s' % (width, units)).replace(' ', '&nbsp;'),
            '2Height': ('%12.3f %s' % (height, units)).replace(' ', '&nbsp;'),
            '3Depth': ('%12.3f %s' % (depth, units)).replace(' ', '&nbsp;'),
            }
        selection = ''.join(['cmds.select(', str(selection), ')'])
        anchor = '<a name=\"%s\">%s</a>' % ('sceneboundingbox','')
        heading = '<h2>%s</h2>' % heading
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % str(t[k]))
            table += '        </tr>\n'
        
        table += '    </tbody>\n'
        table += '</table>\n'
        output.write(anchor)        
        output.write(heading) 
        output.write(help)  
        output.write(table) 
        
        #'06.  No Ngons - # of Ngons/# of Quads/# of Tris'
        (status, number, selection, Dpolycount, Lerr) = self.results_ngons
        heading = '06.  No Ngons - # of Ngons/# of Quads/# of Tris'
        help = ''.join(['<p>', cm.tests.components.f.size.run.__doc__.split('---')[0], '</p>'])
        s = ''
        for e in ["".join([err,'<br />']) for sublist in Lerr for err in sublist] :
            s = ''.join([s, e])
        t = {
            '01Result' :  status and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>',
            '02Number of n-gons' : number,
            '03Tris' : ('%d of %d %6.2f%%' % (Dpolycount['tris'], Dpolycount['face'], float(Dpolycount['tris'])/float(Dpolycount['face'] or 1 )*100.0)).replace(' ', '&nbsp;'),
            '04Quads' : ('%d of %d %6.2f%%' % (Dpolycount['quads'], Dpolycount['face'], float(Dpolycount['quads'])/float(Dpolycount['face'] or 1 )*100.0)).replace(' ', '&nbsp;'),
            '05N-Sided' : ('%d of %d %6.2f%%' % (Dpolycount['n-sided'], Dpolycount['face'], float(Dpolycount['n-sided'])/float(Dpolycount['face'] or 1)*100.0)).replace(' ', '&nbsp;'),
            #'07Selection' : selection,
            #'07Selection' : ''.join([x+'<br/>\n' for x in selection]),
            '06Errors': s
            }
        #selectionstr = ''.join(['cmds.select(', str(selection), ')'])
        anchor = '<a name=\"%s\">%s</a>' % ('ngons','')
        heading = '<h2>%s</h2>' % heading
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % t[k])
            table += '        </tr>\n'
        
        # fill the dict
        D = {}
        for x in selection:
            try:
                    D[x.split('.')[0]].extend([x])
            except KeyError:
                    D[x.split('.')[0]]= [x]
        # insert one empty row and header for the selection of n-sided faces per object
        table += '        <tr>\n'
        table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % '&nbsp;')
        table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % '&nbsp;')
        table += '        </tr>\n'
        table += '        <tr>\n'
        table += ('            <th style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </th>\n' % 'object')
        table += ('            <th style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </th>\n' % 'command to select n-sided faces')
        table += '        </tr>\n'
        for k in D.keys():
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % k)
            table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % ''.join(['cmds.select(', str(D[k]), ')']))
            table += '        </tr>\n'
        
        table += '    </tbody>\n'
        table += '</table>\n'       
        output.write(anchor) 
        output.write(heading)
        output.write(help)   
        output.write(table) 
        
        # '07.  Z-Fighting/Artifacting'
        anchor = '<a name=\"%s\">%s</a>' % ('artifacting','')
        heading = '<h2>%s</h2>' % '07.  Z-Fighting/Artifacting'
        help = '<p>This is a visual inspection. No automated test exists.</p>'
        output.write(anchor) 
        output.write(heading) 
        output.write(help)

        #'08a.  Zer area facess'
        #(status, number, selection) = checkmate.has_ngons()
        (status, number, selection) = self.results_zeroareafaces
        heading = '08a.  Zero Area Faces'
        help = ''.join(['<p>', cm.tests.components.f.area.run.__doc__.split('---')[0], '</p>'])
        s = ''
        for e in ["".join([err,'<br />']) for sublist in Lerr for err in sublist] :
            s = ''.join([s, e])
        t = {
            '01Result' :  status and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>',
            '02Number faces' : number,
            }
        #selectionstr = ''.join(['cmds.select(', str(selection), ')'])
        anchor = '<a name=\"%s\">%s</a>' % ('zerofaces','')
        heading = '<h2>%s</h2>' % heading
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % t[k])
            table += '        </tr>\n'
        # fill the dict
        D = {}
        for x in selection:
            try:
                    D[x.split('.')[0]].extend([x])
            except KeyError:
                    D[x.split('.')[0]]= [x]
        # insert one empty row and header for the selection of n-sided faces per object
        table += '        <tr>\n'
        table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % '&nbsp;')
        table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % '&nbsp;')
        table += '        </tr>\n'
        table += '        <tr>\n'
        table += ('            <th style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </th>\n' % 'object')
        table += ('            <th style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </th>\n' % 'command to select zero area faces')
        table += '        </tr>\n'
        for k in D.keys():
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % k)
            table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % ''.join(['cmds.select(', str(D[k]), ')']))
            table += '        </tr>\n'
        
        table += '    </tbody>\n'
        table += '</table>\n'      
        output.write(anchor) 
        output.write(heading)
        output.write(help)   
        output.write(table) 


        
        # '08.  No Reversed Faces'
        (status, numnonconformingfaces, numreversedmeshes, nonconformingfaces, reversedmeshes,  err) = self.results_flippednormals
        reversedmeshes = ''.join(['cmds.select(', str(reversedmeshes), ')'])
        nonconformingfaces = ''.join(['cmds.select(', str(nonconformingfaces), ')'])
        
        heading = '08b.  No Reversed Faces'
        t = {
            '1Result' :  status and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>',
            '2Number of reversed objects' : numreversedmeshes,
            '3Number of reversed faces' : numnonconformingfaces,
            '4Reversed objects' : reversedmeshes,
            #'5Errors' : err,
            '6Reversed faces' : nonconformingfaces,
            }
        selection = ''.join(['cmds.select(', str(selection), ')'])
        anchor = '<a name=\"%s\">%s</a>' % ('flippednormals','')
        heading = '<h2>%s</h2>' % heading
        help = ''.join(['<p>', cm.tests.components.f.normals.run.__doc__.split('---')[0], '</p>'])
        
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % t[k])
            table += '        </tr>\n'
        
        table += '    </tbody>\n'
        table += '</table>\n'     
        output.write(anchor) 
        output.write(heading)   
        output.write(help)
        output.write(table) 
        
        # '09   No Isolated Vertices - # of'
        #(status, number, selection) = checkmate.has_isolatedvertices2()
        (status, number, selection) = self.results_isolatedvertices2
        heading = '09   No Isolated Vertices - # of'
        help = ''.join(['<p>', cm.tests.components.vtx.isolated.run.__doc__.split('---')[0], '</p>'])
        #total = checkmate.polyvertexcount(faces=0, vertices=0)[1]['vertex']
        total = self.results_polyvertexcount[1]['vertex']
        try:
            percentage = float(number)/float(total)*100.0
        except ZeroDivisionError:
            percentage = 0.0
        t = {
            '2Number of isolated vertices' : '%d of %d (%.2f%%)' % (number,total,percentage),
            '1Result' :  status and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>',
            '3Selection' : selection,
            }
        #selection = ''.join(['cmds.select(', str(selection), ')'])
        anchor = '<a name=\"%s\">%s</a>' % ('isolatedvertices','')
        heading = '<h2>%s</h2>' % heading
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % t[k])
            table += '        </tr>\n'
        # face selection per object
        if number > 0:
            # fill the dict
            D = {}
            for x in selection:
                try:
                        D[x.split('.')[0]].extend([x])
                except KeyError:
                        D[x.split('.')[0]]= [x]
            # insert one empty row and header for the selection of n-sided faces per object
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % '&nbsp;')
            table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % '&nbsp;')
            table += '        </tr>\n'
            table += '        <tr>\n'
            table += ('            <th style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </th>\n' % 'object')
            table += ('            <th style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </th>\n' % 'command to select isolated vertices')
            table += '        </tr>\n'
            for k in D.keys():
                table += '        <tr>\n'
                table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % k)
                table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % ''.join(['cmds.select(', str(D[k]), ')']))
                table += '        </tr>\n'
        

        table += '    </tbody>\n'
        table += '</table>\n'     
        output.write(anchor) 
        output.write(heading)   
        output.write(help)
        output.write(table) 
        
        # '10. No Overlapping Vertices - # of'
        #(status, numberofvertices, numberofobjects, selection, objects) = checkmate.has_coincidentvertices2() 
        (status, numberofvertices, numberofobjects, selection, objects) = self.results_coincidentvertices2
        heading = '10. No Overlapping Vertices - # of'
        help = ''.join(['<p>', cm.tests.components.vtx.coincident.run.__doc__.split('---')[0], '</p>'])
        t = {
            '1Result' :  status and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>',
            '2Number of vertices': numberofvertices,
            '3Number of objects': numberofobjects,
            '5Selection' : selection,
            '4Objects' : objects,
            }
        #selection = ''.join(['cmds.select(', str(selection), ')'])
        anchor = '<a name=\"%s\">%s</a>' % ('coincidentvertices','')
        heading = '<h2>%s</h2>' % heading
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % t[k])
            table += '        </tr>\n'
        # populate the dict
        D = {}
        for x in selection:
            try:
                    D[x.split('.')[0]].extend([x])
            except KeyError:
                    D[x.split('.')[0]]= [x]
        # insert one empty row and header for the selection of n-sided faces per object
        table += '        <tr>\n'
        table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % '&nbsp;')
        table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % '&nbsp;')
        table += '        </tr>\n'
        table += '        <tr>\n'
        table += ('            <th style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </th>\n' % 'object')
        table += ('            <th style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </th>\n' % 'command to overlapping vertices')
        table += '        </tr>\n'
        for k in D.keys():
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % k)
            table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % ''.join(['cmds.select(', str(D[k]), ')']))
            table += '        </tr>\n'
        table += '    </tbody>\n'
        table += '</table>\n'      
        output.write(anchor) 
        output.write(heading) 
        output.write(help)  
        output.write(table) 
        
        # '11. No Overlapping Faces - # of'
        #(status, number, selection) = checkmate.has_laminafaces()
        (status, number, selection) = self.results_laminafaces
        heading = '11. No Overlapping Faces - # of'
        help = ''.join(['<p>', cm.tests.components.f.lamina.run.__doc__.split('---')[0], '</p>'])
        t = {
            '2Number of lamina faces' : number,
            '1Result' :  status and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>',
            '3Selection' : selection,
            }
        # selection = ''.join(['cmds.select(', str(selection), ')'])
        anchor = '<a name=\"%s\">%s</a>' % ('laminafaces','')
        heading = '<h2>%s</h2>' % heading
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % t[k])
            table += '        </tr>\n'
        # face selection per object
        if number > 0:
            # fill the dict
            D = {}
            for x in selection:
                try:
                        D[x.split('.')[0]].extend([x])
                except KeyError:
                        D[x.split('.')[0]]= [x]
            # insert one empty row and header for the selection of n-sided faces per object
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % '&nbsp;')
            table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % '&nbsp;')
            table += '        </tr>\n'
            table += '        <tr>\n'
            table += ('            <th style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </th>\n' % 'object')
            table += ('            <th style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </th>\n' % 'command to select overlapping faces')
            table += '        </tr>\n'
            for k in D.keys():
                table += '        <tr>\n'
                table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % k)
                table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % ''.join(['cmds.select(', str(D[k]), ')']))
                table += '        </tr>\n'
        

        table += '    </tbody>\n'
        table += '</table>\n'
       
        output.write(anchor) 
        output.write(heading)   
        output.write(help)
        output.write(table) 
        
        
        # '12. Naming/Organization  - non-descriptive names also no hierachy'
        
        anchor = '<a name=\"%s\">%s</a>' % ('namingorganization','')
        output.write(anchor) 
        
        # 12a Show Object Naming
        #(status, number, selection) = cm.tests.scene.names.run()
        (status, number, selection) = self.results_defaultnames
        heading = '12a. Naming/Organization - non-descriptive names'
        help = ''.join(['<p>', cm.tests.scene.names.run.__doc__.split('---')[0], '</p>'])
        t = {
            '2Number of objects' : number,
            '1Result' : status and  '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>',
            #'Selection' : selection or "",
            }
        
        heading = '<h2>%s</h2>' % heading
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width: 15%%\"> %s </td>\n' % t[k])
            table += ('            <td style=\"vertical-align: top; width: 75%%\"> %s </td>\n' % '')
            table += '        </tr>\n'
        for k in sorted(selection.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % '')
            table += ('            <td style=\"vertical-align: top; width: 15%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width: 75%%\"> %s </td>\n' % selection[k])
            table += '        </tr>\n'
            
        table += '    </tbody>\n'
        table += '</table>\n'
        output.write(heading)
        output.write(help)   
        output.write(table) 

        
        # 12b Show Object Hierarchy
        #(status, D) = cm.tests.scene.names.run()
        (status, D) = self.results_nohierarchy
        S = {}
        for k in D.keys():
            S[k] = ''
            for type, num in D[k].iteritems():
                S[k]+= '%s %s <br/>' % (num, type)
        
        heading = '12b. Naming/Organization - No hierachy'
        help = ''.join(['<p>', cm.tests.xforms.hierarchy.run.__doc__.split('---')[0], '</p>'])
        t = {
            '2# top level transforms' : len(D.keys()),
            '1Result' : status and  '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>',
            #'Selection' : selection or "",
            }
        anchor = '<a name=\"%s\">%s</a>' % ('defaultnames','')
        heading = '<h2>%s</h2>' % heading
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width: 15%%\"> %s </td>\n' % t[k])
            table += ('            <td style=\"vertical-align: top; width: 75%%\"> %s </td>\n' % '')
            table += '        </tr>\n'
            
        for k in sorted(D.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % '')
            table += ('            <td style=\"vertical-align: top; width: 15%%\"> %s </td>\n' % k)
            table += ('            <td style=\"vertical-align: top; width: 75%%\"> %s </td>\n' % S[k])
            table += '        </tr>\n'
        table += '    </tbody>\n'
        table += '</table>\n'
        output.write(anchor)         
        output.write(heading)
        output.write(help)   
        output.write(table) 
        
        
        
        # '13. History Clear'
        #(status, number, selection) = checkmate.has_history()
        (status, number, selection) = self.results_history
        anchor = '<a name=\"%s\">%s</a>' % ('history','')
        heading = '13. History Clear'
        help = '<p>Tests for construction history. Note that models with deformers require that construction history is present.</p>'
        help = ''.join(['<p>', cm.tests.shapes.history.run.__doc__.split('---')[0], '</p>'])
        t = {
            '2Number of objects' : number,
            '2Result' :  status and  '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>',
            '3Selection' : selection,
            }
        selection = ''.join(['cmds.select(', str(selection), ')'])
        anchor = '<a name=\"%s\">%s</a>' % ('history','')
        heading = '<h2>%s</h2>' % heading
        help = ''
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top;  width: 80%%; font-family: monospace;\"> %s </td>\n' % t[k])
            table += '        </tr>\n'
        
        table += '    </tbody>\n'
        table += '</table>\n'
       
        output.write(anchor) 
        output.write(heading)
        output.write(help)   
        output.write(table) 
        
        # '14. No Extra Elements Present in Renders'
        # (status, number, selection) = checkmate.has_hiddenobjects()
        (status, number, selection) = self.results_hiddenobjects
        anchor = '<a name=\"%s\">%s</a>' % ('hiddenobjects','')
        heading = '<h2>%s</h2>' % '14. No Hidden Objects'
        paragraph = '<p>Tests for hidden objects; i.e. objects that are not visible in the viewports because their visibility attribute is set to ON. Note that all children of an invisible object are also invisible. This test only mentions the objects with the attribute set to OFF, not its invisible children.</p>'
        help = ''.join(['<p>', cm.tests.xforms.hidden.run.__doc__.split('---')[0], '</p>'])
        t = {
            '2Number of hidden objects' : number,
            '1Result' :  status and  '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>',
            '3Selection' : selection,
            }
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width: 15%%\"> %s </td>\n' % t[k])
            table += ('            <td style=\"vertical-align: top; width: 75%%\"> %s </td>\n' % '')
            table += '        </tr>\n'
        
        table += '    </tbody>\n'
        table += '</table>\n'

        output.write(anchor) 
        output.write(heading)
        output.write(help)
        output.write(table)
         
        
        # '15. Textures/Materials included'
        #(status, number, selection) = checkmate.has_missingfiles()
        (status, number, selection) = self.results_missingfiles
        heading = '15. Textures/Materials included'
        #help ='<p>This test shows the name of the file node and the filetexturename if the file texture cannot be found by Maya.</p>'
        help = ''.join(['<p>', cm.tests.scene.missing.run.__doc__.split('---')[0], '</p>'])
        t = {
            '2Number' : number,
            '1Result' :  status and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>',
            #'Files' : selection,
            }
        # selection = ''.join(['cmds.select(', str(selection), ')'])
        anchor = '<a name=\"%s\">%s</a>' % ('missingfiles','')
        heading = '<h2>%s</h2>' % heading
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width: 15%%\"> %s </td>\n' % t[k])
            table += ('            <td style=\"vertical-align: top; width: 75%%\"> %s </td>\n' % '')
            table += '        </tr>\n'
       
        for k in sorted(selection.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % '')
            table += ('            <td style=\"vertical-align: top; width: 15%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width: 75%%\"> %s </td>\n' % selection[k])
            table += '        </tr>\n'
        
        table += '    </tbody>\n'
        table += '</table>\n'
       
        output.write(anchor) 
        output.write(heading)
        output.write(help)   
        output.write(table) 
        
        # No Material
        (status, objectswithoutmaterial, objectswithdefaultmaterial) = self.results_nomaterial
        heading = 'Objects with no or default materials'
        help = ''.join(['<p>', cm.tests.shapes.material.run.__doc__.split('---')[0], '</p>'])
        t = {'01Result': status and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>',
            '02Objects with no material' : objectswithoutmaterial,
            '03Objects with default material' : objectswithdefaultmaterial,
        }
        anchor = '<a name=\"%s\">%s</a>' % ('nomaterial','')
        heading = '<h2>%s</h2>' % heading
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width: 15%%\"> %s </td>\n' % t[k])
            table += ('            <td style=\"vertical-align: top; width: 75%%\"> %s </td>\n' % '')
            table += '        </tr>\n'
        
        table += '    </tbody>\n'
        table += '</table>\n'        
        
        output.write(anchor) 
        output.write(heading)
        output.write(help)
        output.write(table)
        
        # '16. Textures Zipped with Model'
        anchor = '<a name=\"%s\">%s</a>' % ('textureszipped','')
        heading = '<h2>%s</h2>' % '16. Textures Zipped with Model'
        help = '<p>This is a visual inspection. No automated test exists.</p>'
        output.write(anchor) 
        output.write(heading)
        output.write(help)

        # '17. Textures Named - descriptively'
        #(status, number, selection) = cm.tests.scene.names.run(type='textures')
        (status, number, selection) = self.results_defaulttexturenames
        heading = '17. Textures Named - descriptively'
        help = ''.join(['<p>', cm.tests.scene.names.run.__doc__.split('---')[0], '</p>'])
        t = {
            '2Number of textures' : number,
            '1Result' : status and  '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>',
            #'Selection' : selection or "",
            }
        anchor = '<a name=\"%s\">%s</a>' % ('texturesnamed','')
        heading = '<h2>%s</h2>' % heading
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width: 15%%\"> %s </td>\n' % t[k])
            table += ('            <td style=\"vertical-align: top; width: 75%%\"> %s </td>\n' % '')
            table += '        </tr>\n'

        table += '        <tr>\n'
        table += ('            <th style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </th>\n' % 'Default node names')
        table += ('            <th style=\"vertical-align: top; width: 15%%\"> %s </th>\n' % 'default name')
        table += ('            <th style=\"vertical-align: top; width: 75%%\"> %s </th>\n' % 'nodes')
        table += '        </tr>\n'
        
        for k in sorted(selection.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % '')
            table += ('            <td style=\"vertical-align: top; width: 15%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width: 75%%\"> %s </td>\n' % selection[k])
            table += '        </tr>\n'
        
        table += '        <tr>\n'
        table += ('            <th style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </th>\n' % 'All file textures')
        table += ('            <th style=\"vertical-align: top; width: 15%%\"> %s </th>\n' % 'node')
        table += ('            <th style=\"vertical-align: top; width: 75%%\"> %s </th>\n' % 'filename')
        table += '        </tr>\n'
        Dtexturefilenames = cm.utils.find.texturefilenames()
        for k in sorted(Dtexturefilenames):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % '')
            table += ('            <td style=\"vertical-align: top; width: 15%%\"> %s </td>\n' % k)
            table += ('            <td style=\"vertical-align: top; width: 75%%\"> %s </td>\n' % os.path.basename(Dtexturefilenames[k]))
            table += '        </tr>\n'
        table += '    </tbody>\n'
        table += '</table>\n'
        output.write(anchor)         
        output.write(heading)
        output.write(help)   
        output.write(table) 


        # '18. Materials Named - descriptively'
        #(status, number, selection) = cm.tests.scene.names.run(type='materials')
        (status, number, selection) = self.results_defaultmaterialnames
        heading = '18. Materials Named - descriptively'
        help = ''.join(['<p>', cm.tests.scene.names.run.__doc__.split('---')[0], '</p>'])
        t = {
            '2Number of materials' : number,
            '1Result' : status and  '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>',
            #'Selection' : selection or "",
            }
        anchor = '<a name=\"%s\">%s</a>' % ('materialsnamed','')
        heading = '<h2>%s</h2>' % heading
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width: 15%%\"> %s </td>\n' % t[k])
            table += ('            <td style=\"vertical-align: top; width: 75%%\"> %s </td>\n' % '')
            table += '        </tr>\n'
        for k in sorted(selection.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % '')
            table += ('            <td style=\"vertical-align: top; width: 15%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width: 75%%\"> %s </td>\n' % selection[k])
            table += '        </tr>\n'
            
        table += '    </tbody>\n'
        table += '</table>\n'
        output.write(anchor)         
        output.write(heading)
        output.write(help)   
        output.write(table) 
        
        # '19. UV Quality - no stretching, no obvious seams, no flipped or overlapping (stacked) UV\'s'
        anchor = '<a name=\"%s\">%s</a>' % ('uvquality','')
        heading = '<h2>%s</h2>' % '19. UV Quality - no stretching, no obvious seams, no flipped or overlapping (stacked) UV\'s'
        help = '<p>This is a visual inspection. No automated test exists.</p>'
        output.write(anchor) 
        output.write(heading)
        output.write(help)
        
        # 19a
        #(status, number, selection) = checkmate.has_missinguvmaps()
        (status, number, selection) = self.results_missinguvmaps
        heading = '19a. Missing UV maps'
        help = ''.join(['<p>', cm.tests.components.uv.missing.run.__doc__.split('---')[0], '</p>'])
        t = {
            '2Number faces without UVs' : number,
            '1Result' :  status and  '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>',
            '3Selection' : selection,
            }
        selection = ''.join(['cmds.select(', str(selection), ')'])
        anchor = '<a name=\"%s\">%s</a>' % ('missinguvs','')
        heading = '<h2>%s</h2>' % heading
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top;  width: 80%%; font-family: monospace;\"> %s </td>\n' % t[k])
            table += '        </tr>\n'
        
            
        table += '    </tbody>\n'
        table += '</table>\n'
       
        output.write(anchor) 
        output.write(heading)
        output.write(help)   
        output.write(table) 
        
        # 19b
        (status, selection) = self.results_uvbbox
        objselection = selection.keys()
        heading = '19b. UV Bounding Box'
        help = ''.join(['<p>', cm.tests.components.uv.range.run.__doc__.split('---')[0], '</p>'])
        help = self.txt2html(help)
        t = {
            '2Objects' : len(selection.keys()),
            '1Result' :  status and  '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>',
            '3Selection' : ''.join(['cmds.select(', str(objselection), ')'])
            }
        # selection = ''.join(['cmds.select(', str(selection), ')'])
        anchor = '<a name=\"%s\">%s</a>' % ('missinguvs','')
        heading = '<h2>%s</h2>' % heading
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top;  width: 80%%; font-family: monospace;\"> %s </td>\n' % t[k])
            table += '        </tr>\n'
        # insert one empty row and header for the selection of UV values per object
        table += '        <tr>\n'
        table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % '&nbsp;')
        table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </td>\n' % '&nbsp;')
        table += '        </tr>\n'
        table += '        <tr>\n'
        table += ('            <th style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </th>\n' % 'object')
        table += ('            <th style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> %s </th>\n' % 'UV range')
        table += '        </tr>\n'
        for k in selection.keys():
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % k)
            table += ('            <td style=\"vertical-align: top; width: 80%%; font-family: monospace;\"> minU: %.3f maxU: %.3f minV: %.3f maxV: %.3f</td>\n' % selection[k])
            table += '        </tr>\n'
        table += '    </tbody>\n'
        table += '</table>\n'
       
        output.write(anchor) 
        output.write(heading)
        output.write(help)   
        output.write(table) 
        


        # 19c
        anchor = '<a name=\"%s\">%s</a>' % ('uvquality','')
        heading = '<h2>%s</h2>' % '19c. No stretching UV\'s'
        help = '<p>This is a visual inspection. No automated test exists.</p>'
        output.write(anchor) 
        output.write(heading)
        output.write(help)
        
        # 19d
        anchor = '<a name=\"%s\">%s</a>' % ('uvquality','')
        heading = '<h2>%s</h2>' % '19d. No obvious seams'
        help = '<p>This is a visual inspection. No automated test exists.</p>'
        output.write(anchor) 
        output.write(heading)
        output.write(help)
        
        # 19e
        anchor = '<a name=\"%s\">%s</a>' % ('uvquality','')
        heading = '<h2>%s</h2>' % '19e. No flipped  UV\'s'
        help = '<p>This is a visual inspection. No automated test exists. Open the UV editor and turn on Shaded UV Display. See <a href=\"http://download.autodesk.com/us/maya/2011help/files/Editing_UVs_Display_UV_winding_order.htm\">Display UV winding order</a> in the Maya documentation.</p>'
        output.write(anchor) 
        output.write(heading)
        output.write(help)
        
        # 19f
        #(status, number, selection, numverts, vertselection) = checkmate.has_overlappinguvs()
        (status, number, selection, numverts, vertselection) = self.results_overlappinguvs
        
        vertselection = ''.join(['cmds.select(', str(vertselection), ')'])    
        heading = '19f. Overlapping (stacked) UV faces'
        t = {
            '1Result' :  status and '<span style=\"color: red; font-weight: bold;\">FAIL</span>' or '<span style=\"color: green; font-weight: bold;\">PASS</span>',
            '2Number of overlapping UVfaces' : number,
            '3Selection' : selection,
            '4Number of overlapping UVs' : numverts,
            '5Selection' : vertselection,
            }
        anchor = '<a name=\"%s\">%s</a>' % ('overlappinguvs','')
        heading = '<h2>%s</h2>' % heading
        help = ''.join(['<p>', cm.tests.components.uv.coincident.run.__doc__.split('---')[0], '</p>'])
        table ='<table style=\"text-align: left; width: 100%;\" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">\n'
        table += '    <tbody>\n'
        for k in sorted(t.keys()):
            table += '        <tr>\n'
            table += ('            <td style=\"vertical-align: top; white-space: nowrap; width: 20%%\"> %s </td>\n' % re.sub('[0-9]', '', k))
            table += ('            <td style=\"vertical-align: top; width:80%%\"> %s </td>\n' % t[k])
            table += '        </tr>\n'
        
        table += '    </tbody>\n'
        table += '</table>\n'
       
        output.write(anchor) 
        output.write(heading)
        output.write(help)   
        output.write(table) 
        # print a footer
        output.write("""<p class="Copyright">&copy; 2011 TurboSquid</p>""")    
        ############################################################################     
        output.write("""</div>""")
        output.write("""</div>""")
        output.write("""</body>""")
        output.write("""</html>""")
        output.close()
    
    def showHTML(self):
        cmds.showHelp(self.url, absolute=True)
        