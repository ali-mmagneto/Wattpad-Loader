import argparse
import bs4
import requests
import re
import os
from pyrogram import Client, filters
import aspose.words as aw
from ebooklib import epub
from datetime import date



base_apiV2_url = "https://www.wattpad.com/apiv2/"
base_apiV3_url = "https://www.wattpad.com/api/v3/"
dev_error_msg = "Please check the url again, for valid story id. Contact the developer if you think this is a bug."
"""
https://www.wattpad.com/api/v3/stories/{{story_id}}?drafts=0&mature=1&include_deleted=1&fields=id,title,createDate,modifyDate,voteCount,readCount,commentCount,description,url,firstPublishedPart,cover,language,isAdExempt,user(name,username,avatar,location,highlight_colour,backgroundUrl,numLists,numStoriesPublished,numFollowing,numFollowers,twitter),completed,isPaywalled,paidModel,numParts,lastPublishedPart,parts(id,title,length,url,deleted,draft,createDate),tags,categories,rating,rankings,tagRankings,language,storyLanguage,copyright,sourceLink,firstPartId,deleted,draft,hasBannedCover,length
"""

def get_chapter_id(url):
    """Extracts the chapter ID from the given URL."""
    search_id = re.compile(r'\d{5,}')
    id_match = search_id.search(url)
    if id_match:
        return id_match.group()
    return None


def download_webpage(url):
    """Downloads the webpage content from the given URL."""
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        res.raise_for_status()
        return res.text
    except requests.exceptions.RequestException as exc:
        print("There was a problem: %s" % (exc))
        return None


def extract_useful_data(json_data):
    """Extracts useful data from the JSON response."""
    summary = json_data.get('description', '')
    tags = json_data.get('tags', '')
    chapters = json_data.get('parts', '')
    storyName = json_data.get('title', '')
    author = json_data.get('user', '')
    cover = json_data.get('cover', '')
    return summary, tags, chapters, storyName, author, cover


def save_kitap_to_formats(file_name, story_name, author, cover, tags, summary, chapters):
    """Saves the HTML file with the given data."""
    name = file_name.replace(" ", ".").replace(":", "").replace("|", "").replace("..",".")
    file = open(name, 'w', encoding='utf-8')
    file_name = name
    file.write(f"""
        <html>
        <head>
            <meta name='title' content='{story_name}'>
            <meta name='author' content='{author["name"]}' >
        </head>
        <body>
        <div style="text-align:center;">
            <img src="{cover}" alt="cover_image">
        </div>
        <br>
        <h5 align="center">{story_name}</h5>
        <h6 align="center">By {author["name"]} : <a href="https://www.wattpad.com/user/{author["username"]}">{author["username"]}</a></h6>

        <div align="center">Tags: {tags} </div>
        <br><br>
        <div align="center">{summary}</div>
        
        <br><br>
        <div align="left">
            <h6>
                * İyi Okumalar...
                * Bu Kitap @WattpadloaderBot Kullanılarak İndirilmiştir..<br>
            </h6>
        </div>
    """)

    for i, chapter in enumerate(chapters):
        print(f"Getting Chapter {i + 1}....")
        chapter_url = base_apiV2_url + f"storytext?id={chapter['id']}"
        chapter_content = download_webpage(chapter_url)
        if chapter_content:
            soup_res = bs4.BeautifulSoup(chapter_content, 'html.parser')
            file.write(f"""
                <br><br>
                <h2>'{chapter['title']}'</h2><br><br>
                {soup_res.prettify()}
            """)
    file.write("</body></html>")
    file.close()
    print(f"Saved {file_name}")
    return file_name
    
def epubyap(name):
    book = epub.EpubBook()
    output_file = name.split(".html")[0] + ".epub"
    with open(name, 'r', encoding='utf-8') as dosya:
        content = dosya.read()
        print(content)
    
    # create chapter
    c1 = epub.EpubHtml(title="Intro", file_name="chap_01.xhtml", lang="hr")
    c1.content = (content)
    book.add_item(c1)
    try:
        epub.write_epub(output_file, book, {}) 
    except Exception as e:
        print(e) 
        output_file = "yok" 
    return output_file

async def main(id):
    story_id = id
    # Getting JSON data from Wattpad API.
    story_info_url = base_apiV3_url + f"stories/{story_id}?drafts=0&mature=1&include_deleted=1&fields=id,title,createDate,modifyDate,description,url,firstPublishedPart,cover,language,user(name,username,avatar,location,numStoriesPublished,numFollowing,numFollowers,twitter),completed,numParts,lastPublishedPart,parts(id,title,length,url,deleted,draft,createDate),tags,storyLanguage,copyright"
    json_data  = requests.get(story_info_url, headers={'User-Agent': 'Mozilla/5.0'}).json()
    try:
        if json_data.get('result') == 'ERROR':
            error_message = json_data.get('message', 'Unknown error')
            print(f"Error: {error_message}")
            print(dev_error_msg)
            return
        
        if json_data.get('error_type') :
            error_message = json_data.get('message', 'Unknown error')
            print(f"Error: {error_message}")
            print(dev_error_msg)
            return
        
    
        if json_data.get('result') == 'ERROR':
            error_message = json_data.get('message', 'Unknown error')
            print(f"API Error: {error_message}")
            return
    except Exception as exc:
        print(f"Error retrieving JSON data from the API: {exc}")
        return

    # Extracting useful data from JSON.
    summary, tags, chapters, story_name, author, cover = extract_useful_data(json_data)

    # Saving HTML file.
    html_file_name = f"{story_name}.html"
    html_file_name = html_file_name.replace('/', ' ')
    tarih = date.today() 
    yazn = author["name"]
    capt = f"{yazn} - {story_name}\n\n#wattpad {tarih}"
    html = save_kitap_to_formats(html_file_name, story_name, author, cover, tags, summary, chapters)
    epub = epubyap(html)

    return epub, html, capt

@Client.on_message(filters.command("dl"))
async def wpdl(bot, message):
    id = message.text.split(" ")[1]
    try:
        m = await message.reply_text("Kitap İndiriliyor..")
        epub, html, capt = await main(id)
        await m.edit("Kitap Yükleniyor..")
        if epub != "yok":
            await message.reply_document(
                document=epub,
                caption=capt
            )
            os.remove(epub)
        else:
            await message.reply_text("bu kitabı epub yapamadım..")
        await message.reply_document(
            document=html,
            caption=capt
        )
        os.remove(html)
        await m.edit("Kitap Yüklendi..")
    except Exception as e:
        await message.reply_text(e)
