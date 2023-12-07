import telebot
import requests
import sqlite3
import random
from telebot import types
import os
import json
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
from geoposition_mapquest import *
from get_description_deepai import *
from api import *
from save_delete_data_as_json import *
from translate_to_english import *
from search_images import *
from generate_pdf import *

bot = telebot.TeleBot(telegram_api)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    item1 = types.KeyboardButton("Want to visit")
    markup.add(item1)
    item2 = types.KeyboardButton("I've already visited")
    markup.add(item2)
    bot.reply_to(message, "Hello! Enter the name of a place or city to find interesting places in that location. "
                          "Start your message with '/search'", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text.startswith('/search'))
def search_places(message):
    delete_old_json_files()
    location_query = message.text
    api_key = yandex_api
    query = "museums, monuments"
    # Request to the Yandex API Search by organization
    url = f'https://search-maps.yandex.ru/v1/?text={query}, {location_query}&type=biz&lang=en_US&apikey={api_key}'
    response = requests.get(url)
    data = response.json()

    # Processing the results
    if 'features' in data:
        places = data['features']
        places_count = 0  # Place counter
        for place in places:

            name = place['properties']['CompanyMetaData']['name']
            name = translate_to_english(name)
            address = place['properties']['CompanyMetaData']['address']
            description = get_brief_description(name, location_query)
            coordinates = place['geometry']['coordinates']
            coordinates.reverse()

            # Checking the presence of a list of phones ('Phones')
            if 'Phones' in place['properties']['CompanyMetaData']:
                phones = place['properties']['CompanyMetaData']['Phones']

                if isinstance(phones, list):
                    formatted_phones = []
                    for phone in phones:
                        formatted_phone = phone.get('formatted')
                        formatted_phones.append(formatted_phone)
                else:
                    formatted_phones = ['Phone number not available']
            else:
                formatted_phones = ['Phone number not available']

            # Checking for the presence of the 'url' key in the data
            if 'url' in place['properties']['CompanyMetaData']:
                place_url = place['properties']['CompanyMetaData']['url']
            else:
                place_url = "URL not available"

            image_url = search_images(name + " " + address)
            # Here we create a dictionary with data
            place_data = {
                "name": name,
                "address": address,
                "description": description,
                "formatted_phones": formatted_phones,
                "place_url": place_url,
                "image_url": image_url,
                "coordinates": coordinates
            }

            # Save the data as a JSON file
            save_place_data(place_data, name)

            # Create a keyboard with a "Get detailed information" button
            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton("Get detailed information",
                                                 callback_data=f"full_description_{name}")
            markup.add(button1)

            # Create a keyboard with a "Find the way" button
            button2 = types.InlineKeyboardButton("Find the way",
                                                 callback_data=f"find_way_{name}")
            markup.add(button2)

            # Create a keyboard with a "Save the place" button
            button3 = types.InlineKeyboardButton("Want to visit",
                                                 callback_data=f"want_visit_{name}")
            markup.add(button3)

            # Create a keyboard with a "Save the place" button
            button4 = types.InlineKeyboardButton("I've already visited",
                                                 callback_data=f"i_visited_{name}")
            markup.add(button4)

            # Sending location information to user
            bot.send_message(message.chat.id,
                             "*Name:*  {}\n*Address:*  {}\n\n*Description:*  {}\n\n*Phones:* \n{}\n\n*Url:*  {}".format(
                                 name,
                                 address,
                                 description,
                                 '\n'.join(
                                     formatted_phones),
                                 place_url),
                             parse_mode="Markdown",
                             disable_web_page_preview=True,
                             reply_markup=markup)

            places_count += 1  # Increasing the place counter
            # If 1 places have already been displayed, interrupt the cycle
            if places_count >= 1:
                break

        else:
            bot.send_message(message.chat.id, "Sorry, nothing found.")


