
def initialize(context):
    
    context.max_stocks = 100
    context.leverage = 1
    
    schedule_function(func = adjust_portfolio, 
                      date_rule = date_rules.month_start())
    
    set_universe(universe.DollarVolumeUniverse  \
                     (floor_percentile = 98.0,ceiling_percentile = 100.0))

                     
def adjust_portfolio(context, data):
    
    stockcount = 0
    stocks_to_buy = []
    
    for stocks in context.stock_selection:
	
        if data.can_trade(stocks) and stockcount < context.max_stocks:
            stocks_to_buy.append(stocks)
            stockcount = stockcount + 1

    for pos in context.portfolio.positions:

        if context.portfolio.positions[pos].amount > 0 and pos not in stocks_to_buy:
            order_target_value(pos, 0)
            
    for stock in stocks_to_buy:
        order_target_percent(stock, context.leverage / stockcount)
    
def before_trading_start(context, data): 
    
    """
      Called before the start of each trading day. 
      It updates our universe with the
      securities and values found from fetch_fundamentals.
    """
    
    stock_selection = get_fundamentals(
    
        query(
            fundamentals.valuation_ratios.pe_ratio,
            fundamentals.valuation.enterprise_value,
        )
        .filter(fundamentals.valuation_ratios.pe_ratio > 4)
        .filter(fundamentals.valuation.enterprise_value > 100000000)
    )
    context.stock_selection = stock_selection
    
    
def record_account_info(context, data):
    P = context.portfolio
    counter = 0
	
    for stock in data:
        amount = P.positions[stock].amount
        if amount > 0:
            counter = counter + 1
			
    record(stock_count = counter)
    record(cash = context.portfolio.cash)
    
def handle_data(context, data):
    record_account_info(context, data)
    