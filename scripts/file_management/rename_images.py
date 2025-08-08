import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Set
from loguru import logger
import re

class ImageRenamer:
    def __init__(self, source_folder: str, dry_run: bool = False, 
                 image_extensions: List[str] = None, start_number: int = 1):
        """
        初始化图片重命名器
        
        Args:
            source_folder: 源文件夹路径
            dry_run: 是否为试运行模式（不实际重命名文件）
            image_extensions: 图片文件扩展名列表
            start_number: 起始编号
        """
        self.source_folder = Path(source_folder).resolve()
        self.dry_run = dry_run
        self.start_number = start_number
        
        # 默认图片扩展名
        if image_extensions is None:
            self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', 
                                   '.tiff', '.tif', '.webp', '.ico', '.svg'}
        else:
            self.image_extensions = {ext.lower() for ext in image_extensions}
        
        self.stats = {
            'total_folders': 0,
            'total_images': 0,
            'renamed_images': 0,
            'skipped_images': 0,
            'error_images': 0
        }
        
        self.setup_logging()
    
    def setup_logging(self, log_dir='log'):
        """设置日志配置"""
        # 日志库默认输出到终端，移除终端的日志，目前保留终端的日志
        # logger.remove()
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file = os.path.join(log_dir, 'rename_images_{time:YYYY-MM-DD}.log')
        
        # 添加日志记录器，按天滚动，并保留30天的日志
        # TODO：日志级别的控制，通过环境变量控制，容器启动脚本注入
        log_format = "{time:YYYY-MM-DD HH:mm:ss} - {level} - {name}:{function}:{line} - {message}"
        logger.add(log_file, rotation="00:00", retention="30 days", level="DEBUG", format=log_format)
    
    def validate_source_folder(self) -> bool:
        """验证源文件夹是否存在且可访问"""
        if not self.source_folder.exists():
            logger.error(f"错误：源文件夹不存在: {self.source_folder}")
            return False
        
        if not self.source_folder.is_dir():
            logger.error(f"错误：指定路径不是文件夹: {self.source_folder}")
            return False
        
        try:
            # 测试文件夹读取权限
            list(self.source_folder.iterdir())
        except PermissionError:
            logger.error(f"错误：没有权限访问文件夹: {self.source_folder}")
            return False
        except Exception as e:
            logger.error(f"错误：无法访问文件夹 {self.source_folder}: {e}")
            return False
        
        return True
    
    def is_image_file(self, file_path: Path) -> bool:
        """
        判断文件是否为图片文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否为图片文件
        """
        return file_path.suffix.lower() in self.image_extensions
    
    def is_already_numbered(self, filename: str) -> bool:
        """
        判断文件是否已经是数字命名格式
        
        Args:
            filename: 文件名（不含扩展名）
            
        Returns:
            是否已经是数字格式
        """
        # 匹配纯数字文件名（可能有前导零）
        return bool(re.match(r'^\d+$', filename))
    
    def calculate_padding(self, count: int) -> int:
        """
        根据文件数量计算需要的前导零位数
        
        Args:
            count: 文件数量
            
        Returns:
            需要的总位数
        """
        if count == 0:
            return 1
        
        # 计算最大数字需要的位数
        max_number = self.start_number + count - 1
        return len(str(max_number))
    
    def generate_new_name(self, number: int, padding: int, extension: str) -> str:
        """
        生成新的文件名
        
        Args:
            number: 序号
            padding: 总位数
            extension: 文件扩展名
            
        Returns:
            新文件名
        """
        return f"{str(number).zfill(padding)}{extension}"
    
    def natural_sort_key(self, file_path: Path) -> tuple:
        """
        自然排序键函数，用于正确排序包含数字的文件名
        
        Args:
            file_path: 文件路径
            
        Returns:
            排序键元组
        """
        filename = file_path.stem.lower()
        
        # 将文件名分解为文本和数字部分
        parts = re.split(r'(\d+)', filename)
        
        # 将数字部分转换为整数，文本部分保持字符串
        key_parts = []
        for part in parts:
            if part.isdigit():
                key_parts.append(int(part))
            else:
                key_parts.append(part)
        
        return tuple(key_parts)
    
    def get_image_files_in_folder(self, folder_path: Path) -> List[Path]:
        """
        获取文件夹中的所有图片文件，并按自然顺序排序
        
        Args:
            folder_path: 文件夹路径
            
        Returns:
            图片文件路径列表（已排序）
        """
        try:
            image_files = []
            for file_path in folder_path.iterdir():
                if file_path.is_file() and self.is_image_file(file_path):
                    image_files.append(file_path)
            
            # 使用自然排序
            image_files.sort(key=self.natural_sort_key)
            
            # 调试输出排序结果
            logger.debug(f"排序后的文件列表:")
            for i, file_path in enumerate(image_files):
                logger.debug(f"  {i+1}: {file_path.name}")
            
            return image_files
            
        except Exception as e:
            logger.error(f"无法读取文件夹 {folder_path}: {e}")
            return []
    
    def rename_images_in_folder(self, folder_path: Path) -> Dict[str, int]:
        """
        重命名单个文件夹中的图片文件
        
        Args:
            folder_path: 文件夹路径
            
        Returns:
            操作统计信息
        """
        folder_stats = {
            'renamed': 0,
            'skipped': 0,
            'errors': 0
        }
        
        # 获取所有图片文件（已排序）
        image_files = self.get_image_files_in_folder(folder_path)
        
        if not image_files:
            logger.debug(f"文件夹中没有图片文件: {folder_path}")
            return folder_stats
        
        # 计算需要的位数
        padding = self.calculate_padding(len(image_files))
        
        logger.info(f"\n处理文件夹: {folder_path}")
        logger.info(f"找到 {len(image_files)} 个图片文件，使用 {padding} 位数字编号")
        
        # 显示原始文件排序
        logger.info("原始文件排序:")
        for i, file_path in enumerate(image_files[:10]):  # 只显示前10个
            logger.info(f"  {i+1}: {file_path.name}")
        if len(image_files) > 10:
            logger.info(f"  ... 还有 {len(image_files) - 10} 个文件")
        
        # 创建重命名映射
        rename_mapping = []
        current_number = self.start_number
        
        for file_path in image_files:
            old_name = file_path.name
            old_stem = file_path.stem
            extension = file_path.suffix
            
            # 检查是否已经是正确的数字格式
            expected_name = self.generate_new_name(current_number, padding, extension)
            
            if old_name == expected_name:
                logger.debug(f"跳过文件（已是正确格式）: {old_name}")
                folder_stats['skipped'] += 1
            else:
                new_name = expected_name
                rename_mapping.append((file_path, new_name))
            
            current_number += 1
        
        # 执行重命名操作
        for old_path, new_name in rename_mapping:
            new_path = old_path.parent / new_name
            
            try:
                # 检查目标文件是否已存在
                if new_path.exists() and new_path != old_path:
                    # 如果目标文件存在且不是同一个文件，需要特殊处理
                    temp_name = f"temp_{new_name}"
                    temp_path = old_path.parent / temp_name
                    
                    if not self.dry_run:
                        # 先移动到临时名称，避免冲突
                        old_path.rename(temp_path)
                        temp_path.rename(new_path)
                    
                    logger.info(f"重命名: {old_path.name} -> {new_name} (通过临时文件)")
                else:
                    if not self.dry_run:
                        old_path.rename(new_path)
                    
                    action = "[试运行]" if self.dry_run else ""
                    logger.info(f"{action} 重命名: {old_path.name} -> {new_name}")
                
                folder_stats['renamed'] += 1
                
            except Exception as e:
                logger.error(f"重命名失败 {old_path.name} -> {new_name}: {e}")
                folder_stats['errors'] += 1
        
        return folder_stats
    
    def process_folder_recursive(self, folder_path: Path):
        """
        递归处理文件夹
        
        Args:
            folder_path: 文件夹路径
        """
        try:
            self.stats['total_folders'] += 1
            
            # 处理当前文件夹中的图片
            folder_stats = self.rename_images_in_folder(folder_path)
            
            # 更新总体统计
            self.stats['renamed_images'] += folder_stats['renamed']
            self.stats['skipped_images'] += folder_stats['skipped']
            self.stats['error_images'] += folder_stats['errors']
            
            # 递归处理子文件夹
            try:
                for item in folder_path.iterdir():
                    if item.is_dir():
                        self.process_folder_recursive(item)
            except PermissionError:
                logger.warning(f"没有权限访问子文件夹: {folder_path}")
            except Exception as e:
                logger.error(f"处理子文件夹时出错 {folder_path}: {e}")
        
        except Exception as e:
            logger.error(f"处理文件夹失败 {folder_path}: {e}")
    
    def count_total_images(self, folder_path: Path) -> int:
        """
        统计总图片数量（用于预览）
        
        Args:
            folder_path: 文件夹路径
            
        Returns:
            图片总数
        """
        total = 0
        try:
            for item in folder_path.iterdir():
                if item.is_file() and self.is_image_file(item):
                    total += 1
                elif item.is_dir():
                    total += self.count_total_images(item)
        except (PermissionError, OSError):
            pass
        
        return total
    
    def print_summary(self):
        """打印重命名摘要"""
        logger.info("\n" + "="*50)
        logger.info("重命名摘要:")
        logger.info(f"源文件夹: {self.source_folder}")
        logger.info(f"处理文件夹数: {self.stats['total_folders']}")
        logger.info(f"重命名图片数: {self.stats['renamed_images']}")
        logger.info(f"跳过图片数: {self.stats['skipped_images']}")
        logger.info(f"错误图片数: {self.stats['error_images']}")
        logger.info(f"支持的图片格式: {', '.join(sorted(self.image_extensions))}")
        
        if self.dry_run:
            logger.info("\n*** 这是试运行结果，没有实际重命名文件 ***")
        
        if self.stats['error_images'] > 0:
            logger.warning(f"\n注意: 有 {self.stats['error_images']} 个文件处理失败")
    
    def rename_images(self):
        """执行图片重命名"""
        if not self.validate_source_folder():
            return False
        
        try:
            logger.info(f"开始处理文件夹: {self.source_folder}")
            logger.info(f"起始编号: {self.start_number}")
            logger.info(f"排序方式: 自然数字排序")
            
            if self.dry_run:
                logger.info("*** 试运行模式 - 不会实际重命名文件 ***")
                # 预统计图片数量
                total_images = self.count_total_images(self.source_folder)
                logger.info(f"预计处理 {total_images} 个图片文件\n")
            
            # 开始递归处理
            self.process_folder_recursive(self.source_folder)
            
            self.print_summary()
            return True
            
        except KeyboardInterrupt:
            logger.info("\n用户中断操作")
            return False
        except Exception as e:
            logger.error(f"重命名过程中发生错误: {e}")
            return False

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="递归重命名文件夹中的图片文件为数字序号格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  基础用法:
    python rename_images.py "C:\\Photos"
    python rename_images.py /home/user/pictures
  
  试运行模式（不实际重命名文件）:
    python rename_images.py "D:\\Images" --dry-run
  
  自定义起始编号:
    python rename_images.py "C:\\temp" --start-number 100
  
  指定图片扩展名:
    python rename_images.py "C:\\temp" --extensions jpg png gif
  
  组合选项:
    python rename_images.py "C:\\temp" --dry-run --start-number 0 --verbose

