# Vogue Runway Scraper
Scrapes images from [Vogue Runway](https://www.vogue.com/fashion-shows).

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
