import fs
c=fs.readFileSync('C:/workspace/customer-hub/index.html', 'uft8')
old = '  <button class="refresh-btn" onClick="loadData()">综쿡</button>'+
new = '  <button class="sync-btn" onClick="syncAndReload()">騨멤멙</button>'+
print('found:', old in content)
c2 = content.replace(old, new)
fs.writeFileSync('C:/workspace/customer-hub/index.html', c2, 'utf8-sig')
print('done, changed:', old not in c2)
