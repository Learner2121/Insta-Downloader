from pyrogram import filters, Client as Mbot
import bs4, requests,re
import wget,os,traceback
from bot import LOG_GROUP,DUMP_GROUP
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
#    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Length": "99",
    "Origin": "https://saveig.app",
    "Connection": "keep-alive",
    "Referer": "https://saveig.app/en",
}
@Mbot.on_message(filters.regex(r'https?://.*instagram[^\s]+') & filters.incoming, group=1)
async def link_handler(Mbot, message):
    link = message.matches[0].group(0)
    try:
        m = await message.reply_text("⏳")
        url= link.replace("instagram.com","ddinstagram.com")
        url=url.replace("==","%3D%3D")
        if url.endswith("="):
           dump_file=await message.reply_video(url[:-1])
        else:
            dump_file=await message.reply_video(url)
        if 'dump_file' in locals():
           await dump_file.forward(DUMP_GROUP)
        await m.delete()
    except Exception as e:
        try:
            if "/reel/" in url:
               ddinsta=True 
               getdata = requests.get(url).text
               soup = bs4.BeautifulSoup(getdata, 'html.parser')
               meta_tag = soup.find('meta', attrs={'property': 'og:video'})
               try:
                  content_value = meta_tag['content']
               except:
                   pass 
               if not meta_tag:
                  ddinsta=False
                  meta_tag = requests.post("https://saveig.app/api/ajaxSearch", data={"q": link, "t": "media", "lang": "en"}, headers=headers)
                  print(meta_tag)
                  if meta_tag.ok:
                     res=meta_tag.json()
                     print(res)
                #     await message.reply(res)
                     meta=re.findall(r'href="(https?://[^"]+)"', res['data']) 
                     content_value = meta[0]
                  else:
                      return await message.reply("oops something went wrong")
               try:
                   if ddinsta:
                      dump_file=await message.reply_video(f"https://ddinstagram.com{content_value}")
                   else:
                       dump_file=await message.reply_video(content_value)
               except:
                   downfile=wget.download(content_value)
                   dump_file=await message.reply_video(downfile) 
            elif "/p/" in url:
                 getdata = requests.get(url).text
                 soup = bs4.BeautifulSoup(getdata, 'html.parser')
                 meta_tag = soup.find('meta', attrs={'property': 'og:video'})
                 if not meta_tag:
                    meta_tag = soup.find('meta', attrs={'property': 'og:image'})
                    content_value = meta_tag['content']
                    downrm=wget.download(f"https://ddinstagram.com{content_value}")
                    os.rename(downrm,f"{downrm}.png")
                    downfile=f"{downrm}.png"
                    dump_file=await message.reply_photo(downfile)
                 else:
                     content_value = meta_tag['content']
                     try:
                         dump_file=await message.reply_photo(f"https://ddinstagram.com{content_value}")
                     except:
                         downfile=wget.download(f"https://ddinstagram.com{content_value}")
                         dump_file=await message.reply_video(downfile)
            elif "stories" in url:
                  meta_tag = requests.post("https://saveig.app/api/ajaxSearch", data={"q": link, "t": "media", "lang": "en"}, headers=headers)
                  if meta_tag.ok:
                     res=meta_tag.json()
                     meta=re.findall(r'href="(https?://[^"]+)"', res['data']) 
                  else:
                      return await message.reply("oops something went wrong")
                  content_value = meta[0]
                  dump_file=await message.reply_video(content_value)
        except Exception as e:
          #  await message.reply_text(f"https://ddinstagram.com{content_value}")
            if LOG_GROUP:
               await Mbot.send_message(LOG_GROUP,f"Instagram {e} {link}")
               await Mbot.send_message(LOG_GROUP, traceback.format_exc())
          #     await message.reply(tracemsg)
            ##optinal 
            await message.reply(f"400: Sorry, Unable To Find It  try another or report it  to @masterolic or support chat @spotify_supportbot 🤖  ")

        finally:
            if 'dump_file' in locals():
               if DUMP_GROUP:
                  await dump_file.forward(DUMP_GROUP)
            await m.delete()
            if 'downfile' in locals():
                os.remove(downfile)
                
