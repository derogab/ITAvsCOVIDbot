import os
import logging
import imgkit
import secrets
import schedule
import time
from dotenv import load_dotenv
from telegram import InputMediaPhoto
from telegram.ext import Updater
from telegram.ext import CommandHandler
from pymongo import MongoClient

import io
from datetime import datetime as dt, timedelta as td

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

import warnings


# Constants
DATA_URL = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini" \
           "-summary-latest.csv"
ITALIAN_POPULATION = 60_360_000
HIT = ITALIAN_POPULATION / 100 * 80  # We need 80% of population vaccined for herd immunity

# Exclude warnings
warnings.filterwarnings("ignore")

# Init environment variables
load_dotenv()

# Init logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Get telegram token
telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
# Check telegram token
if telegram_bot_token is None:
    print('No telegram token.')
    exit()
# Init telegram bot    
updater = Updater(token=telegram_bot_token, use_context=True)

# Get mongodb auth
mongodb_user = os.environ.get('MONGODB_USER')
mongodb_pass = os.environ.get('MONGODB_PASS')
# Check mongodb auth
if mongodb_user is None or mongodb_pass is None:
    print('No mongodb auth.')
    exit()
mongodb_uri  = 'mongodb://' + mongodb_user + ':' + mongodb_pass + '@db:27017'
# Init mongodb database
client = MongoClient(mongodb_uri)

# Get bot database
db = client['bot']



# Function to generate images from templates
def generate(df, target, template):

    # Get data from df
    totalVaccines = sum(df[target])
    lastWeekData = df.loc[df.index > df.index[-1] - td(days=7)]
    vaccinesPerDayAverage = sum(lastWeekData[target]) / 7
    remainingDays = (HIT - totalVaccines) / vaccinesPerDayAverage
    hitDate = df.index[-1] + td(days=remainingDays)
    first_or_second = 'Seconda Dose' if target == 'seconda_dose' else 'Prima Dose' if target == 'prima_dose' else 'Totale'

    # Generate plot
    plt.ylabel(first_or_second)
    plt.xlabel("Ultima settimana")
    plt.grid(True)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gcf().autofmt_xdate()
    plt.bar(lastWeekData.index, height=lastWeekData[target])
    # Trendline
    z = np.polyfit(range(0, 7), lastWeekData[target], 2)
    p = np.poly1d(z)
    plt.plot(lastWeekData.index, p(range(0, 7)), "r--")
    # Secret 4 filenames
    sf = secrets.token_hex(16)
    # Generate plot filename
    plot_filename = 'plot_' + sf + '.png'
    # Create plot image/png
    plt.savefig('out/' + plot_filename, dpi=300, bbox_inches='tight')
    # Flush the plot
    plt.clf()
    # Generate tmp webpage/html filename
    webpage_filename = 'tmp_' + sf + '.html'
    # Generate template
    with open(template, 'r+') as f:
        with open('out/' + webpage_filename, 'w+') as wf:
            for line in f.read().splitlines():
                if "<!-- totalVaccinations -->" in line:
                    line = f"{totalVaccines}"
                elif "<!-- typeVaccinations -->" in line:
                    line = f"{first_or_second}"
                elif "<!-- totalVaccinationsPerc -->" in line:
                    line = f"{str(round(totalVaccines / ITALIAN_POPULATION * 100, 2)).replace('.', ',')}%"
                elif "<!-- totalVaccinationsLastWeek -->" in line:
                    line = f"{int(vaccinesPerDayAverage*7)}"
                elif "<!-- vaccinesPerDay -->" in line:
                    line = f"{int(vaccinesPerDayAverage)}"
                elif "<!-- hitDate -->" in line:
                    line = f"{hitDate.strftime('%d/%m/%Y')}"
                elif "<!-- hitHour -->" in line:
                    line = f"{hitDate.strftime('%H:%M:%S')}"
                elif "<!-- daysRemaining -->" in line:
                    line = f"{int(remainingDays)}"
                elif "plot.png" in line:
                    line = line.replace('plot.png', plot_filename)
                wf.write("\n" + line)
    # Generate plot filename
    results_filename = 'results_' + sf + '.png'
    # Create results image/png
    imgkit.from_file('out/' + webpage_filename, 'out/' + results_filename)

    # Return out data
    return {
        'plot': 'out/' + plot_filename,
        'results': 'out/' + results_filename,
        'webpage': 'out/' + webpage_filename
    }



