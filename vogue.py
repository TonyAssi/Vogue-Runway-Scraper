import json
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import os
from unidecode import unidecode


##### Takes in a designer (string) and returns all the shows (list) ##########################################
def designer_to_shows(designer):
    # Replace spaces, puncuations, special character, etc. with - and make lowercase
    designer = designer.replace(' ','-').replace('.','-').replace('&','').replace('+','').replace('--','-').lower()
    designer = unidecode(designer)

    # Designer URL
    URL = "https://www.vogue.com/fashion-shows/designer/" + designer

    # Make request
    r = requests.get(URL)

    # Soupify
    soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib

    # Load a dict of the json file with the relevent data
    js = str(soup.find_all('script', type='text/javascript')[4])
    js = js.split(' = ')[1]
    js = js.split(';<')[0]
    data = json.loads(js)

    # Find the show data within the json
    try:
        t = data['transformed']
        d = t['runwayDesignerContent']
        designer_collections = d['designerCollections']
    except:
        print('could not find shows')
        return []

    # Go through each show and add to list
    shows = []
    for show in designer_collections:
        shows.append(show['hed'])

    return shows
####################################################################################################


##### Takes in a designer (string) and show (string) and then downloads images to save path (string) ####################
def designer_show_to_download_images(designer, show, save_path):
    # Replace spaces with - and lowercase
    show = show.replace(' ','-').lower()
    show = unidecode(show)

    # Replace spaces, puncuations, special character, etc. with - and make lowercase
    designer = designer.replace(' ','-').replace('.','-').replace('&','').replace('+','').replace('--','-').lower()
    designer = unidecode(designer)

    # Check to see if images are already downloaded
    if(os.path.exists(save_path + '/' + designer+ '/' + show)):
         print('Photos already downloaded')
         return None

    # URL of the show
    url = "https://www.vogue.com/fashion-shows/" + show + '/' + designer

    # Make request
    r = requests.get(url)

    # Soupify
    soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib

    # Load a dict of the json file with the relevent data
    try:
        js = str(soup.find_all('script', type='text/javascript')[4])
        js = js.split(' = ')[1]
        js = js.split(';</') [0]
        data = json.loads(js)
    except:
        print('could not find js code')
        return None

    # Find the images in the json dict
    try:
        t= data['transformed']
        g = t['runwayShowGalleries']
        gg = g['galleries']
        collection = gg[0]
        #details = gg[1]
        #beauty = gg[2]
    except:
        print('could not fund images')
        return None

    # Photos of each look
    items = collection['items']

    # Create a designer folder if it doesnt exist
    designer_path = save_path + '/' + designer
    if not os.path.exists(designer_path): os.makedirs(designer_path)

    # designer/show folder
    show_path = designer_path + '/' + show

    # Save photos to folder if it doesn't exist
    if not os.path.exists(show_path):
        os.makedirs(show_path)

        # Go through each look
        for look, i in enumerate(items):
            # Get image url
            img_url = i['image']['sources']['md']['url']

            # Download image
            response = requests.get(img_url)
            try:
                img = Image.open(BytesIO(response.content))

                # Save image
                export_path = show_path + '/' + designer + '-' + show + '-' + str(look) + '.png'
                img.save(export_path)
                print(img_url)
            except:
                print("error downloading", img_url)
    else:
       print('Photos already downloaded')

####################################################################################################


###### Takes in a designer (string) and downloads all the images from all the shows to the save path (string)
def designer_to_download_images(designer, save_path):
    shows = designer_to_shows(designer)
    for show in shows:
        print(designer, show)
        designer_show_to_download_images(designer, show, save_path)
####################################################################################################
