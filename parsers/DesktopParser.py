# -*- coding: utf-8 -*-
# This file is part of BlueBox (BackBox XFCE -> FluxBox Menu Automatic Update Daemon).
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
import os.path
import syslog
import codecs
import re
import os

from DesktopFile import DesktopFile

class DesktopParser:

  STATE_NONE    = 0
  STATE_INIT    = 1
  STATE_PARSING = 2

  MANDATORY_FIELDS = (
    'name',
    'exec',
    'categories'
  )

  def __init__( self ):
    self.filename = ""
    self.state    = DesktopParser.STATE_NONE
    self.lineno   = 0
    self.fd       = None
    self.file     = DesktopFile()

  def reset( self ):
    self.filename = ""
    self.state    = DesktopParser.STATE_NONE
    self.lineno   = 0
    self.fd       = None
    self.file     = DesktopFile()

  def __parse_array( self, value, separators ):
    separators = map( lambda s: re.escape(s), separators )
    regexp     = "[%s]" % ''.join(separators)
    items      = re.split( regexp, value )
    items      = map( lambda s: s.strip(), items )
    items      = filter( lambda s:s != '', items )
    return items

  def __parse_bool( self, value ):
    value = value.lower()
    return True if value == 'true' else False

  def parse( self, filename ):
    # handle sym links
    if os.path.islink(filename):
      self.filename = os.readlink( filename )
    else:
      self.filename = filename

    if not os.path.exists( self.filename ):
      return None

    collection = []
    
    self.fd    = codecs.open( self.filename, "r", "utf-8" )
    self.state = DesktopParser.STATE_INIT

    try:
      for line in self.fd.readlines():
        self.lineno += 1
        line = line.strip()

        # skip empty lines and comments
        if line == '' or line[0] == '#':
          continue

        # ok, we've found a [Desktop Entry] line, sate parser state accordingly
        if re.match( '^\[\s*Desktop\s+Entry\s*\]$', line, re.IGNORECASE ):
          self.state = DesktopParser.STATE_PARSING
        # skip label lines
        elif re.match( '^\[.+]$', line, re.IGNORECASE ):
          continue
        # let's parse those bastards!
        elif self.state == DesktopParser.STATE_PARSING and '=' in line:
          ( label, value ) = line.split( '=', 1 )

          label = label.strip().lower()
          value = value.strip()

          collection.append( label )

          if label == 'type':
            self.file.type = value
          elif label == 'version':
            self.file.version = value
          elif label == 'encoding':
            self.file.encoding = value
          elif label == 'name':
            self.file.name = value
          elif label == 'genericname':
            self.file.generic_name = value
          elif label == 'comment':
            self.file.comment = value
          elif label == 'exec':
            self.file.command = value
          elif label == 'icon':
            self.file.icon = value
          elif label == 'terminal':
            self.file.terminal = self.__parse_bool(value)
          elif label == 'categories':
            self.file.categories = self.__parse_array( value, [ ';' ] )
          elif label == 'mimetype':
            self.file.mime_types = self.__parse_array( value, [ ';' ] )
          # skip everything else
          else:
            pass
        # found something before a [Desktop Entry]
        else:
          syslog.syslog( syslog.LOG_ERR, "Corrupted .desktop file '%s' on line %d" % ( self.filename, self.lineno ) )
          
    except UnicodeDecodeError as e:
      return None
    finally:
      self.fd.close()
      self.state = DesktopParser.STATE_NONE

    missing = filter( lambda x:x not in collection, DesktopParser.MANDATORY_FIELDS )
    if missing != ():
      syslog.syslog( syslog.LOG_ERR, "File '%s' missing mandatory fields : %s" % ( self.filename, ', '.join(missing) ) )
      return None
    else:
      return self.file
