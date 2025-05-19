# LCD 位图字体库

这是一个简单的 JavaScript 实现的 LCD 位图字体库，从 C 语言的字体数据转换而来。它支持在 HTML Canvas 上渲染单色位图字体。

## 支持的字体

- `font_8x8`: 8x8 像素字体
- `font_8x16`: 8x16 像素字体
- `font_10x18`: 10x18 像素字体（注意：每行使用 1.25 字节，即第一个字节的[7:0]位和第二个字节的[7:6]位）

## 使用方法

### 1. 引入字体库

```html
<script src="fonts.js"></script>
```

### 2. 使用 API 渲染文本

```javascript
// 获取 canvas 上下文
const canvas = document.getElementById('myCanvas');
const ctx = canvas.getContext('2d');

// 渲染单个字符
const x = 10; // 起始 x 坐标
const y = 10; // 起始 y 坐标
const char = 'A';
const color = '#000000'; // 文本颜色
const bgColor = '#ffffff'; // 背景颜色 (可选)
const nextX = LCDFont.renderChar(ctx, font_8x8, char, x, y, color, bgColor);

// 渲染文本
const text = "Hello, LCD!";
const spacing = 1; // 字符间距 (像素)
LCDFont.renderText(ctx, font_8x8, text, x, y, color, bgColor, spacing);
```

### 3. 像素大小调整

默认情况下，每个字体像素渲染为 Canvas 上的一个像素。你可以通过传递自定义的渲染函数来调整像素大小：

```javascript
// 在 demo.html 和 index.html 中有更详细的像素大小调整示例
```

## 演示页面

- `index.html`: 提供了一个完整的交互式界面，允许选择字体、颜色和像素大小。
- `demo.html`: 简单演示各种字体的渲染效果。

## 注意事项

- 10x18 字体的处理方式特殊，每行使用 2 个字节存储 10 位数据。
- 默认只包括标准 ASCII 字符 (0-127)，可以根据需要扩展字体数据。

## 原始 C 语言结构

原始 C 语言字体数据是通过 `LCD_FONT_DATA_DEFINE` 和 `LCD_ASCII_FONT_DEFINE` 宏定义的，JavaScript 版本已经将这些数据提取并组织为易于使用的对象。

