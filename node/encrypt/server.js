/**
 * Created with PyCharm.
 * User: xio
 * Date: 12-8-10
 * Time: 上午9:17
 * To change this template use File | Settings | File Templates.
 */

var http = require("http");
var url = require("url");

function start(route, handle) {
    function onRequest(request, response) {
        var pathname = url.parse(request.url).pathname;
        console.log("Request for " + pathname + " received.");
        route(handle, pathname, response, request);
    }

    http.createServer(onRequest).listen(8888);
    console.log("Server has started.");
}

exports.start = start;