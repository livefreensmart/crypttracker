# CrypTTracker
Perusing transfers for investigating vote farm accounts

<img src=https://ipfs.busy.org/ipfs/QmZ46c5mZe6DuRNmLouF7PrZM1ZdrvGqi3JbAnQKCmsVe4 width=400 height=300/>

<hr>
<hr>

**CrypTTracker** is a work-in-progress tool for investigating wallet transfers on the STEEM blockchain.

This tool will aid in pinpointing the main account the voting ring uses for withdrawing STEEM. It will also help collect accounts related to a voting ring.

## Python packages
Once Python is installed, install the required packages in your virtual environment
* [beem ](https://github.com/holgern/beem)

## Usage
`detective.py` is the CLI interface:

```
python detective.py --help
Usage: detective.py [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

  crypttracker CLI app



Options:
  -v, --verbose  Enable verbose output
  --help         Show this message and exit.

Commands:
  accountmatch       Find account names similar to the provided string.
  exchangetransfers  Find all transfers to exchanges from a given account.
  memomatch          Find exchange transfers matching a given memo.
  transfermatch      Investigate the connection between two accounts
  transfers          List transfers sent or received by ACCOUNT.
```

Use `python detective.py [COMMAND] --help` to get information on the individual commands.

## Roadmap
* Discord integration or a website
* Consider SteemSQL subscription for faster response time
* Retrieve accounts transferring to the account in question
* Retrieve different accounts using a given wallet address

## Contribution
Pull requests, comments, opening issues are appreciated.
