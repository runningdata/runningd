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
    init.depth += 1
    if init.depth > 100:
        return
    bloods = TblBlood.objects.filter(tblName=blood.parentTbl)
    if init.depth != depth or depth < 0:
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
    init.depth += 1
    if init.depth > 100:
        return
    bloods = TblBlood.objects.filter(parentTbl=blood.tblName)
    if bloods.count() > 0:
        for bld in bloods:
            # if bld in final_bloods:
            #     raise Exception('Already has %s ' % bld)
            final_bloods.add(bld)
            if init.depth != depth or depth < 0:
                find_child_mermaid(bld, final_bloods, init=init, depth=depth)


def check_parent_mermaid(blood, dep_score):
    '''
    # 循环遍历当前节点的父节点
    :param blood:
    :param final_bloods:
    :return:
    '''
    bloods = TblBlood.objects.filter(tblName=blood.parentTbl)
    if bloods.count() > 0:
        for bld in bloods:
            dep_score[bld] = dep_score.get(bld, 0) + 1
            if dep_score[bld] > 50:
                break
            check_parent_mermaid(bld, dep_score)


def check_child_mermaid(blood, dep_score):
    '''
    循环遍历当前节点的子节点
    :param blood:
    :param final_bloods:
    :return:
    '''
    bloods = TblBlood.objects.filter(parentTbl=blood.tblName)
    if bloods.count() > 0:
        for bld in bloods:
            dep_score[bld] = dep_score.get(bld, 0) + 1
            if dep_score[bld] > 50:
                break
            check_child_mermaid(bld, dep_score)


def check_cycle(etlid):
    bloods = TblBlood.objects.filter(relatedEtlId=int(etlid), valid=1)
    dep_score = {}
    for blood in bloods:
        blood.current = blood.id
        check_parent_mermaid(blood, dep_score)
        check_child_mermaid(blood, dep_score)

    dep_score = sorted(dep_score.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
    large_score = [blood for blood, v in dep_score if v > 45]
    if any(v > 45 for blood, v in dep_score):
        return large_score, True
    return large_score, False
