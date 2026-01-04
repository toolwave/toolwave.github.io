import re
from pathlib import Path
from html import unescape

def extract_content_start(content):
    """提取正文开头内容（不包含title）"""
    # 移除head部分
    content = re.sub(r'<head>.*?</head>', '', content, flags=re.DOTALL | re.IGNORECASE)

    # 查找main或body标签后的内容
    main_match = re.search(r'<main[^>]*>(.*?)</main>', content, flags=re.DOTALL | re.IGNORECASE)
    if main_match:
        main_content = main_match.group(0)
    else:
        body_match = re.search(r'<body[^>]*>(.*?)</body>', content, flags=re.DOTALL | re.IGNORECASE)
        if body_match:
            main_content = body_match.group(0)
        else:
            main_content = content

    # 移除h1标题
    main_content = re.sub(r'<h1[^>]*>.*?</h1>', '', main_content, flags=re.DOTALL | re.IGNORECASE)

    # 移除所有HTML标签
    text = re.sub(r'<[^>]+>', ' ', main_content)
    # 移除script和style标签内容
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)

    # 解码HTML实体
    text = unescape(text)

    # 清理空白字符
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text

def generate_description_without_title(content, filename):
    """生成不包含title的description"""
    # 提取title
    title_match = re.search(r'<title>(.*?)</title>', content, flags=re.DOTALL | re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else ''

    # 提取正文内容
    text_content = extract_content_start(content)

    # 直接使用正文开头生成描述
    description = text_content[:400]

    # 清理
    description = description.strip()

    # 尝试在句号处截断，控制在140-170字符
    if len(description) > 170:
        # 寻找最后一个合适的句号
        for marker in ['。', '？', '！', '.', '?', '!']:
            last_pos = description.rfind(marker)
            if 140 <= last_pos <= 170:
                description = description[:last_pos + 1]
                break

        # 如果找不到合适的句号，直接截断
        if len(description) > 170:
            description = description[:167] + '...'

    # 如果太短，扩展到至少140字符
    if len(description) < 140:
        more_text = text_content[400:600]
        if more_text:
            description += ' ' + more_text
            description = description.strip()

            # 再次检查长度
            if len(description) > 170:
                last_period = description.rfind('。')
                if last_period >= 140:
                    description = description[:last_period + 1]
                else:
                    description = description[:167] + '...'

    # 如果还是太短，使用前400字符
    if len(description) < 140:
        description = text_content[:400]
        last_period = description.rfind('。')
        if last_period >= 120:
            description = description[:last_period + 1]
        else:
            description = description[:140] + '...'

    # 确保不包含title内容
    if title and title in description:
        # 如果description开头包含title，移除它
        if description.startswith(title):
            description = description[len(title):].strip()
        else:
            # 尝试移除title在description中的出现
            description = description.replace(title, '', 1).strip()

    return description

def fix_file(filepath):
    """修复单个文件"""
    try:
        content = filepath.read_text(encoding='utf-8-sig')

        # 提取当前description
        desc_match = re.search(r'<meta name="description" content="([^"]+)"', content, re.IGNORECASE)

        if not desc_match:
            print(f"[SKIP] No description found: {filepath.name}")
            return False

        # 提取title
        title_match = re.search(r'<title>(.*?)</title>', content, re.DOTALL | re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else ''

        current_desc = desc_match.group(1)

        # 检查是否包含title
        if title and title in current_desc:
            # 生成新的description（不包含title）
            new_desc = generate_description_without_title(content, filepath.name)

            if current_desc == new_desc:
                print(f"[SKIP] Already optimized: {filepath.name}")
                return False

            # 替换
            new_content = re.sub(
                r'<meta name="description" content="[^"]*"',
                f'<meta name="description" content="{new_desc}"',
                content,
                flags=re.IGNORECASE
            )

            # 保存
            filepath.write_text(new_content, encoding='utf-8-sig')

            return True, new_desc, len(new_desc)
        else:
            print(f"[SKIP] Title not in description: {filepath.name}")
            return False

    except Exception as e:
        print(f"[ERROR] {filepath.name}: {e}")
        return False

def main():
    # 排除的文件
    exclude_files = {'index.html', 'google49cbcf744d3c49aa.html', 'affiliates.html'}

    # 获取所有HTML文件
    html_files = []
    for file in Path('.').glob('*.html'):
        if file.name not in exclude_files:
            html_files.append(file)

    html_files.sort()

    print(f"Found {len(html_files)} HTML files\n")

    success = 0
    for filepath in html_files:
        result = fix_file(filepath)

        if result:
            success += 1
            new_desc = result[1]
            new_len = result[2]
            print(f"[OK] Fixed: {filepath.name}")
            print(f"     New length: {new_len} chars")
            print(f"     Preview: {new_desc[:80]}...")
            print()

    print(f"\nCompleted! Fixed {success}/{len(html_files)} files")

if __name__ == '__main__':
    main()
