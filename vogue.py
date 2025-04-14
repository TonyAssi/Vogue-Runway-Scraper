import json
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import os
from unidecode import unidecode
import csv


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


###### Takes in a designer (string) and show (string) and saves the image urls to a csv
def designer_show_to_csv(designer, show, save_path=None):
    # Normalize show and designer names
    show_clean = unidecode(show.replace(' ', '-').lower())
    designer_clean = unidecode(designer.replace(' ', '-').replace('.', '-').replace('&', '').replace('+', '').replace('--', '-').lower())

    # If saving to CSV, ensure folder exists
    if save_path:
        os.makedirs(save_path, exist_ok=True)
        csv_path = os.path.join(save_path, f"{designer_clean}_{show_clean}.csv")
        if os.path.exists(csv_path):
            print('CSV already exists:', csv_path)
            return None  # prevent duplicate scraping

    # Show URL
    url = f"https://www.vogue.com/fashion-shows/{show_clean}/{designer_clean}"

    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html5lib')
        js = str(soup.find_all('script', type='text/javascript')[4])
        js = js.split(' = ')[1].split(';</')[0]
        data = json.loads(js)
        items = data['transformed']['runwayShowGalleries']['galleries'][0]['items']
    except Exception as e:
        print(f"❌ Could not load show: {designer} - {show}: {e}")
        return None

    rows = []
    for i in items:
        try:
            img_url = i['image']['sources']['md']['url']
            rows.append([designer, show, img_url])
        except:
            print('⚠️ Skipping bad image item')

    # Optionally write CSV
    if save_path and rows:
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['designer', 'show', 'image_url'])
            writer.writerows(rows)
        print(f"✅ CSV saved to {csv_path}")

    return rows
####################################################################################################

###### Takes in a designer (string) and saves the image urls to a csv
def designer_to_csv(designer, save_path):
    designer_clean = unidecode(designer.replace(' ', '-').replace('.', '-').replace('&', '').replace('+', '').replace('--', '-').lower())
    os.makedirs(save_path, exist_ok=True)
    csv_path = os.path.join(save_path, f"{designer_clean}_all_shows.csv")

    if os.path.exists(csv_path):
        print("CSV already exists:", csv_path)
        return

    shows = designer_to_shows(designer)
    if not shows:
        print(f"No shows found for {designer}")
        return

    all_rows = []
    for show in shows:
        print(f"Scraping {designer} - {show}")
        rows = designer_show_to_csv(designer, show)
        if rows:
            all_rows.extend(rows)

    if all_rows:
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['designer', 'show', 'image_url'])
            writer.writerows(all_rows)
        print(f"✅ All shows saved to {csv_path}")
    else:
        print("No images found to write.")
####################################################################################################

###### Takes a .txt file of designers and saves all the images of all the shows of all the designers to a csv
def all_designers_to_csv(txt_path, save_path):
    import csv

    # Make sure output directory exists
    os.makedirs(save_path, exist_ok=True)

    # Final combined CSV path
    csv_path = os.path.join(save_path, "all_designers.csv")

    # Read designer names from .txt file
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            designers = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"❌ Error reading file {txt_path}: {e}")
        return

    if not designers:
        print("No designers found in the file.")
        return

    # Track which designer/show combos have already been written
    existing_rows = set()
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_rows.add((row['designer'], row['show']))

    # Open CSV in append mode
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Write header if file is empty
        if os.stat(csv_path).st_size == 0:
            writer.writerow(['designer', 'show', 'image_url'])

        for designer in designers:
            print(f"\n📂 Starting designer: {designer}")
            try:
                shows = designer_to_shows(designer)
                for show in shows:
                    if (designer, show) in existing_rows:
                        print(f"✅ Already scraped: {designer} - {show}")
                        continue

                    print(f"🔍 Scraping: {designer} - {show}")
                    rows = designer_show_to_csv(designer, show)
                    if rows:
                        writer.writerows(rows)
                        f.flush()  # ✅ Force save after every designer/show
                        existing_rows.update((designer, show) for _ in rows)

            except Exception as e:
                print(f"❌ Failed to process {designer}: {e}")
####################################################################################################

