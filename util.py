import time
import csv
import string
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions


# 获取页面链接（统一处理Edge与Chrome）
def get_urls(browser, config):
    page = 1
    data_id_list = []
    
    try:
        browser.get(config.url)
        browser.set_page_load_timeout(config.timeout)
        while True:
            print(f'Page: {page}')
            try:
                # 寻找页面中的URL
                accept_div = browser.find_element(By.ID, f"accept-{config.level}")
                li_elements = accept_div.find_elements(By.CSS_SELECTOR, "div.note.undefined")
                for li in li_elements:
                    a_element = li.find_element(By.TAG_NAME, "h4").find_element(By.TAG_NAME, "a")
                    data_id_list.append(a_element.get_attribute("href"))

                # 处理下一页按钮
                try:
                    next_btn = accept_div.find_elements(By.CLASS_NAME, "right-arrow")[0].find_element(By.TAG_NAME, "a")
                    browser.execute_script("arguments[0].click();", next_btn)
                    time.sleep(config.wait_time)
                    page += 1
                except Exception:
                    break  # 没有下一页时退出循环
            except Exception as e:
                print(f"Error while fetching URLs: {e}")
                break  # 出现错误时退出循环
    except Exception as e:
        print(f"Error while opening the browser: {e}")
    return list(set(data_id_list))  # 去重并返回结果


# 获取详细信息（统一处理Edge与Chrome）
def get_information(browser, url, config):
    try:
        browser.get(url)
        browser.set_page_load_timeout(config.timeout)
        time.sleep(config.wait_time)
        
        title = string.capwords(browser.find_element(By.CLASS_NAME, "citation_title").text)
        author = string.capwords(browser.find_element(By.CSS_SELECTOR, "div.forum-authors.mb-2").text).split(', ')
        abstract = string.capwords(browser.find_element(By.CSS_SELECTOR, "div.note-content-value.markdown-rendered").text)
        keywords = string.capwords(browser.find_element(By.CSS_SELECTOR, "span.note-content-value").text).split(', ')
        
        # 获取评分与置信度
        ratings, confidences = [], []
        forum_replies = browser.find_elements(By.CSS_SELECTOR, "div#forum-replies > div.note")
        for reply in forum_replies:
            note_contents = reply.find_elements(By.CSS_SELECTOR, "strong.note-content-field.disable-tex-rendering")
            for content in note_contents:
                if "Rating:" in content.text:
                    ratings.append(int(content.find_element(By.XPATH, "./following-sibling::*[1]").text[0]))
                elif "Confidence:" in content.text:
                    confidences.append(int(content.find_element(By.XPATH, "./following-sibling::*[1]").text[0]))

        return {
            "Title": title,
            "Authors": ', '.join(author),
            "Abstract": abstract,
            "Keywords": ', '.join(keywords),
            "Ratings": ', '.join(map(str, ratings)) if ratings else 'No Ratings',
            "Confidences": ', '.join(map(str, confidences)) if confidences else 'No Confidences'
        }
    except Exception as e:
        print(f"Error while extracting information from {url}: {e}")
        return None


# 单线程爬取链接并获取信息
def crawl_meta(config):
    executable_path = config.executable_path
    service = Service(executable_path)
    options = EdgeOptions() if config.browser == "edge" else ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    browser = webdriver.Edge(service=service, options=options) if config.browser == "edge" else webdriver.Chrome(service=ChromeService(executable_path), options=options)
    browser.set_page_load_timeout(config.timeout)
    browser.delete_all_cookies()
    try:
        urls = get_urls(browser, config)
        print(f"Number of submissions: {len(urls)}")
        
        # 保存URL
        with open(config.save_urls, 'w') as f:
            for url in urls:
                f.write(f'{url}\n')
        
        if config.check == 0:
            # 获取每个链接的详细信息
            with open(config.save_informations, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ["Title", "Authors", "Abstract", "Keywords", "Ratings", "Confidences"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                
                for url in urls:
                    info = get_information(browser, url, config)
                    if info:
                        writer.writerow(info)
                        print(info)
                    else:
                        print(f"Failed to retrieve data from {url}")
    except Exception as e:
        print(f"Error during meta crawling: {e}")
    finally:
        browser.quit()


# 并行爬取（多个浏览器实例）
def crawl_meta_parallel(config):
    """Parallel crawl using multiple browsers"""
    urls = []
    with open(config.save_urls) as f:
        urls = [url.strip() for url in f.readlines()[config._from:]]
    
    chunk_size = len(urls) // config.num_browsers
    url_chunks = [urls[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]

    with concurrent.futures.ThreadPoolExecutor(max_workers=config.num_browsers) as executor:
        futures = [executor.submit(process_url_chunk, chunk, config) for chunk in url_chunks]
        for future in futures:
            future.result()  # Ensure all tasks complete


# 并行处理URL块
def process_url_chunk(urls_chunk, config):
    executable_path = config.executable_path
    service = Service(executable_path)
    options = EdgeOptions() if config.browser == "edge" else ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    
    browser = webdriver.Edge(service=service, options=options) if config.browser == "edge" else webdriver.Chrome(service=ChromeService(executable_path), options=options)
    browser.delete_all_cookies()

    try:
        fieldnames = ["Title", "Authors", "Abstract", "Keywords", "Ratings", "Confidences"]
        with open(config.save_informations, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            with open(config.no_get, 'a', encoding='utf-8') as no_get_file:
                for url in urls_chunk:
                    info = get_information(browser, url, config)
                    if info:
                        writer.writerow(info)
                        print(info)
                    else:
                        no_get_file.write(f"{url}\n")
                        print(f"Failed to retrieve data from {url}")
    except Exception as e:
        print(f"Error during processing chunk: {e}")
    finally:
        browser.quit()
