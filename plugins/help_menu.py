
import json
import re
import math
from plugins.base_plugin import BasePlugin
from configs.config_manager import config_manager
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

class HelpMenu(BasePlugin):
    """帮助菜单"""
    
    # 插件基本信息
    name: str = "帮助菜单"
    description: str = ""

    # 菜单中不显示的插件
    excluded_plugins = ["test", "example", "监护人指令"]
    
    def __init__(self):
        super().__init__()
        self.priority = 90  # 优先级，范围0-100，数字越小优先级越高，默认50
        # 优先级稍微调低，以便那些不将功能名称作为关键词的功能在被call名称时能落到此处触发对应的帮助

    async def on_message(self, data, bot) -> bool:
        """处理消息事件"""
        msg = self.get_texts(data)
        
        # 该功能在群聊中不@时不响应
        if not self.at_if_group(data):
            return False
        
        # 非好友私聊过滤
        if self.filter_nonfriend(data):
            return False

        keyword_help = ["help", "功能", "功能列表", "功能菜单", "帮助", "帮助菜单", "菜单"]
        name_desc = {
            plugin.name: plugin.description
            for plugin in bot.plugin_manager.plugins.values()
            if plugin.name != self.name and plugin.name not in self.excluded_plugins # 排除自身和不需显示的插件
        }

        # 帮助菜单--列表
        if msg in keyword_help:
            # 检查开关
            if not await self.check_enable(data, bot):
                return True
            # 发送消息
            if data.get("message_type") == "group":
                gid = str(data.get("group_id")) 
                self_info = await config_manager.get_self_info()
                group_info = await config_manager.get_group_info(gid)
                img_path = generate_help_menu(name_desc, self_info["disable_plugins"], group_info["close_plugins"])    # 生成帮助菜单图片
                await self.send_group_msg(data.get("group_id"), f"[CQ:image,file={img_path}]")
            elif data.get("message_type") == "private":
                self_info = await config_manager.get_self_info()
                img_path = generate_help_menu(name_desc, self_info["disable_plugins"])
                await self.send_private_msg(data.get("user_id"), f"[CQ:image,file={img_path}]")   

            return True

        # 帮助菜单--描述
        elif msg.removesuffix("帮助") in name_desc.keys():
            # 检查开关
            if not await self.check_enable(data, bot):
                return True
            # 发送消息
            send_buff = name_desc[msg.removesuffix("帮助")]
            if not send_buff:
                send_buff = "该功能暂时没写帮助哦Σ( ° △ °|||)︴"
            if data.get("message_type") == "group":
                await self.send_group_msg(data.get("group_id"), send_buff)
            elif data.get("message_type") == "private":
                await self.send_private_msg(data.get("user_id"), send_buff)  
            
            return True

        # 未命中关键词
        else:
            return False


# ------------------------以下为绘图操作------------------------

class Line:
    '''由带格式文本片段组成的行'''
    def __init__(self):
        self.fragments = []
        self.max_ascent = 0
        self.max_descent = 0

    @property
    def height(self):
        return self.max_ascent + self.max_descent

def get_text_size(draw, text, font):
    """使用 getbbox 获取文本的宽度和高度"""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]  # 宽度, 高度

def resize_image(image, scale_factor):
    """等比例缩放图片"""
    width, height = image.size
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
    return resized_image

