# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
import os, os.path
import zipfile


def zip_dir(folder):
    with zipfile.ZipFile(folder + '.zip', 'w') as zipF:
        for lists in os.listdir(folder):
            job = os.path.join(folder, lists)
            print job
            if os.path.isfile(job):
                zipF.write(job)



if __name__ == '__main__':
    # zip_dir('/usr/local/will/test/shell')
    with open('/tmp/20160728095015/default@origin_tbl.job', 'w') as r:
        r.write("ffff")