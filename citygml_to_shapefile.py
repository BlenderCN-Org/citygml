#!/bin/env python
# encoding=utf8


import os
import sys
import glob
from xml.dom import minidom
import pyproj
import ez.lib.ezShapefile as shapefile


frozen = getattr(sys, 'frozen', '')
if not frozen:
    # not frozen: in regular python interpreter
    executable = __file__
elif frozen in ('dll', 'console_exe', 'windows_exe'):
    # frozen: standalone executable
    executable = sys.executable


PRJ_STRING = b'''GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433],AUTHORITY["EPSG",4326]]'''


def project_coordinate(epsg, x, y):
    p = pyproj.Proj(init=epsg)
    lat, lon = p(x, y, inverse=True)
    return lat, lon


def write_prjfile(fn_prj, prj_string):
    with open(fn_prj, 'wb') as f:
        f.write(prj_string)


def building_to_shapefile(fn_citygml, fn_shapefile):
    print(fn_citygml, fn_shapefile)
    wr = shapefile.writer(fn_shapefile, shapefile.PolygonZ)
    wr.addField('ID')
    with open(fn_citygml, 'rb') as f:
        ls = f.read()
        doc=minidom.parseString(ls)
        #node_core = doc.getElementsByTagName('core:CityModel')[0]
        node_building = doc.getElementsByTagName('bldg:Building')[0]
        for node_posList in doc.getElementsByTagName('gml:posList'):
            coords = []
            for pos in node_posList.childNodes[0].nodeValue.splitlines():
                if pos:
                    x,y,z = pos.split()
                    x,y,z = float(x), float(y), float(z)
                    lat, lon = project_coordinate("EPSG:3414", x, y)
                    coords.append((lat, lon, z, 0))
            wr.shapePolygonZ([coords])
            wr.record((1,))
    wr.close()

    write_prjfile(fn_shapefile+'.prj', PRJ_STRING)


def address_to_shapefile(fn_citygml, fn_shapefile):
    print(fn_citygml, fn_shapefile)
    wr = shapefile.writer(fn_shapefile, shapefile.PolyLineZ)
    wr.addField('ID')
    with open(fn_citygml, 'rb') as f:
        ls = f.read()
        doc=minidom.parseString(ls)
        #node_core = doc.getElementsByTagName('core:CityModel')[0]
        for node_pos in doc.getElementsByTagName('gml:pos'):
            coords = []
            x,y,z = node_pos.childNodes[0].nodeValue.split()
            x,y,z = float(x), float(y), float(z)
            lat, lon = project_coordinate("EPSG:3414", x, y)
            #print(x,y,z)
            wr.shapePolylineZ([[(lat, lon, z-10, 0),(lat, lon, z+100, 0)]])
            wr.record((1,))
    wr.close()

    write_prjfile(fn_shapefile+'.prj', PRJ_STRING)


def usage():
	print('''Usage: %s <city gml folder> <output shapefile folder>'''%executable)


if __name__ == '__main__':
    if len(sys.argv)!=3:
        usage()
        sys.exit()
    
    fd_citygml = sys.argv[1]
    fd_shapefile = sys.argv[2]

    try:
        os.makedirs(fd_shapefile)
    except:
        pass

    for fn_citygml in glob.glob(os.path.join(fd_citygml, '*.gml'))[:]:
        basename = os.path.basename(fn_citygml)
        basename = basename[:-4]
        fn_shapefile = os.path.join(fd_shapefile, basename)
        building_to_shapefile(fn_citygml, fn_shapefile+'_building')
        address_to_shapefile(fn_citygml, fn_shapefile+'_address')
