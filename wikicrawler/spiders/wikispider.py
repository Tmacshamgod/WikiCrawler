import scrapy
import re
from wikicrawler.items import WikicrawlerItem


class WikiSpider(scrapy.Spider):
    base_url = "https://en.wikipedia.org"
    pattern = r'(?<=<a href=")/wiki/[a-zA-Z\(\)\-\,_#]*?(?=")'
    random_article_url = "https://en.wikipedia.org/wiki/Special:Random"
    # a dictionary will map each path root to the list of visited pages
    visited_urls_in_path = {}

    name = "wikiSpider"
    allowed_domains = ["wikipedia.org"]
    start_urls = [random_article_url] * 500

    def parse(self, response):
        path_root = response.meta.get('path_root_url')
        doc_text_list = response.xpath("//div[@id='mw-content-text']/div/p").extract()
        href = ''

        # find links in main body paragraphs
        for doc_text in doc_text_list:
            clean_text = self.remove_parentheses(doc_text.encode('utf8'))
            match = re.search(self.pattern, clean_text)
            if match:
                href = match.group(0).split('#')[0]
                break

        # sometimes there are links in pages not in paragraphs
        if href == '':
            doc_text = ''.join(response.xpath("//div[@id='mw-content-text']/div/ul/li").extract())
            clean_text = self.remove_parentheses(doc_text.encode('utf8'))
            match = re.search(self.pattern, clean_text)
            if match:
                href = match.group(0).split('#')[0]

        # if no link is found, then it's a dead end
        if href == '':
            item = WikicrawlerItem()
            item['path_root'] = path_root
            item['depth'] = -1
            item['status'] = 'dead end'
            yield item
            return

        next_page_url = self.base_url + str(href)
        current_depth = response.meta['depth']

        # if a page links to another page in its path or to itself, then it's a cycle
        if next_page_url in self.visited_urls_in_path[path_root] or next_page_url == response.url:
            item = WikicrawlerItem()
            item['path_root'] = path_root
            item['depth'] = -1
            item['status'] = 'cycle'
            yield item
        # reach the philosophy page
        elif href == "/wiki/Philosophy":
            item = WikicrawlerItem()
            item['path_root'] = path_root
            item['depth'] = current_depth + 1
            item['status'] = 'success'
            yield item
        # keep visiting the next page
        else:
            yield scrapy.Request(next_page_url, callback=self.parse, dont_filter=True)

    # removes text within parentheses
    def remove_parentheses(self, html):
        paren_count = 0
        bracket_count = 0
        cleaned_string = ""
        for c in html:
            if c == '<':
                bracket_count += 1
            elif c == '>':
                bracket_count -= 1
            elif c == '(' and bracket_count == 0:
                paren_count += 1
            elif c == ')' and bracket_count == 0:
                paren_count -= 1
                continue
            if paren_count == 0:
                cleaned_string += c
        return cleaned_string
