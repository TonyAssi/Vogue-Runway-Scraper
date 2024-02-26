# Vogue Runway Scraper
Scrapes high resolution images from [Vogue Runway](https://www.vogue.com/fashion-shows).

![gucci-spring-2018-ready-to-wear-1](https://github.com/TonyAssi/Vogue-Runway-Scraper/assets/42156881/081f2c82-fbc5-419f-a0e8-52f8f1a8cdcd)

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
