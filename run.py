import sys
reload(sys)
sys.setdefaultencoding("ISO-8859-1")

from slackbot.bot import Bot

def main():
    bot = Bot()
    bot.run()

if __name__ == "__main__":
    main()
