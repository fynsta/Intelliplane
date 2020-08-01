class Point {
    constructor(x = 0, y = 0) {
        this.x = x;
        this.y = y;
    }
}
class Mover{
    constructor(element=document.createElement("div"),tarX,tarY,x,y){
        this.tarX=tarX;
        this.tarY=tarY;
        this.x=x;
        this.y=y;
    }
    
}

class SwipeElementItem {
    constructor(swipeElement) {
        this.swipeElement = swipeElement;
        this.rafPending = false;
        this.initialTouchPos = null;
        this.lastTouchPos = null;
        this.lastControlXRest = 0;
        this.lastControlYRest = 0;
        this.currentVX = 0;
        this.currentVY = 0;
        this.currentX = 0;
        this.currentY = 0;

        this.onMove = function (swipeControler = new SwipeElementItem(null)) {

        }
        this.lastMove = new Point(0, 0);
        this.lastUpdate = new Date().getTime();
        this.pointToMove = function (point = new Point(0, 0)) {
            return point;
        }
        this.moveToPoint = function (move = new Point(0, 0)) {
            return move;
        }
        this.onMoveEnd = function (swipeControler= new SwipeElementItem(null),mousePosition=new Point(0,0)) {

        }
        this.onMoveStart=function (swipeControler= new SwipeElementItem(null)) {

        }
        if (window.PointerEvent) {
            // Add Pointer Event Listener
            swipeElement.addEventListener('pointerdown', this.handleGestureStart.bind(this), true);
            swipeElement.addEventListener('pointermove', this.handleGestureMove.bind(this), true);
            swipeElement.addEventListener('pointerup', this.handleGestureEnd.bind(this), true);
            swipeElement.addEventListener('pointercancel', this.handleGestureEnd.bind(this), true);
        } else {
            // Add Touch Listener
            swipeElement.addEventListener('touchstart', this.handleGestureStart.bind(this), true);
            swipeElement.addEventListener('touchmove', this.handleGestureMove.bind(this), true);
            swipeElement.addEventListener('touchend', this.handleGestureEnd.bind(this), true);
            swipeElement.addEventListener('touchcancel', this.handleGestureEnd.bind(this), true);

            // Add Mouse Listener
            swipeElement.addEventListener('mousedown', this.handleGestureStart, true);
        }
    }

    getTimeStep() {
        var currentTime = new Date().getTime();
        var toReturn = currentTime - this.lastUpdate;
        this.lastUpdate = currentTime;
        return toReturn;
    }
    // Handle the start of gestures
    handleGestureStart(evt) {
        this.onMoveStart(this);
        evt.preventDefault();

        if (evt.touches && evt.touches.length > 1) {
            return;
        }
        // Add the move and end listeners
        if (window.PointerEvent) {
            evt.target.setPointerCapture(evt.pointerId);
        } else {
            // Add Mouse Listeners
            document.addEventListener('mousemove', this.handleGestureMove, true);
            document.addEventListener('mouseup', this.handleGestureEnd, true);
        }
        //document.style.touchaction="none";
        this.initialTouchPos = this.getGesturePointFromEvent(evt);
        this.swipeElement.style.transition = 'initial';
    }
    /* // [END handle-start-gesture] */

    // Handle move gestures
    //
    /* // [START handle-move] */
    handleGestureMove(evt) {
        evt.preventDefault();

        if (!this.initialTouchPos) {
            return;
        }

        this.lastTouchPos = this.getGesturePointFromEvent(evt);

        if (this.rafPending) {
            return;
        }

        this.rafPending = true;

        window.requestAnimationFrame(this.onAnimFrame.bind(this));
    }
    /* // [END handle-move] */

    /* // [START handle-end-gesture] */
    // Handle end gestures
    handleGestureEnd(evt) {
        evt.preventDefault();

        if (evt.touches && evt.touches.length > 0) {
            return;
        }

        this.rafPending = false;

        // Remove Event Listeners
        if (window.PointerEvent) {
            evt.target.releasePointerCapture(evt.pointerId);
        } else {
            // Remove Mouse Listeners
            document.removeEventListener('mousemove', this.handleGestureMove, true);
            document.removeEventListener('mouseup', this.handleGestureEnd, true);
        }
        document.body.style.touchaction="default";
        this.updateSwipeRestPosition();
        this.onMoveEnd(this,this.lastTouchPos);
        this.initialTouchPos = null;
    }
    /* // [END handle-end-gesture] */

