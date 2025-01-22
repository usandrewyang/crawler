from pathlib import Path

import scrapy
import re

class ZycSpider(scrapy.Spider):
    name = "forum"
    start_urls = [
        # "http://www.zhiyoucheng.co/forum-99-1.html", # 智游学堂
        # "http://www.zhiyoucheng.co/forum-4-1.html", # 德州扑克 (3)
        # "http://www.zhiyoucheng.co/forum-36-1.html", # 奥马哈
        "http://www.zhiyoucheng.co/forum-37-1.html", # 混合牌局
        "http://www.zhiyoucheng.co/forum-18-1.html", # 新手天地
    ]
    # if not valid url, return 0
    # else return 1, 2
    def get_url_type(self, url):
        if '@' in url:
            return 0

        regex_1 = r"forum\.php"
        matches = re.search(regex_1, url)
        if matches:
            return 1

        regex_2 = r"thread-"
        matches = re.search(regex_2, url)
        if matches:
            return 2

        regex_3 = r"forum-"
        matches = re.search(regex_3, url)
        if matches:
            return 3

        return 0

    # get topic id and page number from url
    def get_tid_page(self, url, url_type):
        tid = -1
        page = -1

        if url_type == 1:
            regex = r"(?<=tid=)\d+"
            match = re.search(regex, url)
            if match:
                tid = match.group(0)

                regex = r"(?<=page=)\d+"
                match = re.search(regex, url)
                if match:
                    page =int( match.group(0))

        if url_type == 2:
            regex = r"(?<=thread-)\d+"
            match = re.search(regex, url)
            if match:
                tid = match.group(0)

                regex = r"(?<=\d-)\d+(?=-)"
                match = re.search(regex, url)
                if match:
                    page =int( match.group(0))

        return (tid, page)

    def parse(self, response):
        url = response.request.url
        if not self.get_url_type(url):
            return

        for row in response.css("#threadlisttableid").css("tbody"):
            next_link = row.css("td.icn a::attr(href)").get()
            print(f">>>>>>>>>>>> {next_link}")

            if next_link is not None:
                yield response.follow(next_link, callback=self.parse_content)

    def parse_content(self, response):
        url = response.request.url
        if not self.get_url_type(url):
            return

        print("url: " + url)
        url_type = self.get_url_type(url)
        tid, page = self.get_tid_page(url, url_type)
        if tid == -1 or page == -1:
            print(f"Error: Invalid tid or page number for URL: {url}")
            return

        levels = len(response.css("td.t_f"))
        if levels > 0:
            for i in range(levels):
                # If it is the 1st page and 1st post, it is the main post
                # The rest are following posts.
                # Title field is not required for the following posts.
                if i == 0 and page == 1:
                    yield {
                        "tid": tid,
                        "page": page,
                        "level": (i+1),
                        "url": url,
                        "title": response.css("#thread_subject::text").get(),
                        "author": response.css("div.pi").css("div.authi")[i].css("a::text").getall()[0],
                        "content": response.css("td.t_f")[i].css("td.t_f::text,a::text").getall(),
                    }
                else:
                    yield {
                        "tid": tid,
                        "page": page,
                        "level": (i+1) + (page-1)*10,
                        "url": url,
                        "author": response.css("div.pi").css("div.authi")[i].css("a::text").getall()[0],
                        "content": response.css("td.t_f")[i].css("td.t_f::text,a::text").getall(),
                    }

                for next_link in response.css("td.t_f")[i].css("a::attr(href)").getall():
                    # print("next_link:" + next_link)
                    # if '@' not in next_link:
                    if self.get_url_type(next_link) != 0:
                        yield response.follow(next_link, callback=self.parse_content)

        # parse the next page
        next_page = response.css("a.nxt::attr(href)").get()
        if next_page and self.get_url_type(next_page):
            yield response.follow(next_page, callback=self.parse_content)

