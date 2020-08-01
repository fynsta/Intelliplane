function connect() {
    webSocket = new WebSocket("ws://" + document.getElementById("wssInput").value, "ws");
    webSocket.binaryType = "arraybuffer";
    webSocket.onerror = function (event) {
        console.error("Fehler: ", event);
        disconnect();
    }
    webSocket.onopen = function (event) {
        writeToConsole("connection established");
        document.getElementById("connectionIndicator").value = "disconnect";
    };
    webSocket.onmessage = function (event) {
        if (event.data == "fd") {
            //writeToConsole("new flight data package incoming");
            transferStatus = "fd";
        } else if (event.data == "headDefinition") {
            transferStatus = "headDefinition";
        } else if (transferStatus == "deviceList") {
            var list = JSON.parse(event.data);
            deviceSelector.options.length = list.length;
            for (var i = 0; i < list.length; i++) {
                deviceSelector.options[i].label = list[i];
                deviceSelector.options[i].value = list[i];
            }
            setDevice();
        } else if (event.data == "deviceList") {
            transferStatus = "deviceList";
        } else if (transferStatus == "fd") {
            if (!finishedDrawing) {
                console.log("too fast!!!");
                //finishedDrawing=true;
                //return;
            }
            finishedDrawing = false;
            binaryData = event.data;
            position = 1;
            //writeToConsole("data recieved: "+Date.now());
            //console.log("data recieved: "+Date.now());
            var headNumber = new Uint8Array(event.data.slice(0, 1))[0];
            currentHead = heads[headNumber];
            if (!currentHead)
                return;
            if (event.data.byteLength != 21 && headNumber == 2) {
                return;
            }
            currentFrame={pcTime:new Date().getTime()};
            for (var headPosition = 0; headPosition < currentHead.length; headPosition++) {
                planeParameters[currentHead[headPosition]]();
            }
            if (position != event.data.byteLength) {
                console.log("uebertragungsfehler");
                currentFrame.error="wrong message length";
            }
            dataLog.push(currentFrame);
            artificialHorizon.draw();
            finishedDrawing = true;
            //console.log("finishedDrawing!!!");
        } else if (transferStatus == "headDefinition") {
            heads[new Uint8Array(event.data.slice(0, 1))[0]] = new Uint8Array(event.data.slice(1));
        }
    };
    webSocket.onclose = disconnect;
    document.getElementById("connector").value = "";
}
function disconnect() {
    //alert("geschlossen");
    currentHead = null;
    writeToConsole("connection closed");
    document.getElementById("connectionIndicator").value = "";
    document.getElementById("connector").value = "connect to server";
    heads = [];
    deviceSelector.options.length = 0;
}
function setDevice() {
    webSocket.send("selectDevice " + deviceSelector.options.selectedIndex);
    console.log("device:" + deviceSelector.value.label);

}
function refresh() {
    if (!webSocket || webSocket.readyState != webSocket.OPEN)
        return;
    webSocket.send("requestDeviceList");
    //transferStatus=2;
    //deviceSelector.options.length++;
    //deviceSelector.options[deviceSelector.options.length-1].label=deviceSelector.options.length;
}
function download(filename, text) {
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);
  
    element.style.display = 'none';
    document.body.appendChild(element);
  
    element.click();
  
    document.body.removeChild(element);
  }