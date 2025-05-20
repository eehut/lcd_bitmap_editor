/**
 * 从C语言字体文件转换的JavaScript字体库
 */

// 字体对象定义
const LCDFont = {
  // 通用方法 - 获取字符在字体数据中的索引位置
  getCharIndex: function(fontData, char) {
    const code = char.charCodeAt(0);
    return code * fontData.bytesPerChar;
  },

  // 渲染字符到canvas上下文
  renderChar: function(ctx, fontData, char, x, y, color = '#000000', bgColor = null, pixelSize = 1) {
    const code = char.charCodeAt(0);
    const index = this.getCharIndex(fontData, char);
    
    // 获取字符数据
    const charData = fontData.data.slice(index, index + fontData.bytesPerChar);
    
    // 计算每行需要的字节数（向上取整）
    const bytesPerRow = Math.ceil(fontData.width / 8);
    
    // 绘制字符
    for (let row = 0; row < fontData.height; row++) {
      // 计算这一行的起始索引
      const rowStartIndex = row * bytesPerRow;
      
      // 处理这一行的每一列（像素）
      for (let col = 0; col < fontData.width; col++) {
        // 计算当前像素位于哪个字节
        const byteIndex = rowStartIndex + Math.floor(col / 8);
        // 计算当前像素在字节中的位置（从MSB开始）
        const bitPosition = 7 - (col % 8);
        
        // 从对应字节中提取位值
        const byte = charData[byteIndex] || 0; // 防止越界
        const bit = (byte >> bitPosition) & 0x01;
        
        // 绘制像素
        if (bit || bgColor !== null) {
          ctx.fillStyle = bit ? color : bgColor;
          ctx.fillRect(x + col * pixelSize, y + row * pixelSize, pixelSize, pixelSize);
        }
      }
    }
    
    // 返回下一个字符的x位置
    return x + fontData.width * pixelSize;
  },

  // 渲染文本到canvas上下文
  renderText: function(ctx, fontData, text, x, y, color = '#000000', bgColor = null, spacing = 0, pixelSize = 1) {
    let currentX = x;
    
    for (let i = 0; i < text.length; i++) {
      currentX = this.renderChar(ctx, fontData, text[i], currentX, y, color, bgColor, pixelSize);
      currentX += spacing; // 字符间距
    }
    
    return currentX;
  }
};


// 导出字体对象
window.LCDFont = LCDFont;
