

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