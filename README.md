# The `scrappy` Project

## PROJECT FILES

The following are the list of files used by the project
* requirements.txt - project required python3 modules
* scrapy.cfg - deploy configuration file of scrapy project
* theurge - the main project folder
    * logs
        * .delete_me - this is just a file placeholder (nothing much)
        * spider.log - this file will be generated by the application
    * spider
        * spider.py - a base class for possible item scraped keeper information
        * spider.yaml - scraping field and xpath/css configuration
        * urge.py - the main urge scraping crawlspider
    * __ init __.py` - application module initialization file
    * extensions.py - contains all possible extension classes including task 4's Stat Logging Extension
    * items.py - list of fields to be scraped and keeper info
    * middlewares.py - contains all possible middleware classes including task 3's Latency Logging Middleware
    * pipelines.py - contains all possible spider pipeline classes including the urge base pipeline and a DropItem pipeline for empty items
    * settings.py - a settings file that turns on / off extensions, middlewares, spider env variables, etc.

### Log File

All processing logs will be stored in the `spider.log` file under the `log` folder.

```
    # Create Log Files
    LOG_FILE = 'logs/spider.log'
    ERR_FILE = 'logs/spider_error.log'
    configure_logging(install_root_handler=False)
    logging.basicConfig(level=logging.INFO, filemode='w+', filename=LOG_FILE)
    logging.basicConfig(level=logging.ERROR, filemode='w+', filename=ERR_FILE)
```

### Task 1

There is a simple scrapy settings that can be used to save chunks of data. The `FEED_EXPORT_BATCH_ITEM_COUNT` setting can be set to an integer value (e.g. `20`).

Returning X Products settings is a bit tricky. There are different settings and different logic behind. This can be the number of download request or downloader response count. If this is so, the settings `CLOSESPIDER_ITEMCOUNT` and the `CONCURRENT_ITEMS` can be set to X. This will not guarantee though that exactly X number of items will be scraped. It can be more than X.

Tried to implement both `extensions` and `middlewares` but still did not guarantee the exact X Count. So I assume X here is the number of `items scraped`. To solve this problem, there is need to track the number of items being scraped by the spider `total_items` and match it with `total_item_to_extract` which is nothing but a user defined settings `TOTAL_ITEMCOUNT`, if nothing is set default is `300`.  There is also another pipeline that ignores item with empty `price`, `sales_price`, `brand`, `description` and `category`.

```
2021-05-22 16:02:06 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
{'downloader/exception_count': 13,
 'downloader/exception_type_count/scrapy.exceptions.IgnoreRequest': 13,
 'downloader/request_bytes': 64208,
 'downloader/request_count': 121,
 'downloader/request_method_count/GET': 121,
 'downloader/response_bytes': 3110017,
 'downloader/response_count': 121,
 'downloader/response_status_count/200': 78,
 'downloader/response_status_count/204': 1,
 'downloader/response_status_count/302': 32,
 'downloader/response_status_count/403': 10,
 ...
 ...
 'httpcompression/response_count': 80,
 'item_dropped_count': 20,
 'item_dropped_reasons_count/DropItem': 20,
 'item_scraped_count': 50,  ---> <TOTAL_ITEMCOUNT>
 ...
 ...
 'response_received_count': 89,
 'robotstxt/forbidden': 13,
 'robotstxt/request_count': 9,
 ...
 ...
 'start_time': datetime.datetime(2021, 5, 22, 6, 1, 56, 239365)}
2021-05-22 16:02:06 [scrapy.core.engine] INFO: Spider closed (closespider_itemcount)

