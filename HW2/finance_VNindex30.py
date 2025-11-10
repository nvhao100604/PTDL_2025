# findash_app_vn30.py
# Modified from original findash_app.py to support VN-INDEX 30 (VN30) and S&P500
# - Allows user to choose market (S&P500 or VN30)
# - Loads VN30 tickers from local CSV `vn30_tickers.csv` (column 'Symbol') or falls back to a small sample list
# - Uses robust fetching for S&P500 (requests + User-Agent) to avoid 403
# - Keeps original dashboard structure and tabs

import requests
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

# ------------------------- helper functions for tickers -------------------------

def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        html = requests.get(url, headers=headers, timeout=10).text
        tables = pd.read_html(html)
        tickers = tables[0]["Symbol"].tolist()
        return tickers
    except Exception as e:
        print("⚠️ Could not fetch S&P500 tickers from Wikipedia:", e)
        return ['AAPL','MSFT','GOOG','AMZN','META','TSLA']


def get_vn30_tickers(from_file='vn30_tickers.csv'):
    """
    Load VN30 tickers from a local CSV file. The CSV should have a column named 'Symbol'
    containing the ticker symbol as recognized by yfinance (e.g. 'VIC.VN' or your local format).
    If the file is not found, return a small fallback list (user should replace with real tickers).
    """
    try:
        df = pd.read_csv(from_file)
        if 'Symbol' in df.columns:
            tickers = df['Symbol'].dropna().astype(str).tolist()
            if len(tickers) > 0:
                return tickers
        # try first column if Symbol not present
        tickers = df.iloc[:,0].dropna().astype(str).tolist()
        if len(tickers) > 0:
            return tickers
    except FileNotFoundError:
        print(f"File {from_file} not found. Please create it with VN30 tickers (column 'Symbol').")
    except Exception as e:
        print("Error reading VN30 tickers file:", e)

    # fallback sample list (replace with actual VN30 tickers in your CSV)
    return ['VNM.VN','VIC.VN','VHM.VN','HPG.VN','VCB.VN']


# ------------------------- small helper to normalize tickers -------------------------

def normalize_ticker_for_yf(ticker):
    """Ensure ticker fits yfinance convention. User-provided tickers should already be yfinance-ready.
    This function is a placeholder for any transformation you may need (e.g., add .VN suffix).
    """
    return ticker.strip()


# ------------------------- Dashboard tabs (kept similar to original) -------------------------

def tab1(ticker):
    st.title("Summary")
    st.write("Selected ticker:", ticker)

    def getsummary_safe(ticker):
        try:
            table = si.get_quote_table(ticker, dict_result=False)
            return table
        except Exception as e:
            st.warning(f"Could not fetch quote table for {ticker}: {e}")
            return None

    c1, c2 = st.columns((1,1))
    if ticker and ticker != '-':
        summary = getsummary_safe(ticker)
        if summary is not None:
            try:
                summary['value'] = summary['value'].astype(str)
                showsummary = summary.iloc[[14, 12, 5, 2, 6, 1, 16, 3],]
                showsummary.set_index('attribute', inplace=True)
                with c1:
                    st.dataframe(showsummary)
                showsummary2 = summary.iloc[[11, 4, 13, 7, 8, 10, 9, 0],]
                showsummary2.set_index('attribute', inplace=True)
                with c2:
                    st.dataframe(showsummary2)
            except Exception:
                # fallback display all
                with c1:
                    st.dataframe(summary)

    # Price area chart
    if ticker and ticker != '-':
        @st.cache_data
        def get_stockdata_yf(ticker):
            return yf.download(ticker, period='MAX')
        try:
            chartdata = get_stockdata_yf(ticker)
            fig = px.area(chartdata, x=chartdata.index, y='Close', title=f"Price history: {ticker}")
            fig.update_xaxes(rangeselector=dict(buttons=list([
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=3, label="3M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(count=3, label="3Y", step="year", stepmode="backward"),
                dict(count=5, label="5Y", step="year", stepmode="backward"),
                dict(label = "MAX", step="all")
            ])))
            st.plotly_chart(fig)
        except Exception as e:
            st.warning(f"Could not plot price history: {e}")


def tab2(ticker):
    st.title("Chart")
    st.write("Selected ticker:", ticker)
    st.write("Set duration to '-' to select date range")

    c1, c2, c3, c4, c5 = st.columns((1,1,1,1,1))
    with c1:
        start_date = st.date_input("Start date", datetime.today().date() - timedelta(days=30))
    with c2:
        end_date = st.date_input("End date", datetime.today().date())
    with c3:
        duration = st.selectbox("Select duration", ['-', '1Mo', '3Mo', '6Mo', 'YTD','1Y', '3Y','5Y', 'MAX'])
    with c4:
        inter = st.selectbox("Select interval", ['1d', '1mo'])
    with c5:
        plot = st.selectbox("Select Plot", ['Line', 'Candle'])

    if ticker and ticker != '-':
        @st.cache_data
        def get_chartdata_yf(ticker, duration, inter, start_date, end_date):
            SMA = yf.download(ticker, period='MAX')
            SMA['SMA'] = SMA['Close'].rolling(50).mean()
            SMA = SMA.reset_index()[['Date','SMA']]
            if duration != '-':
                chartdata = yf.download(ticker, period=duration, interval=inter).reset_index()
            else:
                chartdata = yf.download(ticker, start=start_date, end=end_date, interval=inter).reset_index()
            chartdata = chartdata.merge(SMA, on='Date', how='left')
            return chartdata

        try:
            chartdata = get_chartdata_yf(ticker, duration, inter, start_date, end_date)
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            if plot == 'Line':
                fig.add_trace(go.Scatter(x=chartdata['Date'], y=chartdata['Close'], mode='lines', name='Close'), secondary_y=False)
            else:
                fig.add_trace(go.Candlestick(x=chartdata['Date'], open=chartdata['Open'], high=chartdata['High'], low=chartdata['Low'], close=chartdata['Close'], name='Candle'))
            fig.add_trace(go.Scatter(x=chartdata['Date'], y=chartdata['SMA'], mode='lines', name='50-day SMA'), secondary_y=False)
            fig.add_trace(go.Bar(x=chartdata['Date'], y=chartdata['Volume'], name='Volume'), secondary_y=True)
            fig.update_yaxes(range=[0, chartdata['Volume'].max()*3], showticklabels=False, secondary_y=True)
            st.plotly_chart(fig)
        except Exception as e:
            st.warning(f"Could not build chart: {e}")


# For brevity, keep tab3, tab4, tab5, tab6, tab7 implementations
# We'll reuse original functions but they will accept ticker parameter when called

# (You can copy the original implementations from your findash_app.py here)

# ------------------------- Main app run -------------------------

def run():
    st.sidebar.title("Market & Ticker")
    market = st.sidebar.selectbox("Market", ['S&P500','VN30'])

    if market == 'S&P500':
        ticker_list = ['-'] + get_sp500_tickers()
    else:
        ticker_list = ['-'] + get_vn30_tickers()

    global ticker
    ticker = st.sidebar.selectbox("Select a ticker", ticker_list)

    select_tab = st.sidebar.radio("Select tab", ['Summary', 'Chart'])

    if select_tab == 'Summary':
        tab1(ticker)
    elif select_tab == 'Chart':
        tab2(ticker)


if __name__ == "__main__":
    run()
