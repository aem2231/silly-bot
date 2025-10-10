import json

try: 
    with open("tokens.json", "r") as tokens:
        tokenList = json.load(tokens)
    discordToken = tokenList['BOT_TOKEN']
    giphyApiKey = tokenList['GIPHY_API_KEY']
except FileNotFoundError:
    with open("tokens.json", "w") as tokens:
        template = {"BOT_TOKEN": "your_token", "GIPHY_API_KEY": "your_giphy_api_key"}
        json.dump(template, tokens)
except json.JSONDecodeError:
    print("Error decoding JSON in tokens.json. Please check the file format.")
