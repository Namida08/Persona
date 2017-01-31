# coding: UTF-8
import bpy
import math
import sys
sys.path.append("/home/yaku/work/model_sculptor/script")
from model import Model
from landmark import Landmark

#Blenderの命令を使用して変形を行うクラス
class ModelSculptor:
    MODEL_NAME = ""
    MAX_VERTEX_NUM = 1024
    
    #目の周辺の変形させない部分の頂点インデックス
    LEFT_CONST = []
    
    def __init__(self, model_name, file_name, yaw_angle):
        ModelSculptor.MODEL_NAME = model_name
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.data.objects[ModelSculptor.MODEL_NAME].select = True
        #選択オブジェクトをアクティブに
        bpy.context.scene.objects.active = bpy.context.selected_objects[0]
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.mode_set(mode='OBJECT')
        
        self.model = Model(ModelSculptor.MODEL_NAME, file_name, yaw_angle)
        self.model.set_reference_point_index(20, 434)
        self.model.set_distance_points_index([0, 7], [925, 888])

        #self.model.add_landmark(0, 925, [925])
        self.model.add_landmark(1, 219, [238, 219, 235])
        self.model.add_landmark(2, 207, [195, 207, 239])
        self.model.add_landmark(3, 237, [201, 237, 178])
        self.model.add_landmark(4, 233, [188, 233, 229])
        self.model.add_landmark(5, 236, [227, 236, 226])
        self.model.add_landmark(6, 232, [225, 232, 224])
        #self.model.add_landmark(7, 888, [888])
        self.model.add_landmark(8, 87, [106, 87, 103])
        self.model.add_landmark(9, 77, [107, 77, 65])
        self.model.add_landmark(10, 105, [47, 105, 71])
        self.model.add_landmark(11, 101, [58, 101, 99]) 
        self.model.add_landmark(12, 104, [94, 104, 95]) 
        self.model.add_landmark(13, 100, [92, 100, 93])

        self.model.add_landmark(14, 30, [30, 20, 28, 29, 34, 35])
        self.model.add_landmark(15, 23, [23, 21, 22, 27, 31, 39])
        self.model.add_landmark(16, 24, [24, 25, 26, 32, 33, 36, 37, 38])
        self.model.add_landmark(17, 0, [0, 8, 9, 10, 14, 15])
        self.model.add_landmark(18, 3, [3, 1, 2, 7, 11, 19])
        self.model.add_landmark(19, 4, [4, 5, 6, 12, 13, 16, 17, 18])
        #self.model.add_landmark(20, 434, [434])  

        for i in range(0, self.MAX_VERTEX_NUM):
            for j,landmark in enumerate(self.model.get_landmarks()):
                for z,part in enumerate(landmark.get_part_indexes()):
                    if i != part:
                        self.LEFT_CONST.append(i)

        self.model.add_landmark(-1, ModelSculptor.LEFT_CONST[0], ModelSculptor.LEFT_CONST)
    

    def _get_modifier_name(self, i):
        return "Hook-Empty" + ("" if i == 0 else "." + '%03d' % i)
    
    def _get_temporary_object_name(self, i):
        return "Empty" + ("" if i == 0 else "." + '%03d' % i)

    def _get_temporary_object(self, i):
        return bpy.data.objects[self._get_temporary_object_name(i)]

        
    #入力の頂点に紐づくモディファイアを作成する
    def _create_hook_modifier(self):
        for i,landmark in enumerate(self.model.get_landmarks()):
            bpy.ops.object.mode_set(mode='OBJECT')

            self.model.set_parts_select(landmark)
            
            bpy.ops.object.mode_set(mode='EDIT')
            
            #選択したオブジェクトの頂点に紐付くHookモディファイアを作成
            bpy.ops.object.hook_add_newob()
            bpy.ops.mesh.select_all(action="DESELECT")
            #モディファイアの中心座標を特徴点対応頂点にする
            bpy.context.scene.cursor_location = bpy.context.active_object.matrix_world * self.model.get_vertex(landmark).co
            bpy.ops.object.hook_recenter(modifier = self._get_modifier_name(i))
            #bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            bpy.ops.object.mode_set(mode='OBJECT')
    
    #ラプラシアン維持の形状変形設定
    def _laplaciandeform_bind(self):
        bpy.ops.object.mode_set(mode='EDIT')
        
        #メッシュ上の影響を受ける頂点を選択
        for i,landmark in enumerate(self.model.get_landmarks()):
            bpy.ops.object.hook_select(modifier = self._get_modifier_name(i))
            
        #アクティブなオブジェクトに新しい頂点グループを追加
        bpy.ops.object.vertex_group_add()
        #アクティブな頂点グループに選択した頂点を割り当て
        bpy.ops.object.vertex_group_assign()

        #アクティブなオブジェクトにモディファイアを追加
        bpy.ops.object.modifier_add(type='LAPLACIANDEFORM')
        bpy.data.objects[ModelSculptor.MODEL_NAME].modifiers['LaplacianDeform'].vertex_group = 'Group'

        bpy.ops.object.mode_set(mode='OBJECT')
        #ラプラシアン変形モディファイアでメッシュに関連付け
        bpy.ops.object.laplaciandeform_bind(modifier="LaplacianDeform")

    #変形座標セット
    def _empty_locatuion_update(self):
        for i,landmark in enumerate(self.model.get_landmarks()):
            print(self._get_temporary_object(i).location)
            print(self.model.get_movement_vertex(landmark, self._get_temporary_object(i).location))
            self._get_temporary_object(i).location = self.model.get_movement_vertex(landmark, self._get_temporary_object(i).location)
            

    #一時生成物削除
    def _cleanup(self):
        #モディファイアを適用し、スタックから削除
        for i,landmark in enumerate(self.model.get_landmarks()):
            bpy.ops.object.modifier_apply(apply_as = 'DATA', modifier = self._get_modifier_name(i))
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier='LaplacianDeform')

        #オブジェクト削除
        for i,landmark in enumerate(self.model.get_landmarks()):
            self._get_temporary_object(i).select = True
        bpy.ops.object.delete()
        
        #アクティブな頂点グループを削除
        bpy.ops.object.vertex_group_remove(all=False)


    def run(self):
        self._create_hook_modifier()
        self._laplaciandeform_bind()
        self._empty_locatuion_update()
        self._cleanup()
        return True

