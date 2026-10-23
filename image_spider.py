import asyncio
import os
import random
import requests
from playwright.async_api import async_playwright

async def run_spider():
    # 1. 自动创建一个下载文件夹
    save_dir = "cyberpunk_images"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"📁 已自动创建文件夹: {save_dir}")

    async with async_playwright() as p:
        # headless=False 会弹出真实的浏览器让你看清它是怎么干活的
        browser = await p.chromium.launch(headless=False)
        
        # 伪造指纹
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900},
        )
        page = await context.new_page()

        print("🚀 正在打开 Pexels 搜索赛博朋克图片...")
        # 去 Pexels 搜索 cyberpunk
        await page.goto("https://www.pexels.com/search/cyberpunk/", timeout=60000)
        
        # 等待图片列表加载出来
        await page.wait_for_selector('article', timeout=15000)

        # 2. 模拟人类往下滚动，触发懒加载
        print("⏳ 模拟人类滚动页面...")
        for _ in range(3):
            await page.mouse.wheel(0, 1000)
            await page.wait_for_timeout(random.uniform(1000, 2000))

        # 3. 抓取所有图片卡片
        articles = await page.locator('article').all()
        print(f"✅ 找到 {len(articles)} 个结果，开始提取前 5 张高清大图...")

        count = 0
        for article in articles:
            if count >= 5: # 咱们先只下 5 张测试一下
                break
            try:
                # 找到卡片里的 img 标签
                img_element = article.locator('img').first
                
                # 提取图片的高清原图链接
                img_url = await img_element.get_attribute('src')
                alt_text = await img_element.get_attribute('alt') or f"img_{count}"
                
                if img_url:
                    print(f"📥 正在下载: {alt_text[:30]}...")
                    # 用 requests 直接下载图片数据
                    img_data = requests.get(img_url, timeout=10).content
                    
                    # 清理文件名中的非法字符
                    safe_name = "".join([c for c in alt_text if c.isalnum() or c==' ']).rstrip()[:10]
                    filepath = os.path.join(save_dir, f"{count+1}_{safe_name}.jpg")
                    
                    # 写入本地文件
                    with open(filepath, 'wb') as f:
                        f.write(img_data)
                    print(f"   -> 保存成功: {filepath}")
                    count += 1

            except Exception as e:
                print(f"   ⚠️ 跳过一张图，原因: {e}")

        print("\n🎉 抓取并下载完毕！快去文件夹里看图吧！")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_spider())
