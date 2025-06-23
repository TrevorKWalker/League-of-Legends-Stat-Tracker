import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import json
import RiotApiConnection as RAC
import Connections
import Google_Sheets_Connection as GSC

with open("People.json", "r") as f: 
        SUMMONERS = json.load(f)

load_dotenv()
DISCORD_API_KEY = os.getenv("DISCORD_API_KEY")

intents = discord.Intents.default()
intents.message_content = True 
 
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None, case_insensitive=True)


@bot.event
async def on_ready():
    
    print(f'✅ Logged in as {bot.user}')


#####################
# new user command  #
#####################
@bot.command()
async def new_user(ctx, name ,summoner_name, tag, region):
    # check to see is the user is already accounted for
    if name in SUMMONERS:
        await ctx.send(f'Sorry but {name} is already a player in the system. 👋')

    # main logic to add a user
    else:
        # adds the info to the global variable 
        # doesnt write to json immediately incase the command info was invalid
        SUMMONERS[name] = {
            "summoner_name": summoner_name,
            "tag": tag,
            "region": region,
            "puuid":  None
        }
        # protection against invalid entries 
        try: 
            #grabs Puuid which is first possible point of failure
            SUMMONERS[name]["puuid"] = RAC.Get_Puuid(region, summoner_name, tag)
        except:
            # sends message back to user explaining failure 
            # returns to prevent any crashes
            await ctx.send(f'Sorry, I couldn\'t find {name}\'s data in riots server. Please check that all the information is correct and try again. If you are unsure of the format for this command use !help.')
            return
        # writes to the json file which is neccassary for the Connections.create_new_player to work 
        with open("People.json", "w") as f:
            json.dump(SUMMONERS, f, indent = 2)
        #second try statement
        # used two because i wanted different Exception statements 
        try: 
            # update_summoners re-initializes the SUMMONERS variable that is held in Connections.py
            # then creates the player which adds them to the sheet and populates their last ten games
            Connections.update_SUMMONERS()
            Connections.create_new_player(name, "Discord bot stats", "output.csv")
        except:
            #if it fails we need to remove it from the json file so we pop and then write the new one to the file
            SUMMONERS.pop(name)
            with open("People.json", "w") as f:
                json.dump(SUMMONERS, f, indent = 2)
            await ctx.send(f'Sorry, There was a problem retriving previous games for this user. Please try again later.')
            return
        await ctx.send(f'{name} Successfully registered. 👍')


@bot.command(name="help", aliases=["commands"])
async def help_command(ctx, command = None):
    #if else statement to determine which command the user wants explained to them
    if command == None:
        #If the user doesnt specify a command then we will send back a list of all the commands.
        await ctx.send("Please enter a command to recieve more information about it.")
        #this creates essentially a widget that will hold our information so it stands out against just messages
        embed = discord.Embed(
            title="📖 Bot Help",
            description="Here's a list of available commands:",
            color=discord.Color.blurple()
        )
        #this is our field where we will put all of the availible commands
        embed.add_field(name="!new_user <name> <summoner name> <tag> <region>\n!remove_user <name>\n!display_scoreboard\n!credit",
            value= "",                
            inline= False      
                        
        )
    elif command == "new_user" or command == "!new_user":
        embed = discord.Embed(
            title="📖 new_user Help",
            description="!new_user <name> <summoner name> <tag> <region>",
            color=discord.Color.blurple()
        )
        #this is our field where we will put all of the availible commands
        embed.add_field(name="<name>",
            value= "The name field is an alphanumeric string that will be used as the name for your sheet and your user. I suggest you use your real name or discord username. If you include any spaces be sure to wrap your name in quotes.",                
            inline= False                   
        )
        embed.add_field(name="<summoner name>",
            value= "The summoner name field is an alphanumeric string that corresponds to your riot games summoner name. This is the name you see in game and is case sensitive. If you include any spaces be sure to wrap your name in quotes.",                
            inline= False                   
        )
        embed.add_field(name="<tag>",
            value= "The tag field is the #NA1 or equivalent that appears after your summoner name in client. For this field please do not include the # character and simply put NA1 or the equivalent.",                
            inline= False                   
        )
        embed.add_field(name="<region>",
            value= "This field should be the region that your account is from. e.g. 'americas' ",                
            inline= False                   
        )
    #footer that gives me credit
    embed.set_footer(text="Made by: Trevor Walker", icon_url="https://i.imgur.com/9vBTKl0.png") 
    await ctx.send(embed=embed)



bot.run(DISCORD_API_KEY)