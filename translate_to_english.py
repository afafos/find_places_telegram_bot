from transliterate import translit


def translate_to_english(input_string):
    # Checking if there are Russian characters in the string
    has_russian_chars = any(char.isalpha() and 'а' <= char <= 'я' for char in input_string.lower())

    if has_russian_chars:
        # If there are Russian characters, then we transliterate the string
        transliterated_string = translit(input_string, 'ru', reversed=True)
        return transliterated_string
    else:
        # If there are no Russian characters, return the original string
        return input_string

