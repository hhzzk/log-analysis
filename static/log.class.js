var areaArray = new Array();
  areaArray[areaArray.length]=new Array("host","主机");
  areaArray[areaArray.length]=new Array("app","设备");
  areaArray[areaArray.length]=new Array("dev","终端");
  areaArray[areaArray.length]=new Array("server","服务器");
  areaArray[areaArray.length]=new Array("ip","IP地址");

var townArray = new Array();
  townArray[townArray.length]=new Array("host","netstatus","断网/连网时间");
  townArray[townArray.length]=new Array("host","authfailtimes","验证失败次数"); 

  townArray[townArray.length]=new Array("app","netstatus","断网/连网时间");
  townArray[townArray.length]=new Array("app","statuschange","状态改变列表");
  townArray[townArray.length]=new Array("dev","loginconn","登录/连接时间"); 
  townArray[townArray.length]=new Array("dev","authfailtimes","验证失败次数");
  townArray[townArray.length]=new Array("dev","doop","用户操作列表(DO)");
  townArray[townArray.length]=new Array("dev","sceneop","情景模式操作(SCENE)");
  townArray[townArray.length]=new Array("dev","alarmop","闹钟操作(ALARM)");
  townArray[townArray.length]=new Array("dev","modifyop","安防系统操作(MODIFY)");
  townArray[townArray.length]=new Array("server","statuschange","状态改变列表");
  townArray[townArray.length]=new Array("server","servererror","Server出错列表");
  townArray[townArray.length]=new Array("server","dberror","DB出错列表");
  townArray[townArray.length]=new Array("server","debugerror","Debug出错列表");

  townArray[townArray.length]=new Array("ip","open","打开断开次数");

 // townArray[townArray.length]=new Array("application","attrchange","属性改变(dbserver)");
 
function setTown(obj1ID,obj2ID){
  var objArea = document.getElementById(obj1ID);
  var objTown = document.getElementById(obj2ID);
  var i;
  var itemArray = null;

  if(objArea.value.length > 0){
      itemArray = new Array();
      for(i=0;i<townArray.length;i++){
          if(townArray[i][0]==objArea.value){
              itemArray[itemArray.length]=new Array(townArray[i][1],townArray[i][2]);
           }
      }
  }

  for(i = objTown.options.length ; i >= 0 ; i--){
       objTown.options[i] = null;
  }

  objTown.options[0] = new Option("请选则");
  objTown.options[0].value = "";
  if(itemArray != null){
    for(i = 0 ; i < itemArray.length; i++){
      objTown.options[i+1] = new Option(itemArray[i][1]);
      if(itemArray[i][0] != null){
          objTown.options[i+1].value = itemArray[i][0];
      }
    }
  }
}
