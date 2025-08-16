import sys
import subprocess
import os
import json
import re
import html
from datetime import datetime

# Naver 검색 함수 (naver.py 스크립트 호출)
def search_naver(query):
    script_path = os.path.join(os.path.dirname(__file__), 'naver.py')
    try:
        # naver.py를 HTML 모드로 실행
        result = subprocess.run(
            ['python3', script_path, query, 'news', '--json'],
            capture_output=True,
            text=True,
            check=True
        )
        naver_data = json.loads(result.stdout)
        
        items = []
        if "items" in naver_data:
            for item in naver_data["items"]:
                items.append({
                    'title': item.get('title', 'N/A'),
                    'link': item.get('link', '#'),
                    'description': item.get('description', 'N/A') # Use description for snippet
                })
        return items
    except FileNotFoundError:
        print(f"오류: 'naver.py'를 찾을 수 없습니다. 'unified_search.py'와 같은 디렉토리에 있는지 확인하세요.")
        return []
    except subprocess.CalledProcessError as e:
        print(f"naver.py 실행 중 오류 발생: {e.stderr}")
        return []
    except json.JSONDecodeError:
        print(f"naver.py 출력 파싱 오류: {result.stdout}")
        return []
    except Exception as e:
        print(f"알 수 없는 오류 발생: {e}")
        return []

# Google 검색 함수 (default_api.google_web_search 사용)
def search_google(query):
    try:
        google_search_response = default_api.google_web_search(query=query)
        google_results_raw = google_search_response.get('output', '')
        
        # Parse the raw string output from google_web_search
        # This is a simplified parsing based on the observed output format
        results = []
        lines = google_results_raw.split('\n')
        current_item = {}
        for line in lines:
            line = line.strip()
            if line.startswith('*'):
                if current_item:
                    results.append(current_item)
                current_item = {'title': line[1:].strip(), 'link': '#', 'snippet': ''}
            elif line.startswith('Sources:'):
                break # Stop parsing when sources section begins
            elif current_item and not current_item['snippet']:
                # Try to extract link from the line if it contains a URL
                link_match = re.search(r'(https?://\S+)', line)
                if link_match:
                    current_item['link'] = link_match.group(1).strip(')') # Remove trailing parenthesis if any
                else:
                    current_item['snippet'] += line + ' ' # Append to snippet
        if current_item:
            results.append(current_item)

        # Further refine parsing for snippet and link from sources if needed
        # For now, we rely on the initial parsing.

        return results
    except Exception as e:
        print(f"Google 검색 중 오류 발생: {e}")
        return []

# HTML 파일 생성 함수
def generate_html_output(query, naver_results, google_results):
    html_content = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>'{query}' 통합 검색 결과</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }}
        .container {{ max-width: 900px; margin: auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #0056b3; border-bottom: 2px solid #eee; padding-bottom: 10px; text-align: center; }}
        .section {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }}
        h2 {{ color: #007bff; margin-top: 0; }}
        .item {{ margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px dashed #eee; }}
        .item:last-child {{ border-bottom: none; }}
        a {{ color: #007bff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        p {{ line-height: 1.6; margin: 5px 0; }}
        .source {{ font-size: 0.9em; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>'{query}' 통합 검색 결과</h1>

        <div class="section">
            <h2>네이버 검색 결과</h2>
'''
    if naver_results:
        for item in naver_results:
            title = html.unescape(re.sub(r'<[^>]+>', '', item.get('title', 'N/A')))
            link = item.get('link', '#')
            description = html.unescape(re.sub(r'<[^>]+>', '', item.get('description', 'N/A')))
            html_content += f'''
            <div class="item">
                <h3><a href="{link}" target="_blank">{title}</a></h3>
                <p>{description}</p>
            </div>
            '''
    else:
        html_content += "<p>네이버 검색 결과가 없습니다.</p>"

    html_content += f'''
        </div>

        <div class="section">
            <h2>구글 검색 결과</h2>
'''
    if google_results:
        for item in google_results:
            title = html.unescape(item.get('title', 'N/A'))
            link = item.get('link', '#')
            snippet = html.unescape(item.get('snippet', 'N/A'))
            html_content += f'''
            <div class="item">
                <h3><a href="{link}" target="_blank">{title}</a></h3>
                <p>{snippet}</p>
                <p class="source">출처: <a href="{link}" target="_blank">{link}</a></p>
            </div>
            '''
    else:
        html_content += "<p>구글 검색 결과가 없습니다.</p>"

    html_content += f'''
        </div>
    </div>
</body>
</html>'''
    return html_content
    if naver_results:
        for item in naver_results:
            title = html.unescape(re.sub(r'<[^>]+>', '', item.get('title', 'N/A')))
            link = item.get('link', '#')
            description = html.unescape(re.sub(r'<[^>]+>', '', item.get('description', 'N/A')))
            html_content += f'''
            <div class="item">
                <h3><a href="{link}" target="_blank">{title}</a></h3>
                <p>{description}</p>
            </div>
            '''
    else:
        html_content += "<p>네이버 검색 결과가 없습니다.</p>"

    html_content += f'''
        </div>

        <div class="section">
            <h2>구글 검색 결과</h2>
'''
    if google_results:
        for item in google_results:
            title = html.unescape(item.get('title', 'N/A'))
            link = item.get('link', '#')
            snippet = html.unescape(item.get('snippet', 'N/A'))
            html_content += f'''
            <div class="item">
                <h3><a href="{link}" target="_blank">{title}</a></h3>
                <p>{snippet}</p>
                <p class="source">출처: <a href="{link}" target="_blank">{link}</a></p>
            </div>
            '''
    else:
        html_content += "<p>구글 검색 결과가 없습니다.</p>"

    html_content += f'''
        </div>
    </div>
</body>
</html>'''
    return html_content
