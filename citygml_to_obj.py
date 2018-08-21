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


def building_to_mtl(reader, fn_mtl):
    f_mtl = open(fn_mtl+'.mtl', 'wb')
    imgURI = reader.get_imageURI()
    imgURI = os.path.split(imgURI)[-1]
    f_mtl.write(('''newmtl Material.001
Ns 96.078431
Ka 1.000000 1.000000 1.000000
Kd 0.640000 0.640000 0.640000
Ks 0.500000 0.500000 0.500000
Ke 0.000000 0.000000 0.000000
Ni 1.000000
d 1.000000
illum 2
map_Kd %s'''%imgURI).encode('utf8'))
    f_mtl.close()


def building_to_obj(fn_citygml, fn_obj):
    print(fn_citygml, fn_obj)
    reader = citygml.Reader(fn_citygml)
    building_to_mtl(reader, fn_obj)

    f_obj = open(fn_obj+'.obj', 'wb')

    f_obj.write(("mtllib %s.mtl%s"%(os.path.split(fn_obj)[-1], os.linesep)).encode("utf8"))

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
        #coords = [(coord[0]-coord_first[0], coord[1]-coord_first[1], coord[2]-coord_first[2]) for coord in coords]
        idx = range(len(coords))
        idx = ['%d/%d'%(i+1+len(coord_list), i+1+len(coord_list)) for i in idx]
        polygon_list.append(' '.join(idx))
        coord_list.extend(coords)

        for lon, lat, z in coords:
            f_obj.write(("v %.16f %.16f %.16f%s"%(lon, lat*1, z*1, os.linesep)).encode('utf8'))


    for polygon_id, polygon_coords in reader.get_buildings():
        texture_coords = reader.get_texture_coords(polygon_id)
        if polygon_id and texture_coords:
            for x, y in texture_coords:
                f_obj.write(("vt %.16f %.16f%s"%(x, y, os.linesep)).encode('utf8'))
        else:
            for coord in polygon_coords:
                f_obj.write(("vt 0 0%s"%os.linesep).encode('utf8'))



    f_obj.write(("%sg polygon%s"%(os.linesep, os.linesep)).encode("utf8"))


    f_obj.write(("usemtl Material.001%s"%(os.linesep,)).encode("utf8"))

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

    for fn_citygml in glob.glob(os.path.join(fd_citygml, '*.gml'))[:]:
        basename = os.path.basename(fn_citygml)
        basename = basename[:-4]
        fn_obj = os.path.join(fd_obj, basename)
        building_to_obj(fn_citygml, fn_obj+'_building')
