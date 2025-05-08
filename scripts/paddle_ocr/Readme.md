## 部署安装

[https://paddlepaddle.github.io/PaddleOCR/latest/quick_start.html#__tabbed_1_2](https://paddlepaddle.github.io/PaddleOCR/latest/quick_start.html#__tabbed_1_2)

paddlepaddle 和 paddleocr 版本存在依赖关系

```shell
 python -m pip install paddlepaddle-gpu==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/
 pip install paddleocr
```

## 模型存储位置

可以通过设置环境变量 PADDLE_OCR_BASE_DIR 来自定义 OCR 模型的存储位置。如果未设置此变量，模型将下载到以下默认位置：

* 在Linux/macOS上路径为：${HOME}/.paddleocr
* 在Windows上路径为：C:\Users\{username}\.paddleocr
