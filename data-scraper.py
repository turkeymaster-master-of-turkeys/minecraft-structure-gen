import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

async def download_all_mcbuild(start: int = 0):

  download_link = "https://mcbuild.org/download"

  headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
  }

  max_index = 40000
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


if __name__ == "__main__":
  asyncio.run(download_all_mcbuild())
