var server = require("./server");
var router = require("./router");
var requestHandlers = require("./requestHandlers");

var handle = {}
handle["/encrypt"] = requestHandlers.rsa_encrypt;

server.start(router.route, handle);