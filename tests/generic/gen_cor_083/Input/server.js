const commander = require('commander');
const http = require('http')

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('-p, --port <value>', 'Http port to listen on')
  .parse(process.argv);

const options = commander.opts();
console.log('PORT:', `${options.port}`);

const server = http.createServer(
  function(request, response) {
    if (request.method == 'POST') {
      var body = ''
      request.on('data', function(data) {
        body += data
      })
      request.on('end', function() {
        console.log('Body: ' + body)
        response.writeHead(200, {'Content-Type': 'text/html'})
        response.end('post received')
      })
    }
  }
)

const port = options.port
const host = '127.0.0.1'
server.listen(port, host)
console.log(`Listening at http://${host}:${port}`)