
var c;
var vx=0;
var vy=0;
var x=0;
var y=0;
var a;
var lastUpdate=0;
onload=function(){
    a=new SwipeElementItem(this.document.getElementById("m"));
    //new SwipeElementItem(this.document.getElementById("m2"));
    c=this.document.getElementById("m2")
    a.onMove=function(swipeControler=new SwipeElementItem(null)){
        SwipeElementItem.moveElement(0.001*Math.pow(swipeControler.currentX,2),swipeControler.currentY,c);
    }
    a.onMoveEnd=function(swipeControler=new SwipeElementItem(null)){
        x=swipeControler.currentX;
        y=swipeControler.currentY;
        vx=swipeControler.currentVX;
        vy=swipeControler.currentVY;
        window.requestAnimationFrame(glide);
    }
}
function glide(){
    var dt=a.getTimeStep();
    x+=dt*vx;
    y+=dt*vy;
    vx*=0.99;
    vy*=0.99;
    SwipeElementItem.moveElement(x,y,a.swipeElement);
    if(vx*vx+vy*vy>0.01){
        window.requestAnimationFrame(glide);
    }else{
        console.log("finished");
    }
}
function getTimeStep() {
    var currentTime = new Date().getTime();
    var toReturn = currentTime - this.lastUpdate;
    lastUpdate = currentTime;
    return toReturn;
}