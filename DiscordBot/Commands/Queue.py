from DiscordBot.Init import bot, voice_clients
import random


@bot.command(name="list")
async def list_queue(ctx):
    vc = voice_clients.get(ctx.guild.id)
    if not vc or not vc.queue:
        await ctx.send("The queue is currently empty.")
        return

    message = "Current Queue:"
    for i, item in enumerate(vc.queue, start=1):
        if i < 20: message += f"\n{i}. {item.artist} - {item.track}"
    await ctx.send(message)


@bot.command(name="clear")
async def clear(ctx):
    vc = voice_clients.get(ctx.guild.id)
    if vc: vc.queue.clear()
    await ctx.send("Cleared the queue.")


@bot.command(name='shuffle')
async def shuffle(ctx):
    vc = voice_clients.get(ctx.guild.id)
    if not vc or not vc.queue:
        await ctx.send("The queue is empty, nothing to shuffle.")
        return

    random.shuffle(vc.queue)
    await ctx.send("Shuffled the queue")
