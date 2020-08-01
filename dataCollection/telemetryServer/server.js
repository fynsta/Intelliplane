var http = require('http');
var url = require('url');
var fs = require('fs');
// var usbDetect = require('usb-detection');
var SerialPort = require('serialport');
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8081 });
var nStatic = require('node-static');

var fileServer = new nStatic.Server('.');

http.createServer(function (req, res) {
	fileServer.serve(req, res);
	console.log(url.parse(req.url, true).pathname);
})
	.listen(8080);
/*http.createServer(function (req, res) {
	console.log(req.url);
  var q = url.parse(req.url, true);
  var filename = "." + q.pathname;
  fs.readFile(filename, function(err, data) {
	if (err) {
	  res.writeHead(404, {'Content-Type': 'text/html'});
	  return res.end("404 Not Found");
	}
	//res.writeHead(200, {'Content-Type': 'text/html'});
	res.write(data);
	return res.end();
  });
}).listen(8080);*/
/**@type {Device[]} */
var devices = [];
var breakRefreshing = false;
/*usbDetect.startMonitoring();
usbDetect.on('add', function(device) {
   console.log('add', device);
   var j=SerialPort.list.length;
   devices.push(new USBDevice)
  });
usbDetect.on('remove', function(device) {
  console.log('remove', device);
  var j=SerialPort.list.length;
  for(var i=0;i<devices.length;i++){
	if(devices[i].equals(device)){
	  devices.splice(i);
	  i--;
	}
  }
});*/
wss.bufferType = 'arraybuffer';
wss.on('connection', function connection(ws) {
	console.log('new connection established');
	devices[0] = new DemoDevice(ws);
	ws.selectedDevice = 0;
	ws.on('message', function incoming(message) {
		if (message == 'requestDeviceList') {
			breakRefreshing = true;
			SerialPort.list().then(
				ports => {
					ports.forEach(function (port) {
						// console.log(port.comName);
						if (!comNameKnown(port.path)) {
							devices.push(new USBDevice(port.path));
						}
						// console.log(port.pnpId);
						// console.log(port.manufacturer);
					});
					devices = devices.filter(function (value, index, array) {
						return value.available;
					});
					ws.send('deviceList');
					var deviceNames = [];
					for (var i in devices) {
						deviceNames[i] = devices[i].name;
					}
					ws.send(JSON.stringify(deviceNames));
				});
		} else if (message.split(' ')[0] == 'selectDevice') {
			if (devices[ws.selectedDevice]) {
				devices[ws.selectedDevice].stop();
				devices[ws.selectedDevice].ws = null;
			}
			ws.selectedDevice = message.split(' ')[1];
			devices[ws.selectedDevice].ws = ws;
			devices[ws.selectedDevice].initiate();
		} else if (message.startsWith("message:")) {
			devices[ws.selectedDevice].sendUp(message.substr("message:".length));
		}
		console.log('recieved:', message);
	});
	ws.on('error', function close(ws) {
		try {
			breakRefreshing = true;
			devices[ws.selectedDevice].stop();
			devices[ws.selectedDevice].ws = null;

		} catch (error) {
		}
		console.log('connection closed');
	})
	ws.on('close', function close(ws) {
		try {
			breakRefreshing = true;
			devices[ws.selectedDevice].stop();
			devices[ws.selectedDevice].ws = null;

		} catch (error) {
		}
		console.log('connection closed');
	})
	/*console.log("new connection");
	const bin=new Int16Array(5);
	for(var i=0;i<bin.length;i++){
	  bin[i]=i*3;
	}
	ws.send('fd');
	ws.send(bin);*/
});
// head: 0:head-ID  1-end:data types
class Device {
	constructor(name, ws = new WebSocket('')) {
		this.name = name;
		this.ws = ws;
		this.available = true;
		this.logging = false;
		this.loggingFileStream = fs.createWriteStream('log.txt');
	}
	send(data) {
		if (this.logging) {
			this.loggingFileStream.write(data);
			this.loggingFileStream.write('\n');
		}
		if (this.ws.bufferedAmount < 200) {
			this.ws.send(data);
		} else {
			console.log('too much data to send: ' + this.ws.bufferedAmount);
		}
	}
	sendUp(data) { }
	equals() {
		return false;
	}
	initiate() { }
	stop() { }
}
class DemoDevice extends Device {
	constructor(ws = new WebSocket('')) {
		super('Demo', ws);
		this.pitch = 10;
		this.interval = setInterval(() => { }, 1000000);
		clearInterval(this.interval);
		this.finished = true;
	}
	initiate() {
		this.ws.onclose = this.stop.bind(this);
		this.sendHead();
		this.interval = setInterval(() => {
			this.sendData();
			this.pitch += 0.01;
		}, 10);
	}
	stop() {
		clearInterval(this.interval);
	}
	sendHead() {
		this.send('headDefinition');
		var head = new Uint8Array(2);
		head[0] = 0;
		head[1] = 0;
		this.send(head);
	}
	sendData() {
		if (!this.finished) {
			console.log('TOO FAST');
			return;
		}
		this.finished = false;
		//console.log('new demo data buffer: ' + Date.now());
		this.send('fd');
		var head = new Uint8Array(1);
		head[0] = 0;
		var body = new Float32Array(1);
		body[0] = this.pitch;
		var buf = Buffer.alloc(head.byteLength + body.byteLength);
		var view = new Uint8Array(head.buffer);
		for (var i = 0; i < view.byteLength; i++) {
			buf[i] = view[i];
		}
		var offset = view.byteLength;
		view = new Uint8Array(body.buffer);
		for (var i = 0; i < view.byteLength; i++) {
			buf[i + offset] = view[i];
		}

		// this.ws.send(buf);
		this.send(buf);
		this.finished = true;
	}
}
class USBDevice extends Device {
	constructor(serialPort = '') {
		super(serialPort, null);
		this.logging = false;
		this.serialPort = new SerialPort(serialPort, { baudRate: 9600, autoOpen: true, lock: false });
		this.dataBuffer = new Uint8Array(0);
		this.currentByteNum = 0;
		this.lastByteStart = false;
		this.breakRefreshing = false;
		this.serialPort.on('open', function (data) {
			this.available = true;
			console.log('port opened ' + this.serialPort.path);
		}.bind(this));
		this.serialPort.on('data', function (data) { });
		this.serialPort.on('close', function (data) {
			/*devices = devices.filter(function (value, index, arr) {
			  if (value.serialPort && value.serialPort == this.serialPort) {
				return false;
			  }
			  return true;
	  
			})*/
			console.log('port close: ' + this.serialPort.path);
			this.available = false;
			devices = devices.filter(function (value, index, array) {
				return value.available;
			});
			breakRefreshing = false;
			this.tryOpening();
		}.bind(this));
	}
	tryOpening() {
		this.serialPort.open(function (error) {
			if (error && !breakRefreshing) {
				console.log('error opening port');
				setTimeout(this.tryOpening.bind(this), 1000);
			}
		}.bind(this));
	}
	sendUp(data) {
		this.serialPort.write(data, (e, b) => {
			if (e) {
				console.log("Error:" + e);
			}
		});
	}
	initiate() {
		this.sendHead();
		this.serialPort.on('data', function (data) {
			//console.log(data);
			var newDataBuffer = new Uint8Array(this.currentByteNum + data.length);
			for (var i = 0; i < this.currentByteNum; i++) {
				newDataBuffer[i] = this.dataBuffer[i];
			}
			for (const i of data) {
				var currentByte = i;
				// var cont = false;
				if (this.lastByteStart) {
					switch (i) {
						case 0:
							// new data package beginning
							this.currentByteNum = 0;
							// this.dataBuffer = new Uint8Array(0);
							// cont = true;
							break;
						case 1:
							// data package finished
							var cuttedBuffer = new Uint8Array(this.currentByteNum);
							for (const j in newDataBuffer) {
								cuttedBuffer[j] = newDataBuffer[j];
							}
							this.send('fd');
							this.send(cuttedBuffer);
							this.currentByteNum = 0;
							// cont = true;
							break;
						case 2:
							// normal data byte
							currentByte = 255;
							newDataBuffer[this.currentByteNum] = currentByte;
							this.currentByteNum++;
							break;
					}
					this.lastByteStart = false;
					continue;
				}
				if (i == 255) {
					this.lastByteStart = true;
				} else {
					newDataBuffer[this.currentByteNum] = i;
					this.currentByteNum++;
				}
			}
			this.dataBuffer = newDataBuffer;
		}.bind(this));
	}
	equals(dev) {
		return dev.path == this.serialPort.path;
	}
	sendHead() {
		this.send('headDefinition');
		var head = new Uint8Array(6);
		head[0] = 2;  // head number

		head[1] = 0;
		head[2] = 1;
		head[3] = 2;
		head[4] = 3;
		head[5] = 4;
		this.send(head);

		this.send('headDefinition');
		head = new Uint8Array(4);
		head[0] = 3;  // head number

		head[1] = 5;
		head[2] = 6;
		head[3] = 7;
		this.send(head);


		this.send('headDefinition');
		head = new Uint8Array(2);
		head[0] = 4;  // head number

		head[1] = 8;
		this.send(head);

		this.send('headDefinition');
		head = new Uint8Array(2);
		head[0] = 5;  // head number

		head[1] = 9;
		this.send(head);
	}
	stop() {
		if (this.serialPort.isOpen) {
			this.serialPort.close();
			this.serialPort.on("data", (d) => { });
		}
	}
}
function comNameKnown(comName = '') {
	for (var i in devices) {
		if (devices[i].serialPort && devices[i].serialPort.path == comName) {
			return true;
		}
	}
	return false;
}
