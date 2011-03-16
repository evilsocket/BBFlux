import os.path
# -*- coding: utf-8 -*-
import os

class Menu:
  def __init__( self, name = "", label = "" ):
    self.name     = name
    self.label    = label
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
    for menu in self.submenus:
      if menu.isEmpty():
        self.submenus.remove(menu)
      else:
        menu.removeEmptyItems()

  def toFluxBox( self, tabs = 0 ):
    fluxboxmenu = ""

    if self.name.lower() == 'xfce':
      fluxboxmenu += """\
[begin] (fluxbox)'
  [nop] (BackBox Linux)
  [nop]
"""
    else:
      fluxboxmenu += '%s[submenu] (%s)\n' % ( '\t' * tabs, self.label )
      
    for program in self.programs:
      command = program.command.replace( 'sh -c', 'xterm -e' )
      name    = program.name.replace('(','').replace(')','')
      # icon  = '/usr/share/pixmaps/' + program.icon + '.png' if '/' not in program.icon and program.icon != '' else program.icon
      
      fluxboxmenu += '%s[exec] (%s) {%s}\n' % ( '\t' * (tabs + 1), name, command )

    for menu in self.submenus:
      fluxboxmenu += menu.toFluxBox( tabs + 1 )

    if self.name.lower() == 'xfce':
      if os.path.exists( os.path.expanduser( "~/.fluxbox/custom-menu" ) ):
        fluxboxmenu += """\
  [nop]
  [include] (~/.fluxbox/custom-menu)
"""

      fluxboxmenu += """\
  [nop]
  [config] (Configuration)
  [submenu] (Styles) {}
    [stylesdir] (/usr/share/fluxbox/styles)
    [stylesdir] (~/.fluxbox/styles)
  [end]
  [workspaces] (Workspaces)
  [reconfig] (Reconfigure)
  [restart] (Restart)
  [exit] (Exit)
"""

    fluxboxmenu += '%s[end]\n' % ( '\t' * tabs )

    return fluxboxmenu

  # for debug purpose only, doh!
  def debug( self, tabs = 0 ):
    print "%s%s (%s) %s" % ( '\t' * tabs, self.label, self.name, ':' if len(self.submenus) > 0 or len(self.programs) > 0 else '' )

    for program in self.programs:
      print "%s[P %s]" % ( '\t' * (tabs + 1), program.name )

    for menu in self.submenus:
      menu.debug( tabs + 1 )
