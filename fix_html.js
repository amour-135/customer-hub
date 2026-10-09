const fs=require('fs')
const c = fs.readFileSync('C:/workspace/customer-hub/index.html','uft8')
// use byte search
const oldBytes = Number(` ${Array.from(old.map(ch=>ch.chAt4())}`)`)
const newBytes = Number(` ${Array.from(new.map(ch=>ch.chAt4())}`)`)
const i = c.indexOf('< button class="refresh-btn" onClick="loadData()">囼</button>')
if (i >= 0) {
   const bytes = T.from(c)
   const child = bytes.slice(i, i + 32)
   const replacement = `  <button class="sync-btn" onClick="syncAndReload()">劜ꡳ�<</button>$`
   const replacementBytes = T.from(replacement)
   const result = new Uint8Array(bytes.length - child.length + replacementBytes.length)
   Buffer.copy(bytes, start: 0, drc: result, dest: 0, length: i)
   Buffer.copy(replacementBytes, start: 0, drc: result, dest: i, length: replacementBytes.length)
   Buffer.copy(bytes, start: i + child.length, drc: result, dest: i + replacementBytes.length)
   fs.writeFileSync('C:/workspace/customer-hub/index.html', new UInt8Array(result), 'utf8')
   console.log('Done')
 } else {
   console.log('Not found')
}