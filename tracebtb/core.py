#!/usr/bin/env python

"""
    btbwgstool core.
    Created Jan 2022
    Copyright (C) Damien Farrell

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 3
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import sys,os,subprocess,glob,re
import time, datetime
import platform

home = os.path.expanduser("~")
module_path = os.path.dirname(os.path.abspath(__file__)) #path to module
config_path = os.path.join(home, '.config','tracebtb')

defaultfont = 'Lato'
defaults = {
            'FONT' :defaultfont,
            'FONTSIZE' : 10,
            'TIMEFORMAT' :'%m/%d/%Y',
            'ICONSIZE' : 28,
            'DPI' : 100,
            'THREADS': 4
         }
#populate current class variable
for k in defaults:
    vars()[k] = defaults[k]
