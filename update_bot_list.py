#
# Use this module to create or update "bots.py".
#
# The list of known bid bots and vote selling services is fetch from
# the SteemBotTracker API and merged with a list of custom known
# accounts.
# Running this module overwrites "bots.py", including any local
# modifications to that file.

import requests

bid_bots_url = 'https://steembottracker.net/bid_bots'
other_bots_url = 'https://steembottracker.net/other_bots'

# adding a few bots, resteem-services or registration accounts that
# are currently not contained in the steembottracker list
custom_bots = [
    'abcor',
    'all.cars',
    'allaz',
    'banjo',
    'bekirsolak',
    'crypto-n-custard',
    'gangresteem',
    'gina',
    'huge-whale',
    'hugo4u',
    'interfecto',
    'merlin7',
    'minnowbooster',
    'msp-reg',
    'obaku',
    'raise-me-up',
    'resteem.bot',
    'sezenke',
    'smartmarket',
    'steemcleaners',
    'super-booster',
    'superpromoter',
]

def request_json(url):
    """Request a JSON document from an http(s) URL

    :return JSON

    """
    r = requests.get(url)
    return r.json()


def get_bottracker_list():
    """get a list of all bots registered on steembottracker

    :return list of account names

    """
    bid_bots = [a['name'] for a in request_json(bid_bots_url)]
    other_bots = [a['name'] for a in request_json(other_bots_url)]
    return bid_bots + other_bots


if __name__ == "__main__":
    import sys
    bots = set(get_bottracker_list())  # use set to filter duplicates
    bots |= set(custom_bots)
    with open("bots.py", "w") as f:
        f.write("# This file was auto-generated with %s\n" % (sys.argv[0]))
        f.write("# Local modifications will likely be overwritten.\n")
        f.write("# Add custom account entries to %s\n\n" % (sys.argv[0]))
        botstrlist = ["    '%s'," % bot for bot in sorted(bots)]
        f.write("BOTS = [\n%s\n]\n" % ("\n".join(botstrlist)))
