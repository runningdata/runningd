# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''

from metamap.models import TblBlood

def clean_blood(blood, current=0):
    '''
    为了方便mermaid显示，把blood里的@替换为__
    :param blood:
    :return:
    '''
    blood.parentTbl = blood.parentTbl.replace('@', '__').replace('class', 'calss')
    blood.tblName = blood.tblName.replace('@', '__').replace('class', 'calss')
    if current > 0:
        blood.tblName += ';style ' + blood.tblName.replace('@', '__').replace('class', 'calss') + ' fill:#f9f,stroke:#333,stroke-width:4px'
    return blood

def find_parent_mermaid(blood, final_bloods, current=0):
    '''
    # 循环遍历当前节点的父节点
    :param blood:
    :param final_bloods:
    :return:
    '''
    bloods = TblBlood.objects.filter(tblName=blood.parentTbl)
    if bloods.count() > 0:
        for bld in bloods:
            final_bloods.add(clean_blood(bld, current))
            find_parent_mermaid(bld, final_bloods)


def find_child_mermaid(blood, final_bloods, current=0):
    '''
    循环遍历当前节点的子节点
    :param blood:
    :param final_bloods:
    :return:
    '''
    bloods = TblBlood.objects.filter(parentTbl=blood.tblName)
    if bloods.count() > 0:
        for bld in bloods:
            final_bloods.add(clean_blood(bld, current))
            find_parent_mermaid(bld, final_bloods)
