# coding: UTF-8
import bpy
import math
import sys
sys.path.append("/home/yaku/work/model_sculptor/script")
from model import Model
from landmark import Landmark

#Blenderの命令を使用して変形を行うクラス
class ModelSculptor:
    MODEL_NAME = "HTM_DEF"
    
    #目の周辺の変形させない部分の頂点インデックス
    #LEFT_CONST = [30, 33, 32, 120, 122, 125, 320, 312, 311, 314, 319, 289, 315, 296, 294, 324, 288, 285, 287, 23, 28, 29, 130, 138, 139, 135, 134, 362, 113, 115, 116, 119, 20, 19, 3, 15, 123, 124, 126, 322, 310, 313, 290, 309, 292, 291, 316, 297, 295, 293, 323, 286, 301, 14, 22, 25, 26, 129, 131, 137, 132, 136, 127, 133, 140, 114, 117, 17, 118, 21, 141]
    #RIGHT_CONST = [175, 33, 32, 120, 122, 125, 320, 312, 311, 314, 356, 331, 352, 336, 334, 360, 328, 327, 325, 167, 173, 174, 270, 278, 279, 273, 274, 361, 258, 256, 260, 262, 165, 166, 148, 160, 264, 265, 266, 358, 350, 351, 349, 330, 332, 329, 353, 337, 333, 335, 359, 326, 341, 157, 168, 170, 171, 269, 271, 277, 272, 276, 268, 275, 280, 257, 259, 162, 261, 164, 281]
    LEFT_CONST = []
    RIGHT_CONST = []

    def __init__(self, file_name):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.data.objects[ModelSculptor.MODEL_NAME].select = True
        #選択オブジェクトをアクティブに
        bpy.context.scene.objects.active = bpy.context.selected_objects[0]
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.mode_set(mode='OBJECT')
        
        self.model = Model(ModelSculptor.MODEL_NAME, file_name, 0)
        self.model.set_reference_point_index(20, 262)
        self.model.set_distance_points_index([0, 7], [979, 942])
        self.model.add_landmark(-1, -1, LEFT_CONST)
        self.model.add_landmark(-1, -1, RIGHT_CONST)

        self.model.add_landmark(0, 979, [979])
        self.model.add_landmark(1, 235, [235])
        self.model.add_landmark(2, 222, [222])
        self.model.add_landmark(3, 189, [189])
        self.model.add_landmark(4, 250, [250])
        self.model.add_landmark(5, 253, [253])
        self.model.add_landmark(6, 249, [249])
        self.model.add_landmark(7, 942, [942])
        self.model.add_landmark(8, 94, [94])
        self.model.add_landmark(9, 115, [115])
        self.model.add_landmark(10, 48, [48])
        self.model.add_landmark(11, 109, [109]) 
        self.model.add_landmark(12, 112, [112]) 
        self.model.add_landmark(13, 108, [108])  
        self.model.add_landmark(20, 464, [464])  
              
        """
        self.model.add_landmark(1, 241, [241])
        self.model.add_landmark(2, 246, [246])
        self.model.add_landmark(3, 182, [182])
        self.model.add_landmark(4, 194, [194])
        self.model.add_landmark(5, 210, [210])
        self.model.add_landmark(7, 98, [35, 107, 98, 45])
        self.model.add_landmark(8, 102, [10, 102, 49])
        self.model.add_landmark(9, 38, [39, 38, 40])
        self.model.add_landmark(10, 51, [71, 51, 46])
        self.model.add_landmark(11, 67, [69, 67, 68])
        """

    def _get_modifier_name(self, i):
        return "Hook-Empty" + ("" if i == 0 else "." + '%03d' % i)
    
    def _get_temporary_object_name(self, i):
        return "Empty" + ("" if i == 0 else "." + '%03d' % i)

    def _get_temporary_object(self, i):
        return bpy.data.objects[self._get_object_name(i)]

        
    #入力の頂点に紐づくモディファイアを作成する
    #in:  BlenderVectorIndexの配列
    def _create_hook_modifier(self, landmark):
        for i,landmark in enumerate(self.model.get_landmarks()):
            bpy.ops.object.mode_set(mode='OBJECT')

            self.model.set_parts_select(landmark)

            bpy.ops.object.mode_set(mode='EDIT')
            #選択したオブジェクトの頂点に紐付くHookモディファイアを作成
            bpy.ops.object.hook_add_newob()
            bpy.ops.mesh.select_all(action="DESELECT")
            #モディファイアの中心座標を特徴点対応頂点にする
            bpy.context.scene.cursor_location = landmark.get_vertex().co
            bpy.ops.object.hook_recenter(modifier = self._get_modifier_name(i))
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
            self._get_temporary_object(i).location = self.model.get_movement_value(landmark)
            

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

