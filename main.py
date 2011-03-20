#!/usr/bin/python
# -*- coding: utf-8 -*-
# This file is part of BBFlux (BackBox XFCE -> FluxBox Menu Automatic Update Daemon).
#
# Copyright(c) 2010-2011 Simone Margaritelli
# evilsocket@gmail.com - evilsocket@backbox.org
# http://www.evilsocket.net
# http://www.backbox.org
#
# This file may be licensed under the terms of of the
# GNU General Public License Version 2 (the ``GPL'').
#
# Software distributed under the License is distributed
# on an ``AS IS'' basis, WITHOUT WARRANTY OF ANY KIND, either
# express or implied. See the GPL for the specific language
# governing rights and limitations.
#
# You should have received a copy of the GPL along with this
# program. If not, go to http://www.gnu.org/licenses/gpl.html
# or write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import syslog
import codecs
import signal
import os
import sys
import atexit

from glob                  import glob
from time                  import sleep
from parsers.MenuParser    import MenuParser
from parsers.DesktopParser import DesktopParser
from Notifier              import Notifier

# just for constants
class BBFlux:
  FIRST_RUN_FILE  = os.path.expanduser( "~/.fluxbox/.bbflux_generation_done" )
  FLUXBOX_MENU    = os.path.expanduser( "~/.fluxbox/menu" )
  XFCE_MENU       = "/etc/xdg/xdg-backbox/menus/backbox-applications.menu"
  DESKTOP_PATTERN = "/usr/share/applications/*.desktop"
  WAIT_DELAY      = 3
  PID_FILE        = os.path.expanduser( "~/.bbflux.pid" )

def exit_signal_handler( sig, func ): 
  exit(1)

def exit_handler():
  if os.path.exists( BBFlux.PID_FILE ):
    os.unlink( BBFlux.PID_FILE )
    
  syslog.syslog( 'BBFlux Stopped' )

if __name__ == "__main__":
  try:
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'update':
      menuparser     = MenuParser( BBFlux.XFCE_MENU )
      menu           = menuparser.parse()
      desktopparser  = DesktopParser()
      files          = glob( BBFlux.DESKTOP_PATTERN )
      menu           = menuparser.parse()

      print "@ Starting menu generation ..."

      for file in files:
        desktop = desktopparser.parse( file )
        if desktop is None:
          print "@ File '%s' could not be parsed, corrupted content or encoding ." % file
        elif desktop.nodisplay is False:
          menu.findOwnerAndAdd(desktop)

        desktopparser.reset()
      
      print "@ Removing empty items ..."
      menu.removeEmptyItems()

      print "@ Converting to fluxbox standards ..."
      fd = codecs.open( BBFlux.FLUXBOX_MENU, 'w+', 'UTF-8' )
      fd.write( menu.toFluxBox() )
      fd.close()

      print "@ Menu updated ."
    elif len(sys.argv) > 1 and sys.argv[1].lower() == 'kill':
      if os.path.exists( BBFlux.PID_FILE ):
        pid = file( BBFlux.PID_FILE, 'r' ).read().strip()
        if( os.path.exists( '/proc/' + pid ) ):
          os.kill( int(pid), signal.SIGKILL )
          print "@ BBFlux daemong killed ."
        else:
          print "@ BBFlux is not running ."
    else:

      # check if there's another live instance running
      if os.path.exists( BBFlux.PID_FILE ):
        pid = file( BBFlux.PID_FILE, 'r' ).read().strip()
        if( os.path.exists( '/proc/' + pid ) ):
          print "@ BBFlux is already running ."
          quit()

      atexit.register(exit_handler)
        
      signal.signal( signal.SIGTERM, exit_signal_handler )

      pid = open( BBFlux.PID_FILE, 'w+' )
      pid.write( str(os.getpid()) )
      pid.close()

      syslog.openlog( "BBFlux" )

      syslog.syslog( 'BBFlux Started with pid file %s' % BBFlux.PID_FILE )

      first_run      = not os.path.exists( BBFlux.FIRST_RUN_FILE )
      first_run_done = False

      menuparser     = MenuParser( BBFlux.XFCE_MENU )
      menu           = menuparser.parse()
      desktopparser  = DesktopParser()
      prev           = []

      while True:
        files = glob( BBFlux.DESKTOP_PATTERN )

        current = len(files)
        last    = len(prev)

        if current != last:

          if first_run:
            open( BBFlux.FIRST_RUN_FILE, 'w+' ).close()
            first_run_done = True
            first_run      = False
          elif not first_run_done:
            first_run_done = True
            prev           = files
            continue

          menuparser.reset()

          menu = menuparser.parse()

          for file in files:
            desktop = desktopparser.parse( file )
            if desktop == None:
              syslog.syslog( syslog.LOG_NOTICE, "File '%s' could not be parsed, corrupted content or encoding ." % file )
            else:
              menu.findOwnerAndAdd(desktop)

            desktopparser.reset()

          menu.removeEmptyItems()

          fd = codecs.open( BBFlux.FLUXBOX_MENU, 'w+', 'UTF-8' )
          fd.write( menu.toFluxBox() )
          fd.close()

          updated = abs(current - last)
          message = "BBFlux daemon succesfully updated %d item%s in FluxBox menu." % ( updated, "s" if updated > 1 else "" )

          syslog.syslog( message )

          Notifier.getInstance().notify( message )

          prev = files

        sleep( BBFlux.WAIT_DELAY )
      
  except KeyboardInterrupt:
    syslog.syslog( 'User interrupted BBFlux daemon with a keyboard interrupt.' )

  except Exception as e:
    syslog.syslog( syslog.LOG_ERR, str(e) )
