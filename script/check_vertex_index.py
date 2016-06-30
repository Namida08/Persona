import bpy

bpy.ops.object.mode_set(mode='OBJECT')
i = 0
for v in bpy.data.objects['EYE_DEF'].data.vertices:
    if v.select:
        print(i)
    i =i + 1 
  #  print(i)
bpy.ops.object.mode_set(mode='EDIT')

