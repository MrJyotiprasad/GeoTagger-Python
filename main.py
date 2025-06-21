import os
import piexif
from PIL import Image, ImageDraw, ImageFont
from staticmap import StaticMap, CircleMarker
from location_config import LATITUDE, LONGITUDE, ALTITUDE, LOCATION_NAME, WEATHER, CITY

def dms_coords(decimal_coord):
    degrees = int(abs(decimal_coord))
    minutes = int((abs(decimal_coord) - degrees) * 60)
    seconds = round(((abs(decimal_coord) - degrees) * 60 - minutes) * 60 * 1000000)
    return ((degrees, 1), (minutes, 1), (seconds, 1000000))

def add_exif(image_path):
    gps_ifd = {
        piexif.GPSIFD.GPSLatitudeRef: 'N' if LATITUDE >= 0 else 'S',
        piexif.GPSIFD.GPSLatitude: dms_coords(LATITUDE),
        piexif.GPSIFD.GPSLongitudeRef: 'E' if LONGITUDE >= 0 else 'W',
        piexif.GPSIFD.GPSLongitude: dms_coords(LONGITUDE),
        piexif.GPSIFD.GPSAltitudeRef: 0,
        piexif.GPSIFD.GPSAltitude: (int(ALTITUDE), 1),
    }

    exif_dict = {"GPS": gps_ifd}
    exif_bytes = piexif.dump(exif_dict)

    image = Image.open(image_path)
    image.save(image_path, exif=exif_bytes)
    print(f"✅ EXIF added to {image_path}")

def generate_map_badge():
    map_img = StaticMap(160, 160, 10)  # Zoomed out map
    marker = CircleMarker((LONGITUDE, LATITUDE), 'red', 12)
    map_img.add_marker(marker)
    return map_img.render()

def create_overlay(map_img):
    width, height = 450, 160
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 180))
    overlay.paste(map_img, (0, 0))

    draw = ImageDraw.Draw(overlay)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    draw.text((170, 10), LOCATION_NAME, fill="white", font=font)
    draw.text((170, 40), WEATHER, fill="white", font=font)
    draw.text((170, 70), f"Country: {CITY}", fill="white", font=font)
    draw.text((170, 100), f"Lat: {LATITUDE}  Lng: {LONGITUDE}", fill="white", font=font)

    return overlay

def process_image(image_path):
    print(f"📷 Processing {image_path}...")
    add_exif(image_path)

    base_img = Image.open(image_path).convert("RGBA")
    map_img = generate_map_badge()
    overlay = create_overlay(map_img)

    base_img.paste(overlay, (base_img.width - overlay.width - 10, base_img.height - overlay.height - 10), overlay)
    output_path = os.path.splitext(image_path)[0] + "_tagged.jpg"
    base_img.convert("RGB").save(output_path, "JPEG")
    print(f"✅ Saved: {output_path}\n")

for file in os.listdir():
    if file.lower().endswith((".jpg", ".jpeg", ".png")):
        try:
            process_image(file)
        except Exception as e:
            print(f"❌ Failed on {file}: {e}")