from config import TRAIN_NETWORK, VISUALIZE, STOCKS, ITERATION
from datahandler.stock import StockDataHandler
from network.LSTMNetwork import LSTMNetwork
from utils import get_datasets
from csv import writer
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime, timedelta

pourcent1 = 0
pourcent2 = 0
pourcent3 = 0
iGlobal = 1
prixDay = 0
prixFourHour = 0
prixOneHour = 0


def get_predictions(stock, end, inte):
    datasets = get_datasets([stock], end, inte)
    ret_data = []
    for i, data in enumerate(datasets):
        data_handler = StockDataHandler()
        data_handler.add(data, stock)
        lstm_network = LSTMNetwork(data_handler)

        predictions = lstm_network.run_model(
        weight_filename='stock_{0}_weights.h5'.format(stock.split('/')[-1]), train=TRAIN_NETWORK,
        evaluate=True, visualize=VISUALIZE)

        global iGlobal
        globals()["pourcent"+str(iGlobal)] = vars(lstm_network)['pourcent']
        iGlobal = iGlobal+1
        ret_data.append(predictions)
    return ret_data

TOKEN = '5433248059:AAFE7tHfS10z7ojEo4lU_A4XWG1xPALzICQ'


def start(update, context):
    

    update.message.reply_text("""
Bienvenue sur le bot officiel de Bramso.

Les commandes disponibles sont :
- /AAPL pour obtenir la prédiction du prix et du pourcentage de l'action apple.
- /TSLA pour obtenir la prédiction du prix et du pourcentage de l'action tesla.

    """)


def get_yesterday():
    today = datetime. today()
    yesterday = today - timedelta(days=1)
    d4 = today.strftime("%Y-%m-%d")
    return d4

def get_today():
    today = datetime.today()
    return today.strftime("%Y-%m-%d")

def get_hour():
    now = datetime.now()
    return str(now.hour)

def get_aapl(update, context):
    global prixDay
    global prixOneHour
    global iGlobal
    iGlobal=1
    prixDay = get_predictions("EOD/AAPL", get_yesterday(), "1d")[0][0][0]
    
    prixOneHour = get_predictions("EOD/AAPL", get_today(), "1h")[0][0][0]
    update.message.reply_text("""

Les commandes disponibles sont :
- /prix pour obtenir la prédiction du prix.
- /pourcent pour obtenir la prédiction du pourcentage.

    """)

def get_tsla(update, context):
    global prixDay
    global prixOneHour
    global iGlobal
    iGlobal=1
    prixDay = get_predictions("EOD/TSLA", get_yesterday(), "1d")[0][0][0]

    prixOneHour = get_predictions("EOD/TSLA", get_today(), "1h")[0][0][0]
    update.message.reply_text("""

Les commandes disponibles sont :
- /prix pour obtenir la prédiction du prix.
- /pourcent pour obtenir la prédiction du pourcentage.

    """)

def prix(update, context):

    update.message.reply_text("Prediction du prix "+get_today()+"(1jour): "+str(prixDay)+" USD")
    update.message.reply_text("Prediction du prix "+get_hour()+"(1h): "+str(prixOneHour)+" USD")
    update.message.reply_text("""
    Retour vers le menu principal : /start
    """)


def pourcent(update, context):
    update.message.reply_text("Prediction du pourcentage "+get_today()+"(1jour) : "+str(pourcent1)+" %")
    update.message.reply_text("Prediction du pourcentage "+get_hour()+"(1h): "+str(pourcent2)+" %")
    update.message.reply_text("""
    Retour vers le menu principal : /start
    """)


def pas_compris(update, context):
    update.message.reply_text('Je n\'ai pas compris votre message'+update.message.text)
    update.message.reply_text("""
    Retour vers le menu principal : /start
    """)

if __name__ == "__main__":
    print("Prediction du prix :",prixDay)
    updater = Updater(TOKEN, use_context=True)

    # Pour avoir accès au dispatcher plus facilement
    dp = updater.dispatcher

    # On ajoute des gestionnaires de commandes
    # On donne a CommandHandler la commande textuelle et une fonction associée
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("TSLA", get_tsla))
    dp.add_handler(CommandHandler("AAPL", get_aapl))
    dp.add_handler(CommandHandler("prix", prix))
    dp.add_handler(CommandHandler("pourcent", pourcent))


    # Pour gérer les autres messages qui ne sont pas des commandes
    dp.add_handler(MessageHandler(Filters.text, pas_compris))

    # Sert à lancer le bot
    updater.start_polling()

    # Pour arrêter le bot proprement avec CTRL+C
    updater.idle()
