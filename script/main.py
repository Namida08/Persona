# coding: UTF-8
# モデルに直接紐付けるスクリプト


import sys
sys.path.append("../script")
from model_sculptor import ModelSculptor


a = ModelSculptor("MTH_DEF", "../image_1", 0)
a.run()


