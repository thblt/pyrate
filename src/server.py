from flask import Flask, render_template, send_file, redirect, url_for, request, abort, make_response

import pyrate, time, os

app = Flask( __name__ )


@app.template_filter( 'date' )
def filter_datetime( date, fmt='%m %B %Y' ):
	return time.strftime( fmt, time.localtime() )

def getLocale():
	cookie = request.cookies.get( 'locale', None )
	if cookie in pyrate.conf['i18n']['available']:
		return cookie
	accept = request.headers.get( 'Accept-Language', [] ).split( ',' )
	for l in accept:
		if l.strip() in pyrate.conf['i18n']['available']:
			return l
	for l in accept:
		short = l.strip()[0:l.strip().find( '-' )]
		if short in pyrate.conf['i18n']['available']:
			return short

	return pyrate.conf['i18n']['fallback']

@app.route( '/', methods=['get'] )
@app.route( '/<path:path>/', methods=['get'] )
def get( path=None, flashes=[] ):
	setLocaleCookie = True
	locale = request.args.get( 'locale', None )
	if not locale or not locale in pyrate.conf['i18n']['available']:
		locale = getLocale()
		setLocaleCookie = False

	strings = pyrate.strings[locale]
	isRoot = False if path else True
	point = pyrate.readPath( path )

	localeIds = pyrate.conf['i18n']['available']
	locales = list()
	for l in localeIds:
		locales.append( {'id': l, 'name': pyrate.strings[l]['_name'], 'active':True if l == locale else False} )


	if point['type'] == 'dir':
		resp = make_response( render_template( 'main.html', isRoot=isRoot, path=path, dir=point, conf=pyrate.conf, s=strings, locales=locales, flashes=flashes ) )
		if setLocaleCookie: resp.set_cookie( 'locale', locale )
		return resp
	elif point['type'] == 'file':
		return send_file( os.path.join( pyrate.conf['root'], path ), as_attachment=True )

# upload and mkdir

@app.route( '/', methods=['post'] )
@app.route( '/<path:path>/', methods=['post'] )
def post( path=None ):

	if not pyrate.readPath( path, listFiles=False )['type'] == 'dir': abort( 500 )

	locale = getLocale()
	flashes = []
	what = request.form['what']
	if what == 'up':
		file = request.files['upload_file']
		if not file.filename:  # ```If not file``` doesn't work…
			flashes.append( {'level':'warning', 'message':pyrate.strings[locale]['errors']['noFileProvided']} )
		else:
			i = 1
			targetName = pyrate.sanitizeName( file.filename )
			baseTargetName, baseTargetExt = os.path.splitext( targetName )

			print( os.path.join( pyrate.conf['root'], path if path else '', targetName ) )
			while os.path.exists( os.path.join( pyrate.conf['root'], path if path else '', targetName ) ):
				targetName = "{0}_({1}){2}".format( baseTargetName, i, baseTargetExt )
				if i==1:
					flashes.append( {'level':'info', 'message':pyrate.strings[locale]['errors']['fileRenamed']} )
				i+=1

			file.save( os.path.join( pyrate.conf['root'], path if path else '', targetName ) )
			flashes.append( {'level':'success', 'message':pyrate.strings[locale]['errors']['fileSent']} )
	elif what == 'mkdir':
		dirName = pyrate.sanitizeName( request.form['name'] )
		if not dirName:
			flashes.append( {'level':'warning', 'message':pyrate.strings[locale]['errors']['illegalDirName']} )
		else:
			try:
				os.mkdir( os.path.join( pyrate.conf['root'], path if path else '', dirName ) )
				flashes.append( {'level':'success', 'message':pyrate.strings[locale]['errors']['dirCreated']} )
			except FileExistsError:
				flashes.append( {'level':'error', 'message':pyrate.strings[locale]['errors']['dirExists']} )
	return get( path, flashes=flashes )


@app.route( '/favicon.ico/' )
def favicon():
	return redirect( url_for( 'static', filename='favicon.png' ) )

if __name__ == '__main__':
	pyrate.init( open( '../pyrate.yaml', 'r' ) )

	app.run( debug=True )
	# from flask_frozen import Freezer
	# frz = Freezer(app)
	# frz.freeze()
