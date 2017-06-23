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
        blood.tblName += ';style ' + blood.tblName.replace('@', '__').replace('class',
                                                                              'calss') + ' fill:#f9f,stroke:#333,stroke-width:4px'
    return blood


def find_parent_mermaid(blood, final_bloods, init=0, depth=0):
    '''
    # 循环遍历当前节点的父节点
    :param blood:
    :param final_bloods:
    :return:
    '''
    init += 1
    if init > 100:
        return
    bloods = TblBlood.objects.filter(tblName=blood.parentTbl)
    if init != depth or depth < 0:
        if bloods.count() > 0:
            for bld in bloods:
                final_bloods.add(bld)
                find_parent_mermaid(bld, final_bloods, init=init, depth=depth)


def find_child_mermaid(blood, final_bloods, init=0, depth=0):
    '''
    循环遍历当前节点的子节点
    :param blood:
    :param final_bloods:
    :return:
    '''
    init += 1
    if init > 100:
        return
    bloods = TblBlood.objects.filter(parentTbl=blood.tblName)
    if bloods.count() > 0:
        for bld in bloods:
            # if bld in final_bloods:
            #     raise Exception('Already has %s ' % bld)
            final_bloods.add(bld)
            if init != depth or depth < 0:
                find_child_mermaid(bld, final_bloods, init=init, depth=depth)


def check_parent_mermaid(blood, init=0, depth=0):
    '''
    # 循环遍历当前节点的父节点
    :param blood:
    :param final_bloods:
    :return:
    '''
    init += 1
    bloods = TblBlood.objects.filter(tblName=blood.parentTbl)
    if init != depth or depth < 0:
        if bloods.count() > 0:
            for bld in bloods:
                check_parent_mermaid(bld, init=init, depth=depth)


def check_child_mermaid(blood, dep_score, init=0, depth=0):
    '''
    循环遍历当前节点的子节点
    :param blood:
    :param final_bloods:
    :return:
    '''
    init += 1
    bloods = TblBlood.objects.filter(parentTbl=blood.tblName)
    if bloods.count() > 0:
        for bld in bloods:
            # if bld in final_bloods:
            #     raise Exception('Already has %s ' % bld)
            dep_score[bld] = dep_score.get(bld, 0) + 1
            if dep_score[bld] > 30:
                break
            if init != depth or depth < 0:
                check_child_mermaid(bld, dep_score, init=init, depth=depth)


def check_cycle(etlid):
    bloods = TblBlood.objects.filter(relatedEtlId=int(etlid), valid=1)
    final_bloods = set()
    p_depth, c_depth = 0, 0
    dep_score = {}
    for blood in bloods:
        blood.current = blood.id
        if p_depth != -1:
            final_bloods.add(blood)
            find_parent_mermaid(blood, final_bloods, depth=p_depth)
        if c_depth != -1:
            find_child_mermaid(blood, final_bloods, dep_score, depth=c_depth)

    large_score = [blood for blood, v in dep_score.items() if v > 20]
    if any(v > 20 for blood, v in dep_score.items()):
        return False
    return True
