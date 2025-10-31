#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

class FontFile:
    """字模数据类"""
    CHARSET_ASCII = "ascii"
    CHARSET_GB2312 = "gb2312"

    # ANSI 颜色代码
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'bg_black': '\033[40m',
        'bg_red': '\033[41m',
        'bg_white': '\033[47m',
    }

    def __init__(self, charset, width, height, file_path):
        self.charset = charset
        self.width = width
        self.height = height
        self.file_path = file_path
        # 字模数据大小, 宽度每8位一字节, 不足8位也占一字节
        self.bytes_per_line = (width + 7) // 8
        self.font_code_size = self.bytes_per_line * height

    def get_font_data(self, char):
        """获取字模数据"""
        if self.charset == self.CHARSET_ASCII:
            return self.get_ascii_font_data(char)
        elif self.charset == self.CHARSET_GB2312:
            return self.get_gb2312_font_data(char)
        else:
            raise ValueError(f"不支持的字符集: {self.charset}")

    def _read_font_data(self, offset):
        """从字库文件中读取字模数据"""
        try:
            with open(self.file_path, 'rb') as f:
                f.seek(offset)
                font_data = f.read(self.font_code_size)
                return font_data
        except Exception as e:
            print(f"读取字模数据失败: {e}")
            return None

    def _get_gb2312_bytes(self, char):
        """获取GB2312编码字节"""
        try:
            if ord(char) < 128:  # ASCII字符
                # ASCII字符在GB2312中的位置是 0xA1 + ASCII码
                # 比如'A'(0x41) 在GB2312中的编码是 0xA1E1
                return bytes([0xA3, 0xA3 + ord(char) - 35])
            else:  # 汉字
                return char.encode('gb2312')
        except UnicodeEncodeError:
            print(f"警告: 字符 '{char}' 无法用GB2312编码")
            return None

    def _calculate_gb2312_offset(self, gb_bytes):
        """计算字符在GB2312中的偏移量"""
        if len(gb_bytes) != 2:
            return None
        
        t1 = gb_bytes[0]
        t2 = gb_bytes[1]
        
        # HZK40和HZK48字库跳过了前15个区（只包含繁体字，从第16区开始）
        # 参考Java代码: offset = ((t1 - 0xa1 - 0x0f) * 94 + (t2 - 0xa1)) * offset_step
        if self.width == 40 or self.width == 48:
            # 对于40和48尺寸，跳过前15个区（0x0F = 15）
            offset = ((t1 - 0xA1 - 0x0F) * 94 + (t2 - 0xA1)) * self.font_code_size
        else:
            # 对于12, 16, 24, 32尺寸，使用标准GB2312偏移计算
            # 计算区码和位码
            qu = t1 - 0xA0
            wei = t2 - 0xA0
            offset = (94 * (qu - 1) + (wei - 1)) * self.font_code_size
        
        return offset

    def get_ascii_font_data(self, char):
        """获取ASCII字模数据"""
        return None

    def get_gb2312_font_data(self, char):
        """获取GB2312字模数据"""
        gb_bytes = self._get_gb2312_bytes(char)
        if gb_bytes is None:
            return None
        offset = self._calculate_gb2312_offset(gb_bytes)
        if offset is None:
            return None
        return self._read_font_data(offset)
    
    def print_font_array(self, font_data):
        """打印字模数据"""
        print(f"const uint8_t font_data[{self.font_code_size}] = {{")
        for i in range(0, self.font_code_size, 8):
            hex_str = ", ".join(f"0x{b:02X}" for b in font_data[i:i+8])
            print(f"    {hex_str}" + ("," if i < self.font_code_size - 8 else ""))
        print("};")

    def _print_horizontal_scale(self):
        """打印水平坐标"""
        # 打印列号 (十位数)
        print("     ", end="")
        for i in range(self.width):
            print(f"{i//10 if i >= 10 else ' '} ", end="")
        print()
        # 打印列号 (个位数)
        print("     ", end="")
        for i in range(self.width):
            print(f"{i%10} ", end="")
        print()
        # 打印分隔线
        print("    +" + "-" * (self.width * 2 + 1) + "+")

    def print_font_pattern(self, font_data):
        """打印点阵显示（带网格和坐标）"""
        # 打印水平坐标
        self._print_horizontal_scale()

        # 打印每一行
        for row in range(self.height):
            # 打印行号
            print(f"{row:3d} |", end=" ")
            
            # 打印该行的点阵数据
            for col_byte in range(self.bytes_per_line):
                byte = font_data[row * self.bytes_per_line + col_byte]
                # 对于每个字节中的每一位
                for bit in range(8):
                    # 如果已经超出字体宽度，跳过剩余位
                    if col_byte * 8 + bit >= self.width:
                        break
                    # 使用不同的字符显示点和空白
                    if byte & (0x80 >> bit):
                        print("██", end="")
                    else:
                        print("[]", end="")
            print(" |")  # 行尾边框

        # 打印底部分隔线
        print("    +" + "-" * (self.width * 2 + 1) + "+")

        # 打印图例
        print("\n图例:")
        print("██ 表示点阵中的点")
        print("[] 表示空白位置")
        print("坐标格式: [行号, 列号], 从0开始计数")

    def dump_char(self, char):
        """打印字符的点阵数据"""
        print(f"\n字符: '{char}' (UNICODE: {ord(char)} / 0x{ord(char):04X})")

        if self.charset != self.CHARSET_GB2312:
            return

        gb_bytes = self._get_gb2312_bytes(char)
        if gb_bytes is None:
            return
        
        print(f"GB2312编码: {' '.join(f'0x{b:02X}' for b in gb_bytes)}")

        offset = self._calculate_gb2312_offset(gb_bytes)
        if offset is None:
            return
        
        print(f"字库偏移: {offset} (0x{offset:X})")

        font_data = self._read_font_data(offset)
        if font_data is None:
            return

        print("\n字模数据:")
        self.print_font_array(font_data)

        print("\n点阵显示:")
        self.print_font_pattern(font_data)

    def dump_text(self, text):
        """打印文本的点阵数据"""
        for char in text:
            self.dump_char(char)