@bot.callback_query_handler(func=lambda call: call.data.startswith('full_description_'))
def handle_callback_query(call):
    data = call.data.split('_')
    name = data[2]

    # Open a JSON file with location data
    filename = f"{name}.json"
    with open(filename, "r") as file:
        place_data = json.load(file)

    # Extracting data from JSON and storing it in the appropriate variables
    place_name = place_data["name"]
    place_address = place_data["address"]
    place_description = place_data["description"]
    place_formatted_phones = place_data["formatted_phones"]
    place_url = place_data["place_url"]
    place_image_url = place_data["image_url"]

    generate_pdf(place_name, place_address, place_description, place_formatted_phones, place_url, place_image_url)

    with open("{}.pdf".format(name), "rb") as pdf_file:
        bot.send_document(call.message.chat.id, pdf_file)
    # Delete PDF file after sending
    os.remove("{}.pdf".format(name))


# Global variable for storing coordinates
place_user_coordinates = None


@bot.callback_query_handler(func=lambda call: call.data.startswith('find_way_'))
def handle_callback_query(call):
    global place_user_coordinates  # Declare a variable as global
    data = call.data.split('_')
    name = data[2]

    # Open a JSON file with location data
    filename = f"{name}.json"
    with open(filename, "r") as file:
        place_data = json.load(file)

    place_coordinates = place_data["coordinates"]

    # We send the user a request to enter coordinates
    bot.send_message(call.message.chat.id,
                     "Enter the coordinates of your location in the format 'latitude, longitude'. "
                     "Start your message with '/coordinates'")

    @bot.message_handler(func=lambda message: message.text.startswith('/coordinates'))
    def handle_coordinates(message):
        chat_id = message.chat.id
        user_coordinates = message.text

        # We are looking for the index of the '/' symbol to ignore it and take only numbers
        start_index = user_coordinates.find('/coordinates')

        if start_index == -1:
            bot.send_message(chat_id,
                             "Please start your message with '/coordinates' followed by latitude and longitude.")
            return

        user_coordinates = user_coordinates[start_index + len('/coordinates'):].strip()

        # We check that the entered text matches the format 'latitude, longitude'
        coordinates = user_coordinates.split(',')
        if len(coordinates) != 2:
            bot.send_message(chat_id, "Please enter coordinates in the format 'latitude, longitude'.")
            return

        try:
            latitude = float(coordinates[0].strip())
            longitude = float(coordinates[1].strip())
        except ValueError:
            bot.send_message(chat_id, "Invalid coordinates format. Please enter numbers for latitude and longitude.")
            return

        # Save user's latitude and longitude
        place_user_coordinates = [latitude, longitude]

        print(place_user_coordinates)
        print(place_coordinates)

        start_location = place_user_coordinates
        end_location = place_coordinates

        start_location = ', '.join(map(str, start_location))
        end_location = ', '.join(map(str, end_location))

        start_coords = get_coordinates_by_address(start_location)
        end_coords = get_coordinates_by_address(end_location)

        if start_coords and end_coords:
            distance = calculate_distance(start_coords[0], start_coords[1], end_coords[0], end_coords[1])
            bot.send_message(chat_id, f"Distance between points: "
                                      f"{distance * 0.621371:.2f} mi")  # convert to miles
            zoom = get_map_zoom(distance)
            get_static_map(start_location, end_location, zoom)
        else:
            bot.send_message(chat_id, "Could not determine coordinates for the specified addresses.")

        directions_str = get_directions(start_location, end_location)

        bot.send_message(chat_id, directions_str)

        # Open the file 'map.jpg' and send it to the user
        with open('map.jpg', 'rb') as map_file:
            bot.send_photo(message.chat.id, map_file)


