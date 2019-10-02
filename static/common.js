
class Common{
	constructor(){
		this.oldSysTimeForMsg = 0;
		this.showMsgInMilliSecond = 0;
		this.oldSysTimeForFPS = 0;
		this.FPScount = 0;
		this.gameFPS = 0;
		this.tmpFPS = 0;
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
}


function idExist(id, objList){
	for(var i=0; i<objList.length; i++){
		if(id==objList[i].id){
			return true;
		}
	}
	return false;
}