def main():
    # 创建一个字体字典，支持多种字体
    fonts = {
        "HZK12-1": FontFile(FontFile.CHARSET_GB2312, 12, 12, "fonts/hzk1/HZK12"),
        "HZK16-1": FontFile(FontFile.CHARSET_GB2312, 16, 16, "fonts/hzk1/HZK16"),
        "HZK12": FontFile(FontFile.CHARSET_GB2312, 12, 12, "fonts/hzk2/HZK12"),
        "HZK16": FontFile(FontFile.CHARSET_GB2312, 16, 16, "fonts/hzk2/HZK16"),
        "HZK24": FontFile(FontFile.CHARSET_GB2312, 24, 24, "fonts/hzk2/HZK24"),
        "HZK32": FontFile(FontFile.CHARSET_GB2312, 32, 32, "fonts/hzk2/HZK32"),
        "HZK40": FontFile(FontFile.CHARSET_GB2312, 40, 40, "fonts/hzk2/HZK40"),
        "HZK48": FontFile(FontFile.CHARSET_GB2312, 48, 48, "fonts/hzk2/HZK48"),
    }

    # 检查命令行参数
    if len(sys.argv) != 3:
        print(f"用法: {sys.argv[0]} <字体名称> <要显示的文字>")
        print("支持的字体:", ", ".join(fonts.keys()))
        sys.exit(1)

    font_name = sys.argv[1]
    text = sys.argv[2]

    # 检查字体是否支持
    if font_name not in fonts:
        print(f"错误: 不支持的字体 '{font_name}'")
        print("支持的字体:", ", ".join(fonts.keys()))
        sys.exit(1)

    # 检查字体文件是否存在
    font = fonts[font_name]
    if not os.path.exists(font.file_path):
        print(f"错误: 找不到字库文件: {font.file_path}")
        sys.exit(1)

    # 显示文字
    font.dump_text(text)


if __name__ == "__main__":
    main()

