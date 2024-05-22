import pandas as pd


def get_holding_stats(data: pd.DataFrame) -> dict:
    """
    for a given table of airdrop claimant activity, calculate the percentage that did 
    nothing (held), sold some, sold all, or bought more

    args:
        data (DataFrame) : table with the expected column names found in /wallet_data
    returns
        results (dict) : index of percentage results for each of the mentioned buckets.

    """
    holders, sellers, buyers = 0, 0, 0
    
    for _, row in data.iterrows():
        net_bal = get_net_balance(row)

        if net_bal == 0:
            holders += 1
        elif net_bal > 0:
            buyers += 1
        else:
            sellers += 1
    
    assert(len(data) == holders + buyers + sellers) # ensure no double counting

    result = {
        "holders": {
            "raw": holders, 
            "pct": holders / len(data)
        },
        "buyers": {
            "raw": buyers,
            "pct": buyers / len(data)
        },
        "sellers": {
            "raw": sellers,
            "pct": sellers / len(data)
        }
    }
    
    return result

def aggregate_holding_stats(tokens, holding_data: dict, use_raw_tally=True) -> dict:
    """
    aggregates the action statistics for a list of tokens that have passed through 
    get_holding_stats(). uses raw tallies for computing averages. 

    args:
        data (dict) : dictionary of tokens with corresponding holding stat percentages
    returns:
        result (dict) : index of average holding stats
    """
    result = dict()

    tally = "raw" if use_raw_tally else "pct"

    holders, sellers, buyers = 0, 0, 0

    for t in tokens:
        holders += holding_data[t]["holders"][tally] 
        sellers += holding_data[t]["sellers"][tally]
        buyers += holding_data[t]["buyers"][tally] 
    
    total = holders + buyers + sellers
    
    result = {
        "holders": {
            "raw": holders, 
            "pct": holders / total
        },
        "buyers": {
            "raw": buyers,
            "pct": buyers / total
        },
        "sellers": {
            "raw": sellers,
            "pct": sellers / total
        }
    }

    return result


def get_net_balance(row: pd.DataFrame) -> int:
    """
    for a given claimant, calculate the net change after 30 days, with positive values 
    indicating net buy-in, negative values indicating net sell-off, and 0 indicating 
    holding. 

    args: 
        row (DataFrame) : claimant datat
    returns
        net_balance (int) : net balance 

    """
    if 'net' in row:
        return row['net']
    else:
        amount = row["amount"]
        sold = row["Amount Sold"]
        bought = row["Amount Bought"]
        net_balance = (amount - sold + bought) - amount

        return net_balance
    
