from pathlib import Path

import scrapy


class QuotesSpider(scrapy.Spider):
    name = "forum"
    start_urls = [
        "http://www.zhiyoucheng.co/forum-99-1.html",
    ]

    def parse(self, response):
        for row in response.css("#threadlisttableid").css("tbody"):
            yield {
                "text": row.css("a.s.xst::text").get(),
                # "author": row.css("span small::text").get(),
                # "tags": row.css("div.tags a.tag::text").getall(),
            }

            next_page = row.css("td.icn a::attr(href)").get()

            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)
