class Generate{
	constructor(){
		this.state = 'createPilotInServer';
		this.FSMtrigTime = 50;
		this.ID = '';
		this.pilotObj = '';
	}

	pilot(parent, allObj){
		switch(this.state){
			// case 'getID':
			// 	this.state = 'checkID';
			// 	break;

			// case 'checkID':
			// 	this.state = 'createPilotInServer';
			// 	break;

			case 'createPilotInServer':
				var _positionMode = 'auto';
				// var _positionMode = [35, 350];
				WS.send('createPilot@' + _positionMode);
				this.state = 'createPilotInWeb';
				break;

			case 'createPilotInWeb':
				if( this.pilotObj!='' ){
					this.newObj(parent, this.pilotObj);
					this.state = 'finish';
				}
				break;
			case 'finish':
				break;
		}
		console.log('Create Pilot state: ' + this.state);
		if( this.state != 'finish' ){
				var thisVar = this;
				setTimeout(function(){
					thisVar.pilot(parent, allObj);
				}, this.FSMtrigTime);
		}else{
			this.state = 'createPilotInServer';
		}
	}

	newObj( parentObj, obj){
		var _frameID = 'frame_' + obj.id;
		this._createFrame(parentObj, obj);
		this._createMsg(_frameID, obj.id);
		this._createMsgArrow(_frameID, obj.id);
		this._createMain(_frameID, obj.id);
		this._createName(_frameID, obj);
		this._createHp(_frameID, obj.id);
		this._shapeMain(obj, obj.pic);
	}

	_createFrame( parentObj, obj){
		var parent = document.getElementById(parentObj);
		var pilotFrame = document.createElement("div");
		pilotFrame.setAttribute("id", 'frame_' + obj.id);
		pilotFrame.setAttribute("class", "cPilotFrame");
		pilotFrame.style.width = obj.W + 'px';
		pilotFrame.style.height = obj.H + 'px';
		parent.appendChild(pilotFrame);
		pilotFrame.style.visibility = 'hidden'
	}
	_createMsg( parentObj, id){
		var parent = document.getElementById(parentObj);
		var msg = document.createElement("div");
		msg.setAttribute("id", 'msg_' + id);
		msg.setAttribute("class", "cPilotmsg");
		parent.appendChild(msg);
	}
	_createMsgArrow( parentObj, id){
		var parent = document.getElementById(parentObj);
		var msgArrow = document.createElement("div");
		msgArrow.setAttribute("id", 'msgArrow_' + id);
		msgArrow.setAttribute("class", "cPilotMsgArrow");
		parent.appendChild(msgArrow);
		var parentBound = parent.getBoundingClientRect();
		var _leftOffset = (parentBound.width/2) - 3.5;
		msgArrow.style.left = _leftOffset + 'px';
	}
	_createName( parentObj, obj){
		var parent = document.getElementById(parentObj);
		var name = document.createElement("div");
		name.setAttribute("id", 'name_' + obj.id);
		name.setAttribute("class", "cPilotName");
		name.innerHTML = obj.name;
		parent.appendChild(name);
		var parentBound = parent.getBoundingClientRect();
		var nameBound = name.getBoundingClientRect();
		var _leftOffset = (parentBound.width-nameBound.width)/2;
		name.style.left = _leftOffset + 'px';
		name.style.top = parentBound.height + 'px';
	}
	_createHp( parentObj, id){
		var parent = document.getElementById(parentObj);
		var hp = document.createElement("div");
		hp.setAttribute("id", 'HPboarder_' + id);
		hp.setAttribute("class", "cPilotHP");
		hp.style.border = '1px solid #000';
		hp.style.backgroundColor = '#FFF';
		parent.appendChild(hp);
		var parentBound = parent.getBoundingClientRect();
		var hpBound = hp.getBoundingClientRect();
		var _leftOffset = (parentBound.width-hpBound.width)/2;
		hp.style.left = _leftOffset + 'px';

		var parent = document.getElementById('HPboarder_' + id);
		var hp = document.createElement("span");
		hp.setAttribute("id", 'HP_' + id);
		hp.setAttribute("class", "cPilotHP");
		hp.style.opacity = 1;
		parent.appendChild(hp);
		var parentBound = parent.getBoundingClientRect();
		var hpBound = hp.getBoundingClientRect();
		hp.style.top = '0px';
		hp.style.left = '0px';
	}
	_createMain( parentObj, id){
		var parent = document.getElementById(parentObj);
		var pilot = document.createElement("div");
		pilot.setAttribute("id", id);
		pilot.setAttribute("class", "cPilot");
		parent.appendChild(pilot);
	}
	_shapeMain(obj, pic){
		var _obj = document.getElementById(obj.id);
		_obj.style.width = obj.W + 'px';
		_obj.style.height = obj.H + 'px';
		allObj[allObj.length] = obj;
	}
}
