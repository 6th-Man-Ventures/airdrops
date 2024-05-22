import pandas as pd
from statistics import median

def get_token_price_stats(tokens: list[str], price_data: dict, W: int) -> tuple[dict, dict]:
    """given a set of token ids, calculate each tokens price performance and volatility 
        over a time period.
    
    args:
        tokens (list[str]) : first set of token ids
        price_data (dict): coingecko price data of all tokens
        W (int) : window of time to calculate prices for.

    
    returns:
        results (dict) : dictionary of price performance and volatility for each token
                                in set of tokens.
    """

    results = dict()

    for token in tokens:
        data = price_data[token] 
        prices = data['adj_price'][:W] # modify window 
        start, end = prices.iloc[0], prices.iloc[-1]
        variance = (prices.std() / prices.mean()) * 100
        change = (end - start) / start

        results[token] = {
            'variance': variance,
            'price_change': change
        }
    
    return results


def aggregrate_price_stats(data: dict) -> dict:
    """ get averages of all tokens in a set once price performance metrics have been 
    calculated

    args:
        data (dict): dictionary containing price_change and variance stats given by 
        get_token_price_stats().
    
    returns:
        results (dict): summary stats
    """
    variances, changes = [], []

    for token in data:
        change = data[token]["price_change"]
        variance = data[token]["variance"]

        variances.append(variance)
        changes.append(change)

    
    results = {
            "avg_variance": sum(variances) / len(variances),
            "avg_change": sum(changes) / len(changes),
            "median_variance": median(variances),
            "median_change": median(changes)
        }


    return results


def aggregated_time_series(tokens: list[str], prices: dict, w_end: int, interval=5, 
                            w_start=1) -> dict:
    """
    calculate average price change and volatilty over a time series with a given 
    sampling frequency and initial point.

    args: 
        tokens (list[str]) : list of coingecko id's 
        prices (dict) : dictionary of DataFrames containing market data for each token
        w_end (int) : endpoint of desired window of analysis e.g. 60 day analysis 
        interval (int) : optional sampling frequency
        w_start (int) : optional window starting point 
    
    returns:
        time_series (dict) : timeseries data for averaged price_change and volatiltiy 

    """


    time_series = {
            "price": [],
            "variance": [], 
            "freq": []
        }

    W = w_start
    while W < w_end: 
        # calculate each token's stats at W
        price_sts = get_token_price_stats(tokens, prices, W) 
        agg_sts = aggregrate_price_stats(price_sts) # aggregate them
        
        # store aggregated stats 
        time_series["price"].append(agg_sts["avg_change"])
        time_series["variance"].append(agg_sts["avg_variance"])
        time_series["freq"].append(W)

        W += interval
    
    return time_series


def norm_windows(windows: list[list[float]], w: int) -> list[list[float]]:
    """normalizes windows of price data to percent difference from day of unlock 
    (first element of window).

    args: 
        windows (list[list[float]]) : list of intervals of price data, with unlock day 
        being the middle day.
        w (int) : length of window

    returns:
        normed (list[list[float]]) : normalized price windows
    """
    normed = []
    for window in windows:
        norm = pd.Series(index=range(-w, w + 1), dtype='float64')
        for i in range(-w, w + 1):
            norm[i] = ((window[i] - window[0]) / window[0]) * 100

        normed.append(norm)
        
    return normed