def split_text_into_segments(text, keywords):
    """返回一个包含所有文本段的列表，每个段都包含文本内容及其对应的字体和颜色信息"""
    # 对关键字按长度从长到短进行排序，确保较长的关键字优先匹配
    sorted_keywords = sorted(keywords.keys(), key=lambda x: len(x), reverse=True)
    # 将关键字列表转换为正则表达式模式，使用 `|` 分隔多个关键字，并对关键字进行转义
    pattern = '|'.join(map(re.escape, sorted_keywords))
    # 编译正则表达式，将关键字模式用括号分组，并确保关键字后紧跟着"("
    regex = re.compile(f'({pattern})(?=\\()|(\n)')
    # 初始化一个空列表，用于存储分割后的文本段
    segments = []
    # 记录上一次匹配结束的位置，初始为0
    last_end = 0
    # 遍历文本中所有匹配的关键字
    for match in regex.finditer(text):
        # 获取当前匹配的起始和结束位置
        start, end = match.start(), match.end()
        # 如果当前匹配的起始位置大于上一次匹配的结束位置，说明中间有一段非关键字的文本
        if start > last_end:
            # 将这段非关键字的文本添加到 segments 中，font 和 color 为 None
            segments.append({
                'text': text[last_end:start],
                'font': None,
                'color': None
            })
        # 处理高亮词或换行符
        keyword, newline = match.groups()
        # 将当前匹配的关键字添加到 segments 中，并从 keywords 字典中获取对应的 font 和 color
        if keyword:
            segments.append({'text': keyword, 'font': keywords[keyword]['font'], 'color': keywords[keyword]['color']})
        elif newline:
            segments.append({'text': '\n', 'font': None, 'color': None})
        # 更新 last_end 为当前匹配的结束位置
        last_end = end
    # 如果文本的最后一段没有被匹配到关键字，将其添加到 segments 中
    if last_end < len(text):
        segments.append({
            'text': text[last_end:],
            'font': None,
            'color': None
        })
    # 返回分割后的文本段列表
    return segments

def layout_lines(segments, max_width, padding, default_font, default_color):
    '''将 segments 多段带格式文本以固定宽度拆成多行, 每行都是一组 segments '''
    # 初始化一个空列表，用于存储所有行
    lines = []
    # 初始化当前行对象
    current_line = Line()
    # 初始化当前行的起始x坐标（从0开始，不包括左边距）
    x = 0
    # 遍历每个文本段
    for segment in segments:
        # 获取当前段的文本内容
        text = segment['text']
        # 如果是换行符则换到新行
        if text == '\n':
            if current_line.fragments:
                lines.append(current_line)
                current_line = Line()
                x = 0
            continue  # 换行符不占据空间
        # 获取当前段的字体，如果没有指定则使用默认字体
        font = segment['font'] or default_font
        # 获取当前段的颜色，如果没有指定则使用默认颜色
        color = segment['color'] or default_color
        # 循环处理当前段的文本，直到所有文本都被处理完毕
        while text:
            # 计算当前行剩余的可用宽度
            # 可用宽度 = 最大宽度 - 左右内边距 - 已经使用的宽度
            available_width = max_width - 2 * padding - x
            # 如果可用宽度小于等于0，说明当前行已经无法容纳更多内容
            if available_width <= 0:
                # 将当前行添加到lines列表中
                lines.append(current_line)
                # 初始化一个新的行对象
                current_line = Line()
                # 重置x坐标为0（新行的起始位置，不包括左边距）
                x = 0
                # 重新计算可用宽度
                available_width = max_width - 2 * padding
            # 初始化最大可容纳字符数
            max_n = 0
            # 遍历文本，找到当前行可以容纳的最大字符数
            for n in range(1, len(text) + 1):
                # 截取前n个字符
                substring = text[:n]
                # 计算这n个字符的宽度
                substring_width = font.getlength(substring)
                # 如果这n个字符的宽度小于等于可用宽度，则更新max_n
                if substring_width <= available_width:
                    max_n = n
                else:
                    # 否则跳出循环
                    break
            # 如果max_n为0，说明当前行无法容纳任何字符
            if max_n == 0:
                # 将当前行添加到lines列表中
                lines.append(current_line)
                # 初始化一个新的行对象
                current_line = Line()
                # 重置x坐标为0（新行的起始位置，不包括左边距）
                x = 0
                # 重新计算可用宽度
                available_width = max_width - 2 * padding
                # 如果文本不为空，则至少容纳一个字符
                max_n = 1 if text else 0
            # 如果max_n大于0，说明可以容纳部分文本
            if max_n > 0:
                # 截取前max_n个字符
                substring = text[:max_n]
                # 更新剩余的文本
                text = text[max_n:]
                # 将截取的文本片段添加到当前行的fragments列表中
                current_line.fragments.append({
                    'text': substring,
                    'font': font,
                    'color': color
                })
                # 获取字体的ascent和descent（用于计算行高）
                ascent, descent = font.getmetrics()
                # 更新当前行的最大ascent和descent
                current_line.max_ascent = max(current_line.max_ascent, ascent)
                current_line.max_descent = max(current_line.max_descent, descent)
                # 更新当前行的x坐标（增加已使用的宽度）
                x += font.getlength(substring)
    # 如果当前行还有未处理的片段，将其添加到lines列表中
    if current_line.fragments:
        lines.append(current_line)
    # 返回所有行的列表
    return lines

