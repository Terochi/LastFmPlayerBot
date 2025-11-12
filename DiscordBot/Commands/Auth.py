from DiscordBot.Init import bot
from LastFmApi.Auth import get_token, wait_for_session, get_auth_link
from LastFmApi.Users import last_fm_users, save_last_fm_users


@bot.command(name="register")
async def register(ctx):
    token = await get_token()
    await ctx.send(f"Authenticate using this link:\n{get_auth_link(token)}")
    session = await wait_for_session(token)
    if not session:
        await ctx.send(f"Authentication expired.")
        return

    last_fm_users[str(ctx.author.id)] = {
        'name': session["name"],
        'key': session["key"],
    }
    save_last_fm_users()
    await ctx.send(f"Registered your Last.fm as {session["name"]}.")


@bot.command(name="unregister")
async def unregister(ctx):
    last_fm_users.pop(str(ctx.author.id))
    save_last_fm_users()
    await ctx.send(f"Unregistered your Last.fm.")
