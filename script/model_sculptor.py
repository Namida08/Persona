# coding: UTF-8
import bpy
import math
import sys
import numpy as np
sys.path.append("/home/yaku/work/model_sculptor/script")
from model import Model
from landmark import Landmark

#Blenderの命令を使用して変形を行うクラス
class ModelSculptor:
    MODEL_NAME = ""
    
    #変形の影響を受けない部分の頂点インデックス
    FIXED_INDEX = []

    #左眼孔を構成する座標index 24点
    LE_INDEX = [47,58,65,71,74,77,87,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107]
    #右眼孔を構成する座標index 24点
    RE_INDEX = [178,188,195,201,204,207,219,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239]

    #左眼孔周辺座標index 26点
    LER_INDEX = [50,51,54,56,57,61,70,73,88,89,109,120,121,122,123,124,125,140,142,144,145,146,148,149,150,151]
    #右眼孔周辺座標index 26点
    RER_INDEX = [180,181,184,186,187,191,200,203,220,221,241,252,253,254,255,256,257,272,274,276,277,278,280,281,282,283]

    ALLOWABLE_ERROR = 0.3
    completion_count = 0

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
        self.model.add_landmark(11, 101, [58, 101, 97]) 
        self.model.add_landmark(12, 104, [94, 104, 95]) 
        self.model.add_landmark(13, 100, [92, 100, 93])
        
        self.model.add_landmark(14, 30, [30, 20, 28, 29])
        self.model.add_landmark(15, 23, [23, 22, 27, 31])
        self.model.add_landmark(16, 24, [24, 25, 33, 38, 36, 37])
        self.model.add_landmark(17, 10, [10, 8, 9, 0])
        self.model.add_landmark(18, 3, [3, 2, 7, 11])
        self.model.add_landmark(19, 4, [4, 5, 13, 18, 16, 17])
        #self.model.add_landmark(20, 434, [434])

        #ラプラシアン変形の影響を受けない頂点インデックス設定
        for i in range(0, len(self.model.get_vertices())):
            flag = False

            for j,landmark in enumerate(self.model.get_landmarks()):
                for z,part in enumerate(landmark.get_part_indexes()):
                    if i == part:
                        flag = True
                        break
                
            for j,index in enumerate(self.LE_INDEX):
                if i == index:
                    flag = True
                    break
            for j,index in enumerate(self.RE_INDEX):
                if i == index:
                    flag = True
                    break
            for j,index in enumerate(self.LER_INDEX):
                if i == index:
                    flag = True
                    break
            for j,index in enumerate(self.RER_INDEX):
                if i == index:
                    flag = True
                    break

            if not(flag):
                self.FIXED_INDEX.append(i)

        self.model.add_landmark(-1, self.FIXED_INDEX[0], self.FIXED_INDEX)


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
            #モディファイアの中心座標を特徴点対応頂点にする 機能してない？
            #bpy.context.scene.cursor_location = bpy.context.active_object.matrix_world * self.model.get_vertex(landmark).co
            #bpy.ops.object.hook_recenter(modifier = self._get_modifier_name(i))
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
        
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.mode_set(mode='OBJECT')
        #ラプラシアン変形モディファイアでメッシュに関連付け
        bpy.ops.object.laplaciandeform_bind(modifier="LaplacianDeform")

    #3次元点同士の距離
    def _get_3d_point_distance(self, p1, p2):
        return math.sqrt(pow((p1.x - p2[0]), 2) + pow((p1.y - p2[1]), 2) + pow((p1.z - p2[2]), 2))

    #変形
    def _empty_locatuion_update(self):
        movement = [0] * len(self.model.get_landmarks())
        for i,landmark in enumerate(self.model.get_landmarks()):
            if (landmark.has_index()):
                movement[i] = self.model.get_movement_vertex(landmark, self._get_temporary_object(i).location)
                self._get_temporary_object(i).location = movement[i]
                
        for i,landmark in enumerate(self.model.get_landmarks()):
            if (landmark.has_index()):
                #Hookモディファイアを適応し削除
                bpy.ops.object.modifier_apply(apply_as = 'DATA', modifier = self._get_modifier_name(i))
            else:
                #Hookモディファイアを削除
                bpy.ops.object.modifier_remove(modifier = self._get_modifier_name(i))

        #ラプラシアンモディファイアを適応し削除
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier='LaplacianDeform')

        self.completion_count = 0
        for i,landmark in enumerate(self.model.get_landmarks()):
            if (not(landmark.has_index())):
                self.completion_count += 1
            elif self._get_3d_point_distance(self.model.get_vertex(landmark), movement[i]) < self.ALLOWABLE_ERROR:
                print(i, self._get_3d_point_distance(self.model.get_vertex(landmark), movement[i]))
                self.completion_count += 1
            else:
                print(i, self._get_3d_point_distance(self.model.get_vertex(landmark), movement[i]))

    #一時生成物削除
    def _cleanup(self):
        #オブジェクト削除
        for i,landmark in enumerate(self.model.get_landmarks()):
            self._get_temporary_object(i).select = True
        bpy.ops.object.delete()
        
        #アクティブな頂点グループを削除
        bpy.ops.object.vertex_group_remove(all=False)
   
    #変形完了したかの判定
    def _get_completion_flag(self):
        return self.completion_count != len(self.model.get_landmarks())

    #頂点座標データファイル書き込み
    #in: ファイル名 
    #out: 特徴点座標の配列
    def _write_vertex_result(self, file_name):
        f = open(file_name, "w", encoding='utf-8')
        for i,vertex in enumerate(self.model.get_vertices()):
            f.write(str(i) + ":" + str(vertex.co) + "\n")
        f.close()


    def run(self):
        while self._get_completion_flag():
            self._create_hook_modifier()
            self._laplaciandeform_bind()
            self._empty_locatuion_update()
            self._cleanup()
            print("-----------------------------------------")
        self._write_vertex_result("result.txt")
        return True


        