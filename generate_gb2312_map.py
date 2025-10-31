#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
生成GB2312到Unicode的映射表
输出为JSON格式，供JavaScript使用
"""

import json
import sys

def generate_gb2312_unicode_map():
    """生成GB2312编码到Unicode的映射表"""
    mapping = {}
    
    # GB2312包含94个区，每个区94个位
    # 区码范围: 1-94 (对应字节 0xA1-0xFE)
    # 位码范围: 1-94 (对应字节 0xA1-0xFE)
    
    for qu in range(1, 95):  # 区码 1-94
        for wei in range(1, 95):  # 位码 1-94
            try:
                # GB2312字节编码
                gb_byte1 = 0xA0 + qu
                gb_byte2 = 0xA0 + wei
                gb_bytes = bytes([gb_byte1, gb_byte2])
                
                # 转换为Unicode
                try:
                    unicode_char = gb_bytes.decode('gb2312')
                    if unicode_char:
                        unicode_code = ord(unicode_char)
                        # 存储: Unicode码点 -> GB2312字节
                        mapping[unicode_code] = [gb_byte1, gb_byte2]
                except UnicodeDecodeError:
                    # 某些区位码没有对应的字符
                    pass
            except Exception as e:
                pass
    
    return mapping

def main():
    print("Generating GB2312 to Unicode mapping...")
    
    mapping = generate_gb2312_unicode_map()
    
    print(f"Generated {len(mapping)} character mappings")
    
    # 保存为JSON文件
    output_file = "fonts/gb2312_unicode_map.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    
    print(f"Mapping saved to {output_file}")
    
    # 显示一些示例
    print("\nSample mappings:")
    samples = ['中', '国', '你', '好', 'A', '1']
    for char in samples:
        unicode_code = ord(char)
        if unicode_code in mapping:
            gb_bytes = mapping[unicode_code]
            print(f"  '{char}' (U+{unicode_code:04X}) -> GB2312 [0x{gb_bytes[0]:02X}, 0x{gb_bytes[1]:02X}]")
        else:
            # 尝试手动编码ASCII
            if unicode_code < 128:
                if 0x20 <= unicode_code <= 0x7E:
                    gb_bytes = [0xA3, 0xA0 + (unicode_code - 0x20)]
                    print(f"  '{char}' (U+{unicode_code:04X}) -> GB2312 [0x{gb_bytes[0]:02X}, 0x{gb_bytes[1]:02X}] (ASCII)")
            else:
                print(f"  '{char}' (U+{unicode_code:04X}) -> Not in GB2312")

if __name__ == "__main__":
    main()

