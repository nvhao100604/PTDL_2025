import yahoo_fin.stock_info as si
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
#import pyfolio as pf

    
#==============================================================================
# Tab 1 Summary
#==============================================================================

def tab1():
    # Lấy ticker từ biến toàn cục
    global ticker

    st.title("Summary")
    st.write("Select ticker on the left to begin")
    st.write(ticker)

    @st.cache_data
    def getsummary_yf(ticker_local):
        try:
            stock_ticker = yf.Ticker(ticker_local)
            info_dict = stock_ticker.info
            if not info_dict or info_dict.get('regularMarketPrice') is None:
                return pd.DataFrame()
            
            df = pd.DataFrame(info_dict.items(), columns=['attribute', 'value'])
            # Lọc bỏ các giá trị None hoặc rỗng
            df = df[df['value'].notna()]
            df = df[df['value'] != '']
            return df
        except Exception:
            return pd.DataFrame()

    if ticker != '-':
        summary = getsummary_yf(ticker)

        if summary.empty:
            st.error("Could not retrieve summary data for the selected ticker. Data may not be available or ticker is invalid.")
            return

        summary['value'] = summary['value'].astype(str)
        summary.set_index('attribute', inplace=True)

        # Chia đều dữ liệu thành 2 cột
        midpoint = len(summary) // 2
        col1 = summary.iloc[:midpoint]
        col2 = summary.iloc[midpoint:]

        c1, c2 = st.columns(2)
        with c1:
            st.dataframe(col1)
        with c2:
            st.dataframe(col2)
            
                        
             
    #The code below uses the yahoofinance package to get all the available stock
    #price data. Plotly is then used to visualize the data.  An interesting feature
    #from plotly called range selector is also used. A list of dictionaries
    #is added to range selector to make buttons and identify the periods.
    #References:
    #https://plotly.com/python/range-slider/
    
        
    @st.cache_data
    def getstockdata(ticker):
        stockdata = yf.download(ticker, period = 'MAX', progress=False)
        return stockdata
        
    if ticker != '-':
            chartdata = getstockdata(ticker) 
            if chartdata.empty:
                st.warning(f"Could not retrieve price data for ticker {ticker}. Please try another ticker.")           
            else:
                fig = px.area(chartdata, chartdata.index, chartdata['Close'])
                
                fig.update_xaxes(
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1, label="1M", step="month", stepmode="backward"),
                            dict(count=3, label="3M", step="month", stepmode="backward"),
                            dict(count=6, label="6M", step="month", stepmode="backward"),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1Y", step="year", stepmode="backward"),
                            dict(count=3, label="3Y", step="year", stepmode="backward"),
                            dict(count=5, label="5Y", step="year", stepmode="backward"),
                            dict(label = "MAX", step="all")
                        ])
                    )
                )
                st.plotly_chart(fig)
            

#==============================================================================
# Tab 1 Summary
#==============================================================================

def tab1():
    
    st.title("Summary")
    st.write("Select ticker on the left to begin")
    st.write(ticker)
    
    # Updated: Added @st.cache_data for caching
    @st.cache_data
    def getsummary_yf(ticker):
        try:
            stock_ticker = yf.Ticker(ticker)
            info_dict = stock_ticker.info
            # Kiểm tra xem có dữ liệu không
            if not info_dict or info_dict.get('regularMarketPrice') is None:
                 return pd.DataFrame()
            
            df = pd.DataFrame(info_dict.items(), columns=['attribute', 'value'])
            return df 
        except Exception:
            return pd.DataFrame()

    # Danh sách các key Tóm tắt (Sử dụng tên thuộc tính phổ biến của yfinance)
    # LƯU Ý: Nếu bạn cần các trường khác, bạn phải thay đổi tên key ở đây.
    KEYS_COL1 = [
        'regularMarketOpen', 'dayLow', 'dayHigh', 'fiftyTwoWeekLow', 
        'fiftyTwoWeekHigh', 'marketCap', 'volume', 'averageVolume'
    ]
    KEYS_COL2 = [
        'regularMarketPrice', 'previousClose', 'bid', 'ask', 
        'trailingPE', 'forwardPE', 'dividendRate', 'dividendYield'
    ]
        
    c1, c2 = st.columns((1,1))
    
    if ticker != '-':
        summary = getsummary_yf(ticker)
        
        if summary.empty:
            st.error("Could not retrieve summary data for the selected ticker. Data may not be available or ticker is invalid.")
        else:
            # Lọc bằng tên thuộc tính (key) thay vì chỉ mục số
            summary.set_index('attribute', inplace=True)
            summary['value'] = summary['value'].astype(str) # Giữ lại việc chuyển sang str
            
            with c1:        
                # Lọc các hàng có thuộc tính nằm trong danh sách KEYS_COL1
                showsummary_c1 = summary.loc[summary.index.intersection(KEYS_COL1)]
                st.dataframe(showsummary_c1)
                
            with c2:        
                # Lọc các hàng có thuộc tính nằm trong danh sách KEYS_COL2
                showsummary_c2 = summary.loc[summary.index.intersection(KEYS_COL2)]
                st.dataframe(showsummary_c2)
            
                        
             
    #The code below uses the yahoofinance package to get all the available stock
    #price data. Plotly is then used to visualize the data. An interesting feature
    #from plotly called range selector is also used. A list of dictionaries
    #is added to range selector to make buttons and identify the periods.
    #References:
    #https://plotly.com/python/range-slider/
    
        
    @st.cache_data
    def getstockdata(ticker):
        stockdata = yf.download(ticker, start='1900-01-01', progress=False)
        return stockdata
        
    if ticker != '-':
            chartdata = getstockdata(ticker) 
            # Giữ lại kiểm tra .empty đã sửa lỗi ValueError trước đó
            if chartdata.empty:
                st.warning(f"Could not retrieve price data for ticker {ticker}. Please try another ticker.") 
            else:
                fig = px.area(chartdata, x=chartdata.index, y=chartdata['Close'].squeeze())
                
                fig.update_xaxes(
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1, label="1M", step="month", stepmode="backward"),
                            dict(count=3, label="3M", step="month", stepmode="backward"),
                            dict(count=6, label="6M", step="month", stepmode="backward"),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1Y", step="year", stepmode="backward"),
                            dict(count=3, label="3Y", step="year", stepmode="backward"),
                            dict(count=5, label="5Y", step="year", stepmode="backward"),
                            dict(label = "MAX", step="all")
                        ])
                    )
                )
                st.plotly_chart(fig)   
              
    
