import json
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import os
from unidecode import unidecode
import csv


def extract_json_from_script(scripts, key_fragment):
    for script in scripts:
        if script.string and key_fragment in script.string:
            js = script.string
            break
    else:
        return None

    try:
        js_clean = js.split(' = ', 1)[1]
        brace_count = 0
        for i, char in enumerate(js_clean):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    js_clean = js_clean[:i+1]
                    break
        return json.loads(js_clean)
    except Exception as e:
        print(f"❌ JSON extraction failed: {e}")
        return None


def designer_to_shows(designer):
    designer = unidecode(designer.replace(' ', '-').replace('.', '-').replace('&', '').replace('+', '').replace('--', '-').lower())
    URL = f"https://www.vogue.com/fashion-shows/designer/{designer}"
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'html5lib')

    data = extract_json_from_script(soup.find_all('script', type='text/javascript'), 'window.__PRELOADED_STATE__')
    if not data:
        print("❌ Could not find JSON script")
        return []

    try:
        shows = [show['hed'] for show in data['transformed']['runwayDesignerContent']['designerCollections']]
        return shows
    except Exception as e:
        print(f"❌ Failed to parse shows list: {e}")
        return []


def designer_show_to_download_images(designer, show, save_path):
    show = unidecode(show.replace(' ', '-').lower())
    designer = unidecode(designer.replace(' ', '-').replace('.', '-').replace('&', '').replace('+', '').replace('--', '-').lower())
    show_path = os.path.join(save_path, designer, show)
    if os.path.exists(show_path):
        print('Photos already downloaded')
        return

    url = f"https://www.vogue.com/fashion-shows/{show}/{designer}"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib')

    data = extract_json_from_script(soup.find_all('script', type='text/javascript'), 'runwayShowGalleries')
    if not data:
        print("❌ JSON script not found")
        return

    try:
        items = data['transformed']['runwayShowGalleries']['galleries'][0]['items']
    except Exception as e:
        print("❌ Could not find images:", e)
        return

    os.makedirs(show_path, exist_ok=True)

    for i, item in enumerate(items):
        try:
            img_url = item['image']['sources']['md']['url']
            response = requests.get(img_url)
            img = Image.open(BytesIO(response.content))
            export_path = os.path.join(show_path, f"{designer}-{show}-{i}.png")
            img.save(export_path)
            print(img_url)
        except Exception as e:
            print("⚠️ Error downloading:", img_url, e)


def designer_to_download_images(designer, save_path):
    shows = designer_to_shows(designer)
    for show in shows:
        print(designer, show)
        designer_show_to_download_images(designer, show, save_path)


def designer_show_to_csv(designer, show, save_path=None):
    show_clean = unidecode(show.replace(' ', '-').lower())
    designer_clean = unidecode(designer.replace(' ', '-').replace('.', '-').replace('&', '').replace('+', '').replace('--', '-').lower())

    if save_path:
        os.makedirs(save_path, exist_ok=True)
        csv_path = os.path.join(save_path, f"{designer_clean}_{show_clean}.csv")
        if os.path.exists(csv_path):
            print('CSV already exists:', csv_path)
            return None

    url = f"https://www.vogue.com/fashion-shows/{show_clean}/{designer_clean}"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib')

    data = extract_json_from_script(soup.find_all('script', type='text/javascript'), 'runwayShowGalleries')
    if not data:
        print(f"❌ Could not load show: {designer} - {show}")
        return None

    try:
        items = data['transformed']['runwayShowGalleries']['galleries'][0]['items']
    except Exception as e:
        print(f"❌ Failed to find gallery items: {e}")
        return None

    rows = []
    for i in items:
        try:
            img_url = i['image']['sources']['md']['url']
            rows.append([designer, show, img_url])
        except:
            print('⚠️ Skipping bad image item')

    if save_path and rows:
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['designer', 'show', 'image_url'])
            writer.writerows(rows)
        print(f"✅ CSV saved to {csv_path}")

    return rows


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


def all_designers_to_csv(txt_path, save_path):
    os.makedirs(save_path, exist_ok=True)
    csv_path = os.path.join(save_path, "all_designers.csv")

    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            designers = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"❌ Error reading file {txt_path}: {e}")
        return

    if not designers:
        print("No designers found in the file.")
        return

    existing_rows = set()
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_rows.add((row['designer'], row['show']))

    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

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
                        f.flush()
                        existing_rows.update((designer, show) for _ in rows)

            except Exception as e:
                print(f"❌ Failed to process {designer}: {e}")
