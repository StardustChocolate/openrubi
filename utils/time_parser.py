import re
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
import calendar

# 中文数字映射表，用于将中文数字字符转换为阿拉伯数字
_CHINESE_DIGITS = {
    '零': 0,
    '一': 1,
    '二': 2,
    '两': 2,
    '三': 3,
    '四': 4,
    '五': 5,
    '六': 6,
    '七': 7,
    '八': 8,
    '九': 9,
}

# 中文单位映射表，用于解析中文数字中的单位
_CHINESE_UNITS = {
    '十': 10,
    '百': 100,
    '千': 1000,
    '万': 10_000,
    '亿': 100_000_000,
}

# 全角字符转换表，将全角数字和点号转换为半角
_FULLWIDTH_TRANSLATION = str.maketrans(
    '０１２３４５６７８９．',
    '0123456789.',
)

# 时间单位乘数映射表，将各种时间单位转换为秒数
_UNIT_MULTIPLIER = {
    '小时': 3600,
    '时': 3600,
    '钟头': 3600,
    '钟': 3600,
    '分': 60,
    '分钟': 60,
    '秒': 1,
    '秒钟': 1,
    '天': 86400,
    '日': 86400,
    '月': 86400 * 30,  # 假设一个月为30天
    '年': 86400 * 365,  # 假设一年为365天
}

# 时间持续时间正则表达式模式列表，每个元组包含正则表达式和对应的秒数乘数
# 模式按优先级排序：年 > 月 > 天 > 小时 > 分钟 > 秒
_DURATION_PATTERNS = [
    (r'(?P<amount>(?:\d+(?:\.\d+)?|[零一二两三四五六七八九十百千万亿点个半]+))\s*(?P<unit>年)(?P<trailing_half>半)?', 86400 * 365),
    (r'(?P<amount>(?:\d+(?:\.\d+)?|[零一二两三四五六七八九十百千万亿点个半]+))\s*(?P<unit>月)(?P<trailing_half>半)?', 86400 * 30),
    (r'(?P<amount>(?:\d+(?:\.\d+)?|[零一二两三四五六七八九十百千万亿点个半]+))\s*(?P<unit>天|日)(?P<trailing_half>半)?', 86400),
    (r'(?P<amount>(?:\d+(?:\.\d+)?|[零一二两三四五六七八九十百千万亿点个半]+))\s*(?P<unit>小时|钟头|钟|时)(?P<trailing_half>半)?', 3600),
    (r'(?P<amount>(?:\d+(?:\.\d+)?|[零一二两三四五六七八九十百千万亿点个半]+))\s*(?P<unit>分钟|分)(?P<trailing_half>半)?', 60),
    (r'(?P<amount>(?:\d+(?:\.\d+)?|[零一二两三四五六七八九十百千万亿点个半]+))\s*(?P<unit>秒钟|秒)(?P<trailing_half>半)?', 1),
]


def _normalize_text(text: str) -> str:
    """规范化输入文本，将全角字符转换为半角并去除首尾空格"""
    return text.translate(_FULLWIDTH_TRANSLATION).strip()


def _chinese_to_number(chinese: str) -> float:
    """将中文数字字符串转换为浮点数"""
    if not chinese:
        return 0.0
    chinese = chinese.replace('个', '')  # 去除“个”字
    if chinese == '半':
        return 0.5

    # 处理以“半”结尾的情况，如“一半”
    if chinese.endswith('半') and chinese != '半':
        prefix = chinese[:-1]
        prefix_value = _chinese_to_number(prefix)
        return prefix_value + 0.5

    # 处理小数点，如“一二点三”
    if '点' in chinese:
        integer_part, decimal_part = chinese.split('点', 1)
        integer_value = _chinese_to_number(integer_part) if integer_part else 0
        decimal_digits = ''.join(str(_CHINESE_DIGITS.get(c, c)) for c in decimal_part)
        try:
            return integer_value + float('0.' + decimal_digits)
        except ValueError:
            return integer_value

    # 解析中文数字
    total = 0
    section = 0
    current = 0
    last_unit = 1

    for char in chinese:
        if char in _CHINESE_DIGITS:
            current = _CHINESE_DIGITS[char]
        elif char in _CHINESE_UNITS:
            unit = _CHINESE_UNITS[char]
            if current == 0:
                current = 1  # 如“十”表示10
            section += current * unit
            current = 0
            last_unit = unit
        else:
            continue

    total = section + current
    return float(total)