@bot.callback_query_handler(func=lambda call: call.data.startswith('want_visit_'))
def handle_callback_query(call):
    data = call.data.split('_')
    name = data[2]

    # Open a JSON file with location data
    filename = f"{name}.json"
    with open(filename, "r") as file:
        place_data = json.load(file)

    # Extracting data from JSON and storing it in the appropriate variables
    place_name = place_data["name"]

    user_id = call.message.chat.id

    # Function to check and add a user to the Users table
    def check_and_add_user(user_id):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        # Check the presence of a user in the Users table
        cursor.execute("SELECT ID FROM Users WHERE ID=?", (user_id,))
        user_exists = cursor.fetchone()

        if not user_exists:
            # If there is no user, add him
            cursor.execute("INSERT INTO Users (ID) VALUES (?)", (user_id,))
            connection.commit()

        connection.close()

    def check_and_add_place(user_id, place_name):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        cursor.execute("SELECT ID FROM WantToVisit WHERE ID=? AND Place=?", (user_id, place_name))
        place_exists = cursor.fetchone()

        if not place_exists:
            cursor.execute("INSERT INTO WantToVisit (ID, Place) VALUES (?, ?)", (user_id, place_name))
            connection.commit()

        connection.close()

    # Check and add the user to the Users table
    check_and_add_user(user_id)

    # Check and add an entry to the WantToVisit table
    check_and_add_place(user_id, place_name)

    bot.send_message(chat_id=user_id, text="The place you want to visit was saved!")


@bot.callback_query_handler(func=lambda call: call.data.startswith('i_visited_'))
def handle_callback_query(call):
    data = call.data.split('_')
    name = data[2]

    # Open a JSON file with location data
    filename = f"{name}.json"
    with open(filename, "r") as file:
        place_data = json.load(file)

    # Extracting data from JSON and storing it in the appropriate variables
    place_name = place_data["name"]

    user_id = call.message.chat.id  # Получаем ID пользователя из объекта chat

    # Function to check and add a user to the Users table
    def check_and_add_user(user_id):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        # Check the presence of a user in the Users table
        cursor.execute("SELECT ID FROM Users WHERE ID=?", (user_id,))
        user_exists = cursor.fetchone()

        if not user_exists:
            # If there is no user, add him
            cursor.execute("INSERT INTO Users (ID) VALUES (?)", (user_id,))
            connection.commit()

        connection.close()

    # Function to check and add an entry to the Visited table
    def check_and_add_place(user_id, place_name):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        # Check for an entry in the WantToVisit table for a given user and location
        cursor.execute("SELECT ID FROM Visited WHERE ID=? AND Place=?", (user_id, place_name))
        place_exists = cursor.fetchone()

        if not place_exists:
            # If there is no entry, add it
            cursor.execute("INSERT INTO Visited (ID, Place) VALUES (?, ?)", (user_id, place_name))
            connection.commit()

        connection.close()

    # Check and add the user to the Users table
    check_and_add_user(user_id)

    # Check and add an entry to the WantToVisit table
    check_and_add_place(user_id, place_name)

    bot.send_message(chat_id=user_id, text="The place you've already visited was saved!")


@bot.message_handler(func=lambda message: message.text == "Want to visit")
def want_to_visit(message):
    user_id = message.from_user.id

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT Place FROM WantToVisit WHERE ID=?", (user_id,))
    places = cursor.fetchall()

    conn.close()

    if places:
        # If there are entries in the database, send the user a list of places
        places_list = [place[0] for place in places]
        places_message = "\n".join(places_list)
        bot.send_message(message.chat.id, f"The places you want to visit:\n\n{places_message}")
    else:
        bot.send_message(message.chat.id, "You don't have any entries about the places you want to visit.")


@bot.message_handler(func=lambda message: message.text == "I've already visited")
def want_to_visit(message):
    user_id = message.from_user.id

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT Place FROM Visited WHERE ID=?", (user_id,))
    places = cursor.fetchall()

    conn.close()

    if places:
        # If there are entries in the database, send the user a list of places
        places_list = [place[0] for place in places]
        places_message = "\n".join(places_list)
        bot.send_message(message.chat.id, f"The places you've already visited':\n\n{places_message}")
    else:
        bot.send_message(message.chat.id, "You don't have any entries about the places you've already visited.")


if __name__ == '__main__':
    bot.polling()
