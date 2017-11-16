# !/usr/bin/env python
# -*- coding: utf-8 -*
from collections import defaultdict
# Python program to detect cycle
# in a graph

# WHITE : Vertex is not processed yet.  Initially
#         all vertices are WHITE.
#
# GRAY : Vertex is being processed (DFS for this
#        vertex has started, but not finished which means
#        that all descendants (ind DFS tree) of this vertex
#        are not processed yet (or this vertex is in function
#        call stack)
#       这个端点的DFS[深度优先遍历]已经启动，但是还没有结束。也就是说这个端点的所有的后代节点还没有执行完
#
# BLACK : Vertex and all its descendants are
#         processed
#
#


class Graph():
    def __init__(self, V):
        '''
        初始化一个包含V个端点的graph，每个端点都有自己的边数组(就是从自己出发，到别的端点)
        :param V:
        '''
        self.V = V
        self.graph = defaultdict(list)

    def addEdge(self, u, v):
        '''
        添加一条从u到v的边
        :param u:   起点
        :param v:   目标端点
        '''
        self.graph[u].append(v)

    def DFSUtil(self, u, color):
        '''
        开始深度遍历，并标记各种状态的节点
        :param u:           当前节点
        :param color:       节点状态集合
        :return:
        '''
        # GRAY :  This vertex is being processed (DFS
        #         for this vertex has started, but not
        #         ended (or this vertex is in function
        #         call stack)
        # 灰色代表正在处理（这个端点的DFS已经开始了，但是还没有结束）
        color[u] = "GRAY"

        for v in self.graph[u]:
            if color.get(v, 'WHITE') == "GRAY":
                '''
                u -> v这就是back edge了
                '''
                self.back_edge = (u, v)
                return True

            if color.get(v, 'WHITE') == "WHITE" and self.DFSUtil(v, color) == True:
                return True

        # 黑色代表，都顺利遍历完了
        color[u] = "BLACK"
        return False

    def isCyclic(self):
        # 初始的时候是都没有遍历的
        color = dict()

        for i in range(self.V):
            if color.get(i, 'WHITE') == "WHITE":
                if self.DFSUtil(i, color) == True:
                    return True, color
        return False, color



# Driver program to test above functions

# g = Graph(4)
# g.addEdge(0, 1)
# g.addEdge(0, 2)
# g.addEdge(1, 2)
# g.addEdge(2, 0)
# g.addEdge(2, 3)
# g.addEdge(3, 3)
# (is_cy, colors) = g.isCyclic()
# if is_cy:
#     print colors
#     print g.back_edge