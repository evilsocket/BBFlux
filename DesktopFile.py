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
class DesktopFile:
  def __init__( self ):
    self.type         = ""
    self.version      = ""
    self.encoding     = "UTF-8"
    self.name         = ""
    self.generic_name = ""
    self.comment      = ""
    self.command      = ""
    self.icon         = ""
    self.terminal     = False
    self.categories   = []
    self.mime_types   = []
