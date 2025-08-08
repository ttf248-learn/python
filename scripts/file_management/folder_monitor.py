import argparse
import os
import time
import signal
import sys
from loguru import logger
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any, List
from pathlib import Path
from collections import deque

class FolderMonitor:
    def __init__(self, folder_path: str, interval_minutes: float):
        self.folder_path = Path(folder_path).resolve()
        self.interval_minutes = interval_minutes
        self.interval_seconds = interval_minutes * 60
        self.previous_size = None
        self.start_time = datetime.now()
        
        # 历史数据存储 - 使用deque限制内存使用
        self.size_history = deque(maxlen=24*60*7)  # 保留一周的分钟级数据
        self.last_minute_record = None
        self.last_hour_record = None
        self.last_12hour_record = None
        self.last_day_record = None
        
        self.setup_logging()
        self.setup_signal_handlers()
        
    def setup_logging(self, log_dir: str = 'log'):
        """设置日志配置"""
        # loguru默认输出到终端，同时添加文件日志
        # 使用默认的日志目录和文件名格式
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file_path = os.path.join(log_dir, 'folder_monitor_{time:YYYY-MM-DD}.log')
        
        # 添加日志记录器，按天滚动，并保留30天的日志
        log_format = "{time:YYYY-MM-DD HH:mm:ss} - {level} - {name}:{function}:{line} - {message}"
        logger.add(log_file_path, rotation="00:00", retention="30 days", level="DEBUG", format=log_format)
    
    def setup_signal_handlers(self):
        """设置信号处理器"""
        signal.signal(signal.SIGINT, self.signal_handler)
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """处理退出信号"""
        logger.info(f"\n[{self.format_timestamp()}] 监控已停止")
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
                            logger.warning(f"无法访问文件 {filepath}: {e}")
                            continue
                
                return {
                    'total_size': total_size,
                    'file_count': file_count,
                    'folder_count': folder_count,
                    'largest_file': largest_file
                }
                
            except (OSError, IOError) as e:
                if attempt < max_retries - 1:
                    logger.warning(f"获取文件夹信息失败，重试 {attempt + 1}/{max_retries}: {e}")
                    time.sleep(1)
                else:
                    logger.error(f"无法访问文件夹 {folder_path}: {e}")
                    return None
        
        return None
    
    def print_summary(self):
        """打印监控摘要"""
        duration = datetime.now() - self.start_time
        logger.info(f"监控时长: {duration}")
        logger.info(f"监控文件夹: {self.folder_path}")
    
    def add_size_record(self, size: int):
        """添加体积记录到历史数据"""
        now = datetime.now()
        record = {
            'timestamp': now,
            'size': size
        }
        self.size_history.append(record)
        
        # 初始化基准记录
        if self.last_minute_record is None:
            self.last_minute_record = record
            self.last_hour_record = record
            self.last_12hour_record = record
            self.last_day_record = record
    
    def calculate_growth_rates(self, current_size: int) -> Dict[str, Any]:
        """计算各个时间段的增长率"""
        now = datetime.now()
        growth_stats = {
            'per_minute': {'size_change': 0, 'rate': 0, 'available': False},
            'per_hour': {'size_change': 0, 'rate': 0, 'available': False},
            'per_12hour': {'size_change': 0, 'rate': 0, 'available': False},
            'per_day': {'size_change': 0, 'rate': 0, 'available': False}
        }
        
        # 计算每分钟增长率
        if (self.last_minute_record and 
            (now - self.last_minute_record['timestamp']).total_seconds() >= 60):
            
            time_diff = (now - self.last_minute_record['timestamp']).total_seconds() / 60
            size_change = current_size - self.last_minute_record['size']
            growth_stats['per_minute'] = {
                'size_change': size_change,
                'rate': size_change / time_diff if time_diff > 0 else 0,
                'available': True
            }
            self.last_minute_record = {'timestamp': now, 'size': current_size}
        
        # 计算每小时增长率
        if (self.last_hour_record and 
            (now - self.last_hour_record['timestamp']).total_seconds() >= 3600):
            
            time_diff = (now - self.last_hour_record['timestamp']).total_seconds() / 3600
            size_change = current_size - self.last_hour_record['size']
            growth_stats['per_hour'] = {
                'size_change': size_change,
                'rate': size_change / time_diff if time_diff > 0 else 0,
                'available': True
            }
            self.last_hour_record = {'timestamp': now, 'size': current_size}
        
        # 计算每12小时增长率
        if (self.last_12hour_record and 
            (now - self.last_12hour_record['timestamp']).total_seconds() >= 43200):
            
            time_diff = (now - self.last_12hour_record['timestamp']).total_seconds() / 43200
            size_change = current_size - self.last_12hour_record['size']
            growth_stats['per_12hour'] = {
                'size_change': size_change,
                'rate': size_change / time_diff if time_diff > 0 else 0,
                'available': True
            }
            self.last_12hour_record = {'timestamp': now, 'size': current_size}
        
        # 计算每天增长率
        if (self.last_day_record and 
            (now - self.last_day_record['timestamp']).total_seconds() >= 86400):
            
            time_diff = (now - self.last_day_record['timestamp']).total_seconds() / 86400
            size_change = current_size - self.last_day_record['size']
            growth_stats['per_day'] = {
                'size_change': size_change,
                'rate': size_change / time_diff if time_diff > 0 else 0,
                'available': True
            }
            self.last_day_record = {'timestamp': now, 'size': current_size}
        
        return growth_stats
    
    def get_historical_growth(self, current_size: int) -> Dict[str, Any]:
        """获取基于历史数据的增长统计"""
        if not self.size_history:
            return {}
        
        now = datetime.now()
        growth_data = {}
        
        # 查找不同时间段的历史记录
        time_periods = {
            '1_minute': 60,
            '1_hour': 3600,
            '12_hours': 43200,
            '1_day': 86400
        }
        
        for period_name, seconds in time_periods.items():
            target_time = now - timedelta(seconds=seconds)
            
            # 查找最接近目标时间的记录
            closest_record = None
            min_time_diff = float('inf')
            
            for record in self.size_history:
                time_diff = abs((record['timestamp'] - target_time).total_seconds())
                if time_diff < min_time_diff:
                    min_time_diff = time_diff
                    closest_record = record
            
            if closest_record and min_time_diff <= seconds * 0.1:  # 允许10%的时间误差
                actual_time_diff = (now - closest_record['timestamp']).total_seconds()
                size_change = current_size - closest_record['size']
                
                growth_data[period_name] = {
                    'size_change': size_change,
                    'time_diff_hours': actual_time_diff / 3600,
                    'available': True,
                    'record_time': closest_record['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                growth_data[period_name] = {'available': False}
        
        return growth_data
    
    def format_growth_info(self, growth_stats: Dict[str, Any], 
                          historical_growth: Dict[str, Any]) -> str:
        """格式化增长信息"""
        if not growth_stats and not historical_growth:
            return ""
        
        growth_info = []
        
        # 实时增长率（基于固定间隔）
        if growth_stats:
            if growth_stats['per_minute']['available']:
                rate = growth_stats['per_minute']['rate']
                growth_info.append(f"分钟增长: {self.format_size(int(rate))}/min")
            
            if growth_stats['per_hour']['available']:
                rate = growth_stats['per_hour']['rate']
                growth_info.append(f"小时增长: {self.format_size(int(rate))}/h")
            
            if growth_stats['per_12hour']['available']:
                rate = growth_stats['per_12hour']['rate']
                growth_info.append(f"12小时增长: {self.format_size(int(rate))}/12h")
            
            if growth_stats['per_day']['available']:
                rate = growth_stats['per_day']['rate']
                growth_info.append(f"日增长: {self.format_size(int(rate))}/day")
        
        # 历史增长数据
        if historical_growth:
            if historical_growth.get('1_hour', {}).get('available'):
                change = historical_growth['1_hour']['size_change']
                growth_info.append(f"过去1小时: {self.format_size(int(change))}")
            
            if historical_growth.get('12_hours', {}).get('available'):
                change = historical_growth['12_hours']['size_change']
                growth_info.append(f"过去12小时: {self.format_size(int(change))}")
            
            if historical_growth.get('1_day', {}).get('available'):
                change = historical_growth['1_day']['size_change']
                growth_info.append(f"过去24小时: {self.format_size(int(change))}")
        
        return " | ".join(growth_info) if growth_info else ""

    def format_output(self, timestamp: str, stats: Dict[str, Any], 
                     size_change: Optional[float] = None, 
                     growth_stats: Optional[Dict[str, Any]] = None,
                     historical_growth: Optional[Dict[str, Any]] = None) -> str:
        """格式化输出信息"""
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
        
        # 添加增长信息
        growth_info = self.format_growth_info(growth_stats or {}, historical_growth or {})
        if growth_info:
            output += f"\n    增长统计: {growth_info}"
        
        return output
    
    def monitor(self):
        """开始监控"""
        logger.info(f"开始监控文件夹: {self.folder_path}")
        logger.info(f"监控间隔: {self.interval_minutes} 分钟")
        logger.info("按 Ctrl+C 停止监控\n")
        
        while True:
            try:
                timestamp = self.format_timestamp()
                stats = self.get_folder_stats(self.folder_path)
                
                if stats is not None:
                    current_size = stats['total_size']
                    size_change = None
                    
                    if self.previous_size is not None:
                        size_change = current_size - self.previous_size
                    
                    # 添加到历史记录
                    self.add_size_record(current_size)
                    
                    # 计算增长率
                    growth_stats = self.calculate_growth_rates(current_size)
                    historical_growth = self.get_historical_growth(current_size)
                    
                    output = self.format_output(timestamp, stats, size_change, 
                                              growth_stats, historical_growth)
                    logger.info(output)
                    
                    self.previous_size = current_size
                else:
                    logger.error(f"[{timestamp}] 错误：无法获取文件夹统计信息")
                
                time.sleep(self.interval_seconds)
                
            except Exception as e:
                logger.error(f"[{self.format_timestamp()}] 监控过程中发生错误: {e}")
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
        """
    )
    
    parser.add_argument(
        "folder_path",
        help="要监控的文件夹路径"
    )
    
    parser.add_argument(
        "-i", "--interval",
        type=float,
        default=1.0,
        help="监控间隔，单位分钟 (默认: 1.0)"
    )
    
    return parser.parse_args()



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
    
    return True

def main():
    """主函数"""
    try:
        args = parse_args()
        
        if not validate_args(args):
            sys.exit(1)
        
        # 创建监控器实例
        monitor = FolderMonitor(
            folder_path=args.folder_path,
            interval_minutes=args.interval
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
