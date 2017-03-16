# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
import os, os.path
import zipfile

import shutil


def zip_dir(folder):
    with zipfile.ZipFile(folder + '.zip', 'w') as zipF:
        for lists in os.listdir(folder):
            job = os.path.join(folder, lists)
            print job
            if os.path.isfile(job):
                zipF.write(job)

def unzip(zip_file, target, delete_target=False):
    with zipfile.ZipFile(zip_file, 'r') as zipF:
        if delete_target:
            print('target %s found , and deleted ' % target)
            shutil.rmtree(target)
        zipF.extractall(target)