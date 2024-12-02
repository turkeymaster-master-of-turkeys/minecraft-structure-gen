import asyncio
import os
import re
import time
import webbrowser

import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from pynput.keyboard import Controller, Key


async def download_all_mcbuild(start: int = 0):
  download_link = "https://mcbuild.org/download"

  headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
  }

  max_index = 19000
  num_browsers = 50

  async def download_offset(offset: int):
    async with async_playwright() as p:
      browser = await p.chromium.launch(headless=True)
      context = await browser.new_context(accept_downloads=True, extra_http_headers=headers)
      page = await context.new_page()

      for i in range(offset + start, max_index, num_browsers):
        try:
          await page.goto(f"{download_link}/schematic={i}", referer=download_link)
          html_content = await page.content()
          if "File not available or link expired." in html_content:
            continue
          download = await page.wait_for_event("download", timeout=12000)
          filename = download.suggested_filename.replace(" - (mcbuild_org)", "")
          if filename.endswith(".schematic"):
            await download.save_as(f"data/mcbuild/{filename}")
            print(f"File {i} downloaded: {filename}")
        except PlaywrightTimeoutError:
          pass

      await context.close()
      await browser.close()

  tasks = [download_offset(i) for i in range(num_browsers)]
  await asyncio.gather(*tasks)


def download_all_minecraft_schematic(start: int = 0):
  schematics_link = "https://www.minecraft-schematics.com/schematic"
  keyboard = Controller()

  time.sleep(2)

  for i in range(start, 30000):
    webbrowser.open(f"{schematics_link}/{i}/download/action/?type=schematic")
    time.sleep(0.25)
    keyboard.press(Key.ctrl)
    keyboard.press('w')
    keyboard.release('w')
    keyboard.press('w')
    keyboard.release('w')
    keyboard.release(Key.ctrl)
    time.sleep(0.25)


def rename_minecraft_schematic_files():
  path = "data/minecraft-schematic/"
  files = os.listdir(path)
  for file in files:
    split = file.split(".")
    number = split[0]
    if number.isnumeric() and len(split) > 1:
      extension = split[1]
      response = requests.get(f"https://www.minecraft-schematics.com/schematic/{number}/")
      if response.status_code != 200:
        continue
      html_content = response.text
      soup = BeautifulSoup(html_content, "html.parser")
      category_attribute = soup.find("i", {"class": "fa fa-th-large"})
      if not category_attribute:
        continue
      category = category_attribute.find_next("td").get_text(strip=True)
      name = soup.find("h1").get_text(strip=True)
      os.makedirs(f"data/minecraft-schematic/{category}/", exist_ok=True)
      invalid_chars = r'[<>:"/\\|?*\0]'
      sanitised = re.sub(invalid_chars, "_", name).strip().replace("\t"," ")
      print(f"Replacing {number} with {sanitised}")
      os.replace(f"data/minecraft-schematic/{number}.{extension}", f"data/minecraft-schematic/{category}/{sanitised}.{extension}")

if __name__ == "__main__":
  rename_minecraft_schematic_files()
