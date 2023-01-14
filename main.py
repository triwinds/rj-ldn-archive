import requests
from pathlib import Path
import json


last_ldn_info_path = Path('last_ldn_info.json')


def load_last_ldn_info():
    if last_ldn_info_path.exists():
        with open(last_ldn_info_path, 'r') as f:
            return json.load(f)
    return {}


def get_ldn_info():
    resp = requests.get('https://raw.githubusercontent.com/wiki/Ryujinx/Ryujinx/'
                        'Multiplayer-(LDN-Local-Wireless)-Guide.md')
    lines = resp.text.splitlines()
    start_line, end_line = 0, 9999
    i = 0
    version = None
    for line in lines:
        i += 1
        if line.startswith('## Download LDN'):
            start_line = i
            version = line[15:-5].strip()
        elif line.startswith('## Table of Contents'):
            end_line = i - 2
            break
    lines = lines[start_line:end_line]
    download_url = {}
    for line in lines:
        if not line.startswith('### '):
            continue
        sp = line.split(':', maxsplit=1)
        download_url[sp[0][4:].strip()] = sp[1].strip()
    print({'version': version, 'download_url': download_url})
    return {'version': version, 'download_url': download_url}


def download_windows_package(ldn_info):
    download_url_map = ldn_info['download_url']
    download_url = download_url_map.get('Windows (Avalonia UI)') or download_url_map.get('Windows')
    if not download_url:
        raise RuntimeError('No download url found')
    print(f'download_url: {download_url}')
    download_file(download_url, f'download/ldn-{ldn_info["version"]}.zip')


def download_file(url, local_filename):
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    headers = {'user-agent': ua}
    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


def main():
    last_ldn_info = load_last_ldn_info()
    latest_ldn_info = get_ldn_info()
    if last_ldn_info.get('version') != latest_ldn_info.get('version'):
        print('download_windows_package')
        download_windows_package(latest_ldn_info)
        with open(last_ldn_info_path, 'w') as f:
            return json.dump(latest_ldn_info, f)


if __name__ == '__main__':
    main()
