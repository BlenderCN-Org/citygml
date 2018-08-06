#!/bin/env python
# encoding=utf8


import os
import sys
import glob
from xml.dom import minidom
import pyproj


def project_coordinate(epsg, x, y):
    p = pyproj.Proj(init=epsg)
    lat, lon = p(x, y, inverse=True)
    return lat, lon


class Reader():
    def __init__(self, filename):
        #self._filename = filename
        self._coords = []
        self._buildings = []
        self._addresses = []
        self._texture_coords = []
        self.parse(filename)

    def parse(self, filename):
        self._filename = filename
        with open(self._filename, 'rb') as f:
            ls = f.read()
            doc = minidom.parseString(ls)
            self._parse_building(doc)
            self._parse_address(doc)
            self._parse_appearance(doc)


    def _parse_appearance(self, root):
        for node_textureCoordinates in root.getElementsByTagName('app:textureCoordinates'):
            ring_id = node_textureCoordinates.getAttribute("ring")[1:]
            texture_coords = []
            #print(node_textureCoordinates)
            #print(dir(node_textureCoordinates))
            #print(node_textureCoordinates.nodeValue)
            pss = node_textureCoordinates.childNodes[0].nodeValue.strip().split()
            for i in range(len(pss)//2):
                x = pss[i*2]
                y = pss[i*2+1]
                x,y = float(x), float(y)
                texture_coords.append((x, y))
            if texture_coords:
                self._texture_coords.append((ring_id, texture_coords))


    def _parse_building(self, root):
        #node_building = root.getElementsByTagName('bldg:Building')[0]
        for node_linearRing in root.getElementsByTagName('gml:LinearRing'):
            linearRing_id = node_linearRing.getAttribute("gml:id")
            #gml:exterior''
            node_posList = node_linearRing.getElementsByTagName('gml:posList')[0]
            building_coords = []
            for pos in node_posList.childNodes[0].nodeValue.splitlines():
                if pos:
                    x,y,z = pos.split()
                    x,y,z = float(x), float(y), float(z)
                    #lat, lon = project_coordinate("EPSG:3414", x, y)
                    lat, lon = x, y
                    self._coords.append((lat, lon, z))
                    building_coords.append((lat, lon, z))
            if building_coords:
                self._buildings.append((linearRing_id, building_coords))


    def _parse_address(self, root):
        for node_pos in root.getElementsByTagName('gml:pos'):
            x,y,z = node_pos.childNodes[0].nodeValue.split()
            x,y,z = float(x), float(y), float(z)
            lat, lon = project_coordinate("EPSG:3414", x, y)
            self._addresses.append((lat, lon, z))



    def get_coords(self):
        return self._coords

    def get_buildings(self):
        return self._buildings

    def get_addresses(self):
        return self._addresses

    def get_texture_coords(self):
        return self._texture_coords

