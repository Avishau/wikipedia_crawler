import random
import urllib.parse
import urllib.request
import os
from bs4 import BeautifulSoup as bs
import requests

def get_links(soup_obj, url, width, visited):
    links = set()
    all_page_links = soup_obj.find_all('a', href=True)
    for a in all_page_links:
        href = a['href']
        if href.startswith('/wiki') and ":" not in href:
            full_url = urllib.parse.urljoin(url, href)
            if full_url not in visited:
                links.add(full_url)
                visited.add(full_url)
    return random.sample(list(links), min(len(links), width))




def save_image(directory, img_url):
    # res = requests.get(img_url) #returns a response object of a HTTP request
    # #dir is where we'll save the img: ${dir}/img_name, from img_url -> HTTP obj -> img_name extract
    # #TODO: TRY TO USE urllib to short the process
    max_len_name = 100
    # if res.status_code == 200:
    #     img_name = img_url.rsplit('/',1)[-1]
    #     if len(img_name) < max_len_name:
    #         file_path = os.path.join(directory, img_name)
    #         with open(file_path, 'wb') as img_file:
    #             img_file.write(res.content)
    #     #for cases where the name is very long
    #     else:
    #         img_name = img_url.rsplit('/', 2)[1]
    #         shorter_img_name = img_name.rsplit('%')[0]
    #         file_path = os.path.join(directory, shorter_img_name)
    #         with open(file_path, 'wb') as img_file:
    #             img_file.write(res.content)

    #TODO: with urllib:
    img_name = img_url.rsplit('/', 1)[-1]
    if len(img_name) < max_len_name:
        file_path = os.path.join(directory, img_name)
        urllib.request.urlretrieve(img_url, file_path)
    else:
        shorter_img_name = img_name.rsplit('%')[0]
        while True:
            if len(shorter_img_name) < max_len_name:
                break
            else:
                shorter_img_name = shorter_img_name[:len(shorter_img_name)//2]
        img_name = shorter_img_name
        file_path = os.path.join(directory, img_name)
        urllib.request.urlretrieve(img_url, file_path)

def get_images_from_url(soup_obj, url):
    max_num_images = 20
    min_width = 45
    min_height = 45

    all_images = soup_obj.find_all('img', class_='mw-file-element')
    # print(all_images)
    content_images = []
    for img in all_images:
        img_height = int(img.get('width'))
        img_width = int(img.get('height'))
        if img_height > min_height and img_width > min_width:
            src = img.get('src')
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
            # from the url page and the src, create a full path
                src = urllib.parse.urljoin(url, src)
            content_images.append(src)

    return random.sample(content_images, min((len(content_images), max_num_images)))



#Extract from the Soup obj the title tag's content and strips it from spaces
def get_page_title(soup_obj, url):
    return soup_obj.find("title").text.strip()

def get_soup_object(url):
    res = requests.get(url)
    return bs(res.text,'html.parser') if res.status_code == 200 else None


def crawl(url, main_dir, width, depth, visited=None):
    visited = set() if not visited else visited
    visited.add(url)
    #soup obj creation
    soup_obj = get_soup_object(url)
    if not soup_obj:
        return
    #dir creation process
    page_title = get_page_title(soup_obj, url)
    page_dir = os.path.join(main_dir, page_title)
    os.makedirs(page_dir, exist_ok=True)

    #Extraction pictures(urls) from the page represented as soup_obj
    images_from_page = get_images_from_url(soup_obj, url)
    for img in images_from_page:
        save_image(page_dir, img)

    if depth > 0:
        links = get_links(soup_obj, url,width, visited)
        for link in links:
            crawl(link, main_dir, width, depth - 1, visited)



def main():
    width = int(input("Please enter Crawler's width: "))
    assert width > 0, "Enter a positive number"

    depth = int(input("Please enter Crawler's depth: "))
    assert depth >= 0, "Enter a non negative number"

    start_url = input("Please enter a Wikipedia URL to start with: ")
    main_dir = "/home/mefathim/MefathimProjects/wiki_photos"

    crawl(start_url, main_dir, width, depth)

if __name__ == "__main__":
    main()