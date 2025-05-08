from paddleocr import PaddleOCR, draw_ocr
import os
import time
from PIL import Image

# 记录开始时间
start_time = time.time()

# Paddleocr目前支持的多语言语种可以通过修改lang参数进行切换
# 例如`ch`, `en`, `fr`, `german`, `korean`, `japan`
ocr = PaddleOCR(use_angle_cls=True, lang="ch")  # need to run only once to download and load model into memory

# 计算初始化耗时
init_time = time.time() - start_time
print(f"初始化耗时: {init_time:.2f}秒")

# 使用相对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))

img_path = os.path.join(project_root, 'assets', 'images', 'paddleocr.png')
if not os.path.exists(img_path):
    raise FileNotFoundError(f'图片文件不存在: {img_path}')

# 开始OCR识别
ocr_start_time = time.time()
result = ocr.ocr(img_path, cls=True)
for idx in range(len(result)):
    res = result[idx]
    for line in res:
        print(line)

# 计算OCR识别耗时
ocr_time = time.time() - ocr_start_time
print(f"OCR识别耗时: {ocr_time:.2f}秒")

# 显示结果
result = result[0]
image = Image.open(img_path).convert('RGB')
boxes = [line[0] for line in result]
txts = [line[1][0] for line in result]
scores = [line[1][1] for line in result]

# 开始保存图片
save_start_time = time.time()

font_path = os.path.join(project_root, 'assets', 'fonts', 'simfang.ttf')
im_show = draw_ocr(image, boxes, txts, scores, font_path=font_path)
im_show = Image.fromarray(im_show)

output_path = os.path.join(project_root, 'output', 'result.jpg')
im_show.save(output_path)

# 计算保存图片耗时
save_time = time.time() - save_start_time
print(f"保存图片耗时: {save_time:.2f}秒")

# 计算总耗时
total_time = time.time() - start_time
print(f"总耗时: {total_time:.2f}秒")
