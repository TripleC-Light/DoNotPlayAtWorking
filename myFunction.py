import uuid

def getUniqueID():
    # _getUID = False
    # while not _getUID:
    #     _UID = uuid.uuid1()
    #     if _UID not in _IDlist:
    #         _getUID = True
    # return _UID
    return str(uuid.uuid1())[0:8]
