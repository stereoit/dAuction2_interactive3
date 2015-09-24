__author__ = 'MSIS'

"""
The most basic (working) CherryPy 3.0 Windows service possible.
Requires Mark Hammond's pywin32 package.
"""
import dAuction2

import cherrypy
cherrypy.config.update({'server.socket_port': 9090})
if __name__ == '__main__':
    cherrypy.quickstart(dAuction2)