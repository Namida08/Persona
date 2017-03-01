import bpy
import bpy_extras
import math
import sys
sys.path.append("../script")
from point import Point

#頂点のindexを調べるためのコード

point_index = [925,219,207,237,233,236,232,888,87,77,105,101,104,100,30,23,24,10,3,4,434]
points = []
angle = math.radians(60)
projection_vector = Point(math.cos(angle), math.sin(angle))

bpy.ops.object.mode_set(mode='OBJECT')


for p in point_index:
    i = 0
    for v in bpy.data.objects['MTH_DEF'].data.vertices:
        if i == p:
            points.append(Point(v.co.x, v.co.z))
        i += 1 

for p in points:
    p = p - points[20]

for p in points:
    print(p.get_projection_vector_distance(projection_vector))


bpy.ops.object.mode_set(mode='EDIT')

