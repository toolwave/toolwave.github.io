import re
import sys
from pathlib import Path
from html.parser import HTMLParser
from html import unescape

# 设置stdout编码为UTF-8
sys.stdout.reconfigure(encoding='utf-8')

class TitleExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = None

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.in_title = True

    def handle_data(self, data):
        if getattr(self, 'in_title', False):
            self.title = data.strip()
            self.in_title = False

def extract_title(content):
    """提取标题"""
    match = re.search(r'<title>(.*?)</title>', content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def extract_content_start(content):
    """提取正文开头内容"""
    # 移除head部分
    content = re.sub(r'<head>.*?</head>', '', content, flags=re.DOTALL | re.IGNORECASE)

    # 查找main或body标签后的内容
    main_match = re.search(r'<main[^>]*>.*?</main>', content, flags=re.DOTALL | re.IGNORECASE)
    if main_match:
        main_content = main_match.group(0)
    else:
        body_match = re.search(r'<body[^>]*>(.*?)</body>', content, flags=re.DOTALL | re.IGNORECASE)
        if body_match:
            main_content = body_match.group(0)
        else:
            main_content = content

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

    # 获取前500字符用于生成描述
    return text[:500] if len(text) > 500 else text

def generate_description(title, content_start, filename):
    """生成meta description"""
    # 从文件名中提取关键词
    keywords = filename.replace('-', ' ').replace('.html', '').split()

    # 提取正文前200字符
    content_preview = content_start[:200] if len(content_start) > 200 else content_start

    # 生成描述
    description = content_preview.strip()

    # 如果太短，补充内容
    if len(description) < 120:
        if len(content_start) > 200:
            description = content_start[:300].strip()
            # 在句号处截断
            last_period = description.rfind('。')
            if last_period > 100:
                description = description[:last_period + 1]

    # 确保不超过160字符
    if len(description) > 160:
        # 尝试在句号处截断
        last_period = description.rfind('。')
        if last_period > 120 and last_period < 155:
            description = description[:last_period + 1]
        else:
            description = description[:157] + "..."

    return description

def update_html_file(filepath):
    """更新HTML文件"""
    try:
        # 尝试多种编码读取
        content = None
        for encoding in ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    content = f.read()
                    break
            except:
                continue

        if not content:
            print(f"[SKIP] Cannot read: {filepath.name}")
            return False

        # 检查是否已经有meta description和canonical
        has_description = '<meta name="description"' in content
        has_canonical = 'rel="canonical"' in content

        if has_description and has_canonical:
            print(f"[SKIP] Already has meta tags: {filepath.name}")
            return False

        # 提取标题和内容
        title = extract_title(content)
        if not title:
            print(f"[SKIP] No title: {filepath.name}")
            return False

        content_start = extract_content_start(content)

        # 生成description
        description = generate_description(title, content_start, filepath.name)

        # 生成canonical URL
        canonical_url = f"https://toolwave.github.io/{filepath.name}"

        # 更新content
        updated = False

        # 添加或更新meta description
        if not has_description:
            # 查找title标签后的位置
            title_pattern = r'(<title>.*?</title>)'
            replacement = r'\1\n<meta name="description" content="' + description.replace('"', '&quot;') + '">'
            content = re.sub(title_pattern, replacement, content, flags=re.DOTALL)
            updated = True

        # 添加或更新canonical
        if not has_canonical:
            # 查找meta description或title后的位置
            if '<meta name="description"' in content:
                insert_after = r'(<meta name="description"[^>]*>)'
            else:
                insert_after = r'(<title>.*?</title>)'

            canonical_tag = f'\n<link rel="canonical" href="{canonical_url}">'
            content = re.sub(insert_after, r'\1' + canonical_tag, content, flags=re.DOTALL)
            updated = True

        if updated:
            # 保存文件
            with open(filepath, 'w', encoding='utf-8-sig') as f:
                f.write(content)
            print(f"[OK] Updated: {filepath.name}")
            print(f"    Desc: {description[:60]}...")
            return True
        else:
            print(f"[SKIP] No changes: {filepath.name}")
            return False

    except Exception as e:
        print(f"[ERROR] ({filepath.name}): {e}")
        return False

def main():
    # 排除的文件
    exclude_files = {'index.html', 'google49cbcf744d3c49aa.html'}

    # 获取所有HTML文件
    html_files = []
    for file in Path('.').glob('*.html'):
        if file.name not in exclude_files:
            html_files.append(file)

    html_files.sort()

    print(f"找到 {len(html_files)} 个HTML文件\n")

    success_count = 0
    for filepath in html_files:
        if update_html_file(filepath):
            success_count += 1

    print(f"\n完成！成功更新 {success_count}/{len(html_files)} 个文件")

if __name__ == '__main__':
    main()
