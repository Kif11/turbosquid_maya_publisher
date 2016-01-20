import os
import re
import tempfile

from maya import cmds as cmds

import cm.report.report

def foldercontents(*args, **kwargs):
	valid_kwargs = ['verbose', 'dir', 'sub']
	for k, v in kwargs.iteritems():
		if k not in valid_kwargs:
			raise TypeError("Invalid keyword argument %s" % k)
			
	# verbose mode
	try:
		verbose = kwargs['verbose']
	except KeyError:
		verbose = False 
		if cmds.optionVar(exists='checkmateVerbosity'):
			   verbose = cmds.optionVar(query='checkmateVerbosity')

	# check subdirectories
	try:
		sub = kwargs['sub']
	except KeyError:
		sub=False
	
	# which directory
	try:
		searchpath = kwargs['dir']
		print 'you gave me ', searchpath
	except KeyError:
		if not cmds.about(batch=True):
			searchpath = cmds.fileDialog2(fileMode=3, okCaption='Open',caption='Open the folder with scenes to run Check-Mate on')
		else:
			print '#Error: can\'t open'
			exit
	if verbose:
		print 'checking %s' % searchpath
	
	scenefiles = []
	exp = ".*\.m[a-b]$"	
	if sub:
		for dir in searchpath:
			if verbose:
				print'dir:', dir
				for root, dirs, files in os.walk(dir):
					for f in files:
						if (re.compile(exp).match(f)) and  True or False:
							print 'found -> ', f
							scenefiles.append(os.path.join(root, f))
	else:
		for dir in searchpath:
			if verbose:
				print 'dir: ',  dir
				files = os.listdir(dir)
				for f in files:
					if (re.compile(exp).match(f)) and  True or False:
						print 'found ::: ', f
						scenefiles.append(os.path.join(dir, f))
	return scenefiles	


def folder(*args, **kwargs):
	""" create reports for all files in a folder
	"""
	valid_kwargs = ['sub']
	for k, v in kwargs.iteritems():
		if k not in valid_kwargs:
			raise TypeError("Invalid keyword argument %s" % k)
	try:
		includesubdir = kwargs['sub']
	except KeyError:
		includesubdir = False 
		if cmds.optionVar(exists='includeSubDir'):
			includesubdir = cmds.optionVar(query='includeSubDir')
		else:
			includesubdir = False  
	print "Include Sub-directories: ", includesubdir  
	for f in foldercontents(verbose=True, sub=includesubdir):
		print 'Open for reporting : ', f
		fileWithLog([f])
		print 'create report for : ', f
		r=cm.report.report.Report('current')
		print 'write report for : ', f
		r.writeHTML()
		#r.showHTML()
		
# 
def fileWithLog(*args):
	""" open file, create log and report number of errors and warnings
		returns   (False, None) if no problems were encountered  
	"""
	result = False
	batch = cmds.about(batch=True)
	err = None	
	Lrequires = []
	Lwarnings = []
	Lerrors = []
	try:
		cmds.file(new=True, force=True) 
	except RuntimeError:
		scenefilename = cmds.file(sn=True)
		print '%s is not a new scene, has unsaved changes' % scenefilename
		pass
	# save the log file to a temp directory	
	scriptEditorLog = os.path.join(tempfile.gettempdir(), 'scriptEditor.log')
	# scriptEditorLog = ''.join([cmds.internalVar(userTmpDir=True), 'scriptEditor.log'])
	# delete the log file if it exists 
	try:
		os.remove(scriptEditorLog) 
	# ignore errors if the file does not exist
	except OSError:
		pass
	# if we're in GUI mode write the outut of the script editor to a log file
	if batch:
		print 'we\'re soooo... in batch mode'
		# sys.stderr = open(scriptEditorLog, w)
		
	cmds.scriptEditorInfo(historyFilename=scriptEditorLog, writeHistory=True)
	# open a scene file,  if a file name is provided, use it	
	try:
		scenefilename = args[0] 
	except IndexError:	  
		multipleFilters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"
		scenefilename = cmds.fileDialog2(fileFilter=multipleFilters, fileMode=1, okCaption='Open',caption='Open a Maya scene file for certification')
	# open the scene file	
	cmds.file(scenefilename[0],open=True, force=True)
	# turn off the file logging
	cmds.scriptEditorInfo(historyFilename=scriptEditorLog, writeHistory=False)
	
	
	openfile = open(scriptEditorLog, 'r')
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
				
	errors = map((lambda x: '# Error:' in x), lines)
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
	return result, Lrequires, Lwarnings, Lerrors
	
