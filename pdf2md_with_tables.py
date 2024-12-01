import os
import pdfplumber
import re
from datetime import datetime
from typing import List, Dict

def extract_table_to_md(table) -> str:
    """将表格转换为Markdown格式"""
    if not table or not table[0]:
        return ""
    
    # 清理单元格数据
    cleaned_table = []
    for row in table:
        cleaned_row = []
        for cell in row:
            if cell is None:
                cell = ""
            cell = str(cell).strip().replace('\n', '<br>')
            cleaned_row.append(cell)
        cleaned_table.append(cleaned_row)
    
    # 获取每列的最大宽度
    col_widths = [max(len(str(row[i])) for row in cleaned_table) for i in range(len(cleaned_table[0]))]
    
    # 生成markdown表格
    md_table = []
    
    # 表头
    header = "|" + "|".join(f" {cell:{width}} " for cell, width in zip(cleaned_table[0], col_widths)) + "|"
    md_table.append(header)
    
    # 分隔行
    separator = "|" + "|".join(f" {'-'*width} " for width in col_widths) + "|"
    md_table.append(separator)
    
    # 数据行
    for row in cleaned_table[1:]:
        row_str = "|" + "|".join(f" {cell:{width}} " for cell, width in zip(row, col_widths)) + "|"
        md_table.append(row_str)
    
    return "\n".join(md_table) + "\n\n"

def convert_pdf_to_md(pdf_path: str, output_dir: str) -> str:
    # 获取PDF文件名和相对路径
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    rel_path = os.path.dirname(os.path.relpath(pdf_path, "data"))
    
    # 创建输出目录
    target_dir = os.path.join(output_dir, rel_path)
    os.makedirs(target_dir, exist_ok=True)
    
    # 创建markdown文件路径
    md_path = os.path.join(target_dir, f"{pdf_name}.md")
    
    with pdfplumber.open(pdf_path) as pdf, open(md_path, 'w', encoding='utf-8') as md_file:
        # 写入文件信息
        md_file.write(f"# {pdf_name}\n\n")
        md_file.write(f"原始文件：{pdf_path}\n")
        md_file.write(f"转换时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        md_file.write("## 目录\n\n")
        
        # 处理每一页
        for page_num, page in enumerate(pdf.pages, 1):
            md_file.write(f"## 第 {page_num} 页\n\n")
            
            # 提取表格
            tables = page.extract_tables()
            
            # 提取文本
            text = page.extract_text()
            
            # 如果有表格，将文本分段并在适当位置插入表格
            if tables:
                # 处理文本和表格
                text_parts = text.split('\n')
                table_index = 0
                
                for part in text_parts:
                    part = part.strip()
                    if part:
                        md_file.write(f"{part}\n\n")
                        # 在段落后插入表格
                        if table_index < len(tables):
                            md_file.write(extract_table_to_md(tables[table_index]))
                            table_index += 1
            else:
                # 没有表格，直接写入文本
                text = re.sub(r'\s+', ' ', text).strip()
                md_file.write(f"{text}\n\n")
    
    print(f"转换完成！输出文件：{md_path}")
    return md_path

def find_pdf_files(directory: str) -> List[str]:
    """递归查找所有PDF文件"""
    pdf_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

def main():
    # 设置路径
    pdf_dir = "data"
    output_dir = "data/markdown"
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 查找所有PDF文件
    pdf_files = find_pdf_files(pdf_dir)
    
    # 统计信息
    total_files = len(pdf_files)
    converted_files = 0
    failed_files = []
    
    # 转换文件
    for pdf_path in pdf_files:
        try:
            convert_pdf_to_md(pdf_path, output_dir)
            converted_files += 1
            print(f"进度: {converted_files}/{total_files}")
        except Exception as e:
            failed_files.append((pdf_path, str(e)))
            print(f"转换 {pdf_path} 时出错：{str(e)}")
    
    # 打印总结
    print("\n转换完成！")
    print(f"总文件数: {total_files}")
    print(f"成功转换: {converted_files}")
    print(f"失败文件数: {len(failed_files)}")
    
    if failed_files:
        print("\n失败文件列表:")
        for file, error in failed_files:
            print(f"- {file}: {error}")

if __name__ == "__main__":
    main() 