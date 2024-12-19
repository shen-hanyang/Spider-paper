import sys
from config import Config
from util import crawl_meta

if __name__ == '__main__':
    config = Config()  # 获取配置文件

    if config.browser == "edge":
        crawl_meta(config)
    elif config.browser == "chrome":
        crawl_meta(config)
    else:
        print("无效的浏览器类型，请传入 'chrome' 或 'edge'。")