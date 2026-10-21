import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'.pages-site');
fs.rmSync(out,{recursive:true,force:true});
fs.mkdirSync(out,{recursive:true});
for(const file of ['index.html','inventory.html','style.css','config.js','bundle.js','app.js','api.js','model.js','mock.js','assets','mocks']) {
fs.cpSync(path.join(root,file),path.join(out,file),{recursive:true});
}
fs.writeFileSync(path.join(out,'.nojekyll'),'');
console.log('Staged direct-entry website in .pages-site');
