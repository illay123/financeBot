import "chatBotInfrastructure.py"
#***********************************************main***********************************************#
if __name__ == '__main__':
    if '--debug' in sys.argv:
        print("[INFO] - debug mode")
        DEBUG = True
        print('Number of arguments:', len(sys.argv), 'arguments.')
        print('Argument List:', sys.argv)
    if "start" in sys.argv:
        print("[INFO] - starting the bot")
        BOT = Bot(TOKEN, URL)
        BOT.start()
    elif "test" in sys.argv:
        print("[INFO] - starting tests, the bot will shout down automaticlly after")
        # unittest.main()
        print(stripParameters("--a 2019-08-18 --d bla --p chop --c boom trach"))
    else:
        print("[USAGE] Chat.py start/test [--debug]")