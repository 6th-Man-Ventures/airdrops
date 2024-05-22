from datetime import datetime
import requests
import pandas as pd
import statsmodels.api as stat

"""
functions to retrieve and process data from the CoinGecko API. 
"""

KEY = "your-api-key-here"


def to_unix(date: datetime) -> int:
    """turn datetime object into unix"""
    
    return int(date.timestamp())

def to_date(unix: int) -> datetime:
    """turn unix timestamp into datetime object"""
    
    unix = unix / 1000
    date = datetime.fromtimestamp(unix)
    return date

def get_historical_data(id: str, start: datetime, end: datetime) -> pd.DataFrame:
    """ method to retrieve historical price, supply, and eth price data for a given token
    
    args: 
        id (str) : CoinGecko id of token
        start (datetime) : start date for data
        end (datetime) : end date for data
    
    returns:
        DataFrame of prices for token, circulating supply, and eth prices
    
    """

    if KEY is None: 
        raise(Exception("No API Key Specified."))
    
    window_length = (end - start).days

    start, end = to_unix(start), to_unix(end)
    res = requests.get(f"https://pro-api.coingecko.com/api/v3/coins/{id}/market_chart/range?interval=daily&vs_currency=usd&from={start}&to={end}&x_cg_pro_api_key={KEY}")
    eth_res = requests.get(f"https://pro-api.coingecko.com/api/v3/coins/ethereum/market_chart/range?interval=daily&vs_currency=usd&from={start}&to={end}&x_cg_pro_api_key={KEY}") 
    btc_res = requests.get(f"https://pro-api.coingecko.com/api/v3/coins/bitcoin/market_chart/range?interval=daily&vs_currency=usd&from={start}&to={end}&x_cg_pro_api_key={KEY}")    
    
    if res.status_code != 200:
        print(id, "bad response")
        return pd.DataFrame()


    prices = res.json()["prices"]
    mktcaps = res.json()["market_caps"]
    volumes = res.json()["total_volumes"]
    eth_prices = eth_res.json()["prices"]
    btc_prices = btc_res.json()["prices"]
    
    # turn json objects into columns for dataframe
    date_col, price_col, eth_col, btc_col = [], [], [], []
    for price, eth, btc in zip(prices, eth_prices, btc_prices):
        date = price[0]
        date_obj = to_date(date)
        date_col.append(date_obj)
        price_col.append(price[1])
        eth_col.append(eth[1])
        btc_col.append(btc[1])

    data_dict = {
        "date" : date_col,
        "price" : price_col,
        'eth': eth_col,
        'btc': btc_col
        
    }
    
    df = pd.DataFrame(data_dict)
    df = df.set_index('date')

    
    normed = normalize_macro(df)
    normed['pct_change_price'] = ((normed['adj_price'] - normed['adj_price'].iat[0]) / normed['adj_price'].iat[0])

    if len(normed['price']) != window_length:
        print(date_col)
        raise(Exception(f"{id}: expected {window_length} data points. Received {len(normed['price'])} \n {normed['price']}"))

    
    print(id, res)
    
    return normed  

def normalize_macro(df):
    # set pct_change cols
    df["price_change"] = df['price'].pct_change().fillna(0)
    df["eth_change"] = df['eth'].pct_change().fillna(0)
    df["btc_change"] = df['btc'].pct_change().fillna(0)

    # use mult regression to find betas
    X = df[['btc_change', 'eth_change']]
    X = stat.add_constant(X)
    y = df['price_change']

    mult_reg = stat.OLS(y, X).fit()
    betas = mult_reg.params

    # remove betas of macro asset proxies
    df["adj_change"] = df['price_change'] - (betas['eth_change'] * df['eth_change']) 
    - (betas['btc_change'] * df['btc_change'])

    # adjust final price
    df['adj_price'] = df['price'].iloc[0] * (1 + df['adj_change']).cumprod()

    return df

