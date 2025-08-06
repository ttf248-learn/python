#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced XML to Excel Converter
高级XML到Excel转换器 - 支持命令行参数和批量处理

使用方法:
    python xml_to_excel_advanced.py input.xml [output.xlsx]
    python xml_to_excel_advanced.py --batch *.xml
    python xml_to_excel_advanced.py --help
"""

import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
import argparse
import os
import sys
import glob
from pathlib import Path

class ExcelXMLConverter:
    """
    Excel XML转换器类
    """
    
    def __init__(self):
        self.namespaces = {
            'ss': 'urn:schemas-microsoft-com:office:spreadsheet',
            'o': 'urn:schemas-microsoft-com:office:office',
            'x': 'urn:schemas-microsoft-com:office:excel',
            'html': 'http://www.w3.org/TR/REC-html40'
        }
    
    def parse_cell_value(self, data_element):
        """
        解析单元格值并根据类型进行转换
        
        Args:
            data_element: XML数据元素
            
        Returns:
            转换后的值
        """
        if data_element is None:
            return ''
            
        cell_value = data_element.text if data_element.text else ''
        data_type = data_element.get('{urn:schemas-microsoft-com:office:spreadsheet}Type', 'String')
        
        try:
            if data_type == 'Boolean':
                return bool(int(cell_value)) if cell_value else False
            elif data_type == 'Number':
                return float(cell_value) if cell_value else 0
            elif data_type == 'DateTime':
                if cell_value and 'T' in cell_value:
                    # 处理日期时间格式
                    date_part = cell_value.split('T')[0]
                    return datetime.strptime(date_part, '%Y-%m-%d').strftime('%Y-%m-%d')
                return cell_value
            else:
                return str(cell_value)
        except Exception:
            return str(cell_value)  # 如果转换失败，返回原始字符串
    
    def parse_worksheet(self, worksheet):
        """
        解析单个工作表
        
        Args:
            worksheet: XML工作表元素
            
        Returns:
            list: 工作表数据行列表
        """
        table = worksheet.find('.//ss:Table', self.namespaces)
        if table is None:
            return []
        
        sheet_data = []
        rows = table.findall('.//ss:Row', self.namespaces)
        
        for row in rows:
            row_data = []
            cells = row.findall('.//ss:Cell', self.namespaces)
            current_col = 0
            
            for cell in cells:
                # 处理单元格索引（跳过的列）
                index_attr = cell.get('{urn:schemas-microsoft-com:office:spreadsheet}Index')
                if index_attr:
                    target_col = int(index_attr) - 1
                    # 填充空列
                    while current_col < target_col:
                        row_data.append('')
                        current_col += 1
                
                # 获取单元格数据
                data_element = cell.find('.//ss:Data', self.namespaces)
                cell_value = self.parse_cell_value(data_element)
                row_data.append(cell_value)
                current_col += 1
            
            sheet_data.append(row_data)
        
        return sheet_data
    
    def parse_xml_file(self, xml_file_path):
        """
        解析XML文件
        
        Args:
            xml_file_path (str): XML文件路径
            
        Returns:
            dict: 包含所有工作表数据的字典
        """
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            
            workbook_data = {}
            worksheets = root.findall('.//ss:Worksheet', self.namespaces)
            
            for worksheet in worksheets:
                sheet_name = worksheet.get(
                    '{urn:schemas-microsoft-com:office:spreadsheet}Name', 
                    'Sheet1'
                )
                sheet_data = self.parse_worksheet(worksheet)
                if sheet_data:  # 只添加非空工作表
                    workbook_data[sheet_name] = sheet_data
            
            return workbook_data
            
        except ET.ParseError as e:
            raise ValueError(f"XML解析错误: {e}")
        except Exception as e:
            raise ValueError(f"文件读取错误: {e}")
    
    def normalize_sheet_data(self, sheet_data):
        """
        标准化工作表数据（确保所有行具有相同列数）
        
        Args:
            sheet_data (list): 原始工作表数据
            
        Returns:
            list: 标准化后的数据
        """
        if not sheet_data:
            return []
        
        max_cols = max(len(row) for row in sheet_data)
        normalized_data = []
        
        for row in sheet_data:
            # 补齐列数
            normalized_row = row[:]
            while len(normalized_row) < max_cols:
                normalized_row.append('')
            normalized_data.append(normalized_row)
        
        return normalized_data
    
    def convert_to_excel(self, xml_file_path, output_excel_path=None, verbose=True):
        """
        将XML文件转换为Excel文件
        
        Args:
            xml_file_path (str): 输入XML文件路径
            output_excel_path (str): 输出Excel文件路径
            verbose (bool): 是否显示详细信息
            
        Returns:
            str: 输出文件路径
        """
        if verbose:
            print(f"正在解析XML文件: {xml_file_path}")
        
        # 检查输入文件
        if not os.path.exists(xml_file_path):
            raise FileNotFoundError(f"输入文件不存在: {xml_file_path}")
        
        # 解析XML数据
        workbook_data = self.parse_xml_file(xml_file_path)
        
        if not workbook_data:
            raise ValueError("XML文件中没有找到有效的工作表数据")
        
        # 生成输出文件路径
        if output_excel_path is None:
            base_name = Path(xml_file_path).stem
            output_dir = Path(xml_file_path).parent
            output_excel_path = output_dir / f"{base_name}_converted.xlsx"
        
        # 转换为Excel
        with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
            total_rows = 0
            
            for sheet_name, sheet_data in workbook_data.items():
                if verbose:
                    print(f"正在处理工作表: {sheet_name}")
                
                # 标准化数据
                normalized_data = self.normalize_sheet_data(sheet_data)
                
                if normalized_data:
                    # 创建DataFrame
                    if len(normalized_data) > 1:
                        # 第一行作为列名
                        headers = normalized_data[0]
                        data_rows = normalized_data[1:]
                        df = pd.DataFrame(data_rows, columns=headers)
                    else:
                        df = pd.DataFrame(normalized_data)
                    
                    # 写入Excel
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    total_rows += len(df)
                    
                    if verbose:
                        print(f"  - 已写入 {len(df)} 行数据")
            
            if verbose:
                print(f"转换完成！总共处理 {total_rows} 行数据")
                print(f"输出文件: {output_excel_path}")
        
        return str(output_excel_path)

def batch_convert(pattern, verbose=True):
    """
    批量转换XML文件
    
    Args:
        pattern (str): 文件匹配模式
        verbose (bool): 是否显示详细信息
    """
    converter = ExcelXMLConverter()
    xml_files = glob.glob(pattern)
    
    if not xml_files:
        print(f"没有找到匹配的文件: {pattern}")
        return
    
    print(f"找到 {len(xml_files)} 个XML文件")
    
    success_count = 0
    for xml_file in xml_files:
        try:
            if verbose:
                print(f"\n{'='*50}")
            output_file = converter.convert_to_excel(xml_file, verbose=verbose)
            success_count += 1
            
            if verbose:
                file_size = os.path.getsize(output_file)
                print(f"文件大小: {file_size:,} 字节")
                
        except Exception as e:
            print(f"转换失败 {xml_file}: {e}")
    
    print(f"\n批量转换完成！成功转换 {success_count}/{len(xml_files)} 个文件")

def main():
    """
    主函数 - 处理命令行参数
    """
    parser = argparse.ArgumentParser(
        description='将Microsoft Excel XML文件转换为标准Excel格式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s input.xml                    # 转换单个文件
  %(prog)s input.xml output.xlsx        # 指定输出文件名
  %(prog)s --batch "*.xml"              # 批量转换所有XML文件
  %(prog)s --batch "data/*.xml"         # 批量转换data目录下的XML文件
        """
    )
    
    parser.add_argument('input', nargs='?', help='输入XML文件路径')
    parser.add_argument('output', nargs='?', help='输出Excel文件路径（可选）')
    parser.add_argument('--batch', metavar='PATTERN', help='批量转换模式，使用文件匹配模式')
    parser.add_argument('--quiet', '-q', action='store_true', help='静默模式，减少输出信息')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    
    args = parser.parse_args()
    
    # 检查参数
    if args.batch:
        # 批量转换模式
        batch_convert(args.batch, verbose=not args.quiet)
    elif args.input:
        # 单文件转换模式
        try:
            converter = ExcelXMLConverter()
            output_file = converter.convert_to_excel(
                args.input, 
                args.output, 
                verbose=not args.quiet
            )
            
            if not args.quiet:
                file_size = os.path.getsize(output_file)
                print(f"\n转换成功！")
                print(f"输入文件: {args.input}")
                print(f"输出文件: {output_file}")
                print(f"文件大小: {file_size:,} 字节")
                
        except Exception as e:
            print(f"转换失败: {e}")
            sys.exit(1)
    else:
        # 没有提供参数，使用默认文件
        default_file = "3. ForwardSplit.xml"
        if os.path.exists(default_file):
            try:
                converter = ExcelXMLConverter()
                output_file = converter.convert_to_excel(default_file, verbose=not args.quiet)
                
                if not args.quiet:
                    file_size = os.path.getsize(output_file)
                    print(f"\n转换成功！")
                    print(f"输入文件: {default_file}")
                    print(f"输出文件: {output_file}")
                    print(f"文件大小: {file_size:,} 字节")
                    
            except Exception as e:
                print(f"转换失败: {e}")
                sys.exit(1)
        else:
            parser.print_help()
            print(f"\n错误: 请提供输入文件或使用 --batch 选项")
            sys.exit(1)

if __name__ == "__main__":
    main()