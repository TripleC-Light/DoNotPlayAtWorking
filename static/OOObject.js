class Object{
	constructor( id ){
		this.id = id;
		this.name = this.id;
		this.HP = 100;
		this.X = 0;
		this.Y = 0;
		this.width = 0;
		this.height = 0;
		this.pic = "";
	}

	show(){
		document.getElementById(this.id).style.visibility = 'visible';
	}

	hide(){
		document.getElementById(this.id).style.visibility = 'hidden';
	}

	setPositionInPX( X, Y){
		var _obj = document.getElementById(this.id);
		this.X = X;
		this.Y = Y;
		_obj.style.left = this.X + 'px';
		_obj.style.top = this.Y + 'px';
	}

	setPositionRandomInPX(){
		var _X = Math.floor(Math.random()*document.body.clientWidth);
		var _Y = Math.floor(Math.random()*document.body.clientHeight);
		this.setPositionInPX( _X, _Y);
	}

	shake(shakeLevel){
		var _monsterObj = document.getElementById(this.id);
		var _X = this.X;
		_X += shakeLevel;
		_monsterObj.style.left = _X + '%';
		setTimeout(function(){
			_X -= shakeLevel;
			_monsterObj.style.left = _X + '%';
		},30);
	}

	hit( ATK ){
		var _this = this;
		this.HP -= ATK;
		if( this.HP<=0 ){
			this.LV += 1;
			this.hide();
			if( this.LV>2 ){
				this.LV = 0;
			}
		}
		this.autoSetHPcolor()
		this.shake(2);
		this.showHP();
		setTimeout(function(){
			_this.setPositionRandom();
		},100);
		setTimeout(function(){
			_this.hideHP();
		},500);
	}

	reBorn(){
		var _obj = document.getElementById(this.id);
		var _size = ['70px', '70px'];
		_obj.style.width = _size[0];
		_obj.style.height = _size[1];
		this.hide();
	}

	setPic(pic){
		this.pic = pic;
		var _obj = document.getElementById(this.id);
		_obj.style.backgroundImage = "url(" + pic + ")";
	}

	goto( P2){
		var _P1 = [ this.X, this.Y ];
		var _dX = _P1[0] - P2[0];
		var _dY = _P1[1] - P2[1];
		if( distance( _P1, P2)<1 ){
			return true;
		}else{
			var _step = 10;
			var _d = Math.round(distance( _P1, P2));
			var _howManyTimesToGo = Math.round(_d / _step);
			this.X = this.X - ( _dX / _howManyTimesToGo );
			this.Y = this.Y - ( _dY / _howManyTimesToGo );
			this.setPositionInPX( this.X, this.Y);
			return false;
		}
	}
}

function distance( P1, P2){
	var _dX = P1[0] - P2[0];
	var _dY = P1[1] - P2[1];
	return Math.sqrt( _dX*_dX + _dY*_dY );
}