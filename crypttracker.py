# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 09:59:53 2018

@author: lovenfreedom (Steemit username) livefreensmart (Github username)
rewrite: crokkon (Steem & Github username)

Goals for hackathon:
1. provide account name and find transfers to exchanges
   create a list of exchanges from penguinpablo's and lukestokes' list - done
2. provide account name and find transfers to other accounts
3. provide account name and find who transferred to this account name
4. provide wallet address and find other accounts using it

Roadmap:
Discord integration

"""
import sys
from beem.blockchain import Blockchain
from beem.account import Account
from beem.amount import Amount
from beem.utils import parse_time, addTzInfo
from datetime import datetime, timedelta
from exchanges import EXCHANGES
from bots import BOTS


def datestr(date=None):
    """Convert timestamps to strings in a predefined format

    """
    if date is None:
        date = datetime.utcnow()
    if isinstance(date, str):
        date = parse_time(date)
    return date.strftime("%y-%m-%d %H:%M:%S")


def parse_transfer_history(account, days=0, include_bots=False,
                           debug=False):
    """parse the transfer history of an account

    :param str account: account to be parsed
    :param float days: number of days to take into account. 0 uses all
    available data (default)
    :param bool debug: enable debug printout (disabled by default)

    :return dict of sets with the list of receivers (`'sent_to'`),
    senders (`'received_from'`) and exchange memos
    (`'exchange_memos'`).

    """
    sent_to = set()
    received_from = set()
    exchange_memos = set()
    if debug:
        print("Parsing account history of %s" % (account))
    acc = Account(account)
    stop_time = addTzInfo(datetime.utcnow()) - timedelta(days=days)
    for op in acc.history_reverse(only_ops=['transfer']):
        if debug:
            sys.stdout.write("%s\r" % (op['timestamp']))
        if days and parse_time(op['timestamp']) < stop_time:
            break
        if acc['name'] == op['from']:
            if op['to'] in EXCHANGES:
                exchange_memos |= set([op['memo']])
            elif op['to'] not in BOTS or include_bots is True:
                sent_to |= set([op['to']])
        if acc['name'] == op['to']:
            if op['from'] in EXCHANGES or \
               (op['from'] in BOTS and not include_bots):
                continue
            received_from |= set([op['from']])
    return {'sent_to': sent_to, 'received_from': received_from,
            'exchange_memos': exchange_memos}


def transfermatch(account1, account2, days=0, include_bots=False,
                  debug=False):
    """Investigate the connection between two accounts based on their
    transfer history within the last [days] days.

    :param str account1: first account name
    :param str account2: second account name
    :param float days: number of days to take into account. 0 uses all
    available data (default)
    :param bool debug: enable debug printout (disabled by default)

    :return multi-line string with the results

    """
    hist1 = parse_transfer_history(account1, days=days,
                                   include_bots=include_bots,
                                   debug=debug)
    hist2 = parse_transfer_history(account2, days=days,
                                   include_bots=include_bots,
                                   debug=debug)
    result = "Transfer analysis between %s and %s:" % (account1, account2)
    if account1 in hist2['sent_to']:
        result += "\n+ %s transferred funds to %s" % (account2, account1)
    if account2 in hist1['sent_to']:
        result += "\n+ %s transferred funds to %s" % (account1, account2)
    if account1 not in hist2['sent_to'] and \
       account2 not in hist1['sent_to']:
        result += "\n- No transfers between them"
    receiver_overlap = hist1['sent_to'] & hist2['sent_to']
    if len(receiver_overlap):
        result += "\n+ Both sent funds to %s" % \
                  (", ".join(sorted(receiver_overlap)))
    else:
        result += "\n- No common fund receivers found"
    sender_overlap = hist1['received_from'] & hist2['received_from']
    if len(sender_overlap):
        result += "\n+ Both received funds from %s" % \
                  (", ".join(sorted(sender_overlap)))
    else:
        result += "\n- No common fund senders found"
    memo_overlap = hist1['exchange_memos'] & hist2['exchange_memos']
    if len(memo_overlap):
        result += "\n+ Both transferred funds to exchanges using memos %s" % \
                  (", ".join(sorted(memo_overlap)))
    else:
        result += "\n- No common exchange memos"
    return result


def transfers(account, trx_type='all', days=0, include_bots=False,
              debug=False):
    """Find all transfers sent or received by [account] within the last
    [days] days.

    :param str account: account to parse
    :param str trx_type: transaction type to list. Valid types are
    "in", "out" and "all".
    :param float days: number of days to take into account. 0 uses all
    available data (default)
    :param bool debug: enable debug printout (disabled by default)

    :return multi-line string with the results

    """
    trx_types = ['in', 'out', 'all']
    if trx_type not in trx_types:
        raise ValueError("Invalid trx_type - allowed values: %s" %
                         (trx_types))
    acc = Account(account)
    stop_time = addTzInfo(datetime.utcnow()) - timedelta(days=days)
    receivers = set()
    senders = set()
    result = ""
    for op in acc.history_reverse(only_ops=['transfer']):
        if debug:
            sys.stdout.write("%s\r" % (op['timestamp']))
        if days and parse_time(op['timestamp']) < stop_time:
            break
        if include_bots is False and \
           (op['from'] in BOTS or op['to'] in BOTS):
            continue  # skip transfers from/to bots
        if op['to'] == acc['name'] and trx_type in ['in', 'all']:
            result += "\n%s: %s received %s from %s: %s" % \
                      (datestr(op['timestamp']), op['to'],
                       Amount(op['amount']), op['from'], op['memo'])
            senders |= set([op['from']])
        if op['from'] == acc['name'] and trx_type in ['out', 'all']:
            result += "\n%s: %s sent %s to %s: %s" % \
                      (datestr(op['timestamp']), op['from'],
                       Amount(op['amount']), op['to'], op['memo'])
            receivers |= set([op['to']])
    if trx_type in ['in', 'all']:
        result += "\n%s received funds from %d senders: %s" % \
                  (account, len(senders), ", ".join(sorted(senders)))
    if trx_type in ['out', 'all']:
        result += "\n%s sent funds to %d receivers: %s" % \
                  (account, len(receivers), ", ".join(sorted(receivers)))
    if trx_type == 'all':
        overlap = set(senders) & set(receivers)
        result += "\n%s both sent to and received funds from %d accounts: " \
                  "%s" % (account, len(overlap), ", ".join(sorted(overlap)))
    return result[1:]


def memomatch(exchange, memo, days=0, debug=False):
    """Find all transfers to a given exchange that were done with the
    provided memo within the last [days] days. The memo parameter may
    be a substring of the actual transfer memo.

    :param str exchange: exchange account to parse
    :param str memo: memo or memo-substring to match
    :param float days: number of days to take into account. 0 uses all
    available data (default)
    :param bool debug: enable debug printout (disabled by default)

    :return multi-line string with the results

    """
    acc = Account(exchange)
    stop_time = addTzInfo(datetime.utcnow()) - timedelta(days=days)
    result = ""
    for op in acc.history_reverse(only_ops=['transfer']):
        if debug:
            sys.stdout.write("%s\r" % (op['timestamp']))
        if days and parse_time(op['timestamp']) < stop_time:
            break
        if memo not in op['memo']:
            continue
        result += "\n%s: %s transferred %s to %s: %s" % \
                  (datestr(op['timestamp']), op['from'],
                   Amount(op['amount']), op['to'], op['memo'])

    return result[1:]


def accountmatch(account, limit=10):
    """Find account names similar to the provided string. [account] can be
    an existing account of a partial name. Limit the output to [limit]
    results.

    :param str account: account to parse
    :param int limit: maximum number of similar account names to return

    :return list of account names
    """
    bc = Blockchain()
    return [acc['name'] for acc in
            bc.get_similar_account_names(account, limit=limit)]


def exchangetransfers(account, days=0, debug=False):
    """Find all outgoing transfers from a given account to any of the
    exchanges within the last [days] days.

    :param str account: account to parse
    :param float days: number of days to take into account. 0 uses all
    available data (default)
    :param bool debug: enable debug printout (disabled by default)

    :return multi-line string with the results
    """
    acc = Account(account)
    stop_time = addTzInfo(datetime.utcnow()) - timedelta(days=days)
    result = ""
    for op in acc.history_reverse(only_ops=['transfer']):
        if debug:
            sys.stdout.write("%s\r" % (op['timestamp']))
        if days and parse_time(op['timestamp']) < stop_time:
            break
        if op['to'] not in EXCHANGES:
            continue
        result += "\n%s: %s transferred %s to %s: %s" % \
                  (datestr(op['timestamp']), op['from'],
                   Amount(op['amount']), op['to'], op['memo'])
    return result[1:]
