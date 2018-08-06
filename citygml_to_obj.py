#!/bin/env python
# encoding=utf8


import os
import sys
import glob
from xml.dom import minidom
import pyproj
import citygml


frozen = getattr(sys, 'frozen', '')
if not frozen:
    # not frozen: in regular python interpreter
    executable = __file__
elif frozen in ('dll', 'console_exe', 'windows_exe'):
    # frozen: standalone executable
    executable = sys.executable


def project_coordinate(epsg, x, y):
    p = pyproj.Proj(init=epsg)
    lat, lon = p(x, y, inverse=True)
    return lat, lon


def write_prjfile(fn_prj, prj_string):
    with open(fn_prj, 'wb') as f:
        f.write(prj_string)


def building_to_obj(fn_citygml, fn_obj):
    print(fn_citygml, fn_obj)
    reader = citygml.Reader(fn_citygml)
    f_obj = open(fn_obj+'.obj', 'wb')

    coord_list = []
    polygon_list = []
    coord_first = None
    for polygon_id, polygon_coords in reader.get_buildings():
        coords = []
        for coord in polygon_coords:
            lat, lon, z = coord
            coords.append((lat, lon, z))
            #if coords[0]==coords[-1]:
            #    del coords[-1]
            if not coord_first:
                coord_first = coords[0]
        coords = [(coord[0]-coord_first[0], coord[1]-coord_first[1], coord[2]-coord_first[2]) for coord in coords]
        idx = range(len(coords))
        idx = ['%d'%(i+1+len(coord_list)) for i in idx]
        polygon_list.append(' '.join(idx))
        coord_list.extend(coords)

        for lat, lon, z in coords:
            f_obj.write(("v %f %f %f%s"%(lat, lon, z, os.linesep)).encode('utf8'))

    f_obj.write(("%sg polygon%s"%(os.linesep, os.linesep)).encode("utf8"))

    for polygon in polygon_list:
        f_obj.write(("f %s%s"%(polygon, os.linesep)).encode('utf8'))

    f_obj.close()


def usage():
	print('''Usage: %s <city gml folder> <output obj folder>'''%executable)


if __name__ == '__main__':
    if len(sys.argv)!=3:
        usage()
        sys.exit()
    
    fd_citygml = sys.argv[1]
    fd_obj = sys.argv[2]

    try:
        os.makedirs(fd_obj)
    except:
        pass

    for fn_citygml in glob.glob(os.path.join(fd_citygml, '*.gml'))[:1]:
        basename = os.path.basename(fn_citygml)
        basename = basename[:-4]
        fn_obj = os.path.join(fd_obj, basename)
        building_to_obj(fn_citygml, fn_obj+'_building')