    moveElementWithoutTouch(move = new Point(0, 0)) {
        var newXTransform = (move.x) + 'px';
        var newYTransform = (move.y) + 'px';

        var transformStyle = 'translate(' + newXTransform + ", " + newYTransform + ')';
        this.swipeElement.style.webkitTransform = transformStyle;
        this.swipeElement.style.MozTransform = transformStyle;
        this.swipeElement.style.msTransform = transformStyle;
        this.swipeElement.style.transform = transformStyle;

        //adapt control point to new position
        var controlPoint = this.moveToPoint(move);
        this.lastControlXRest = controlPoint.x;
        this.lastControlYRest = controlPoint.y;
        this.rafPending = false;
    }
    updateSwipeRestPosition() {
        var differenceInX = this.initialTouchPos.x - this.lastTouchPos.x;
        this.lastControlXRest = this.lastControlXRest - differenceInX;

        var differenceInY = this.initialTouchPos.y - this.lastTouchPos.y;
        this.lastControlYRest = this.lastControlYRest - differenceInY;
        this.swipeElement.style.transition = 'all 150ms ease-out';
    }

    getGesturePointFromEvent(evt) {
        var point = {};

        if (evt.targetTouches) {
            point.x = evt.targetTouches[0].clientX;
            point.y = evt.targetTouches[0].clientY;
        } else {
            // Either Mouse event or Pointer Event
            point.x = evt.clientX;
            point.y = evt.clientY;
        }

        return point;
    }

    /* // [START on-anim-frame] */
    onAnimFrame() {
        if (!this.rafPending) {
            return;
        }

        //var differenceInX = this.initialTouchPos.x - this.lastTouchPos.x;
        //var differenceInY = this.initialTouchPos.y - this.lastTouchPos.y;
        this.currentX = this.lastControlXRest - this.initialTouchPos.x + this.lastTouchPos.x;
        this.currentY = this.lastControlYRest - this.initialTouchPos.y + this.lastTouchPos.y;
        var move = this.pointToMove(new Point(this.currentX, this.currentY));
        /*var newXTransform = (move.x) + 'px';
        var newYTransform = (move.y) + 'px';

        var transformStyle = 'translate(' + newXTransform + ", " + newYTransform + ')';
        this.swipeElement.style.webkitTransform = transformStyle;
        this.swipeElement.style.MozTransform = transformStyle;
        this.swipeElement.style.msTransform = transformStyle;
        this.swipeElement.style.transform = transformStyle;*/
        SwipeElementItem.moveElement(move.x,move.y,this.swipeElement);
        this.onMove(this);
        this.updateV(new Point(this.currentX, this.currentY));
        this.rafPending = false;
    }
    static moveElement(x = 0, y = 0, el) {
        var newXTransform = x + 'px';
        var newYTransform = y + 'px';

        var transformStyle = 'translate(' + newXTransform + ", " + newYTransform + ')';
        el.style.webkitTransform = transformStyle;
        el.style.MozTransform = transformStyle;
        el.style.msTransform = transformStyle;
        el.style.transform = transformStyle;
    }
    static savePosition(toSave=document.createElement("div")){
        var rect=toSave.getBoundingClientRect();
        toSave.oldX=rect.left;
        toSave.oldY=rect.top;
    }
    static slideElement(toSlide=document.createElement("div")){
        //var oldX=toSlide.clientLeft;
        //var oldY=toSlide.clientTop;
        //toSlide.parentElement.removeChild(toSlide);
        //newParent.children.item(childNumber).insertBefore(toSlide);
        var rect=toSlide.getBoundingClientRect();
        
        SwipeElementItem.moveElement(toSlide.oldX-rect.left,toSlide.oldY-rect.top,toSlide);

    }
    updateV(newMove = new Point(0, 0)) {
        var dt = this.getTimeStep();
        if (dt == 0) {
            return;
        }
        this.currentVX += ((newMove.x - this.lastMove.x) / dt - this.currentVX) * (1 - 0*Math.pow(0.99, dt));
        this.currentVY += ((newMove.y - this.lastMove.y) / dt - this.currentVY) * (1 - 0*Math.pow(0.99, dt));
        this.lastMove = newMove;
    }
    /* // [END on-anim-frame] */

    /* // [START addlisteners] */
    // Check if pointer events are supported.

    /* // [END addlisteners] */
}
