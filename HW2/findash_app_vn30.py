"""
VN30 Financial Dashboard - FinDash Vietnam
Phiên bản cho thị trường chứng khoán Việt Nam
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
from io import StringIO
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CẤU HÌNH VÀ DỮ LIỆU VN30
# ============================================================================

# Danh sách VN30 (30 cổ phiếu vốn hóa lớn nhất)
VN30_TICKERS = {
    'ACB': 'Ngân hàng ACB',
    'BCM': 'Khoáng sản Bắc Cạn',
    'BID': 'Ngân hàng BIDV',
    'BVH': 'Bảo Việt',
    'CTG': 'Ngân hàng Vietinbank',
    'FPT': 'FPT Corporation',
    'GAS': 'PetroVietnam Gas',
    'GVR': 'Cao su Việt Nam',
    'HDB': 'Ngân hàng HDBank',
    'HPG': 'Hòa Phát Group',
    'KDH': 'Khang Điền',
    'MBB': 'Ngân hàng MB',
    'MSN': 'Masan Group',
    'MWG': 'Mobile World',
    'NVL': 'Novaland',
    'PLX': 'Petrolimex',
    'POW': 'PetroVietnam Power',
    'SAB': 'Sabeco',
    'SSI': 'Chứng khoán SSI',
    'STB': 'Ngân hàng Sacombank',
    'TCB': 'Ngân hàng Techcombank',
    'TPB': 'Ngân hàng TPBank',
    'VCB': 'Ngân hàng Vietcombank',
    'VHM': 'Vinhomes',
    'VIB': 'Ngân hàng VIB',
    'VIC': 'Vingroup',
    'VJC': 'Vietjet Air',
    'VNM': 'Vinamilk',
    'VPB': 'Ngân hàng VPBank',
    'VRE': 'Vincom Retail'
}

# ============================================================================
# HÀM LẤY DỮ LIỆU TỪ VNSTOCK
# ============================================================================

@st.cache_data(ttl=3600)
def get_stock_data_vn(ticker, start_date=None, end_date=None):
    """
    Lấy dữ liệu cổ phiếu Việt Nam từ vnstock hoặc nguồn khác
    """
    try:
        # Dùng vnstock 
        from vnstock import stock_historical_data
        
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        df = stock_historical_data(ticker, start_date, end_date, 'VCI')
        df['Date'] = pd.to_datetime(df['TradingDate'])
        df.set_index('Date', inplace=True)
        
        # Chuẩn hóa tên cột
        df.rename(columns={
            'Open': 'Open',
            'High': 'High', 
            'Low': 'Low',
            'Close': 'Close',
            'Volume': 'Volume'
        }, inplace=True)
        
        return df[['Open', 'High', 'Low', 'Close', 'Volume']]
        
    except ImportError:
        # Nếu không có vnstock, tạo dữ liệu mẫu
        st.warning("⚠️ Chưa cài đặt vnstock. Đang hiển thị dữ liệu mẫu.")
        return generate_sample_data(ticker, start_date, end_date)

def generate_sample_data(ticker, start_date, end_date):
    """Tạo dữ liệu mẫu cho demo"""
    if start_date is None:
        start_date = datetime.now() - timedelta(days=365*5)
    if end_date is None:
        end_date = datetime.now()
    
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Giá khởi điểm theo từng mã
    base_prices = {
        'VCB': 90000, 'VIC': 80000, 'VHM': 70000, 'HPG': 25000,
        'VNM': 75000, 'TCB': 45000, 'FPT': 80000, 'MWG': 60000,
        'GAS': 95000, 'MSN': 60000
    }
    base_price = base_prices.get(ticker, 50000)
    
    np.random.seed(hash(ticker) % 2**32)
    returns = np.random.normal(0.0005, 0.02, len(dates))
    prices = base_price * (1 + returns).cumprod()
    
    df = pd.DataFrame({
        'Date': dates,
        'Open': prices * (1 + np.random.uniform(-0.01, 0.01, len(dates))),
        'High': prices * (1 + np.random.uniform(0, 0.02, len(dates))),
        'Low': prices * (1 + np.random.uniform(-0.02, 0, len(dates))),
        'Close': prices,
        'Volume': np.random.randint(100000, 5000000, len(dates))
    })
    
    df.set_index('Date', inplace=True)
    return df

@st.cache_data(ttl=3600)
def get_company_info(ticker):
    """Lấy thông tin công ty"""
    # Thông tin mẫu cho các công ty VN30
    info = {
        'ticker': ticker,
        'name': VN30_TICKERS.get(ticker, ticker),
        'exchange': 'HOSE',
        'industry': 'Đang cập nhật',
        'market_cap': 'Đang cập nhật',
        'employees': 'Đang cập nhật'
    }
    return info

# ============================================================================
# TAB 1: TỔNG QUAN (SUMMARY)
# ============================================================================

def tab1_summary(ticker):
    st.title("📊 Tổng Quan")
    
    if ticker == '-':
        st.info("👈 Vui lòng chọn mã cổ phiếu ở thanh bên trái để bắt đầu")
        return
    
    # Thông tin công ty
    company_info = get_company_info(ticker)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Mã CK", ticker)
    with col2:
        st.metric("Sàn", company_info['exchange'])
    with col3:
        st.metric("Ngành", company_info['industry'])
    
    st.subheader(f"🏢 {company_info['name']}")
    
    # Lấy dữ liệu
    data = get_stock_data_vn(ticker)
    
    if data is not None and not data.empty:
        # Tính toán các chỉ số
        current_price = data['Close'].iloc[-1]
        prev_price = data['Close'].iloc[-2] if len(data) > 1 else current_price
        change = current_price - prev_price
        change_pct = (change / prev_price) * 100
        
        # Hiển thị giá và thay đổi
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Giá hiện tại",
                f"{current_price:,.0f} ₫",
                f"{change:+,.0f} ({change_pct:+.2f}%)"
            )
        
        with col2:
            st.metric("Giá mở cửa", f"{data['Open'].iloc[-1]:,.0f} ₫")
        
        with col3:
            st.metric("Cao nhất", f"{data['High'].iloc[-1]:,.0f} ₫")
        
        with col4:
            st.metric("Thấp nhất", f"{data['Low'].iloc[-1]:,.0f} ₫")
        
        # Thống kê thêm
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_volume = data['Volume'].tail(30).mean()
            st.metric("KL TB 30 ngày", f"{avg_volume:,.0f}")
        
        with col2:
            high_52w = data['High'].tail(252).max()
            st.metric("Cao nhất 52 tuần", f"{high_52w:,.0f} ₫")
        
        with col3:
            low_52w = data['Low'].tail(252).min()
            st.metric("Thấp nhất 52 tuần", f"{low_52w:,.0f} ₫")
        
        # Biểu đồ giá
        st.subheader("📈 Biểu đồ Giá")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            fill='tozeroy',
            name='Giá đóng cửa',
            line=dict(color='#1f77b4', width=2)
        ))
        
        fig.update_xaxes(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1T", step="month", stepmode="backward"),
                    dict(count=3, label="3T", step="month", stepmode="backward"),
                    dict(count=6, label="6T", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1N", step="year", stepmode="backward"),
                    dict(count=3, label="3N", step="year", stepmode="backward"),
                    dict(count=5, label="5N", step="year", stepmode="backward"),
                    dict(label="Tất cả", step="all")
                ])
            ),
            rangeslider=dict(visible=True)
        )
        
        fig.update_layout(
            title=f"Giá cổ phiếu {ticker}",
            xaxis_title="Thời gian",
            yaxis_title="Giá (₫)",
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Thống kê tóm tắt
        st.subheader("📊 Thống kê Tóm tắt")
        
        col1, col2 = st.columns(2)
        
        with col1:
            stats_df = pd.DataFrame({
                'Chỉ số': [
                    'Giá trung bình 30 ngày',
                    'Giá trung bình 90 ngày',
                    'Độ biến động (30 ngày)',
                    'Tỷ suất sinh lợi YTD'
                ],
                'Giá trị': [
                    f"{data['Close'].tail(30).mean():,.0f} ₫",
                    f"{data['Close'].tail(90).mean():,.0f} ₫",
                    f"{data['Close'].tail(30).std():,.0f} ₫",
                    f"{((data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100):.2f}%"
                ]
            })
            st.dataframe(stats_df, hide_index=True, use_container_width=True)
        
        with col2:
            # Phân phối khối lượng
            fig_vol = go.Figure()
            fig_vol.add_trace(go.Bar(
                x=data.index.tail(30),
                y=data['Volume'].tail(30),
                name='Khối lượng',
                marker_color='lightblue'
            ))
            fig_vol.update_layout(
                title="Khối lượng giao dịch 30 ngày gần nhất",
                xaxis_title="Ngày",
                yaxis_title="Khối lượng",
                height=300
            )
            st.plotly_chart(fig_vol, use_container_width=True)

# ============================================================================
# TAB 2: BIỂU ĐỒ NÂNG CAO (CHART)
# ============================================================================

def tab2_chart(ticker):
    st.title("📈 Biểu Đồ Nâng Cao")
    
    if ticker == '-':
        st.info("👈 Vui lòng chọn mã cổ phiếu")
        return
    
    st.write(f"**Mã cổ phiếu:** {ticker} - {VN30_TICKERS.get(ticker, '')}")
    
    # Tùy chọn
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        duration = st.selectbox(
            "Khoảng thời gian",
            ['1 tháng', '3 tháng', '6 tháng', 'YTD', '1 năm', '3 năm', '5 năm', 'Tất cả']
        )
    
    with col2:
        chart_type = st.selectbox(
            "Loại biểu đồ",
            ['Nến (Candlestick)', 'Đường (Line)', 'Diện tích (Area)']
        )
    
    with col3:
        show_sma = st.checkbox("Hiển thị SMA", value=True)
    
    with col4:
        sma_period = st.number_input("Chu kỳ SMA", min_value=5, max_value=200, value=50)
    
    # Lấy dữ liệu theo duration
    if duration == '1 tháng':
        start_date = datetime.now() - timedelta(days=30)
    elif duration == '3 tháng':
        start_date = datetime.now() - timedelta(days=90)
    elif duration == '6 tháng':
        start_date = datetime.now() - timedelta(days=180)
    elif duration == 'YTD':
        start_date = datetime(datetime.now().year, 1, 1)
    elif duration == '1 năm':
        start_date = datetime.now() - timedelta(days=365)
    elif duration == '3 năm':
        start_date = datetime.now() - timedelta(days=365*3)
    elif duration == '5 năm':
        start_date = datetime.now() - timedelta(days=365*5)
    else:
        start_date = None
    
    data = get_stock_data_vn(ticker, start_date=start_date)
    
    if data is not None and not data.empty:
        # Tính SMA
        if show_sma:
            data['SMA'] = data['Close'].rolling(window=sma_period).mean()
        
        # Vẽ biểu đồ
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
            subplot_titles=(f'Giá {ticker}', 'Khối lượng')
        )
        
        # Biểu đồ giá
        if chart_type == 'Nến (Candlestick)':
            fig.add_trace(
                go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name='OHLC'
                ),
                row=1, col=1
            )
        elif chart_type == 'Đường (Line)':
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['Close'],
                    mode='lines',
                    name='Giá đóng cửa',
                    line=dict(color='blue', width=2)
                ),
                row=1, col=1
            )
        else:  # Area
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['Close'],
                    fill='tozeroy',
                    name='Giá đóng cửa',
                    line=dict(color='blue', width=1)
                ),
                row=1, col=1
            )
        
        # SMA
        if show_sma and 'SMA' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['SMA'],
                    mode='lines',
                    name=f'SMA({sma_period})',
                    line=dict(color='orange', width=2, dash='dash')
                ),
                row=1, col=1
            )
        
        # Khối lượng
        colors = ['red' if data['Close'].iloc[i] < data['Open'].iloc[i] else 'green' 
                  for i in range(len(data))]
        
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['Volume'],
                name='Khối lượng',
                marker_color=colors
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=700,
            showlegend=True,
            xaxis_rangeslider_visible=False,
            hovermode='x unified'
        )
        
        fig.update_yaxes(title_text="Giá (₫)", row=1, col=1)
        fig.update_yaxes(title_text="Khối lượng", row=2, col=1)
        fig.update_xaxes(title_text="Ngày", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Phân tích kỹ thuật
        st.subheader("🔍 Phân tích Kỹ thuật")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # RSI
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            st.metric("RSI (14)", f"{current_rsi:.2f}")
            if current_rsi > 70:
                st.caption("🔴 Vùng quá mua")
            elif current_rsi < 30:
                st.caption("🟢 Vùng quá bán")
            else:
                st.caption("⚪ Trung lập")
        
        with col2:
            # MACD
            ema12 = data['Close'].ewm(span=12).mean()
            ema26 = data['Close'].ewm(span=26).mean()
            macd = ema12 - ema26
            signal = macd.ewm(span=9).mean()
            
            st.metric("MACD", f"{macd.iloc[-1]:.0f}")
            if macd.iloc[-1] > signal.iloc[-1]:
                st.caption("🟢 Tín hiệu mua")
            else:
                st.caption("🔴 Tín hiệu bán")
        
        with col3:
            # Bollinger Bands
            sma20 = data['Close'].rolling(window=20).mean()
            std20 = data['Close'].rolling(window=20).std()
            upper_bb = sma20 + (std20 * 2)
            lower_bb = sma20 - (std20 * 2)
            
            current_price = data['Close'].iloc[-1]
            bb_position = ((current_price - lower_bb.iloc[-1]) / 
                          (upper_bb.iloc[-1] - lower_bb.iloc[-1])) * 100
            
            st.metric("BB Position", f"{bb_position:.1f}%")
            if bb_position > 80:
                st.caption("🔴 Gần dải trên")
            elif bb_position < 20:
                st.caption("🟢 Gần dải dưới")
            else:
                st.caption("⚪ Trung lập")

# ============================================================================
# TAB 3: THỐNG KÊ (STATISTICS)
# ============================================================================

def tab3_statistics(ticker):
    st.title("📊 Thống Kê Chi Tiết")
    
    if ticker == '-':
        st.info("👈 Vui lòng chọn mã cổ phiếu")
        return
    
    st.write(f"**Mã cổ phiếu:** {ticker} - {VN30_TICKERS.get(ticker, '')}")
    
    data = get_stock_data_vn(ticker)
    
    if data is not None and not data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Thống Kê Giá")
            
            price_stats = pd.DataFrame({
                'Chỉ số': [
                    'Giá hiện tại',
                    'Giá trung bình',
                    'Giá cao nhất',
                    'Giá thấp nhất',
                    'Độ lệch chuẩn',
                    'Hệ số biến động (CV)',
                    'Tỷ suất sinh lợi'
                ],
                'Giá trị': [
                    f"{data['Close'].iloc[-1]:,.0f} ₫",
                    f"{data['Close'].mean():,.0f} ₫",
                    f"{data['High'].max():,.0f} ₫",
                    f"{data['Low'].min():,.0f} ₫",
                    f"{data['Close'].std():,.0f} ₫",
                    f"{(data['Close'].std() / data['Close'].mean()) * 100:.2f}%",
                    f"{((data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100):.2f}%"
                ]
            })
            st.dataframe(price_stats, hide_index=True, use_container_width=True)
            
            st.subheader("📊 Phân phối Giá")
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(
                x=data['Close'],
                nbinsx=50,
                name='Phân phối giá',
                marker_color='lightblue'
            ))
            fig_hist.update_layout(
                xaxis_title="Giá (₫)",
                yaxis_title="Tần suất",
                height=300
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            st.subheader("📦 Thống Kê Khối Lượng")
            
            volume_stats = pd.DataFrame({
                'Chỉ số': [
                    'KL hiện tại',
                    'KL trung bình',
                    'KL cao nhất',
                    'KL thấp nhất',
                    'Tổng KL giao dịch',
                    'Giá trị giao dịch TB'
                ],
                'Giá trị': [
                    f"{data['Volume'].iloc[-1]:,.0f}",
                    f"{data['Volume'].mean():,.0f}",
                    f"{data['Volume'].max():,.0f}",
                    f"{data['Volume'].min():,.0f}",
                    f"{data['Volume'].sum():,.0f}",
                    f"{(data['Close'] * data['Volume']).mean():,.0f} ₫"
                ]
            })
            st.dataframe(volume_stats, hide_index=True, use_container_width=True)
            
            st.subheader("📊 Khối lượng theo Thời gian")
            fig_vol = go.Figure()
            fig_vol.add_trace(go.Scatter(
                x=data.index,
                y=data['Volume'],
                mode='lines',
                fill='tozeroy',
                name='Khối lượng',
                line=dict(color='green')
            ))
            fig_vol.update_layout(
                xaxis_title="Ngày",
                yaxis_title="Khối lượng",
                height=300
            )
            st.plotly_chart(fig_vol, use_container_width=True)
        
        # Phân tích tương quan
        st.subheader("🔗 Ma trận Tương Quan OHLC")
        
        corr_matrix = data[['Open', 'High', 'Low', 'Close', 'Volume']].corr()
        
        fig_corr = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values,
            texttemplate='%{text:.2f}',
            textfont={"size": 12},
            colorbar=dict(title="Tương quan")
        ))
        
        fig_corr.update_layout(
            title="Ma trận Tương quan",
            height=400
        )
        
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Thống kê theo tháng/năm
        st.subheader("📅 Thống Kê Theo Thời Gian")
        
        data_monthly = data.resample('M').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        })
        data_monthly['Return'] = data_monthly['Close'].pct_change() * 100
        
        st.dataframe(
            data_monthly.tail(12).style.format({
                'Open': '{:,.0f}',
                'High': '{:,.0f}',
                'Low': '{:,.0f}',
                'Close': '{:,.0f}',
                'Volume': '{:,.0f}',
                'Return': '{:+.2f}%'
            }),
            use_container_width=True
        )

# ============================================================================
# TAB 4: PHÂN TÍCH KỸ THUẬT (TECHNICAL ANALYSIS)
# ============================================================================

def tab4_technical(ticker):
    st.title("🔧 Phân Tích Kỹ Thuật")
    
    if ticker == '-':
        st.info("👈 Vui lòng chọn mã cổ phiếu")
        return
    
    st.write(f"**Mã cổ phiếu:** {ticker} - {VN30_TICKERS.get(ticker, '')}")
    
    data = get_stock_data_vn(ticker)
    
    if data is not None and not data.empty:
        
        # Tính các chỉ báo
        # Moving Averages
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['SMA_200'] = data['Close'].rolling(window=200).mean()
        data['EMA_12'] = data['Close'].ewm(span=12).mean()
        data['EMA_26'] = data['Close'].ewm(span=26).mean()
        
        # MACD
        data['MACD'] = data['EMA_12'] - data['EMA_26']
        data['Signal'] = data['MACD'].ewm(span=9).mean()
        data['MACD_Hist'] = data['MACD'] - data['Signal']
        
        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        data['BB_Middle'] = data['Close'].rolling(window=20).mean()
        data['BB_Std'] = data['Close'].rolling(window=20).std()
        data['BB_Upper'] = data['BB_Middle'] + (data['BB_Std'] * 2)
        data['BB_Lower'] = data['BB_Middle'] - (data['BB_Std'] * 2)
        
        # Tabs cho các chỉ báo
        tab_ma, tab_macd, tab_rsi, tab_bb = st.tabs([
            "📊 Moving Averages", 
            "📈 MACD", 
            "📉 RSI", 
            "📊 Bollinger Bands"
        ])
        
        with tab_ma:
            st.subheader("Đường Trung Bình Động (Moving Averages)")
            
            fig_ma = go.Figure()
            
            fig_ma.add_trace(go.Scatter(
                x=data.index, y=data['Close'],
                name='Giá đóng cửa',
                line=dict(color='black', width=2)
            ))
            
            fig_ma.add_trace(go.Scatter(
                x=data.index, y=data['SMA_20'],
                name='SMA 20',
                line=dict(color='blue', width=1, dash='dash')
            ))
            
            fig_ma.add_trace(go.Scatter(
                x=data.index, y=data['SMA_50'],
                name='SMA 50',
                line=dict(color='orange', width=1, dash='dash')
            ))
            
            fig_ma.add_trace(go.Scatter(
                x=data.index, y=data['SMA_200'],
                name='SMA 200',
                line=dict(color='red', width=1, dash='dash')
            ))
            
            fig_ma.update_layout(
                title="Biểu đồ Moving Averages",
                xaxis_title="Ngày",
                yaxis_title="Giá (₫)",
                height=500,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_ma, use_container_width=True)
            
            # Phân tích
            col1, col2, col3 = st.columns(3)
            
            current_price = data['Close'].iloc[-1]
            sma20 = data['SMA_20'].iloc[-1]
            sma50 = data['SMA_50'].iloc[-1]
            sma200 = data['SMA_200'].iloc[-1]
            
            with col1:
                if current_price > sma20:
                    st.success(f"Giá > SMA20: {sma20:,.0f} ₫ ✅")
                else:
                    st.error(f"Giá < SMA20: {sma20:,.0f} ₫ ❌")
            
            with col2:
                if current_price > sma50:
                    st.success(f"Giá > SMA50: {sma50:,.0f} ₫ ✅")
                else:
                    st.error(f"Giá < SMA50: {sma50:,.0f} ₫ ❌")
            
            with col3:
                if current_price > sma200:
                    st.success(f"Giá > SMA200: {sma200:,.0f} ₫ ✅")
                else:
                    st.error(f"Giá < SMA200: {sma200:,.0f} ₫ ❌")
        
        with tab_macd:
            st.subheader("MACD (Moving Average Convergence Divergence)")
            
            fig_macd = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.6, 0.4]
            )
            
            # Giá
            fig_macd.add_trace(
                go.Scatter(x=data.index, y=data['Close'], name='Giá', line=dict(color='black')),
                row=1, col=1
            )
            
            # MACD
            fig_macd.add_trace(
                go.Scatter(x=data.index, y=data['MACD'], name='MACD', line=dict(color='blue')),
                row=2, col=1
            )
            
            fig_macd.add_trace(
                go.Scatter(x=data.index, y=data['Signal'], name='Signal', line=dict(color='orange')),
                row=2, col=1
            )
            
            # Histogram
            colors = ['green' if val >= 0 else 'red' for val in data['MACD_Hist']]
            fig_macd.add_trace(
                go.Bar(x=data.index, y=data['MACD_Hist'], name='Histogram', marker_color=colors),
                row=2, col=1
            )
            
            fig_macd.update_yaxes(title_text="Giá (₫)", row=1, col=1)
            fig_macd.update_yaxes(title_text="MACD", row=2, col=1)
            fig_macd.update_layout(height=600, hovermode='x unified')
            
            st.plotly_chart(fig_macd, use_container_width=True)
            
            # Tín hiệu
            col1, col2, col3 = st.columns(3)
            
            macd_current = data['MACD'].iloc[-1]
            signal_current = data['Signal'].iloc[-1]
            hist_current = data['MACD_Hist'].iloc[-1]
            
            with col1:
                st.metric("MACD", f"{macd_current:.2f}")
            
            with col2:
                st.metric("Signal", f"{signal_current:.2f}")
            
            with col3:
                st.metric("Histogram", f"{hist_current:.2f}")
            
            if macd_current > signal_current:
                st.success("🟢 Tín hiệu MUA - MACD cắt lên Signal line")
            else:
                st.error("🔴 Tín hiệu BÁN - MACD cắt xuống Signal line")
        
        with tab_rsi:
            st.subheader("RSI (Relative Strength Index)")
            
            fig_rsi = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.6, 0.4]
            )
            
            # Giá
            fig_rsi.add_trace(
                go.Scatter(x=data.index, y=data['Close'], name='Giá', line=dict(color='black')),
                row=1, col=1
            )
            
            # RSI
            fig_rsi.add_trace(
                go.Scatter(x=data.index, y=data['RSI'], name='RSI', line=dict(color='purple')),
                row=2, col=1
            )
            
            # Các vùng
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
            fig_rsi.add_hline(y=50, line_dash="dot", line_color="gray", row=2, col=1)
            
            fig_rsi.update_yaxes(title_text="Giá (₫)", row=1, col=1)
            fig_rsi.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)
            fig_rsi.update_layout(height=600, hovermode='x unified')
            
            st.plotly_chart(fig_rsi, use_container_width=True)
            
            # Phân tích RSI
            rsi_current = data['RSI'].iloc[-1]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("RSI Hiện tại", f"{rsi_current:.2f}")
            
            with col2:
                if rsi_current > 70:
                    st.error("🔴 VÙng QUÁ MUA (Overbought) - Cân nhắc bán")
                elif rsi_current < 30:
                    st.success("🟢 VÙng QUÁ BÁN (Oversold) - Cân nhắc mua")
                else:
                    st.info("⚪ VÙng TRUNG LẬP - Chờ tín hiệu rõ ràng")
        
        with tab_bb:
            st.subheader("Bollinger Bands")
            
            fig_bb = go.Figure()
            
            # Bollinger Bands
            fig_bb.add_trace(go.Scatter(
                x=data.index, y=data['BB_Upper'],
                name='BB Upper',
                line=dict(color='gray', width=1, dash='dash'),
                showlegend=True
            ))
            
            fig_bb.add_trace(go.Scatter(
                x=data.index, y=data['BB_Lower'],
                name='BB Lower',
                line=dict(color='gray', width=1, dash='dash'),
                fill='tonexty',
                fillcolor='rgba(128, 128, 128, 0.2)',
                showlegend=True
            ))
            
            fig_bb.add_trace(go.Scatter(
                x=data.index, y=data['BB_Middle'],
                name='BB Middle (SMA20)',
                line=dict(color='orange', width=1, dash='dot')
            ))
            
            fig_bb.add_trace(go.Scatter(
                x=data.index, y=data['Close'],
                name='Giá đóng cửa',
                line=dict(color='blue', width=2)
            ))
            
            fig_bb.update_layout(
                title="Biểu đồ Bollinger Bands",
                xaxis_title="Ngày",
                yaxis_title="Giá (₫)",
                height=500,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_bb, use_container_width=True)
            
            # Phân tích
            current_price = data['Close'].iloc[-1]
            bb_upper = data['BB_Upper'].iloc[-1]
            bb_middle = data['BB_Middle'].iloc[-1]
            bb_lower = data['BB_Lower'].iloc[-1]
            bb_width = ((bb_upper - bb_lower) / bb_middle) * 100
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("BB Upper", f"{bb_upper:,.0f} ₫")
            
            with col2:
                st.metric("BB Middle", f"{bb_middle:,.0f} ₫")
            
            with col3:
                st.metric("BB Lower", f"{bb_lower:,.0f} ₫")
            
            with col4:
                st.metric("BB Width", f"{bb_width:.2f}%")
            
            # Vị trí giá
            if current_price > bb_upper:
                st.error("🔴 Giá Vượt TRÊN dải Bollinger - Cân nhắc bán")
            elif current_price < bb_lower:
                st.success("🟢 Giá Dưới DƯỚI dải Bollinger - Cân nhắc mua")
            else:
                st.info("⚪ Giá trong dải Bollinger - Trung lập")

# ============================================================================
# TAB 5: MÔ PHỎNG MONTE CARLO
# ============================================================================

def tab5_monte_carlo(ticker):
    st.title("🎲 Mô Phỏng Monte Carlo")
    
    if ticker == '-':
        st.info("👈 Vui lòng chọn mã cổ phiếu")
        return
    
    st.write(f"**Mã cổ phiếu:** {ticker} - {VN30_TICKERS.get(ticker, '')}")
    
    st.info("""
    📊 **Mô phỏng Monte Carlo** là phương pháp dự đoán giá cổ phiếu trong tương lai 
    dựa trên biến động lịch sử và phân phối xác suất ngẫu nhiên.
    """)
    
    # Tùy chọn
    col1, col2 = st.columns(2)
    
    with col1:
        n_simulations = st.selectbox(
            "Số lần mô phỏng",
            [200, 500, 1000, 2000],
            index=1
        )
    
    with col2:
        time_horizon = st.selectbox(
            "Thời gian dự đoán (ngày)",
            [30, 60, 90, 120],
            index=0
        )
    
    # Lấy dữ liệu
    data = get_stock_data_vn(ticker)
    
    if data is not None and not data.empty:
        # Tính toán
        close_prices = data['Close'].tail(60)  # Lấy 60 ngày gần nhất
        daily_returns = close_prices.pct_change().dropna()
        
        mean_return = daily_returns.mean()
        std_return = daily_returns.std()
        last_price = close_prices.iloc[-1]
        
        # Hiển thị thông tin
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Giá hiện tại", f"{last_price:,.0f} ₫")
        
        with col2:
            st.metric("Lợi nhuận TB/ngày", f"{mean_return*100:.3f}%")
        
        with col3:
            st.metric("Độ biến động/ngày", f"{std_return*100:.3f}%")
        
        # Chạy mô phỏng
        if st.button("🚀 Chạy Mô Phỏng", type="primary"):
            with st.spinner("Đang chạy mô phỏng..."):
                # Monte Carlo Simulation
                simulation_results = pd.DataFrame()
                
                np.random.seed(42)
                
                for i in range(n_simulations):
                    prices = [last_price]
                    
                    for _ in range(time_horizon):
                        random_return = np.random.normal(mean_return, std_return)
                        next_price = prices[-1] * (1 + random_return)
                        prices.append(next_price)
                    
                    simulation_results[i] = prices[1:]
                
                # Vẽ biểu đồ mô phỏng
                st.subheader("📈 Kết quả Mô Phỏng")
                
                fig_sim = go.Figure()
                
                # Vẽ một số đường mô phỏng (không vẽ hết để tránh rối)
                sample_sims = min(100, n_simulations)
                for i in range(sample_sims):
                    fig_sim.add_trace(go.Scatter(
                        y=simulation_results[i],
                        mode='lines',
                        line=dict(width=0.5),
                        opacity=0.3,
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                
                # Đường giá hiện tại
                fig_sim.add_hline(
                    y=last_price,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Giá hiện tại: {last_price:,.0f} ₫",
                    annotation_position="right"
                )
                
                fig_sim.update_layout(
                    title=f"Mô phỏng {n_simulations} kịch bản trong {time_horizon} ngày",
                    xaxis_title="Ngày",
                    yaxis_title="Giá (₫)",
                    height=500
                )
                
                st.plotly_chart(fig_sim, use_container_width=True)
                
                # Phân tích kết quả
                st.subheader("📊 Phân Tích Kết Quả")
                
                ending_prices = simulation_results.iloc[-1].values
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Giá trung bình dự đoán",
                        f"{ending_prices.mean():,.0f} ₫",
                        f"{((ending_prices.mean() / last_price - 1) * 100):+.2f}%"
                    )
                
                with col2:
                    st.metric(
                        "Giá cao nhất",
                        f"{ending_prices.max():,.0f} ₫",
                        f"{((ending_prices.max() / last_price - 1) * 100):+.2f}%"
                    )
                
                with col3:
                    st.metric(
                        "Giá thấp nhất",
                        f"{ending_prices.min():,.0f} ₫",
                        f"{((ending_prices.min() / last_price - 1) * 100):+.2f}%"
                    )
                
                # Value at Risk (VaR)
                st.subheader("⚠️ Value at Risk (VaR)")
                
                fig_var = go.Figure()
                
                fig_var.add_trace(go.Histogram(
                    x=ending_prices,
                    nbinsx=50,
                    name='Phân phối giá',
                    marker_color='lightblue'
                ))
                
                # Percentiles
                var_95 = np.percentile(ending_prices, 5)
                var_5 = np.percentile(ending_prices, 95)
                
                fig_var.add_vline(
                    x=var_95,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"5th percentile: {var_95:,.0f} ₫"
                )
                
                fig_var.add_vline(
                    x=var_5,
                    line_dash="dash",
                    line_color="green",
                    annotation_text=f"95th percentile: {var_5:,.0f} ₫"
                )
                
                fig_var.update_layout(
                    title="Phân phối Giá sau Mô phỏng",
                    xaxis_title="Giá (₫)",
                    yaxis_title="Tần suất",
                    height=400
                )
                
                st.plotly_chart(fig_var, use_container_width=True)
                
                # VaR calculations
                col1, col2 = st.columns(2)
                
                with col1:
                    var_loss = last_price - var_95
                    st.error(f"""
                    **📉 VaR 95% (Downside Risk)**
                    - Giá có thể giảm xuống: **{var_95:,.0f} ₫**
                    - Rủi ro thua lỗ: **{var_loss:,.0f} ₫** ({(var_loss/last_price*100):.2f}%)
                    - Xác suất: 5%
                    """)
                
                with col2:
                    var_gain = var_5 - last_price
                    st.success(f"""
                    **📈 VaR 95% (Upside Potential)**
                    - Giá có thể tăng lên: **{var_5:,.0f} ₫**
                    - Tiềm năng lợi nhuận: **{var_gain:,.0f} ₫** ({(var_gain/last_price*100):.2f}%)
                    - Xác suất: 5%
                    """)
                
                # Xác suất tăng/giảm
                st.subheader("📊 Xác Suất Biến Động")
                
                prob_increase = (ending_prices > last_price).sum() / n_simulations * 100
                prob_decrease = (ending_prices < last_price).sum() / n_simulations * 100
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.success(f"🟢 Xác suất giá TĂNG: **{prob_increase:.1f}%**")
                
                with col2:
                    st.error(f"🔴 Xác suất giá GIẢM: **{prob_decrease:.1f}%**")

# ============================================================================
# TAB 6: DANH MỤC ĐẦU TƯ
# ============================================================================

def tab6_portfolio(ticker):
    st.title("💼 Danh Mục Đầu Tư")
    
    st.info("""
    📊 Theo dõi hiệu suất của danh mục đầu tư VN30 của bạn.
    Chọn nhiều mã cổ phiếu để so sánh xu hướng giá.
    """)
    
    # Chọn cổ phiếu
    selected_tickers = st.multiselect(
        "Chọn các mã cổ phiếu trong danh mục",
        options=list(VN30_TICKERS.keys()),
        default=['VCB', 'VIC', 'VHM', 'HPG'],
        format_func=lambda x: f"{x} - {VN30_TICKERS[x]}"
    )
    
    if not selected_tickers:
        st.warning("⚠️ Vui lòng chọn ít nhất một mã cổ phiếu")
        return
    
    # Khoảng thời gian
    period = st.selectbox(
        "Khoảng thời gian",
        ['1 tháng', '3 tháng', '6 tháng', '1 năm', '3 năm', '5 năm'],
        index=3
    )
    
    if period == '1 tháng':
        start_date = datetime.now() - timedelta(days=30)
    elif period == '3 tháng':
        start_date = datetime.now() - timedelta(days=90)
    elif period == '6 tháng':
        start_date = datetime.now() - timedelta(days=180)
    elif period == '1 năm':
        start_date = datetime.now() - timedelta(days=365)
    elif period == '3 năm':
        start_date = datetime.now() - timedelta(days=365*3)
    else:
        start_date = datetime.now() - timedelta(days=365*5)
    
    # Lấy dữ liệu cho tất cả các mã
    portfolio_data = pd.DataFrame()
    
    with st.spinner("Đang tải dữ liệu..."):
        for tick in selected_tickers:
            data = get_stock_data_vn(tick, start_date=start_date)
            if data is not None and not data.empty:
                portfolio_data[tick] = data['Close']
    
    if portfolio_data.empty:
        st.error("Không thể tải dữ liệu danh mục")
        return
    
    # Chuẩn hóa về 100 để so sánh
    normalized_data = (portfolio_data / portfolio_data.iloc[0]) * 100
    
    # Vẽ biểu đồ
    st.subheader("📈 So Sánh Xu Hướng Giá")
    
    fig_portfolio = go.Figure()
    
    for col in normalized_data.columns:
        fig_portfolio.add_trace(go.Scatter(
            x=normalized_data.index,
            y=normalized_data[col],
            name=f"{col} - {VN30_TICKERS[col]}",
            mode='lines',
            line=dict(width=2)
        ))
    
    fig_portfolio.update_layout(
        title="Biểu đồ So sánh (Base 100)",
        xaxis_title="Ngày",
        yaxis_title="Chỉ số (Base = 100)",
        height=600,
        hovermode='x unified',
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.01)
    )
    
    st.plotly_chart(fig_portfolio, use_container_width=True)
    
    # Thống kê hiệu suất
    st.subheader("📊 Hiệu Suất Danh Mục")
    
    returns = portfolio_data.pct_change().dropna()
    
    performance_stats = []
    
    for col in portfolio_data.columns:
        total_return = (portfolio_data[col].iloc[-1] / portfolio_data[col].iloc[0] - 1) * 100
        volatility = returns[col].std() * np.sqrt(252) * 100  # Annualized
        sharpe = (returns[col].mean() / returns[col].std()) * np.sqrt(252) if returns[col].std() != 0 else 0
        max_price = portfolio_data[col].max()
        min_price = portfolio_data[col].min()
        current_price = portfolio_data[col].iloc[-1]
        
        performance_stats.append({
            'Mã CK': col,
            'Tên': VN30_TICKERS[col],
            'Giá hiện tại': f"{current_price:,.0f} ₫",
            'Tổng lợi nhuận': f"{total_return:+.2f}%",
            'Cao nhất': f"{max_price:,.0f} ₫",
            'Thấp nhất': f"{min_price:,.0f} ₫",
            'Độ biến động': f"{volatility:.2f}%",
            'Sharpe Ratio': f"{sharpe:.2f}"
        })
    
    perf_df = pd.DataFrame(performance_stats)
    
    st.dataframe(
        perf_df.style.background_gradient(
            subset=['Tổng lợi nhuận'],
            cmap='RdYlGn',
            vmin=-50,
            vmax=50
        ),
        hide_index=True,
        use_container_width=True
    )
    
    # Ma trận tương quan
    st.subheader("🔗 Ma Trận Tương Quan")
    
    corr_matrix = returns.corr()
    
    fig_corr = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(title="Tương quan")
    ))
    
    fig_corr.update_layout(
        title="Ma trận Tương quan Lợi nhuận",
        height=500
    )
    
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Phân bổ rủi ro - lợi nhuận
    st.subheader("📊 Phân Bổ Rủi Ro - Lợi Nhuận")
    
    scatter_data = []
    for col in portfolio_data.columns:
        total_return = (portfolio_data[col].iloc[-1] / portfolio_data[col].iloc[0] - 1) * 100
        volatility = returns[col].std() * np.sqrt(252) * 100
        scatter_data.append({
            'Mã': col,
            'Lợi nhuận (%)': total_return,
            'Rủi ro (%)': volatility
        })
    
    scatter_df = pd.DataFrame(scatter_data)
    
    fig_scatter = px.scatter(
        scatter_df,
        x='Rủi ro (%)',
        y='Lợi nhuận (%)',
        text='Mã',
        size=[100] * len(scatter_df),
        color='Lợi nhuận (%)',
        color_continuous_scale='RdYlGn',
        title="Biểu đồ Rủi ro - Lợi nhuận"
    )
    
    fig_scatter.update_traces(textposition='top center')
    fig_scatter.update_layout(height=500)
    
    st.plotly_chart(fig_scatter, use_container_width=True)

# ============================================================================
# TAB 7: SO SÁNH VN30
# ============================================================================

def tab7_comparison(ticker):
    st.title("⚖️ So Sánh VN30")
    
    st.info("""
    📊 So sánh chi tiết các mã cổ phiếu VN30 về giá, khối lượng, 
    và các chỉ số kỹ thuật.
    """)
    
    # Chọn nhóm ngành
    sectors = {
        'Ngân hàng': ['ACB', 'BID', 'CTG', 'HDB', 'MBB', 'STB', 'TCB', 'TPB', 'VCB', 'VIB', 'VPB'],
        'Bất động sản': ['KDH', 'NVL', 'VHM', 'VIC', 'VRE'],
        'Công nghiệp': ['BCM', 'GAS', 'GVR', 'HPG', 'POW'],
        'Tiêu dùng': ['MWG', 'SAB', 'VNM', 'MSN', 'FPT'],
        'Dịch vụ': ['PLX', 'SSI', 'VJC', 'BVH']
    }
    
    selected_sector = st.selectbox(
        "Chọn nhóm ngành",
        options=['Tất cả'] + list(sectors.keys())
    )
    
    if selected_sector == 'Tất cả':
        available_tickers = list(VN30_TICKERS.keys())
    else:
        available_tickers = sectors[selected_sector]
    
    # Chọn mã để so sánh
    compare_tickers = st.multiselect(
        "Chọn mã để so sánh (tối đa 5)",
        options=available_tickers,
        default=available_tickers[:min(3, len(available_tickers))],
        format_func=lambda x: f"{x} - {VN30_TICKERS[x]}",
        max_selections=5
    )
    
    if not compare_tickers:
        st.warning("⚠️ Vui lòng chọn ít nhất một mã")
        return
    
    # Lấy dữ liệu
    comparison_data = {}
    
    with st.spinner("Đang tải dữ liệu..."):
        for tick in compare_tickers:
            data = get_stock_data_vn(tick)
            if data is not None and not data.empty:
                comparison_data[tick] = data
    
    if not comparison_data:
        st.error("Không thể tải dữ liệu")
        return
    
    # Bảng so sánh
    st.subheader("📊 Bảng So Sánh Chi Tiết")
    
    comparison_table = []
    
    for tick, data in comparison_data.items():
        current_price = data['Close'].iloc[-1]
        prev_price = data['Close'].iloc[-2] if len(data) > 1 else current_price
        change = current_price - prev_price
        change_pct = (change / prev_price) * 100
        
        # Tính các chỉ số
        returns = data['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252) * 100
        
        high_52w = data['High'].tail(252).max()
        low_52w = data['Low'].tail(252).min()
        
        avg_volume = data['Volume'].tail(30).mean()
        
        comparison_table.append({
            'Mã': tick,
            'Tên': VN30_TICKERS[tick][:20],
            'Giá': f"{current_price:,.0f}",
            'Thay đổi': f"{change:+,.0f}",
            '%': f"{change_pct:+.2f}%",
            'Cao 52w': f"{high_52w:,.0f}",
            'Thấp 52w': f"{low_52w:,.0f}",
            'KL TB': f"{avg_volume:,.0f}",
            'Volatility': f"{volatility:.2f}%"
        })
    
    comp_df = pd.DataFrame(comparison_table)
    
    st.dataframe(comp_df, hide_index=True, use_container_width=True)
    
    # Biểu đồ so sánh giá (normalized)
    st.subheader("📈 So Sánh Xu Hướng Giá (30 ngày)")
    
    fig_compare = go.Figure()
    
    for tick, data in comparison_data.items():
        recent_data = data.tail(30)
        normalized = (recent_data['Close'] / recent_data['Close'].iloc[0]) * 100
        
        fig_compare.add_trace(go.Scatter(
            x=recent_data.index,
            y=normalized,
            name=f"{tick}",
            mode='lines+markers',
            line=dict(width=2)
        ))
    
    fig_compare.update_layout(
        title="Biểu đồ So sánh 30 ngày (Base 100)",
        xaxis_title="Ngày",
        yaxis_title="Chỉ số",
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_compare, use_container_width=True)
    
    # So sánh khối lượng
    st.subheader("📊 So Sánh Khối Lượng Giao Dịch")
    
    fig_volume = go.Figure()
    
    for tick, data in comparison_data.items():
        recent_data = data.tail(30)
        
        fig_volume.add_trace(go.Bar(
            x=recent_data.index,
            y=recent_data['Volume'],
            name=f"{tick}",
            opacity=0.7
        ))
    
    fig_volume.update_layout(
        title="So sánh Khối lượng 30 ngày",
        xaxis_title="Ngày",
        yaxis_title="Khối lượng",
        height=400,
        barmode='group'
    )
    
    st.plotly_chart(fig_volume, use_container_width=True)
    
    # Biểu đồ radar so sánh
    st.subheader("🎯 Biểu Đồ Radar So Sánh")
    
    radar_data = []
    
    for tick, data in comparison_data.items():
        returns = data['Close'].pct_change().dropna()
        
        # Chuẩn hóa các chỉ số về thang 0-100
        total_return = (data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100
        volatility = returns.std() * np.sqrt(252) * 100
        avg_volume = data['Volume'].mean()
        momentum = (data['Close'].iloc[-1] / data['Close'].iloc[-30] - 1) * 100 if len(data) >= 30 else 0
        
        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1] if not rsi.empty else 50
        
        radar_data.append({
            'Mã': tick,
            'Lợi nhuận': min(max(total_return + 50, 0), 100),
            'Thanh khoản': min(avg_volume / 1000000, 100),
            'Momentum': min(max(momentum + 50, 0), 100),
            'RSI': current_rsi,
            'Ổn định': max(100 - volatility, 0)
        })
    
    # Tạo biểu đồ radar
    fig_radar = go.Figure()
    
    categories = ['Lợi nhuận', 'Thanh khoản', 'Momentum', 'RSI', 'Ổn định']
    
    for item in radar_data:
        fig_radar.add_trace(go.Scatterpolar(
            r=[item[cat] for cat in categories],
            theta=categories,
            fill='toself',
            name=item['Mã']
        ))
    
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title="Biểu đồ Radar So sánh",
        height=500
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    # Cấu hình trang
    st.set_page_config(
        page_title="VN30 FinDash",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .main {
            padding: 0rem 1rem;
        }
        .stMetric {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 5px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.image("https://via.placeholder.com/300x100/1e3a8a/ffffff?text=VN30+FinDash", use_container_width=True)
    
    st.sidebar.title("⚙️ Cấu hình")
    
    # Chọn mã cổ phiếu
    ticker_list = ['-'] + list(VN30_TICKERS.keys())
    
    ticker = st.sidebar.selectbox(
        "🔍 Chọn mã cổ phiếu",
        options=ticker_list,
        format_func=lambda x: f"{x} - {VN30_TICKERS.get(x, 'Chọn mã')}" if x != '-' else "-- Chọn mã --"
    )
    
    # Thông tin về mã đã chọn
    if ticker != '-':
        st.sidebar.success(f"✅ Đã chọn: **{ticker}**")
        st.sidebar.caption(VN30_TICKERS[ticker])
    
    st.sidebar.markdown("---")
    
    # Chọn tab
    selected_tab = st.sidebar.radio(
        "📑 Chọn chức năng",
        [
            "📊 Tổng quan",
            "📈 Biểu đồ nâng cao",
            "📊 Thống kê",
            "🔧 Phân tích kỹ thuật",
            "🎲 Monte Carlo",
            "💼 Danh mục đầu tư",
            "⚖️ So sánh VN30"
        ]
    )
    
    st.sidebar.markdown("---")
    
    # Thông tin
    st.sidebar.info("""
    **VN30 FinDash**
    
    Dashboard phân tích tài chính cho 30 cổ phiếu vốn hóa lớn nhất thị trường Việt Nam.
    
    **Tính năng:**
    - 📊 Theo dõi giá real-time
    - 📈 Biểu đồ kỹ thuật
    - 🎲 Mô phỏng Monte Carlo
    - 💼 Quản lý danh mục
    - ⚖️ So sánh cổ phiếu
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2024 VN30 FinDash")
    
    # Hiển thị tab được chọn
    if selected_tab == "📊 Tổng quan":
        tab1_summary(ticker)
    elif selected_tab == "📈 Biểu đồ nâng cao":
        tab2_chart(ticker)
    elif selected_tab == "📊 Thống kê":
        tab3_statistics(ticker)
    elif selected_tab == "🔧 Phân tích kỹ thuật":
        tab4_technical(ticker)
    elif selected_tab == "🎲 Monte Carlo":
        tab5_monte_carlo(ticker)
    elif selected_tab == "💼 Danh mục đầu tư":
        tab6_portfolio(ticker)
    elif selected_tab == "⚖️ So sánh VN30":
        tab7_comparison(ticker)

if __name__ == "__main__":
    main()

        