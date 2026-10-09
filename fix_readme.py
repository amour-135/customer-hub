content = open('C:/workspace/customer-hub/README.md', 'r', encoding='utf-8-sig').read()
content = content.replace('当前用户：沐宸（李林威）', '当前用户：（已登录）')
open('C:/workspace/customer-hub/README.md', 'w', encoding='utf-8-sig').write(content)
print('done')