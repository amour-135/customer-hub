content = open('C:/workspace/customer-hub/index.html', 'r', encoding='utf-8').read()
content = content.replace(
    \"if (type === 'feishu') return 'https://applink.feishu.cn/client/imconversation/?openChatId=' + groupId;\",
    \"if (type === 'feishu') return 'feishu://imconversation?openChatId=' + groupId;\"
)
open('C:/workspace/customer-hub/index.html', 'w', encoding='utf-8').write(content)
print('done')