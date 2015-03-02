var gTimeout;
var gRefreshTime=30000;
var gLastSearchTime;

function displayData(jsonData)
{
    var data = JSON.parse(jsonData); 
    var status_html = Process(jsonData);
    $("#display").html(status_html);

}

var host = 'ws://127.0.0.1:9999/result';

var websocket = new WebSocket(host);

websocket.onopen = function (evt){};
websocket.onmessage = function(evt){
    displayData(evt.data)
}
websocket.onerror = function (evt) { };

function send(){
    var data = JSON.stringify({
    args:
        {   starttime : $("#starttime").val(),
            endtime   : $("#endtime").val(),
            startver  : $("#startver").val(),
            endver    : $("#endver").val(),
            optionid  : $("#optionid").val()
        },
    name      : $("#option").val() + "_" + $("#context").val()
}) ;
   
    websocket.send(data)
}
