## A quick note

This is not a good discord bot by any means. I don't recommend you use it as a moderation bot. It was simply just a small project for me to work on my python skills.

## Getting Started

To use this bot, you'll need to create a bot application on the Discord Developer Portal and obtain a bot token. Here's how to set it up:

1. If you have git installed, run `git clone https://github.com/aem2231/bot.git` otherwise download [this zip file](https://github.com/aem2231/bot.git) and extract it to suitable directory.
   
2. Create a Discord Bot Application:

   - Go to the [Discord Developer Portal](https://discord.com/developers/applications) and log in or create an account if you don't have one already.
   - Click on "New Application" to create a new application. Make sure to give it an appropriate name.
   - Go to the "Bot" tab on the left sidebar and click "Add Bot" to create a bot user.
   - Go to the "OAuth2" tab on the left sidebar and click "URL Generator".

3. Invite the bot to a server

   - Select "Bot" as a scope and select the required permissions. It must have the "Send Messages" permission as a minimum.
   - For moderation commands to work, you must select "Kick Members" and "Ban Members" permissions. I will hopefully add more in the future.
   - Copy the URL under the scopes menue, paste it into a browser and select the server you want the bot to join.

4. Obtain the Bot Token and neccesary API keys:

   - Under the "Token" section in the bot settings, click "Reset Token". You may have to enter your password or 2FA code to do this.
   - Once your token has been revealed, click "Copy Token" to copy it to your clipboard.
   - Go to the [Giphy Developer page](https://developers.giphy.com/) and create and account if you doint have one already.
   - Head to your [Dashboard](https://developers.giphy.com/dashboard/) and select 'Create App'. Make sure to select the API option.
   - Once you app as been created, double click your token to copy it to your clipboard.

5. Set up the bot for use:

   5.1 - NixOS only
      - Open your favourite terminal emulator, eg alacritty
      - `cd` to the directory where you cloned this repo to
      - run `nix develop`
         - run your text editor of choice from the terminal, for example `vscode .`

   5.2 - Replace the Token and other API variables:
      - Run the bot by running `python client.py`
      - A `tokens.json` file shouldve been created with the following content, replace the palceholders with the relevent tokens/api keys.
         ```
         {
            "BOT_TOKEN": "your_token",
            "GIPHY_API_TOKEN":"your_giphy_api_key"
         }
         ```
   - Replace 'your_token' with your bots token.
   - Replace 'your_giphy_api_key' with your giphy API key.
   - Make sure you do not remove the double quotations.

6. Run the bot:
   - Run the `client.py` file in your ide/text editor of choice
   - If you've set up the bot correctly, you should see 'Client is running!' in your terminal and the bot will be online.

## Prerequisites

If you are on nixOS, this step can be ignored so long as you followed step 4.1 correctly. 
Before running the bot, make sure you have the necessary libraries installed. You can install them using pip:

```bash
pip install discord.py
pip install qrcode
pip install requests
pip install ping3
```
# silly-bot
