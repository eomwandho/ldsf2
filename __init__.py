# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ldsf2
                                 A QGIS plugin
 Land Degradation Survelliance Framework Site Randomization Tool
                             -------------------
        begin                : 2014-06-27
        copyright            : (C) 2014 by ICRAF
        email                : e.omwandho@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    # load ldsf2 class from file ldsf2
    from ldsf2 import ldsf2
    return ldsf2(iface)
