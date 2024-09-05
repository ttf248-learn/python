import os
import cairosvg
from defusedxml.common import EntitiesForbidden

def convert_svg_to_png(input_folder, output_folder):
    # 创建输出文件夹，如果不存在的话
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        if filename.endswith(".svg"):
            svg_path = os.path.join(input_folder, filename)
            png_filename = filename.replace(".svg", ".png")
            png_path = os.path.join(output_folder, png_filename)
            
            try:
                # 转换 SVG 为 PNG
                cairosvg.svg2png(url=svg_path, write_to=png_path)
                # print(f"Converted {svg_path} to {png_path}")
            except EntitiesForbidden as e:
                print(f"Skipping {svg_path}: {e}")
            except Exception as e:
                print(f"Failed to convert {svg_path}: {e}")

# 指定输入文件夹和输出文件夹
input_folder = r"/home/core/easytrade/logo"
output_folder = r"/home/core/easytrade/logo_png"

# 执行转换
convert_svg_to_png(input_folder, output_folder)
