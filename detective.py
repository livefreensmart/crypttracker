# -*- coding: utf-8 -*-
"""
Created on Wed Nov 07 2018

@author: crokkon

"""
from __future__ import print_function
import click
import crypttracker as ct


@click.group(chain=True)
@click.option(
    '--verbose', '-v', default=False, is_flag=True,
    help='Enable verbose output')
@click.pass_context
def cli(ctx, verbose):
    """crypttracker CLI app

    """
    ctx.obj['DEBUG'] = verbose
    pass


@cli.command()
@click.argument('account1')
@click.argument('account2')
@click.option('--days', '-d', default=0,
              help='Restrict transfers to the last [days] days'
              '(0: no limit, default)')
@click.option('--include-bots', '-i', default=False, is_flag=True,
              help='Include transfers to/from known bidbots/services. '
              'Default: false')
@click.pass_context
def transfermatch(ctx, account1, account2, days, include_bots):
    """Investigate the connection between two accounts

    """
    print(ct.transfermatch(account1, account2, days=days,
                           debug=ctx.obj['DEBUG']))


@cli.command()
@click.argument('account')
@click.option('--days', '-d', default=0,
              help='Restrict transfers to the last [days] days'
              '(0: no limit, default)')
@click.option('--trx-type', '-t', type=click.Choice(['in', 'out', 'all']),
              default='all', help="Limit transaction type. Can be 'in', "
              "'out', or 'all' (default)")
@click.option('--include-bots', '-i', default=False, is_flag=True,
              help='Include transfers to/from known bidbots/services. '
              'Default: false')
@click.pass_context
def transfers(ctx, account, days, trx_type, include_bots):
    """List transfers sent or received by ACCOUNT.

    """
    print(ct.transfers(account, days=days, trx_type=trx_type,
                       include_bots=include_bots,
                       debug=ctx.obj['DEBUG']))


@cli.command()
@click.argument('exchange')
@click.argument('memo')
@click.option('--days', '-d', default=0,
              help='Restrict transfers to the last [days] days'
              '(0: no limit, default)')
@click.pass_context
def memomatch(ctx, exchange, memo, days):
    """Find exchange transfers matching a given memo.

    MEMO can be a full transfer memo or a substring.

    """
    print(ct.memomatch(exchange, memo, days=days,
                       debug=ctx.obj['DEBUG']))


@cli.command()
@click.argument('account')
@click.option('--limit', '-l', default=10,
              help='limit the output to [limit] results (default: 10)')
@click.pass_context
def accountmatch(ctx, account, limit):
    """Find account names similar to the provided string.

    ACCOUNT can be an existing account or a partial name. Limit the
    output to [limit] results.

    """
    print(", ".join(ct.accountmatch(account, limit)))


@cli.command()
@click.argument('account')
@click.option('--days', '-d', default=0,
              help='Restrict transfers to the last [days] days '
              '(0: no limit, default)')
@click.pass_context
def exchangetransfers(ctx, account, days):
    """Find all transfers to exchanges from a given account.

    Lists all transfers from a given account to any of the known
    exchanges within the last [days] days (default: no limit).

    """
    print(ct.exchangetransfers(account, days=days,
                               debug=ctx.obj['DEBUG']))


if __name__ == "__main__":
    cli(obj={})
