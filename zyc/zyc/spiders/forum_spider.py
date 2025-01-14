from pathlib import Path

import scrapy
import re


class ZycSpider(scrapy.Spider):
    name = "forum"
    start_urls = [
        "http://www.zhiyoucheng.co/forum-99-1.html",
    ]

    def parse(self, response):
        for row in response.css("#threadlisttableid").css("tbody"):
            # yield {
            #     "text": row.css("a.s.xst::text").get(),
            #     # "author": row.css("span small::text").get(),
            #     # "tags": row.css("div.tags a.tag::text").getall(),
            # }

            next_link = row.css("td.icn a::attr(href)").get()

            if next_link is not None:
                yield response.follow(next_link, callback=self.parse_content)

    def parse_content(self, response):
        levels = len(response.css("td.t_f"))
        if levels > 1:
            for i in range(levels):
                # If it is the 1st floor, it is master post
                url = response.request.url
                print("url: " + url)
                # match = re.search(r"tid=(\d+)", url)
                # if match:
                #     tid = match.group(1)
                # else:
                #     tid = 0
                if i == 0:
                    yield {
                        "master_url": url,
                        "title": response.css("#thread_subject::text").get(),
                        "author": response.css("div.pi").css("div.authi")[i].css("a::text").getall()[0],
                        "content": response.css("td.t_f")[i].css("td.t_f::text,a::text").getall(),
                        "level": i,
                    }
                # the rest posts are following posts
                else:
                    yield {
                        "followed_url": url,
                        "author": response.css("div.pi").css("div.authi")[i].css("a::text").getall()[0],
                        "content": response.css("td.t_f")[i].css("td.t_f::text,a::text").getall(),
                        "level": i,
                    }

                for next_link in response.css("td.t_f")[i].css("a::attr(href)").getall():
                    # print("next_link:" + next_link)
                    if '@' not in next_link:
                        yield response.follow(next_link, callback=self.parse_content)

