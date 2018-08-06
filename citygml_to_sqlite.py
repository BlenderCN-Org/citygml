#!/bin/env python
# encoding=utf8


import os
import sys
import glob
from xml.dom import minidom
import pyproj
import citygml
from ez.lib.ezSQLite import SQLite


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



def building_to_sqlite(fn_citygml, fn_sqlite):
    print(fn_citygml, fn_sqlite)

    reader = citygml.Reader(fn_citygml)

    sq = SQLite(fn_sqlite)

    sq.dropTable('gml_polygon')
    sq.execute('''create table gml_polygon (
      gml_id text,
      num_coords integer
    )''')

    sq.dropTable("coordinates")
    sq.execute('''create table coordinates (
      gml_id text,
      seq_num integer,
      lat number,
      lon number,
      z number
    )''')
    for gml_id, coords in reader.get_buildings():
        sq.insert('gml_polygon', (gml_id, len(coords)))
        for i, coord in enumerate(coords):
            rec = [gml_id, i]
            rec.extend(coord)
            #print(rec)
            sq.insert('coordinates', rec)

    sq.close()


def texture_to_sqlite(fn_citygml, fn_sqlite):
    print(fn_citygml, fn_sqlite)

    reader = citygml.Reader(fn_citygml)

    sq = SQLite(fn_sqlite)

    sq.dropTable('texture')
    sq.execute('''create table texture (
      gml_id text,
      num_coords integer
    )''')
    sq.dropTable('texture_coords')
    sq.execute('''create table texture_coords (
      gml_id text,
      seq_num integer,
      x number,
      y number
    )''')
    for gml_id, coords in reader.get_texture_coords():
        sq.insert('texture', (gml_id, len(coords)))
        for i, coord in enumerate(coords):
            sq.insert('texture_coords', (gml_id, i, coord[0], coord[1]))

    sq.close()


def address_to_sqlite(fn_citygml, fn_sqlite):
    print(fn_citygml, fn_sqlite)
    reader = citygml.Reader(fn_citygml)
    sq = SQLite(fn_sqlite)

    sq.dropTable("addresses")
    sq.execute('''create table addresses (
      lat number,
      lon number,
      z number
    )''')
    for address in reader.get_addresses():
        sq.insert('addresses', address)

    sq.close()


def usage():
	print('''Usage: %s <city gml folder> <output sqlite folder>'''%executable)


if __name__ == '__main__':
    if len(sys.argv)!=3:
        usage()
        sys.exit()
    
    fd_citygml = sys.argv[1]
    fd_sqlite = sys.argv[2]

    try:
        os.makedirs(fd_sqlite)
    except:
        pass

    for fn_citygml in glob.glob(os.path.join(fd_citygml, '*.gml'))[:1]:
        basename = os.path.basename(fn_citygml)
        basename = basename[:-4]
        fn_sqlite = os.path.join(fd_sqlite, basename)
        building_to_sqlite(fn_citygml, fn_sqlite+'.sq3')
        address_to_sqlite(fn_citygml, fn_sqlite+'.sq3')
        texture_to_sqlite(fn_citygml, fn_sqlite+'.sq3')