def draw_text_with_highlight(
    draw,                       # 要绘制的图片
    text,                       # 要在图片上绘制的文本
    keywords,                   # 文本中高亮的关键词
    start_x,                    # 文本起始坐标x
    start_y,
    max_width=800,              # 文本最大宽度，自动换行
    default_font=None,          # 默认字体
    default_color=(0, 0, 0),    # 默认颜色
    padding=0                   # 页边距
):
    """对传入的draw对象绘制文本，支持多个高亮词及其自定义样式，返回值为总绘制高度"""
    segments = split_text_into_segments(text, keywords)
    lines = layout_lines(segments, max_width, padding, default_font, default_color)

    y = start_y
    for line in lines:
        x = start_x + padding
        for fragment in line.fragments:
            text_segment = fragment['text']
            font = fragment['font']
            color = fragment['color']
            ascent, _ = font.getmetrics()
            draw.text((x, y + line.max_ascent - ascent), text_segment, fill=color, font=font)
            x += font.getlength(text_segment)
        y += line.height
    
    # 返回总绘制高度（当前y减去起始y）
    return y - start_y

def draw_text_with_fallback(draw, x_y, text, font_primary, font_fallback, fill='black'):
    x, y = x_y
    total_width = 0  # 初始化总宽度
    for char in text:
    # 检查字符是否可以被主字体渲染
        mask = font_primary.getmask(char)
        if mask.getbbox() is None:  # 如果字符无法渲染
            # 使用备用字体
            draw.text((x + total_width, y+8), char, font=font_fallback, embedded_color=True)
            total_width += font_fallback.getlength(char)    # 获取字符宽度并累加
        else:
            # 使用主字体
            draw.text((x + total_width, y), char, font=font_primary, fill=fill)
            total_width += font_primary.getlength(char)
    return total_width  # 返回绘制的总长度

