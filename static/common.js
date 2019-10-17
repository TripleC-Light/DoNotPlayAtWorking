
class Common{
	constructor(){
		this.oldSysTimeForMsg = 0;
		this.showMsgInMilliSecond = 0;
		this.oldSysTimeForFPS = 0;
		this.FPScount = 0;
		this.gameFPS = 0;
		this.tmpFPS = 0;
		this.oldSysTimeForRecycle = 0;
		this.recycleObjInMilliSecond = 0;
	}

	timeToUpdateMsg(){
		var _sysTime = new Date().getTime();
		if( (_sysTime-this.oldSysTimeForMsg)>this.showMsgInMilliSecond ){
			this.oldSysTimeForMsg = _sysTime;
			return true;
		}else{
			return false;
		}
	}

	timeToRecycleObj(){
		var _sysTime = new Date().getTime();
		if( (_sysTime-this.oldSysTimeForRecycle)>this.recycleObjInMilliSecond ){
			this.oldSysTimeForRecycle = _sysTime;
			return true;
		}else{
			return false;
		}
	}

	countFPS(){
		if( this.FPScount>=10 ){
			this.FPScount = 0;
			this.gameFPS /= 10;
			this.tmpFPS = this.gameFPS;
			this.gameFPS = 0;
		}else{
			var _sysTime = new Date().getTime();
			var _FPS = 1000 / (_sysTime - this.oldSysTimeForFPS);
			if( _FPS>20 ){
				// console.log('Data read from Buffer');
			}else{
    			this.oldSysTimeForFPS = _sysTime;
				this.gameFPS += parseFloat(_FPS.toFixed(2));
				this.FPScount += 1;
			}
		}
		return this.tmpFPS.toFixed(2);
	}

	getXYinMap(_map){
		var _mainMapBounding = $('#iMainMap')[0].getBoundingClientRect();
		var e = window.event;
		var x = e.clientX;
		var y = e.clientY;
		x = x-_mainMapBounding.left;
		y = y-_mainMapBounding.top;
		return ([Math.round(x),Math.round(y)]);
	}

	webSocketURL(){	
		var _url = location.href;
		var _ws = '';
		_url = _url.split('://');
		if( _url[0]=='https' ){
			_ws = 'wss';
		}else{
			_ws = 'ws';
		}
		_url = _url[1].split('/');
		return( _ws + "://" + _url[0] + "/ws" );
	}

	strLen(sString){
		var _enStr = 0;
		var _twStr = 0;
		var s = sString;
		for (var i=0; i<s.length; i++){
			if (s.substr(i,1).charCodeAt(0)>255){
				_twStr += 1;
			}else{
				_enStr += 1;
			}
		}
		return ([_twStr, _enStr]);
	}

	strLenInPX(_msg){
		var _srtLength = this.strLen(_msg);
		var _oneENcharLenInPX = 12;
		var _oneTWcharLenInPX = 7.6;
		var _strLenInPX = (_srtLength[0]*(_oneTWcharLenInPX*2)) + (_srtLength[1]*_oneENcharLenInPX);
		return _strLenInPX;
	}

	idExist(id, objList){
		for(var i=0; i<objList.length; i++){
			if(id==objList[i].id){
				return true;
			}
		}
		return false;
	}

	distance(e1, e2){
		var _P1 = [e1.X, e1.Y];
		var _P2 = [e2.X, e2.Y];
	    var _dX = _P1[0] - _P2[0];
	    var _dY = _P1[1] - _P2[1];
    	return Math.sqrt(Math.pow(_dX,2) + Math.pow(_dY,2));
	}
}
