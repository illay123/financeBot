"""running the chat bot script on the Infrastructure,
 actually just getting and parsing the command line arguments """
#**********************************************import*********************************************#
import sys
import logging
import argparse
import chatBotScript
from chatBotInfrastructure import Bot
#*************************************************************************************************#
TOKEN = "660462542:AAFGXJ3D8iYC3Sai8Grouysz2TIdya-9fL8" #get rid of this
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
#***********************************************main**********************************************#

def setParser():
    """defining the parse behaviour from the command line"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-D", "--dev", help="using or setting the development database",
                    action="store_true")
    parser.add_argument("-d", "--debug", help="show debugging data when running",
                    action="store_true")
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
    parser.add_argument("mode", help="operation mode of the server", 
                    choices=["start", "test", "init"])
    parser.add_argument("-c", "--config", help="path to .config file, can be done by dragging")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = setParser()
    if args.debug:
        logging.debug("debug mode began")
        logging.info('Number of arguments: {} arguments.'.format(len(sys.argv)))
        logging.info('Argument List: {}'.format(sys.argv))
    if args.mode == "start":
        logging.info("starting the bot")
        BOT = Bot(TOKEN, URL, chatBotScript.STARTSTATE)
        BOT.start()
    elif args.mode == "test":
        logging.info("starting tests, the bot will shout down automaticlly after")
        # unittest.main()
