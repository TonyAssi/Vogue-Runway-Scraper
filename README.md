# Vogue Runway Scraper
Scrapes high res images from [Vogue Runway](https://www.vogue.com/fashion-shows).
[](https://cdn.discordapp.com/attachments/1120417968032063538/1175971396522885190/gucci-spring-2018-ready-to-wear-0.png?ex=656d2bb5&is=655ab6b5&hm=3169e89c455160076de7edbae150cebe41d58218561e27ed57c53541985101dc&) [](https://cdn.discordapp.com/attachments/1120417968032063538/1175971397030387782/gucci-spring-2018-ready-to-wear-2.png?ex=656d2bb5&is=655ab6b5&hm=ca1e99b3ae61f78c92b32a3821670076db670a47ee5a62435a12042e08a89554&)

## Installation
```bash
pip install -r requirements.txt
```

## Usage
Import the scraper module
```python
import vogue
```
Get a list of all the runway shows from a particular designer
```python
vogue.designer_to_shows('gucci')
```
Download images from a designer and specific runway show
```python
vogue.designer_show_to_download_images('gucci', 'Spring 2018 Ready-to-Wear', './images')
```
Download all images from all shows of a designer
```python
vogue.designer_to_download_images('gucci','./images')
```
