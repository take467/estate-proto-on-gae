import logging
import os
import re
import sys
import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


# use zipped gaeo
try:
    import os
    if os.path.exists("gaeo.zip"):
        import sys
        sys.path.insert(0, 'gaeo.zip')
except:
    print "use normal gaeo folder"

import gaeo
from gaeo.dispatch import router

webapp.template.register_template_library( 'templatefilters')

def initRoutes():
    r = router.Router()
    
    #TODO: add routes here

    r.connect('/:controller/:action/:id')
    r.connect('/document/feed/:id/:filename.:suffix',controller='files',action='feed')
    r.connect('/document/feed/:id/:filename',controller='files',action='feed')
    r.connect('/product/thumbnail/:id/:filename.:suffix',controller='product',action='thumbnail')
    r.connect('/product/thumbnail/:id/:filename',controller='product',action='thumbnail')
    r.connect('/google7562b62e5c4ce30a.:sufix',controller='welcome',action='google')
    r.connect('/view/export/:id/:filename.:suffix',controller='view',action='export')

def initPlugins():
    """
    Initialize the installed plugins
    """
    plugins_root = os.path.join(os.path.dirname(__file__), 'plugins')
    if os.path.exists(plugins_root):
        plugins = os.listdir(plugins_root)
        for plugin in plugins:
            if not re.match('^__|^\.', plugin):
                try:
                    exec('from plugins import %s' % plugin)
                except ImportError:
                    logging.error('Unable to import %s' % (plugin))
                except SyntaxError:
                    logging.error('Unable to import name %s' % (plugin))

from openid.server import server as OpenIDServer
import store


def InitializeOpenId():
  oidserver = OpenIDServer.Server(store.DatastoreStore())
  OpenIDServer.Server.server_instance = oidserver


def main():
    # add the project's directory to the import path list.
    sys.path.append(os.path.dirname(__file__))
    sys.path.append(os.path.join(os.path.dirname(__file__), 'application'))

    # get the gaeo's config (singleton)
    config = gaeo.Config()
    # setup the templates' location
    config.template_dir = os.path.join(
        os.path.dirname(__file__), 'application', 'templates')

    initRoutes()
    # initialize the installed plugins
    initPlugins()

    # initialize the OpenID server
    InitializeOpenId()

    app = webapp.WSGIApplication([
                (r'.*', gaeo.MainHandler),
            ], debug=True)
    wsgiref.handlers.CGIHandler().run(app)

if __name__ == '__main__':
    main()
