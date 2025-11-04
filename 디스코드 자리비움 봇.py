
import discord
from discord.ext import commands

# 디스코드 봇 토큰
TOKEN = ''

# 봇 명령어 접두사
bot = commands.Bot(command_prefix='!!!', intents=discord.Intents.all())

# 상태 정보를 저장할 딕셔너리
afk_users = {}
dnd_users = {}
unavailable_users = {}
prior_users = {}

# 점검 알림방 및 로그 채널 정보 저장
maintenance_channel = None
maintenance_role = None
log_channel = None

@bot.event
async def on_ready():
    print(f'봇이 로그인되었습니다. {bot.user}')

@bot.event
async def on_message(message):
    # 봇 자신이 메시지를 보낼 경우 무시합니다.
    if message.author == bot.user:
        return
    
    # 다른 사람이 봇을 @멘션하거나, 유저를 @멘션한 경우 처리
    mentioned_users = message.mentions
    if mentioned_users:
        for mentioned_user in mentioned_users:
            # 언급된 유저의 상태 확인
            embed = None
            if mentioned_user.id in afk_users:
                embed = discord.Embed(title="자리비움 상태", description=f"{mentioned_user.mention}님은 자리비움 상태입니다.", color=discord.Color.blue())
                embed.add_field(name="사유", value=afk_users[mentioned_user.id], inline=False)
            elif mentioned_user.id in dnd_users:
                embed = discord.Embed(title="방해 금지 상태", description=f"{mentioned_user.mention}님은 방해 금지 상태입니다.", color=discord.Color.red())
                embed.add_field(name="사유", value=dnd_users[mentioned_user.id], inline=False)
            elif mentioned_user.id in unavailable_users:
                embed = discord.Embed(title="게임 못함 상태", description=f"{mentioned_user.mention}님은 게임 못함 상태입니다.", color=discord.Color.orange())
                embed.add_field(name="사유", value=unavailable_users[mentioned_user.id], inline=False)
            elif mentioned_user.id in prior_users:
                embed = discord.Embed(title="선약 상태", description=f"{mentioned_user.mention}님은 선약 상태입니다.", color=discord.Color.purple())
                embed.add_field(name="사유", value=prior_users[mentioned_user.id], inline=False)
            
            # 상태가 설정되어 있다면 임베드로 사유를 표시
            if embed:
                await message.channel.send(embed=embed)
    
    # 봇이 명령어를 처리하도록 해야 하므로 반드시 'await bot.process_commands(message)' 호출
    await bot.process_commands(message)

async def prompt_for_reason(ctx, title, color):
    """사용자에게 사유를 입력받는 공통 함수"""
    await ctx.author.send(f"{ctx.author.mention}, `{ctx.command}` 명령어를 처리하기 위해 사유를 입력해주세요.")
    
    def check(msg):
        return msg.author == ctx.author and isinstance(msg.channel, discord.DMChannel)
    
    try:
        dm_message = await bot.wait_for('message', check=check, timeout=60)
        reason = dm_message.content

        embed = discord.Embed(title=title, description=f"{ctx.author.mention}님의 상태입니다.", color=color)
        embed.add_field(name="사유", value=reason, inline=False)
        return embed, reason
    except Exception:
        await ctx.author.send("사유 입력 시간이 초과되었습니다. 명령어를 다시 입력해주세요.")
        return None, None

# !!!자리비움
@bot.command()
async def 자리비움(ctx):
    embed, reason = await prompt_for_reason(ctx, "자리비움", discord.Color.blue())
    if embed:
        afk_users[ctx.author.id] = reason
        await ctx.reply(embed=embed)

        # 로그 채널에 기록
        if log_channel:
            await log_channel.send(f"[자리비움] {ctx.author.mention} - 사유: {reason}")

# !!!방해금지
@bot.command()
async def 방해금지(ctx):
    embed, reason = await prompt_for_reason(ctx, "방해 금지", discord.Color.red())
    if embed:
        dnd_users[ctx.author.id] = reason
        await ctx.reply(embed=embed)

        # 로그 채널에 기록
        if log_channel:
            await log_channel.send(f"[방해금지] {ctx.author.mention} - 사유: {reason}")

# !!!게임못함
@bot.command()
async def 게임못함(ctx):
    embed, reason = await prompt_for_reason(ctx, "게임 못함", discord.Color.orange())
    if embed:
        unavailable_users[ctx.author.id] = reason
        await ctx.reply(embed=embed)

        # 로그 채널에 기록
        if log_channel:
            await log_channel.send(f"[게임못함] {ctx.author.mention} - 사유: {reason}")

