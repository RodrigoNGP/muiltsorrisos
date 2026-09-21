/**
 * Servidor local: arquivos estáticos + rotas /api (mesmo formato da Vercel).
 * Uso:  node server.js   (lê variáveis do arquivo .env, se existir)
 */
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const PORT = Number(process.env.PORT) || 5501;

// Carrega .env simples (CHAVE=valor)
const envFile = path.join(ROOT, '.env');
if (fs.existsSync(envFile)) {
  fs.readFileSync(envFile, 'utf8').split(/\r?\n/).forEach(function (line) {
    const m = line.match(/^\s*([\w.]+)\s*=\s*(.*)\s*$/);
    if (m && !(m[1] in process.env)) process.env[m[1]] = m[2].replace(/^["']|["']$/g, '');
  });
}

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json', '.xml': 'application/xml', '.txt': 'text/plain; charset=utf-8',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.ico': 'image/x-icon',
};

http.createServer(async function (req, res) {
  const url = new URL(req.url, 'http://localhost');
  let pathname = decodeURIComponent(url.pathname);

  if (pathname.startsWith('/api/')) {
    const file = path.join(ROOT, 'api', path.basename(pathname) + '.js');
    if (!fs.existsSync(file)) { res.statusCode = 404; return res.end('Not found'); }
    try {
      return await require(file)(req, res);
    } catch (err) {
      console.error(err);
      res.statusCode = 500;
      return res.end('Erro interno');
    }
  }

  if (pathname.endsWith('/')) pathname += 'index.html';
  const filePath = path.join(ROOT, path.normalize(pathname));
  if (!filePath.startsWith(ROOT) || /[\\/](_src|api|\.env)/.test(filePath.slice(ROOT.length))) {
    res.statusCode = 403;
    return res.end('Forbidden');
  }
  fs.readFile(filePath, function (err, data) {
    if (err) { res.statusCode = 404; return res.end('Not found'); }
    res.setHeader('Content-Type', TYPES[path.extname(filePath).toLowerCase()] || 'application/octet-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.end(data);
  });
}).listen(PORT, function () {
  console.log('Landing Multisorrisos rodando em http://localhost:' + PORT);
});