def _parse_amount(amount_text: str) -> float:
    """解析数量文本，支持阿拉伯数字、中文数字和半数"""
    amount_text = amount_text.replace(' ', '')
    if not amount_text:
        return 0.0
    # 处理阿拉伯数字后跟“半”的情况，如“1.5”或“1半”
    if amount_text.endswith('半') and any(ch.isdigit() for ch in amount_text[:-1]):
        prefix = amount_text[:-1].replace('个', '')
        try:
            return float(prefix) + 0.5
        except ValueError:
            return _chinese_to_number(amount_text)

    # 处理纯阿拉伯数字
    if amount_text.isdigit() or re.fullmatch(r'\d+\.\d+', amount_text):
        return float(amount_text)

    # 处理以“半”开头的中文，如“半”
    if amount_text.startswith('半') and not any(ch.isdigit() for ch in amount_text):
        return 0.5

    # 其他情况使用中文数字解析
    return _chinese_to_number(amount_text)


def extract_seconds(text: str) -> int:
    """从时间描述文本中提取总秒数
    
    支持的格式示例：
    - 中文数字：'十分钟', '一个半小时', '一年半'
    - 阿拉伯数字：'10分', '2小时30分', '3.5小时'
    - 混合单位：'1天2小时', '半个月'
    
    返回值：总秒数（整数）
    """
    normalized = _normalize_text(text)
    total_seconds = 0

    # 遍历所有模式，匹配并累加秒数
    for pattern, multiplier in _DURATION_PATTERNS:
        for match in re.finditer(pattern, normalized):
            raw_amount = match.group('amount')
            parsed_amount = _parse_amount(raw_amount)
            total_seconds += int(parsed_amount * multiplier)
            # 如果有尾随的“半”，额外加0.5倍的单位秒数
            if match.groupdict().get('trailing_half'):
                total_seconds += int(0.5 * multiplier)

    return total_seconds


