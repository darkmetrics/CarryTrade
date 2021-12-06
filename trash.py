def CarryTrade(fx_data:pd.DataFrame,
               n_trade:int=3,
               vol_data:Union[pd.Series, None]=None,
               vol_index:Union[str,None]=None,
               vol_type:str='simple',
               vol_quantile:Union[float]=0.95,
               quantile_method:str='nearest',
               vol_lag:int=1):
    """
    Returns results for carry trade strategy blablabla
    
    Parameters:
    -----------
    fx_data: pd.DataFrame with spot and forward FX prices. Forward FX
        columns should contain '1m' in column names. For each currency
        in the dataset there should be both spot and forward column.
        Number of currencies can not be less than n_trade * 2.
    n_trade:int, default 3 (as in article). Number of currency pairs
        to long and to short.    
    vol_data: pd.Series, default None. pd.Series with historical values
        for some volatility index.
    vol_index: str, default None. Name of the volatility index series:
        for instance, 'VIX' of 'VXY'.
    vol_type: str, default 'simple'. Possible values: 'simple' or 
        'averaged'. Depends on the volatility signal methodology 
        calculation (simple or averaged by 60 days, for details study
        the paper).
    vol_quantile:float, default None. The percentile of empirical
        volatility indicator distribution to use when calculating 
        "signal" for trading strategy (whether to trade or not).
    quantile_method: str, default 'nearest'. Possible values: 'linear', 
        'lower', 'higher', 'midpoint', 'nearest'. Empirical quantile 
        calculation method for np.percentile for volatility index.
    vol_lag: int, default 1. How many periods to shift volatility indicator
        ahead to use lags of volatility when calculating "signal".
    
    """
    # names for forward, spot and forward premium columns
    spot_cols = [x for x in fx_data.columns if '1m' not in x]
    fwd_cols = [x for x in fx_data.columns if '1m' in x]
    prem_cols = [x+'_premium' for x in spot_cols]
    ret_cols = [x+'_ret' for x in spot_cols]
    pos_cols = [x+'_pos' for x in spot_cols]
    # calculate spot returns and forward premiums 
    for x in spot_cols:
        fx_data[f'{x}_ret']=fx_data[x].pct_change()
        fx_data[f'{x}_premium']=(fx_data[f'{x}1m'] - fx_data[x])/fx_data[x]
    
    # shift premium column data 1 day ahead
    # to use forward data from day t_1 to trade in day t
    fx_data[prem_cols].shift(1)
    fx_data.dropna(inplace=True)
    
    # transform data to dict to make strategy faster
    fx_dict = fx_data[prem_cols].to_dict(orient='index')
    position_dict = {}
    
    # find tickers with n_trade highest forward premiums
    # and n_trade lowest forward premiums for each date
    for time, data in fx_dict.items():
        sorted_data = {k: v for k, v in \
                       sorted(data.items(), key=lambda item:item[1])}
        
        sorted_tickers = list(sorted_data.keys())
        # short tickers with highest premium (lowest discount)
        short_tickers = [x.split('_')[0] for x in sorted_tickers[-n_trade:]]
        # long tickers with lowest premium (highest discount)
        long_tickers = [x.split('_')[0] for x in sorted_tickers[0:n_trade]]

        # add positions to position dict
        position_dict[time]={(k+"_pos"):1 if k in long_tickers else \
                             (-1 if k in short_tickers else 0) \
                             for k in spot_cols}
    
    position_df = pd.DataFrame(position_dict).T
    fx_data = pd.merge(left=position_df, right=fx_data, 
                       left_index=True,
                       right_index=True)
    # calculate total strategy return
    fx_data['carry_return']=( (fx_data[pos_cols].div(n_trade)).values * \
                                 (fx_data[ret_cols]).values ).sum(axis=1)
    
    # take into account volatility
    if vol_index:
        if vol_type=='simple':
            # calculate expanding window volatility percentile
            percentile = vol_data.expanding().apply(lambda x: \
                                         np.quantile(x, 
                                                     q=vol_quantile, 
                                                     interpolation=quantile_method))
            percentile.name='threshold'
            # shift (or not shift) volatility data to decide whether 
            # to trade or not in day t based on volatility data from t-1
            vol_data = pd.concat([vol_data.shift(vol_lag), 
                                  percentile.shift(vol_lag)], 
                                 axis=1)
            
        elif vol_type=='averaged':
            # calculate expanding window average VIX over last 60 days
            average_60 = vol_data.rolling(window=60).mean().shift(1)
            # we shift series by 1 since volatility in day t is divided by
            # average of t-1 ... t-60 volatility values
            vol_change = vol_data/average_60
            percentile = vol_change.expanding().apply(lambda x: \
                                         np.quantile(x, 
                                                     q=vol_quantile, 
                                                     interpolation=quantile_method))
            vol_change.name = f'{vol_index}_change'
            percentile.name='threshold'
            # shift (or not shift) volatility data to decide whether 
            # to trade or not in day t based on volatility data from t-1
            vol_data = pd.concat([vol_data.shift(vol_lag), 
                                  vol_change.shift(vol_lag),
                                  percentile.shift(vol_lag)], 
                                 axis=1)
        
        # merge fx and volatility data to drop unnecessary vol data
        fx_data=pd.merge(left=fx_data,
                         right=vol_data,
                         how='left',
                         left_index=True,
                         right_index=True)
        fx_data.fillna(method='ffill', inplace=True)
        fx_data.dropna(inplace=True)
        
        # calculate trading signal for different approaches
        if vol_type=='simple':
            fx_data['signal'] = (fx_data[vol_index]<=fx_data['threshold'])*1
        elif vol_type=='averaged':
            fx_data['signal'] = (fx_data[vol_change.name]<=fx_data['threshold'])*1
            
        fx_data['strategy_return'] = fx_data['carry_return']*fx_data['signal']
            
    return fx_data