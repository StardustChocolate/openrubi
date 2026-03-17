import json
from pypinyin import Style, pinyin
from collections import OrderedDict
from pathlib import Path

# 构建多音字选择的文件路径
current_file = Path(__file__)
target_file = current_file.parent.parent / 'arkrecode' / 'members' / 'pinyin_choices.json'

def load_pinyin_cache():
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_pinyin_cache(cache):
    # 如果目录不存在，创建目录（包括所有父目录）
    target_file.parent.mkdir(parents=True, exist_ok=True)
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def get_pinyin_choice(char, cache):
    # 优先使用缓存
    if char in cache:
        return cache[char]
    
    # 获取所有拼音候选
    candidates = pinyin(char, style=Style.NORMAL, heteronym=True)[0]
    
    # 单音字直接返回
    if len(candidates) <= 1:
        return candidates[0] if candidates else char
    
    # 多音字提示选择
    print(f"\n遇到多音字: {char}")
    print("候选拼音: " + ", ".join(f"[{i+1}] {p}" for i, p in enumerate(candidates)))
    
    while True:
        choice = input("请选择拼音序号或直接输入拼音（输入q保留原字）：").strip().lower()
        
        if choice == "q":
            return char
        
        # 处理数字选择
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(candidates):
                selected = candidates[index]
                cache[char] = selected
                return selected
        
        # 处理直接拼音输入
        if choice in candidates:
            cache[char] = choice
            return choice
        
        print("无效输入，请重新选择")

def process_string(s, cache):
    result = []
    for char in s:
        if '\u4e00' <= char <= '\u9fff':  # 汉字处理
            pinyin_choice = get_pinyin_choice(char, cache)
            result.append(pinyin_choice)
        else:  # 非汉字保留原样
            result.append(char)
    # return "".join(result)
    return "".join(result).lower()  # 转小写输出

def process_string_fast(s, cache):
    result = []
    for char in s:
        if '\u4e00' <= char <= '\u9fff':  # 汉字处理
            if char in cache:
                pinyin_choice = cache[char]
            else:
                # 获取默认拼音（第一个候选）
                pinyin_choice = pinyin(char, style=Style.NORMAL, heteronym=False)[0][0]
            result.append(pinyin_choice)
        else:  # 非汉字保留原样
            result.append(char)
    return "".join(result).lower()  # 转小写输出

def process_dictionary(original_dict):
    cache = load_pinyin_cache()
    processed_dict = OrderedDict()
    
    for key in original_dict:
        new_key = process_string(key, cache)
        processed_dict[new_key] = original_dict[key]
    
    save_pinyin_cache(cache)
    return processed_dict

# 开始转换
if __name__ == '__main__':
    with open('/root/Rubi/project/arkrecode/members/character_dic.json', 'r', encoding='utf-8') as f:
        sample_dict = json.load(f)
    processed = process_dictionary(sample_dict)
    with open('/root/Rubi/project/arkrecode/members/character_dic_pinyin.json', 'w', encoding='utf-8') as f:
        json.dump(processed, f, ensure_ascii=False, indent=4, separators=(',', ': '), default=str)
