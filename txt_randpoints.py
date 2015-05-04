"""
/***************************************************************************
 Point Cluster Tool
 V 0.0.1
                                 A QGIS plugin
 A simple example plugin to load shapefiles
                              -------------------
        begin                : 2012-04-08
        copyright            : (C) 2012 by Erick Omwandho Opiyo
                                            Dr Tor Vagen 
                                            ICRAF GeoScience Lab
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
import csv

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import gftools_utils
import siterand_core
from ui.ui_txtrandpoints import Ui_txtgen


class Dialog(QDialog, Ui_txtgen):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        
        self.buttonOk = self.buttonBox.button( QDialogButtonBox.Ok )
        QObject.connect(self.btnSelectCsv, SIGNAL("clicked()"), self.select_csv)
        QObject.connect(self.toolOut, SIGNAL("clicked()"), self.outFile)
        #QObject.connect(self.buttonBox, SIGNAL("accepted()"), self.run)      
    
    def select_csv(self):
        file_name = QFileDialog.getOpenFileName(self, self.tr('Select input CSV file'), '', self.tr('CSV files (*.csv *.CSV)'))
        if not file_name.isEmpty():
            self.txtCsvPath.setText(file_name)
            
        header = self.read_csv_header(file_name)
        if not header:
            return
        
        self.longcol.clear()
        self.latcol.clear()
        self.shapeidcol.clear()
        self.site.clear()
        
        for field in header:
            self.longcol.addItem(QString(field))
            self.latcol.addItem(QString(field))
            self.shapeidcol.addItem(QString(field))
            self.site.addItem(QString(field))

        for x in range(0, len(header)):
            if (header[x].lower().strip() == "id") or (header[x].lower().strip() == "shapeid") or (header[x].lower().strip() == 'shape_id') :
                self.shapeidcol.setCurrentIndex(x)
                break
            
        for x in range(0, len(header)):
            if (header[x].lower().strip() == "site"):
                self.site.setCurrentIndex(x)
                break

        for x in range(0, len(header)):
            if (header[x].find("x") >= 0) or (header[x].find("X") >= 0) or (header[x].lower()[0:3] == 'lon'):
                self.longcol.setCurrentIndex(x)
                break

        for x in range(0, len(header)):
            if (header[x].find("y") >= 0) or (header[x].find("Y") >= 0) or (header[x].lower()[0:3] == 'lat'):
                self.latcol.setCurrentIndex(x)
                break

            
    def outFile(self):
        self.outShape.clear()
        ( self.shapefileName, self.encoding ) = gftools_utils.saveDialog( self )
        if self.shapefileName is None or self.encoding is None:
            return
        self.outShape.setText( QString( self.shapefileName ) )
        
    def accept(self):
        self.buttonOk.setEnabled(False)
        if self.txtCsvPath.text() == "":
            QMessageBox.information(self, self.tr("Warning!!"), self.tr("No input layer specified"))
        elif self.outShape.text() == "":
            QMessageBox.information(self, self.tr("Warning"), self.tr("Please specify output shapefile"))
        elif self.longcol.currentText() == "":
            QMessageBox.information(self, self.tr("Warning"), self.tr("Please specify Longitude Column"))
        elif self.latcol.currentText() == "":
            QMessageBox.information(self, self.tr("Warning"), self.tr("Please specify Latitude Column"))
        elif self.site.currentText() == "":
            QMessageBox.information(self, self.tr("Warning"), self.tr("Please specify Site Column"))
        elif self.shapeidcol.currentText() == "":
            QMessageBox.information(self, self.tr("Warning"), self.tr("Please specify Feature ID"))
        else:
            outPath = self.outShape.text()
            if outPath.contains("\\"):
                outName = outPath.right((outPath.length() - outPath.lastIndexOf("\\")) - 1)
            else:
                outName = outPath.right((outPath.length() - outPath.lastIndexOf("/")) - 1)
            if outName.endsWith(".shp"):
                outName = outName.left(outName.length() - 4) 
            #message = self.geometry_import_from_csv(unicode(self.txtCsvPath.displayText()), 
            #    unicode(self.longcol.currentText()), unicode(self.latcol.currentText()),
            #    unicode(self.shapeidcol.currentText()), unicode(self.outShape.displayText()))
            
            self.geometry_import_from_csv(unicode(self.txtCsvPath.displayText()), 
                unicode(self.longcol.currentText()), unicode(self.latcol.currentText()),
                unicode(self.shapeidcol.currentText()), unicode(self.site.currentText()), unicode(self.outShape.displayText()))
            
            addToTOC = QMessageBox.question(self, self.tr("Cluster Points"),
                                            self.tr("Created output Cluster point shapefile:\n%1\n\nWould you like to add the new layer to the TOC?").arg(outPath),
                                            QMessageBox.Yes, QMessageBox.No, QMessageBox.NoButton)
            if addToTOC == QMessageBox.Yes:
                #gftools_utils.addShapeToCanvas( self.shapefileName )
                self.vlayer = QgsVectorLayer(outPath, unicode(outName), "ogr")
                QgsMapLayerRegistry.instance().addMapLayer(self.vlayer)
                #self.populateLayers()
            self.buttonOk.setEnabled( True )
            
            #vlayer = QgsVectorLayer(unicode(self.outShape.displayText()), unicode(outName), "ogr")
            #QgsMapLayerRegistry.instance().addMapLayer(vlayer)
                
                #if message <> None:
                #    QMessageBox.critical(self.iface.mainWindow(), "Geometry Import", message)           
            
    def geometry_import_from_csv(self,node_filename, long_colname, lat_colname, 
                                        shapeid_colname, site_colname, shapefile_name):
        try:
            infile = open(node_filename, 'r')           
        except:
            return "Failure opening " + node_filename
            
        try:
            dialect = csv.Sniffer().sniff(infile.read(2048))
        except:
            return "Bad CSV file (verify that your delimiters are consistent): " + node_filename
        
        infile.seek(0)
        reader = csv.reader(infile, dialect)
        header = reader.next()
    
        lat_col = -1
        long_col = -1
        shapeid_col = -1
        site_col = -1
        
        for x in range(len(header)):
            # print header[x]
            if (header[x] == lat_colname):
                lat_col = x
            elif (header[x] == long_colname):
                long_col = x
            elif (header[x] == shapeid_colname):
                shapeid_col = x
            elif (header[x] == site_colname):
                site_col = x
                
        if (lat_col < 0):
            return "Invalid latitude column name: " + lat_colname
    
        if (long_col < 0):
            return "Invalid longitude column name: " + long_colname
    
        if (shapeid_col < 0):
            return "Invalid shape ID column name: " + shapeid_colname
        
        if (site_col < 0):
            return "Invalid Site column name: " + site_colname
        
        if QFile(shapefile_name).exists():
            if not QgsVectorFileWriter.deleteShapeFile(QString(shapefile_name)):
                return "Failure deleting existing shapefile: " + shapefile_name
        
        outfile = QgsVectorLayer("Point?crs=epsg:4326", "txt_temp_centroid", "memory")
        outfile.startEditing()
        outfile_provider = outfile.dataProvider()
        outfile_provider.addAttributes( [QgsField("Site", QVariant.String)])
        
        current_shape_id = False
        reading = True
        while reading:
            try:
                row = reader.next()
            except:
                reading = False
                
            if reading and (len(row) > long_col) and (len(row) > lat_col) and (len(row) > shapeid_col) and (len(row) > site_col) \
                and is_float(row[long_col]) and is_float(row[lat_col]):

                point = QgsPoint(float(row[long_col]), float(row[lat_col]))
                                     
            else:
                point = False
                
            if point:
                geometry = QgsGeometry.fromPoint(point)
                #current_shape_id = row[shapeid_col]
                current_site = row[site_col]
                attributes = { 0 : QVariant(str(current_site)) }
                #for x in range(len(header)):
                    #QMessageBox.information(self, self.tr("Message"), self.tr(str(range(len(header)))))
                    #sys.exit(0)
                #    if x >= len(row):
                #        attributes[len(attributes)] = QVariant("")
                #    elif ((x != lat_col) and (x != long_col) and (x != shapeid_col)):
                 #       attributes[len(attributes)] = QVariant(str(row[x]))
                            
                newfeature = QgsFeature()
                newfeature.setAttributeMap(attributes)
                newfeature.setGeometry(geometry)
                outfile_provider.addFeatures([newfeature])
        
        outfile.commitChanges()
        outfile.updateExtents()  
        siterand_core.geometry(outfile, self.shapefileName, self.encoding, "txt", "NULL")
        
        return None
                
        
    
    def read_csv_header(self, filename):
        try:
            infile = open(filename, 'r')
        except:
            QMessageBox.information(qgis.mainWindow(), "Input CSV File", "Failure opening " + filename)
            return None
    
        try:
            dialect = csv.Sniffer().sniff(infile.read(2048))
        except:
            QMessageBox.information(qgis.mainWindow(), "Input CSV File", 
                "Bad CSV file - verify that your delimiters are consistent");
            return None
    
        infile.seek(0)
        reader = csv.reader(infile, dialect)
            
        header = reader.next()
        del reader
        del infile
    
        if len(header) <= 0:
            QMessageBox.information(qgis.mainWindow(), "Input CSV File", 
                filename + " does not appear to be a CSV file")
            return None
    
        return header
    
def is_float(s):
    try:
        float(s)
        return True
    except:
        return False

            
            
                 
    

    
   
        
        
        
        
        
        