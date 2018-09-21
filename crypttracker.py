# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 09:59:53 2018

@author: lovenfreedom (Steemit username) livefreensmart (Github username)

Goals for hackathon:
1. provide account name and find transfers to exchanges
  create a list of exchanges from penguinpablo's and lukestokes' list - done
  calculating estimated block num by date is an option for longer date range
    but for quick and dirty calculation of start block we'll use a dandy formula
2. provide account name and find transfers to other accounts
3. provide account name and find who transferred to this account name
4. provide wallet address and find other accounts using it

Roadmap:
Finish goals 3 and 4
Consider SteemSQL
Discord integration

"""

import datetime
import logging
import requests
from beem import Steem, blockchain
from beem.instance import set_shared_steem_instance
from beem.nodelist import NodeList
from lxml import html

from exchanges import EXCHANGES

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig()

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


def transfersAll(byAccount, hasMemo=True):
    """
    Get all transfers from Steemit account's transfer page
    https://steemit.com/@username/transfers

    :param str byAccount: Steemit account name to investigate
    :param bool hasMemo: Default True means grab memo. False means grab the transaction only.
    :return: List of all transfers visible on the account's page
    :rtype list
    """

    transferPage = "https://steemit.com/@{}/transfers".format(byAccount)
    page = requests.get(transferPage)
    tree = html.fromstring(page.content)

    ## Grab transfers only, ignore receive transactions
    if hasMemo:
        transfers = tree.xpath("//*[contains(text(),'Transfer')]/text()|//*[contains(text(),'Transfer')]/a/text()|//span[@class='Memo']/text()")
    else:
        transfers = tree.xpath("//*[contains(text(),'Transfer')]/text()|//*[contains(text(),'Transfer')]/a/text()")
     
    reformatTransfers = []
    oneTransfer = ""

    ## TODO: Find a more efficient way to group the xpath results.
    for eachTransfer in transfers:
        if "Transfer" in eachTransfer:
            if oneTransfer:
                reformatTransfers.append(oneTransfer)                     

            oneTransfer = eachTransfer
        else:
            oneTransfer += " " + eachTransfer
             
    return reformatTransfers

def transfersExchange(byAccount):
    """
    Retrieve all transfers to exchanges. Limited to transfers visible on account's transfer page.

    :param str byAccount: Steemit account name to investigate
    :return: List of all exchange transfers visible on the account's page
    :rtype list
    """
    
    allTransfers = transfersAll(byAccount)
    transferList = []
    
    for eachTransfer in allTransfers:
        if any(exch in eachTransfer for exch in EXCHANGES):
            transferList.append(eachTransfer)
            print(eachTransfer)
    
def transfersNonExchange(byAccount):
    """
    Retrieve all transfers to other accounts excluding exchanges. Limited to transfers visible on account's transfer page.

    :param str byAccount: Steemit account name to investigate
    :return: List of all non-exchange transfers visible on the account's page
    :rtype list
    """

    allTransfers = transfersAll(byAccount, False)
    transferList = []
    
    for eachTransfer in allTransfers:
        if not any(exch in eachTransfer for exch in EXCHANGES):
            transferList.append(eachTransfer)
            print(eachTransfer)

def streamTransfersOut(byAccount, lastDays=7):
    """
    Filter transfers to exchanges. Stream blockchain transactions starting from block N days prior to current block.
    WARNING: May be slow unless you can afford SteemSQL subscription.

    :param str byAccount: Steemit account name to investigate
    :param float lastDays: How far back you want to stream the blockchain
    :return: Merged list of transfer memos (usually wallet addresses) and other accounts using the same memo
    :rtype list
    """

    memoList = []
    accomplice = []
    try:
        currentBlock = blockChain.get_current_block_num()
        for eachTxn in blockChain.stream(opNames=['transfer'],start=calcStartBlock(currentBlock, lastDays), stop=currentBlock):
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
        logger.info(" from transferOut()" + str(datetime.datetime.utcnow()))
        logger.error(error)

    return memoList + accomplice
    
def calcStartBlock(currentBlock, lastDays):
    """
    Calculate starting block to stream based on how many days far back is specified.
      Formula:
        1. days to seconds = 60secs x 60mins x 24hrs x lastDays
        2. seconds to blocks = (days to seconds)/3 seconds

    Note: 1 block is generated every 3 seconds

    Beem has blockchain.get_estimated_block_num that takes datetime parameter. But you need to use beem.utils to properly provide UTC datetime.

    :param int currentBlock: Current block number
    :param float lastDays: Allow less than 1 day for hours/minutes
    :return: Calculated start block number
    :rtype: int
    """

    daysToBlocks = int(round((60*60*24*lastDays)/3))
    ## Round result of division and convert to int.
    ## Original type results in float. Stream requires int type for start and stop blocks.

    return currentBlock-daysToBlocks

def main():
    try:
        streamTransfersOut('reidlist', lastDays=0.08)
    except Exception as error:
        logger.info("from main")
        logger.info(datetime.datetime.utcnow())
        logger.error(error)

if __name__ == '__main__':
    main()