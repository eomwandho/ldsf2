from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import gftools_utils
from random import *
import math, csv, os.path

country_dict = {"CI":"Cote d'Ivoire","GH":"Ghana","BI":"Burundi","LR":"Liberia",
                "EH":"Western Sahara","MA":"Morocco","BF":"Burkina Faso","DJ":"Djibouti",
                "RE":"Reunion","GN":"Guinea","GW":"Guinea-Bissau","ML":"Mali",
                "GQ":"Equatorial Guinea","MR":"Mauritania","SC":"Seychelles",
                "SN":"Senega","SL":"Sierra Leone","GM":"The Gambia","ER":"Eritrea",
                "ET":"Ethiopia","SD":"Sudan","UG":"Uganda","DZ":"Algeria","CM":"Cameroon",
                "CF":"Central African Republic","LY":"Libya","LS":"Lesotho","TN":"Tunisia",
                "NA":"Namibia","MG":"Madagascar","MU":"Mauritius","BJ":"Benin","TG":"Togo",
                "EG":"Egypt","SO":"Somalia","TD":"Chad","NE":"Niger","NG":"Nigeria",
                "ST":"Sao Tome & Principe","BW":"Botswana","YT":"Mayotte","KE":"Kenya",
                "RW":"Rwanda","TZ":"Tanzania","ZM":"Zambia","ZW":"Zimbabwe","KM":"Comoros",
                "MW":"Malawi","MZ":"Mozambique","ZA":"South Africa","SZ":"Swaziland",
                "AO":"Angola","CG":"Congo","CD":"Congo DRC","GA":"Gabon"}

w = "w"; c = "c"

country_path =  os.path.join(os.path.dirname(__file__), "country.csv")
wrs_path = os.path.join(os.path.dirname(__file__), "wrs2.csv")

q_country_dict = {}
q_wrs_dict = {}

def csv_gen(path, dictionary, typ):
    infile = open(path, 'r')
    infile.seek(0)
    reader = csv.reader(infile)
    header = reader.next()
    reading = True
    while reading:
        try:
            row = reader.next()
        except:
            reading = False
        if reading:
            if typ == c: dictionary[row[0]] = QgsGeometry().fromWkt(row[2])
            elif typ == w: dictionary[str(row[0]) + str(row[1])] = QgsGeometry().fromWkt(row[2])
        else:
            layer = False

csv_gen(country_path, q_country_dict, c)
csv_gen(wrs_path, q_wrs_dict, w)

