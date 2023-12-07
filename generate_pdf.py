import re
import os
import requests
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus.flowables import PageBreak
from reportlab.lib.units import inch
import PIL.Image


def generate_pdf(name, address, description, formatted_phones, url, image_url):
    # Sanitize the filename to remove any invalid characters
    name = re.sub(r'[\/:*?"<>|]', '_', name)

    pdf_filename = f"{name}.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=landscape(letter))
    story = []

    # Register the DejaVuSans.ttf font
    pdfmetrics.registerFont(TTFont("DejaVuSans", "fonts_for_pdf/DejaVuSans.ttf"))

    styles = getSampleStyleSheet()
    styleN = styles["Normal"]
    styleH = styles["Heading1"]
    styleT = styles["Title"]

    # Use the DejaVuSans font for Normal style
    styleN.fontName = "DejaVuSans"

    title = Paragraph(name, style=styleH)
    story.append(title)

    flag = 0

    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            with open('photo.jpg', 'wb') as fp:
                fp.write(response.content)
        else:
            print(f"Error: Status code {response.status_code}")
            flag = 1
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while executing the request: {e}")

    # Insert an image into a PDF document if available
    if os.path.exists('photo.jpg') and flag == 0:

        # Opening the image
        image = PIL.Image.open('photo.jpg')  # Specify the path to your image

        # Getting the width and height of the image
        width, height = image.size
        k = height / width

        # Create an Image object and set the coordinates for insertion on the left
        image = Image('photo.jpg', width=250 / k, height=250)
        image.hAlign = 'LEFT'

        story.append(image)

    else:
        print("Image 'photo.jpg' not found.")

    address_text = Paragraph(f"<b><u>Address:</u></b> {address}", style=styleN)
    story.append(address_text)

    # Add an empty line
    story.append(Spacer(1, 12))

    description_text = Paragraph(f"<b><u>Description:</u></b> {description}", style=styleN)
    story.append(description_text)

    story.append(Spacer(1, 12))
    phones_text = "<b><u>Phones:</u></b><br/>" + "<br/>".join(formatted_phones)
    phones_text = Paragraph(phones_text, style=styleN)
    story.append(phones_text)

    story.append(Spacer(1, 12))
    url_text = Paragraph(f"<b><u>URL:</u></b> {url}", style=styleN)
    story.append(url_text)

    doc.build(story)

