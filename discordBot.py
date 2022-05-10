import os
import time

import discord
from dotenv import load_dotenv
from discord.ext import commands

from td_api import makeCustNameRequests, makeTransfer, makeTransferReceiptRequests, getCustIDfromAccID, makeAccountBalanceRequests

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
guild = int(os.getenv('DISCORD_GUILD'))

bot = commands.Bot(command_prefix='!')

userData = {}

@bot.event
async def on_ready():
    # guild = discord.utils.get(client.guilds, name=GUILD)

    print (f'{bot.user.name} has connected to Discord!')

    await bot.get_guild(guild).create_role(name='verified', colour=discord.Colour.dark_teal())

    # print (f'{guild.name}(id: {guild.id})')

@bot.command(name='balance', help='Check balance')
async def checkBalance(ctx):
    # print (type(ctx.message.channel.type))
    if ctx.message.channel.type == discord.ChannelType.private:
        # print ("Got thru")
        myBalance = makeAccountBalanceRequests(userData[ctx.message.author])
        await ctx.message.author.dm_channel.send("Your account balance is $" + myBalance)

@bot.command(name='register', help='Register new user')
async def createAcc(ctx):
    member=ctx.message.author

    await member.create_dm()
    await member.dm_channel.send("Please enter your account ID:")

    BEGIN = time.time()
    accID = ''

    while accID == '':
        elapsed = time.time() - BEGIN
        if elapsed >= 0.4:
            BEGIN = time.time()
            async for message in member.dm_channel.history(limit=1):
                if message.author == member:
                    accID = message.content

    customerName = makeCustNameRequests(getCustIDfromAccID(accID))

    if customerName == '404':
        await ctx.message.author.dm_channel.send("Sorry! We couldn't find your TD account. Please register again")
        return
    elif customerName == '400':
        await ctx.message.author.dm_channel.send("Sorry! Please check your account ID and register again")
        return
    elif customerName == '500':
        await ctx.message.author.dm_channel.send("Sorry! We ran into an error! Please register again")
        return
    elif not customerName.isdigit():
        await ctx.message.author.dm_channel.send("Is your name " + customerName + "? {y/n}")

        confirm = ''

        while confirm == '':
            elapsed = time.time() - BEGIN
            if elapsed >= 0.4:
                BEGIN = time.time()
                async for message in member.dm_channel.history(limit=1):
                    if message.author == member:
                        if message.content == 'y' or message.content == 'n':
                            confirm = message.content
                        else:
                            await ctx.message.author.dm_channel.send("Please enter {y/n}")

        if confirm == "y":
            await ctx.message.author.dm_channel.send("Thank you for registering!")
            userData [member] = accID

            verifiedRole=None
            
            for i in bot.get_guild(guild).roles:
                if i.name == 'verified':
                    verifiedRole = bot.get_guild(guild).get_role(i.id)
                    
            await member.add_roles(verifiedRole)
            confirm = ''
            return
        elif confirm == "n":
            await ctx.message.author.dm_channel.send("Please check your customer ID again and register again!")
            confirm = ''
            return

@bot.command(name='showUserData', help='Shows list of all registered users')
async def memberOutput(ctx):
    # print (userData)
    memList = ''
    for key in userData:
        memList += " " + key.name + '\n'

    # print (memList)

    if not memList:
        await ctx.send("There don't seem to be anyone logged in to Discord Pay at the moment. Register for free today!")
    else:
        await ctx.send("```Members registered:\n" + memList + "```")


    # print (ctx.message.channel.type)

@bot.command(name='send', help='Arguments: Amount, Recipient, Message(Optional)')
async def sendMoney(ctx,amount,recipient: discord.User,message=""):
    transferID=makeTransfer(amount, userData [ctx.message.author],userData [recipient], message)
    if transferID:
        await ctx.send("Hooray! Your money has been sent!")
        
        transInfo=makeTransferReceiptRequests(transferID)

        await recipient.dm_channel.send("This is the amount transferred: ${}, from: {}, Personalized message: {} ".format(transInfo['result']['amount'], makeCustNameRequests(getCustIDfromAccID(transInfo['result']['fromAccountId'])), transInfo['result']['receipt'][14:-2]))

    else:
        await ctx.send("Oops! There seems to have been an error!")

# @bot.command(name='nick')
# async def checkNick(ctx, member: discord.Member):
#     nickname=member.name
#     await ctx.send(nickname)

# @bot.command(name='kill')
# async def killBot(ctx):
#     await ctx.close()

if __name__ == "__main__":   
    bot.run(token)
