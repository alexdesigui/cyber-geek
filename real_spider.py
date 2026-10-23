import asyncio
import random
from playwright.async_api import async_playwright

async def run_scraper():
    async with async_playwright() as p:
        # 启动无头浏览器
        browser = await p.chromium.launch(headless=True)
        
        # 伪造浏览器指纹
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN"
        )
        page = await context.new_page()
        
        # 拦截图片和视频，只抓文本，提升速度
        await page.route("**/*", lambda route: asyncio.create_task(
            route.abort() if route.request.resource_type in ["image", "media", "font"] else route.continue_()
        ))

        print("🚀 正在启动隐形浏览器，请求目标网站...")
        try:
            # 访问动态加载的靶场
            await page.goto("http://quotes.toscrape.com/js/", timeout=30000)
            
            # 等待页面元素加载
            await page.wait_for_selector('.quote', timeout=10000)
            
            # 随机停顿
            delay = random.uniform(2.0, 4.0)
            print(f"⏳ 假装人类思考，随机停顿 {delay:.2f} 秒...")
            await page.wait_for_timeout(delay * 1000)

            # 提取数据
            quotes = await page.locator('.quote').all()
            print(f"✅ 成功获取到 {len(quotes)} 条数据！\n")

            for i, quote in enumerate(quotes):
                text = await quote.locator('.text').inner_text()
                author = await quote.locator('.author').inner_text()
                print(f"[{i+1}] {author}: {text}")

        except Exception as e:
            print(f"❌ 抓取失败: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())