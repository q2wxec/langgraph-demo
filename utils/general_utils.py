from urllib.parse import urlparse
import time
import os
import configparser


__all__ = [ 'isURL',  'get_time',  'truncate_filename', 'read_files_with_extensions','get_config','is_valid_json_array','load_prompt']

BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, os.pardir)))


def isURL(string):
    result = urlparse(string)
    return result.scheme != '' and result.netloc != ''


def get_time(func):
    def inner(*arg, **kwargs):
        s_time = time.time()
        res = func(*arg, **kwargs)
        e_time = time.time()
        print('函数 {} 执行耗时: {} 秒'.format(func.__name__, e_time - s_time))
        return res
    return inner


def truncate_filename(filename, max_length=200):
    # 获取文件名后缀
    file_ext = os.path.splitext(filename)[1]

    # 获取不带后缀的文件名
    file_name_no_ext = os.path.splitext(filename)[0]

    # 计算文件名长度，注意中文字符
    filename_length = len(filename.encode('utf-8'))

    # 如果文件名长度超过最大长度限制
    if filename_length > max_length:
        # 生成一个时间戳标记
        timestamp = str(int(time.time()))
        # 截取文件名
        while filename_length > max_length:
            file_name_no_ext = file_name_no_ext[:-4]
            new_filename = file_name_no_ext + "_" + timestamp + file_ext
            filename_length = len(new_filename.encode('utf-8'))
    else:
        new_filename = filename

    return new_filename

def read_files_with_extensions():
    # 获取当前脚本文件的路径
    current_file = os.path.abspath(__file__)

    # 获取当前脚本文件所在的目录
    current_dir = os.path.dirname(current_file)

    # 获取项目根目录
    project_dir = os.path.dirname(current_dir)

    directory = project_dir + '/data'
    print(f'now reading {directory}')
    extensions = ['.md', '.txt', '.pdf', '.jpg', '.docx', '.xlsx', '.eml', '.csv'] 
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(tuple(extensions)):
                file_path = os.path.join(root, file)
                yield file_path



def get_config(section, option, fallback=''):
    BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, os.pardir)))
    config = configparser.ConfigParser()
    config.read(os.path.join(BASE_DIR,'config.ini'))
    return config.get(section, option, fallback=fallback)

import json

def is_valid_json_array(json_string):
    """
    判断给定的字符串是否是一个有效的JSON数组。

    参数:
        json_string (str): 待验证的字符串。

    返回:
        bool: 如果字符串是有效的JSON数组，返回True；否则返回False。
    """
    try:
        # 尝试解析字符串为JSON
        data = json.loads(json_string)
        
        # 检查解析结果是否为列表
        if isinstance(data, list):
            return True
        else:
            return False
    except json.JSONDecodeError:
        # 解析失败，说明不是有效的JSON
        return False
    
def load_prompt(path):
    with open(os.path.join(BASE_DIR, path), 'r', encoding='utf-8') as f:
        return f.read()