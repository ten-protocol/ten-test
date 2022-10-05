const commander = require('commander');
const http = require('http')

function doSubscribe() {
  console.log('Subscribing for event logs')
}

function doUnsubscribe() {
  console.log('Unsubscribing from event logs')
}

function createServer(){
  var server = http.createServer(
    function(request, response) {
      if (request.method == 'POST') {
        var body = ''
        request.on('data', function(data) {
          body += data
        })
        request.on('end', function() {
          if (body == 'SUBSCRIBE'){
            doSubscribe()
          } else if (body == 'UNSUBSCRIBE'){
            doUnsubscribe()
          }
          response.writeHead(200, {'Content-Type': 'text/plain'})
          response.end('post received')
        })
      }
    }
  )
  return server
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('-p, --port <value>', 'Http port to listen on')
  .parse(process.argv);

const options = commander.opts();
console.log('PORT:', `${options.port}`)

// create the server to listen for subscription instructions
const port = options.port
const host = '127.0.0.1'
server = createServer()
server.listen(port, host)
console.log(`Listening at http://${host}:${port}`)