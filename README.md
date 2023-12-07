# Telegram Bot for Locating Interesting Places

This Telegram bot is designed to assist users in discovering fascinating places within a specified location. By leveraging various APIs, the bot provides details about museums, monuments and other points of interest. Users can obtain information, directions, and save places they wish to visit or have already explored.

## Getting Started

### Prerequisites

Before running the bot, you'll need API keys for the following services:

- Telegram API
- Yandex API
- DeepAI API
- Serpapi API
- MapQuest API

### Installation

1. **Clone the repository to your local machine:**

   ```
   git clone https://github.com/your-username/telegram-bot.git
   ```
2. **Navigate to the project directory.**
   ```
   cd telegram-bot
   ```
3. **Install the required dependencies.**
   ```
   pip install -r requirements.txt
   ```

### Configuration

**In the api.py file, replace the placeholder values for API keys with your actual keys:**

   ```
   telegram_api = "telegram_api_key"
   yandex_api = "yandex_api_key"
   deepai_api = "deepai_api_key"
   serpapi_api = "serpapi_api_key"
   mapquest_api = "mapquest_api_key"
   ```
### Usage   
   
**Start the bot by running the main.py script:**

```
python main.py
```

### Functionality

- **Searching for Places:**
  Use the `/search` command to find museums, monuments and more in a specific location.

- **Viewing Details:**
  Use the `Get detailed information` button to receive a PDF document with detailed information about a place, including its name, address, description, phone numbers and URL.

- **Finding the Way:**
  Use the `Find the way` button to get directions and a static map between your location and the chosen place.

- **Saving Places:**
  Save places you want to visit or have already visited. Access the lists with the `Want to visit` and `I've already visited` buttons.

### Additional Scripts

- **geoposition_mapquest.py:**
  Contains functions for calculating distances, obtaining coordinates and generating static maps using the MapQuest API.

- **generate_pdf.py:**
  Defines a function for creating PDFs with place details and images.

- **delete_db.py:**
  A script to delete the SQLite database.

- **get_description_deepai.py:**
  Fetches brief descriptions using the DeepAI text generation API.

- **save_delete_data_as_json.py:**
  Functions to save place data as JSON and delete old JSON files.

- **search_images.py:**
  Searches for images related to a place using the Serpapi image search API.

- **translate_to_english.py:**
  Transliterates Russian characters to English.
