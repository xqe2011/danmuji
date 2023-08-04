import emoji, re

def isAllCharactersEmoji(content):
    string = emoji.replace_emoji(content, '[emoji]')
    string = re.sub(r'\[.*?\]', '', string)
    return string == ''
