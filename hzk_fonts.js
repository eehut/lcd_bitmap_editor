/**
 * 汉字字库(HZK)处理模块
 * 支持从HZK字库文件中提取汉字点阵数据
 */

// 汉字字库类
class HZKFont {
    constructor(name, width, height, filePath) {
        this.name = name;
        this.width = width;
        this.height = height;
        this.filePath = filePath;
        this.charset = 'gb2312';
        
        // 计算字模数据大小
        this.bytesPerLine = Math.ceil(width / 8);
        this.bytesPerChar = this.bytesPerLine * height;
        
        // 字库数据缓存
        this.fontData = null;
        this.isLoaded = false;
    }

    /**
     * 加载字库文件
     */
    async load() {
        if (this.isLoaded) {
            return true;
        }

        try {
            console.log(`Loading HZK font: ${this.name} from ${this.filePath}`);
            const response = await fetch(this.filePath);
            if (!response.ok) {
                throw new Error(`Failed to load font file: ${response.statusText}`);
            }
            
            this.fontData = await response.arrayBuffer();
            this.isLoaded = true;
            console.log(`HZK font ${this.name} loaded: ${this.fontData.byteLength} bytes`);
            return true;
        } catch (error) {
            console.error(`Error loading HZK font ${this.name}:`, error);
            this.isLoaded = false;
            return false;
        }
    }

    /**
     * 计算GB2312字符在字库中的偏移量
     * @param {Uint8Array} gbBytes - GB2312编码字节 [高字节, 低字节]
     * @returns {number|null} - 字库偏移量
     */
    calculateOffset(gbBytes) {
        if (!gbBytes || gbBytes.length !== 2) {
            return null;
        }

        const t1 = gbBytes[0];
        const t2 = gbBytes[1];

        // HZK40和HZK48字库跳过了前15个区（只包含繁体字，从第16区开始）
        if (this.width === 40 || this.width === 48) {
            // 对于40和48尺寸，跳过前15个区（0x0F = 15）
            const offset = ((t1 - 0xA1 - 0x0F) * 94 + (t2 - 0xA1)) * this.bytesPerChar;
            return offset;
        } else {
            // 对于12, 16, 24, 32尺寸，使用标准GB2312偏移计算
            // 计算区码和位码
            const qu = t1 - 0xA0;
            const wei = t2 - 0xA0;
            const offset = (94 * (qu - 1) + (wei - 1)) * this.bytesPerChar;
            return offset;
        }
    }

    /**
     * 获取字符的字模数据
     * @param {string} char - 要获取字模的字符
     * @returns {Uint8Array|null} - 字模数据
     */
    getCharData(char) {
        if (!this.isLoaded || !this.fontData) {
            console.error(`Font ${this.name} not loaded`);
            return null;
        }

        // 获取GB2312编码
        const gbBytes = gb2312Encoder.encodeChar(char);
        if (!gbBytes) {
            console.warn(`Failed to encode character '${char}' to GB2312`);
            return null;
        }

        // 计算偏移量
        const offset = this.calculateOffset(gbBytes);
        if (offset === null || offset < 0) {
            console.warn(`Invalid offset for character '${char}'`);
            return null;
        }

        // 检查偏移量是否在文件范围内
        if (offset + this.bytesPerChar > this.fontData.byteLength) {
            console.warn(`Offset ${offset} out of range for character '${char}' in font ${this.name}`);
            return null;
        }

        // 提取字模数据
        const charData = new Uint8Array(this.fontData, offset, this.bytesPerChar);
        return charData;
    }

    /**
     * 将字符绘制到位图
     * @param {Array} bitmap - 位图数组
     * @param {string} char - 要绘制的字符
     * @param {number} x - X坐标
     * @param {number} y - Y坐标
     * @param {boolean} invert - 是否反显
     * @returns {boolean} - 是否成功绘制
     */
    drawChar(bitmap, char, x, y, invert = false) {
        const charData = this.getCharData(char);
        if (!charData) {
            return false;
        }

        const canvasWidth = bitmap[0].length;
        const canvasHeight = bitmap.length;

        // 绘制字符
        for (let row = 0; row < this.height; row++) {
            const rowStartIndex = row * this.bytesPerLine;
            
            for (let col = 0; col < this.width; col++) {
                // 计算当前像素位于哪个字节
                const byteIndex = rowStartIndex + Math.floor(col / 8);
                // 计算当前像素在字节中的位置（从MSB开始）
                const bitPosition = 7 - (col % 8);
                
                // 从对应字节中提取位值
                const byte = charData[byteIndex] || 0;
                const bit = (byte >> bitPosition) & 0x01;
                
                // 设置位图像素
                const targetX = x + col;
                const targetY = y + row;
                if (targetX >= 0 && targetX < canvasWidth && targetY >= 0 && targetY < canvasHeight) {
                    bitmap[targetY][targetX] = invert ? !bit : bit;
                }
            }
        }

        return true;
    }
}

// 汉字字库管理器
class HZKFontManager {
    constructor() {
        this.fonts = {};
        this.currentFont = null;
    }

    /**
     * 注册字库
     */
    registerFont(name, width, height, filePath) {
        const font = new HZKFont(name, width, height, filePath);
        this.fonts[name] = font;
        return font;
    }

    /**
     * 获取字库
     */
    getFont(name) {
        return this.fonts[name] || null;
    }

    /**
     * 获取所有已注册的字库名称
     */
    getFontNames() {
        return Object.keys(this.fonts);
    }

    /**
     * 设置当前使用的字库
     */
    async setCurrentFont(name) {
        const font = this.getFont(name);
        if (!font) {
            console.error(`Font ${name} not found`);
            return false;
        }

        if (!font.isLoaded) {
            const loaded = await font.load();
            if (!loaded) {
                return false;
            }
        }

        this.currentFont = font;
        console.log(`Current HZK font set to: ${name}`);
        return true;
    }

    /**
     * 获取当前字库
     */
    getCurrentFont() {
        return this.currentFont;
    }
}

// 创建全局字库管理器
const hzkFontManager = new HZKFontManager();

// 注册所有可用的汉字字库
hzkFontManager.registerFont('HZK12', 12, 12, 'fonts/hzk2/HZK12');
hzkFontManager.registerFont('HZK16', 16, 16, 'fonts/hzk2/HZK16');
hzkFontManager.registerFont('HZK24', 24, 24, 'fonts/hzk2/HZK24');
hzkFontManager.registerFont('HZK32', 32, 32, 'fonts/hzk2/HZK32');
hzkFontManager.registerFont('HZK40', 40, 40, 'fonts/hzk2/HZK40');
hzkFontManager.registerFont('HZK48', 48, 48, 'fonts/hzk2/HZK48');

console.log('HZK font manager initialized with fonts:', hzkFontManager.getFontNames().join(', '));

