# import difflib

# local_str = '維天運通 LOGORY'
# network_str = '合肥維天運通信息科技股份有限公司'
# loc = network_str.find(local_str[0])
# print('完整字符比较', difflib.SequenceMatcher(None, local_str, network_str).ratio())
# print('首位字符相似度', difflib.SequenceMatcher(None, network_str[:len(local_str)].lower(), local_str.lower()).ratio())
# print('定位串字符相似度', difflib.SequenceMatcher(None, network_str[loc:len(local_str)+loc].lower(), local_str.lower()).ratio())

# # 
# print('3D MEDICINES-B'.lower())
# print(difflib.SequenceMatcher(None, '3D Medicines Inc.'.lower(), '3D MEDICINES-B'.lower()).quick_ratio())
# print(difflib.SequenceMatcher(None, '美皓醫療'.lower(), '美皓集團'.lower()).quick_ratio())
# print(difflib.SequenceMatcher(None, '國際控股', '濠暻科技').quick_ratio())
# print(difflib.SequenceMatcher(None, '陽光保險', '陽光保險').quick_ratio())

# # create https server
# # import http.server
# # import ssl

# # httpd = http.server.HTTPServer(('localhost', 4443), http.server.SimpleHTTPRequestHandler)
# # httpd.socket = ssl.wrap_socket(httpd.socket, certfile='server.pem', server_side=True)
# # httpd.serve_forever()

# s1 = "維天運通 LOGORY"
# s2 = "合肥維天運通信息科技股份有限公司"
# similarity = difflib.SequenceMatcher(None, s1, s2).ratio()
# print(similarity)

# print(difflib.__version__)

import jieba
import numpy as np
from scipy.spatial.distance import cosine

# 定义两个字符串
str1 = "維天運通 LOGORY"
str2 = "合肥維天運通信息科技股份有限公司"

# 统一处理字符串，英文转换为小写
str1 = str1.lower()
str2 = str2.lower()

# 找到第二个字符串中第一个字符的位置
index = str2.find(str1[0])

# 如果找到了，截取第二个字符串
if index != -1:
    str2 = str2[index:index+len(str1)]

# 使用 jieba 库进行分词
words1 = list(jieba.cut(str1))
words2 = list(jieba.cut(str2))

# 计算两个字符串的词向量（以词频作为权重）
vector1 = np.zeros(len(words1))
vector2 = np.zeros(len(words1))

for i, word in enumerate(words1):
    vector1[i] += 1 # 统计第一个字符串中每个词出现的次数
    if word in words2:
        vector2[i] += 1 # 统计第二个字符串中每个词出现的次数

# 计算两个字符串的相似度（以余弦距离作为指标）
similarity = 1 - cosine(vector1, vector2)

print("两个字符串的相似度是：", similarity)

bstr = 'xxx'

print(bstr)