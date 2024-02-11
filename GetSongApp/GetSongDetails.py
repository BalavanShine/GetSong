from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import quote


def getsong(name, resource):
    url = "https://dev.iw233.cn/Music1/?name={}&type={}".format(quote(name), resource)

    # 创建ChromeOptions对象，设置无头模式
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 设置无头模式

    # 创建Chrome浏览器对象，并将chrome_options传入
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 打开网页
        driver.get(url)

        # 等待动态加载的内容完全加载
        wait = WebDriverWait(driver, 10)  # 最多等待10秒
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "ol")))

        # 定位所有的<li>元素
        li_elements = driver.find_elements(By.CSS_SELECTOR, "ol li")

        # 初始化三个列表
        li_songs = []
        li_singers = []
        li_contents = []

        # 逐个点击<li>元素并提取内容
        for li_element in li_elements:
            # 点击<li>元素
            li_element.click()

            # 等待内容加载完成
            wait.until(EC.visibility_of_element_located((By.ID, "j-src-btn")))

            # 提取歌曲和歌手信息
            song = li_element.find_element(By.CLASS_NAME, "aplayer-list-title").text
            singer = li_element.find_element(By.CLASS_NAME, "aplayer-list-author").text
            li_songs.append(song)
            li_singers.append(singer)

            # 提取内容
            music_link = driver.find_element(By.ID, "j-src-btn").get_attribute('href')
            li_contents.append(music_link)

        return li_songs, li_singers, li_contents
    finally:
        # 关闭浏览器
        driver.quit()

#
# if __name__ == "__main__":
#     li_songs, li_singers, li_contents = get_li_contents(url)
#     for song, singer, content in zip(li_songs, li_singers, li_contents):
#         print(f"Song: {song}, Singer: {singer}, Content: {content}")
