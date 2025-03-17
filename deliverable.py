import discord
import re
from datetime import datetime
from config import Config as conf

class Deliverable:

    @staticmethod
    def get_alert_embed(model: str, img: str, url: str, price: float, location: str, quantity: int):
        quantity = f"{quantity}+" if quantity == 10 else quantity
        description = f"**Canada Computers**\n:bell: **Stock Alert!** `{model}` is now available at **{location}**!\n\
            **Quantity:** {quantity}\n\
            **Price:** ${price:.2f}\n\
            **Checked on:** {datetime.now().strftime("%Y-%m-%d %H:%M")} EST"
        embed = discord.Embed(colour=discord.Colour.red(),
                    description=description,
                    title=model,
                    url=url)
        embed.set_thumbnail(url=img) 
        return embed

    @staticmethod
    def get_instock_embed(data: dict, last_checked):
        description = f"Accurate as of: {last_checked} EST\n"

        # Splits description into chunks if it exceeds Discord's embed character limit of 4096
        descriptions = []
        embeds = []
        for location, stock_info in data.items():

            if len(description + f"{location}\n") >= 4090:
                descriptions.append(description)
                description = f"Accurate as of: {last_checked} EST\n"
            description += f"{location}\n"

            for model, info in stock_info.items():
                quantity = info[0]
                url = info[1]
                # Shorten model name to save character space
                truncated_model = re.sub(conf.truncate_patterns, '', model, flags=re.IGNORECASE)
                truncated_model = re.sub(r"\s+", " ", truncated_model).strip()

                if len(description + f"{quantity} [{truncated_model}]({url})\n") >= 4090:
                    descriptions.append(description)
                    description = f"Accurate as of: {last_checked} EST\n"
                    description += f"{location}\n"

                description += f"{quantity} - [{truncated_model}]({url})\n"

            if len(description + "\n") >= 4090:
                descriptions.append(description)
                description = f"Accurate as of: {last_checked} EST\n"
            description += "\n"
        descriptions.append(description)

        # Create the embeds based on the descriptions
        for i, d in enumerate(descriptions):
            embeds.append(discord.Embed(colour=discord.Colour.red(),
                    description=d,
                    title=f"Current availability ({i+1}/{len(descriptions)})"))
        
        return embeds
    
    @staticmethod
    def format_instock_data(data):
        '''
        Formats in-stock data such that it's easier to create the embed
        Format: {location: {model: [quantity, url]}}
        '''
        new = {}
        for d in data:
            location = d[0]
            model = d[1]
            url = d[2]
            quantity = d[3]
            new.setdefault(location, {})
            new[location].setdefault(model, [quantity, url])

        return new