import os
import disnake
import config as con
from pymongo import MongoClient
from keepAlive import keep_alive
from disnake.ext import commands

bot = commands.Bot(command_prefix = '?',intents = disnake.Intents.all())
cluster = MongoClient(con.MONGODB_URL)
clans = cluster.botdb.clans

@bot.command(aliases=['c-create'])
async def c_create(ctx, name: str = None):
    if not name:
      return await ctx.send("Укажи имя клану!")
    post = {
        "owner": ctx.author.id,
        "name": name,
        "members": [],
        "rep": 0
    }
    clans.insert_one(post)
    await ctx.send("Клан успешно создан!")

@bot.command(aliases=['c-delete'])
async def c_delete(ctx, name: str = None):
    if not name:
        return await ctx.send("Укажи имя клана, который ты хочешь удалить!")
    clan = clans.find_one({"name": name})
    if not clan:
        return await ctx.send("Такой клан не найден!")
    if ctx.author.id != clan['owner']:
        return await ctx.send("Только владелец клана может удалить его!")
    clans.delete_one({"name": name})
    await ctx.send("Клан успешно удален!")

@bot.command(aliases=['c-info'])
async def c_info(ctx, name: str = None):
    if not name:
        return await ctx.send("Укажи имя клану!")
    clan_obj = clans.find_one({"name": name})
    if not clan_obj:
        return await ctx.send("Клана с таким названием не существует!")

    arr_members = []
    for member in clan_obj['members']:
        arr_members.append(ctx.guild.get_member(member).name)
    members_str = "\n".join(arr_members)
      
    await ctx.send(f"Название: {clan_obj['name']}, Овнер: {clan_obj['owner']}\nУчастники: {members_str}")

@bot.command(aliases=['c-add'])
async def c_add(ctx, member: disnake.Member = None):
     if not member:
         return await ctx.send("Укажи пользователя, которого хочешь добавить в клан!")

     clan_obj = clans.find_one({"owner": ctx.author.id})

     if not clan_obj:
       return await ctx.send("Вы не являетесь создателем какого-либо клана!")

     find = False
     for clan in clans.find():
       if member.id in clan['members']:
           find = True

     if find:
      return await ctx.send("Указанный вами пользователь состоит в каком-либо клане!")
      
     arr_members = clan_obj['members']
     arr_members.append(member.id)
    
     clans.update_one({"owner": ctx.author.id}, {"$set":{"members": arr_members}})       
     await ctx.send("Успешно!")

@bot.command(aliases=['c-remove'])
async def c_remove(ctx, member: disnake.Member = None):
     if not member:
         return await ctx.send("Укажи пользователя, которого хочешь кикнуть из клана!")

     clan_obj = clans.find_one({"owner": ctx.author.id})

     if not clan_obj:
       return await ctx.send("Вы не являетесь создателем какого-либо клана!")

     if member.id not in clan_obj['members']:
      return await ctx.send("Указанный вами пользователь не состоит в вашем клане!")
      
     arr_members = clan_obj['members']
     arr_members.remove(member.id)
    
     clans.update_one({"owner": ctx.author.id}, {"$set":{"members": arr_members}})       
     await ctx.send("Успешно!")


async def on_ready():
    print(f'Successfully logged in as {bot.user}')

# Commands

@bot.command()
async def hello(ctx):
    await ctx.channel.send(f'Hello! {ctx.author}')

keep_alive()

token = os.environ['TOKEN']
bot.run(token)