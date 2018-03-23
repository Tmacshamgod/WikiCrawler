import json
import matplotlib.pyplot as plt
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from wikicrawler.spiders.wikispider import WikiSpider

# run the crawler, items.json will be generated for the result
process = CrawlerProcess(get_project_settings())
process.crawl(WikiSpider)
process.start()

with open('items.json') as item_file:
    items = json.load(item_file)

path_lengths = []
for item in items:
    if item['status'] == 'success':
        path_lengths.append(int(item['depth']))

success_count = len(path_lengths)
success_percentage = (float(success_count) / len(items)) * 100 if len(items) > 0 else 0.0
avg_path_len = float(sum(path_lengths)) / len(path_lengths) if len(path_lengths) > 0 else 0.0

path_length_dict = {}
for l in path_lengths:
    if l not in path_length_dict:
        path_length_dict[l] = 1
    else:
        path_length_dict[l] += 1

with open('result.txt', 'wb') as result_file:
    result_file.write('There are ' + str(success_count) + ' successful paths\n')
    result_file.write('Approximately ' + str(success_percentage) + '% of 500 pages will eventually lead to Philosophy\n')
    result_file.write('Average path length: ' + str(avg_path_len) + '\n')
    result_file.write('Path Length Distribution: ' + str(path_length_dict) + '\n')

# plot the distribution of path lengths
xaxis = []
yaxis = []

for path_length in path_length_dict.keys():
    xaxis.append(path_length)
    yaxis.append(path_length_dict[path_length])

plt.bar(xaxis, yaxis, align='center')
plt.xlabel('Path Length')
plt.ylabel('Frequency')
plt.title('Frequency of Path Lengths to the Philosophy Page')
plt.savefig('result.png')
