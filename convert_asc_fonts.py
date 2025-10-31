#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert ASC font files to JavaScript format
"""
import os
import struct

def convert_asc_to_js(font_file, height, width, output_file):
    """
    Convert ASC font file to JavaScript format
    
    Args:
        font_file: Path to the binary font file
        height: Font height in pixels
        width: Font width in pixels
        output_file: Output JavaScript file path
    """
    
    # Read the binary file
    with open(font_file, 'rb') as f:
        data = f.read()
    
    # Calculate bytes per character from file
    # Note: The original data uses column-major or row-major packing
    # For display, we need bytes in row-major format
    file_bytes_per_char = len(data) // 95  # 95 printable characters (ASCII 32-126)
    
    # Calculate bytes per row for display
    bytes_per_row = (width + 7) // 8  # Ceiling division
    bytes_per_char_display = bytes_per_row * height
    
    # Total number of printable characters in file (ASCII 32-126)
    total_printable_chars = 95
    
    # Array to store converted data
    js_data = []
    
    # Determine if column-major or row-major based on height
    # According to Num2Mat.java: height==12 or height==48 use row-major, else use column-major
    is_column_major = not (height == 12 or height == 48)
    
    # Process all 128 ASCII characters (0x00-0x7f)
    for ascii_code in range(128):
        # Determine if this is a printable character
        is_printable = 32 <= ascii_code < 127
        
        # Get character data
        if is_printable:
            # Calculate offset in bytes (only printable chars are in the file)
            file_char_index = ascii_code - 32
            offset = file_char_index * file_bytes_per_char
            
            # Get character data from file
            char_data = data[offset:offset + file_bytes_per_char]
        else:
            # Use all zeros for non-printable characters  
            char_data = bytes([0] * file_bytes_per_char)
        
        # Convert column-major to row-major if needed
        # For column-major: data is stored column by column
        # For row-major: data is stored row by row
        if is_column_major:
            # Convert column-major to row-major for display
            # Each bit represents: column j, row i at index = j * height + i
            # We need to reorder to: row i, column j at index = i * width + j
            reordered_data = bytearray([0] * bytes_per_char_display)
            
            for i in range(height):  # row
                for j in range(width):  # column
                    # Calculate bit position in column-major format
                    bit_index = j * height + i
                    
                    # Get byte and bit in source data
                    source_byte_idx = bit_index // 8
                    source_bit_idx = bit_index % 8
                    
                    # Get the bit value
                    source_byte = char_data[source_byte_idx] if source_byte_idx < len(char_data) else 0
                    bit_value = (source_byte >> (7 - source_bit_idx)) & 1
                    
                    # Calculate position in row-major format
                    dest_bit_index = i * width + j
                    dest_byte_idx = dest_bit_index // 8
                    dest_bit_idx = dest_bit_index % 8
                    
                    # Set the bit in destination
                    if bit_value:
                        reordered_data[dest_byte_idx] |= (1 << (7 - dest_bit_idx))
            
            char_data = bytes(reordered_data)
        
        # Convert to hex array
        hex_array = []
        
        # Process bytes
        for byte_val in char_data:
            hex_array.append(f'0x{byte_val:02x}')
        
        # Add comment with character info
        if ascii_code < 32:
            char_name = f'^{chr(ascii_code + 64)}'
        elif ascii_code == 0x7f:
            char_name = '.'
        else:
            char_name = chr(ascii_code)
        
        js_data.append(f'    /* {ascii_code} 0x{ascii_code:02x} \'{char_name}\' */')
        
        # Group by width (format output for readability)
        bytes_per_line = bytes_per_row
        
        for i in range(0, len(hex_array), bytes_per_line):
            line_hex = ", ".join(hex_array[i:i + bytes_per_line])
            
            # Decode bits for visualization
            bits_str = ""
            for j in range(i, min(i + bytes_per_line, len(hex_array))):
                byte_val = int(hex_array[j], 16)
                for k in range(7, -1, -1):
                    bits_str += "1" if (byte_val >> k) & 1 else "0"
            
            js_data.append(f'    {line_hex}, /* {bits_str} */')
        
        js_data.append("")  # Empty line between characters
    
    # Write JavaScript file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f'const font_{width}x{height} = {{\n')
        f.write(f'    width: {width},\n')
        f.write(f'    height: {height},\n')
        f.write(f'    bytesPerChar: {bytes_per_char_display},  // Each character uses {bytes_per_char_display} bytes ({width}x{height} bitmap, {bytes_per_row} byte(s) per row)\n')
        f.write(f'    data: [\n')
        f.write(f'    // Contains 128 characters (0x00-0x7f), non-printable chars set to 0\n')
        
        for line in js_data:
            f.write(line + '\n')
        
        f.write(f'    ]\n')
        f.write(f'  }};\n\n')
        f.write(f'// Export font data to global scope\n')
        f.write(f'window.font_{width}x{height} = font_{width}x{height};\n')
    
    print(f"Converted {font_file} to {output_file}")


def main():
    """Main function to convert all ASC font files"""
    
    base_dir = 'fonts/font_bin/ASC'
    
    # Define font specifications
    fonts = [
        ('ASC12_8', 12, 8),
        ('ASC16_8', 16, 8),
        ('ASC24_12', 24, 12),
        ('ASC32_16', 32, 16),
        ('ASC48_24', 48, 24),
    ]
    
    for font_name, height, width in fonts:
        input_file = os.path.join(base_dir, font_name)
        output_file = f'fonts/font_{width}x{height}.js'
        
        if os.path.exists(input_file):
            convert_asc_to_js(input_file, height, width, output_file)
        else:
            print(f"Warning: {input_file} not found")


if __name__ == '__main__':
    main()

