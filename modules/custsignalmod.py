from helpers.parameters import (
    parse_args, load_config
)
# Load arguments then parse settings
args = parse_args()
#get config file
DEFAULT_CONFIG_FILE = 'config.yml'
config_file = args.config if args.config else DEFAULT_CONFIG_FILE
parsed_config = load_config(config_file)

# Available indicators here: https://python-tradingview-ta.readthedocs.io/en/latest/usage.html#retrieving-the-analysis

from tradingview_ta import TA_Handler, Interval, Exchange
# use for environment variables
import os
# use if needed to pass args to external modules
import sys
# used for directory handling
import glob
import time
import threading

#OSC_INDICATORS = ['MACD', 'Stoch.RSI', 'Mom','RSI'] # Indicators to use in Oscillator analysis
OSC_INDICATORS = ['BBP', 'RSI'] # Indicators to use in Oscillator analysis
OSC_THRESHOLD = 2 # Must be less or equal to number of items in OSC_INDICATORS
MA_INDICATORS = ['EMA10', 'EMA20'] # Indicators to use in Moving averages analysis
MA_THRESHOLD = 2 # Must be less or equal to number of items in MA_INDICATORS 
INTERVAL = Interval.INTERVAL_5_MINUTES #Timeframe for analysis
MY_SECOND_INTERVAL = Interval.INTERVAL_15_MINUTES #Timeframe to verify RSI

EXCHANGE = 'BINANCE'
SCREENER = 'CRYPTO'
PAIR_WITH = parsed_config['trading_options']['PAIR_WITH']
TICKERS = parsed_config['trading_options']['TICKERS_LIST']
TIME_TO_WAIT = parsed_config['trading_options']['TIME_DIFFERENCE'] # Minutes to wait between analysis
FULL_LOG = parsed_config['script_options']['VERBOSE_MODE'] # List analysis result to console

def analyze(pairs):
    signal_coins = {}
    analysis = {}
    second_analysis = {}
    handler = {}
    second_handler = {}

    if os.path.exists('signals/custsignalmod.exs'):
        os.remove('signals/custsignalmod.exs')

    for pair in pairs:
        handler[pair] = TA_Handler(
            symbol=pair,
            exchange=EXCHANGE,
            screener=SCREENER,
            interval=INTERVAL,
            timeout= 10)

        second_handler[pair] = TA_Handler(
            symbol=pair,
            exchange=EXCHANGE,
            screener=SCREENER,
            interval=MY_SECOND_INTERVAL,
            timeout= 10)

    for pair in pairs:
        try:
            analysis = handler[pair].get_analysis()
            second_analysis = second_handler[pair].get_analysis()
        except Exception as e:
            # print("Signalsample:")
            # print("Exception:")
            # print(e)
            # print (f'Coin: {pair}')
            # print (f'handler: {handler[pair]}')
            # print('')
            dont_print_on_exception = True

        first_RSI = float(analysis.indicators['RSI'])
        second_RSI = float(second_analysis.indicators['RSI'])

        oscCheck=0
        maCheck=0
        for indicator in OSC_INDICATORS:
            if analysis.oscillators ['COMPUTE'][indicator] == 'BUY' and first_RSI <= 50 and second_RSI <= 50: oscCheck +=1

        for indicator in MA_INDICATORS:
            if analysis.moving_averages ['COMPUTE'][indicator] == 'BUY': maCheck +=1

        if FULL_LOG:
            print(f'Custsignalmod:{pair} Oscillators:{oscCheck}/{len(OSC_INDICATORS)} Moving averages:{maCheck}/{len(MA_INDICATORS)}')

        if oscCheck > OSC_THRESHOLD and maCheck > MA_THRESHOLD:
                signal_coins[pair] = pair
                if FULL_LOG:
                    print(f'Custsignalmod: Signal detected on {pair} at {oscCheck}/{len(OSC_INDICATORS)} oscillators and {maCheck}/{len(MA_INDICATORS)} moving averages.')
                with open('signals/custsignalmod.exs','a+') as f:
                    f.write(pair + '\n')

    return signal_coins

def do_work():
    signal_coins = {}
    pairs = {}

    pairs=[line.strip() for line in open(TICKERS)]
    for line in open(TICKERS):
        pairs=[line.strip() + PAIR_WITH for line in open(TICKERS)]

    while True:
        if not threading.main_thread().is_alive(): exit()
        signal_coins = analyze(pairs)
        if FULL_LOG:
            print(f'Custsignalmod: Analyzing {len(pairs)} coins')
            print(f'Custsignalmod: {len(signal_coins)} coins above {OSC_THRESHOLD}/{len(OSC_INDICATORS)} oscillators and {MA_THRESHOLD}/{len(MA_INDICATORS)} moving averages Waiting {TIME_TO_WAIT} minutes for next analysis.')
        time.sleep((TIME_TO_WAIT*60))