```

The generated items are saved in file named `sales-<index>.jl` where `<index>` are sequence number from 1 to N. This and the other feed settings are configured in the settings.py.

```
FEED_EXPORT_BATCH_ITEM_COUNT = 20
FEEDS = {
    'sale-%(batch_id)d.jl' : {
                'format' : 'jl',
                'store_empty' : False,
                # These are the fields that will be included in the JL file/s. 
                # These fields needs to be defined in the items.py
                'fields': ['title','brand','description','price','salePrice','website'],
                'overwrite': True
            }
}
CLOSESPIDER_ITEMCOUNT=300
CONCURRENT_ITEMS=50
TOTAL_ITEMCOUNT=300
```

### Task 2

I can't find any specific scrapy settings or configuration for this task. To do this, a yaml file `spider.yaml` was introduced. This file will be loaded during spider initialization.

```
# Load the YAML Configuration
dir_path = os.path.dirname(os.path.realpath(__file__))
global config
with open(r'%s/spider.yaml' % dir_path) as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
```

`spider.yaml`
```
urge:
  css:
    category: "h1._31Nwh.JLwaS::text"
    price: "div.eP0wn._2xJnS span._2plVT::text"
    brand: "span.URfXD::text"
    website: "a.ZV4Wf::text"
  xpath:
    salePrice: "//*[@class='_2Mqpk']/a[1]/div[2]/text()[2]"
    description: "//article/a/p/text()"
```

### Task 3

There are few ways to do this. The app used the DownloadMiddleware to track down the Download Latency. The `TheurgeDownloaderMiddleware` class is used to log the latency of downloads.

```
2021-05-22 16:29:18 [urge] INFO: Download (minutes, seconds): (0.0, 0.16039)
```

### Task 4 - Category Browsed extension

It is assumed that categories can be extracted from 2 different areas. First being as part of the request query parameter - `cat`. If there are no `cat` query parameter, it is assumed that it is a generic browsing hence the category can be extracted from the search's breadcrumbs represented by an `h1` tag. If both are not present the app uses the `brands` query parameter or the `brand` extracted information. If none of these information are present, the app tag it as `generic`. The `TheurgeStatsLogging` class is created to count the items per category.

```
2021-05-22 16:29:18 [urge] INFO: ===============URGE STAT LINE==================
2021-05-22 16:29:18 [urge] INFO: {
   "bags-backpacks": 1,
   "bags": 1,
   "bags-accessories": 1,
   "bags-tote-shopper-bags": 1,
   "bags-clutches-pouches": 1,
   "bags-shoulder-bags": 1,
   "bags-satchels-cross-body-bags": 1,
   "shoes-flatforms": 1,
   "shoes-flats": 1,
   "shoes-sneakers": 1,
   "shoes-heels": 1,
   "shoes": 1,
   "shoes-boots": 1,
   "clothing-maternity": 1,
   "clothing-plus-size": 1,
   "grooming-suncare": 1,
   "grooming-sleeping-aids": 1,
   "grooming-nails": 1,
   "grooming-shave": 1,
   "grooming-bath-body": 10,
   "Aglini for Men": 1,
   "AUMORFIA for Men": 1,
   "AM Eyewear for Men": 1,
   "Arnar Mar Jonsson for Men": 1,
   "Aerin Beauty for Men": 1,
   "Aleksandr Manam\u00efs for Men": 1,
   "aztec for Men": 1,
   "authentic outfitters for Men": 1,
   "austin manor for Men": 1,
   "aussie chiller for Men": 1,
   "aubSparkle for Men": 1,
   "attention for Men": 1,
   "Artisan & Fox for Men": 1,
   "artznwordz for Men": 1,
   "artefact for Men": 1,
   "angelo rossi for Men": 1,
   "andre gianni for Men": 1,
   "american sunshine for Men": 1,
   "america team sports for Men": 1,
   "amali for Men": 1,
   "allstate floral for Men": 1,
   "attention": 1,
   "adidas Originals & attention for Men": 1,
   "adidas & attention for Men": 1,
   "Zara & attention for Men": 1,
   "Y-3 & attention for Men": 1,
   "Versace & attention for Men": 1,
   "Vans & attention for Men": 1,
   "Tommy Hilfiger & attention for Men": 1,
   "Tom Ford & attention for Men": 1,
   "Valentino & attention for Men": 1,
   "Typo & attention for Men": 1,
   "Tod's & attention for Men": 1,
   "Thom Browne & attention for Men": 1,
   "allstate floral": 1,
   "adidas Originals & allstate floral for Men": 1,
   "Zara & allstate floral for Men": 1,
   "Y-3 & allstate floral for Men": 1,
   "Versace & allstate floral for Men": 5,
   "adidas & allstate floral for Men": 11,
   "Vans & allstate floral for Men": 1,
   "KENZO, Vans & attention for Men": 1,
   "Jordan, Vans & attention for Men": 1,
   "Jacob Cohen, Vans & attention for Men": 1,
   "Jil Sander, Vans & attention for Men": 30,
   "adidas": 3,
   "Vans": 5,
   "Jil Sander": 7,
   "Thom Browne": 1,
   "Burberry": 1,
   "accessories-travel": 119,
   "Saint Laurent": 1,
   "accessories": 19,
   "Burberry for Men": 1,
   "Saint Laurent for Men": 1,
   "Fay": 1,
   "COLORADO": 4,
   "Alexander McQueen": 1,
   "Moncler": 2,
   "S.t. Dupont": 1,
   "HAY": 1,
   "Gucci": 1,
   "Mon Purse": 1,
   "Tumi": 1,
   "Stay Made": 1,
   "Victoria's Secret": 1,
   "Oscar de la Renta": 1,
   "Canada Goose": 1,
   "Aspinal of London": 1,
   "Louis Vuitton": 5
}
2021-05-22 16:29:18 [urge] INFO: ===============================================
```

## RUNNING THE APP

To run the application, proceed to the root directory of the cloned repository

e.g. 

```
$ ~/Development/personalWorkspace/scrappy (main)
```

### Create the pyhon environment

Skip this process if already has. Python 3 is required with Pip and VirtualEnv installed as well.

```
$ virtualenv .venv --python=python3
created virtual environment CPython3.8.8.final.0-64 in 220ms
  creator CPython3Posix(dest=/Development/personalWorkspace/scrappy/.env, clear=False, no_vcs_ignore=False, global=False)
  seeder FromAppData(download=False, pip=bundle, setuptools=bundle, wheel=bundle, via=copy, app_data_dir=/home/x/.local/share/virtualenv)
    added seed packages: pip==21.0.1, setuptools==56.0.0, wheel==0.36.2
  activators BashActivator,CShellActivator,FishActivator,PowerShellActivator,PythonActivator,XonshActivator
