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
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from ldsf2dialog import ldsf2Dialog
import os.path


class ldsf2:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'ldsf2_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = ldsf2Dialog()

    def initGui(self):
        # Create action that will start plugin configuration
        self.pp_gen = QAction(
            QIcon(":/plugins/ldsf2/images/icon.png"),
            u"LDSF Site Randomization Tool", self.iface.mainWindow())
        # connect the action to the run method
        self.pp_gen.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.pp_gen)
        self.iface.addPluginToMenu(u"&LDSF", self.pp_gen)

        self.csv_gen = QAction(
            QIcon(":/plugins/ldsf2/images/icon.png"),
            u"LDSF Site Randomization Tool", self.iface.mainWindow())
        # connect the action to the run method
        self.csv_gen.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.csv_gen)
        self.iface.addPluginToMenu(u"&LDSF", self.csv_gen)

        self.ext_gen = QAction(
            QIcon(":/plugins/ldsf2/images/icon.png"),
            u"LDSF Site Randomization Tool", self.iface.mainWindow())
        # connect the action to the run method
        self.ext_gen.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.ext_gen)
        self.iface.addPluginToMenu(u"&LDSF", self.ext_gen)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&LDSF", self.pp_gen)
        self.iface.removeToolBarIcon(self.pp_gen)

        self.iface.removePluginMenu(u"&LDSF", self.csv_gen)
        self.iface.removeToolBarIcon(self.csv_gen)

        self.iface.removePluginMenu(u"&LDSF", self.ext_gen)
        self.iface.removeToolBarIcon(self.ext_gen)

    # run method that performs all the real work
    def pp_gen(self):
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code)
            pass

    def csv_gen(self):
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code)
            pass

    def ext_gen(self):
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code)
            pass
