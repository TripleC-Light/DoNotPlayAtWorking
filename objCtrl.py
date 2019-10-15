def clearBeHITstate(_gObjList):
    for _id in list(_gObjList.keys()):
        _pilot = _gObjList[_id]
        if _pilot.type == 'pilot' or _pilot.type == 'enemy':
            _pilot.beHIT = False