def parse_reminder_time(text: str) -> Optional[Dict[str, Any]]:
    """
    解析提醒时间表达式
    
    支持格式：
    - 相对时间：'两小时后', '30分钟后', '明天上午9点'
    - 重复时间：'每天下午三点', '每周四提醒', '每月15号'
    - 具体时间：'4月15日提醒', '2024年5月1日10点'
    
    返回字典：
    - type: 'once' 或 'repeat'
    - next_time: 下次提醒的datetime对象
    - interval: 重复间隔（秒），仅对repeat有效
    - description: 原始描述
    """
    text = _normalize_text(text)
    
    # 解析相对时间
    relative_patterns = [
        (r'(\d+(?:\.\d+)?|[零一二两三四五六七八九十百千万亿点个半]+)\s*(小时|钟头|钟|时|分钟|分|秒钟|秒|天|日)\s*后', 'relative'),
        (r'明天\s*(上午|早上|中午|下午)?\s*(\d+|[零一二两三四五六七八九十百千万亿]+)\s*(点|时)', 'tomorrow'),
        (r'后天\s*(上午|早上|中午|下午)?\s*(\d+|[零一二两三四五六七八九十百千万亿]+)\s*(点|时)', 'day_after_tomorrow'),
    ]
    
    for pattern, pattern_type in relative_patterns:
        match = re.search(pattern, text)
        if match:
            if pattern_type == 'relative':
                amount_text = match.group(1)
                unit = match.group(2)
                seconds = extract_seconds(f"{amount_text}{unit}")
                next_time = datetime.now() + timedelta(seconds=seconds)
                return {
                    'type': 'once',
                    'next_time': next_time,
                    'interval': None,
                    'description': text
                }
            elif pattern_type == 'tomorrow':
                period = match.group(1)  # 上午/中午/下午
                hour = _parse_amount(match.group(2))
                if period == '下午':
                    hour += 12
                elif period == '中午':
                    if hour < 12:
                        hour += 12
                tomorrow = datetime.now() + timedelta(days=1)
                next_time = tomorrow.replace(hour=int(hour), minute=0, second=0, microsecond=0)
                return {
                    'type': 'once',
                    'next_time': next_time,
                    'interval': None,
                    'description': text
                }
            elif pattern_type == 'day_after_tomorrow':
                period = match.group(1)
                hour = _parse_amount(match.group(2))
                if period == '下午':
                    hour += 12
                elif period == '中午':
                    if hour < 12:
                        hour += 12
                day_after = datetime.now() + timedelta(days=2)
                next_time = day_after.replace(hour=int(hour), minute=0, second=0, microsecond=0)
                return {
                    'type': 'once',
                    'next_time': next_time,
                    'interval': None,
                    'description': text
                }
    
    # 解析重复时间
    repeat_patterns = [
        (r'每天\s*(上午|早上|中午|下午|晚上|凌晨|清晨)?\s*(\d+|[零一二两三四五六七八九十百千万亿]+)\s*(点|时)', 86400, 'daily'),
        (r'每天下午\s*(\d+|[零一二两三四五六七八九十百千万亿]+)\s*(点|时)', 86400, 'daily_afternoon'),
        (r'每周\s*([一二三四五六七日])\s*(上午|早上|中午|下午|晚上|凌晨|清晨)?\s*(\d+|[零一二两三四五六七八九十百千万亿]+)?\s*(点|时)?', 604800, 'weekly'),
        (r'每月\s*(\d+|[零一二两三四五六七八九十百千万亿]+)\s*号', 86400 * 30, 'monthly'),
    ]
    
    for pattern, interval, pattern_type in repeat_patterns:
        match = re.search(pattern, text)
        if match:
            now = datetime.now()
            if pattern_type == 'daily':
                period = match.group(1)  # 上午/中午/下午/晚上/凌晨/清晨
                hour = _parse_amount(match.group(2))
                
                # 处理时间段
                if period == '下午':
                    hour += 12
                elif period in ('中午', '早上', '上午'):
                    if hour < 12:
                        hour += 12 if period == '中午' else 0
                elif period == '晚上':
                    hour += 12 if hour < 12 else hour
                elif period == '凌晨':
                    pass  # 凌晨1点就是1点
                elif period == '清晨':
                    pass  # 清晨6点就是6点
                
                today_time = now.replace(hour=int(hour), minute=0, second=0, microsecond=0)
                next_time = today_time if today_time > now else today_time + timedelta(days=1)
                return {
                    'type': 'repeat',
                    'next_time': next_time,
                    'interval': interval,
                    'description': text
                }
            elif pattern_type == 'daily_afternoon':
                hour = _parse_amount(match.group(1)) + 12  # 下午
                today_time = now.replace(hour=int(hour), minute=0, second=0, microsecond=0)
                next_time = today_time if today_time > now else today_time + timedelta(days=1)
                return {
                    'type': 'repeat',
                    'next_time': next_time,
                    'interval': interval,
                    'description': text
                }
            elif pattern_type == 'weekly':
                weekday_map = {'一': 0, '二': 1, '三': 2, '四': 3, '五': 4, '六': 5, '日': 6}
                weekday = weekday_map[match.group(1)]
                period = match.group(2)  # 上午/中午/下午/晚上/凌晨/清晨
                hour = _parse_amount(match.group(3)) if match.group(3) else 9  # 默认9点
                
                # 处理时间段
                if period == '下午':
                    hour += 12
                elif period in ('中午', '早上', '上午'):
                    if hour < 12:
                        hour += 12 if period == '中午' else 0
                elif period == '晚上':
                    hour += 12 if hour < 12 else hour  # 晚上通常是12点后
                elif period == '凌晨':
                    pass  # 凌晨1点就是1点，不需要加12
                elif period == '清晨':
                    pass  # 清晨6点就是6点，不需要加12
                
                days_ahead = (weekday - now.weekday()) % 7
                if days_ahead == 0 and (now.hour < hour or (now.hour == hour and now.minute < 0)):
                    days_ahead = 7
                next_time = (now + timedelta(days=days_ahead)).replace(hour=int(hour), minute=0, second=0, microsecond=0)
                return {
                    'type': 'repeat',
                    'next_time': next_time,
                    'interval': interval,
                    'description': text
                }
            elif pattern_type == 'monthly':
                day = int(_parse_amount(match.group(1)))
                year = now.year
                month = now.month
                if day < now.day or (day == now.day and now.hour >= 9):  # 默认9点
                    month += 1
                    if month > 12:
                        month = 1
                        year += 1
                try:
                    next_time = datetime(year, month, day, 9, 0, 0)
                except ValueError:
                    # 处理无效日期，如2月30日
                    next_time = datetime(year, month, calendar.monthrange(year, month)[1], 9, 0, 0)
                return {
                    'type': 'repeat',
                    'next_time': next_time,
                    'interval': interval,
                    'description': text
                }
    
    # 解析具体日期
    date_patterns = [
        (r'(\d{4})?\s*年\s*(\d+|[零一二两三四五六七八九十百千万亿]+)\s*月\s*(\d+|[零一二两三四五六七八九十百千万亿]+)\s*日\s*(\d+|[零一二两三四五六七八九十百千万亿]+)?\s*(点|时)?', 'full_date'),
        (r'(\d+|[零一二两三四五六七八九十百千万亿]+)\s*月\s*(\d+|[零一二两三四五六七八九十百千万亿]+)\s*日\s*(\d+|[零一二两三四五六七八九十百千万亿]+)?\s*(点|时)?', 'month_day'),
    ]
    
    for pattern, pattern_type in date_patterns:
        match = re.search(pattern, text)
        if match:
            now = datetime.now()
            if pattern_type == 'full_date':
                year = int(match.group(1)) if match.group(1) else now.year
                month = int(_parse_amount(match.group(2)))
                day = int(_parse_amount(match.group(3)))
                hour = int(_parse_amount(match.group(4))) if match.group(4) else 9
                try:
                    next_time = datetime(year, month, day, hour, 0, 0)
                    if next_time < now:
                        next_time = next_time.replace(year=year + 1)
                except ValueError:
                    return None
                return {
                    'type': 'once',
                    'next_time': next_time,
                    'interval': None,
                    'description': text
                }
            elif pattern_type == 'month_day':
                month = int(_parse_amount(match.group(1)))
                day = int(_parse_amount(match.group(2)))
                hour = int(_parse_amount(match.group(3))) if match.group(3) else 9
                year = now.year
                if month < now.month or (month == now.month and day < now.day):
                    year += 1
                try:
                    next_time = datetime(year, month, day, hour, 0, 0)
                except ValueError:
                    return None
                return {
                    'type': 'once',
                    'next_time': next_time,
                    'interval': None,
                    'description': text
                }
    
    return None


if __name__ == '__main__':
    # 示例测试用例
    samples = [
        '十分钟',
        '半个钟',
        '10分',
        '一个半小时',
        '1个半小时',
        '2小时30分',
        '3.5小时',
        '半小时',
        '45秒',
        '一小时二十分钟',
        '一天',
        '两天',
        '半个月',
        '一年半',
        '3年2个月',
    ]
    # 运行测试并打印结果
    for sample in samples:
        print(f"{sample} -> {extract_seconds(sample)} 秒")
