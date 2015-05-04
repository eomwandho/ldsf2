"""
/***************************************************************************
 Point Cluster Tool
 V 0.0.1
                                 A QGIS plugin
 A simple example plugin to load shapefiles
                              -------------------
        begin                : 2012-04-08
        copyright            : (C) 2012 by Erick O. Opiyo
                                            Dr Tor Vagen
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
from qgis.core import *

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import gftools_utils
import siterand_core


#from ui_geoinformaticsLab import Ui_geoinformaticsLab
from ui.ui_pprandpoints import Ui_ppgen

#class Dialog(QDialog, Ui_geoinformaticsLab):
class Dialog(QDialog, Ui_ppgen):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.mapCanvas = self.iface.mapCanvas()
        self.buttonOk = self.buttonBox_2.button( QDialogButtonBox.Ok )
        self.cancel_close = self.buttonBox_2.button( QDialogButtonBox.Close )
        self.progressBar.setValue(0)
        QObject.connect(self.toolOut, SIGNAL("clicked()"), self.outFile)
        layers = gftools_utils.getLayerNames([QGis.Polygon, QGis.Point])
        self.inShape.addItems(layers)
        
    def accept(self):
        self.buttonOk.setEnabled(False)
        if self.inShape.currentText() == "":
            QMessageBox.information(self, self.tr("Warning!!"), self.tr("No input layer specified"))
        elif self.outShape.text() == "":
            QMessageBox.information(self, self.tr("Warning"), self.tr("Please specify output shapefile"))
        else:
            outPath = self.outShape.text()
            if outPath.contains("\\"):
                outName = outPath.right((outPath.length() - outPath.lastIndexOf("\\")) - 1)
            else:
                outName = outPath.right((outPath.length() - outPath.lastIndexOf("/")) - 1)
            if outName.endsWith(".shp"):
                outName = outName.left(outName.length() - 4)
            self.outShape.clear()
            siterand_core.geometry(self.inShape.currentText(), self.shapefileName, self.encoding, "pp", "NULL")
            addToTOC = QMessageBox.question(self, self.tr("Cluster Points"),
            self.tr("Created output Cluster point shapefile:\n%1\n\nWould you like to add the new layer to the TOC?").arg(outPath), 
            QMessageBox.Yes, QMessageBox.No, QMessageBox.NoButton)
            if addToTOC == QMessageBox.Yes:
                self.vlayer = QgsVectorLayer(outPath, unicode(outName), "ogr")
                QgsMapLayerRegistry.instance().addMapLayer(self.vlayer)
        self.buttonOk.setEnabled( True )
    
    def outFile(self):
        self.outShape.clear()
        ( self.shapefileName, self.encoding ) = gftools_utils.saveDialog( self )
        if self.shapefileName is None or self.encoding is None:
            return
        self.outShape.setText( QString( self.shapefileName ) )   
        
             