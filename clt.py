#!/usr/bin/python
import argparse
import shelve
import sys
import re
from dwolla import DwollaUser, DwollaClientApp

config = shelve.open('dwolla')

# Helper functions
def pretty(d, indent=0):
    for key, value in d.iteritems():
        print str(key) + ": " + str(value)
        
def gatekeeper():
    if not config.has_key('token'):
        sys.exit("Please login first.")
        return

def isEmail(email):
	if len(email) > 7:
		if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
			return True
	return False

def isDwolla(dwollaId):
    return False

# Authentication
def logout(args):
    if config.has_key('token'):
        del config['token']
    config.sync()
    print 'You are now logged out.'
    
def login(args):
    token = raw_input('OAuth Token: ')
    config['token'] = token
    config.sync()
    return True

def showconfig(args):
    pretty(config)
    return True

# User methods
def me(args):
    gatekeeper();
    print 'Fetching your account information...'
    pretty(DwollaUser(config['token']).get_account_info())

def send(args):
    gatekeeper()
    
    # Ask for required parameters
    while not args.destination_id:
        args.destination_id = raw_input('Destination ID: ')
    while not args.amount:
        args.amount = raw_input('Amount: ')
    while not args.pin:
        args.pin = raw_input('Your PIN: ')
        
    # Try to determine the destination type
    if isDwolla(args.destination_id):
        isDwollaQ = raw_input('That destination looks like a Dwolla ID. Is this correct? [y/n] defaults to yes: ')
        if not isDwollaQ or isDwollaQ == 'y':
            args.destination_type == 'Dwolla'

    if isEmail(args.destination_id):
        isEmailQ = raw_input('That destination looks like an email address. Is this correct? [y/n] defaults to no: ')
        if isEmailQ == 'y':
            args.destination_type == 'Email'

    # Start request
    print 'Sending...'

    # Required Parameters
    params = {}
    params['dest'] = args.destination_id
    params['amount'] = args.amount
    params['pin'] = args.pin

    # Optional Parameters
    if args.destination_type:
        params['dest_type'] = args.destination_type
    if args.notes:
        params['notes'] = args.notes
    if args.assume_costs:
        params['assume_cost'] = args.assume_costs

    # Send request and print response
    print DwollaUser(config['token']).send_funds(**params)
    print 'Sent!'

def fundingSources(args):
    gatekeeper()
    print 'Retrieving funding sources...'
    pretty(DwollaUser(config['token']).get_funding_sources())

def fundingSources(args):
    gatekeeper()
    print 'Retrieving funding sources...'
    pretty(DwollaUser(config['token']).get_funding_sources())

def transactions(args):
    gatekeeper()
    print 'Retrieving transactions...'
    pretty(DwollaUser(config['token']).get_transaction_list())

def balance(args):
    gatekeeper()
    print 'Retrieving balance...'
    print 'Your account balance is: $' + str(DwollaUser(config['token']).get_balance())


# Init CLT
parser = argparse.ArgumentParser(description='Dwolla tools.')
subparsers = parser.add_subparsers()

# Subcommand: Login
login_parser = subparsers.add_parser('login', help='Authenticate')
login_parser.set_defaults(func=login)

# Subcommand: Logout
logout_parser = subparsers.add_parser('logout', help='Logout')
logout_parser.set_defaults(func=logout)

# Subcommand: Config
config_parser = subparsers.add_parser('config', help='Show config')
config_parser.set_defaults(func=showconfig)

# Subcommand: Send
send_parser = subparsers.add_parser('send', help='Send money')
send_parser.add_argument('-d', '--destination-id', metavar='destination_id', dest='destination_id', help='Destination ID')
send_parser.add_argument('-t', '--destination-type', metavar='destination_type', dest='destination_type', help='Destination Type', default=None)
send_parser.add_argument('-a', '--amount', metavar='amount', dest='amount', help='Amount')
send_parser.add_argument('-p', '--pin', metavar='pin', dest='pin', help='PIN')
send_parser.add_argument('-c', '--assume-costs', metavar='assume_costs', dest='assume_costs', help='Assume Costs?', default=False)
send_parser.add_argument('-n', '--notes', metavar='notes', dest='notes', help='Notes', default=None)
send_parser.set_defaults(func=send)

# Subcommand: Transactions
transactions_parser = subparsers.add_parser('transactions', help='Transactions Listing')
transactions_parser.set_defaults(func=transactions)

# Subcommand: Me
me_parser = subparsers.add_parser('me', help='Account information')
me_parser.set_defaults(func=me)

# Subcommand: Balance
balance_parser = subparsers.add_parser('balance', help='Account balance')
balance_parser.set_defaults(func=balance)

# Subcommand: Funding
funding_parser = subparsers.add_parser('funding', help='Funding source(s)')
funding_parser.add_argument('-f', '--funding-id', metavar='funding_id', dest='funding_id', help='Funding Source ID', default=None)
funding_parser.set_defaults(func=fundingSources)

# Start CLT
args = parser.parse_args()
args.func(args)