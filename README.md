# Vogue Runway Scraper
Scrapes high resolution images from [Vogue Runway](https://www.vogue.com/fashion-shows).

![](https://cdn.discordapp.com/attachments/1120417968032063538/1175972124716957837/gucci.png?ex=656d2c63&is=655ab763&hm=13fe4faf0cabc6c0ddbc4be0b41e9397ff27a6e19eed8f4b9bd696926cc169c1&)

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
vogue.designer_to_download_images('gucci', './images')
```