# Function to get data
def download():

    # Download from open data
    r = requests.get(DATA_URL)
    # Create dataframe from data
    df = pd.read_csv(
        io.StringIO(r.text),
        index_col="data_somministrazione",
    )
    # Set date as index 
    df.index = pd.to_datetime(
        df.index,
        format="%Y-%m-%d",
    )
    # Sort value based on date
    df.sort_values('data_somministrazione')
    # Delete sum data if already exists
    df = df[df["area"] != "ITA"]
    # Set target counters to numeric
    df["prima_dose"] = pd.to_numeric(df["prima_dose"])
    df["seconda_dose"] = pd.to_numeric(df["seconda_dose"])
    # Group by day and sum counters
    df_first = df.groupby(['data_somministrazione'])['prima_dose'].sum().reset_index()
    df_second = df.groupby(['data_somministrazione'])['seconda_dose'].sum().reset_index()
    # Re-set date as ID in new dataframe
    df_first = df_first.set_index('data_somministrazione')
    df_second = df_second.set_index('data_somministrazione')
    
    # If there are current day data...
    if dt.now() - df_first.index[-1] < td(days=1):
        df_first = df_first[:-1]  # Ignore the current day because it's often incomplete
    if dt.now() - df_second.index[-1] < td(days=1):
        df_second = df_second[:-1]  # Ignore the current day because it's often incomplete

    # Generata images
    intro = generate(df_second, 'seconda_dose', 'assets/templates/intro.html')
    plot1 = generate(df_first, 'prima_dose', 'assets/templates/plot.html')
    plot2 = generate(df_second, 'seconda_dose', 'assets/templates/plot.html')

    return intro, plot1, plot2



# Help command
def help(update, context):

    # Help msg
    help_msg  = "_Lista dei comandi_ \n\n"
    help_msg += "/start - Avvia il bot \n"
    help_msg += "/get - Ricevi i dati aggiornati \n"
    help_msg += "/news ON/OFF - Attiva o Disattiva le notifiche giornaliere \n"
    help_msg += "/help - Messaggio di aiuto \n"
    help_msg += "/info - Informazioni su questo bot \n"
    help_msg += "/stop - Disattiva il bot \n"

    # Send welcome message
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_msg, parse_mode='Markdown')



# Info command
def info(update, context):

    # Info msg
    info_msg  = "_Informazioni utili sul bot_\n\n"
    info_msg += "Il bot è stato sviluppato da @derogab e il [codice sorgente](https://github.com/derogab/ITAvsCOVIDbot) è pubblicamente disponibile su Github. \n\n"
    info_msg += "I dati mostrati sono scaricati dagli [Open Data ufficiali](https://github.com/italia/covid19-opendata-vaccini) sui vaccini in Italia. \n\n"
    info_msg += "I grafici sono automaticamente generati mediante il codice della [repository pubblica](https://github.com/MarcoBuster/quanto-manca) di @MarcoBuster. \n\n"
    
    # Send welcome message
    context.bot.send_message(chat_id=update.effective_chat.id, text=info_msg, parse_mode='Markdown', disable_web_page_preview=True)



# Start command
def start(update, context):
    global db

    # Insert user to db
    myquery = {
        "_id": update.effective_chat.id
    }
    newvalues = {
        "$set": { 
            "_id": update.effective_chat.id,
            "username": update.effective_chat.username,
            "first_name": update.effective_chat.first_name,
            "last_name": update.effective_chat.last_name,
            "active": True,
            "news": True
        }
    }
    db.users.update_one(myquery, newvalues, upsert=True)

    # welcome msg
    welcome_msg  = "Benvenuto su 🇮🇹 *ITA vs. COVID* 🦠 !\n\n"
    welcome_msg += "Il bot che ti aggiorna sulla battaglia contro il Covid in Italia."

    # Send welcome message
    context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_msg, parse_mode='Markdown')
    # Send help message
    help(update, context)
    # Send help message
    info(update, context)



