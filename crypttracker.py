# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 09:59:53 2018

@author: lovenfreedom
"""
from exchanges import EXCHANGES
from beem.instance import set_shared_steem_instance
from discord.ext.commands import Bot
from discord import Webhook, RequestsWebhookAdapter, File
from beem import Steem, blockchain
from pprint import pprint
from beem.nodelist import NodeList
from lxml import html
import requests
import logging
import os
import datetime
import discord
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig()


# Constants - values that aren't supposed to change through the duration of the program
BOT_NAME = "Peruser"
BOT_PREFIX = ("?p", "!p")
BOT_DESC = "Crypto Transaction Tracker in Steemit"
TOKEN = ""  # Get at discordapp.com/developers/applications/me
INVITE_LINK = "https://discordapp.com/oauth2/authorize?client_id=473108742657933324&scope=bot&permissions=8"
BOT_GAME = "with anti-abuse specialists"  # game/status of the bot when booted up

## Create the bot with description and prefix to trigger commands, allow DM to the bot
cttBot = Bot(description=BOT_DESC, command_prefix=BOT_PREFIX, pm_help = True)

# Retrieve nodes from list. Invoking update_nodes() ensures only active nodes are used to connect to.
nodes = NodeList()
nodes.update_nodes()

# Create steem instance with functioning nodes. Enclose in try/except just in case.
stm = Steem()
try:
    stm = Steem(node=nodes.get_nodes())
except Exception as error:
    logger.error(error)
    logger.info(datetime.datetime.utcnow())
    
set_shared_steem_instance(stm)

blockChain = blockchain.Blockchain() ## mode=head for instant confirmation, irreversible for confirmed txns

## 1. provide account name and find transfers to exchanges
##   create a list of exchanges from penguinpablo's and lukestokes' list - done
##   calculating estimated block num by date is an option for longer date range 
##       but for quick and dirty calculation of start block we'll use a dandy formula
##   
## 2. provide wallet address and find other accounts using it
## 3. provide account name and find other accounts transferring to it


## get all transfers from steemit account's transfer page
def transfersAll(byAccount, hasMemo=True):   
    transferPage = "https://steemit.com/@{}/transfers".format(byAccount)
    page = requests.get(transferPage)
    tree = html.fromstring(page.content)
    
    if hasMemo:
        transfers = tree.xpath("//*[contains(text(),'Transfer')]/text()|//*[contains(text(),'Transfer')]/a/text()|//span[@class='Memo']/text()")
    else:
        transfers = tree.xpath("//*[contains(text(),'Transfer')]/text()|//*[contains(text(),'Transfer')]/a/text()")
     
    reformatTransfers = []
    oneTransfer = ""
     
    for eachTransfer in transfers:
        if "Transfer" in eachTransfer:
            if oneTransfer:
                reformatTransfers.append(oneTransfer)                     
                 ##print(oneTransfer)
                 
            oneTransfer = eachTransfer
        else:
            oneTransfer += " " + eachTransfer
             
    return reformatTransfers
             
## filter transfers to exchanges
def transfersExchange(byAccount):
    
    allTransfers = transfersAll(byAccount)
    transferList = []
    
    for eachTransfer in allTransfers:
        if any(exch in eachTransfer for exch in EXCHANGES):
            transferList.append(eachTransfer)
            #print(eachTransfer)
    
        
## filter transfers to other accounts
def transfersNonExchange(byAccount):
    
    allTransfers = transfersAll(byAccount, False)
    transferList = []
    
    for eachTransfer in allTransfers:
        if not any(exch in eachTransfer for exch in EXCHANGES):
            transferList.append(eachTransfer)
            print(eachTransfer)
    

## filter transfers through streaming blockchain
def transferOut(byAccount, lastDays=7, isAll=False):
    memoList = []
    accomplice = []
    try:
        currentBlock = blockchain.get_current_block_num()
        for eachTxn in blockchain.stream(opNames=['transfer'],start=calcStartBlock(currentBlock, lastDays), stop=currentBlock):
            if eachTxn['type'] != 'transfer':
                continue
                
            if eachTxn['to'] in EXCHANGES:
                if memoList and eachTxn['memo'] in memoList and byAccount != eachTxn['from']:                    
                    accomplice.append(eachTxn['from'])
                    print(eachTxn['from'])
                elif eachTxn['memo'] not in memoList and byAccount == eachTxn['from']:
                    memoList.append(eachTxn['memo'])
                    print(eachTxn['memo'])
                    
                
    except Exception as error:
        logger.info(" from transferOut()" + datetime.datetime.utcnow())
        logger.error(error)
    
def calcStartBlock(currentBlock, lastDays):
    """
      days to seconds = 60secs x 60mins x 24hrs x lastDays
      seconds to blocks = (days to seconds)/3 seconds
      Note: 1 block is generated every 3 seconds
    """
    
    daysToBlocks = (60*60*24*lastDays)/3
    
    return currentBlock-daysToBlocks


def main():
    try:
        #cttBot.run(TOKEN)
        transferOut('aurora-ca', lastDays=2)
    except Exception as error:
        logger.info("from main")
        logger.info(datetime.datetime.utcnow())
        logger.error(error)

if __name__ == '__main__':
    main()