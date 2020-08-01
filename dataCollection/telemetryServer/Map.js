class MapGraphic {
    constructor(canvasBase) {
        var canvas = document.createElement("div");
        canvas.style.position = "absolute";
        canvas.style.width = "100%"
        canvas.style.height = "100%"
        canvas.style.overflow = "auto"
        canvasBase.appendChild(canvas);
        this.minX = Infinity;
        this.maxX = -Infinity;
        this.minY = Infinity;
        this.maxY = -Infinity;
        this.canvas = canvas;
        this.overlay = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        this.overlay.setAttribute("class", "map");
        this.overlay.style.overflow = "visible";
        this.overlay.style.zIndex = "1";
        //this.overlay.setAttribute("viewBox","0 0 100 100");
        //this.overlay.style.height="100px";
        //this.overlay.style.width="100px";
        //this.overlay.setAttribute("height",this.backgroundImage.style.height*0+200+"px");
        //this.overlay.setAttribute("width",this.backgroundImage.style.width*0+200+"px");
        canvas.appendChild(this.overlay);
        this.canvas = canvas;
        /**@type {MapPart[]} */
        this.images = [];
        this.zoomFactor = 10000;
        var zoomIn = document.createElement("button");
        zoomIn.style.position = "absolute";
        zoomIn.style.left = "50px";
        zoomIn.innerHTML = "+";
        zoomIn.onclick = function () {
            var oldX = this.canvas.scrollLeft;
            var oldY = this.canvas.scrollTop;
            this.zoomFactor *= 2;
            this.fitMaps();
            this.canvas.scrollTo(oldX * 2, oldY * 2);
        }.bind(this);
        zoomIn.style.zIndex = 4;
        canvasBase.appendChild(zoomIn);
        var zoomOut = document.createElement("button");
        zoomOut.style.position = "absolute";
        zoomOut.style.left = "100px";
        zoomOut.innerHTML = "-";
        zoomOut.onclick = function () {
            var oldX = this.canvas.scrollLeft;
            var oldY = this.canvas.scrollTop;
            this.zoomFactor /= 2;
            this.fitMaps();
            this.canvas.scrollTo(oldX / 2, oldY / 2);
        }.bind(this);
        zoomOut.style.zIndex = 4;
        canvasBase.appendChild(zoomOut);
    }
    /**@param {MapPart} p */
    addMapPart(p) {
        this.images.push(p);
        var change = false;
        if (p.x < this.minX) {
            this.minX = p.x;
            change = true;
        }
        if (p.y > this.maxY) {
            this.maxY = p.y;
            change = true;
        }
        if (p.y - p.h < this.minY) {
            this.minY = p.y - p.h;
            //change=true;
        }
        if (p.x + p.w > this.maxX) {
            this.maxX = p.x + p.w;
            //change=true;
        }
        if (change) {
            this.fitMaps();
        } else {
            p.backgroundImage.style.left = (p.x - this.minX) * this.zoomFactor + "px";
            p.backgroundImage.style.top = (this.maxY - p.y) * this.zoomFactor + "px";
        }
        p.backgroundImage.style.height = p.h * this.zoomFactor + "px";
        p.backgroundImage.style.width = p.w * this.zoomFactor + "px";
        /*var backgroundImage=document.createElement("img");
        backgroundImage.setAttribute("src",backgroundImagePath);
        backgroundImage.setAttribute("class","map");
        this.canvas.appendChild(backgroundImage);*/
        this.canvas.appendChild(p.backgroundImage);
    }
    fitMaps() {
        for (var img of this.images) {
            img.backgroundImage.style.left = (img.x - this.minX) * this.zoomFactor + "px";
            img.backgroundImage.style.top = (this.maxY-img.y) * this.zoomFactor + "px";
            img.backgroundImage.style.height = img.h * this.zoomFactor + "px";
            img.backgroundImage.style.width = img.w * this.zoomFactor + "px";
        }
        this.overlay.setAttribute("viewBox", "0 0 1 1");
        this.overlay.style.top = this.maxY * this.zoomFactor + "px";
        this.overlay.style.left = -this.minX * this.zoomFactor + "px";
        this.overlay.style.height = this.zoomFactor + "px";
    }
    drawLine(x1, y1, x2, y2, color = "black") {
        if (isNaN(x1 + y1 + x2 + y2))
            return;
        if (this.minX > x1 || this.minX > x2) {
            this.minX = Math.min(x1, x2);
        }
        if (this.maxX < x1 || this.maxX < x2) {
            this.maxX = Math.max(x1, x2);
        }
        if (this.minY > y1 || this.minY > y2) {
            this.minY = Math.min(y1, y2);
        }
        if (this.maxY < y1 || this.maxY < y2) {
            this.maxY = Math.max(y1, y2);
        }
        var line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute("x1", x1);
        line.setAttribute("y1", -y1);
        line.setAttribute("x2", x2);
        line.setAttribute("y2", -y2);
        line.setAttribute("stroke", color);
        line.setAttribute("stroke-width", 0.5 / this.zoomFactor);
        this.overlay.appendChild(line);
        this.fitMaps();
    }
    xConv(x = 0) {
        return (x - this.minX) * this.zoomFactor;
    }
    yConv(y = 0) {
        return (y - this.minY) * this.zoomFactor;
    }
}
class MapPart {
    /**
     * 
     * @param {string} backgroundImagePath 
     * @param {number} x x of left part of map
     * @param {number} y y of top part of map
     * @param {number} w width of map
     * @param {number } h height of map
     */
    constructor(backgroundImagePath, x, y, w, h) {
        this.backgroundImage = document.createElement("img");
        this.backgroundImage.setAttribute("src", backgroundImagePath);
        this.backgroundImage.setAttribute("class", "map");
        this.x = x;
        this.y = y;
        this.h = h;
        this.w = w;
    }
}
