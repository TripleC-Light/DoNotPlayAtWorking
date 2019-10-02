class Generate{
	constructor(){
		this.state = 'getID';
		this.FSMtrigTime = 50;
		this.ID = '';
	}

	pilot(parent, allObj){
		switch(this.state){
			case 'getID':
				console.log('getID');
				this.ID = '';
				WS.send('getID');
				this.state = 'checkID';
				break;

			case 'checkID':
				console.log('checkID');
				if(this.ID!=''){
					if(idExist(myID, allObj)){
						console.log('ID:' + this.ID + ' already exist');
						this.state = 'finish';
					}else{
						console.log('ID:' + this.ID);
						this.state = 'createPilotInServer';
					}
				}
				break;

			case 'createPilotInServer':
				console.log('createPilotInServer');
				var _positionMode = 'auto';
				// var _positionMode = [35, 350];
				WS.send('createPilot@' + _positionMode);
				this.state = 'createPilot';

			case 'createPilotInWeb':
				console.log('createPilotInWeb');
				var _new = {
					id : this.ID,
					width: 70,
					height: 70,
					name: this.ID,
					pic: ""
				};
				this.newObj(parent, _new);
				var _mainMap = document.getElementById(parent);
				// WS.send('createPilot@' + _mainMap.getBoundingClientRect().left + ',' + _mainMap.getBoundingClientRect().top);
				this.state = 'finish';
				break;
			case 'finish':
				console.log('finish');
				break;
		}
		if( this.state != 'finish' ){
				var thisVar = this;
				setTimeout(function(){
					thisVar.pilot(parent, allObj);
				}, this.FSMtrigTime);
		}else{
			this.state = 'getID';
		}
	}

	newObj( parentObj, obj){
		var _frameID = 'frame_' + obj.id;
		this._createFrame(parentObj, obj.id);
		this._createMsg(_frameID, obj.id);
		this._createMsgArrow(_frameID, obj.id);
		this._createMain(_frameID, obj.id);
		this._createName(_frameID, obj);
		this._createHp(_frameID, obj.id);
		this._shapeMain(obj.id, obj.pic);
	}

	_createFrame( parentObj, id){
		var _id = id;
		var parent = document.getElementById(parentObj);
		var pilotFrame = document.createElement("div");
		pilotFrame.setAttribute("id", 'frame_' + _id);
		pilotFrame.setAttribute("class", "cPilotFrame");
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
	}
	_createName( parentObj, obj){
		var parent = document.getElementById(parentObj);
		var name = document.createElement("div");
		name.setAttribute("id", 'name_' + obj.id);
		name.setAttribute("class", "cPilotName");
		name.innerHTML = obj.id;
		parent.appendChild(name);
		var parentBound = parent.getBoundingClientRect();
		var nameBound = name.getBoundingClientRect();
		var _leftOffset = (parent.getBoundingClientRect().width-name.getBoundingClientRect().width)/2;
		name.style.left = _leftOffset + 'px';
		name.style.top = parent.getBoundingClientRect().height + 'px';
	}
	_createHp( parentObj, id){
		var parent = document.getElementById(parentObj);
		var hp = document.createElement("div");
		hp.setAttribute("id", 'HP_' + id);
		hp.setAttribute("class", "cPilotHP");
		parent.appendChild(hp);
	}
	_createMain( parentObj, id){
		var parent = document.getElementById(parentObj);
		var pilot = document.createElement("div");
		pilot.setAttribute("id", id);
		pilot.setAttribute("class", "cPilot");
		parent.appendChild(pilot);
	}
	_shapeMain(id, pic){
		var _main = new Object(id);
		_main.reBorn();
		allObj[allObj.length] = _main;
	}
}
