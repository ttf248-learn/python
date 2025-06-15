import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import logging

class FileOrganizerByYear:
    def __init__(self, source_folder: str, dry_run: bool = False, use_creation_date: bool = False):
        """
        初始化文件整理器
        
        Args:
            source_folder: 源文件夹路径
            dry_run: 是否为试运行模式（不实际移动文件）
            use_creation_date: 是否使用文件创建时间而非修改时间
        """
        self.source_folder = Path(source_folder).resolve()
        self.dry_run = dry_run
        self.use_creation_date = use_creation_date
        self.stats = {
            'total_files': 0,
            'moved_files': 0,
            'skipped_files': 0,
            'error_files': 0,
            'created_folders': 0
        }
        self.year_folders = {}
        self.setup_logging()
    
    def setup_logging(self):
        """设置日志记录"""
        self.logger = logging.getLogger('FileOrganizer')
        self.logger.setLevel(logging.INFO)
        
        # 控制台输出
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def validate_source_folder(self) -> bool:
        """验证源文件夹是否存在且可访问"""
        if not self.source_folder.exists():
            self.logger.error(f"错误：源文件夹不存在: {self.source_folder}")
            return False
        
        if not self.source_folder.is_dir():
            self.logger.error(f"错误：指定路径不是文件夹: {self.source_folder}")
            return False
        
        try:
            # 测试文件夹读取权限
            list(self.source_folder.iterdir())
        except PermissionError:
            self.logger.error(f"错误：没有权限访问文件夹: {self.source_folder}")
            return False
        except Exception as e:
            self.logger.error(f"错误：无法访问文件夹 {self.source_folder}: {e}")
            return False
        
        return True
    
    def get_file_year(self, file_path: Path) -> int:
        """
        获取文件的年份
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件的年份
        """
        try:
            if self.use_creation_date:
                # 使用创建时间
                timestamp = file_path.stat().st_ctime
            else:
                # 使用修改时间
                timestamp = file_path.stat().st_mtime
            
            return datetime.fromtimestamp(timestamp).year
        except Exception as e:
            self.logger.warning(f"无法获取文件时间 {file_path}: {e}")
            # 如果无法获取时间，使用当前年份
            return datetime.now().year
    
    def create_year_folder(self, year: int) -> Path:
        """
        创建年份文件夹
        
        Args:
            year: 年份
            
        Returns:
            年份文件夹路径
        """
        year_folder = self.source_folder / str(year)
        
        if year not in self.year_folders:
            if not year_folder.exists():
                if not self.dry_run:
                    try:
                        year_folder.mkdir(exist_ok=True)
                        self.logger.info(f"创建年份文件夹: {year_folder}")
                        self.stats['created_folders'] += 1
                    except Exception as e:
                        self.logger.error(f"无法创建文件夹 {year_folder}: {e}")
                        raise
                else:
                    self.logger.info(f"[试运行] 将创建年份文件夹: {year_folder}")
                    self.stats['created_folders'] += 1
            
            self.year_folders[year] = year_folder
        
        return self.year_folders[year]
    
    def move_file(self, file_path: Path, year_folder: Path) -> bool:
        """
        移动文件到年份文件夹
        
        Args:
            file_path: 源文件路径
            year_folder: 目标年份文件夹
            
        Returns:
            是否移动成功
        """
        destination = year_folder / file_path.name
        
        # 处理文件名冲突
        counter = 1
        original_destination = destination
        while destination.exists():
            name_parts = file_path.stem, counter, file_path.suffix
            destination = year_folder / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
            counter += 1
        
        try:
            if not self.dry_run:
                shutil.move(str(file_path), str(destination))
                self.logger.info(f"移动文件: {file_path.name} -> {destination.parent.name}/{destination.name}")
            else:
                self.logger.info(f"[试运行] 移动文件: {file_path.name} -> {destination.parent.name}/{destination.name}")
            
            self.stats['moved_files'] += 1
            return True
            
        except Exception as e:
            self.logger.error(f"移动文件失败 {file_path} -> {destination}: {e}")
            self.stats['error_files'] += 1
            return False
    
    def scan_and_organize_files(self) -> Dict[int, List[str]]:
        """
        扫描并整理文件
        
        Returns:
            按年份分组的文件列表
        """
        file_groups = {}
        
        try:
            # 获取所有文件（不包括子文件夹）
            all_files = [f for f in self.source_folder.iterdir() if f.is_file()]
            self.stats['total_files'] = len(all_files)
            
            if self.stats['total_files'] == 0:
                self.logger.info("文件夹中没有找到任何文件")
                return file_groups
            
            self.logger.info(f"找到 {self.stats['total_files']} 个文件")
            self.logger.info(f"整理模式: {'创建时间' if self.use_creation_date else '修改时间'}")
            
            if self.dry_run:
                self.logger.info("*** 试运行模式 - 不会实际移动文件 ***\n")
            
            # 首先扫描所有文件，按年份分组
            for file_path in all_files:
                try:
                    year = self.get_file_year(file_path)
                    
                    if year not in file_groups:
                        file_groups[year] = []
                    
                    file_groups[year].append(file_path.name)
                    
                except Exception as e:
                    self.logger.error(f"处理文件失败 {file_path}: {e}")
                    self.stats['error_files'] += 1
            
            # 显示分组统计
            self.logger.info("文件分组统计:")
            for year in sorted(file_groups.keys()):
                count = len(file_groups[year])
                self.logger.info(f"  {year}年: {count} 个文件")
            
            self.logger.info("")
            
            # 执行文件移动
            for file_path in all_files:
                try:
                    year = self.get_file_year(file_path)
                    
                    # 跳过已经在年份文件夹中的文件
                    if file_path.parent.name == str(year):
                        self.logger.debug(f"跳过文件（已在正确位置）: {file_path.name}")
                        self.stats['skipped_files'] += 1
                        continue
                    
                    # 创建年份文件夹
                    year_folder = self.create_year_folder(year)
                    
                    # 移动文件
                    self.move_file(file_path, year_folder)
                    
                except Exception as e:
                    self.logger.error(f"处理文件失败 {file_path}: {e}")
                    self.stats['error_files'] += 1
        
        except Exception as e:
            self.logger.error(f"扫描文件夹失败: {e}")
            raise
        
        return file_groups
    
    def print_summary(self):
        """打印整理摘要"""
        self.logger.info("\n" + "="*50)
        self.logger.info("整理摘要:")
        self.logger.info(f"源文件夹: {self.source_folder}")
        self.logger.info(f"总文件数: {self.stats['total_files']}")
        self.logger.info(f"移动文件数: {self.stats['moved_files']}")
        self.logger.info(f"跳过文件数: {self.stats['skipped_files']}")
        self.logger.info(f"错误文件数: {self.stats['error_files']}")
        self.logger.info(f"创建文件夹数: {self.stats['created_folders']}")
        
        if self.dry_run:
            self.logger.info("\n*** 这是试运行结果，没有实际移动文件 ***")
        
        if self.stats['error_files'] > 0:
            self.logger.warning(f"\n注意: 有 {self.stats['error_files']} 个文件处理失败")
    
    def organize(self):
        """执行文件整理"""
        if not self.validate_source_folder():
            return False
        
        try:
            self.logger.info(f"开始整理文件夹: {self.source_folder}")
            file_groups = self.scan_and_organize_files()
            self.print_summary()
            return True
            
        except KeyboardInterrupt:
            self.logger.info("\n用户中断操作")
            return False
        except Exception as e:
            self.logger.error(f"整理过程中发生错误: {e}")
            return False

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="按年份整理文件夹中的文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  基础用法:
    python organize_files_by_year.py "C:\\Downloads"
    python organize_files_by_year.py /home/user/documents
  
  试运行模式（不实际移动文件）:
    python organize_files_by_year.py "D:\\Photos" --dry-run
  
  使用文件创建时间而非修改时间:
    python organize_files_by_year.py "C:\\temp" --use-creation-date
  
  组合选项:
    python organize_files_by_year.py "C:\\temp" --dry-run --use-creation-date

注意事项:
  - 脚本只会移动文件，不会移动子文件夹
  - 如果目标位置存在同名文件，会自动重命名（添加数字后缀）
  - 建议先使用 --dry-run 选项预览操作结果
        """
    )
    
    parser.add_argument(
        "folder_path",
        help="要整理的文件夹路径"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="试运行模式，只显示将要执行的操作，不实际移动文件"
    )
    
    parser.add_argument(
        "--use-creation-date",
        action="store_true",
        help="使用文件创建时间而非修改时间来确定年份"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细输出"
    )
    
    return parser.parse_args()

def main():
    """主函数"""
    try:
        args = parse_args()
        
        # 设置日志级别
        if args.verbose:
            logging.getLogger('FileOrganizer').setLevel(logging.DEBUG)
        
        # 创建整理器实例
        organizer = FileOrganizerByYear(
            source_folder=args.folder_path,
            dry_run=args.dry_run,
            use_creation_date=args.use_creation_date
        )
        
        # 执行整理
        success = organizer.organize()
        
        if success:
            print("\n整理完成！")
            sys.exit(0)
        else:
            print("\n整理失败！")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"程序运行错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
