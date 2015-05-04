"""
/***************************************************************************
 Point Cluster Tool
 V 0.0.1
                                 A QGIS plugin
 A simple example plugin to load shapefiles
                              -------------------
        begin                : 2012-04-08
        copyright            : (C) 2012 by Erick Omwandho Opiyo
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
from ui.ui_extrandpoints import Ui_extgen


class Dialog(QDialog, Ui_extgen):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        QObject.connect(self.toolOut, SIGNAL("clicked()"), self.outFile)
        QObject.connect(self.btnUpdate, SIGNAL("clicked()"), self.updateLayer)
        QObject.connect(self.btnCanvas, SIGNAL("clicked()"), self.updateCanvas)
        self.buttonOk = self.buttonBox.button( QDialogButtonBox.Ok )
        self.xMin.setValidator(QDoubleValidator(self.xMin))
        self.xMax.setValidator(QDoubleValidator(self.xMax))
        self.yMin.setValidator(QDoubleValidator(self.yMin))
        self.yMax.setValidator(QDoubleValidator(self.yMax))
        self.populateLayers()
        
    def populateLayers( self ):
        self.inShape.clear()
        layermap = QgsMapLayerRegistry.instance().mapLayers()
        for name, layer in layermap.iteritems():
            self.inShape.addItem( unicode( layer.name() ) )
            if layer == self.iface.activeLayer():
                self.inShape.setCurrentIndex( self.inShape.count() -1 )
                
    def updateLayer( self ):
        mLayerName = self.inShape.currentText()
        if not mLayerName == "":
            mLayer = gftools_utils.getMapLayerByName( unicode( mLayerName ) )
            boundBox = mLayer.extent()
            self.updateExtents( boundBox )  
            
    def updateCanvas( self ):
        canvas = self.iface.mapCanvas()
        boundBox = canvas.extent()
        mLayerName = self.inShape.currentText()
        if not mLayerName == "":
            xMin = boundBox.xMinimum()
            yMin = boundBox.yMinimum()
            xMax = boundBox.xMaximum()
            yMax = boundBox.yMaximum()
        self.updateExtents( boundBox )
    
    def outFile(self):
        self.outShape.clear()
        ( self.shapefileName, self.encoding ) = gftools_utils.saveDialog( self )
        if self.shapefileName is None or self.encoding is None:
            return
        self.outShape.setText( QString( self.shapefileName ) )
        
    def updateExtents( self, boundBox ):
        self.xMin.setText( unicode( boundBox.xMinimum() ) )
        self.yMin.setText( unicode( boundBox.yMinimum() ) )
        self.xMax.setText( unicode( boundBox.xMaximum() ) )
        self.yMax.setText( unicode( boundBox.yMaximum() ) )

    def accept(self):
        self.buttonOk.setEnabled( False )
        if self.xMin.text() == "" or self.xMax.text() == "" or self.yMin.text() == "" or self.yMax.text() == "":
            QMessageBox.information(self, self.tr("Vector grid"), self.tr("Please specify valid extent coordinates"))
        elif self.outShape.text() == "":
            QMessageBox.information(self, self.tr("Vector grid"), self.tr("Please specify output shapefile"))
        else:
            try:
                boundBox = QgsRectangle(
                float( self.xMin.text() ),
                float( self.yMin.text() ),
                float( self.xMax.text() ),
                float( self.yMax.text() ) )
            except:
                QMessageBox.information(self, self.tr("Vector grid"), self.tr("Invalid extent coordinates entered"))
                
            outPath = self.outShape.text()
            if outPath.contains("\\"):
                outName = outPath.right((outPath.length() - outPath.lastIndexOf("\\")) - 1)
            else:
                outName = outPath.right((outPath.length() - outPath.lastIndexOf("/")) - 1)
            if outName.endsWith(".shp"):
                outName = outName.left(outName.length() - 4)
            self.outShape.clear()        
            self.gen( float( self.xMin.text() ),float( self.yMin.text() ),float( self.xMax.text() ),
                      float( self.yMax.text() ), str(self.site.text()))
            addToTOC = QMessageBox.question(self, self.tr("Cluster Points"),
                                            self.tr("Created output Cluster point shapefile:\n%1\n\nWould you like to add the new layer to the TOC?").arg(outPath),
                                            QMessageBox.Yes, QMessageBox.No, QMessageBox.NoButton)
            if addToTOC == QMessageBox.Yes:
                #gftools_utils.addShapeToCanvas( self.shapefileName )
                self.vlayer = QgsVectorLayer(outPath, unicode(outName), "ogr")
                QgsMapLayerRegistry.instance().addMapLayer(self.vlayer)
                self.populateLayers()
            self.buttonOk.setEnabled( True )
                      
        
        self.buttonOk.setEnabled( True )
        QMessageBox.information(self, self.tr("Message"), self.tr(str(self.site.text())))
        
    def gen(self, xMin, yMin, xMax, yMax, site):
        outfile = QgsVectorLayer("Polygon?crs=epsg:4326", "ext_temp_poly", "memory")
        outfile_provider = outfile.dataProvider()
        outfeature = QgsFeature()
        pt1 = QgsPoint(xMin,yMax)
        pt2 = QgsPoint(xMax,yMax)
        pt3 = QgsPoint(xMax,yMin)
        pt4 = QgsPoint(xMin,yMin)
        polygon = [[pt1, pt2, pt3, pt4, pt1]]
        geom = QgsGeometry.fromPolygon(polygon)
        outfeature.setGeometry(geom)
        outfeature.addAttribute(0, QVariant(""))
        outfile_provider.addFeatures([outfeature])
        siterand_core.geometry(outfile, self.shapefileName, self.encoding, "ext", site)
     