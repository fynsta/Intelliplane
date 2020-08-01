const lightYellow = "rgb(255, 244, 120)";
class Instrument {
    /**@param {HTMLCanvasElement} canvas*/
    constructor(canvas) {
        this.canvas = canvas;
        this.canvasDrawer = canvas.getContext("2d");
        this.resize();
        this.draw();
        instruments.length++;
        instruments[instruments.length - 1] = this;
        this.minArea = 200 * 50
    }
    resize() {
        this.height = this.canvas.clientHeight;
        this.width = this.canvas.clientWidth;
        var area = this.width * this.height;
        var factor = area / this.minArea;
        if (factor < 1) {
            this.height /= factor;
            this.width /= factor;
            writeToConsole("zu klein");
        }
        this.canvas.height = this.height;
        this.canvas.width = this.width;
    }
    draw() {
        alert("hii");
    }
}
class ArtificialHorizon extends Instrument {
    constructor(canvas) {
        super(canvas);
        this.horizonImage = document.getElementById("artificialHorizonImage");
        this.pitch = 10;
        this.radBank = 0;
        this.bank = 0;
        this.onePitchDegree = 0;
        this.bigLine = 0;
        this.smallLine = 0;
        this.mediumLine = 0;
        this.maxPitchValue = 0;
        this.canvas.style.backgroundColor = "blue";
        this.minArea = 400 * 400;
        this.canvasDrawer.textAlign = "center";
        this.elv = 0;
        this.rud = 0;
        this.ail = 0;
        this.thr = 0;
    }
    setPitch(pitchRad) {
        /*while(pitchRad>Math.PI){
            pitchRad-=Math.PI
        }
        while(pitchRad<-Math.PI){
            pitchRad+=Math.PI;
        }*/
        this.pitch = pitchRad * 180 / Math.PI;
        if (Math.abs(this.pitch) > 360) {
            this.pitch = 0;
        }
    }
    setBank(bankRad) {
        this.bank = bankRad * 180 / Math.PI;
        this.radBank = bankRad;
    }
    /**
     * 
     * @param {Float32Array} input 
     */
    setRxInput(input) {
        this.thr = input[0];
        this.elv = input[1];
        this.ail = input[2];
        this.rud = input[3];
    }
    resize() {
        super.resize();


        this.canvasDrawer.translate(this.width / 2, this.height / 2);
        this.onePitchDegree = this.height / 40;
        this.bigLine = this.width / 20;
        this.smallLine = this.width / 100;
        this.mediumLine = this.width / 50;
        this.maxPitchValue = 0.6 * Math.sqrt(this.height * this.height + this.width * this.width);
    }
    draw() {
        this.canvasDrawer.setTransform(1, 0, 0, 1, 0, 0);
        this.canvasDrawer.clearRect(0, 0, this.width, this.height);
        this.canvasDrawer.translate(this.width / 2, this.height / 2);


        this.canvasDrawer.rotate(-this.radBank);
        this.canvasDrawer.fillStyle = "brown";
        this.canvasDrawer.fillRect(-this.maxPitchValue, this.onePitchDegree * this.pitch, this.maxPitchValue * 2, this.maxPitchValue * 2);
        this.canvasDrawer.strokeStyle = "#FFFFFF";
        this.canvasDrawer.lineWidth = this.height / 400;
        var i = 0;
        for (var y = this.onePitchDegree * this.pitch; y < this.maxPitchValue; y += 2.5 * this.onePitchDegree) {
            this.canvasDrawer.beginPath();
            if (i % 10 == 0) {
                this.canvasDrawer.moveTo(-this.bigLine, y);
                this.canvasDrawer.lineTo(this.bigLine, y);
            } else if (i % 5 == 0) {
                this.canvasDrawer.moveTo(-this.mediumLine, y);
                this.canvasDrawer.lineTo(this.mediumLine, y);
            } else {
                this.canvasDrawer.moveTo(-this.smallLine, y);
                this.canvasDrawer.lineTo(this.smallLine, y);
            }
            this.canvasDrawer.stroke();
            if (i % 10 == 0 && i != 0) {
                this.canvasDrawer.textAlign = "center";
                this.canvasDrawer.textBaseline = "middle";
                this.canvasDrawer.strokeText(i, -this.bigLine - this.mediumLine, y);
                this.canvasDrawer.strokeText(i, this.bigLine + this.mediumLine, y);
            }
            i -= 2.5;
        }
        i = 0;
        for (var y = this.onePitchDegree * this.pitch; y > -this.maxPitchValue; y -= 2.5 * this.onePitchDegree) {
            if (i % 10 == 0) {
                this.canvasDrawer.moveTo(-this.bigLine, y);
                this.canvasDrawer.lineTo(this.bigLine, y);
            } else if (i % 5 == 0) {
                this.canvasDrawer.moveTo(-this.mediumLine, y);
                this.canvasDrawer.lineTo(this.mediumLine, y);
            } else {
                this.canvasDrawer.moveTo(-this.smallLine, y);
                this.canvasDrawer.lineTo(this.smallLine, y);
            }
            this.canvasDrawer.stroke();
            if (i % 10 == 0 && i != 0) {
                this.canvasDrawer.textAlign = "center";
                this.canvasDrawer.textBaseline = "middle";
                this.canvasDrawer.strokeText(i, -this.bigLine - this.mediumLine, y);
                this.canvasDrawer.strokeText(i, +this.bigLine + this.mediumLine, y);
            }
            i += 2.5;
        }


        this.canvasDrawer.setTransform(1, 0, 0, 1, 0, 0);
        //draw inputs
        this.canvasDrawer.rect(this.width * this.rud - 5, this.height * this.elv - 5, 10, 10);
        this.canvasDrawer.stroke();

        this.canvasDrawer.translate(this.width / 2, this.height / 2);
        this.canvasDrawer.strokeStyle = lightYellow;
        this.canvasDrawer.lineWidth = this.height / 50;
        this.canvasDrawer.beginPath();
        this.canvasDrawer.moveTo(-0.4 * this.width, 0);
        this.canvasDrawer.lineTo(-0.1 * this.width, 0);
        this.canvasDrawer.lineTo(-0.1 * this.width, this.height / 20);
        this.canvasDrawer.stroke();
        this.canvasDrawer.beginPath();
        this.canvasDrawer.moveTo(0.4 * this.width, 0);
        this.canvasDrawer.lineTo(0.1 * this.width, 0);
        this.canvasDrawer.lineTo(0.1 * this.width, this.height / 20);
        this.canvasDrawer.stroke();
        this.canvasDrawer.rect(-this.canvasDrawer.lineWidth / 2, -this.canvasDrawer.lineWidth / 2, this.canvasDrawer.lineWidth, this.canvasDrawer.lineWidth);
        this.canvasDrawer.stroke();



    }
}
class ValueDrawer extends Instrument {
    constructor(canvas, horizonal = false, valueRange = 100, numOfValues = 10, valueToText = (value) => value) {
        super(canvas);
        this.horizonal = horizonal;
        this.value = 0;
        this.valueRange = valueRange;
        this.numOfValues = numOfValues;
        if (horizonal) {
            this.minArea *= 2;
        }
        this.valueToText = valueToText;
        this.canvasDrawer.translate(this.height / 2, this.width / 2);
    }
    resize() {
        super.resize();
        this.canvasDrawer.setTransform(1, 0, 0, 1, 0, 0);
        this.canvasDrawer.translate(this.width / 2, this.height / 2);

    }
    draw() {
        if (Math.abs(this.value) > 1000000)
            return;
        var minValueToDraw = this.value - this.valueRange / 2;
        minValueToDraw -= minValueToDraw % (this.valueRange / this.numOfValues);
        var maxValueToDraw = minValueToDraw + this.valueRange;
        var step = this.valueRange / this.numOfValues;
        this.canvasDrawer.clearRect(-this.width / 2, -this.height / 2, this.width, this.height);
        this.canvasDrawer.strokeStyle = "#FFFFFF";
        this.canvasDrawer.textAlign = "center";
        this.canvasDrawer.textBaseline = "middle";
        if (this.horizonal) {
            for (var value = minValueToDraw; value <= maxValueToDraw; value += step) {
                var coordinate = this.valueToX(value);
                this.canvasDrawer.beginPath();
                this.canvasDrawer.moveTo(coordinate, 0);
                this.canvasDrawer.lineTo(coordinate, -this.height / 2);
                this.canvasDrawer.stroke();
                this.canvasDrawer.strokeText(this.valueToText(value), coordinate, 0);
            }
            this.canvasDrawer.strokeStyle = lightYellow;
            var coordinate = 0;
            this.canvasDrawer.beginPath();
            this.canvasDrawer.moveTo(coordinate, -this.height / 4);
            this.canvasDrawer.lineTo(coordinate + 5, -this.height / 2);
            this.canvasDrawer.lineTo(coordinate - 5, -this.height / 2);
            this.canvasDrawer.closePath();
            this.canvasDrawer.stroke();
        } else {
            for (var value = minValueToDraw; value <= maxValueToDraw; value += step) {
                var coordinate = this.valueToY(value);
                this.canvasDrawer.beginPath();
                this.canvasDrawer.moveTo(0, coordinate);
                this.canvasDrawer.lineTo(-this.width / 2, coordinate);
                this.canvasDrawer.stroke();
                this.canvasDrawer.strokeText(this.valueToText(value), 0, coordinate);
            }
            var coordinate = 0
            this.canvasDrawer.strokeStyle = lightYellow;
            this.canvasDrawer.beginPath();
            this.canvasDrawer.moveTo(-this.width / 4, coordinate);
            this.canvasDrawer.lineTo(-this.width / 2, coordinate + 5);
            this.canvasDrawer.lineTo(-this.width / 2, coordinate - 5);
            this.canvasDrawer.closePath();
            this.canvasDrawer.stroke();
        }
    }
    valueToY(value) {
        return -(value - this.value) * this.height / this.valueRange;
    }
    valueToX(value) {
        return (value - this.value) * this.width / this.valueRange;
    }
}