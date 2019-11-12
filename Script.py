import time
import random

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
        self.msgCtrl = ''
        self.mapCtrl = ''

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
                self.msgCtrl.add('centerInfo', '出現了一個令人好奇的神祕按鈕')
                self.objCtrl.mapSize = self.mapSize
                _item = self.objCtrl.createItem('button')
                _item.id = 'Scene00Button'
                _item.name = '神秘的按鈕'
                self.itemID = _item.id
                self.objList[_item.id] = _item
                self.state = 2

            elif _scene == 2:
                if self.itemID not in self.objList:
                    self.mapCtrl.shake(5)
                    self.state = 3
                    self.oldSysTime = time.time()
                    print('Push Button')

            elif _scene == 3:
                if (time.time()-self.oldSysTime) > 2:
                    self.msgCtrl.add('centerInfo', '有人手癢按下了按鈕, 導致世界發生了異變')
                    self.oldSysTime = time.time()
                    self.state = 4
                    print('Push Button')

            elif _scene == 4:
                if (time.time()-self.oldSysTime) > 2:
                    self.Start = True
                    _item = self.objCtrl.createItem('Zkey')
                    _item.W = _item.W * 1.5
                    _item.H = _item.H * 1.5
                    _item.X = self.mapSize[0]/2
                    _item.Y = _item.H - 20
                    _item.tX = _item.X
                    _item.tY = _item.Y
                    _item.name = '按[Z]進行攻擊!!'
                    self.itemID = _item.id
                    self.objList[_item.id] = _item
                    for _i in range(1):
                        _enemy = self.objCtrl.createCharacter('zombie')
                        self.objList[_enemy.id] = _enemy
                    self.state = 5

            elif _scene == 5:
                _enemyNum = 0
                self.objCtrl.createItemInRandom('fullHP', 0.1, 2)
                for _id in list(_objList.keys()):
                    if _objList[_id].type == 'enemy':
                        _enemyNum += 1
                if _enemyNum == 0:
                    self.oldSysTime = time.time()
                    self.state = 6

            elif _scene == 6:
                self.objCtrl.createItemInRandom('fullHP', 1, 3)
                if (time.time() - self.oldSysTime) > 1:
                    self.state = 7

            elif _scene == 7:
                for _i in range(1):
                    _enemy = self.objCtrl.createCharacter('zombie')
                    self.objList[_enemy.id] = _enemy
                self.state = 8

            elif _scene == 8:
                _enemyNum = 0
                self.objCtrl.createItemInRandom('fullHP', 0.1, 2)
                for _id in list(_objList.keys()):
                    if _objList[_id].type == 'enemy':
                        _enemyNum += 1
                if _enemyNum == 0:
                    self.oldSysTime = time.time()
                    self.state = 9

            elif _scene == 9:
                self.objCtrl.createItemInRandom('fullHP', 1, 3)
                if (time.time() - self.oldSysTime) > 1:
                    self.state = 10

            elif _scene == 10:
                for _i in range(1):
                    _enemy = self.objCtrl.createCharacter('robot')
                    self.objList[_enemy.id] = _enemy
                self.state = 11

            elif _scene == 11:
                _enemyNum = 0
                self.objCtrl.createItemInRandom('fullHP', 0.1, 2)
                for _id in list(_objList.keys()):
                    if _objList[_id].type == 'enemy':
                        _enemyNum += 1
                if _enemyNum == 0:
                    self.oldSysTime = time.time()
                    self.state = 12

            elif _scene == 12:
                print('Stage Clear')
                self.objCtrl.createItemInRandom('fullHP', 1, 3)
                self.msgCtrl.add('centerInfo', '敵人已全部消滅, 世界暫時恢復了和平')
                self.objList[self.itemID].timeOut = 0
                self.Start = False
                self.state = 0

            # print('Scene: ' + str(_scene))
