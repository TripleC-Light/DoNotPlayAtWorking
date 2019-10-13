class ObjCtrl{
	constructor(e){
		this.allObj = '';
		this.frame = $('#frame_' + e.id);
		this.frameBound = '';
		this.pilot = $('#' + e.id);
		this.pilotBound = '';
	}

	syncPilotObj(e){
		if( !Com.idExist(e.id, this.allObj) ){
			console.log('Create pilot in web: ' + e.id);
			Create.newObj( 'iMainMap', e);
		}
		this.frameBound = $('#frame_' + e.id)[0].getBoundingClientRect();
		this.pilotBound = $('#' + e.id)[0].getBoundingClientRect();
	}

	showPilot(e){
		this.frame.css('visibility','visible');
		$('#name_' + e.id).css('visibility','visible');
		if( e.id==myID ){
			this.frame.css('zIndex',999);
		}
	}

	updatePilotXY(e){
		// var _pilotBound = $('#' + e.id)[0].getBoundingClientRect();
		this.frame.css({'left': e.X-(this.frameBound.width/2)});
		this.frame.css({'top' : this.frameBound.top - (this.pilotBound.top-e.Y) - (this.pilotBound.height/2)});
	}
	
	updatePilotHP(e){
		/*--- if use jquery width will not update, I don't know why ---*/
		var _HPlengthInPx = 50;
		var _HPmax = 10;
		var _damage = Math.round(_HPlengthInPx/_HPmax);
		var _pilotHP = document.getElementById('HP_' + e.id);
		// console.log(e.id + ':' + e.HP + ', L=' + e.HP*_damage);
		_pilotHP.style.display = 'inline-block';
		_pilotHP.style.visibility = 'visible';
		if( (e.HP*_damage)<0 ){
			_pilotHP.style.width = '0px';
		}else{
			_pilotHP.style.width = e.HP*_damage + 'px';
		}
		// console.log(_pilotHP.style.width);
		if( _pilotHP.style.width<(_HPlengthInPx/5) ){
			_pilotHP.style.backgroundColor = '#F00';
		}else if( _pilotHP.style.width<(_HPlengthInPx/2) ){
			_pilotHP.style.backgroundColor = '#FFC90E';

		}
		if( e.HIT ){
			this.shake(e, 10);
		}
	}

	updatePilotMsg(e){
		var _msg = $('#msg_'+e.id);
		var _msgArrow = $('#msgArrow_'+e.id);
		if(e.msg!=''){
			var _strLenInPX = Com.strLenInPX(e.msg);
			var _textAlign = '';
			if( _strLenInPX<250 ){
				_textAlign = 'center';
			}else{
				_strLenInPX = 250;
				_textAlign = 'left';
			}
			_msg.width(_strLenInPX);
			_msg.css('textAlign', _textAlign);
			_msg[0].innerHTML = e.msg;
			_msg.css('display','inline-block');
			var _msgBound = _msg[0].getBoundingClientRect();
			_msg.css({'top':(0-_msgBound.height-20)});
			_msg.css('left', (0-((_msgBound.width-this.frameBound.width)/2)));
			_msgArrow.css('display','block');
		}else{
			_msgArrow.css('display','none');
			_msg.css('display','none');
			_msg[0].innerHTML = '';
		}
	}

	updatePic(e){
		var _actionStr = '';
		var _width = 0;
		if( e.id==myID && attackState ){
			_actionStr = 'attack_';
			this.pilot.width(e.W*1.5);
			if( e.dir=='left' ){
				this.pilot.css('left',0-(e.W/2));
			}
		}else if( e.attack!=0 ){
			_actionStr = 'attack_';
			this.pilot.width(e.W*1.5);
			if( e.dir=='left' ){
				this.pilot.css('left',0-(e.W/2));
			}
		}else{
			this.pilot.css('left',0);
			this.pilot.width(e.W);
		}
		if( e.HIT ){
			_actionStr = 'beHIT_';
		}
		this.pilot.css('backgroundImage',"url('./static/pilot/" + e.pic + "/" + _actionStr + e.dir + ".gif')");
		this.pilot.css('visibility','visible');
	}

	deleteOfflinePilot(e){
		if( e.timeOut==0){
			console.log(e.id)
			var _pilotFrameObj = document.getElementById('frame_' + e.id);
			var _parentObj = document.getElementById('iMainMap');
			_parentObj.removeChild(_pilotFrameObj);
			console.log('Delete: ' + e.id);
			for(var i=0; i<this.allObj.length; i++){
				if( this.allObj[i].id == e.id ){
					this.allObj.splice(i,1);
				}
			}
			if( e.id==myID ){
				myID = '';
			}
			return true;
		}

		if( e.HP<=0 ){
			if( e.type=='pilot' ){
				this.pilot.css('backgroundImage',"url('./static/pilot/item/coffin.gif')");
			}
			return true;
		}
		return false;
	}

	shake(obj, shakeLevel){
		var _this = this;
		var _X = this.frame.position().left;
		_X += shakeLevel;
		this.frame.css('left', _X);
		setTimeout(function(){
			_X -= shakeLevel;
			_this.frame.css('left', _X);
		},30);
	}
}
