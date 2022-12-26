import nextcord as discord
from nextcord.ui import Button, View
from types import FunctionType

class AchievementsView(View):
    def __init__(self, default_embed: discord.Embed):
        super().__init__(timeout=180)
        self.default_embed = default_embed
        
        self.all_achs_button = Button(label="View all achievements", style=discord.ButtonStyle.primary, custom_id="achs")

    async def init(self, message: discord.Message, button_callback: FunctionType):
        self.message = message
        self.all_achs_button.callback = button_callback
        self.add_item(self.all_achs_button)
        await self.message.edit(content="", view=self, embed=self.default_embed)

    async def on_timeout(self):
        await self.message.edit(view=self)