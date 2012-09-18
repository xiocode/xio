/**
 * Created with PyCharm.
 * User: xio
 * Date: 12-8-10
 * Time: 上午9:18
 * To change this template use File | Settings | File Templates.
 */

function route(handle, pathname, response, request) {
    console.log("About to route a request for " + pathname);
    if (typeof handle[pathname] === 'function') {
        handle[pathname](response, request);
    } else {
        console.log("No request handler found for " + pathname);
        response.writeHead(404, {"Content-Type": "text/html"});
        response.write("404 Not found");
        response.end();
    }
}

exports.route = route;