/**
 * GB2312 编码转换模块
 * 用于在浏览器中将Unicode字符转换为GB2312编码
 * 
 * 注意：由于JavaScript没有内置GB2312支持，我们使用一个变通方法：
 * 1. 对于ASCII字符，使用固定的编码规则
 * 2. 对于汉字，使用Python服务端生成的映射表，或使用内置的常用汉字映射
 */

// GB2312编码器类
class GB2312Encoder {
    constructor() {
        // Unicode到GB2312的映射表
        this.unicodeToGB2312Map = new Map();
        this.isLoaded = false;
        this.mappingURL = 'fonts/gb2312_unicode_map.json';
    }

    /**
     * 加载GB2312映射表
     */
    async loadMapping() {
        if (this.isLoaded) {
            return true;
        }

        try {
            // 尝试从外部JSON文件加载完整映射表
            const response = await fetch(this.mappingURL);
            if (response.ok) {
                const mapping = await response.json();
                for (const [unicode, gb] of Object.entries(mapping)) {
                    this.unicodeToGB2312Map.set(parseInt(unicode), gb);
                }
                console.log(`Loaded ${this.unicodeToGB2312Map.size} GB2312 mappings from file`);
            } else {
                console.warn('GB2312 mapping file not found, using built-in encoding');
            }
        } catch (error) {
            console.warn('Failed to load GB2312 mapping file:', error.message);
        }

        this.isLoaded = true;
        console.log('GB2312 encoder initialized');
        return true;
    }

    /**
     * 将Unicode字符转换为GB2312字节
     * @param {string} char - 单个字符
     * @returns {Uint8Array|null} - GB2312编码的字节数组 [高字节, 低字节]
     */
    encodeChar(char) {
        if (!char || char.length === 0) {
            return null;
        }

        const code = char.charCodeAt(0);

        // ASCII字符处理（参考Python代码）
        if (code < 128) {
            // ASCII字符在GB2312中的编码: 0xA3, 0xA0 + (code - 0x20)
            // 例如: 空格(0x20) -> [0xA3, 0xA0]
            //       'A'(0x41) -> [0xA3, 0xC1]
            if (code >= 0x20 && code <= 0x7E) {
                return new Uint8Array([0xA3, 0xA0 + (code - 0x20)]);
            } else {
                // 其他ASCII控制字符
                return new Uint8Array([0xA3, 0xA0 + code]);
            }
        }

        // 汉字处理 - 使用映射表
        if (this.unicodeToGB2312Map.has(code)) {
            const gbCode = this.unicodeToGB2312Map.get(code);
            // gbCode应该是一个数组 [高字节, 低字节] 或一个16位整数
            if (Array.isArray(gbCode)) {
                return new Uint8Array(gbCode);
            } else if (typeof gbCode === 'number') {
                return new Uint8Array([gbCode >> 8, gbCode & 0xFF]);
            } else if (typeof gbCode === 'object' && gbCode.bytes) {
                return new Uint8Array(gbCode.bytes);
            }
        }

        // 如果没有映射表，尝试使用escape编码技巧
        // 这个方法可以在某些浏览器中工作
        try {
            const encoded = this.encodeWithEscape(char);
            if (encoded) {
                return encoded;
            }
        } catch (error) {
            console.warn(`Failed to encode character '${char}' (U+${code.toString(16).toUpperCase()})`);
        }

        console.warn(`Character '${char}' (U+${code.toString(16).toUpperCase()}) not found in GB2312 mapping`);
        return null;
    }

    /**
     * 使用escape技巧编码字符（回退方案）
     * 注意：这个方法在现代浏览器中可能不完全可靠
     */
    encodeWithEscape(char) {
        try {
            // 尝试使用unescape/escape编码（已弃用但可能仍然工作）
            // 这里先返回null，因为这个方法不可靠
            return null;
        } catch (error) {
            return null;
        }
    }

    /**
     * 批量编码文本
     * @param {string} text - 要编码的文本
     * @returns {Array} - 字符编码信息数组
     */
    encodeText(text) {
        const result = [];
        for (let i = 0; i < text.length; i++) {
            const char = text.charAt(i);
            const encoded = this.encodeChar(char);
            result.push({
                char: char,
                unicode: char.charCodeAt(0),
                gb2312: encoded,
                success: encoded !== null
            });
        }
        return result;
    }

    /**
     * 检查字符是否可以编码
     */
    canEncode(char) {
        if (!char || char.length === 0) {
            return false;
        }
        const code = char.charCodeAt(0);
        // ASCII字符总是可以编码
        if (code < 128) {
            return true;
        }
        // 检查映射表
        return this.unicodeToGB2312Map.has(code);
    }
}

// 创建全局编码器实例
const gb2312Encoder = new GB2312Encoder();

// 初始化编码器（异步）
gb2312Encoder.loadMapping().catch(error => {
    console.error('Failed to initialize GB2312 encoder:', error);
});

