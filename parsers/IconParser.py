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
import fnmatch

class IconParser:
  __instance = None
  
  def __init__(self):
    self.cache = {}

  def __findIcon( self, path, pattern ):
    for root, dirnames, filenames in os.walk( path ):
      for filename in fnmatch.filter( filenames,  pattern ):
        return os.path.join(root, filename)

    return None

  def getIconByName( self, name ):
    name = name.replace( '.png', '' )
    
    if name is None or name == '':
      return None
    if name[0] == '/':
      return name
    elif self.cache.has_key(name):
      return self.cache[name]
    else:
      if os.path.exists( '/usr/share/pixmaps/' + name + '.png' ):
        self.cache[name] = '/usr/share/pixmaps/' + name + '.png'
        return '/usr/share/pixmaps/' + name + '.png'
      else:
        icon = self.__findIcon( '/usr/share/icons', name + '.png' )
        if icon is not None:
          self.cache[name] = icon

        return icon

  @classmethod
  def getInstance(cls):
    if cls.__instance is None:
      cls.__instance = IconParser()
    return cls.__instance