```
`--python=python3` is optional if the default python version is version 3 and above.

### Enable the python environment

Enable the python environment and install the python modules

```
$ source .venv/bin/activate
(.venv) $ pip install -r requirements.txt
Collecting attrs==21.2.0
  Using cached attrs-21.2.0-py2.py3-none-any.whl (53 kB)
Collecting Automat==20.2.0
  Using cached Automat-20.2.0-py2.py3-none-any.whl (31 kB)
Collecting cffi==1.14.5
  Using cached cffi-1.14.5-cp38-cp38-manylinux1_x86_64.whl (411 kB)
Collecting constantly==15.1.0
  Using cached constantly-15.1.0-py2.py3-none-any.whl (7.9 kB)

...
...
Collecting zope.interface==5.4.0
  Using cached zope.interface-5.4.0-cp38-cp38-manylinux2010_x86_64.whl (259 kB)
Requirement already satisfied: setuptools in ./.env/lib/python3.8/site-packages (from zope.interface==5.4.0->-r requirements.txt (line 32)) (56.0.0)
Installing collected packages: six, pycparser, idna, attrs, zope.interface, w3lib, pyasn1, lxml, incremental, hyperlink, hyperframe, hpack, cssselect, constantly, cffi, Automat, Twisted, pyasn1-modules, priority, parsel, jmespath, itemadapter, h2, cryptography, service-identity, queuelib, pyOpenSSL, PyDispatcher, Protego, itemloaders, Scrapy, PyYAML
Successfully installed Automat-20.2.0 Protego-0.1.16 PyDispatcher-2.0.5 PyYAML-5.4.1 Scrapy-2.5.0 Twisted-21.2.0 attrs-21.2.0 cffi-1.14.5 constantly-15.1.0 cryptography-3.4.7 cssselect-1.1.0 h2-3.2.0 hpack-3.0.0 hyperframe-5.2.0 hyperlink-21.0.0 idna-3.1 incremental-21.3.0 itemadapter-0.2.0 itemloaders-1.0.4 jmespath-0.10.0 lxml-4.6.3 parsel-1.6.0 priority-1.3.0 pyOpenSSL-20.0.1 pyasn1-0.4.8 pyasn1-modules-0.2.8 pycparser-2.20 queuelib-1.6.1 service-identity-21.1.0 six-1.16.0 w3lib-1.22.0 zope.interface-5.4.0
```

### Execute the Scrapping App

To start scraping, run the command

```
(.venv) $ scrapy runspider theurge/spiders/urge.py
...
...
...
 'website': 'harrods.com'}
{'brand': 'Purdey',
 'brand_param': 'Mulberry,Off-White,Paul Smith,Purdey,R.M. Williams,ROYCE New '
                'York,Radley London,Saint Laurent,The People Vs.,Things '
                'Remembered,Vetements,Want Les Essentiels De La Vie,Wolf',
 'category': "Men's Mulberry, Off-White, Paul Smith, Purdey, R.M. Williams, "
             'ROYCE New York, Radley London, Saint Laurent, The People Vs., '
             'Things Remembered, Vetements, Want Les Essentiels De La Vie & '
             'Wolf Travel Accessories',
 'category_param': 'accessories-travel',
 'date': datetime.datetime(2021, 5, 22, 16, 29, 20, 396455),
 'description': 'Leather Passport Cover',
 'price': '$168',
 'project': 'theurge',
 'salePrice': '$222.00',
 'server': 'talampas-linux',
 'spider': 'urge',
 'url': 'https://theurge.com/men/search/?cat=accessories-travel&brands=Mulberry,Off-White,Paul+Smith,Purdey,R.M.+Williams,ROYCE+New+York,Radley+London,Saint+Laurent,The+People+Vs.,Things+Remembered,Vetements,Want+Les+Essentiels+De+La+Vie,Wolf',
 'website': 'harrods.com'}
