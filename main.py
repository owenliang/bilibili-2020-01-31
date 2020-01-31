import asyncio
import aiohttp
from bs4 import BeautifulSoup

# 定时下载"当前在线页面"
async def cron_online_list():
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get('https://www.bilibili.com/video/online.html') as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    ebox_list = soup.find_all('div', attrs={'class':'ebox'})
                    for ebox in ebox_list:
                        # 找链接和标题
                        a = ebox.find('a')
                        href = 'https:' + a.attrs['href']
                        title = a.attrs['title']
                        # 找在线人数
                        b = ebox.select('p.ol b')
                        online = b[0].get_text()
                        # 生成下载任务
                        detail_task = {
                            'title': title,
                            'href': href,
                            'online': online,
                        }
                        asyncio.create_task(detail_download(session, detail_task))
            except Exception as e:
                print(e)
            await asyncio.sleep(5)

# 详情页下载协程
async def detail_download(session, task):
    try:
        async with session.get(task['href']) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            info_box = soup.select_one('div#v_desc .info')
            if info_box:
                task['info'] = info_box.get_text()
            else:
                task['info'] = '这个家伙很懒'
            print(task)
    except Exception as e:
        pass

asyncio.run(cron_online_list())
