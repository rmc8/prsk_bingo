import os
import random
import pathlib
import datetime

import requests
import pandas as pd
from tqdm import tqdm
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

URL: str = "https://api.pjsek.ai/database/master/musics?$limit=2048&$skip=0&"
jacket_url: str = "https://storage.sekai.best/sekai-assets/music/jacket/jacket_s_{music_num:03}_rip/jacket_s_{music_num:03}.webp"
output_dir: str = "./bingo/"
os.makedirs(output_dir, exist_ok=True)
with open("./src/template.html", mode="r", encoding="utf-8") as f:
    HTML: str = f.read()


def web_driver(headless: bool = False, log_lv: int = 3) -> Chrome:
    # Options
    options = Options()
    options.add_argument(f"log-level={log_lv}")

    # Headless
    if headless:
        options.add_argument("--headless")

    # Return the driver
    return Chrome(
        ChromeDriverManager().install(),
        options=options,
    )


def epoc2dt(epoc):
    return datetime.datetime.fromtimestamp(epoc / 1000)


def main():
    r = requests.get(URL)
    music_list: dict = r.json()["data"]
    odf = pd.DataFrame(music_list)
    odf["pubDate"] = odf.publishedAt.map(epoc2dt)
    df = odf[odf["pubDate"] <= datetime.datetime.now()]
    music_id_list: list = df["id"].tolist()
    try:
        driver = web_driver(headless=True)
        driver.set_window_size(628, 628)
        for i in tqdm(range(1, 21)):
            music_list: list = random.sample(music_id_list, 24)
            data_list: list = []
            cnt: int = 0
            while music_list:
                if cnt != 12:
                    music_num = music_list.pop()
                    data: str = f'<td><img src="{jacket_url.format(music_num=music_num)}"></td>'
                    data_list.append(data)
                else:
                    data_list.append('<td><div class="free">★</div></td>')
                cnt += 1
            html = HTML.replace("{{data}}", "".join(data_list))
            p = pathlib.Path("./tmp.html")
            html_path = p.resolve()
            with open(html_path, mode="w", encoding="utf-8") as f:
                print(html, file=f)
            driver.get(f"file:///{html_path}")
            # elm = driver.find_element(By.CLASS_NAME, "wrapper")
            p = pathlib.Path(f"./bingo/bingo_{i:02}.png")
            driver.save_screenshot(str(p.resolve()))
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
