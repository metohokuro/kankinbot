from discord.ext import commands
from discord import app_commands
from PayPaython_mobile import PayPay
from Kyasher import Kyash
import asyncio


converted_amount = 0
imputamount = 0
log_channel = 1273093666344538172
flag = 0
#with open("token.txt", "r", encoding="utf-8") as file:
#    ぺいぺいtoken = file.read()


#from aiopaypaythonwebapi import PayPayWebAPI

#url=input("URL?: ")
#paypay.login(url)
#print(paypay.access_token)#アクセストークンは90日有効
#print(paypay.refresh_token)
#print(paypay.device_uuid)#デバイスUUIDで登録デバイスを管理してるぽい
#print(paypay.client_uuid)#クライアントUUIDは特に必要ない

# Botの設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
kankin_rate = 80  # デフォルトの換金率
saitei = 1000
あくせすとーくん = ''
りふれっしゅとーくん = ''
きゃっしゅとーくん = ''

TOKEN = ''

kyash=Kyash(access_token=きゃっしゅとーくん)
paypay=PayPay(access_token=あくせすとーくん)
get_balance=paypay.get_balance()#これも引数なし、PayPay残高を取得する
#print(get_balance.useable_balance)#すべての残高
残高 = (get_balance.all_balance)
kyash.get_wallet()
aaa = (kyash.all_balance)
kankinchannel = 0
paypay.alive()

class KankinView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="スタート", style=discord.ButtonStyle.green)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("換金を開始します！", view=NumberSelectionView(), ephemeral=True)

    @discord.ui.button(label="残高確認", style=discord.ButtonStyle.red)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        global 残高,aaa
        await interaction.response.defer()  # すぐに応答を確保する
        get_balance=paypay.get_balance()#これも引数なし、PayPay残高を取得する
        #print(get_balance.useable_balance)#すべての残高
        残高 = (get_balance.all_balance)
        kyash.get_wallet()
        aaa = (kyash.all_balance)
        await interaction.followup.send(f'paypayは{残高}円でkyashは{aaa}円', ephemeral=True)

class ConfirmButtonView(discord.ui.View):
    def __init__(self, amount, choice):
        super().__init__(timeout=None)
        self.amount = amount
        self.choice = choice  # 1番 or 2番の情報を保存

    @discord.ui.button(label="換金確定", style=discord.ButtonStyle.green)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        global kankinchannel
        await interaction.response.send_modal(TextInputModal(self.choice))
        user = interaction.user
        guild = interaction.guild
        kankinchannel = guild.get_channel(log_channel)

class AmountInputModal(discord.ui.Modal, title="換金額入力"):
    def __init__(self, choice):
        global imputamount
        super().__init__(timeout=None)
        self.choice = choice  # 1番 or 2番を保持
        self.amount_input = discord.ui.TextInput(label="何円換金しますか？", required=True)
        self.add_item(self.amount_input)
        imputamount = self.amount_input

    async def on_submit(self, interaction: discord.Interaction):
        global kankin_rate,converted_amount
        amount = int(self.amount_input.value)
        converted_amount = int(amount * kankin_rate // 100)
        if self.choice == "paypay→kyash":
            if converted_amount > int(aaa):
                await interaction.response.send_message('ごめんなさい。在庫がありません', ephemeral=True)
                return
        if self.choice == "kyash→paypay":
            if converted_amount > int(残高):
                await interaction.response.send_message('ごめんなさい。在庫がありません', ephemeral=True)
                return
        if int(self.amount_input.value) < saitei:
            await interaction.response.send_message("最低金額よりも低いです", ephemeral=True)
        else:
            try:
                amount = int(self.amount_input.value)
                converted_amount = int(amount * kankin_rate // 100)
                view = ConfirmButtonView(converted_amount, self.choice)
                await interaction.response.send_message(f"{converted_amount}円に換金されます", view=view, ephemeral=True)
            except ValueError:
                await interaction.response.send_message("無効な金額です。", ephemeral=True)


        

class TextInputModal(discord.ui.Modal, title="情報入力"):
    def __init__(self, choice):
        super().__init__(timeout=None)
        self.choice = choice

        if self.choice == "paypay→kyash":
            self.input1 = discord.ui.TextInput(label="paypayのリンクを入力", required=True)
            
        else:
            self.input1 = discord.ui.TextInput(label='kyashのリンクを入力', required=True)

        self.add_item(self.input1)
        

    async def on_submit(self, interaction: discord.Interaction):
        global converted_amount,flag
        if 'https://pay.paypay.ne.jp/' in self.input1.value or 'https://kyash.me/payments/' in self.input1.value:
            link = self.input1.value
            if self.choice == "paypay→kyash":
                link_info=paypay.link_check(link)
                if int(link_info.amount) == int(imputamount):
                    if flag == 0:
                        paypay.link_receive(link,link_info=link_info)
                        kankinlink = kyash.create_link(amount=converted_amount,message="換金",is_claim=False)
                        embed = embed = discord.Embed(title="換金成功")
                        embed.add_field(name="商品", value=kankinlink, inline=False)
                        await interaction.user.send(embed = embed)
                        sales_log_embed = discord.Embed(title="【換金】",description=f"購入者: {interaction.user.name}\n何からなにへ: {self.choice}\n何円:{imputamount}\n",color=0xFF0000)
                        await kankinchannel.send(embed = sales_log_embed)
                        flag =1
                    else:
                        await interaction.response.send_message('ごめんなさい。人数制限です。',ephemeral=True)
                        return
                else:
                	interaction.response.send_message(f'金額がちゃいます', ephemeral=True)
            elif self.choice == "kyash→paypay":
                link_info=kyash.link_check(link)
                if int(kyash.link_amount) == int(imputamount):
                    ゆゆあいで = kyash.link_uuid
                    if flag == 0:
                        kyash.link_recieve(url=link,link_uuid=ゆゆあいで)
                        kankinsitalink = paypay.create_link(amount=converted_amount)
                        embed = embed = discord.Embed(title="換金成功")
                        embed.add_field(name="商品", value=kankinsitalink, inline=False)
                        await interaction.user.send(embed = embed)
                        sales_log_embed = discord.Embed(title="【換金】",description=f"購入者: {interaction.user.name}\n何からなにへ: {self.choice}\n何円:{imputamount}\n",color=0xFF0000)
                        await kankinchannel.send(embed = sales_log_embed)
                        flag = 1
                    else:
                        await interaction.response.send_message('ごめんなさい。人数制限です。',ephemeral=True)
                        return

                    
                else:
                    interaction.response.send_message(f'金額がちゃいます', ephemeral=True)
                    return
        else:
            await interaction.response.send_message('入力された形式が違います https://pay.paypay.ne.jp/　、またはhttps://kyash.me/payments/で始まるリンクを貼ってください', ephemeral=True)
            return

        #await interaction.response.send_message(f"入力された値:\n{self.input1.label}: {self.input1.value}",ephemeral=True)

class NumberSelectionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="paypay→kyash", style=discord.ButtonStyle.blurple)
    async def number_one_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AmountInputModal("paypay→kyash"))

    @discord.ui.button(label="kyash→paypay", style=discord.ButtonStyle.blurple)
    async def number_two_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AmountInputModal("kyash→paypay"))

