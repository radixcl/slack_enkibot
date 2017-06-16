#!/usr/bin/env python
# -*- coding: utf8 -*-

from slackbot import settings
from slackbot.bot import respond_to
from slackbot.bot import listen_to

import re
import time

from google import google

import sqlite3
conn = sqlite3.connect('./enkibot/zlearn.db', check_same_thread=False)
conn.row_factory = sqlite3.Row
conn.text_factory = str

def getzlearn(definition):
    c = conn.cursor()
    t = (definition, )
    c.execute('SELECT * FROM defs WHERE UPPER(k)=UPPER(?)', t)
    data = c.fetchone()
    return data

def getusername(message):
    userid = message._get_user_id()
    users = message._client.users
    return next(v['name'] for k, v in users.items() if k == userid)

def newkey(key, definition, username):
    timestamp = int(time.time())
    c = conn.cursor()
    t = (key, timestamp, username, '', definition)
    c.execute("INSERT INTO defs ('k', 'c', 'a', 'f', 'd') VALUES (?, ?, ?, ?, ?)", t);
    conn.commit()

def delkey(key):
    c = conn.cursor()
    t = (key, )
    c.execute("DELETE FROM defs WHERE k = ?", t)
    conn.commit()

@respond_to('^\?\? (.*)')
@listen_to('^\?\? (.*)')
def getdefinition(message, str):

    d = str.split(' ');
    key = d[0]

    if d[0] == '-a':
        verbose = 1
        key = d[1]
    else:
        verbose = 0
        key = d[0]

    data = getzlearn(key)
    if type(data) is sqlite3.Row:
        definition = data[4].encode('utf-8').strip()
        #replacements
        definition = definition.replace('%n', getusername(message))
        definition = definition.replace('*', '*­')
        message.send('*%s* == %s' % (key, definition))

        if verbose == 1:
            message.send('(author: %s) (%s)' % (data[2], time.ctime(int(data[1]))))

        else:
            message.send('Entry *%s* not found.' % (key))

@respond_to('^\!learn (.*)')
@listen_to('^\!learn (.*)')
def learndefinition(message, str):
    user = getusername(message)
    if not user in settings.ADMINS:
        #print "nope"
        return

    d = str.split(' ');

    if len(d) < 2:
        message.send('Cannot learn blank entry')
        return

    if d[0] == '-f':
        overwrite = 1
        key = d[1]
        defs = ' '.join(d[2:])
    else:
        overwrite = 0
        key = d[0]
        defs = ' '.join(d[1:])

    if defs == '':
        message.send('Cannot learn blank entry')
        return

    # check if already exists
    data = getzlearn(key)
    if type(data) is sqlite3.Row:
        if overwrite == 0:
            message.send('Key *%s* already exists' % (key))
            return
        else:
            delkey(key)

    newkey(key, defs, '%s(Slack)' % user)
    message.send('Learned *%s*.' % key)

@respond_to('^\!forget (.*)')
@listen_to('^\!forget (.*)')
def learndefinition(message, str):
    user = getusername(message)
    if not user in settings.ADMINS:
        #print "nope"
        return

    d = str.split(' ');
    key = d[0]
    defs = ' '.join(d[1:])

    # check if already exists
    data = getzlearn(key)
    if type(data) is not sqlite3.Row:
        message.send('Key *%s* does not exist.' % (key))
        return

    delkey(key)
    message.send('Removed *%s*.' % (key))

@respond_to('^\!find (.*)')
@listen_to('^\!find (.*)')
def finddefinition(message, str):
    d = str.split(' ');
    key = d[0]
    key = key.replace('*', '%')

    c = conn.cursor()
    t = (key, )
    c.execute('SELECT k FROM defs WHERE d like ?', t)
    data = c.fetchall()
    l = len(data)
    message.send('Matched %s keys' % l)
    if l > 0:
        message.send( ', '.join(e[0].decode('ISO-8859-1').encode('utf8') for e in data) )

@respond_to('^\!listkeys (.*)')
@listen_to('^\!listkeys (.*)')
def finddefinition(message, str):
    d = str.split(' ');
    key = d[0]
    key = key.replace('*', '%')

    c = conn.cursor()
    t = (key, )
    c.execute('SELECT k FROM defs WHERE k like ?', t)
    data = c.fetchall()
    l = len(data)
    message.send('Matched %s keys' % l)
    if l > 0:
        message.send( ', '.join(e[0] for e in data) )

@respond_to('^\!google (.*)')
@listen_to('^\!google (.*)')
def googlesearch(message, str):
    #message.send('google %s' % str)
    res = google.search(str, 1)

    if len(res) < 1:
        message.send('Google returned no results.')
    else:
        message.send('%s' % (res[0].link))
