# coding: UTF-8
import math

class Landmark:
    
    #image: 画像上の特徴点index
    #model: モデル上の対応頂点index
    #part:  モデル上の対応変形部位の頂点index配列
    def __init__(self, point_index, vertex_index, part_indexes):
        self.point_index = point_index
        self.vertex_index = vertex_index
        self.part_indexes = part_indexes
        
    def get_point_index(self):
        return self.point_index

    def get_vertex_index(self):
        return self.vertex_index

    def get_part_indexes(self):
        return self.part_indexes

    def has_index(self):
        if (self.get_point_index() != -1 and self.get_vertex_index() != -1):
            return True
        else:
            return False

