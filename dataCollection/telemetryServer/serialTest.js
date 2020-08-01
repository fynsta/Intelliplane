var SerialPort = require('serialport');
var port = new SerialPort("/dev/ttyUSB0", { baudRate: 9600, autoOpen: true ,lock:true});
port.on("data", (data) => {
    console.log("data: "+data);
});
port.on("open", ev => {
    console.log("isOpen!");
    setInterval(() => {
        port.write("{setLED:100}");
        console.log("sending test message");
    }, 1000);

})