#==============================================================================
# Tab 2 Chart
#==============================================================================


#The code below divides the streamlit page into 5 columns. The first two columns
#have a date picker option to select start and end dates and the the other three
#have dropdown selection boxes for duration, interval, and type of plot.

# def tab2():
#     st.title("Chart")
#     st.write(ticker)
    
#     st.write("Set duration to '-' to select date range")
    
#     c1, c2, c3, c4,c5 = st.columns((1,1,1,1,1))
    
#     with c1:
        
#         start_date = st.date_input("Start date", datetime.today().date() - timedelta(days=30))
        
#     with c2:
        
#         end_date = st.date_input("End date", datetime.today().date())        
        
#     with c3:
        
#         duration = st.selectbox("Select duration", ['-', '1Mo', '3Mo', '6Mo', 'YTD','1Y', '3Y','5Y', 'MAX'])          
        
#     with c4: 
        
#         inter = st.selectbox("Select interval", ['1d', '1mo'])
        
#     with c5:
        
#         plot = st.selectbox("Select Plot", ['Line', 'Candle'])
    
#     def flatten_columns(df):
#         df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
#         return df
        
 
# #The code below first obtains all the data using the download option from yahoo finance.
# #It then creates a column for the simple moving average, makes the date index into a column
# #and then subsets the dataframe to get just the date and and SMA column.
# #Then if a duration is selected from the dropdown, data for that duration is downloaded
# # and the SMA column is merged to the dataframe. If a duration is not selected then
# #automatically the specified date range is used to get the data and that is also merged
# #with the SMA column
# #References:
# #https://towardsdatascience.com/data-science-in-finance-56a4d99279f7

           
             
#     @st.cache_data           
#     def getchartdata(ticker):

#         SMA = yf.download(ticker, start="1900-01-01", progress=False)

#         # ✅ Flatten MultiIndex columns
#         SMA = flatten_columns(SMA)

#         SMA.index.name = "Date"
#         SMA = SMA.reset_index()

#         SMA["SMA"] = SMA["Close"].rolling(50).mean()
#         SMA = SMA[["Date", "SMA"]]

#         # Load chartdata
#         if duration != "-":
#             chartdata = yf.download(ticker, period=duration, interval=inter)
#         else:
#             chartdata = yf.download(ticker, start=start_date, end=end_date, interval=inter)

#         # ✅ Flatten MultiIndex columns
#         chartdata = flatten_columns(chartdata)

#         chartdata.index.name = "Date"
#         chartdata = chartdata.reset_index()

#         # ✅ Debug (giữ lại)
#         print("==== SMA COLUMNS ====")
#         print(SMA.columns.tolist())
#         print("==== CHARTDATA COLUMNS ====")
#         print(chartdata.columns.tolist())

#         # ✅ Merge không lỗi nữa
#         chartdata = chartdata.merge(SMA, on="Date", how="left")
#         return chartdata


