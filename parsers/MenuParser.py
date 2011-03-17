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
import codecs
import re

from xml.dom import minidom
from Menu    import Menu

class MenuParser:
  def __init__( self, filename ):
    self.filename = filename
    self.xmldoc   = minidom.parse( self.filename )
    self.root     = Menu()

  def reset(self):
    self.xmldoc = minidom.parse( self.filename )
    self.root   = Menu()

  def __getDataFromDirectoryFile( self, directory ):
    name  = ""
    icon  = ""
    
    fd    = codecs.open( "/usr/share/desktop-directories/" + directory, "r", "utf-8" )
    lines = fd.readlines()
    fd.close()

    for line in lines:
      line = line.strip()
      m    = re.match( '^Name\s*=\s*(.+)$', line )
      if m:
        name = m.group(1)
      else:
        m = re.match( '^Icon\s*=\s*(.+)$', line )
        if m:
          icon = m.group(1)

    return ( name, icon )

  def __getChildData( self, node, name ):
    nodes = node.childNodes
    for node in nodes:
      if node.nodeType == node.ELEMENT_NODE and node.tagName == name:
        return node.firstChild.nodeValue
    return None

  def __recurse( self, node, root ):
    nodes = node.childNodes

    for node in nodes:
      if node.nodeType == node.ELEMENT_NODE and node.tagName == 'Menu':
        name      = self.__getChildData( node, 'Name' )
        directory = self.__getChildData( node, 'Directory' )
        menu      = Menu()
        menu.name = name

        if directory is not None:
          ( label, icon ) = self.__getDataFromDirectoryFile( directory )
          menu.label = label
          menu.icon  = icon
          menu.setFather(root)
          root.addSubMenu(menu)

        self.__recurse( node, menu )

  def parse(self):
    nodes = self.xmldoc.childNodes
    
    for node in nodes:
      if node.nodeType == node.ELEMENT_NODE and node.tagName == 'Menu':
        name      = self.__getChildData( node, 'Name' )
        directory = self.__getChildData( node, 'Directory' )      

        self.root.name = name

        if directory is not None:
          ( label, icon ) = self.__getDataFromDirectoryFile( directory )
          self.root.label = label
          self.root.icon  = icon

        self.__recurse( node, self.root )

    return self.root
