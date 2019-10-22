import time

class Script:
    def __init__(self):
        self.Start = False
        self.state = 0
        self.region = ''
        self.objCtrl = ''
        self.objList = {}
        self.mapSize = []
        self.itemID = 0
        self.oldSysTime = 0

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
                self.objCtrl.mapSize = self.mapSize
                _item = self.objCtrl.createItem('button')
                _item.id = 'Scene00Button'
                _item.name = '神秘的按鈕'
                self.itemID = _item.id
                self.objList[_item.id] = _item
                self.state = 2

            elif _scene == 2:
                if self.itemID not in self.objList:
                    self.state = 3
                    print('Push Button')

            elif _scene == 3:
                self.Start = True
                _item = self.objCtrl.createItem('Zkey')
                _item.X = self.mapSize[0]/2
                _item.Y = _item.W*2
                _item.tX = _item.X
                _item.tY = _item.Y
                _item.name = '攻擊!!'
                self.itemID = _item.id
                self.objList[_item.id] = _item

                for _i in range(1):
                    _enemy = self.objCtrl.createEnemy('zombie')
                    self.objList[_enemy.id] = _enemy
                self.state = 4

            elif _scene == 4:
                _enemyNum = 0
                for _id in list(_objList.keys()):
                    if _objList[_id].type == 'enemy':
                        _enemyNum += 1
                if _enemyNum == 0:
                    self.oldSysTime = time.time()
                    self.state = 5

            elif _scene == 5:
                if (time.time() - self.oldSysTime) > 1:
                    self.state = 6

            elif _scene == 6:
                for _i in range(1):
                    _enemy = self.objCtrl.createEnemy('zombie')
                    self.objList[_enemy.id] = _enemy
                self.state = 7

            elif _scene == 7:
                _enemyNum = 0
                for _id in list(_objList.keys()):
                    if _objList[_id].type == 'enemy':
                        _enemyNum += 1
                if _enemyNum == 0:
                    self.oldSysTime = time.time()
                    self.state = 8

            elif _scene == 8:
                print('Stage Clear')
                self.objList[self.itemID].timeOut = 0
                self.Start = False
                self.state = 9

            # print('Scene: ' + str(_scene))
