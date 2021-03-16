# nerdlandbot
This is a Python-based discord bot developed by the nerdland fan community.

# Roadmap
This bot was setup mostly as an experiment, and there is no clearly defined goal so far.
If you have any suggestions feel free to log an issue in this repository, any new ideas or challenges are much appreciated.

# Privacy policy.
This bot was developed with privacy as one of our core ideals.
Because of this we have formulated a few statements about the inner workings.

The bot will only listen to user commands. 
We will not parse any user messages, nor track any reactions, unless those made specifically to interact with the bot.
We will not track any user data, except for your user ID, as this is required to notify you.
We will not store any data about your messages, reactions, or other actions you take on discord.

The logs we keep are strictly for debugging purposes, and will not contain any personal info.

# Setting up your development environment
To get this project up and running, make sure you have the following installed:
- Python 3
- PIP
- [Poetry](https://python-poetry.org/docs/#installation)
- Use your favourite ide and git to clone the nerdlandbot to your local machine

Once you have these installed (you can check by running 'python --version', 'pip -V' and 'poetry -V' in a commandline), add the required packages (see requirements.txt). To do this, you have 2 options (choose only 1):

1. If you're just starting out with python and "virtual environment" doesn't ring a bell, using pip will install the required packages in a way you can use them anywhere. You can run this command in a terminal from any folder you like.
```
pip install -r requirements.txt
```

2. If you have more experience and work with virtual environments, poetry is more your kind of thing and will make the required packages available for this specific project only. You should run this command in the folder you created when cloning the repository, the one where README.md is located.
```
poetry install
```

# Creating your own test bot
When trying out things, it's best to create your own bot and use that one to test your code. To create your test version of the nerdlandbot:
- Go to discord.com https://discord.com/login?redirect_to=%2Fdevelopers%2Fapplications and log in.
- Create a new application eg. "bob-testbot"
- Switch to the 'Bot' configuration (select 'Bot' on the left panel)
- Create a bot and give it a name "bob-testbot" for example
- Make sure you set both 'Presence intent' and 'Server members intent' under 'Privileged Gateway Intents'

# Get your bot invited to servers
To get your bot invited onto a server, you need to create an invitation URL.
- Go to your application (see creating your own test bot above)
- Copy the "client id" from your application (! NOT your bot token !)
- The URL to invite your bot to a server is: https://discord.com/api/oauth2/authorize?client_id=<APPLICATION_CLIENT_ID>&permissions=0&scope=bot

When visiting that page, you'll see a list of servers you have administration rights for. If you have your own server, it will be listed here. 
If you want to test on the NerdlandBottest server, provide this URL in the #helpdesk channel and kindly ask somebody to accept your bot and create a test channel.
Alternatively, you will need to acquire a `DISCORD_TOKEN`. It is possible to obtain one with a developer account on Discord.

# Create your .env file
You need a file to keep your bot token safely. You'll do this by creating a file with name ".env" which must contain following lines:
```
# .env
DISCORD_TOKEN=<BOT_TOKEN>
PREFIX=?
```
Make sure this file is listed in the .gitignore file, so your bot token isn't uploaded to github for everyone to see (and use).

# Using YouTube functionality 

For using the YouTube notifications functionality you'll need to set the `YOUTUBE TOKEN` in your `.env` file. Follow the instructions [here](https://developers.google.com/youtube/registering_an_application) to create an API key.


# Using spreadsheet functionality

* To use the spreadsheet functionality you'll need to go [here](https://console.developers.google.com/?hl=nl).  
* Login with your google-account. Click "create project".  
* Give the project a name and click "create". Then click on "enable apis and services".  
* Look for "sheets" and click on "Google Sheets API". Then click on "enable".  
* On the right-side, click "create credentials". Select "Google Sheets API". On the next question select "web server".  
* Select "Application data" and "no, I'm not using them". Click "what credentials do I need?".  
* Fill in the fields and for the role select "project -> editor". Select JSON if not yet selected. Click "continue".  
* You'll automatically download the JSON. Rename it to something shorter and don't share it!  
* Put it in the same folder as the .env-file. Go into the JSON to copy the client_email field.  
* Add that email in google sheets like you'd add a normal user.  
* In the .env-file add a field `SHEETS_JSON` and enter the JSON-filename with double quotes around it.  
* Add another field named `SPREADSHEET` and enter the spreadsheetname in double quotes. 


# Running the bot on your local machine
You can now run the bot by running the following command in the root of your nerdlandbot folder:
```
python -m nerdlandbot
```



# Running this bot with docker

```
docker run -itd --restart="unless-stopped" --name nerdlandbot \
 -e PREFIX=<Your prefix here> \
 -e DISCORD_TOKEN=<Your discord token here> \
 -v <Your bind mount path for guild configs>:/GuildConfigs \
 nerdlandfansunofficial/nerdlandbot:latest
```

# Links
* [Nerdland website](https://nerdland.be)
* [Nerdland merch](https://www.mistert.be/nerdland)
