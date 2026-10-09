import fs
data= open('C:/workspace/customer-hub/index.html',"rb").read()
old = b'  <button class="refresh-btn" onClick="loadData()"> 刷新</button>
')
new = b'  <button class="sync-btn" onClick="syncAndReload()"> 同步BOSS </button>
')
print('found:', old in data)
data2= data.replace(old, new)
open('C:/workspace/customer-hub/index.html',"wb").write(data2)
print('done:', old not in data2)
