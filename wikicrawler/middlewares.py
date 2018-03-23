# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
from scrapy.http import Request
from scrapy.spidermiddlewares.depth import DepthMiddleware


# pass the path's root page from response to request
# and maintain the dict that maps each root page to its list of paths urls
class PathRootUrlMiddleware(object):
    rootKey = 'path_root_url'

    def process_spider_output(self, response, result, spider):
        def _filter(request):
            if isinstance(request, Request):
                stored_path_root = response.meta.get(self.rootKey)
                request.meta[self.rootKey] = stored_path_root
                spider.visited_urls_in_path[stored_path_root].append(response.url)
            return True

        if self.rootKey not in response.meta:
            path_root = response.url
            response.meta[self.rootKey] = path_root
            spider.visited_urls_in_path[path_root] = []
        return (r for r in result or () if _filter(r))


# report the depth, but not count the first step
class IgnoreRandomDepthMiddleware(DepthMiddleware):
    def process_spider_output(self, response, result, spider):
        def _filter(request):
            if isinstance(request, Request):
                depth = response.meta['depth'] + 1
                request.meta['depth'] = depth
                if self.prio:
                    request.priority -= depth * self.prio
                if self.maxdepth and depth > self.maxdepth:
                    return False
                elif self.stats:
                    if self.verbose_stats:
                        self.stats.inc_value('request_depth_count/%s' % depth, spider=spider)
                    self.stats.max_value('request_depth_max', depth, spider=spider)
            return True

        random_url = "https://en.wikipedia.org/wiki/Special:Random"
        if self.stats and 'depth' not in response.meta and response.url != random_url:
            response.meta['depth'] = 0
            if self.verbose_stats:
                self.stats.inc_value('request_depth_count/0', spider=spider)
        return (r for r in result or () if _filter(r))
