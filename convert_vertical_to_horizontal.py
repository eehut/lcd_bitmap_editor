#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将纵向取模的字库文件转换为横向取模
支持不同大小的字库（HZK16, HZK24等）
"""

import sys
import os

def calculate_font_size(width, height):
    """计算单个字符的字模大小（字节数）"""
    bytes_per_line = (width + 7) // 8
    return bytes_per_line * height

def decode_vertical_pattern(data, width, height):
    """
    纵向取模解码：从上到下，从左到右
    返回一个二维数组，[行][列] = 0或1
    """
    bytes_per_column = (height + 7) // 8
    pattern = []
    
    for row in range(height):
        line = []
        for col in range(width):
            # 计算字节索引：第col列的字节索引
            col_byte_idx = col * bytes_per_column + (row // 8)
            bit_in_byte = row % 8
            
            if col_byte_idx < len(data):
                byte = data[col_byte_idx]
                val = byte & (0x80 >> bit_in_byte)
            else:
                val = 0
            line.append(1 if val else 0)
        pattern.append(line)
    
    return pattern

def encode_horizontal_pattern(pattern, width, height):
    """
    横向取模编码：从左到右，从上到下
    输入：二维数组 [行][列]
    输出：字节数组
    """
    bytes_per_line = (width + 7) // 8
    result = bytearray()
    
    for row in range(height):
        for col_byte in range(bytes_per_line):
            byte_val = 0
            for bit in range(8):
                col = col_byte * 8 + bit
                if col < width and pattern[row][col]:
                    byte_val |= (0x80 >> bit)
            result.append(byte_val)
    
    return bytes(result)

def calculate_gb2312_offset(gb_bytes, font_size):
    """计算字符在GB2312中的偏移量"""
    if len(gb_bytes) != 2:
        return None
    qu = gb_bytes[0] - 0xA0
    wei = gb_bytes[1] - 0xA0
    offset = (94 * (qu - 1) + (wei - 1)) * font_size
    return offset

def convert_font_file(input_file, output_file, width, height):
    """
    转换字库文件从纵向取模到横向取模
    
    Args:
        input_file: 输入文件路径（纵向取模）
        output_file: 输出文件路径（横向取模）
        width: 字符宽度
        height: 字符高度
    """
    if not os.path.exists(input_file):
        print(f"错误: 找不到输入文件: {input_file}")
        return False
    
    font_size = calculate_font_size(width, height)
    print(f"字符尺寸: {width}x{height}")
    print(f"每字符字节数: {font_size}")
    
    # 计算文件大小
    file_size = os.path.getsize(input_file)
    num_chars = file_size // font_size
    print(f"输入文件大小: {file_size} 字节")
    print(f"字符数量: {num_chars}")
    
    if file_size % font_size != 0:
        print(f"警告: 文件大小 ({file_size}) 不是字符大小的整数倍，可能会有数据丢失")
    
    # GB2312字符集范围
    # 区码: 0xA1-0xFE (94个区)
    # 位码: 0xA1-0xFE (94个位)
    total_expected = 94 * 94 * font_size
    if num_chars < 94 * 94:
        print(f"警告: 字符数量 ({num_chars}) 少于预期的 GB2312 字符数 (8836)")
    
    # 打开文件
    with open(input_file, 'rb') as fin, open(output_file, 'wb') as fout:
        converted_count = 0
        
        # 逐字符处理
        for char_idx in range(num_chars):
            # 读取纵向取模数据
            offset = char_idx * font_size
            fin.seek(offset)
            vertical_data = fin.read(font_size)
            
            if len(vertical_data) < font_size:
                break
            
            # 解码为点阵模式
            pattern = decode_vertical_pattern(vertical_data, width, height)
            
            # 编码为横向取模
            horizontal_data = encode_horizontal_pattern(pattern, width, height)
            
            # 写入输出文件
            fout.write(horizontal_data)
            converted_count += 1
            
            # 显示进度
            if (char_idx + 1) % 1000 == 0:
                progress = (char_idx + 1) * 100 // num_chars
                print(f"进度: {char_idx + 1}/{num_chars} ({progress}%)")
    
    print(f"\n转换完成!")
    print(f"转换字符数: {converted_count}")
    print(f"输出文件: {output_file}")
    
    # 验证输出文件大小
    output_size = os.path.getsize(output_file)
    expected_size = converted_count * font_size
    if output_size == expected_size:
        print(f"输出文件大小验证通过: {output_size} 字节")
    else:
        print(f"警告: 输出文件大小 ({output_size}) 与预期 ({expected_size}) 不匹配")
    
    return True

def verify_conversion(input_file, output_file, width, height, test_chars="我"):
    """
    验证转换结果
    """
    print(f"\n验证转换结果 (测试字符: '{test_chars}'):")
    print("-" * 60)
    
    font_size = calculate_font_size(width, height)
    
    for char in test_chars:
        try:
            if ord(char) < 128:
                gb_bytes = bytes([0xA3, 0xA3 + ord(char) - 35])
            else:
                gb_bytes = char.encode('gb2312')
        except:
            print(f"  跳过字符 '{char}' (无法用GB2312编码)")
            continue
        
        offset = calculate_gb2312_offset(gb_bytes, font_size)
        if offset is None:
            continue
        
        # 读取原始数据
        with open(input_file, 'rb') as f:
            f.seek(offset)
            original_data = f.read(font_size)
        
        # 读取转换后数据
        with open(output_file, 'rb') as f:
            f.seek(offset)
            converted_data = f.read(font_size)
        
        # 解码并显示
        pattern_original = decode_vertical_pattern(original_data, width, height)
        pattern_converted = decode_vertical_pattern(converted_data, width, height)
        
        print(f"\n字符: '{char}'")
        print("原始 (纵向解码):")
        for i, row in enumerate(pattern_original):
            line = "".join("██" if bit else "[]" for bit in row[:16])
            print(f"  {i:2d}: {line}")
        
        print("转换后 (应该用横向解码):")
        # 用横向方式解码转换后的数据
        bytes_per_line = (width + 7) // 8
        print("  ", end="")
        for col in range(min(width, 16)):
            print(f"{col%10}", end=" ")
        print()
        for row in range(height):
            print(f"  {row:2d}:", end=" ")
            for col_byte in range(bytes_per_line):
                byte = converted_data[row * bytes_per_line + col_byte]
                for bit in range(8):
                    if col_byte * 8 + bit >= width:
                        break
                    val = byte & (0x80 >> bit)
                    print("██" if val else "[]", end="")
            print()

def main():
    """主函数"""
    if len(sys.argv) < 4:
        print("用法:")
        print("  单个文件: convert_vertical_to_horizontal.py <输入文件> <输出文件> <宽度> <高度> [验证字符]")
        print("  批量转换: convert_vertical_to_horizontal.py --batch")
        print("\n示例:")
        print("  python3 convert_vertical_to_horizontal.py fonts/HZK16_1 fonts/HZK16_converted 16 16")
        print("  python3 convert_vertical_to_horizontal.py fonts/HZK24 fonts/HZK24_converted 24 24 '我'")
        print("\n批量转换预设:")
        print("  - HZK16_1 (16x16) -> HZK16_converted")
        print("  - HZK24 (24x24) -> HZK24_converted (如果存在)")
        sys.exit(1)
    
    # 批量转换模式
    if len(sys.argv) == 2 and sys.argv[1] == "--batch":
        batch_convert()
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    width = int(sys.argv[3])
    height = int(sys.argv[4])
    verify_chars = sys.argv[5] if len(sys.argv) > 5 else "我"
    
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")
    print(f"字符尺寸: {width}x{height}")
    print("-" * 60)
    
    # 执行转换
    if convert_font_file(input_file, output_file, width, height):
        # 验证转换结果
        verify_conversion(input_file, output_file, width, height, verify_chars)
        print("\n转换和验证完成!")

def batch_convert():
    """批量转换预设的字库文件"""
    print("批量转换模式")
    print("=" * 60)
    
    # 定义要转换的字库
    fonts_to_convert = [
        ("fonts/HZK16_1", "fonts/HZK16_converted", 16, 16),
        # 如果需要转换HZK24，取消下面的注释
        # ("fonts/HZK24", "fonts/HZK24_converted", 24, 24),
    ]
    
    for input_file, output_file, width, height in fonts_to_convert:
        if not os.path.exists(input_file):
            print(f"\n跳过 {input_file} (文件不存在)")
            continue
        
        print(f"\n处理: {input_file} -> {output_file}")
        print(f"尺寸: {width}x{height}")
        print("-" * 60)
        
        if convert_font_file(input_file, output_file, width, height):
            print(f"✓ {output_file} 转换成功")
        else:
            print(f"✗ {input_file} 转换失败")
    
    print("\n" + "=" * 60)
    print("批量转换完成!")

if __name__ == "__main__":
    main()

