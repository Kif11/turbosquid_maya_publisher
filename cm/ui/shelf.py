
import maya.cmds as cmds
import maya.mel
import os

def ClearUI():
	if cmds.scrollLayout("ReviewLayout", query = True, exists = True):
		cmds.deleteUI("ReviewLayout")
		cmds.scrollLayout("ReviewLayout", p = "CheckMateWindow")

def createOptionsWindow(*args):
	
	if cmds.window('CheckMateWindow',exists=True):
		cmds.showWindow("CheckMateWindow")
		return
		
	cmWindow = cmds.window('CheckMateWindow', title="CheckMate review tools", w = 300, h = 800, menuBar=True,menuBarVisible=True)
	
	cmds.menu('CheckMateTestsMenu',parent=cmWindow,label="Tests",mnemonic="T")

	cmds.menuItem('historyItem', echoCommand=True,
		label='Construction History',
		annotation='check for construction history',
		command='import cm.ui.shelf as shelf; shelf.ClearUI();import cm.tests.shapes.history; reload(cm.tests.shapes.history); cm.tests.shapes.history.run()'
		)
		
	cmds.menuItem('zeroAreaFacesItem', echoCommand=True,
		label='Zero Area Faces',
		annotation='check for faces with no surface area ',
		command='import cm.ui.shelf as shelf; shelf.ClearUI();import cm.tests.components.f.area; reload(cm.tests.components.f.area); cm.tests.components.f.area.run()'
		)
		
	cmds.menuItem('ngonsItem', echoCommand=True,
		label='N-sided Faces',
		annotation='check for ngons (n-sided faces)',
		command='import cm.ui.shelf as shelf; shelf.ClearUI();import cm.tests.components.f.size; reload(cm.tests.components.f.size); cm.tests.components.f.size.run()'
		)
	
	cmds.menuItem('centeredAtOriginItem', echoCommand=True,
		label='Centered At Origin',
		annotation='Check for centered at origin',
		command='import cm.ui.shelf as shelf; shelf.ClearUI();import cm.tests.xforms.centered;reload(cm.tests.xforms.centered); cm.tests.xforms.centered.run()'
		)
	
	cmds.menuItem('nonZeroTransformsItem', echoCommand=True,
		label='Non-Zero Transforms',
		annotation='check for non-zero transforms',
		command='import cm.ui.shelf as shelf; shelf.ClearUI();import cm.tests.xforms.identity;reload(cm.tests.xforms.identity); cm.tests.xforms.identity.run()'
		)
	
	cmds.menuItem('polyvertexcountItem', echoCommand=True,
		label='Polygon and Vertex Count',
		annotation='count polys and vertices',
		command='import cm.ui.shelf as shelf; shelf.ClearUI();import cm.stats.poly;reload(cm.stats.poly); cm.stats.poly.run()'
		)
	
	cmds.menuItem('sceneBoundingBoxItem', echoCommand=True,
		label='Scene Bounding Box',
		annotation='return Scene Bounding Box Values',
		command='import cm.ui.shelf as shelf; shelf.ClearUI();import cm.stats.bbox;reload(cm.stats.bbox); cm.stats.bbox.run()'
		)
	
	cmds.menuItem('flippedNormalstem', echoCommand=True,
		label='Flipped Normals',
		annotation='check for reversed normals',
		command='import cm.ui.shelf as shelf; shelf.ClearUI();import cm.tests.components.f.normals; reload(cm.tests.components.f.normals); cm.tests.components.f.normals.run()'
		)
		
	cmds.menuItem('isolatedVerticesItem', echoCommand=True,
		label='Isolated Vertices',
		annotation='check for isolated vertices',
		command='import cm.ui.shelf as shelf; shelf.ClearUI();import cm.tests.components.vtx.isolated; reload(cm.tests.components.vtx.isolated); cm.tests.components.vtx.isolated.run()'
		)

	cmds.menuItem('coincidentVerticesItem', echoCommand=True,
		label='Overlapping Vertices',
		annotation='check for overlapping (coincident) vertices',
		command='import cm.ui.shelf as shelf; shelf.ClearUI();import cm.tests.components.vtx.coincident; reload(cm.tests.components.vtx.coincident); cm.tests.components.vtx.coincident.run()'
		)
		
	cmds.menuItem('laminaFacesItem', echoCommand=True,
		label='Overlapping (lamina) Faces',
		annotation='check for overlapping (lamina) faces',
		command='import cm.ui.shelf as shelf; shelf.ClearUI();import cm.tests.components.f.lamina; reload(cm.tests.components.f.lamina); cm.tests.components.f.lamina.run()'
		)
	
	cmds.menuItem('defaultNamesItem', echoCommand=True,
		label='Default Names',
		annotation='check for objects with default names',
		command='import cm.ui.shelf as shelf; shelf.ClearUI();import cm.tests.scene.names;reload(cm.tests.scene.names); cm.tests.scene.names.run()'
		)
		
	cmds.menuItem('noHierarchyItem', echoCommand=True,
		label='No Hierarchy',
		annotation='check for hierarchy in scene',
		command='import cm.ui.shelf as shelf; shelf.ClearUI();import cm.tests.xforms.hierarchy;reload(cm.tests.xforms.hierarchy); cm.tests.xforms.hierarchy.run()'
		)
		
	cmds.menuItem('noHiddenItem', echoCommand=True,
		label='No Hidden Objects',
		annotation='check for hidden objects in in scene',
		command='import cm.ui.shelf as shelf; shelf.ClearUI();import cm.tests.xforms.hidden;reload(cm.tests.xforms.hidden); cm.tests.xforms.hidden.run()'
		)

	cmds.menuItem('noMissingFilesItem', echoCommand=True,
		label='No Missing Files',
		annotation='check for hierarchy in scene',
		command='import cm.ui.shelf as shelf; shelf.ClearUI();import cm.tests.scene.missing;reload(cm.tests.scene.missing); cm.tests.scene.missing.run()'
		)
		
	cmds.menuItem('noMaterialsItem', echoCommand=True,
		label='No Missing Materials',
		annotation='check for missing or default material',
		command='import cm.ui.shelf as shelf; shelf.ClearUI();import cm.tests.shapes.material; reload(cm.tests.shapes.material); cm.tests.shapes.material.run()'
		)
		
	cmds.menuItem('defaultTextureNamesItem', echoCommand=True,
		label='Default Texture Names',
		annotation='check for default texture names',
		command='import cm.ui.shelf as shelf; shelf.ClearUI();import cm.tests.scene.names;reload(cm.tests.scene.names); cm.tests.scene.names.run(type=\'textures\')'
		)
		
	cmds.menuItem('defaultMaterialNamesItem', echoCommand=True,
		label='Default Material Names',
		annotation='check for default material names',
		command='import cm.ui.shelf as shelf; shelf.ClearUI();import cm.tests.scene.names;reload(cm.tests.scene.names); cm.tests.scene.names.run(type=\'materials\')'
		)
		
	cmds.menuItem('missingUVmapsItem', echoCommand=True,
		label='Missing UVs',
		annotation='check for missing UVs',
		command='import cm.ui.shelf as shelf; shelf.ClearUI();import cm.tests.components.uv.missing; reload(cm.tests.components.uv.missing); cm.tests.components.uv.missing.run()'
		)
		
	cmds.menuItem('overlappingUVsItem', echoCommand=True,
		label='Overlapping UVs',
		annotation='check for default material names',
		command='import cm.ui.shelf as shelf; shelf.ClearUI();import cm.tests.components.uv.coincident; reload(cm.tests.components.uv.coincident); cm.tests.components.uv.coincident.run()'
		)
	cmds.menuItem('UVbboxItem', echoCommand=True,
		label='UV Bounding Box',
		annotation='check UV bounding box',
		command='import cm.ui.shelf as shelf; shelf.ClearUI();import cm.tests.components.uv.range; reload(cm.tests.components.uv.range); cm.tests.components.uv.range.run()'
		)
		
	cmds.menu('CheckMateReportsMenu',parent=cmWindow,label="Reports",mnemonic="R")
	cmds.menuItem('saveHTMLitem',
		label="Save HTML report on current scene",
		annotation="Write HTML report for current scene",
		command='import cm.report.report;reload(cm.report.report);r=cm.report.report.Report(\'current\');r.writeHTML();r.showHTML()'
		) 
	cmds.menuItem('saveHTMLitemOpenFile',
		label="Open scene and save HTML report",
		annotation="Close this scene, open new scene and write HTML report",
		command='import cm.report.report;reload(cm.report.report);r=cm.report.report.Report(\'open\');r.writeHTML();r.showHTML()'
		) 
	cmds.menuItem(divider=True)
	cmds.menuItem('saveHTMLitemFolder', 
		label="Open folder and save HTML reports",
		annotation="Close this scene, open a folder and write HTML reports for all files in folder",
		command='import cm.report.report;reload(cm.report.report);cm.utils.open.folder()'
		)
	cmds.menuItem('includesubdirItem',
		label='Include Subdirectories', 
		annotation='Include subdirectories',
		checkBox=cmds.optionVar(query='includeSubDir'),
		command = 'import cm.ui.callbacks; reload(cm.ui.callbacks);cm.ui.callbacks.includesubdirCB()')
	
	cmds.menu('CheckMateOptionsMenu',parent=cmWindow,label="Options",mnemonic="O")
	
	
	cmds.menuItem('verbosityItem',
		label='Verbose', 
		annotation='Enable verbose output. Warning: SLOW',
		checkBox=cmds.optionVar(query='checkmateVerbosity'),
		command = 'import cm.ui.callbacks; reload(cm.ui.callbacks);cm.ui.callbacks.verbosityCB()')
	
	cmds.menuItem(divider=True)
	

	cmds.scrollLayout("ReviewLayout", p = "CheckMateWindow")
	
	cmds.showWindow("CheckMateWindow")
		

		
