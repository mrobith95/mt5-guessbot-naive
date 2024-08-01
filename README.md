# mt5-guessbot-naive
This is a simple implementation of Random Walk (also called naive or no change model) to forecast latest candle's close price of indicies/stocks/forex/stuff provided by your MetaTrader5. This code also gives you 95% confidence interval for that candle's close and log prediction vs actual data.

### Disclaimer
While random walk model can used as benchmark for time series forecasting, note that its prediction is (almost) never accurate. Desicions or trades made using forecasts from this code are 100% your responsibility. 

### Requirement
To use this, you need to have Python at least 3.8.10 and the following packages installed:
* pandas at least 1.4.2
* numpy at least 1.22.3
* MetaTrader5 at least 5.0.37

You can download all of these packages using `pip install`.

## How to use?
Follow these steps:
* Modify the "Login and Settings" sheet in the ``mt5-guessbot-naive.xlsx`` file.
* Open the ``mt5-guessbot-naive.py`` file on Python's default IDLE and click "Run" > "Run Module". Make sure the ``mt5-guessbot-naive.py`` and ``mt5-guessbot-naive.xlsx`` files are in the same folder.

### How to stop the bot
If you run this on python's IDLE, you can press ``Ctrl+C`` in Python Shell. Python Shell should be open when you run ``mt5-guessbot-naive.py`` on IDLE.

## Settings
The bot's settings can be found in the ``mt5-guessbot-naive.xlsx`` file.

The ``Login and Settings`` contains login data. Fill only on the 2nd row with the following information:
* ``Acc. Number``: Your Account Number.
* ``Password``: That account's password.
* ``Server``: Server assigned for that account.

The ``Pair Table`` sheet contains settings for the symbol/pairs you want to forecast. The important data starts from the second row. You can fill in more than one row if you want to use this bot for more than one symbol/pair. The following information is required for each row:
* ``simbol``: Symbol/Pair name. Make sure this matches with the Symbol Name written on Market Watch.
* ``timeframe``: How often the bot forecast. Only receive the following: M1, M5, M15, M30, H1, H4, D1.
