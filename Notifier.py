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
class Notifier:
  __instance = None

  def __init__(self):
    self.libnotify = False

    try:
      import pynotify
      if pynotify.init("BlueBox - BackBox Linux Fluxbox Menu Auto Generation Daemon"):
        self.libnotify = True
    except:
      pass

  def notify( self, message ):
    if self.libnotify:
      import pynotify
      notification = pynotify.Notification( "BlueBox Notification", message )
      notification.show()

  @classmethod
  def getInstance(cls):
    if cls.__instance is None:
      cls.__instance = Notifier()
    return cls.__instance