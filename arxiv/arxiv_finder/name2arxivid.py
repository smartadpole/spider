#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arXiv ID 查找器
根据论文名称自动搜索对应的 arXiv ID
"""

import re
import requests
import time
import argparse
import os
from typing import List, Tuple, Optional
from urllib.parse import quote
import xml.etree.ElementTree as ET


class ArXivIDFinder:
    """arXiv ID 查找器类"""
    
    def __init__(self, delay: float = 1.0):
        """
        初始化查找器
        
        Args:
            delay: 请求间隔时间（秒），避免请求过于频繁
        """
        self.delay = delay
        self.base_url = "http://export.arxiv.org/api/query"
        
    def clean_title(self, title: str) -> str:
        """
        清理论文标题，去除常见的前后缀和连接符
        
        Args:
            title: 原始标题
            
        Returns:
            清理后的标题
        """
        # 去除文件扩展名
        title = re.sub(r'\.pdf.*$', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\.txt.*$', '', title, flags=re.IGNORECASE)
        
        # 去除下划线、连字符等连接符，替换为空格
        title = re.sub(r'[_-]', ' ', title)
        
        # 去除多余的空格
        title = re.sub(r'\s+', ' ', title).strip()
        
        # 去除常见的论文前缀
        prefixes_to_remove = [
            r'^paper\s*[-_:]?\s*',
            r'^arxiv\s*[-_:]?\s*',
            r'^preprint\s*[-_:]?\s*',
            r'^draft\s*[-_:]?\s*',
        ]
        
        for prefix in prefixes_to_remove:
            title = re.sub(prefix, '', title, flags=re.IGNORECASE)
        
        # 去除会议名称和年份信息
        conference_patterns = [
            r'\s*(?:CVPR|ICCV|ECCV|ICLR|ICML|NeurIPS|AAAI|IJCAI|ACL|EMNLP|NAACL|SIGIR|SIGKDD|WWW|ICDE|SIGMOD|VLDB|ICSE|FSE|ASE|OOPSLA|PLDI|POPL|SOSP|OSDI|NSDI|SIGCOMM|INFOCOM|MOBICOM|SIGGRAPH|TOG|SIGCHI|UIST|CHI)\s*(?:20\d{2})?\s*(?:paper)?\s*$',
            r'\s*(?:paper)?\s*(?:CVPR|ICCV|ECCV|ICLR|ICML|NeurIPS|AAAI|IJCAI|ACL|EMNLP|NAACL|SIGIR|SIGKDD|WWW|ICDE|SIGMOD|VLDB|ICSE|FSE|ASE|OOPSLA|PLDI|POPL|SOSP|OSDI|NSDI|SIGCOMM|INFOCOM|MOBICOM|SIGGRAPH|TOG|SIGCHI|UIST|CHI)\s*(?:20\d{2})?\s*$',
            r'\s*(?:20\d{2})\s*(?:CVPR|ICCV|ECCV|ICLR|ICML|NeurIPS|AAAI|IJCAI|ACL|EMNLP|NAACL|SIGIR|SIGKDD|WWW|ICDE|SIGMOD|VLDB|ICSE|FSE|ASE|OOPSLA|PLDI|POPL|SOSP|OSDI|NSDI|SIGCOMM|INFOCOM|MOBICOM|SIGGRAPH|TOG|SIGCHI|UIST|CHI)\s*(?:paper)?\s*$',
        ]
        
        for pattern in conference_patterns:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        
        # 去除年份（4位数字）
        title = re.sub(r'\s*20\d{2}\s*', ' ', title)
        
        # 去除常见的后缀词
        suffix_patterns = [
            r'\s+paper\s*$',
            r'\s+preprint\s*$',
            r'\s+draft\s*$',
            r'\s+version\s*$',
            r'\s+final\s*$',
            r'\s+submission\s*$',
        ]
        
        for pattern in suffix_patterns:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        
        # 再次去除多余的空格
        title = re.sub(r'\s+', ' ', title).strip()
        
        return title.strip()
    
    def generate_search_variants(self, title: str) -> List[str]:
        """
        生成标题的多个搜索变体，用于模糊匹配
        
        Args:
            title: 清理后的标题
            
        Returns:
            搜索变体列表
        """
        variants = [title]

        # 变体4: 使用引号包围的精确匹配
        variants.append(f'"{title}"')
        
        # 变体1: 去除冠词和介词
        words = title.split()
        filtered_words = []
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among'}
        
        for word in words:
            if word.lower() not in stop_words:
                filtered_words.append(word)
        
        if len(filtered_words) > 3:  # 确保有足够的词
            variants.append(' '.join(filtered_words))
        
        # 变体2: 只保留前几个关键词（通常是核心概念）
        if len(words) > 4:
            # 保留前4个词
            variants.append(' '.join(words[:4]))
        
        # 变体3: 去除最后一个词（可能是修饰词）
        if len(words) > 3:
            variants.append(' '.join(words[:-1]))

        
        # 去重并过滤空字符串
        unique_variants = list(set([v.strip() for v in variants if v.strip()]))
        
        return unique_variants
    
    def search_arxiv(self, title: str) -> Optional[str]:
        """
        在arXiv中搜索论文标题，返回对应的arXiv ID
        
        Args:
            title: 论文标题
            
        Returns:
            arXiv ID，如果未找到则返回None
        """
        try:
            # 构建查询参数
            params = {
                'search_query': f'ti:"{title}"',
                'start': 0,
                'max_results': 5,
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }
            
            # 发送请求
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            # 解析XML响应
            root = ET.fromstring(response.content)
            
            # 查找arXiv ID
            entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            if entries:
                # 获取第一个结果的ID
                arxiv_id = entries[0].find('.//{http://www.w3.org/2005/Atom}id')
                if arxiv_id is not None:
                    # 提取ID中的数字部分
                    id_text = arxiv_id.text
                    match = re.search(r'arxiv\.org/abs/(\d+\.\d+)', id_text)
                    if match:
                        return match.group(1)
            
            return None
            
        except Exception as e:
            print(f"搜索标题 '{title}' 时出错: {e}")
            return None
    
    def fuzzy_search_arxiv(self, title: str) -> Optional[str]:
        """
        使用模糊匹配在arXiv中搜索论文标题
        
        Args:
            title: 论文标题
            
        Returns:
            arXiv ID，如果未找到则返回None
        """
        # 生成搜索变体
        variants = self.generate_search_variants(title)
        
        print(f"  尝试 {len(variants)} 个搜索变体...")
        
        for i, variant in enumerate(variants, 1):
            print(f"    变体 {i}: {variant}")
            
            try:
                # 构建查询参数
                params = {
                    'search_query': f'ti:"{variant}"',
                    'start': 0,
                    'max_results': 3,  # 减少结果数量以提高速度
                    'sortBy': 'relevance',
                    'sortOrder': 'descending'
                }
                
                # 发送请求
                response = requests.get(self.base_url, params=params, timeout=10)
                response.raise_for_status()
                
                # 解析XML响应
                root = ET.fromstring(response.content)
                
                # 查找arXiv ID
                entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
                
                if entries:
                    # 获取第一个结果的ID
                    arxiv_id = entries[0].find('.//{http://www.w3.org/2005/Atom}id')
                    if arxiv_id is not None:
                        # 提取ID中的数字部分
                        id_text = arxiv_id.text
                        match = re.search(r'arxiv\.org/abs/(\d+\.\d+)', id_text)
                        if match:
                            print(f"    ✓ 在变体 {i} 中找到 arXiv ID: {match.group(1)}")
                            return match.group(1)
                
                # 添加短暂延迟避免请求过于频繁
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    变体 {i} 搜索出错: {e}")
                continue
        
        return None
    
    def find_arxiv_id(self, title: str) -> Tuple[str, Optional[str]]:
        """
        查找论文的arXiv ID
        
        Args:
            title: 原始论文标题
            
        Returns:
            (原始标题, arXiv ID) 的元组
        """
        # 清理标题
        cleaned_title = self.clean_title(title)
        
        if not cleaned_title:
            return title, None
        
        print(f"  清理后标题: {cleaned_title}")
        
        # 首先尝试精确匹配
        arxiv_id = self.search_arxiv(cleaned_title)
        
        # 如果精确匹配失败，尝试模糊匹配
        if not arxiv_id:
            print(f"  精确匹配失败，尝试模糊匹配...")
            arxiv_id = self.fuzzy_search_arxiv(cleaned_title)
        
        # 添加延迟避免请求过于频繁
        time.sleep(self.delay)
        
        return cleaned_title, arxiv_id
    
    def process_file(self, input_file: str, output_file: str = None) -> None:
        """
        处理输入文件，查找所有论文的arXiv ID
        
        Args:
            input_file: 输入文件名列表文件
            output_file: 输出结果文件，如果为None则打印到控制台
        """
        try:
            # 读取输入文件
            with open(input_file, 'r', encoding='utf-8') as f:
                titles = [line.strip() for line in f if line.strip()]
            
            print(f"共读取到 {len(titles)} 个论文标题")
            
            # 处理每个标题
            arxiv_ids = []
            failed_titles = []
            
            for i, title in enumerate(titles, 1):
                cleaned_title, arxiv_id = self.find_arxiv_id(title)
                print(f"正在处理 ({i}/{len(titles)}): {cleaned_title}")

                if arxiv_id:
                    arxiv_ids.append(arxiv_id)
                    print(f"  ✓ 找到 arXiv ID: {arxiv_id}")
                else:
                    failed_titles.append(cleaned_title)
                    print(f"  ✗ 未找到 arXiv ID，保留名称")
            
            # 准备输出内容
            output_content = []
            output_content.append("找到的 arXiv ID:")
            output_content.extend(arxiv_ids)
            output_content.append("")
            output_content.append("搜索失败的文献名字:")
            output_content.extend(failed_titles)
            
            # 输出结果
            if output_file:
                # 保存到文件
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("\n".join(output_content))
                print(f"\n处理完成！结果已保存到: {output_file}")
            else:
                # 直接打印到控制台
                print("\n" + "="*50)
                print("\n".join(output_content))
                print("="*50)
            
            print(f"成功找到 {len(arxiv_ids)} 个 arXiv ID")
            print(f"搜索失败 {len(failed_titles)} 个文献")
            
        except FileNotFoundError:
            print(f"错误: 找不到输入文件 {input_file}")
        except Exception as e:
            print(f"处理文件时出错: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='根据论文名称自动搜索arXiv ID')
    parser.add_argument('input_file', help='包含论文名称的输入文件')
    parser.add_argument('-o', '--output', default=None, 
                       help='输出文件路径 (默认: 直接打印到控制台)')
    parser.add_argument('-d', '--delay', type=float, default=1.0,
                       help='请求间隔时间（秒）(默认: 1.0)')
    
    args = parser.parse_args()
    
    # 检查输入文件是否存在
    if not os.path.exists(args.input_file):
        print(f"错误: 输入文件 {args.input_file} 不存在")
        return
    
    # 创建查找器并处理文件
    finder = ArXivIDFinder(delay=args.delay)
    finder.process_file(args.input_file, args.output)


if __name__ == "__main__":
    main() 