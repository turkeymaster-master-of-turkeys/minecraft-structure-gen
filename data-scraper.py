import asyncio
from playwright.async_api import async_playwright


class DataScraper:
    async def download_file_with_wait(self, url: str) -> bool:
        """
        Downloads a file from a given URL and waits for completion.

        :param url: URL to download
        :return: Whether the file was downloaded
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
        }
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(accept_downloads=True, extra_http_headers=headers)
            page = await context.new_page()
            await page.goto(url, referer='/'.join(url.split('/')[0:-1]) + '/')

            try:
                download = await page.wait_for_event("download")
            except asyncio.TimeoutError:
                print("Error: Timed out")
                return False
            await download.save_as(f"data/{download.suggested_filename}")

            print(f"File downloaded: {download.suggested_filename}")
            await browser.close()
        return True


if __name__ == "__main__":
    scraper = DataScraper()
    asyncio.run(scraper.download_file_with_wait("https://mcbuild.org/download/schematic=18505"))
