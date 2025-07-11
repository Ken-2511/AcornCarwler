#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进的日志分析器 - 更准确地统计最后一次运行中while循环的次数
"""

import re
from datetime import datetime

def find_last_run_logs(log_file_path: str) -> str:
    """找到最后一次运行的日志内容"""
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

def analyze_while_loop_count_improved(log_content: str) -> int:
    """
    改进的while循环次数分析
    
    根据代码分析，每次while循环都按顺序执行：
    1. 处理ECE334课程（产生Button相关日志）
    2. random_sleep()
    3. 处理ECE311课程（产生Button相关日志）  
    4. random_sleep()
    5. 检查fail_count，如果>=1则退出
    
    我们通过分析日志的时间序列和模式来判断循环次数
    """
    
    lines = log_content.split('\n')
    
    # 提取所有相关的日志行，包含时间戳
    button_logs = []
    for line in lines:
        if any(keyword in line for keyword in ["Button clicked", "Button not clicked", "Button not available"]):
            button_logs.append(line.strip())
    
    print(f"找到 {len(button_logs)} 个按钮相关的日志")
    
    # 由于每次while循环会处理两门课程（ECE334和ECE311），
    # 所以每次循环会产生2个按钮相关的日志
    estimated_loops_method1 = len(button_logs) // 2
    
    # 方法2：通过"Button not available"来分析
    # 如果按钮不可用，程序会记录"Button not available"并增加fail_count
    # 当fail_count >= 1时程序退出，这意味着最后一次出现"Button not available"时程序就退出了
    not_available_logs = []
    for line in lines:
        if "Button not available" in line:
            not_available_logs.append(line.strip())
    
    print(f"找到 {len(not_available_logs)} 个'Button not available'日志")
    
    # 方法3：通过"Extracted"日志来分析
    # 每次check_and_secure_course函数中，会对每个PRA调用span_element.text并记录"Extracted XXX"
    # ECE334有2个PRA，ECE311有2个PRA，所以每次while循环会产生4个"Extracted"日志
    extracted_logs = []
    for line in lines:
        if "Extracted" in line:
            extracted_logs.append(line.strip())
    
    print(f"找到 {len(extracted_logs)} 个'Extracted'日志")
    estimated_loops_method3 = len(extracted_logs) // 4  # 每次循环4个Extracted日志
    
    # 显示具体的日志
    print("\n=== 按钮相关日志分析 ===")
    for i, log in enumerate(button_logs[:10]):  # 只显示前10个
        print(f"{i+1:2d}: {log}")
    if len(button_logs) > 10:
        print(f"... 还有 {len(button_logs)-10} 个日志")
    
    print(f"\n=== 分析结果 ===")
    print(f"方法1 - 按钮日志总数除以2: {estimated_loops_method1} 次循环")
    print(f"方法2 - Button not available数量: {len(not_available_logs)} 次")
    print(f"方法3 - Extracted日志总数除以4: {estimated_loops_method3} 次循环")
    
    # 最终判断：使用方法3（Extracted日志）作为最准确的方法
    # 因为每次while循环都会产生固定数量的Extracted日志
    final_count = estimated_loops_method3
    
    return final_count

def analyze_program_exit_reason(log_content: str):
    """分析程序退出的原因"""
    lines = log_content.split('\n')
    
    print("\n=== 程序退出原因分析 ===")
    
    # 查找CAPTCHA相关日志
    captcha_logs = [line for line in lines if "CAPTCHA" in line]
    if captcha_logs:
        print("发现CAPTCHA相关日志：")
        for log in captcha_logs:
            print(f"  {log.strip()}")
    
    # 查找fail_count相关的线索
    not_available_count = len([line for line in lines if "Button not available" in line])
    print(f"Button not available出现次数: {not_available_count}")
    
    # 查找程序最后的日志
    last_logs = [line.strip() for line in lines[-20:] if line.strip()]
    print("\n最后的几条日志：")
    for log in last_logs[-5:]:
        print(f"  {log}")

def main():
    """主函数"""
    log_file_path = "acorn_crawler_old.log"
    
    print("=== 改进的日志分析器 ===")
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
    loop_count = analyze_while_loop_count_improved(last_run_content)
    
    # 分析程序退出原因
    analyze_program_exit_reason(last_run_content)
    
    print("=" * 50)
    print(f"🎯 最终结论：最后一次运行中，while循环执行了 {loop_count} 次")
    
    # 额外统计信息
    lines = last_run_content.split('\n')
    total_lines = len([line for line in lines if line.strip()])
    print(f"\n📊 详细统计：")
    print(f"   - 最后一次运行的日志总行数: {total_lines}")
    print(f"   - while循环次数: {loop_count}")
    if loop_count > 0:
        print(f"   - 平均每次循环产生日志行数: {total_lines // loop_count}")

if __name__ == "__main__":
    main() 