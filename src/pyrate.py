'''
Created on 16 juil. 2013

@author: tehboii
'''

import os, yaml
from werkzeug import secure_filename

conf = None
strings = dict()
reservedNames = []  # List of names which potentially conflicts with service routes.

def readPath( relativePath, listFiles=True ):
	if relativePath == '/': relativePath = None
	path = os.path.abspath( os.path.join( conf['root'], relativePath if relativePath else '' ) )
	if not path.startswith( conf['root'] ):
		raise Exception( "Illegal access" )

	if os.path.isdir( path ):

		files = list()
		crumbs = list()
		if listFiles:	
			if relativePath:
				parent, child = os.path.split( relativePath )
				crumbs.append( child )
				while( parent ):
					parent, child = os.path.split( parent )
					crumbs.append( child )
				crumbs.reverse()
	
			for file in os.listdir( path ):
				if not exposeFile( file  ):
													continue;
				entry = {'name': file, 'type':'question-sign'}
				ext = os.path.splitext( file )[1][1:]
				if os.path.isdir( os.path.join( path, file ) ): 
					entry['type'] = 'folder-close'
				else:
					for type_, exts in conf['typeIcons'].items():
						if ext in exts:
							entry['type'] = type_
							break;
				entry['size'] = os.stat(os.path.join(path, file)).st_size
				entry['date'] = os.path.getctime(os.path.join(path, file))
				files.append( entry )
		return {'type':'dir', 'crumbs':crumbs, 'files':files, 'canUpload': True if relativePath else False}
	elif os.path.isfile( path ):
		return {'type':'file'}

	return None

def acceptFile( path, name ):
	name = sanitizeName( name )
	return True

def acceptDir( path, name ):
	name = sanitizeName( name )
	return True

def sanitizeName( name ):
	""" Returns a valid file name out of anything """
	if not name:
		raise Exception( "Empty name" )

	while name in reservedNames: name = {'_{0}'.format( name )}

	name = secure_filename( name )
	
	return name

def exposeFile( path ):
	path = os.path.abspath( path )

	path, file = os.path.split( path )  # returns ('', 'file') for just 'file' (but '/path' returns ('/', 'path'))

	if ( file != conf['dirSetup'] ) and ( not file.startswith( '.' ) ):
		return True

	return False

def init( confStream ):
	global conf, strings
	conf = yaml.load( confStream )
	conf['root'] = os.path.abspath( conf['root'] )
	for l in conf['i18n']['available']:
		strings[l] = yaml.load(open('i18n/{0}.yaml'.format(l), 'r'))
