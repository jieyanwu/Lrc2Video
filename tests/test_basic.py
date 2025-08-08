# def hex_to_ass_color(hex_color):
#     """将十六进制颜色转换为ASS颜色格式"""
#     hex_color = hex_color.lstrip('#')
#     r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
#     return f"{b:02x}{g:02x}{r:02x}"

# hex_color = "#FF0000"
# print(hex_to_ass_color(hex_color))


def hex_to_ass_color(hex_color):
    """将十六进制颜色转换为ASS颜色格式"""
    hex_color = hex_color.lstrip('#')
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"{b:02x}{g:02x}{r:02x}"

print(hex_to_ass_color("#FF0000"))  # 应输出：0000ff