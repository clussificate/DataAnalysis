# -*- coding:utf-8 -*-
from __future__ import division
import numpy as np
import collections
import sys
import json
reload(sys)
sys.setdefaultencoding('utf8')



class poiTagSim(object):
    def __init__(self,filename):
        self.filename = filename
        self.poi_set = []  # poi 集合
        self.tags_set = []  # 标签集合
        self.poi_tags = {}   # poi下的tags信息
        self.poi_tags_matrix = []   # poi标签矩阵
        self.tags_poi = {}  # 共同评论的poi以及共同评论数

    """
    读取文件
    """
    def read_file(self):
        with open(self.filename, 'r') as f:
            for line in f:
                if line:
                    yield line
                else:
                    return

    """
    生成poi_tags字典
    """
    def poi_tags_dic(self):
        row_num = 0
        for line in self.read_file():
            if row_num == 0:    # 跳出第一行
                row_num += 1
                continue
            item = line.split('\t')
            poi_name = item[2]
            tag_name = item[5]
            if poi_name not in self.poi_tags:
                self.poi_tags[poi_name] = [tag_name]
            else:
                self.poi_tags[poi_name].append(tag_name)

    """
    列表去重：输入一个列表，输出一个集合
    """
    def listToSet(self,mylist):
        myset = []
        for item in mylist:
            if item in myset:
                continue
            else:
                myset.append(item)
        return myset

    """
    生成Poi集合和标签集合
    """
    def gene_set(self):
        poi_list = []
        tags_list = []
        for key, items in self.poi_tags.items():
            poi_list.append(key)
            tags_list.extend(items)
        self.poi_set = self.listToSet(poi_list)
        self.tags_set = self.listToSet(tags_list)

    """
    生成poi_tag的矩阵
    """
    def gene_mat(self):
        poi_tags_matrix = np.zeros((len(self.poi_set), len(self.tags_set)))
        for poi in self.poi_tags.keys():
            # print("-----------")
            # print(poi)
            PoiInd = self.poi_set.index(poi)
            for tag in self.poi_tags[poi]:
                # print(tag)
                TagInd = self.tags_set.index(tag)
                poi_tags_matrix[PoiInd, TagInd] = 1
                self.poi_tags_matrix = poi_tags_matrix

    """
    生成tags_poi倒排序字典{tag1:[poi1,poi2]},tag2:[poi..]...}
    为了加快相似矩阵的计算速度
    """
    def reverse(self):

        for key, items in self.poi_tags.items():
            for item in items:
                if item not in self.tags_poi:
                    self.tags_poi[item] = set()
                self.tags_poi[item].add(key)

    """
    计算Jaccard相似度
    """
    def caclJacSim(self):
        C = {}
        N = {}
        for tag, pois in self.tags_poi.items():
            for poi1 in pois:
                if poi1 in N:
                    N[poi1] += 1
                else:
                    N[poi1] = 1
                    C[poi1] = {}
                for poi2 in pois:
                    if poi1 == poi2:
                        continue
                    if poi2 in C[poi1]:
                        C[poi1][poi2] += 1
                    else:
                        C[poi1][poi2] = 1

        poi_sim = collections.defaultdict(dict)
        for poi, related_pois in C.items():
            for related_poi, comm in related_pois.items():
                poi_sim[poi][related_poi] = comm/(N[poi]+N[related_poi]-comm)
        return poi_sim



        ## 计算太慢
        # poi_sim = np.zeros((len(self.poi_set), len(self.poi_set)))
        # if self.poi_tags_matrix == []:
        #     print("....no poi_tags_matrix....")
        # for i in range(len(self.poi_tags_matrix)):
        #     for j in range(i+1, len(self.poi_tags_matrix)):
        #         sim = self.JacSim(self.poi_tags_matrix[i], self.poi_tags_matrix[j])
        #         poi_sim[i,j] = sim
        #         poi_sim[j,i] = sim
        # return poi_sim

    """
    写文件
    """
    def write_sim(self,poi_sim,filename):
        if poi_sim:
            with open(filename, 'w') as f:
                for key, items in poi_sim.items():
                    for key2, value in items.items():
                        f.write(str(key)+'\t'+str(key2)+'\t'+str(value)+'\n')

    """
    运行程序
    """
    def run(self):
        self.poi_tags_dic()
        print(u"...生成poi_tags词典")
        # print(self.poi_tags)
        self.gene_set()
        print(u"...生成poi集合、tags集合....")
        # self.gene_mat()
        # print("...生成poi-tags矩阵....")
        self.reverse()
        print(u"...生成tag_poi反转词典....")
        # print(json.dumps(self.tags_poi, encoding = 'UTF-8', ensure_ascii=False))
        poi_sim = self.caclJacSim()
        print(u"...相似度计算完毕...")
        # print(u"007 island similarities as follows:")
        # print(poi_sim['007岛'])
        return poi_sim


if __name__ == '__main__':
    filename = sys.argv[1]
    myPoitagSimTest = poiTagSim(filename)
    poi_sim = myPoitagSimTest.run()
    outPutFile = sys.argv[2]
    myPoitagSimTest.write_sim(poi_sim, outPutFile)
    print("finished....")