# !!!선약
@bot.command()
async def 선약(ctx):
    embed, reason = await prompt_for_reason(ctx, "선약", discord.Color.purple())
    if embed:
        prior_users[ctx.author.id] = reason
        await ctx.reply(embed=embed)

        # 로그 채널에 기록
        if log_channel:
            await log_channel.send(f"[선약] {ctx.author.mention} - 사유: {reason}")

# !!!복귀
@bot.command()
async def 복귀(ctx):
    user = ctx.author
    if user.id in afk_users:
        afk_users.pop(user.id)
        await ctx.reply(f'{user.mention}님이 자리비움 상태에서 복귀하였습니다.')

        # 로그 채널에 기록
        if log_channel:
            await log_channel.send(f"[복귀] {user.mention} - 자리비움 상태 해제")
    elif user.id in dnd_users:
        dnd_users.pop(user.id)
        await ctx.reply(f'{user.mention}님이 방해 금지 상태에서 복귀하였습니다.')

        # 로그 채널에 기록
        if log_channel:
            await log_channel.send(f"[복귀] {user.mention} - 방해 금지 상태 해제")
    elif user.id in unavailable_users:
        unavailable_users.pop(user.id)
        await ctx.reply(f'{user.mention}님이 게임 못함 상태에서 복귀하였습니다.')

        # 로그 채널에 기록
        if log_channel:
            await log_channel.send(f"[복귀] {user.mention} - 게임 못함 상태 해제")
    elif user.id in prior_users:
        prior_users.pop(user.id)
        await ctx.reply(f'{user.mention}님이 선약 상태에서 복귀하였습니다.')

        # 로그 채널에 기록
        if log_channel:
            await log_channel.send(f"[복귀] {user.mention} - 선약 상태 해제")
    else:
        await ctx.reply(f'{user.mention}님은 현재 자리비움, 방해 금지, 게임 못함, 또는 선약 상태가 아닙니다.')

# !!!도움
@bot.command()
async def 도움(ctx):
    embed = discord.Embed(
        title="도움말",
        description="사용 가능한 명령어 목록입니다.",
        color=discord.Color.green()
    )
    embed.add_field(name="!!!자리비움", value="자리비움 상태를 설정합니다.", inline=False)
    embed.add_field(name="!!!방해금지", value="방해 금지 상태를 설정합니다.", inline=False)
    embed.add_field(name="!!!게임못함", value="게임 못함 상태를 설정합니다.", inline=False)
    embed.add_field(name="!!!선약", value="선약 상태를 설정합니다.", inline=False)
    embed.add_field(name="!!!복귀", value="자리비움 또는 방해 금지 상태를 해제합니다.", inline=False)
    await ctx.reply(embed=embed)

# !!!로그 <채널>
@bot.command()
async def 로그(ctx, channel: discord.TextChannel):
    global log_channel
    if log_channel:
        await ctx.reply(f"이미 로그 채널이 {log_channel.mention}으로 설정되어 있습니다.")
    else:
        log_channel = channel
        await ctx.reply(f"로그 채널이 {channel.mention}으로 설정되었습니다.")

    # 상태별 유저와 사유를 로그로 기록
    if log_channel:
        await log_channel.send(f"[로그 설정됨] 상태 변경 사항 기록 시작")

# !!!점검알림방 <채널> <역할>
@bot.command()
async def 점검알림방(ctx, channel: discord.TextChannel, role: discord.Role):
    global maintenance_channel, maintenance_role
    if maintenance_channel:
        await ctx.reply(f"점검 알림방이 이미 {maintenance_channel.mention}으로 설정되어 있습니다.")
    else:
        maintenance_channel = channel
        maintenance_role = role
        await ctx.reply(f"점검 알림방이 {channel.mention}으로 설정되었고, 알림 역할이 {role.mention}으로 설정되었습니다.")

# !!!점검 <사유>
@bot.command()
async def 점검(ctx, *, reason="사유 없음"):
    if maintenance_channel and maintenance_role:
        embed = discord.Embed(
            title="게임 점검 알림",
            description=f"게임 점검이 예정되어 있습니다.",
            color=discord.Color.gold()
        )
        embed.add_field(name="사유", value=reason, inline=False)
        embed.set_footer(text=f"공지 담당자: {ctx.author.display_name}")

        await maintenance_channel.send(f"{maintenance_role.mention}", embed=embed)
        await ctx.reply("점검 알림이 전송되었습니다.")
    else:
        await ctx.reply("점검 알림방 또는 알림 역할이 설정되지 않았습니다. !!!점검알림방 명령어로 먼저 설정해주세요.")

# 봇 실행
bot.run('')