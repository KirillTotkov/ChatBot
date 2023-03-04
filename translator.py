from googletrans import Translator

translator = Translator()


def translate_message_to_english(text: str) -> str:
    try:
        result = translator.translate(text).text
        return result
    except Exception as e:
        return e


def translate_message_to_russian(text: str) -> str:
    try:
        result = translator.translate(text, dest='ru').text
        return result
    except Exception as e:
        return e
