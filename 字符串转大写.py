# 函数 输入字符串转大写，保存到粘贴板
# 作者：李宇
# 日期：2019-12-31
# 语言：Python 3.7.4
# 依赖：pyperclip
# 说明：将输入字符串转大写，保存到粘贴板
# 用法：将需要转换的字符串复制到剪贴板，运行程序，即可将转换后的字符串保存到剪贴板

import pyperclip
import time

text = ''

while True:
    if text != pyperclip.paste() and pyperclip.paste().find('const') == -1:
        text = pyperclip.paste()
        pyperclip.copy('const char k' + text.upper() + '[] = "' + text + '";')
        print('转换成功', text, '->', pyperclip.paste())

    # 休眠1秒
    time.sleep(1)