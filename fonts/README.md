# 显示汉字逻辑

1. 一些中文字库自带ASCII，ASCII字符在GB2312中的位置是 0xA1 + ASCII码

2. 下拉输入框“ASCII字库”增加一个选项：“汉字库”， 当用户选中这个作为ASCII字库时，从指定的汉字库读取编码来绘制ASCII字符。

3. 增加一个汉字库选择框，列出fonts/hzk2目录中汉字库，供用户选择。

处理文本输入框字符时，先将汉字和ASCII字符区分，然后根据各自的下拉选择框选中的字库来绘制字符。

4. 由于需要在WEB页面中使用GB2312的字库，因此需要在WEB页上支持将汉字码点转换为GB2312区位码。
需要实现如下逻辑 

```python

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

```

python中一个encode('gb2312')就可以将一个UNICODE码点转成 GB2312编码，不知道在WEB前端应用中，是否有对应的函数？