@bot.tree.command(name="kankinritu", description="換金率を設定するコマンド")
@commands.has_permissions(administrator=True)
@app_commands.describe(rate="換金率を入力してください")
async def kankinritu(interaction: discord.Interaction, rate: int):
    global kankin_rate
    paypay.alive()
    kankin_rate = rate
    await interaction.response.send_message(f"換金率を {rate}% に設定しました。", ephemeral=True)
@kankinritu.error
async def kankinritu_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.MissingPermissions):
        await interaction.response.send_message("⚠️ **管理者だけが実行できます！**", ephemeral=True)

@bot.tree.command(name="kankin", description="換金を開始するコマンド")
@commands.has_permissions(administrator=True)
async def kankin(interaction: discord.Interaction):
    paypay.alive()
    embed = discord.Embed(title="換金", description=f"換金率 {kankin_rate}%,最低金額{saitei}円", color=discord.Color.blue())
    view = KankinView()
    await interaction.response.send_message(embed=embed, view=view)
@kankin.error
async def kankin_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.MissingPermissions):
        await interaction.response.send_message("⚠️ **管理者だけが実行できます！**", ephemeral=True)

@bot.tree.command(name="saiteisetting", description="換金の最低金額を設定")
@commands.has_permissions(administrator=True)
@app_commands.describe(money="換金の最低金額を入力してください")
async def saiteisetting(interaction: discord.Interaction, money: int):
    paypay.alive()
    global saitei
    saitei = money
    await interaction.response.send_message(f"最低金額を {money}円に設定しました。", ephemeral=True)
@saiteisetting.error
async def saiteisettiing_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.MissingPermissions):
        await interaction.response.send_message("⚠️ **管理者だけが実行できます！**", ephemeral=True)

        
@bot.tree.command(name="token", description="トークンをリフレッシュ")
@commands.has_permissions(administrator=True)
async def token(interaction: discord.Interaction):
    await interaction.response.defer()
    global りふれっしゅとーくん,あくせすとーくん
    try:
        paypay.token_refresh(りふれっしゅとーくん)
        あくせすとーくん = paypay.access_token
        りふれっしゅとーくん = paypay.refresh_token
        await interaction.followup.send(f'トークンをリフレッシュ成功！', ephemeral=True)
    except:
        await interaction.followup.send(f'なぜか失敗', ephemeral=True)
    
    
    #with open("token.txt", "w", encoding="utf-8") as file:
    	#file.write(aaaaaaa
@token.error
async def token_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.MissingPermissions):
        await interaction.response.send_message("⚠️ **管理者だけが実行できます！**", ephemeral=True)
    
@bot.event
async def on_ready():
    print(f"{bot.user} でログインしました！")
    await bot.tree.sync()
@bot.event
async def on_guild_join(guild):
    allowed_guild_id = 1096651765681750056  # 許可するサーバーのIDを入れてね！
    allowed_guild_id2 = 1348083101087039641

    if guild.id != allowed_guild_id and guild.id != allowed_guild_id2:
        await guild.leave()  # 指定外のサーバーなら抜ける
        print(f"⚠️ 許可されていないサーバー {guild.name} ({guild.id}) から退出しました。")
@bot.event
async def on_command_error(ctx, error):
    embed = discord.Embed(title="エラーが発生しました！", description=f"```{error}```", color=discord.Color.red())
    await ctx.send(embed=embed)
# Botのトークンを設定
bot.run(TOKEN)
