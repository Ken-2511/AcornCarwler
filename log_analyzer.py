#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志分析器 - 统计最后一次运行中while循环的次数
"""

import re
from typing import List, Tuple

def find_last_run_logs(log_file_path: str) -> str:
    """
    找到最后一次运行的日志内容
    
    Args:
        log_file_path: 日志文件路径
        
    Returns:
        最后一次运行的日志内容
    """
    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 找到所有"--- 开始多线程通知任务 ---"的位置
        pattern = r"--- 开始多线程通知任务 ---"
        matches = list(re.finditer(pattern, content))
        
        if len(matches) < 2:
            print(f"日志文件中找到的'--- 开始多线程通知任务 ---'数量不足（只有{len(matches)}个）")
            if len(matches) == 1:
                print("只有一次运行记录，将分析从程序开始到结束的全部日志")
                # 找到最后一个匹配位置之前的内容
                return content[:matches[0].start()]
            else:
                print("没有找到任何'--- 开始多线程通知任务 ---'标记")
                return ""
        
        # 获取最后两次之间的内容
        second_last_pos = matches[-2].start()
        last_pos = matches[-1].start()
        
        last_run_content = content[second_last_pos:last_pos]
        print(f"找到最后一次运行的日志，从位置{second_last_pos}到{last_pos}")
        
        return last_run_content
        
    except FileNotFoundError:
        print(f"错误：找不到日志文件 {log_file_path}")
        return ""
    except Exception as e:
        print(f"读取日志文件时出错：{e}")
        return ""

def analyze_while_loop_count(log_content: str) -> int:
    """
    分析while循环的次数
    
    根据代码分析，每次while循环都会：
    1. 先处理ECE334课程
    2. 再处理ECE311课程
    
    Args:
        log_content: 日志内容
        
    Returns:
        while循环的次数
    """
    
    # 方法1：通过ECE334的处理次数来统计（每次while循环都会先处理ECE334）
    # 查找ECE334相关的日志
    ece334_patterns = [
        r"Button clicked",  # 成功点击按钮
        r"Button not clicked",  # 按钮点击失败  
        r"Button not available"  # 按钮不可用
    ]
    
    ece334_count = 0
    lines = log_content.split('\n')
    
    # 查找每次ECE334处理的开始
    # 每次while循环开始时都会先处理ECE334
    in_ece334_processing = False
    
    for line in lines:
        # 检查是否包含ECE334相关的日志
        for pattern in ece334_patterns:
            if re.search(pattern, line):
                if not in_ece334_processing:
                    ece334_count += 1
                    in_ece334_processing = True
                    print(f"第{ece334_count}次while循环: {line.strip()}")
                break
        
        # 如果遇到ECE311的处理，说明ECE334处理完成
        if "ECE311" in line and in_ece334_processing:
            in_ece334_processing = False
    
    print(f"\n方法1 - 通过ECE334处理次数统计：{ece334_count}次while循环")
    
    # 方法2：通过"Button clicked"或"Button not available"等关键日志来统计
    # 每次while循环中，ECE334和ECE311各会产生一次这样的日志
    button_logs = []
    for line in lines:
        for pattern in ece334_patterns:
            if re.search(pattern, line):
                button_logs.append(line.strip())
                break
    
    # 由于每次while循环处理两门课（ECE334和ECE311），所以总日志数除以2
    total_button_logs = len(button_logs)
    estimated_loops = total_button_logs // 2
    
    print(f"方法2 - 通过按钮操作日志统计：共{total_button_logs}个按钮操作日志，估计{estimated_loops}次while循环")
    
    # 方法3：更精确的分析 - 查找每次循环的完整模式
    # 每次while循环的模式：ECE334处理 -> ECE311处理
    ece334_processed = False
    ece311_processed = False
    precise_count = 0
    
    for line in lines:
        # 检测ECE334处理
        if any(re.search(pattern, line) for pattern in ece334_patterns) and "ECE334" not in line:
            # 这里需要更精确的判断逻辑
            pass
            
        # 由于日志中可能不会明确标识是哪个课程的处理，我们使用方法1的结果
    
    return ece334_count

def main():
    """主函数"""
    log_file_path = "acorn_crawler_old.log"
    
    print("=== 日志分析器 ===")
    print(f"分析日志文件: {log_file_path}")
    print()
    
    # 获取最后一次运行的日志
    last_run_content = find_last_run_logs(log_file_path)
    
    if not last_run_content:
        print("无法获取最后一次运行的日志内容")
        return
    
    print(f"最后一次运行的日志长度: {len(last_run_content)} 字符")
    print("=" * 50)
    
    # 分析while循环次数
    loop_count = analyze_while_loop_count(last_run_content)
    
    print("=" * 50)
    print(f"🎯 结论：最后一次运行中，while循环执行了 {loop_count} 次")
    
    # 额外统计信息
    lines = last_run_content.split('\n')
    total_lines = len([line for line in lines if line.strip()])
    print(f"📊 统计信息：")
    print(f"   - 最后一次运行的日志总行数: {total_lines}")
    print(f"   - while循环次数: {loop_count}")
    if loop_count > 0:
        print(f"   - 平均每次循环产生日志行数: {total_lines // loop_count}")

if __name__ == "__main__":
    main() 