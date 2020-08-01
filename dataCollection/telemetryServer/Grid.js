
function addColumn() {
    hideResizer();
    columns++;
    setGridSizes();
}
function deleteColumn() {
    hideResizer();
    if (columns < 2) {
        return;
    }
    columns--;
    setGridSizes();
}

function setWindowSizes() {
    with (artificialHorizon.canvas) {
        style.height = parentElement.clientHeight * 0.9 + "px";
        style.width = parentElement.clientWidth * 0.9 + "px";
        style.marginLeft = parentElement.clientWidth * 0.05 + "px";
    }
    artificialHorizon.resize();
    with (speedDisplay.canvas) {
        style.height = parentElement.clientHeight * 0.9 + "px";
        style.width = parentElement.clientWidth / 20 + "px";
    }
    speedDisplay.resize();
    with (altitudeDisplay.canvas) {
        style.height = parentElement.clientHeight * 0.9 + "px";
        style.width = parentElement.clientWidth / 20 + "px";
        style.marginLeft = parentElement.clientWidth * 0.95 + "px";
    }
    altitudeDisplay.resize();
    with (compass.canvas) {
        style.height = parentElement.clientHeight / 10 + "px";
        style.width = parentElement.clientWidth + "px";
        style.marginLeft = parentElement.clientWidth * 0.0 + "px";
        style.marginTop = parentElement.clientHeight * 0.9 + "px";
    }
    compass.resize();
    //drawAH();
}
var finishedDrawing = true;
function drawInstruments() {
    finishedDrawing = false;
    instruments.forEach(function (element) { element.draw() });
    finishedDrawing = true;
    //setTimeout(drawInstruments, 1000 / framerate);
    window.requestAnimationFrame(drawInstruments);

}
function resetDisplays() {
    //columns=3;
    for (var i = displays.length - 1; i >= 0; i--) {
        selectDisplay(i);
    }
    setWindowSizes();
}
function selectDisplay(a) {
    /*var row=1;
    if(a>2){
        row=2;
    }*/
    row = Math.floor(a / columns) + 1;
    //var column=1+(a%3);
    column = 1 + a % columns;
    //grid.setValue(displays[a],row,column);
    displays[a].style.gridColumnStart = column;
    displays[a].style.gridColumnEnd = column;
    displays[a].style.gridRowStart = row;
    displays[a].style.gridRowEnd = row;
}
function setGridSizes() {
    var height = this.window.innerHeight;
    var width = this.window.innerWidth;
    var c = "";
    widths = new Array(columns);
    for (var i = 0; i < columns; i++) {
        widths[i] = (i + 1) * width / columns;
        c += width / columns + "px ";
    }
    grid.style.gridTemplateColumns = c;
    c = "";
    var rows = Math.ceil(displays.length / columns);
    if(height / rows<0.8*width / columns){
        height=rows*0.8*width / columns;
    }
    heights = new Array(rows);
    for (var i = 0; i < rows; i++) {
        heights[i] = (i + 1) * height / rows;
        c += height / rows + "px ";
    }
    grid.style.gridTemplateRows = c;
    resetDisplays();
}
function updateFramerate() {
    framerate = document.getElementById("framerateSetter").value;
}

var swipeXItems = [];
var swipeYItems = [];
function resizeGridInitiator() {
    grid.style.touchAction = "none";
    swipeXItems = [];
    swipeYItems = [];
    resizerButton.onclick = hideResizer;
    resizerButton.value = "stop resizing grid";
    heights = grid.style.gridTemplateRows.split("px");
    widths = grid.style.gridTemplateColumns.split("px");
    var last = 0;
    for (var i = 0; i < heights.length - 1; i++) {
        heights[i]++;
        heights[i]--;
        var resizer = document.createElement("div");
        resizer.setAttribute("class", "resizerH");
        resizer.style.top = heights[i] + last - 5 + "px";
        last += heights[i];
        resizer.yIndex = i;
        grid.insertBefore(resizer, grid.childNodes[0] || null);
        swipeYItems[i] = new SwipeElementItem(resizer);
        swipeYItems[i].pointToMove = function (point = new Point(0, 0)) {
            return new Point(0, point.y);
        }
        swipeYItems[i].onMoveStart = function (swipeControler) {
            grid.style.touchAction = "none";
        }
        swipeYItems[i].onMoveEnd = function (swipeControler) {
            var yChange = swipeControler.currentY;
            heights[swipeControler.swipeElement.yIndex] += yChange;
            var sum = 0;
            for (var i in heights) {
                sum += heights[i];
            }
            grid.style.height = sum + "px";
            var c = "";
            for (var i = 0; i < heights.length - 1; i++) {
                c += heights[i] + "px ";
            }
            grid.style.gridTemplateRows = c;
            setWindowSizes();
            hideResizer();
            resizeGridInitiator();
            //grid.style.touchAction="auto";
        }
    }
    last = 0;
    for (var i = 0; i < widths.length - 1; i++) {
        widths[i]++;
        widths[i]--;
        var resizer = document.createElement("div");
        resizer.setAttribute("class", "resizerW");
        resizer.style.left = widths[i] - 5 + last + "px";
        last += widths[i];
        resizer.xIndex = i;
        grid.insertBefore(resizer, grid.childNodes[0] || null);
        swipeXItems[i] = new SwipeElementItem(resizer);
        swipeXItems[i].pointToMove = function (point = new Point(0, 0)) {
            return new Point(point.x);
        }
        swipeXItems[i].onMoveStart = function (swipeControler) {
            grid.style.touchAction = "none";
        }
        swipeXItems[i].onMoveEnd = function (swipeControler) {
            var xChange = swipeControler.currentX;
            widths[swipeControler.swipeElement.xIndex] += xChange;
            var sum = 0;
            for (var i in widths) {
                sum += widths[i];
            }
            grid.style.width = sum + "px";
            var c = "";
            for (var i = 0; i < widths.length - 1; i++) {
                c += widths[i] + "px ";
            }
            grid.style.gridTemplateColumns = c;
            setWindowSizes();
            hideResizer();
            resizeGridInitiator();
            //grid.style.touchAction="auto";
        }
    }
}
function hideResizer() {
    resizerButton.onclick = resizeGridInitiator;
    resizerButton.value = "resize grid";
    try {
        swipeXItems.forEach(function (el) {
            grid.removeChild(el.swipeElement);
        });
        swipeYItems.forEach(function (el) {
            grid.removeChild(el.swipeElement);
        });

    } catch (error) {

    }
    grid.style.touchAction = "auto";
}