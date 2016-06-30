# coding: UTF-8
import math

class Point:

    @staticmethod
    def distance(a, b):
        return sqrt(pow((a.x - b.x), 2) + pow((a.y - b.y), 2))

    #内積
    @staticmethod
    def dot_product(a, b):
        return a.x * b.x + a.y * b.y

    #2ベクトル間の角度
    @staticmethod
    def angle_of_vector(a, b):
        ad = a.get_distance()
        bd = b.get_distance()
        cos_sita = Point.dot_product(a, b) / (ad * bd)
        return acos(cos_sita)
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Point(self.x * other.x, self.y * other.y)

    def __div__(self, other):
        return Point(self.x / other.x, self.y / other.y)

    def __imul__(self, value):
        self.x *= value
        self.y *= value
        return self

    def get_distance(self):
        return sqrt(pow(self.x, 2) + pow(self.y, 2))

    #正投影ベクトルの距離
    #in : projection=投影面ベクトル
    def get_projection_vector_distance(self, projection):
        return self.get_distance() * cos(Point.angle_of_vector(self, projection))