# #The code below uses plotly to visualize the data. Subplots from plotly is used to make 2 y axis.
# #First y axis shows the stock close price and SMA and the second is used to show volume. 
# #Plotly graph objects are used to add graphs to the axes.The range for the y axis for 
# #volume is manipulated so that the bars appear small.
# #References:
# #https://plotly.com/python/multiple-axes/   
# #https://plotly.com/python/candlestick-charts/        
        
#     if ticker != '-':
#             chartdata = getchartdata(ticker) 
            
                       
#             fig = make_subplots(specs=[[{"secondary_y": True}]])
            
#             if plot == 'Line':
#                 fig.add_trace(go.Scatter(x=chartdata['Date'], y=chartdata['Close'], mode='lines', 
#                                          name = 'Close'), secondary_y = False)
#             else:
#                 fig.add_trace(go.Candlestick(x = chartdata['Date'], open = chartdata['Open'], 
#                                              high = chartdata['High'], low = chartdata['Low'], close = chartdata['Close'], name = 'Candle'))
              
                    
#             fig.add_trace(go.Scatter(x=chartdata['Date'], y=chartdata['SMA'], mode='lines', name = '50-day SMA'), secondary_y = False)
            
#             fig.add_trace(go.Bar(x = chartdata['Date'], y = chartdata['Volume'], name = 'Volume'), secondary_y = True)

#             fig.update_yaxes(range=[0, chartdata['Volume'].max()*3], showticklabels=False, secondary_y=True)
            
#             max_volume = chartdata['Volume'].max()
#             # Chỉ cập nhật trục Y cho volume nếu max_volume > 0
#             if max_volume > 0:
#                  fig.update_yaxes(range=[0, max_volume * 3], showticklabels=False, secondary_y=True)
#             else:
#                  # Nếu max volume là 0, chỉ cần ẩn trục Y thứ 2
#                  fig.update_yaxes(showticklabels=False, secondary_y=True)
      
#             st.plotly_chart(fig)
           
             
@st.cache_data
def _download_prices(ticker, start_date=None, end_date=None, duration='-', inter='1d'):
    # yfinance đôi khi trả MultiIndex columns
    if duration != '-':
        # Map duration -> period cho yfinance
        period_map = {
            '1Mo':'1mo','3Mo':'3mo','6Mo':'6mo','YTD':'ytd','1Y':'1y','3Y':'3y','5Y':'5y','MAX':'max'
        }
        period = period_map.get(duration, '1y')
        df = yf.download(ticker, period=period, interval=inter, auto_adjust=False)
    else:
        df = yf.download(
            ticker,
            start=pd.to_datetime(start_date),
            end=pd.to_datetime(end_date) + pd.Timedelta(days=1),
            interval=inter,
            auto_adjust=False
        )

    if df.empty:
        return df

    # Flatten MultiIndex (nếu có)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index().rename(columns={'Adj Close':'AdjClose'})
    return df

def _sma(series, window=50):
    return series.rolling(window=window, min_periods=1).mean()

