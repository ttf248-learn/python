# 导入必要的库
import argparse
import logging
import multiprocessing
import os

from PIL import Image


# 定义一个函数，将图片转换成黑白，维持透明背景，保存图片，并返回文件体积
def convert_and_save(image_file):
    # 打开图片
    try:
        image = Image.open(image_file)
    except Exception as e:
        logging.error(f"Failed to open {image_file}: {e}")
        return None, None
    # 获取图片的模式，如果是 RGBA 模式，说明有透明背景
    mode = image.mode
    if mode == "RGBA":
        # 创建一个和图片大小一致的白色背景图片
        background = Image.new("RGB", image.size, (255, 255, 255))
        # 将原图片粘贴到白色背景上，忽略透明像素
        background.paste(image, mask=image.split()[3])
        # 将合成的图片转换成灰度模式
        gray_image = background.convert("L")
        # 将灰度图片再转换成 RGBA 模式，以便保留透明背景
        final_image = gray_image.convert("RGBA")
    else:
        # 如果不是 RGBA 模式，直接将图片转换成灰度模式
        final_image = image.convert("L")
    # 获取原图片的文件名和扩展名
    file_name, file_ext = os.path.splitext(image_file)
    # 定义新图片的文件名，添加 _bw 后缀表示黑白
    new_file_name = file_name + "_bw" + file_ext
    # 保存新图片，并优化质量，减少文件体积
    try:
        final_image.save(new_file_name, optimize=True)
    except Exception as e:
        logging.error(f"Failed to save {new_file_name}: {e}")
        return None, None
    # 获取原图片和新图片的文件体积，并返回
    old_size = os.path.getsize(image_file)
    new_size = os.path.getsize(new_file_name)
    return file_name, old_size, new_size

# 定义一个函数，解析命令行参数，并返回文件夹路径和扩展名列表
def parse_args():
    # 创建一个解析器对象
    parser = argparse.ArgumentParser(description="Convert images to black and white and optimize quality.")
    # 添加一个必选的位置参数，表示文件夹路径
    parser.add_argument("folder_path", help="The path of the folder that contains the images.")
    # 添加一个可选的参数，表示扩展名列表，默认为 png, jpg, jpeg 和 gif
    parser.add_argument("-e", "--extensions", nargs="+", default=[".png", ".jpg", ".jpeg", ".gif"], help="The extensions of the image files.")
    # 解析命令行参数，并返回结果对象
    args = parser.parse_args()
    return args.folder_path, args.extensions

# 定义一个函数，打印优化前后的文件体积大小对比
def print_result(result):
    # 如果结果不为空，说明转换和保存成功
    if result:
        # 解包结果为文件名和文件体积元组
        if len(result) == 3:
            file, old_size, new_size = result
            # 在控制台展示优化前后的文件体积大小对比
            logging.info(f"{file}: {old_size} bytes -> {new_size} bytes")
        else:
            logging.info(f"{result}")

# 配置日志记录器，将日志输出到控制台和文件中，设置日志等级为 INFO
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s",
                    handlers=[logging.StreamHandler(),
                              logging.FileHandler("log.txt")])

# 调用函数，获取文件夹路径和扩展名列表
folder_path, extensions = parse_args()

if __name__ == "__main__":
    # Windows 需要这个函数的原因是 Windows 缺乏 fork() 函数（这不完全正确）。
    # 因此，在 Windows 上，fork() 是通过创建一个新的进程来模拟的，这个新的进程中运行的代码，在 Linux 上是在子进程中运行的。
    # 由于这些代码要在技术上无关的进程中运行，所以它必须在运行之前被传递到那里。
    # 传递的方式是先将它们序列化，然后通过管道从原始进程发送到新的进程。
    # 另外，这个新的进程被通知它必须运行通过管道传递的代码，通过向它传递 --multiprocessing-fork 命令行参数。
    # 如果你看一下 freeze_support() 函数的实现，它的任务是检查它运行在哪个进程中，是否应该运行通过管道传递的代码
    multiprocessing.freeze_support()

    # 创建一个进程池，根据电脑的核心数自动分配进程
    pool = multiprocessing.Pool()
    # 创建一个空列表，用于存放异步任务的结果对象
    results = []
    # 遍历文件夹中的所有文件
    for file in os.listdir(folder_path):
        # 拼接完整的文件路径
        file_path = os.path.join(folder_path, file)
        # 判断是否是图片文件，根据扩展名判断，可以根据需要修改扩展名列表
        if any(file_path.endswith(ext) for ext in extensions):
            # 调用函数，转换并保存图片，并获取文件体积，使用异步方式，不阻塞主进程
            result = pool.apply_async(convert_and_save, args=(file_path,), callback=print_result)
            # 将结果对象添加到列表中
            results.append((file, result))
    # 关闭进程池，不再接受新的任务
    pool.close()
    # 等待所有的任务完成
    pool.join()