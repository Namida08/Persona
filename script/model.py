# coding: UTF-8
import bpy
import bpy_extras
import math
import sys
sys.path.append("/home/yaku/work/model_sculptor/script")
from landmark import Landmark
from point import Point

class Model:
    
    #画像の特徴点の座標配列取得
    #in:  参照画像のファイル名
    #out: 特徴点の座標配列
    def _get_image_feature_points(self, file_name):
        array = []
        f = open(file_name, "r")
        data = f.read().split("\n") 
        for line in data:
            if line:
                point = list(map(int, line.split(' ')))
                array.append(Point(point[0], point[1]))
        f.close()
        return array

    def __init__(self, object_name, file_name, yaw_angle):
        self.object = bpy.data.objects[object_name]
        self.vertices = self.object.data.vertices
        self.feature_points = self._get_image_feature_points(file_name)
        self.yaw_angle = yaw_angle
        self.image_reference_point_index = -1
        self.model_reference_point_index = -1
        self.image_distance_point_indexes = [-1, -1]
        self.model_distance_point_indexes = [-1, -1]
        self.landmarks = []

    def get_object(self):
        return object

    def get_vertices(self):
        return vertices

    def get_feature_points(self):
        return feature_points
    
    def get_image_reference_point(self):
        return self.get_feature_points()[self.image_reference_point_index]

    def get_model_reference_vertex(self):
        return self.get_vertices()[self.get_model_reference_point_index]

    def get_image_distance_points(self):
        return [self.get_feature_points()[self.image_distance_point_indexes[0]],
                self.get_feature_points()[self.image_distance_point_indexes[1]]]
    
    def get_model_distance_vertices(self):
        return [self.get_vertices()[self.model_distance_point_indexes[0]], 
                self.get_vertices()[self.model_distance_point_indexes[1]]]

    def get_landmarks(self):
        return landmarks

    def get_feature_point(self, landmark):
        return self.get_feature_points()[landmark.get_point_index()]

    def get_vertex(self, landmark):
        return self.get_vertices()[landmark.get_vertex_index()]

    def get_parts(self, landmark):
        parts = []
        for index in landmark.get_part_indexes():
            parts.append(self.get_vertices()[index])
        return parts

    #原点座標からのベクトル
    def _get_local_image_point(self, point):
        return point - self.get_image_reference_point()
    
    #モデルのXZ投影面上での2点間の距離
    def _get_projection_vector_distance_xz(self, vertex1, vertex2):
        point = Point(vertex1.co.x - vertex2.co.x,
                      vertex1.co.z - vertex2.co.z)
        projection_vector = Point(cos(self.yaw_angle), sin(self.yaw_angle))
        return point.get_projection_vector_distance(projection_vector)
    
    #眼間距離から画像と比べてのモデルの倍率を取得
    def _get_magnification(self):
        image = self.get_image_distance_points()
        model = self.get_model_distance_vertices()
        image_d = Point.distance(image[0], image[1])
        model_d = self._get_projection_vector_distance_xz(model[0], model[1])
        return model_d / image_d

    #原点座標からのベクトル
    def _get_local_model_point(self, vertex):
        return Point(self._get_projection_vector_distance_xz(vertex, self.get_model_reference_vertex()),
                    vertex.co.y - self.get_model_reference_vertex().co.y)

    #投影面上での距離差
    def _get_distance(self, landmark):
        image = self._get_local_image_point(self.get_feature_point(landmark))
        image *= self._get_magnification()
        model = self._get_local_model_point(self.get_vertex(landmark))       
        return image - model
    
    #移動量加味した座標
    def get_movement_value(self, landmark):
        vector = self.get_vertex(landmark).co

        if (not(landmark.has_index())):
            return [vector.x, vector.y, vector.z]
        
        value = self._get_distance(landmark)
        result = [vector.x + value[0] * cos(self.yaw_angle),
                  vector.y + value[1],
                  vector.z + value[0] * sin(self.yaw_angle)]
        return result


    def add_landmark(self, point_index, vertex_index, part_indexes):
        self.get_landmarks().append(Landmark(point_index, vertex_index, part_indexe))

    def set_reference_point_index(image_point, model_point):
        self.image_reference_point_index = image_point
        self.model_reference_point_index = model_point
    
    def set_distance_points_index(image_points, model_points):
        self.image_distance_point_indexes = image_points
        self.model_distance_point_indexes = model_points

    def set_parts_select(self, landmark):
        for part in self.get_parts(landmark):
            part.select = True
    
