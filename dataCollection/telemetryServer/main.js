//document.getElementById("ah").style.width="10px";
"usestrict";


var grid;
var speedDisplay;
var altitudeDisplay;
var artificialHorizon;
var compass;
var map;
var bank = 0;
/**@type {WebSocket} */
var webSocket;
var instruments = [];
var heights = [];
var widths = [];
var displays = [document.createElement("div")];
var devices = [];
var planeParameters = [];
var movers = [document.createElement("div")];
var heads = [];
var currentHead = null;
var deviceSelector;
var transferStatus = 0;
var framerate = 10;
var columns;
var time = 0;
var lat = 0;
var lon = 0;
var position = 0;
var binaryData;
var resizerButton;
var ledPower = 0;
var ledInterval = -1;
var lastXPos = 0;
var lastYPos = 0;
var dataLog = [];
var currentFrame = {};
onresize = setWindowSizes;
planeParameters[0] = function () {
    var b = new Float32Array(binaryData.slice(position, position + 4))[0];
    artificialHorizon.setPitch(b);
    currentFrame.p = b;
    position += 4;
}
planeParameters[1] = function () {
    var b = new Float32Array(binaryData.slice(position, position + 4))[0];
    artificialHorizon.setBank(b);
    currentFrame.b = b;
    position += 4;
}
planeParameters[2] = function () {
    var b = new Float32Array(binaryData.slice(position, position + 4))[0];
    compass.value = b * 180 / 3.1415;
    currentFrame.h = b;
    position += 4;
}
planeParameters[3] = function () {
    var b = new Float32Array(binaryData.slice(position, position + 4))[0];
    altitudeDisplay.value += 0.1 * (b - altitudeDisplay.value);
    currentFrame.a = b;
    position += 4;
}
planeParameters[4] = function () {
    var b = new Float32Array(binaryData.slice(position, position + 4))[0];
    speedDisplay.value += 0.01 * (b - speedDisplay.value);
    currentFrame.s = b;
    position += 4;
}
planeParameters[5] = function () {
    var b = new Uint32Array(binaryData.slice(position, position + 4))[0];
    time = b;
    const date = new Date(time);
    currentFrame.t = b;
    writeToConsole("Zeit: " + timeToString(time));
    position += 4;
}
planeParameters[6] = function () {
    var b = new Float64Array(binaryData.slice(position, position + 8))[0];
    lat = b;
    currentFrame.lat = b;
    position += 8;
}
planeParameters[7] = function () {
    var b = new Float64Array(binaryData.slice(position, position + 8))[0];
    lon = b;
    currentFrame.lon = b;
    if (lon != 0 && lastXPos != 0) {
        map.drawLine(lastXPos, lastYPos, lon, lat);
    }
    if (lon != 0) {
        lastXPos = lon;
        lastYPos = lat;
    }
    position += 8;
}

