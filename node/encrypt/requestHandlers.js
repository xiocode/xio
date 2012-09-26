/**
 * Created with PyCharm.
 * User: xio
 * Date: 12-8-10
 * Time: 上午9:23
 * To change this template use File | Settings | File Templates.
 */

var rsa = require('./rsa.js')
var url = require('url')

function rsa_encrypt(response, request) {
    password = url.parse(request.url, true).query.password
    var rsakey = new rsa.RSAKey()
    pubkey = rsakey.setPublic('EB2A38568661887FA180BDDB5CABD5F21C7BFD59C090CB2D245A87AC253062882729293E5506350508E7F9AA3BB77F4333231490F915F6D63C55FE2F08A49B353F444AD3993CACC02DB784ABBB8E42A9B1BBFFFB38BE18D78E87A0E41B9B8F73A928EE0CCEE1F6739884B9777E4FE9E88A1BBE495927AC4A799B3181D6442443','10001')
    rsa_password = rsakey.encrypt(password)
    console.log("Request handler 'rsa_encrypt' was called.");
    response.writeHead(200, {"Content-Type": "text/html"});
    response.write(rsa_password);
    response.end();
}

exports.rsa_encrypt = rsa_encrypt;