def geometry(myLayer, shapefileName, encoding, type, site):
    if type == "pp":
        myLayer = gftools_utils.getVectorLayerByName( unicode(myLayer) )
        site = "NULL"
    elif type == "csv":
        myLayer = myLayer
        site = "NULL"
    elif type == "ext":
        myLayer = myLayer
        site = site
    if myLayer.type() == myLayer.VectorLayer:
        vprovider = myLayer.dataProvider()
        allAttrs = vprovider.attributeIndexes()
        vprovider.select(allAttrs)
        v1 = QgsVectorLayer("Point?crs=epsg:4326", "temp_centroid", "memory")
        v1.startEditing()
        pr = v1.dataProvider()
        pr.addAttributes( [QgsField("Country", QVariant.String),QgsField("Code", QVariant.String), 
                           QgsField("wrs2Path", QVariant.String), QgsField("wrs2Row", QVariant.String),
                           QgsField("Site", QVariant.String)] )
        inFeat = QgsFeature()
        outFeat = QgsFeature()
        nElement = 0
        while vprovider.nextFeature(inFeat):
            nElement += 1
            inGeom = inFeat.geometry()
            atMap = inFeat.attributeMap()
            for (k,attr) in atMap.iteritems():
                if k == 0:
                    indCSVSite = 4; attrCSV = attr.toString()
                #elif attr.toString() == "site" : attrCSV =  attr.toString()
            if type == "ext":
                  attrCSV = site
            outGeom = QgsGeometry(inGeom.centroid())
            for k,v in q_country_dict.iteritems():
                if outGeom.intersects(v):
                    country = k
                    break
                elif not outGeom.intersects(v):
                    country = "NULL"
            if country == "NULL":
                country_name = "NULL"
            elif not country == "NULL":
                country_name = country_dict[country]
            for k,v in q_wrs_dict.iteritems():
                if outGeom.intersects(v):
                    wrs = k         
            outFeat.setAttributeMap({0 : QVariant(country_name),1 : QVariant(country), 
                                     2 : QVariant(wrs[0:3]), 3 : QVariant(wrs[3:5]),
                                     4 : QVariant(attrCSV)})
            outFeat.setGeometry(outGeom)
            pr.addFeatures([outFeat])
        
        v1.commitChanges()
        v1.updateExtents()
        
        allAttrs = pr.attributeIndexes()
        pr.select(allAttrs)
        v_buffer = QgsVectorLayer("Polygon?crs=epsg:4326", "temp_buffer", "memory")
        v_buffer.startEditing()
        pr_buffer = v_buffer.dataProvider()
        pr_buffer.addAttributes( [QgsField("Country", QVariant.String), QgsField("Code", QVariant.String), 
                                  QgsField("wrs2Path", QVariant.String), QgsField("wrs2Row", QVariant.String),
                                  QgsField("Site", QVariant.String)] )
        inFeat_centroid = QgsFeature()
        outFeat_buffer = QgsFeature()
        nElement = 0
        while pr.nextFeature(inFeat_centroid):
            nElement += 1
            inGeom_centroid = inFeat_centroid.geometry()
            atMap_centroid = inFeat_centroid.attributeMap()
            outGeom_buffer = QgsGeometry(inGeom_centroid.buffer(0.05,10))
            outFeat_buffer.setAttributeMap(atMap_centroid)
            outFeat_buffer.setGeometry(outGeom_buffer)
            pr_buffer.addFeatures([outFeat_buffer])
        
        v_buffer.commitChanges()
        v_buffer.updateExtents()

        allAttrs_buffer = pr_buffer.attributeIndexes()
        pr_buffer.select(allAttrs_buffer)
        v_grid = QgsVectorLayer("Polygon?crs=epsg:4326", "temp_grid", "memory")
        v_grid.startEditing()
        pr_grid = v_grid.dataProvider()
        pr_grid.addAttributes( [QgsField("Country", QVariant.String), QgsField("Code", QVariant.String), 
                                QgsField("wrs2Path", QVariant.String), QgsField("wrs2Row", QVariant.String),
                                QgsField("Site", QVariant.String)] )
        in_buffer = QgsFeature()
        out_grid = QgsFeature()
        out_geom = QgsGeometry()
        nElement = 0
        cnt = 0
        while pr_buffer.nextFeature(in_buffer):
            geom = in_buffer.geometry()
            atMap_buffer = in_buffer.attributeMap()
            cnt += 1
            x = geom.asPolygon()
            x = str(x).strip('[()]')
            lon = []; lat = []
            x = x.split("), (")
            for b in x:
                c = b.split(",")
                lon.append(float(str(c[:1]).strip("[]").strip("'")))
                lat.append(float(str(c[1:2]).strip("[]").strip("'")))
            xOffset = (max(lon) - min(lon))/ 4
            yOffset = (max(lat) - min(lat))/ 4
            y = max(lat)
            count = 0
            while y >= min(lat):
                x = min(lon)
                while x <= max(lon):
                    glinc = 0.005076
                    x0 = x + xOffset
                    y0 = y - yOffset
                    if not (x0 > max(lon) and x < min(lon) and y0 < min(lat) and y > max(lat)) :
                        pt1 = QgsPoint(x + glinc, y - glinc)
                        pt2 = QgsPoint(x0 - glinc, y - glinc)
                        pt3 = QgsPoint(x0 - glinc, y0 + glinc)
                        pt4 = QgsPoint(x + glinc, y0 + glinc)
                        pt5 = QgsPoint(x + glinc, y - glinc)
                        count += 1
                        if geom.intersects(QgsGeometry().fromPolygon([[pt1, pt2, pt3, pt4, pt5]])):
                            out_grid.setGeometry(QgsGeometry().fromPolygon([[pt1, pt2, pt3, pt4, pt5]]))
                            out_grid.setAttributeMap(atMap_buffer)
                            pr_grid.addFeatures([out_grid])
                    else:
                        pass
                    x = x + xOffset
                y = y - yOffset
        
        v_grid.commitChanges()
        v_grid.updateExtents()
        
        
        allAttrs_buffer = pr_grid.attributeIndexes()
        pr_grid.select(allAttrs_buffer)
        grid_centroid = QgsVectorLayer("Point?crs=epsg:4326", "temp_grid_centroid", "memory")
        grid_centroid.startEditing()
        pr_grid_centroid = grid_centroid.dataProvider()
        pr_grid_centroid.addAttributes( [QgsField("Country", QVariant.String), QgsField("Code", QVariant.String), 
                                         QgsField("wrs2Path", QVariant.String), QgsField("wrs2Row", QVariant.String),
                                         QgsField("Site", QVariant.String)] )
        inGrid = QgsFeature()
        outGrid_Rand = QgsFeature()
        while pr_grid.nextFeature(inGrid):
            geom = inGrid.geometry()
            atMap_grid_centroid = inGrid.attributeMap()
            x = geom.asPolygon()
            x = str(x).strip('[()]')
            lon = []; lat = []
            x = x.split("), (")
            for b in x:
                c = b.split(",")
                lon.append(float(str(c[:1]).strip("[]").strip("'")))
                lat.append(float(str(c[1:2]).strip("[]").strip("'")))
            outGrid_Rand.setGeometry(QgsGeometry().fromPoint(QgsPoint(min(lon) + (max(lon) - min(lon))* random(),min(lat) + (max(lat) - min(lat)) * random())))
            outGrid_Rand.setAttributeMap(atMap_grid_centroid)
            pr_grid_centroid.addFeatures([outGrid_Rand])
        
        grid_centroid.commitChanges()
        grid_centroid.updateExtents()
        
        allAttrs_grid_centroid = pr_grid_centroid.attributeIndexes()
        pr_grid_centroid.select(allAttrs_grid_centroid)
        grid_centroid_buffer = QgsVectorLayer("Polygon?crs=epsg:4326", "temp_centroid_buffer", "memory")
        grid_centroid_buffer.startEditing()
        pr_centroid_buffer = grid_centroid_buffer.dataProvider()
        pr_centroid_buffer.addAttributes( [QgsField("Country", QVariant.String), QgsField("Code", QVariant.String), 
                                           QgsField("wrs2Path", QVariant.String), QgsField("wrs2Row", QVariant.String),
                                           QgsField("Site", QVariant.String), QgsField("Cluster", QVariant.Int)] )
        inGrid_Centroid = QgsFeature()
        outGrid_Centroid_Buffer = QgsFeature()
        count = 1
        while pr_grid_centroid.nextFeature(inGrid_Centroid):
            inGrid_Geom_centroid = inGrid_Centroid.geometry()
            atMap_grid_centroid_buffer = inGrid_Centroid.attributeMap()
            for (k,attr) in atMap_grid_centroid_buffer.iteritems():
                if k == 0:
                    indCountry = k; attrCountry = attr.toString()
                elif k == 1:
                    indCode = k; attrCode = attr.toString()
                elif k == 2:
                    indwrs2Path = k; attrwrs2Path = attr.toString()
                elif k == 3:
                    indwrs2Row = k; attrwrs2Row = attr.toString()
                elif k == 4:
                    indSite = k; attrSite = attr.toString()
            if count == 17: count = 1
            if count == 1: site_in = 4
            elif count == 2: site_in = 8
            elif count == 3: site_in = 12
            elif count == 4: site_in = 16
            elif count == 5: site_in = 3
            elif count == 6: site_in = 7
            elif count == 7: site_in = 11
            elif count == 8: site_in = 15
            elif count == 9: site_in = 2
            elif count == 10: site_in = 6
            elif count == 11: site_in = 10
            elif count == 12: site_in = 14
            elif count == 13: site_in = 1
            elif count == 14: site_in = 5
            elif count == 15: site_in = 9
            elif count == 16: site_in = 13
            outGrid_Geom_buffer = QgsGeometry(inGrid_Geom_centroid.buffer(0.00564,10))
            outGrid_Centroid_Buffer.setGeometry(outGrid_Geom_buffer)
            outGrid_Centroid_Buffer.setAttributeMap({indCountry : QVariant(attrCountry), indCode : QVariant(attrCode), 
                                                     indwrs2Path : QVariant(attrwrs2Path), indwrs2Row : QVariant(attrwrs2Row),
                                                     indSite : QVariant(attrSite) , 5 :  QVariant(site_in)})
            pr_centroid_buffer.addFeatures([outGrid_Centroid_Buffer])
            count += 1
        
        grid_centroid_buffer.commitChanges()
        grid_centroid_buffer.updateExtents()
        
        allAttrs_centroid_buffer = pr_centroid_buffer.attributeIndexes()
        pr_centroid_buffer.select(allAttrs_centroid_buffer)
        fields = { 0 : QgsField("Country", QVariant.String), 1 : QgsField("Code", QVariant.String), 
                  2 : QgsField("wrs2Path", QVariant.String), 3 : QgsField("wrs2Row", QVariant.String),
                  4 : QgsField("SiteName", QVariant.String), 5 : QgsField("ldsfID", QVariant.String), 
                  6 :  QgsField("Cluster", QVariant.String), 7 : QgsField("Plot", QVariant.String), 
                  8 : QgsField("X", QVariant.String), 9 : QgsField("Y", QVariant.String )}
        crs = QgsCoordinateReferenceSystem()
        crs.createFromSrid(4326)
        writer = QgsVectorFileWriter(shapefileName, encoding, fields, QGis.WKBPoint, crs)
        inGrid_buffer = QgsFeature()
        outCluster_points = QgsFeature()
        while pr_centroid_buffer.nextFeature(inGrid_buffer):
            countin = 1
            rand_points_dic = {}
            count = 1
            geom = inGrid_buffer.geometry()
            atMap_cluster_points = inGrid_buffer.attributeMap()
            for (k,attr) in atMap_cluster_points.iteritems():
                if k == 0:
                    indCountry = k; attrCountry = attr.toString()
                elif k == 1:
                    indCode = k; attrCode = attr.toString()
                elif k == 2:
                    indwrs2Path = k; attrwrs2Path = attr.toString()
                elif k == 3:
                    indwrs2Row = k; attrwrs2Row = attr.toString()
                elif k == 4:
                    indSite = 4; attrSite = attr.toString()
                elif k == 5:
                    indCluster = 5; attrCluster = attr.toString()

            x = geom.asPolygon()
            lon = []; lat = []
            while count <= 15:
                if count == 1:
                    pntValid = False
                    cnt = str(countin) + str(count)
                    while pntValid == False:
                        pnt = (randpointgen(x))
                        if geom.intersects(QgsGeometry().fromPoint(QgsPoint(pnt[0],pnt[1]))):
                            rand_points_dic[int(cnt)] = pnt
                            pntValid = True
                        else:
                            pntValid = False
                else:
                    pntValid = False
                    while pntValid == False:
                        pnt = randpointgen(x)
                        for k,v in rand_points_dic.iteritems():
                            long1, lat1 = pnt
                            long2, lat2 = v
                            val, dist = distance_on_unit_sphere(lat1, long1, lat2, long2)
                            if val and geom.intersects(QgsGeometry().fromPoint(QgsPoint(pnt[0],pnt[1]))):
                                pntValid = True
                            else:
                                pntValid = False
                                break
                    cnt = str(countin) + str(count)
                    rand_points_dic[cnt] = pnt
                    cnt_field = count
                count = count + 1
            countin = countin + 1
            
            for k in sorted(rand_points_dic.iterkeys()):
                site_name = attrCode + "." + attrSite + "." + attrCluster + "." + str(k)[1:]
                outCluster_points.setGeometry(QgsGeometry().fromPoint(QgsPoint(rand_points_dic[k][0],rand_points_dic[k][1])))
                outCluster_points.addAttribute(0, QVariant(attrCountry))
                outCluster_points.addAttribute(1, QVariant(attrCode))
                outCluster_points.addAttribute(2, QVariant(attrwrs2Path))
                outCluster_points.addAttribute(3, QVariant(attrwrs2Row))
                outCluster_points.addAttribute(4, QVariant(attrSite))
                outCluster_points.addAttribute(5, QVariant(site_name))
                outCluster_points.addAttribute(6, QVariant(attrCluster))
                outCluster_points.addAttribute(7, QVariant(str(k)[1:]))
                outCluster_points.addAttribute(8, QVariant(str(rand_points_dic[k][0])))
                outCluster_points.addAttribute(9, QVariant(str(rand_points_dic[k][1])))
                
                writer.addFeature(outCluster_points)
        del writer
        
def distance_on_unit_sphere(lat1, long1, lat2, long2):

    degrees_to_radians = math.pi/180.0
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )
    
    dist = arc*6373000
    
    if dist < 50:
        return 0, dist
    else:
        return 1, dist
    
def randpointgen(a):
    a = str(a).strip('[()]').split("), (")
    lon = []; lat = []
    for b in a:
        c = b.split(",")
        lon.append(float(c[0]))
        lat.append(float(c[1]))
    randPnt = (min(lon) + (max(lon) - min(lon))* random()), (min(lat) + (max(lat) - min(lat)) * random())
    
    return randPnt



            
            