# 绘制文本
def generate_help_menu(plugins_dic, disable_plugins=None, close_plugins=None):
    disable_plugins = disable_plugins or []
    close_plugins = close_plugins or []

    # 获取路径
    current_file = Path(__file__)
    font_default_path = current_file.parent.parent / 'font' / 'SanJiYuanTiJian-Cu-2.ttf'
    font_emoji_path = current_file.parent.parent / 'font' / 'SEGUIEMJ.TTF'
    images_path = current_file.parent.parent / 'images' / 'help_menu'
    temp_file_path = current_file.parent.parent / 'temp' / 'function_list.png'

    # 创建画布
    template_width, template_height = 1000, 1000    # 画布尺寸
    canvas = Image.new('RGBA', (template_width, template_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(canvas)

    # 绘制标题
    y = 80  # 装饰边线
    text = "呐呐呐~  这里是功能列表："
    font = ImageFont.truetype(font_default_path, 36, encoding='utf-8') # 使用系统字体，或者指定字体文件路径
    # 目标区域的左上角和右下角坐标
    left, top, right, bottom = 0, y, 1000, y+36
    # 计算文本的宽度和高度
    text_width, text_height = get_text_size(draw, text, font=font)
    # 计算文本的起始位置，使其在目标区域内居中
    x_ = left + (right - left - text_width) // 2
    y_ = top + (bottom - top - text_height) // 2
    # 在图像上绘制文本
    draw.text((x_, y_), text, font=font, fill='black')

    y += (bottom - top) + 40 # 行距

    # 绘制通用功能
    text = "通用类："
    font = ImageFont.truetype(font_default_path, 24, encoding='utf-8')
    font_emoji = ImageFont.truetype(font_emoji_path, 24)
    draw.text((100, y), text, font=font, fill='black')
    y += 34 # 行距
    column = 0  # 列索引
    for name in plugins_dic.keys():
        x = column * 270 + 100
        width = draw_text_with_fallback(draw, (x, y), f"🌟{name}", font, font_emoji, fill='black')
        
        if name in []:
            draw.text((x + width, y), f"(维护中)", font=font, fill='Grey')
        elif name in disable_plugins:
            draw.text((x + width, y), f"(已封禁)", font=font, fill='Purple')
        elif name in close_plugins:
            draw.text((x + width, y), f"(已关闭)", font=font, fill='DarkRed')
        else:
            draw.text((x + width, y), f"(已开启)", font=font, fill='DarkGreen')

        column += 1
        if column > 2 :
            column = 0
            y += 30

    y += 60 # 行距

    # 绘制权限功能
    # text = "权限类："
    # font = ImageFont.truetype('./font/SanJiYuanTiJian-Cu-2.ttf', 24, encoding='utf-8')
    # font_emoji = ImageFont.truetype('./font/SEGUIEMJ.TTF', 24)
    # draw.text((100, y), text, font=font, fill='black')
    # y += 34 # 行距
    # column = 0  # 列索引
    # for k,v in admin.items():
    #     x = column * 270 + 100
    #     width = draw_text_with_fallback(draw, (x, y), f"🍀{v}", font, font_emoji, fill='black')
        
    #     if k in function_maintenance:
    #         draw.text((x + width, y), f"(维护中)", font=font, fill='Grey')
    #     elif k in forbid_func:
    #         draw.text((x + width, y), f"(已封禁)", font=font, fill='Purple')
    #     elif k in disable_func:
    #         draw.text((x + width, y), f"(已关闭)", font=font, fill='DarkRed')
    #     else:
    #         draw.text((x + width, y), f"(已开启)", font=font, fill='DarkGreen')

    #     column += 1
    #     if column > 2 :
    #         column = 0
    #         y += 30

    # y += 30 # 行距

    # 小提示
    font = ImageFont.truetype(font_default_path, 24, encoding='utf-8')
    text = "💗输入「功能名+帮助」即可查看该功能的详细说明哦~示例：一言帮助"
    draw_text_with_fallback(draw, (100, y), text, font, font_emoji, fill='black')
    y += 30 # 行距
    text = "💗@我并发送:「更新日志」，即可拉取最近的一次更新记录~"
    draw_text_with_fallback(draw, (100, y), text, font, font_emoji, fill='black')
    # y += 26 # 行距
    # text = ""
    # draw_text_with_fallback(draw, (132, y), text, font, font_emoji, fill='black')
    y += 30 # 行距

    y += 80  # 装饰边线

    # 创建背景画布
    count = math.ceil(max(1, (y - 500) / 200))  # 需要的中间段数量
    template_height = 500 + 200 * count
    new_canvas = Image.new('RGBA', (template_width, template_height), 'white')  # 背景为白色
    # 添加背景图片
    bg_img = Image.open(images_path / "BG_help.png").resize((template_width, template_height))
    new_canvas.paste(bg_img, (0, 0), bg_img)
    # 添加上边框
    img_frame = Image.open(images_path / "frame_help_up.png")
    new_canvas.paste(img_frame, (0, 0), img_frame)
    # 添加中边框
    img_frame = Image.open(images_path / "frame_help_mid.png")
    for i in range(count):
        new_canvas.paste(img_frame, (0, 230+i*200), img_frame)
    # 添加下边框
    img_frame = Image.open(images_path / "frame_help_down.png")
    new_canvas.paste(img_frame, (0, 230+count*200), img_frame)

    # 将文字画布粘贴到背景画布上
    new_canvas.paste(canvas, (0, 0), canvas)

    # 保存结果
    new_canvas.save(temp_file_path)

    return temp_file_path
