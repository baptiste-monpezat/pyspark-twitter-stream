const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 9011,host:"app_web_server_1"});

console.log("Test webserver")
wss.on('connection', function connection(ws) {
  console.log("connection ok")
  ws.on('message', function incoming(message) {
    wss.clients.forEach((client) => {
      if(client.readyState === WebSocket.OPEN){
          console.log(message)
      }
      if (client !== ws && client.readyState === WebSocket.OPEN) {
        console.log(message)
        client.send(message);
      }
    });
  });

});