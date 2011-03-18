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
import os
from parsers.IconParser import IconParser

class Menu:
  def __init__( self, name = "", label = "", icon = "" ):
    self.name     = name
    self.label    = label
    self.icon     = icon
    self.father   = None
    self.submenus = []
    self.programs = []
    
  def setFather( self, menu ):
    self.father = menu

  def addSubMenu( self, menu ):
    self.submenus.append( menu )

  def findOwnerAndAdd( self, desktop ):

    if self.name in desktop.categories:
      self.programs.append( desktop )
      return True
    # special case, tnx to Raffaele messed up brain -.-
    elif self.father != None and self.father.name == 'Services' and len(desktop.categories) > 0 and self.name in desktop.categories[0]:
      self.programs.append( desktop )
      return True
    # same as before
    elif self.name == 'Hacking' and desktop.categories[0] == u'BackBox':
      self.programs.append( desktop )
      return True
    else:
      for menu in self.submenus:
        if menu.findOwnerAndAdd( desktop ) is True:
          return True

    return False

  def isEmpty( self ):
    if len(self.programs) != 0:
      return False
    else:
      for menu in self.submenus:
        if menu.isEmpty() is False:
          return False

      return True

  def removeEmptyItems(self):
    empty = []
    for menu in self.submenus:
      if menu.isEmpty():
        empty.append( menu )
      else:
        menu.removeEmptyItems()
    # remove empty items after the loop to avoid strange behaviour
    self.submenus = filter( lambda x:x not in empty, self.submenus )

  def toFluxBox( self, tabs = 0 ):
    fluxboxmenu = ""

    if self.name.lower() == 'xfce':
      fluxboxmenu += "[begin] (BackBox Linux)\n"
    else:
      icon = IconParser.getInstance().getIconByName( self.icon )
      icon = '<%s>' % icon if icon is not None else ''

      fluxboxmenu += '%s[submenu] (%s) %s\n' % ( '\t' * tabs, self.label, icon )
      
    for program in self.programs:
      command = program.command.replace( 'sh -c', 'xterm -e' )
      name    = program.name.replace('(','').replace(')','')
      icon    = IconParser.getInstance().getIconByName( program.icon )
      icon    = '<%s>' % icon if icon is not None else ''
      
      fluxboxmenu += '%s[exec] (%s) {%s} %s\n' % ( '\t' * (tabs + 1), name, command, icon )

    for menu in self.submenus:
      fluxboxmenu += menu.toFluxBox( tabs + 1 )

    if self.name.lower() == 'xfce':
      if os.path.exists( os.path.expanduser( "~/.bbflux-custom-menu" ) ):
        fluxboxmenu += """\
  [separator]
  [include] (~/.bbflux-custom-menu)
"""
    fluxboxmenu += '%s[end]\n' % ( '\t' * tabs )

    return fluxboxmenu

  # for debug purpose only, doh!
  def debug( self, tabs = 0 ):
    print "%s%s (%s) %s" % ( '\t' * tabs, self.label, self.name, ':' if len(self.submenus) > 0 or len(self.programs) > 0 else '' )

    for program in self.programs:
      print "%s[P %s] <%s>" % ( '\t' * (tabs + 1), program.name, program.icon )

    for menu in self.submenus:
      menu.debug( tabs + 1 )
