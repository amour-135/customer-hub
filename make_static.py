import json

with open('C:/workspace/customer-hub/customers_export.json', 'r', encoding='utf-8') as f:
    data = f.read()

with open('C:/workspace/customer-hub/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace fetch call with embedded data
html2 = html.replace("fetch('/api/customers')", 'const customers = ' + data + ';')

with open('C:/workspace/customer-hub/index_static.html', 'w', encoding='utf-8') as f:
    f.write(html2)

print('done, size:', len(html2))