# Stop command
def stop(update, context):
    global db

    # Set active = false on db
    myquery = {
        "_id": update.effective_chat.id
    }
    newvalues = {
        "$set": { 
            "active": False
        }
    }
    db.users.update_one(myquery, newvalues, upsert=True)

    # stop msg
    stop_msg  = "Il bot è stato spento.\n\n"
    stop_msg += "Quando vorrai riavviarlo ti basterà cliccare su /start"

    # Send welcome message
    context.bot.send_message(chat_id=update.effective_chat.id, text=stop_msg, parse_mode='Markdown')



# News command
def news(update, context):
    global db

    msg = update.message.text
    news = msg.replace('/news', '').strip().lower()

    if news == "on":
        to_set = True
        set_msg  = "Le notifiche giornaliere sono state correttamente abiitate.\n\n"
        set_msg += "Riceverai i dati sul progresso della battaglia contro il Covid in Italia ogni giorno alle 18:00."
    
    elif news == "off":
        to_set = False
        set_msg = "Le notifiche giornaliere sono state correttamente disabilitate."
    
    else:
        # Invalid param msg
        invalid_param_msg  = "Il parametro inserito è errato. \n\n"
        invalid_param_msg += "/news ON - Per attivare le notifiche giornaliere\n"
        invalid_param_msg += "/news OFF - Per disattivare le notifiche giornaliere\n\n"
        # Send message
        context.bot.send_message(chat_id=update.effective_chat.id, text=invalid_param_msg, parse_mode='Markdown')
        # Exit
        return

    # Set news on db
    myquery = {
        "_id": update.effective_chat.id
    }
    newvalues = {
        "$set": { 
            "news": to_set
        }
    }
    db.users.update_one(myquery, newvalues, upsert=True)

    # Send welcome message
    context.bot.send_message(chat_id=update.effective_chat.id, text=set_msg, parse_mode='Markdown')



# Get data
def get(update, context):

    # Download data
    intro, plot1, plot2 = download()
    
    # Send photos
    p1 = open(intro['results'], 'rb')
    p2 = open(plot1['results'], 'rb')
    p3 = open(plot2['results'], 'rb')

    p1 = InputMediaPhoto(media=p1)
    p2 = InputMediaPhoto(media=p2)
    p3 = InputMediaPhoto(media=p3)

    context.bot.send_media_group(chat_id=update.effective_chat.id, media=[p1, p2, p3])

    # Remove tmp files
    for data in [intro, plot1, plot2]:
        os.remove(data['plot'])
        os.remove(data['webpage'])
        os.remove(data['results'])
    


# Cron job
def job():
    global db
    
    # Job running...
    print('Job running...')

    # Download data
    data = download()
    
    # Get active user with daily news
    users = db.users.find({
        "active": True,
        "news": True
    })

    # Counters
    news_sent_counter = 0
    news_fail_counter = 0
    # Send news to all active user 
    for user in users:
        
        try:
            # Send photo
            updater.bot.send_photo(chat_id=user['_id'], photo=open(data['results'], 'rb'), caption="")
            # Count news successfully sent
            news_sent_counter = news_sent_counter + 1
            # Log
            print('[JOB] Message successfully sent to ', user['_id'])
        except: 
            # Count news fail
            news_fail_counter = news_fail_counter + 1
            # Error on sending
            print('[JOB] Failed to send to ', user['_id'])

    # Log results
    print("[JOB] Results: {sent} messages sent, {fail} messages failed.".format(sent=news_sent_counter, fail=news_fail_counter))

    # Remove tmp files
    os.remove(data['plot'])
    os.remove(data['webpage'])
    os.remove(data['results'])
    




# Telegram dispatcher
dispatcher = updater.dispatcher

# Add /help command
start_handler = CommandHandler('help', help)
dispatcher.add_handler(start_handler)
# Add /info command
start_handler = CommandHandler('info', info)
dispatcher.add_handler(start_handler)
# Add /start command
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
# Add /stop command
start_handler = CommandHandler('stop', stop)
dispatcher.add_handler(start_handler)
# Add /get command
start_handler = CommandHandler('get', get)
dispatcher.add_handler(start_handler)
# Add /news command
start_handler = CommandHandler('news', news)
dispatcher.add_handler(start_handler)

# Setup cron
schedule.every().day.at("18:00").do(job)

# Start bot
updater.start_polling()

# Run schedule and check bot
while True:
    
    if not updater.running:
        # Bot is down.
        exit() # and auto restart

    schedule.run_pending()
    time.sleep(1)