重命名规则:
  - 每个文件夹中的图片独立编号
  - 编号位数根据文件夹中图片数量自动确定
  - 例如：1-9个文件用1位数，10-99个文件用2位数，100-999个文件用3位数
  - 文件按名称排序后依次编号

注意事项:
  - 脚本会递归处理所有子文件夹
  - 每个文件夹的图片独立编号，从起始数字开始
  - 建议先使用 --dry-run 选项预览操作结果
  - 支持的默认图片格式：jpg, jpeg, png, gif, bmp, tiff, tif, webp, ico, svg
        """
    )
    
    parser.add_argument(
        "folder_path",
        nargs='?',
        help="要处理的文件夹路径（如果不提供，将提示输入）"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="试运行模式，只显示将要执行的操作，不实际重命名文件"
    )
    
    parser.add_argument(
        "--start-number",
        type=int,
        default=1,
        help="起始编号（默认: 1）"
    )
    
    parser.add_argument(
        "--extensions",
        nargs="+",
        help="指定图片文件扩展名（默认：常见图片格式）"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细输出"
    )
    
    return parser.parse_args()

def get_folder_path_from_input() -> str:
    """从控制台输入获取文件夹路径"""
    print("图片重命名工具")
    print("="*30)
    
    while True:
        folder_path = input("请输入要处理的文件夹路径: ").strip()
        
        if not folder_path:
            print("路径不能为空，请重新输入。")
            continue
        
        # 去除引号
        folder_path = folder_path.strip('"\'')
        
        path = Path(folder_path)
        if not path.exists():
            print(f"路径不存在: {folder_path}")
            continue
        
        if not path.is_dir():
            print(f"指定路径不是文件夹: {folder_path}")
            continue
        
        return str(path.resolve())

def confirm_operation(folder_path: str, dry_run: bool) -> bool:
    """确认操作"""
    if dry_run:
        return True
    
    print(f"\n即将重命名文件夹中的所有图片文件: {folder_path}")
    print("此操作将递归处理所有子文件夹中的图片文件。")
    
    while True:
        response = input("确认继续？(y/n): ").strip().lower()
        if response in ['y', 'yes', '是']:
            return True
        elif response in ['n', 'no', '否']:
            return False
        else:
            print("请输入 y/yes/是 或 n/no/否")

def main():
    """主函数"""
    try:
        args = parse_args()
        
        # 设置日志级别
        if args.verbose:
            logger.remove()
            logger.add(sys.stderr, level="DEBUG")
        
        # 获取文件夹路径
        if args.folder_path:
            folder_path = args.folder_path
        else:
            folder_path = get_folder_path_from_input()
        
        # 确认操作
        if not confirm_operation(folder_path, args.dry_run):
            print("操作已取消。")
            sys.exit(0)
        
        # 创建重命名器实例
        renamer = ImageRenamer(
            source_folder=folder_path,
            dry_run=args.dry_run,
            image_extensions=args.extensions,
            start_number=args.start_number
        )
        
        # 执行重命名
        success = renamer.rename_images()
        
        if success:
            print("\n重命名完成！")
            sys.exit(0)
        else:
            print("\n重命名失败！")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"程序运行错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