planeParameters[8] = function () {
    const length = new Uint8Array(binaryData.slice(position, position + 1))[0];
    var enc = new TextDecoder("utf-8");
    var message = enc.decode(binaryData.slice(position + 1, position + 1 + length));
    writeToConsole(message);
    position += length + 1;
    if (message == "set power " + ledPower) {
        window.clearInterval(ledInterval);
        ledInterval = -1;
    }
}
planeParameters[9] = function () {
    const length = new Uint8Array(binaryData.slice(position, position + 1))[0];
    if (binaryData.byteLength < position + 1 + length * 4) {
        throw new Error("message too short");
        return;
    }
    const sensorData = new Float32Array(binaryData.slice(position + 1, position + 1 + length * 4));
    artificialHorizon.setRxInput(sensorData);
    currentFrame.elv = artificialHorizon.elv;
    currentFrame.rud = artificialHorizon.rud;
    currentFrame.ail = artificialHorizon.ail;
    currentFrame.thr = artificialHorizon.thr;
    position += length * 4 + 1;
}
onclose = function () {
    webSocket.close();
}
onload = function () {
    grid = this.document.getElementById("grid");
    if (this.window.innerHeight < this.window.innerWidth) {
        columns = 3;
    } else {
        columns = 1;
    }
    displays[0] = this.document.getElementById("settings");
    displays[1] = this.document.getElementById("pfd");
    displays[2] = this.document.getElementById("map");
    displays[3] = this.document.getElementById("flightData");
    displays[4] = this.document.getElementById("grapher");
    displays[5] = this.document.getElementById("console");
    document.getElementById("wssInput").value = window.location.hostname + ":8081";

    deviceSelector = document.getElementById("deviceSelector");
    deviceSelector.onchange = setDevice;
    speedDisplay = new ValueDrawer(this.document.getElementById("speedDisplay"), false, 10, 10, (value) => value < 0 ? "" : value);
    altitudeDisplay = new ValueDrawer(this.document.getElementById("altitudeDisplay"), false, 50, 5);
    artificialHorizon = new ArtificialHorizon(this.document.getElementById("artificialHorizon"));
    compass = new ValueDrawer(this.document.getElementById("compass"), true, 60, 6, value => ((value + 360) % 360));
    resizerButton = document.getElementById("resizer");
    const commandInput = document.getElementById("commandInput");
    commandInput.onkeypress = ev => {
        if (ev.key == "Enter") {
            webSocket.send("message:{" + ev.target.value + "}");
        }
    }
    setGridSizes();
    const landingLightSlider = this.document.getElementById("landingLightSlider");
    landingLightSlider.onchange = function (ev) {
        ledPower = parseInt(ev.target.value);
        webSocket.send("message:{setLED:" + ledPower + "}");
        if (ledInterval != -1) {
            clearInterval(ledInterval);
        }
        var timesSent = 0;
        ledInterval = setInterval(() => {
            webSocket.send("message:{setLED:" + ledPower + "}");
            if (++timesSent > 20)
                clearInterval(ledInterval);
        }, 300);
    }
    map = new MapGraphic(this.document.getElementById("map"));
    //map.addMapPart();
    map.addMapPart(new MapPart("demomap.png", 8.164838, 50.029121, 8.347979 - 8.164838, 50.029121 - 49.943347));
    window.requestAnimationFrame(drawInstruments);
    makeMovers();
}
function makeMovers() {
    movers = [];
    for (var i = 0; i < displays.length; i++) {
        movers[i] = document.createElement("div");
        movers[i].setAttribute("class", "mover");
    }
}
var moverItems = [];
function makeMoversVisible() {
    var button = document.getElementById("mover");
    button.innerHTML = "stop moving";
    button.onclick = makeMoversInvisible;
    moverItems = [];
    for (var i in movers) {
        displays[i].prepend(movers[i]);
        moverItems[i] = new SwipeElementItem(movers[i]);
        moverItems[i].display = displays[i];
        //var b=displays[i];
        moverItems[i].onMoveStart = function (sc) {
            grid.style.touchAction = "none";
            for (var el of displays) {
                el.style.filter = "blur(5px)";
            }
            this.display.style.filter = "none";
            this.display.style.zIndex = 10;
        }
        moverItems[i].onMove = function (sei) {
            SwipeElementItem.moveElement(sei.currentX, sei.currentY, this.display);
            SwipeElementItem.moveElement(-20, 0, this.swipeElement);
        }.bind(moverItems[i]);
        moverItems[i].onMoveEnd = function (sc, mousePosition) {
            grid.style.touchAction = "default";
            for (var el of displays) {
                el.style.filter = "none";
                el.style.zIndex = "0";
            }
            for (var i in moverItems) {
                moverItems[i].swipeElement.style.zIndex = "10";
            }
            //this.display.style.zIndex="0";
            var below = document.elementsFromPoint(mousePosition.x, mousePosition.y);
            var targetDisplay = null;
            for (var el of below) {
                if (displays.includes(el) && el != this.display) {
                    targetDisplay = el;
                }
            }
            if (targetDisplay == null) {
                return;
            }
            var a = this.display;
            var b = targetDisplay;

            var bufferRS = a.style.gridRowStart;
            var bufferCS = a.style.gridColumnStart;
            var bufferRE = a.style.gridRowEnd;
            var bufferCE = a.style.gridColumnEnd;
            a.style.gridRowStart = b.style.gridRowStart;
            a.style.gridColumnStart = b.style.gridColumnStart;
            a.style.gridRowEnd = b.style.gridRowEnd;
            a.style.gridColumnEnd = b.style.gridColumnEnd;

            b.style.gridRowStart = bufferRS;
            b.style.gridColumnStart = bufferCS;
            b.style.gridRowEnd = bufferRE;
            b.style.gridColumnEnd = bufferCE;
            for (var el of displays) {
                SwipeElementItem.moveElement(0, 0, el);
            }
            for (el of moverItems) {
                this.lastControlXRest = 0;
                this.lastControlYRest = 0;
            }
            setWindowSizes();
        }
    }
}
function makeMoversInvisible() {
    var button = document.getElementById("mover");
    button.innerHTML = "start moving";
    button.onclick = makeMoversVisible;
    for (var i in displays) {
        displays[i].removeChild(movers[i]);
    }
}


function writeToConsole(text) {
    var para = document.createElement("p");
    para.appendChild(document.createTextNode(text));
    var console = document.getElementById("consoleOutput");
    console.appendChild(para);
    while (console.childElementCount > 100) {
        console.removeChild(console.firstChild);
    }
    console.scrollTo(0, console.scrollHeight);
}
function downloadData() {
    download("flight " + new Date().toDateString(), JSON.stringify(dataLog));
    dataLog = [];
}