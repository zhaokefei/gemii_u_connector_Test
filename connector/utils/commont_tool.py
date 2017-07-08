#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import json

def save_json(filename, data, dirName, mode='a'):
    """
    @brief      Saves dict to json file.
    @param      filename  String
    @param      data      Dict
    @param      dirName   String
    @return     file path
    """
    # Log.debug('save json: ' + filename)
    fn = filename
    if not os.path.exists(dirName):
        os.makedirs(dirName)
    fn = os.path.join(dirName, filename)

    with open(fn, mode) as f:
        f.write(json.dumps(data, indent=4) + '\n')
    return fn