...
2021-05-22 16:29:20 [urge] INFO: ext log -> Spider closed: urge
2021-05-22 16:29:20 [urge] DEBUG: Displaying final Stats after Process ....
2021-05-22 16:29:20 [urge] INFO: mid download -> Spider closed: urge
2021-05-22 16:29:20 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
{'downloader/exception_count': 33,
...
 'downloader/request_count': 475,
 'downloader/request_method_count/GET': 475,
 'downloader/response_bytes': 16268961,
 'downloader/response_count': 469,
 'downloader/response_status_count/200': 356,
 'downloader/response_status_count/204': 1,
 'downloader/response_status_count/301': 4,
 'downloader/response_status_count/302': 94,
 'downloader/response_status_count/403': 12,
...
 'finish_time': datetime.datetime(2021, 5, 22, 6, 29, 20, 716802),
 'httpcompression/response_bytes': 114912560,
 'httpcompression/response_count': 365,
 'item_dropped_count': 40,
 'item_dropped_reasons_count/DropItem': 40,
 'item_scraped_count': 300,
...
 'scheduler/dequeued/memory': 482,
 'scheduler/enqueued': 21511,
 'scheduler/enqueued/memory': 21511,
 'start_time': datetime.datetime(2021, 5, 22, 6, 28, 37, 980426)}
2021-05-22 16:29:20 [scrapy.core.engine] INFO: Spider closed (closespider_itemcount)

```