# expose extractor package on import
from importlib import import_module

# import all extractors so SeedSpider can find them dynamically later
import_module("crawler.extractors.grandstream")
