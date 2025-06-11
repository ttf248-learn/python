import argparse
import os
import time
import signal
import sys
import json
import logging
from datetime import datetime
from typing import Tuple, Optional, Dict, Any
from pathlib import Path

class FolderMonitor:
    def __init__(self, folder_path: str, interval_minutes: float, 
                 log_file: Optional[str] = None, json_output: bool = False):
        self.folder_path = Path(folder_path).resolve()
        self.interval_minutes = interval_minutes
        self.interval_seconds = interval_minutes * 60
        self.json_output = json_output
        self.previous_size = None
        self.start_time = datetime.now()
        self.setup_logging(log_file)
        self.setup_signal_handlers()
        
    def setup_logging(self, log_file: Optional[str]):
        """设置日志记录"""
        self.logger = logging.getLogger('FolderMonitor')
        self.logger.setLevel(logging.INFO)
        
        # 控制台输出
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 文件输出
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def setup_signal_handlers(self):
        """设置信号处理器"""
        signal.signal(signal.SIGINT, self.signal_handler)
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """处理退出信号"""
        self.logger.info(f"\n[{self.format_timestamp()}] 监控已停止")
        self.print_summary()
        sys.exit(0)
    
    def format_timestamp(self) -> str:
        """格式化时间戳"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def format_size(self, size_bytes: int) -> str:
        """自适应格式化文件大小"""
        if size_bytes is None:
            return "未知"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size = float(size_bytes)
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        else:
            return f"{size:.2f} {units[unit_index]}"
    
    def get_folder_stats(self, folder_path: Path, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        获取文件夹统计信息，包括总大小、文件数量和文件夹数量
        """
        for attempt in range(max_retries):
            try:
                total_size = 0
                file_count = 0
                folder_count = 0
                largest_file = {'name': '', 'size': 0}
                
                for root, dirs, files in os.walk(folder_path):
                    folder_count += len(dirs)
                    
                    for filename in files:
                        file_count += 1
                        filepath = Path(root) / filename
                        
                        try:
                            if filepath.exists():
                                file_size = filepath.stat().st_size
                                total_size += file_size
                                
                                # 跟踪最大文件
                                if file_size > largest_file['size']:
                                    largest_file = {
                                        'name': str(filepath.relative_to(folder_path)),
                                        'size': file_size
                                    }
                        except (OSError, IOError) as e:
                            self.logger.warning(f"无法访问文件 {filepath}: {e}")
                            continue
                
                return {
                    'total_size': total_size,
                    'file_count': file_count,
                    'folder_count': folder_count,
                    'largest_file': largest_file
                }
                
            except (OSError, IOError) as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"获取文件夹信息失败，重试 {attempt + 1}/{max_retries}: {e}")
                    time.sleep(1)
                else:
                    self.logger.error(f"无法访问文件夹 {folder_path}: {e}")
                    return None
        
        return None
    
    def print_summary(self):
        """打印监控摘要"""
        duration = datetime.now() - self.start_time
        self.logger.info(f"监控时长: {duration}")
        self.logger.info(f"监控文件夹: {self.folder_path}")
    
    def format_output(self, timestamp: str, stats: Dict[str, Any], 
                     size_change: Optional[float] = None) -> str:
        """格式化输出信息"""
        if self.json_output:
            output_data = {
                'timestamp': timestamp,
                'folder_path': str(self.folder_path),
                'total_size_bytes': stats['total_size'],
                'total_size_formatted': self.format_size(stats['total_size']),
                'file_count': stats['file_count'],
                'folder_count': stats['folder_count'],
                'largest_file': stats['largest_file']
            }
            
            if size_change is not None:
                output_data['size_change_bytes'] = size_change
                output_data['size_change_formatted'] = self.format_size(abs(int(size_change)))
            
            return json.dumps(output_data, ensure_ascii=False, indent=2)
        else:
            # 文本格式输出
            size_str = self.format_size(stats['total_size'])
            
            change_indicator = ""
            if size_change is not None:
                if size_change > 0:
                    change_indicator = f" (+{self.format_size(int(size_change))})"
                elif size_change < 0:
                    change_indicator = f" (-{self.format_size(int(abs(size_change)))})"
                else:
                    change_indicator = " (无变化)"
            
            output = f"[{timestamp}] 文件夹体积: {size_str}{change_indicator}"
            output += f" | 文件: {stats['file_count']} | 文件夹: {stats['folder_count']}"
            
            if stats['largest_file']['name']:
                largest_size = self.format_size(stats['largest_file']['size'])
                output += f" | 最大文件: {stats['largest_file']['name']} ({largest_size})"
            
            return output
    
    def monitor(self):
        """开始监控"""
        self.logger.info(f"开始监控文件夹: {self.folder_path}")
        self.logger.info(f"监控间隔: {self.interval_minutes} 分钟")
        self.logger.info(f"输出格式: {'JSON' if self.json_output else '文本'}")
        self.logger.info("按 Ctrl+C 停止监控\n")
        
        while True:
            try:
                timestamp = self.format_timestamp()
                stats = self.get_folder_stats(self.folder_path)
                
                if stats is not None:
                    current_size = stats['total_size']
                    size_change = None
                    
                    if self.previous_size is not None:
                        size_change = current_size - self.previous_size
                    
                    output = self.format_output(timestamp, stats, size_change)
                    self.logger.info(output)
                    
                    self.previous_size = current_size
                else:
                    self.logger.error(f"[{timestamp}] 错误：无法获取文件夹统计信息")
                
                time.sleep(self.interval_seconds)
                
            except Exception as e:
                self.logger.error(f"[{self.format_timestamp()}] 监控过程中发生错误: {e}")
                time.sleep(self.interval_seconds)

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="监控文件夹体积变化",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  基础用法:
    python folder_monitor.py "C:\\Users\\Documents"
    python folder_monitor.py /home/user/documents
  
  指定监控间隔:
    python folder_monitor.py "D:\\Downloads" -i 0.5          # 30秒间隔
    python folder_monitor.py "D:\\Downloads" --interval 5    # 5分钟间隔
  
  保存日志到文件:
    python folder_monitor.py "C:\\temp" --log monitor.log
    python folder_monitor.py "C:\\temp" --log "logs\\monitor_%Y%m%d.log"
  
  JSON格式输出:
    python folder_monitor.py "C:\\temp" --json
    python folder_monitor.py "C:\\temp" --json --log data.json
  
  使用配置文件:
    python folder_monitor.py "C:\\temp" --config config.json
  
  生成示例配置文件:
    python folder_monitor.py --generate-config
        """
    )
    
    parser.add_argument(
        "folder_path",
        nargs='?',
        help="要监控的文件夹路径"
    )
    
    parser.add_argument(
        "-i", "--interval",
        type=float,
        default=1.0,
        help="监控间隔，单位分钟 (默认: 1.0)"
    )
    
    parser.add_argument(
        "--log",
        help="日志文件路径，支持时间格式化如 %%Y%%m%%d"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="使用JSON格式输出"
    )
    
    parser.add_argument(
        "--config",
        help="配置文件路径（JSON格式）"
    )
    
    parser.add_argument(
        "--generate-config",
        action="store_true",
        help="生成示例配置文件"
    )
    
    return parser.parse_args()

def generate_sample_config():
    """生成示例配置文件"""
    config = {
        "interval": 5.0,
        "log_file": "logs/folder_monitor_%Y%m%d.log",
        "json_output": False,
        "max_retries": 3,
        "description": "文件夹监控配置文件",
        "examples": {
            "short_interval": "间隔30秒: interval = 0.5",
            "hourly_check": "每小时检查: interval = 60",
            "json_log": "JSON日志: json_output = true, log_file = 'data.json'"
        }
    }
    
    config_file = "folder_monitor_config.json"
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        print(f"示例配置文件已生成: {config_file}")
        print("\n配置文件内容:")
        print(json.dumps(config, ensure_ascii=False, indent=2))
        return True
    except Exception as e:
        print(f"生成配置文件失败: {e}")
        return False

def load_config(config_path: str) -> Dict[str, Any]:
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"错误：无法加载配置文件 {config_path}: {e}")
        sys.exit(1)

def validate_args(args) -> bool:
    """验证命令行参数"""
    folder_path = Path(args.folder_path)
    
    if not folder_path.exists():
        print(f"错误：文件夹路径不存在: {folder_path}")
        return False
    
    if not folder_path.is_dir():
        print(f"错误：指定路径不是文件夹: {folder_path}")
        return False
    
    if args.interval <= 0:
        print("错误：监控间隔必须大于0")
        return False
    
    if args.interval < 0.01:  # 优化最小间隔检查
        print("警告：监控间隔过短可能影响系统性能")
    
    # 验证日志文件路径
    if args.log:
        log_path = Path(args.log)
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"错误：无法创建日志文件目录: {e}")
            return False
    
    return True

def main():
    """主函数"""
    try:
        args = parse_args()
        
        # 生成配置文件选项
        if args.generate_config:
            generate_sample_config()
            return
        
        # 检查是否提供了文件夹路径
        if not args.folder_path:
            print("错误: 请提供要监控的文件夹路径")
            print("使用 --help 查看详细使用说明")
            sys.exit(1)
        
        # 如果指定了配置文件，从配置文件加载参数
        if args.config:
            config = load_config(args.config)
            # 配置文件中的参数会覆盖命令行参数（除了folder_path）
            args.interval = config.get('interval', args.interval)
            args.log = config.get('log_file', args.log)
            args.json = config.get('json_output', args.json)
        
        # 处理日志文件路径中的时间格式化
        if args.log:
            args.log = datetime.now().strftime(args.log)
        
        if not validate_args(args):
            sys.exit(1)
        
        # 创建监控器实例
        monitor = FolderMonitor(
            folder_path=args.folder_path,
            interval_minutes=args.interval,
            log_file=args.log,
            json_output=args.json
        )
        
        # 开始监控
        monitor.monitor()
        
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 监控已停止")
    except Exception as e:
        print(f"程序运行错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
