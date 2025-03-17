import discord, os, asyncio, aiohttp
from scraper import *
from discord.ext import tasks
from datetime import datetime
from db import DB
from static_strings import *
from charts import Chart
from dotenv import load_dotenv
from config import Config as conf
from utils import fetch, shorten_url
from deliverable import Deliverable as dlvr

last_checked = datetime.now().strftime("%Y-%m-%d %H:%M")

def run_discord_bot():
    client = discord.Client(intents=discord.Intents.all())

    @tasks.loop()
    async def check_stock():
        global last_checked
        log_channel = client.get_channel(conf.log_channel_id)

        while True:
            async with aiohttp.ClientSession() as session:

                # Retreive GPU data that are being tracked
                items_query = DB.get_query("SELECT * FROM products")
                urls = [url[3] for url in items_query]
                responses = await asyncio.gather(*(fetch(url, session) for url in urls))

                for i, item in enumerate(items_query):
                    response = responses[i][0]
                    status = responses[i][1]
                    model_id, model, gpu, url = item[0], item[1], item[2], item[3]
                    data, status = await Scraper.update(response, status)

                    # Reports any links with bad responses
                    if status:
                        await log_channel.send(f'Item with the link {url} has {status}')

                    if not data:
                        continue

                    # Checks stock quantity for each CC location, one SKU at a time
                    for location, quantity in data['availability'].items():
                        notified_quantity = DB.get_query(f"SELECT quantity FROM in_stock WHERE model_id={model_id} AND region='{location}'")[0][0]

                        # Pings alert channel only if stock quantity goes up
                        if quantity > notified_quantity:
                            channel = client.get_channel(conf.alert_channel_id[gpu])
                            role = channel.guild.get_role(conf.cc_roles[location])

                            new_quantity = quantity - notified_quantity
                            embed = dlvr.get_alert_embed(model, data['img'], url, data['price'], location, new_quantity)

                            await channel.send(content=f'{role.mention}', embed=embed)

                            # Add this restock into DB
                            new_data = (model_id, location, new_quantity, data['price'], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            insert_stmt = ("INSERT INTO stock_data (model_id, region, quantity, price, timestamp) "
                                        "VALUES (?, ?, ?, ?, ?)")
                            DB.insert(insert_stmt, new_data)
                            
                        # Pings spam channel if in stock
                        if quantity > 0 and gpu in conf.spam_channel_id:
                            channel = client.get_channel(conf.spam_channel_id[gpu])
                            embed = dlvr.get_alert_embed(model, data['img'], url, data['price'], location, quantity)
                            await channel.send(embed=embed)
                        
                        # Update in_stock table with latest quantities
                        updated_quantity = (quantity, model_id, location)
                        update_stmt = "UPDATE in_stock SET quantity = ? WHERE model_id = ? AND region = ?"
                        DB.update(update_stmt, updated_quantity)

            await log_channel.send(f'Task successfully ran at: {datetime.now().strftime("%H:%M:%S")} EST')
            last_checked = datetime.now().strftime("%Y-%m-%d %H:%M")
            await asyncio.sleep(150)
                    
    @client.event
    async def on_ready():
        print("We have logged in as {0.user}".format(client))
        channel = client.get_channel(conf.command_channel_id)
        log_channel = client.get_channel(conf.log_channel_id)

        await channel.send("I'm back online")
        await log_channel.send("Online")

        if not any(task.get_name() == "stock_checker" for task in asyncio.all_tasks()):
            task = client.loop.create_task(check_stock())
            task.set_name("stock_checker")

    @client.event
    async def on_message(message):
        user_message = str(message.content).strip()
        channel = client.get_channel(conf.command_channel_id)
        user_id = message.author.id

        if message.author == client.user or message.channel != channel:
            return

        if re.search('!locations', user_message, re.IGNORECASE):
            # Sends a list of all CC locations

            stmt = "SELECT region AS location FROM locations"
            table = DB.get_query_table(stmt)
            await channel.send(table)

        if re.search('!help', user_message, re.IGNORECASE):
            # Sends a list of all commands and how to use them

            await channel.send(help)

        if re.search('!chart', user_message, re.IGNORECASE):
            # Sends historical stock data as a chart.

            m = user_message.replace("!chart", "").strip()
            m = re.sub(r"\s*=\s*", "=", m).split(',')

            # Extract filters inputted by user
            locations, gpus = [], []
            for x in m:
                filter = [y.strip() for y in x.split('=')]

                if re.search('location', filter[0], re.IGNORECASE) and len(filter) == 2:
                    params = filter[1].split("/")
                    for param in params:
                        locations.append(param.strip().title())

                elif re.search('gpu', filter[0], re.IGNORECASE) and len(filter) == 2:
                    params = filter[1].split("/")

                    for param in params:
                        gpu = param.title().strip() if not 'xt' in param.lower() else param.upper().strip()
                        gpu = re.sub(r"(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])", " ", gpu)
                        gpus.append(gpu)

            # Construct SQL statement based on filters
            stmt = f"SELECT products.gpu, sum(stock_data.quantity), strftime('%Y-%m-%d', stock_data.timestamp) AS day \
                     FROM stock_data LEFT JOIN products ON products.id=stock_data.model_id "
            
            if locations:
                stmt += "WHERE "
                for i, location in enumerate(locations):
                    if i == 0:
                        stmt += f"(stock_data.region='{location}' "
                    else:
                        stmt += f"OR stock_data.region='{location}' "
                stmt += ") "

            if gpus:
                for i, gpu in enumerate(gpus):
                    if i == 0 and not locations:
                        stmt += f"WHERE (products.gpu='{gpu}' "
                    elif i == 0:
                        stmt += f"AND (products.gpu='{gpu}' "
                    else:
                        stmt += f"OR products.gpu='{gpu}' "
                stmt += ") "
            stmt += "GROUP BY products.gpu, day \
                     ORDER BY day ASC "
            
            # If there are no GPU filters, then just get all distinct GPUs (need this for chart config)
            if not gpus:
                gpus = DB.get_query("SELECT DISTINCT(gpu) from products")
                gpus = [gpu[0] for gpu in gpus]          

            data = DB.get_query(stmt)
            chart_config = Chart.create_chart_config(data, locations, gpus)
            url = Chart.get_bar_chart_url(chart_config)
            if url:
                short, status = await shorten_url(url)
                if short:
                    await channel.send(short)
                else:
                    await channel.send(f"```{status}```")
            else:
                await channel.send('```No data available```')

        if re.search(r"!(?:a|n)chart", user_message, re.IGNORECASE):
            # Sends historical stock data as a chart for a particular brand

            brand = "AMD" if re.search(r"!achart", user_message, re.IGNORECASE) else "NVIDIA"

            # Extract location filter, if any
            location = user_message.lower().replace("!achart", "").replace("!nchart", "").strip()
            location = location.title() if location else None

            # Construct SQL statement based on filter
            stmt = f"SELECT products.gpu, sum(stock_data.quantity), strftime('%Y-%m-%d', stock_data.timestamp) AS day \
                     FROM stock_data LEFT JOIN products ON products.id=stock_data.model_id WHERE products.brand='{brand}' "
            stmt += f"AND stock_data.region='{location}' " if location else ''
            stmt += "GROUP BY products.gpu, day \
                     ORDER BY day ASC "
            
            # Get list of distinct GPUs (need this for chart config)
            gpus = DB.get_query(f"SELECT DISTINCT(gpu) FROM products WHERE brand='{brand}'")
            gpus = [gpu[0] for gpu in gpus]
                
            data = DB.get_query(stmt)
            chart_config = Chart.create_chart_config(data, [location], gpus, brand)
            url = Chart.get_bar_chart_url(chart_config)
            if url:
                short, status = await shorten_url(url)
                if short:
                    await channel.send(short)
                else:
                    await channel.send(f"```{status}```")
            else:
                await channel.send('```No data available```')

        if re.search('!hour', user_message, re.IGNORECASE):
            # Sends all-time hourly stock scan distribution as a chart

            # Extract location filter, if any
            location = user_message.replace("!hour", "").strip().lower()
            location = location.title() if location else None

            # Construct SQL statement based on filter
            stmt = "SELECT CASE \
                    WHEN locations.timezone='PST' THEN strftime('%H', datetime(timestamp, '-3 hour')) \
                    WHEN locations.timezone='PST' AND strftime('%H', timestamp)='3' THEN '00' \
                    WHEN locations.timezone='EST' AND strftime('%H', timestamp)='0' THEN '00' \
                    ELSE strftime('%H', timestamp) \
                    END \
                    as hour, \
                    sum(quantity) AS quantity \
                    FROM stock_data LEFT JOIN locations ON locations.region=stock_data.region "
            stmt += f"WHERE stock_data.region='{location}' " if location else ''
            stmt += "GROUP BY hour"

            data = DB.get_query(stmt)
            chart_config = Chart.create_hour_dist_chart_config(data, location)
            url = Chart.get_bar_chart_url(chart_config)
            if url:
                short, status = await shorten_url(url)
                if short:
                    await channel.send(short)
                else:
                    await channel.send(f"```{status}```")
            else:
                await channel.send('```No data available```')

        if re.search('!instock', user_message, re.IGNORECASE):
            # Sends a list of items that are currently in stock
            m = user_message.replace("!get", "").strip()
            m = re.sub(r"\s*=\s*", "=", m).split(',')

            # Extract filters
            location, gpu = None, None
            for x in m:
                filter = [y.strip() for y in x.split('=')]

                if re.search('location', filter[0], re.IGNORECASE) and len(filter) == 2:
                    location = filter[1].title()

                elif re.search('gpu', filter[0], re.IGNORECASE) and len(filter) == 2:
                    gpu = filter[1].title() if not 'xt' in filter[1].lower() else filter[1].upper()
                    gpu = re.sub(r"(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])", " ", gpu) # Adds space e.g. 5070Ti -> 5070 Ti

            # Construct SQL statement based on filters
            stmt = "SELECT region AS location, model, url, quantity FROM in_stock LEFT JOIN products ON products.id=in_stock.model_id WHERE in_stock.quantity>0 "
            stmt += f"AND products.gpu='{gpu}' " if gpu else ''
            stmt += f"AND in_stock.region='{location}' " if location else ''

            data = DB.get_query(stmt)
            data = dlvr.format_instock_data(data)
            embeds = dlvr.get_instock_embed(data, last_checked)
            for embed in embeds:
                await channel.send(embed=embed)

        if re.search('!rank', user_message, re.IGNORECASE):
            # Sends a rank of stores based on amount of stock received

            gpu = user_message.replace("!rank", "").strip().lower()
            gpu = gpu if gpu else None
            if gpu and re.search(r"[a-zA-Z]", gpu):
                gpu = re.sub(r"(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])", " ", gpu.title()) # Adds space e.g. 5070Ti -> 5070 Ti
                gpu = gpu.upper() if 'xt' in gpu.lower() else gpu

            # Construct SQL statement
            stmt = "SELECT stock_data.region as location, SUM(stock_data.quantity) as total FROM stock_data LEFT JOIN products ON products.id=stock_data.model_id "
            stmt += f"WHERE products.gpu='{gpu}' " if gpu else ""
            stmt += "GROUP BY region ORDER BY total DESC"

            table = DB.get_query_table(stmt)
            title = f"Total {gpu} stock received by store" if gpu else "Total stock received by store"
            embed = discord.Embed(colour=discord.Colour.red(),
                description=table,
                title=title)
            await channel.send(embed=embed)

        if re.search('!topsku', user_message, re.IGNORECASE):
            # Returns top SKUs of gpu

            gpu = user_message.replace("!topsku", "").strip().lower()
            gpu = gpu if gpu else None

            if gpu and re.search(r"[a-zA-Z]", gpu):
                gpu = re.sub(r"(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])", " ", gpu.title()) # Adds space e.g. 5070Ti -> 5070 Ti
                gpu = gpu.upper() if 'xt' in gpu.lower() else gpu

            # Construct SQL statement
            stmt = f"SELECT products.model, SUM(stock_data.quantity) AS total \
                    FROM stock_data \
                    LEFT JOIN products ON products.id=stock_data.model_id "
            stmt += f"WHERE products.gpu='{gpu}' " if gpu else ""
            stmt += "GROUP BY products.model \
                    ORDER BY total DESC"
            
            table = DB.get_top_sku_table(stmt)
            title = f"Top {gpu} SKUs" if gpu else "Top SKUs"
            embed = discord.Embed(colour=discord.Colour.red(),
                description=table,
                title=title)
            await channel.send(embed=embed)
        
        if re.search('!me', user_message, re.IGNORECASE):
            # Sends personalized in-stock table based on discord roles.

            stmt = "SELECT region AS location, model, url, quantity FROM in_stock LEFT JOIN products ON products.id=in_stock.model_id WHERE in_stock.quantity>0 "
            location_filters = []
            gpu_filters = []
            roles = [role.name for role in message.author.roles]

            # Every user has the @everyone role by default
            if len(roles) == 1:
                await channel.send("```You do not have any roles assigned. Please add roles or use !instock instead```")

            else:
                for role in roles:
                    if 'CC' in role:
                        location = role.replace("CC-", "")
                        location_filters.append(location)
                    elif 'Mute' in role:
                        gpu = role.replace("Mute ", "")
                        gpu_filters.append(gpu)
                
                if location_filters:
                    location_filter = "("
                    first = True
                    for l in location_filters:
                        location_filter += f"location='{l}' " if first else f"OR location='{l}' "
                        if first:
                            first = False
                    location_filter += ")"
                    stmt += f"AND {location_filter} "
                
                if gpu_filters:
                    gpu_filter = ""
                    first = True
                    for g in gpu_filters:
                        gpu_filter += f"gpu!='{g}' " if first else f"AND gpu!='{g}' "
                        if first:
                            first = False
                    stmt += f"AND {gpu_filter} "
                
                data = DB.get_query(stmt)
                data = dlvr.format_instock_data(data)
                embeds = dlvr.get_instock_embed(data, last_checked)
                for embed in embeds:
                    await channel.send(embed=embed)

        if re.search('!shutdown', user_message, re.IGNORECASE) and user_id == 228995300696522752:
            await channel.send("I go sleep <:isleep:1342714730074079232> Commands won't work until I'm back online")
            log_channel = client.get_channel(conf.log_channel_id)
            await log_channel.send("Offline")
            await client.close()


    load_dotenv()
    client.run(os.getenv('TOKEN'))


if __name__ == '__main__':
    pass