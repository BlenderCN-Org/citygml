#!/bin/env python
# encoding=utf8

"""
author:     Eric Zhang(snow31450588@gmail.com)
purpose:    Automatically Import, Triangulate, Export OBJ files
history:
    2018-09-03  Initial version

bpy.ops.import_scene.obj(filepath="", axis_forward='-Z', axis_up='Y', filter_glob="*.obj;*.mtl", use_edges=True, use_smooth_groups=True, use_split_objects=True, use_split_groups=True, use_groups_as_vgroups=False, use_image_search=True, split_mode='ON', global_clamp_size=0)

bpy.ops.export_scene.obj(filepath="", check_existing=True, axis_forward='-Z', axis_up='Y', filter_glob="*.obj;*.mtl", use_selection=False, use_animation=False, use_mesh_modifiers=True, use_mesh_modifiers_render=False, use_edges=True, use_smooth_groups=False, use_smooth_groups_bitflags=False, use_normals=True, use_uvs=True, use_materials=True, use_triangles=False, use_nurbs=False, use_vertex_groups=False, use_blen_objects=True, group_by_object=False, group_by_material=False, keep_vertex_order=False, global_scale=1, path_mode='AUTO')
"""


import os
import glob


def main(fd_in, fd_out):
    bpy.ops.object.delete()
    for i,fn_in in enumerate(glob.glob(os.path.join(fd_in, '*.obj'))):
        basename = os.path.basename(fn_in)
        fn_out = os.path.join(fd_out, basename)
        bpy.ops.object.select_all(action="DESELECT")
        bpy.ops.import_scene.obj(filepath=fn_in)
        for key, val in bpy.context.scene.objects.items():
            if val.type == 'MESH':
                bpy.context.scene.objects[key].select = True
                bpy.context.scene.objects.active = bpy.data.objects[key]
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
        bpy.ops.export_scene.obj(filepath=fn_out, path_mode='COPY')
        bpy.ops.object.delete()


