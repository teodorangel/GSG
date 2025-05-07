# Scrapy settings for GrandGuruAI crawler project

BOT_NAME = 'grandguru'

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure item pipelines for images and manual PDFs
ITEM_PIPELINES = {
    'crawler.pipelines.ProductPipeline': 50,
    'crawler.pipelines.CategoryImagesPipeline': 100,
    'crawler.pipelines.ManualFilesPipeline': 200,
}

# Directory to store downloaded category icons
IMAGES_STORE = 'images/categories'

# Directory to store downloaded manual PDF files
FILES_STORE = 'files/manuals'

# Optional: set user agent
USER_AGENT = 'GrandGuruCrawler (+https://github.com/teodorangel/GSG)' 