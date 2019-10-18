class Script:
    def __init__(self):
        self.state = 0
        self.region = ''
        self.objCtrl = ''
        self.objList = {}
        self.mapSize = []
        self.itemID = 0

    def run(self, _objList):
        _region = self.region
        _scene = self.state
        self.objList = _objList

        if _region == '0-0':

            if _scene == 0:
                _pilotNum = 0
                for _id in list(_objList.keys()):
                    if _objList[_id].type == 'pilot':
                        _pilotNum += 1
                if _pilotNum >= 3:
                    self.state = 1

            elif _scene == 1:
                for _id in list(_objList.keys()):
                    if _objList[_id].type == 'pilot':
                        self.objCtrl.mapSize = self.mapSize
                        _item = self.objCtrl.createItem('button')
                        self.itemID = _item.id
                        self.objList[_item.id] = _item
                self.state = 2

            elif _scene == 2:
                if self.itemID in self.objList:
                    if _objList[self.itemID].HP == 0:
                        print('Push Button')

            print('Scene: ' + str(_scene))
