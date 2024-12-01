import os
from PyPDF2 import PdfReader
import re
from datetime import datetime

def convert_pdf_to_md(pdf_path, output_dir):
    # 获取PDF文件名（不含扩展名）和相对路径
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    rel_path = os.path.dirname(os.path.relpath(pdf_path, "data"))
    
    # 创建对应的输出目录
    target_dir = os.path.join(output_dir, rel_path)
    os.makedirs(target_dir, exist_ok=True)
    
    # 读取PDF文件
    reader = PdfReader(pdf_path)
    
    # 创建markdown文件
    md_path = os.path.join(target_dir, f"{pdf_name}.md")
    
    with open(md_path, 'w', encoding='utf-8') as md_file:
        # 写入文件头部信息
        md_file.write(f"# {pdf_name}\n\n")
        md_file.write(f"原始文件：{pdf_path}\n")
        md_file.write(f"转换时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        md_file.write("## 目录\n\n")
        
        # 提取并写入正文内容
        for page_num, page in enumerate(reader.pages, 1):
            md_file.write(f"## 第 {page_num} 页\n\n")
            text = page.extract_text()
            # 基本的文本清理
            text = re.sub(r'\s+', ' ', text).strip()
            md_file.write(f"{text}\n\n")
            
    print(f"转换完成！输出文件：{md_path}")
    return md_path

def find_pdf_files(directory):
    """递归查找所有PDF文件"""
    pdf_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

def main():
    # 设置输入输出路径
    pdf_dir = "data"  # PDF文件所在目录
    output_dir = "data/markdown"  # 输出目录
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 查找所有PDF文件
    pdf_files = find_pdf_files(pdf_dir)
    
    # 统计信息
    total_files = len(pdf_files)
    converted_files = 0
    failed_files = []
    
    # 遍历PDF文件并转换
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