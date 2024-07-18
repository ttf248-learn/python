import os
import subprocess

def convert_svg_to_png(input_folder, output_folder):
    # 创建输出文件夹，如果不存在的话
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 获取输入文件夹中的所有 SVG 文件
    svg_files = [f for f in os.listdir(input_folder) if f.endswith(".svg")]
    total_files = len(svg_files)
    failed_files = []

    # 遍历并转换每个 SVG 文件
    for index, filename in enumerate(svg_files):
        svg_path = os.path.join(input_folder, filename)
        png_filename = filename.replace(".svg", ".png")
        png_path = os.path.join(output_folder, png_filename)
        
        try:
            # 使用 inkscape 将 SVG 转换为 PNG
            subprocess.run(['inkscape', svg_path, '--export-filename', png_path], check=True)
            print(f"Converted {svg_path} to {png_path} ({index + 1}/{total_files})")
        except subprocess.CalledProcessError as e:
            print(f"Failed to convert {svg_path}: {e}")
            failed_files.append(svg_path)
        except Exception as e:
            print(f"An error occurred: {e}")
            failed_files.append(svg_path)

    print("Conversion finished")
    if failed_files:
        print("Failed to convert the following files:")
        for file in failed_files:
            print(file)
    else:
        print("All files converted successfully")

# 指定输入文件夹和输出文件夹
input_folder = r"/home/core/easytrade/logo"
output_folder = r"/home/core/easytrade/logo_png"

# 执行转换
convert_svg_to_png(input_folder, output_folder)
