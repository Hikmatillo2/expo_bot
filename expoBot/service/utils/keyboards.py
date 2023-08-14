import telebot


class InlineKeyboard(telebot.types.InlineKeyboardMarkup):
    def __init__(self, text: list[list[str, str]] | list[list[list[str, str]]]):
        super().__init__()
        self.text = text
        self.make_keyboard()

    def make_keyboard(self):
        for text in self.text:
            if type(text) == list:
                self.row(*[telebot.types.InlineKeyboardButton(button[0], callback_data=button[1]) for button in text])
            else:
                self.add(telebot.types.InlineKeyboardButton(text[0], callback_data=text[1]))


class Keyboard(telebot.types.ReplyKeyboardMarkup):
    def __init__(self, text: list[str] | list[list[str]], resize: bool = True):
        super().__init__()
        self.resize_keyboard = resize
        self.text = text
        self.make_keyboard()

    def make_keyboard(self):
        for text in self.text:
            if type(text) == list:
                self.row(*[telebot.types.KeyboardButton(text_[0]) for text_ in text])
            else:
                self.add(telebot.types.KeyboardButton(text))