def _rsi(close, period=14):
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    gain = up.rolling(period).mean()
    loss = down.rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def tab2():
    st.title("Chart")
    st.write(ticker)
    st.write("Set duration to '-' to select date range")

    c1, c2, c3, c4, c5 = st.columns((1,1,1,1,1))
    with c1:
        start_date = st.date_input("Start date", datetime.today().date() - timedelta(days=180))
    with c2:
        end_date = st.date_input("End date", datetime.today().date())
    with c3:
        duration = st.selectbox("Select duration", ['-', '1Mo', '3Mo', '6Mo', 'YTD','1Y', '3Y','5Y', 'MAX'])
    with c4:
        inter = st.selectbox("Select interval", ['1d', '1wk', '1mo'])
    with c5:
        plot = st.selectbox("Select Plot", ['Line', 'Candle'])

    if ticker == '-':
        st.info("Chọn mã ở sidebar để xem biểu đồ.")
        return

    df = _download_prices(ticker, start_date, end_date, duration, inter)
    if df.empty or not {'Date','Close'}.issubset(df.columns):
        st.error("Không tải được dữ liệu giá hoặc thiếu cột cần thiết.")
        return

    # Chỉ báo
    df['SMA50'] = _sma(df['Close'], 50)
    up_mask = df['Close'].diff().fillna(0) >= 0
    vol_colors = np.where(up_mask, 'green', 'red')

    if plot == 'Line':
        # === 1 chart: Close + SMA (y1), Volume (y2), legend bên phải ===
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close'))
        fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA50'], mode='lines', name='50-day SMA'))
        fig.add_trace(
            go.Bar(x=df['Date'], y=df['Volume'], name='Volume',
                   marker=dict(color=vol_colors), opacity=0.35, yaxis='y2')
        )

        fig.update_layout(
            title=f"{ticker} — Close, 50-day SMA & Volume",
            hovermode='x unified',
            margin=dict(l=20, r=120, t=40, b=20),   # chừa chỗ bên phải cho legend
            xaxis=dict(title=''),
            yaxis=dict(title='Price'),
            yaxis2=dict(title='Volume', overlaying='y', side='right', showgrid=False),
            xaxis_rangeslider_visible=False,
            legend=dict(orientation='v', x=1.02, y=1, xanchor='left', yanchor='top')  # >>> legend bên phải
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        # === 1 chart duy nhất: Candle + SMA (y1), Volume (y2) ===
        fig = make_subplots(rows=1, cols=1, specs=[[{"secondary_y": True}]])

        if {'Open','High','Low','Close'}.issubset(df.columns):
            fig.add_trace(
                go.Candlestick(
                    x=df['Date'], open=df['Open'], high=df['High'],
                    low=df['Low'], close=df['Close'],
                    name='Candle', showlegend=True
                ),
                row=1, col=1, secondary_y=False
            )
        else:
            fig.add_trace(
                go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close'),
                row=1, col=1, secondary_y=False
            )

        fig.add_trace(
            go.Scatter(x=df['Date'], y=df['SMA50'], mode='lines', name='50-day SMA'),
            row=1, col=1, secondary_y=False
        )

        fig.add_trace(
            go.Bar(x=df['Date'], y=df['Volume'], name='Volume',
                   marker=dict(color=vol_colors), showlegend=True),
            row=1, col=1, secondary_y=True
        )

        fig.update_yaxes(title_text="Price", secondary_y=False)
        fig.update_yaxes(title_text="Volume", secondary_y=True, showgrid=False)

        fig.update_layout(
            title=f"{ticker} — Candlestick, 50-day SMA & Volume",
            hovermode='x unified',
            margin=dict(l=20, r=120, t=40, b=20),
            xaxis_rangeslider_visible=False,
            legend=dict(orientation='v', x=1.02, y=1, xanchor='left', yanchor='top')
        )

        st.plotly_chart(fig, use_container_width=True)
    
    def flatten_columns(df):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        return df

#==============================================================================
# Tab 3 Statistics
#==============================================================================

#The code below obtains information using get_stats_valuation and get_stats in
#Yahoo Finance. It then slices the dataframes and displays them in different 
#columns of the streamlit page under different headings.
# def tab3():
#      st.title("Statistics")
#      st.write(ticker)
#      c1, c2 = st.columns(2)
     
         
     
#      with c1:
#          st.header("Valuation Measures")
#          #@st.cache
#          def getvaluation(ticker):
#                  return si.get_stats_valuation(ticker)
    
#          if ticker != '-':
#                 valuation = getvaluation(ticker)
#                 valuation[1] = valuation[1].astype(str)
#                 valuation = valuation.rename(columns = {0: 'Attribute', 1: ''})
#                 valuation.set_index('Attribute', inplace=True)
#                 st.table(valuation)
                
        
#          st.header("Financial Highlights")
#          st.subheader("Fiscal Year")
         
#          #@st.cache
#          def getstats(ticker):
#                  return si.get_stats(ticker)
         
#          if ticker != '-':
#                 stats = getstats(ticker)
#                 stats['Value'] = stats['Value'].astype(str)
#                 stats.set_index('Attribute', inplace=True)
#                 st.table(stats.iloc[29:31,])
                
        
#          st.subheader("Profitability")
         
#          if ticker != '-':
#                 stats = getstats(ticker)
#                 stats['Value'] = stats['Value'].astype(str)
#                 stats.set_index('Attribute', inplace=True)
#                 st.table(stats.iloc[31:33,])
                
                
                
#          st.subheader("Management Effectiveness")
         
#          if ticker != '-':
#                 stats = getstats(ticker)
#                 stats['Value'] = stats['Value'].astype(str)
#                 stats.set_index('Attribute', inplace=True)
#                 st.table(stats.iloc[33:35,])
         
         
                
#          st.subheader("Income Statement")
         
#          if ticker != '-':
#                 stats = getstats(ticker)
#                 stats['Value'] = stats['Value'].astype(str)
#                 stats.set_index('Attribute', inplace=True)
#                 st.table(stats.iloc[35:43,])  
            
         
#          st.subheader("Balance Sheet")
         
#          if ticker != '-':
#                 stats = getstats(ticker)
#                 stats['Value'] = stats['Value'].astype(str)
#                 stats.set_index('Attribute', inplace=True)
#                 st.table(stats.iloc[43:49,])
         
#          st.subheader("Cash Flow Statement")
         
#          if ticker != '-':
#                 stats = getstats(ticker)
#                 stats['Value'] = stats['Value'].astype(str)
#                 stats.set_index('Attribute', inplace=True)
#                 st.table(stats.iloc[49:,])
         
        
                           
#      with c2:
#          st.header("Trading Information")
         
         
#          st.subheader("Stock Price History")
                  
#          if ticker != '-':
#                 stats = getstats(ticker)
#                 stats['Value'] = stats['Value'].astype(str)
#                 stats.set_index('Attribute', inplace=True)
#                 st.table(stats.iloc[:7,])
         
#          st.subheader("Share Statistics")
                  
#          if ticker != '-':
#                 stats = getstats(ticker)
#                 stats['Value'] = stats['Value'].astype(str)
#                 stats.set_index('Attribute', inplace=True)
#                 st.table(stats.iloc[7:19,])
         
#          st.subheader("Dividends & Splits")
                  
#          if ticker != '-':
#                 stats = getstats(ticker)
#                 stats['Value'] = stats['Value'].astype(str)
#                 stats.set_index('Attribute', inplace=True)
#                 st.table(stats.iloc[19:29,])


def tab3():
    st.title("Statistics")
    st.write(ticker)
    
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # Column 1: Valuation
    c1, c2 = st.columns(2)
    
    with c1:
        st.header("Valuation Measures")
        valuation_keys = ['marketCap','sharesOutstanding','floatShares','beta','trailingPE','forwardPE','priceToBook']
        valuation_data = {k: info[k] for k in valuation_keys if k in info}
        st.dataframe(pd.DataFrame(valuation_data.items(), columns=['Attribute','Value']), width=600, height=300)
        
        st.header("Financial Highlights")
        st.subheader("Income Statement")
        if stock.financials is not None:
            st.dataframe(stock.financials, width=600, height=300)
        
        st.subheader("Balance Sheet")
        if stock.balance_sheet is not None:
            st.dataframe(stock.balance_sheet, width=600, height=300)
        
        st.subheader("Cash Flow Statement")
        if stock.cashflow is not None:
            st.dataframe(stock.cashflow, width=600, height=300)
    
    # Column 2: Trading info
    with c2:
        st.header("Trading Information")
        trading_keys = ['previousClose','open','dayLow','dayHigh','volume','averageVolume','fiftyTwoWeekLow','fiftyTwoWeekHigh']
        trading_data = {k: info[k] for k in trading_keys if k in info}
        st.dataframe(pd.DataFrame(trading_data.items(), columns=['Attribute','Value']), width=600, height=300)
        
        st.subheader("Business Summary")
        if 'longBusinessSummary' in info:
            with st.expander("View full summary"):
                st.write(info['longBusinessSummary'][:1000] + " ...")
         
            
     

#==============================================================================
# Tab 4 Financials
#==============================================================================

#The code below obtains yearly and quartely financial statements from Yahoo Finance
#and displays them according the options selected by the users in streamlit. A
#combination of if statements is used to display according to the selected options.


# def tab4():
#       st.title("Financials")
#       st.write(ticker)
      
#       statement = st.selectbox("Show", ['Income Statement', 'Balance Sheet', 'Cash Flow'])
#       period = st.selectbox("Period", ['Yearly', 'Quarterly'])
      
#       @st.cache_data
#       def getyearlyincomestatement(ticker):
#             return si.get_income_statement(ticker)
      
#       @st.cache_data
#       def getquarterlyincomestatement(ticker):
#             return si.get_income_statement(ticker, yearly = False)
      
#       @st.cache_data
#       def getyearlybalancesheet(ticker):
#             return si.get_balance_sheet(ticker)
      
#       @st.cache_data
#       def getquarterlybalancesheet(ticker):
#             return si.get_balance_sheet(ticker, yearly = False)      

#       @st.cache_data
#       def getyearlycashflow(ticker):
#             return si.get_cash_flow(ticker)
      
#       @st.cache_data
#       def getquarterlycashflow(ticker):
#             return si.get_cash_flow(ticker, yearly = False)
        
          
#       if ticker != '-' and statement == 'Income Statement' and period == 'Yearly':
#                 data = getyearlyincomestatement(ticker)
#                 st.table(data)
            
#       if ticker != '-' and statement == 'Income Statement' and period == 'Quarterly':
#                 data = getquarterlyincomestatement(ticker)
#                 st.table(data)            

#       if ticker != '-' and statement == 'Balance Sheet' and period == 'Yearly':
#                 data = getyearlybalancesheet(ticker)
#                 st.table(data)            
      
#       if ticker != '-' and statement == 'Balance Sheet' and period == 'Quarterly':
#                 data = getquarterlybalancesheet(ticker)
#                 st.table(data)        
      
#       if ticker != '-' and statement == 'Cash Flow' and period == 'Yearly':
#                 data = getyearlycashflow(ticker)
#                 st.table(data)        
      
        
#       if ticker != '-' and statement == 'Cash Flow' and period == 'Quarterly':
#                 data = getquarterlycashflow(ticker)
#                 st.table(data)      
                
                
def tab4():
    import yfinance as yf
    import streamlit as st
    import pandas as pd

    st.title("Financials")
    st.write(ticker)

    statement = st.selectbox("Show", ['Income Statement', 'Balance Sheet', 'Cash Flow'])
    period = st.selectbox("Period", ['Yearly', 'Quarterly'])

    if ticker == '-':
        st.warning("Please select a valid ticker.")
        return

    stock = yf.Ticker(ticker)

    # Lấy dữ liệu theo loại và kỳ
    def get_data():
        if statement == 'Income Statement':
            df = stock.financials if period == 'Yearly' else stock.quarterly_financials
        elif statement == 'Balance Sheet':
            df = stock.balance_sheet if period == 'Yearly' else stock.quarterly_balance_sheet
        elif statement == 'Cash Flow':
            df = stock.cashflow if period == 'Yearly' else stock.quarterly_cashflow
        else:
            df = pd.DataFrame()
        return df

    data = get_data()

    if data.empty:
        st.warning(f"{statement} ({period}) data not available.")
    else:
        # Chuyển cột datetime sang str để hiển thị đẹp hơn
        data.columns = data.columns.strftime('%Y-%m-%d') if hasattr(data.columns, 'strftime') else data.columns
        st.dataframe(data)

                 
        
      
        
      
#==============================================================================
# Tab 5 Analysis
#==============================================================================

#In the code below, get_analysts_info is used to obtain the data. The output is
#in the form of a dictionary. .items() is used to get the items from the dictionary
#and then a for loop i used under which the dictionary items are changed into a list
# and each element of the list is then converted to a dataframe for displaying.


# def tab5():
#       st.title("Analysis")
#       st.write("Currency in USD")
#       st.write(ticker)
      
#       @st.cache_data
#       def getanalysis(ticker):
#             analysis_dict = si.get_analysts_info(ticker)
#             return analysis_dict.items()
 
           
#       if ticker != '-':           
#            for i in range(6):
#             analysis = getanalysis(ticker)
#             df = pd.DataFrame(list(analysis)[i][1])
#             st.table(df)


# def tab5():
#     st.title("Analysis")
#     st.write("Currency in USD")
#     st.write(ticker)
    
#     if ticker != '-':
#         stock = yf.Ticker(ticker)
        
#         st.subheader("Analyst Recommendations")
#         try:
#             rec = stock.recommendations
#             if rec is not None:
#                 st.dataframe(rec.tail(10))
#             else:
#                 st.write("Analyst data not available.")
#         except:
#             st.write("Analyst data not available.")
import streamlit as st
import pandas as pd
import time  # <--- thêm dòng này
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def tab5():
    st.title("Analysis")
    st.write("Currency in USD")
    st.write(ticker)

    @st.cache_data
    def getanalysis(ticker):
        url = f"https://finance.yahoo.com/quote/{ticker}/analysis"

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(3)  # đợi trang load

        html = driver.page_source
        driver.quit()

        tables = pd.read_html(html)
        table_names = [
            "Earnings Estimate",
            "Revenue Estimate",
            "Earnings History",
            "EPS Trend",
            "EPS Revisions",
            "Growth Estimates"
        ]

        # map tên bảng với dữ liệu tương ứng
        table_mapper = {name: tbl for name, tbl in zip(table_names, tables[:len(table_names)])}
        return table_mapper

    if ticker != '-':
        analysis = getanalysis(ticker)  # chỉ gọi 1 lần
        for name, df in analysis.items():
            st.subheader(name)
            st.table(df)
           
#==============================================================================
# Tab 6 Monte Carlo Simulation
#==============================================================================

#The code below performs and displays the monte carlo simulation for a specified
#time horizon and number of intervals



# def tab6():
#      st.title("Monte Carlo Simulation")
#      st.write(ticker)
     
#      #Dropdown for selecting simulation and horizon
#      simulations = st.selectbox("Number of Simulations (n)", [200, 500, 1000])
#      time_horizon = st.selectbox("Time Horizon (t)", [30, 60, 90])
     
#      #The code below takes past 30 day data using get_data. Then it gets the close
#      #price column and uses .pct_change() to get the daily return. Daily volatility 
#      #is then calculated as the standard deviation of the daily return.
#      @st.cache_data
#      def montecarlo(ticker, time_horizon, simulations):
     
#          end_date = datetime.now().date()
#          start_date = end_date - timedelta(days=30)
     
#          stock_price = si.get_data(ticker, start_date, end_date)
#          close_price = stock_price['close']
     
     
#          daily_return = close_price.pct_change()
#          daily_volatility = np.std(daily_return)
     
#          #Initialize the simulation dataframe    
#          simulation_df = pd.DataFrame()
     
#          for i in range(simulations):        
                      
#                 # The list to store the next stock price
#                 next_price = []
    
#     #    Create the next stock price
#                 last_price = close_price[-1]
    
#                 for x in range(time_horizon):
                               
#                       # Generate the random percentage change around the mean (0) and std (daily_volatility)
#                       future_return = np.random.normal(0, daily_volatility)

#             # Generate the random future price
#                       future_price = last_price * (1 + future_return)

#             # Save the price and go next
#                       next_price.append(future_price)
#                       last_price = future_price
    
#     #    Store the result of the simulation
#                 simulation_df[i] = next_price
                
#          return simulation_df   
          
# #The code below plots the monte carlo simulation using maplotlib. It also calculates
# #variance at risk and displays it. the VAR is calculated using the last row of
# #the montecarlo simulation. the distribution of this ending price is displaued and
# #the 5th percentile of the distribution is marked


#      if ticker != '-':
#          mc = montecarlo(ticker, time_horizon, simulations)
                  
#          end_date = datetime.now().date()
#          start_date = end_date - timedelta(days=30)
         
#          stock_price = si.get_data(ticker, start_date, end_date)
#          close_price = stock_price['close']
         
#          fig, ax = plt.subplots(figsize=(15, 10))
         

#          ax.plot(mc)
#          plt.title('Monte Carlo simulation for ' + str(ticker) + ' stock price in next ' + str(time_horizon) + ' days')
#          plt.xlabel('Day')
#          plt.ylabel('Price')
         
         
#          plt.axhline(y= close_price[-1], color ='red')
#          plt.legend(['Current stock price is: ' + str(np.round(close_price[-1], 2))])
#          ax.get_legend().legendHandles[0].set_color('red')

#          st.pyplot(fig)
         
#          # Value at Risk
#          st.subheader('Value at Risk (VaR)')
#          ending_price = mc.iloc[-1:, :].values[0, ]
#          fig1, ax = plt.subplots(figsize=(15, 10))
#          ax.hist(ending_price, bins=50)
#          plt.axvline(np.percentile(ending_price, 5), color='red', linestyle='--', linewidth=1)
#          plt.legend(['5th Percentile of the Future Price: ' + str(np.round(np.percentile(ending_price, 5), 2))])
#          plt.title('Distribution of the Ending Price')
#          plt.xlabel('Price')
#          plt.ylabel('Frequency')
#          st.pyplot(fig1)
         
         
#          future_price_95ci = np.percentile(ending_price, 5)
#          # Value at Risk
#          VaR = close_price[-1] - future_price_95ci
#          st.write('VaR at 95% confidence interval is: ' + str(np.round(VaR, 2)) + ' USD')
         
         

def tab6():
    st.title("Monte Carlo Simulation")
    st.write("Ticker:", ticker)
    
    # Dropdowns
    simulations = st.selectbox("Number of Simulations (n)", [200, 500, 1000])
    time_horizon = st.selectbox("Time Horizon (t)", [30, 60, 90])

    @st.cache_data
    def montecarlo_yf(ticker, time_horizon, simulations):
        stock = yf.Ticker(ticker)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        hist = stock.history(start=start_date, end=end_date)
        if hist.empty:
            return None
        
        close_price = hist['Close']
        daily_return = close_price.pct_change().dropna()
        daily_volatility = np.std(daily_return)

        simulation_df = pd.DataFrame()

        for i in range(simulations):
            next_price = []
            last_price = close_price[-1]
            for _ in range(time_horizon):
                future_return = np.random.normal(0, daily_volatility)
                future_price = last_price * (1 + future_return)
                next_price.append(future_price)
                last_price = future_price
            simulation_df[i] = next_price
        
        return simulation_df, close_price[-1]

    if ticker != '-':
        result = montecarlo_yf(ticker, time_horizon, simulations)
        if result is None:
            st.write("Stock price data not available for this ticker.")
            return
        mc, last_close = result

        # Plot Monte Carlo paths
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(mc)
        plt.title(f"Monte Carlo Simulation for {ticker} over next {time_horizon} days")
        plt.xlabel("Day")
        plt.ylabel("Price")
        plt.axhline(y=last_close, color='red', linestyle='--')
        plt.legend([f"Current stock price: {last_close:.2f} USD"])
        st.pyplot(fig)

        # Value at Risk (VaR)
        st.subheader("Value at Risk (VaR) at 95% confidence")
        ending_prices = mc.iloc[-1, :].values
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        ax2.hist(ending_prices, bins=50)
        var_5pct = np.percentile(ending_prices, 5)
        plt.axvline(var_5pct, color='red', linestyle='--', linewidth=2)
        plt.title("Distribution of Ending Prices")
        plt.xlabel("Price")
        plt.ylabel("Frequency")
        st.pyplot(fig2)

        VaR = last_close - var_5pct
        st.write(f"VaR at 95% confidence interval: {VaR:.2f} USD")
         
     
  
#==============================================================================
# Tab 7 Your Portfolio's Trend
#==============================================================================

#The code below uses a multiselect box to allow user to select multiple tickers.
#Then a new dataframe is created with each ticker as a column. A for loop is used to
#populate each column with the close price of that ticker. Then plotly is used to 
#visualize the trend of the selected portfolio
#Reference:
#https://blog.quantinsti.com/stock-market-data-analysis-python/


def tab7():
    st.title("Your Portfolio's Trend")

    # ✅ Lấy danh sách tickers S&P500 trực tiếp từ Wikipedia
    @st.cache_data
    def get_sp500_tickers():
        import requests
        import pandas as pd

        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(url, headers=headers).text

        tables = pd.read_html(html)

        for df in tables:
            cols = [str(c).lower() for c in df.columns]
            if "symbol" in cols:
                symbol_col = df.columns[[ "symbol" in str(c).lower() for c in df.columns ]][0]
                return df[symbol_col].tolist()

        return []

    sp500_tickers = get_sp500_tickers()

    # Cho người dùng chọn ticker
    selected_tickers = st.multiselect(
        "Select tickers in your portfolio",
        options=sp500_tickers,
        default=["AAPL"]
    )

    if not selected_tickers:
        st.warning("Please select at least one ticker.")
        return

    # Lấy dữ liệu đóng cửa cho từng ticker
    df = pd.DataFrame()
    for t in selected_tickers:
        try:
            data = yf.download(t, period='5y', progress=False)['Close']
            df[t] = data
        except Exception as e:
            st.error(f"Error downloading {t}: {e}")

    if not df.empty:
        fig = px.line(df, labels={'value':'Price', 'index':'Date'})
        st.plotly_chart(fig)
    else:
        st.warning("No data available for selected tickers.")
      
        
    
    
    
#==============================================================================
# Main body
#==============================================================================

def run1():
    
    # Add the ticker selection on the sidebar
    # Get the list of stock tickers from S&P500
    ticker_list = ['-'] + si.tickers_sp500()
    
    # Add selection box
    global ticker
    ticker = st.sidebar.selectbox("Select a ticker", ticker_list)
    
    
    # Add a radio box
    select_tab = st.sidebar.radio("Select tab", ['Summary', 'Chart', 'Statistics', 'Financials', 'Analysis', 'Monte Carlo Simulation', "Your Portfolio's Trend"])
    
    # Show the selected tab
    if select_tab == 'Summary':
        tab1()
    elif select_tab == 'Chart':
        tab2()
    elif select_tab == 'Statistics':
        tab3()
    elif select_tab == 'Financials':
        tab4()
    elif select_tab == 'Analysis':
        tab5()
    elif select_tab == 'Monte Carlo Simulation':
        tab6()
    elif select_tab == "Your Portfolio's Trend":
        tab7()
        
def run():
    import requests
    import pandas as pd
    from io import StringIO

    # Hàm thay thế si.tickers_sp500() để tránh lỗi 403
    def get_sp500_tickers():
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        headers = {"User-Agent": "Mozilla/5.0"}

        html = requests.get(url, headers=headers).text

        tables = pd.read_html(StringIO(html))

        # ✅ Tìm bảng có cột chứa “Symbol”
        for df in tables:
            cols = [str(c).lower() for c in df.columns]
            if any("symbol" in c for c in cols):
                # ✅ tìm đúng tên cột symbol thực tế
                symbol_col = df.columns[[ "symbol" in str(c).lower() for c in df.columns ]][0]
                return df[symbol_col].tolist()

        # ✅ nếu không tìm được bảng phù hợp
        raise ValueError("Không tìm được bảng S&P500 hoặc cột Symbol trong Wikipedia.")


    # Lấy danh sách ticker
    ticker_list = ['-'] + get_sp500_tickers()

    # Add selection box
    global ticker
    ticker = st.sidebar.selectbox("Select a ticker", ticker_list)

    # Add a radio box
    select_tab = st.sidebar.radio(
        "Select tab",
        [
            'Summary', 'Chart', 'Statistics', 'Financials',
            'Analysis', 'Monte Carlo Simulation', "Your Portfolio's Trend"
        ]
    )

    # Show the selected tab
    if select_tab == 'Summary':
        tab1()
    elif select_tab == 'Chart':
        tab2()
    elif select_tab == 'Statistics':
        tab3()
    elif select_tab == 'Financials':
        tab4()
    elif select_tab == 'Analysis':
        tab5()
    elif select_tab == 'Monte Carlo Simulation':
        tab6()
    elif select_tab == "Your Portfolio's Trend":
        tab7()
       
    
if __name__ == "__main__":
    run()    
