import os
import random
import pathlib
import datetime
from typing import List, Tuple

import fire
import requests
import pandas as pd
from tqdm import tqdm
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

PJSEK_MUSIC_URL: str = (
    "https://api.pjsek.ai/database/master/musics?$limit=2048&$skip=0&"
)
JACKET_URL: str = "https://storage.sekai.best/sekai-assets/music/jacket/jacket_s_{music_num:03}_rip/jacket_s_{music_num:03}.webp"
BINGO_DIR: str = "./bingo/"
TEMPLATE_PATH: str = "./src/template.html"
WINDOW_SIZE: Tuple[int, int] = (644, 761)


def web_driver(headless: bool = False, log_level: int = 3) -> Chrome:
    """Selenium WebDriverを作成する."""
    options = Options()
    options.add_argument(f"log-level={log_level}")

    if headless:
        options.add_argument("--headless")

    return Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )



def epoch_to_datetime(epoch: int) -> datetime.datetime:
    """エポック秒を日時に変換する."""
    return datetime.datetime.fromtimestamp(epoch / 1000)


def create_bingo_card(
    driver: Chrome, music_id_list: List[int], html_path: pathlib.Path
) -> None:
    """ビンゴカードを生成する."""
    music_list = random.sample(music_id_list, 24)
    data_list: list = []
    cnt: int = 0
    while music_list:
        if cnt != 12:
            music_num = music_list.pop()
            data = f'<td><img src="{JACKET_URL.format(music_num=music_num)}"></td>'
            data_list.append(data)
        else:
            data_list.append('<td><div class="free">★</div></td>')
        cnt += 1
    with open(TEMPLATE_PATH, mode="r", encoding="utf-8") as f:
        html = f.read().replace("{{data}}", "".join(data_list))
    with open(html_path, mode="w", encoding="utf-8") as f:
        print(html, file=f)
    driver.get(f"file:///{html_path}")


def save_bingo_card(driver: Chrome, output_path: str) -> None:
    """ビンゴカードをスクリーンショットとして保存する."""
    p = pathlib.Path(output_path)
    driver.save_screenshot(str(p.resolve()))


def main(n: int = 20) -> None:
    r = requests.get(PJSEK_MUSIC_URL)
    music_list = r.json()["data"]
    odf = pd.DataFrame(music_list)
    odf["pubDate"] = odf.publishedAt.map(epoch_to_datetime)
    df = odf[odf["pubDate"] <= datetime.datetime.now()]
    music_id_list = df["id"].tolist()
    os.makedirs(BINGO_DIR, exist_ok=True)
    driver = web_driver(headless=False)
    try:
        driver.set_window_size(*WINDOW_SIZE)
        html_path = pathlib.Path("./tmp.html").resolve()
        for i in tqdm(range(1, n + 1)):
            create_bingo_card(driver, music_id_list, html_path)
            save_bingo_card(driver, f"{BINGO_DIR}bingo_{i:04}.png")
        os.remove(html_path)
    finally:
        driver.quit()


if __name__ == "__main__":
    fire.Fire(main)
