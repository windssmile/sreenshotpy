import tkinter as tk
from tkinter import ttk, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import datetime
import re
from urllib.parse import urlparse

def get_filename(url):
    # 提取主域名
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc
    # 只保留字母数字和点
    safe_netloc = re.sub(r'[^a-zA-Z0-9.]', '_', netloc)
    # 当前时间
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return f"screenshot_{safe_netloc}_{now}.png"

def screenshot_webpage(url, output_path, mode):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    if mode == "iPhone":
        chrome_options.add_argument('--window-size=393,800')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1')
    else:
        chrome_options.add_argument('--window-size=1920,800')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(5)

    # 刷新页面
    driver.refresh()
    time.sleep(3)

    # 模拟滚动到底部，确保动态内容加载
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    # 获取页面实际高度
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    if scroll_height < 800:
        scroll_height = 800
    driver.set_window_size(driver.get_window_size()['width'], scroll_height)
    time.sleep(1)

    # 回到顶部，防止顶部被裁剪
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)

    # 隐藏滚动条
    driver.execute_script("document.body.style.overflow='hidden';")

    # 尝试移除常见蒙层
    js_remove_mask = """
    var keywords = ['modal', 'mask', 'overlay', 'popup', 'dialog', 'cover', 'shade'];
    var all = document.querySelectorAll('*');
    for (var i=0; i<all.length; i++) {
        var el = all[i];
        var cls = (el.className || '') + ' ' + (el.id || '');
        for (var j=0; j<keywords.length; j++) {
            if (cls.toLowerCase().indexOf(keywords[j]) !== -1) {
                el.style.display = 'none';
            }
        }
    }
    """
    driver.execute_script(js_remove_mask)

    driver.save_screenshot(output_path)
    driver.quit()

def start_screenshot():
    url = url_entry.get()
    mode = mode_var.get()
    if not url:
        messagebox.showerror("错误", "请输入网址")
        return
    filename = get_filename(url)
    try:
        screenshot_webpage(url, filename, mode)
        status_label.config(text=f"{filename} 已保存")
    except Exception as e:
        status_label.config(text=f"截图失败: {e}")

# 创建GUI窗口
root = tk.Tk()
root.title("网页截图工具")

tk.Label(root, text="请输入网址:").grid(row=0, column=0, padx=10, pady=10)
url_entry = tk.Entry(root, width=40)
url_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="截图模式:").grid(row=1, column=0, padx=10, pady=10)
mode_var = tk.StringVar(value="普通浏览器")
mode_combo = ttk.Combobox(root, textvariable=mode_var, values=["普通浏览器", "iPhone"], state="readonly")
mode_combo.grid(row=1, column=1, padx=10, pady=10)

screenshot_btn = tk.Button(root, text="开始截图", command=start_screenshot)
screenshot_btn.grid(row=2, column=0, columnspan=2, pady=20)

status_label = tk.Label(root, text="", fg="green")
status_label.grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()