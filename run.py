#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from slackbot.bot import Bot

def main():
    bot = Bot()
    bot.run()

if __name__ == "__main__":
    main()
