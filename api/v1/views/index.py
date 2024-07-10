#!/usr/bin/python3
"""routes for web page to access table information"""


from flask import jsonify
from api.v1.views import app_views
from models import storage
from models.registration import Registration
from models.logout import TokenBlacklist


@app_views.route('/status', methods=['GET'], strict_slashes=False)
def get_status():
    """"return status of request"""
    data = {"status": "OK"}
    res = jsonify(data)
    res.status_code = 200
    return res


@app_views.route('/stats', methods=['GET'], strict_slashes=False)
def get_stat():
    """return table name and number of rows"""
    class_map = {'Registration': Registration, 'TokenBlacklist': TokenBlacklist}
    cls = ["Registration", "TokenBlacklist"]
    tables = storage.table_names()
    all_tables = {}
    for x in range(len(cls)):
        c = cls[x]
        class_name = class_map[c]
        obj = storage.count(class_name)
        all_tables[tables[x]] = obj
    res = jsonify(all_tables)
    res.status_code = 200
    return(res)
