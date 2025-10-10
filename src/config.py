import json
import os

# Construct the absolute path to the tokens.json file
tokens_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tokens.json'))

try:
  with open(tokens_path, "r") as tokens:
    tokenList: dict[str, str] = json.load(tokens)
    discordToken: str = tokenList["BOT_TOKEN"]
    giphyToken: str = tokenList["GIPHY_API_TOKEN"]
except FileNotFoundError:
  with open(tokens_path, "w") as tokens:
    template = {
      "BOT_TOKEN": "your_token",
      "GIPHY_API_TOKEN": "your_giphy_api_key"
    }
  json.dump(template, tokens, indent=2)
  print(f"tokens.json not found. A template has been created at {tokens_path}")
  print("Please paste your bot token and Giphy API key in the tokens.json file.")
  exit()
except (json.JSONDecodeError, KeyError) as e:
  print(f"Error reading or parsing tokens.json: {e}")
  print("Please ensure tokens.json is formatted correctly and contains BOT_TOKEN and GIPHY_API_TOKEN.")
  exit()
