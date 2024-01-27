#Gói phần mềm ứng dụng cho tài chính môn
#Mã học phần: 	231CN0801
#Tên sinh viên: Vũ Đào Phương Quỳnh
#MSSV: K214142082
#Chủ đề: Phân tích tài chính CTCP Tập đoàn Bamboo Capital
#Import dữ liệu
import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import plost
warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from operator import itemgetter
import numpy as np
from tabulate import tabulate
import mpld3
import streamlit.components.v1 as components
#Thiết lập cấu hình trang
st.set_page_config(page_title="BCG COMPANY", page_icon=":boom:", layout="wide", initial_sidebar_state='expanded')
st.title("PHÂN TÍCH TÀI CHÍNH CTCP TẬP ĐOÀN BAMBOO CAPITAL - BCG")
#Thiết lập thanh Menu trái
st.sidebar.header('CHỌN LĨNH VỰC MUỐN PHÂN TÍCH')
st.markdown("""
<style>
    .block-container {
        padding-top: 3rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 3rem;
    }
    [data-testid="stMetricValue"] {
        font-size: 16px;
    }
    div[data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        border: 1px solid #9DB2BF;
        padding: 10px 10px 20px 10px;
        border-radius: 3px;
        color: #E4E3E3;
        overflow-wrap: break-word;
    }
</style>
""", unsafe_allow_html=True)
#Tạo thanh lựa chọn để chuyển hướng trang
select = st.sidebar.selectbox('Chọn lĩnh vực', ('Tài chính', 'Cổ phiếu'))
#Xử lý file dữ liệu
@st.cache_data
def load_data():
    #Load data stock
    filename = 'D:/Price-Vol VN 2015-2023.xlsx' #Xử lý dữ liệu file Giá và khối lượng
    price = pd.read_excel(filename, sheet_name='Price', engine='openpyxl')
    volume = pd.read_excel(filename, sheet_name='Volume', engine='openpyxl')
    Info1 = pd.read_excel(filename, sheet_name='Info', engine='openpyxl')
    # Lấy giá trị công ty BCG từ sheet price
    price1 = price.fillna(0)
    price1.Code = price1.Code.str.replace('VT:', '').str.replace('(P)', '')
    price2 = price1[price1['Code'] == 'BCG']
    price2 = price2.T
    price4 = price2.reset_index()
    price4.columns = ['Date', 'Close']
    # Loại bỏ các dòng có ít nhất một giá trị NaN
    price4 = price4.iloc[3:].reset_index(drop=True)
    # Lấy thông tin công ty BCG từ sheet Info
    Info1.Symbol = Info1.Symbol.str.replace('VT:', '')
    Info = Info1[Info1['Symbol'] == 'BCG'] #Trích dữ liệu BCG
    # Xử lý sheet Volume
    vl1 = volume.fillna(0)
    vl1.Code = vl1.Code.str.replace('VT:', '').str.replace('(VO)', '')
    vl= vl1[vl1['Code'] == 'BCG']
    vl = vl.T
    vl = vl.reset_index()
    vl = vl.iloc[3:].reset_index(drop=True)
    vl.columns = ['Date', 'Vol']
    price4['Vol'] = vl['Vol'] * 1
    #tải dữ liệu Báo cáo tài chính các năm
    VN2018 = pd.read_excel("D:/2018-Vietnam.xlsx")
    VN2019 = pd.read_excel("D:/2019-Vietnam.xlsx")
    VN2020 = pd.read_excel("D:/2020-Vietnam.xlsx")
    VN2021 = pd.read_excel("D:/2021-Vietnam.xlsx")
    VN2022 = pd.read_excel("D:/2022-Vietnam.xlsx")
    # Gộp các file dữ liệu BCTC thành 1 file
    inf = pd.concat([VN2018, VN2019, VN2020, VN2021, VN2022], ignore_index=True)
    inf = inf.iloc[7:].reset_index(drop=True)
    inf.columns = inf.iloc[0]
    inf = inf[1:]
    inf.reset_index(drop=True, inplace=True)
    inf = pd.DataFrame(inf)
    inf.columns = inf.columns.where(inf.columns.str.extract(r'\s*([^\n]+)\n', expand=False))
    inf.index.name = "Năm"
    df = inf[inf['Mã'] == 'BCG'] #Trích dữ liệu công ty BCG
    df = df.fillna(0)
    #Xử lý các ký tự không cần thiết trong tên cột
    df.columns = df.columns.str.replace(f'\nHợp nhất\nQuý: Hàng năm\nNăm: 2018', '')
    df.columns = df.columns.str.replace(f'\nĐơn vị: Triệu VND', '')
    df.columns = df.columns.str.replace("\n", " ")
    return filename, price, Info, volume, price1,price2,price4,vl1,vl,df,inf,Info1
filename, price, Info, volume, price1,price2, price4,vl1, vl,df,inf, Info1 = load_data()

#Thiết lập trang "Cổ phiếu"
if 'Cổ phiếu' in select:
    st.caption(
        """ Trang này sẽ đưa ra các thông tin về mã chứng khoán BCG của CTCP 
        Tập đoàn Bamboo Capital, đồng thời đưa ra thông tin so sánh với công ty khác"""
    )
    # Trích xuất dữ liệu thông tin
    database = ('Name', 'Full Name', 'Hist.', 'Exchange', 'Sector', 'Currency')
    data_values = (Info['Name'].iloc[0], Info['Full Name'].iloc[0], Info['Hist.'].iloc[0], Info['Exchange'].iloc[0],
                   Info['Sector'].iloc[0], Info['Currency'].iloc[0])
    #Thiết lập các cột
    col1, sp, col2 = st.columns([0.5,0.1, 2])
    with col1:
        st.subheader("Thông tin cơ bản")
        col1.metric("Name", data_values[0])
        col1.metric('Full Name', data_values[1])
        col1.metric('Hist.', data_values[2])
        col1.metric("Exchange", data_values[3])
        col1.metric("Sector", data_values[4])
        col1.metric('Currency', data_values[5])

        # Thiết lập thời gian tùy chỉnh
        price4['Date'] = pd.to_datetime(price4['Date'])
        startDate = pd.to_datetime(price4["Date"]).min()
        endDate = pd.to_datetime(price4["Date"]).max()
        # Getting the min and max date
        startDate = price4["Date"].min()
        endDate = price4["Date"].max()
    with col2:
        #Tạo Box chọn các loại chỉ báo kỹ thuật
        st.subheader("Chỉ báo kỹ thuật của công ty BCG")
        option = st.selectbox(
            "Chỉ báo kỹ thuật",
            ("MACD", "Bolliger Bands", "RSI","MA","Volume and Close price"))
        col3, col4 = st.columns([1,1])
        with col3:
            date1 = pd.to_datetime(st.date_input("Ngày bắt đầu", startDate))
        with col4:
            date2 = pd.to_datetime(st.date_input("Ngày kết thúc", endDate))
        price4 = price4[(price4["Date"] >= date1) & (price4["Date"] <= date2)].copy()
    with col2:
        #Tạo biểu đồ Volume and Close price
        def VolClo():
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=price4['Date'], y=price4['Vol'], name='Volume',
                                     marker=dict(color='#DAF7A6', opacity=0.7), mode='lines', fill='tozeroy'))
            fig.add_trace(go.Scatter(x=price4['Date'], y=price4['Close'], name='Close',
                       line=dict(color='#FC253B', width=1, shape='spline')))
            fig.update_layout(
                height=400,
                title=dict(
                    text='Volume and Close price of BCG',
                    x=0.3, y=0.95,
                    font=dict(family="Tahoma", size=25)),
                xaxis=dict(title='Date'),
                yaxis=dict(title='Price'),
                showlegend=True,
                legend=dict(x=0, y=1))
            st.plotly_chart(fig, use_container_width=True)
            st.divider()
        #Tạo biểu đồ MACD
        def Macd():
            price4['Close'] = price4['Close'].fillna(0)
            short_window = 12
            long_window = 26
            signal_line_window = 9

            # Tính giá trị
            price4['Short_MA'] = price4['Close'].rolling(window=short_window).mean()
            price4['Long_MA'] = price4['Close'].rolling(window=long_window).mean()
            price4['macd'] = price4['Short_MA'] - price4['Long_MA']
            price4['signal_line'] = price4['macd'].rolling(window=signal_line_window).mean()
            price4['macd_histogram'] = price4['macd'] - price4['signal_line']

            # Tạo hình ảnh chứa biểu đồ
            fig = go.Figure()

            # Thêm biểu đồ Volume
            fig.add_trace(go.Scatter(x=price4['Date'], y=price4['Vol'], name='Volume',
                                     marker=dict(color='#DAF7A6', opacity=0.7), mode='lines', fill='tozeroy'))

            # Thêm đường MACD
            fig.add_trace(go.Scatter(x=price4['Date'], y=price4['macd'], mode='lines', name='MACD',
                                     line=dict(color='red', width=0.75, shape='spline')))

            # Thêm đường Signal Line
            fig.add_trace(go.Scatter(x=price4['Date'], y=price4['signal_line'], mode='lines', name='Signal Line',
                                     line=dict(color='green', width=0.75, shape='spline')))

            # Thêm Histogram
            fig.add_trace(go.Scatter(x=price4['Date'], y=price4['macd_histogram'], name='Histogram',
                                     marker=dict(color='#86ADFC', opacity=0.7, ), mode='lines', fill='tozeroy'))
            fig.update_layout(yaxis2=dict(title='Volume', color='yellow', overlaying='y', side='right'))
            fig.update_layout(
                height=400,
                title=dict(
                    text='MACD of BCG',
                    x=0.4, y=0.95,
                    font=dict(family="Tahoma", size=30)),
                xaxis=dict(title='Date'),
                yaxis=dict(title='Price'),
                showlegend=True,
                legend=dict(x=0, y=1))
            st.plotly_chart(fig, use_container_width=True)
            st.divider()
        #Tạo biểu đồ Bolliger Bands
        def Bolliger_Bands():
            window = st.slider('Chiều dài dải băng', 1, 200, 25)
            ##Tính giá trị của Bolliger
            price4['Bollinger_Middle'] = price4['Close'].rolling(window=window).mean()
            price4['Bollinger_Std'] = price4['Close'].rolling(window=window).std()
            price4['Bollinger_Upper'] = price4['Bollinger_Middle'] + 2 * price4['Bollinger_Std']
            price4['Bollinger_Lower'] = price4['Bollinger_Middle'] - 2 * price4['Bollinger_Std']
            # Tạo layout
            fig = go.Figure()

            # Thêm trace cho đường Close
            fig.add_trace(go.Scatter(x=price4['Date'], y=price4['Close'], name='Close',
                                     line=dict(color='red', shape='spline', width=1),
                                     marker=dict(color='red', size=10)))
            # Add bar trace for volume
            fig.add_trace(go.Scatter(x=price4['Date'], y=price4['Vol'], name='Volume',
                                     marker=dict(color='#DAF7A6', opacity=0.7), mode='lines', fill='tozeroy'))

            # Thêm trace cho đường Bollinger Upper
            fig.add_trace(go.Scatter(x=price4['Date'], y=price4['Bollinger_Upper'], name='Bollinger Upper',
                                     line=dict(color='#4E86F6', shape='spline', width=0.75), mode='lines',
                                     legendgroup='group1',
                                     marker=dict(color='red', size=10), ))

            # Thêm trace cho đường Bollinger Lower
            fig.add_trace(go.Scatter(x=price4['Date'], y=price4['Bollinger_Lower'], name='Bollinger Lower',
                                     line=dict(color='#4E86F6', shape='spline', width=0.75), mode='lines',
                                     legendgroup='group1',
                                     marker=dict(color='red', size=10),
                                     fill='tonexty', fillcolor='rgba(0, 0, 255, 0.1)'))

            # Cập nhật layout
            fig.update_layout(
                height=400,
                title=dict(
                    text='Bolliger Bands of BCG',
                    x=0.3, y=0.95,
                    font=dict(family="Tahoma", size=30)),
                xaxis=dict(title='Date'),
                yaxis=dict(title='Price'),
                showlegend=True,
                legend=dict(x=0, y=1))  # Display the chart
            st.plotly_chart(fig, use_container_width=True)
            st.divider()
        #Tạo biểu đồ RSI
        def RSI():
            fig = go.Figure()
            # Tính toán các giá trị
            price4['Date'] = pd.to_datetime(price4['Date'])
            price4['Price Change'] = price4['Close'].diff()
            rsi_period = st.slider('Length of RSI PERIOD', 0, 200, 25)
            price4['Gain'] = price4['Price Change'].apply(lambda x: x if x > 0 else 0).rolling(window=rsi_period).mean()
            price4['Loss'] = -price4['Price Change'].apply(lambda x: x if x < 0 else 0).rolling(
                window=rsi_period).mean()
            # Calculate Relative Strength (RS) and Relative Strength Index (RSI)
            price4['RS'] = price4['Gain'] / price4['Loss']
            price4['RSI'] = 100 - (100 / (1 + price4['RS']))

            # Plot RSI line with overbought and oversold levels
            fig = px.line(price4, x='Date', y='RSI', labels={'value': 'RSI', 'variable': 'Technical Indicator'})
            fig.add_shape(
                dict(type='line', y0=70, y1=70, x0=price4['Date'].min(), x1=price4['Date'].max(),
                     line=dict(color='red', dash='dash'), ),
            )
            fig.add_shape(
                dict(type='line', y0=30, y1=30, x0=price4['Date'].min(), x1=price4['Date'].max(),
                     line=dict(color='green', dash='dash'), ),
            )

            # Cậo nhật layout
            fig.update_layout(
                height=400,
                title=dict(
                    text='Relative Strength Index (RSI)',
                    x=0.4, y=0.95,
                    font=dict(family="Time New Roman", size=30)),
                xaxis=dict(title='Date', tickformat='%Y-%m-%d'),
                yaxis=dict(title='Price'),
                showlegend=True,
                legend=dict(x=0, y=1))

            # Show the chart
            st.plotly_chart(fig, use_container_width=True)
            st.divider()
        #Tạo biểu đồ MA
        def MA():
            window1 = st.slider('Length of Window', 0, 200, 25)
            price4['MA'] = price4['Close'].rolling(window=window1).mean()
            fig = go.Figure()
            # Add scatter plot for original data
            fig.add_trace(
                go.Scatter(x=price4['Date'], y=price4['Close'], name='Close',
                          line=dict(color='#64F147', width=1, shape='spline')))
            fig.add_trace(
                go.Scatter(x=price4['Date'], y=price4['MA'], name=f'Moving Average {window1}',
                           line=dict(color='#650EEF', width=1, shape='spline')))
            fig.update_layout(
                height=400,
                title=dict(
                    text='Close and MA of BCG',
                    x=0.4,y=0.95,
                    font=dict(family="Time New Roman",size=30)),
                xaxis=dict(title='Date'),
                yaxis=dict(title='Price'),
                showlegend=True,
                legend=dict(x=0, y=1))
            st.plotly_chart(fig, use_container_width=True)
            st.divider()
    #kết hợp với lệnh if để đưa ra các loại biểu đồ tương ứng với lựa chọn đã chọn
        if 'MACD' in option:
            Macd()
        elif "Bolliger Bands" in option:
            Bolliger_Bands()
        elif "RSI" in option:
            RSI()
        elif "MA" in option:
            MA()
        elif "Volume and Close price" in option:
            VolClo()
    #Chuyên mục so sánh với công ty khác
    st.subheader("So sánh với công ty khác")
    ss1, ss2 = st.columns([1, 1])
    with ss1:
        option2 = st.selectbox(
            "Chọn chỉ báo",
            ("Close", "MA"),
            label_visibility="visible") #Thanh lựa chọn chỉ báo
    with ss2:
            option1 = st.selectbox(
                "Chọn công ty muốn so sánh",
                Info1['Symbol'],
                label_visibility="visible") #thanh lựa chọn công ty muốn so sánh
        # Xử lý dữ liệu công ty thứ 2
    price5 = price1[price1['Code'] == option1]
    price5 = price5.T
    price5 = price5.reset_index()
    price5.columns = ['Date', 'Close']
    price5 = price5.iloc[3:].reset_index(drop=True)
    second_price = price5['Close']
    #Tạo biểu đồ so sánh giá đóng cửa
    def close():
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(x=price4['Date'], y=price4['Close'], name='Close of BCG',
                           line=dict(color='skyblue', width=2, shape='spline')))
            fig.add_trace(
                go.Scatter(x=price4['Date'], y=price5['Close'], name=f'Close of {option1}',
                           line=dict(color='blue', width=2, shape='spline')))
            fig.update_layout(
                height=400,
                title=dict(
                    text=f'BCG VS {option1}',
                    x=0.4, y=0.95,
                    font=dict(family="Time New Roman", size=30)),
                xaxis=dict(title='Date'),
                yaxis=dict(title='Price'),
                showlegend=True,
                legend=dict(x=0, y=1))
            # Display the chart
            st.plotly_chart(fig, use_container_width=True)
            st.divider()
    #Tạo biểu đồ so sánh Giá trị trung bình
    def ma():
            fig = go.Figure()
            window2 = st.slider('Length of Window', 0, 200, 20)
            price5['MA'] = price5['Close'].rolling(window=window2).mean()
            price4['MA'] = price4['Close'].rolling(window=window2).mean()
            # Add trace for MACD line
            fig.add_trace(
                go.Scatter(x=price4['Date'], y=price4['MA'], name='MA of BCG',
                           line=dict(color='skyblue', width=2, shape='spline')))
            fig.add_trace(
                go.Scatter(x=price4['Date'], y=price5['MA'], name=f'MA of {option1}',
                           line=dict(color='blue', width=2, shape='spline')))
            fig.update_layout(
                height=400,
                title=dict(
                    text=f'BCG VS {option1}',
                    x=0.4, y=0.95,
                    font=dict(family="Time New Roman", size=30)),
                xaxis=dict(title='Date'),
                yaxis=dict(title='Price'),
                showlegend=True,
                legend=dict(x=0, y=1))
            # Display the chart
            st.plotly_chart(fig, use_container_width=True)
            st.divider()
    #Kết hợp lệnh If xuất giá trị tương ứng với lựa chọn ở trên
    if 'Close' in option2:
        close()
    if "MA" in option2:
        ma()
#Thiết lập trang "tài chính"
elif "Tài chính" in select:
    st.caption(
        """Ở trang này, Các chỉ số quan trọng liên quan đến doanh thu,
         lợi nhuận và tài sản của CTCP Tập đoàn Bamboo Capital trong những năm gần đây sẽ được giới thiệu và trình bày."""
    )

    # Thiết lập các cột
    col1, col2 = st.columns([2.25, 1.75])
    with col2:
        # Hiển thị subheader
        start_year, end_year = st.select_slider(
            'Điều chỉnh khoảng thời gian',
            options=[2018, 2019, 2020, 2021, 2022],
            value=(2018, 2022))
        df1 = df
        df1 = df1[(df1["Năm "] >= start_year) & (df1["Năm "] <= end_year)].copy()


    with col1:
        option1 = st.selectbox('Danh mục phân tích', ("Tài sản","Nguồn vốn","Chi phí",
                                                      "Kết quả kinh doanh", "Cân đối kế toán",
                                                      "Tăng trưởng doanh thu theo năm",
                                                      "Tăng trưởng lợi nhuận",
                                                      "Hiệu suất tài chính",
                                                      "Biên lợi nhuận năm",
                                                      "Dòng tiền theo năm"))
    col3, col4 = st.columns([2.25, 1.75])
    with col3:
        if "Tăng trưởng doanh thu theo năm" in option1:
            df1 = df1.sort_values(by='Năm ')
            # Tính tăng trưởng doanh thu
            df1['Tăng trưởng'] = df1['KQKD. Doanh thu thuần'].pct_change() * 100
            # Dữ liệu cho đường parabol
            x = np.array(df1['Năm '])
            y_parabol = -0.01 * (x - len(df1['Năm ']) / 2) ** 2 + 1000
            # Tạo đối tượng biểu đồ tương tác
            fig = go.Figure()
            # Thêm biểu đồ cột cho doanh thu thuần
            fig.add_trace(
                go.Bar(x=df1['Năm '], y=df1['KQKD. Doanh thu thuần'], name='Doanh thu thuần', marker_color='skyblue'))
            # Thêm đường tăng trưởng
            fig.add_trace(
                go.Scatter(x=df1['Năm '], y=df1['Tăng trưởng'], mode='lines+markers', name='Tăng trưởng', yaxis='y2',
                           line=dict(color='red')))
            # Cấu hình trục y phụ cho đường tăng trưởng
            fig.update_layout(yaxis2=dict(title='Tăng trưởng (%)', overlaying='y', side='right'))
            # Cấu hình giao diện tương tác
            fig.update_layout(
                title=dict(
                    text='Tăng trưởng doanh thu theo năm',
                    x=0.3, y=0.95,
                    font=dict(family="Tahoma", size=20)),
                xaxis_title='Năm ',
                yaxis_title='Doanh thu (đơn vị: tỷ đồng)'
            )
            # Hiển thị biểu đồ
            st.plotly_chart(fig, use_container_width=True)
            st.divider()
        elif "Tăng trưởng lợi nhuận" in option1:
            df1 = df1.sort_values(by='Năm ')
            # Tính tăng trưởng doanh thu
            df1['Tăng trưởng lợi nhuận'] = df1['KQKD. Cổ đông của Công ty mẹ'].pct_change() * 100
            # Dữ liệu cho đường parabol
            x = np.array(df1['Năm '])
            y_parabol = -0.01 * (x - len(df1['Năm ']) / 2) ** 2 + 1000
            # Tạo đối tượng biểu đồ tương tác
            fig = go.Figure()
            # Thêm biểu đồ cột cho doanh thu thuần
            fig.add_trace(
                go.Bar(x=df1['Năm '], y=df1['KQKD. Cổ đông của Công ty mẹ'], name='Lợi nhuận sau thuế của cổ đông công ty mẹ',
                       marker_color='skyblue'))
            # Thêm đường tăng trưởng
            fig.add_trace(
                go.Scatter(x=df1['Năm '], y=df1['Tăng trưởng lợi nhuận'], mode='lines+markers', name='Tăng trưởng', yaxis='y2',
                           line=dict(color='red')))
            # Cấu hình trục y phụ cho đường tăng trưởng
            fig.update_layout(yaxis2=dict(title='Tăng trưởng (%)', overlaying='y', side='right'))
            # Cấu hình giao diện tương tác
            fig.update_layout(
                title=dict(
                    text='Tăng trưởng lợi nhuận',
                    x=0.3, y=0.95,
                    font=dict(family="Tahoma", size=20)),
                xaxis_title='Năm ',
                yaxis_title='Lợi nhuận (đơn vị: tỷ đồng)'
            )
            # Hiển thị biểu đồ
            st.plotly_chart(fig, use_container_width=True)
            st.divider()
        elif "Biên lợi nhuận năm" in option1:
            #tính toán giá trị
            df1['Doanh thu thuần'] = df1['KQKD. Doanh thu thuần']
            df1['Lợi nhuận gộp'] = df1['KQKD. Lợi nhuận gộp về bán hàng và cung cấp dịch vụ']
            df1['EBITDA'] = df1['KQKD. Lợi nhuận thuần từ hoạt động kinh doanh']
            df1['Lợi nhuận sau thuế'] = df1['KQKD. Lợi nhuận sau thuế thu nhập doanh nghiệp']
            df1['Tỷ suất lợi nhuận gộp biên (%)'] = (df1['Lợi nhuận gộp'] / df1['Doanh thu thuần']) * 100
            df1['Tỷ lệ lãi EBITDA (%)'] = (df1['EBITDA'] / df1['Doanh thu thuần']) * 100
            df1['Tỷ suất sinh lợi trên doanh thu thuần (%)'] = (df1['Lợi nhuận sau thuế'] / df1[
                'Doanh thu thuần']) * 100
            fig = go.Figure()

            # Add traces for each profit margin with colors
            fig.add_trace(go.Scatter(x=df1['Năm '], y=df1['Tỷ suất lợi nhuận gộp biên (%)'],
                                     mode='lines+markers', name='Lợi Nhuận Gộp',
                                     line=dict(color='skyblue'), marker=dict(color='blue', size=10)))
            fig.add_trace(go.Scatter(x=df1['Năm '], y=df1['Tỷ lệ lãi EBITDA (%)'],
                                     mode='lines+markers', name='Lãi EBITDA',
                                     line=dict(color='green'), marker=dict(color='green', size=10)))
            fig.add_trace(go.Scatter(x=df1['Năm '], y=df1['Tỷ suất sinh lợi trên doanh thu thuần (%)'],
                                     mode='lines+markers', name='Lợi Nhuận Sau Thuế',
                                     line=dict(color='red'), marker=dict(color='red', size=10)))
            fig.update_layout(
                title=dict(
                    text='Biên lợi nhuận theo năm',
                    x=0.3, y=0.95,
                    font=dict(family="Tahoma", size=20)),
                xaxis_title='Năm ',
                yaxis_title='Tỷ suất lợi nhuận (%)'
            )
            # Hiển thị biểu đồ
            st.plotly_chart(fig, use_container_width=True)
            st.divider()
        elif "Kết quả kinh doanh" in option1:
            fig = go.Figure()
            # Thêm biểu đồ cột cho doanh thu thuần
            fig.add_trace(
                go.Bar(x=df1['Năm '], y=df1['KQKD. Doanh thu thuần'], name='Doanh thu (tỷ)', marker_color='skyblue'))
            fig.add_trace(
                go.Bar(x=df1['Năm '], y=df1['KQKD. Lợi nhuận sau thuế thu nhập doanh nghiệp'], name='Lợi nhuận (tỷ)',
                       marker_color='#C70039'))

            fig.update_layout(
                title=dict(
                    text='Kết quả kinh doanh theo năm',
                    x=0.3, y=0.95,
                    font=dict(family="Tahoma", size=20)),
                xaxis_title='Năm ',
                yaxis_title='Doanh thu (đơn vị: tỷ đồng)'
            )
            # Hiển thị biểu đồ
            st.plotly_chart(fig, use_container_width=True)
            st.divider()
        elif "Cân đối kế toán" in option1:
            df1['Nợ trên tài sản'] = (df1['CĐKT. NỢ PHẢI TRẢ'] / df1['CĐKT. TỔNG CỘNG TÀI SẢN']) * 100
            fig = go.Figure()
            fig.add_trace(
                go.Bar(x=df1['Năm '], y=df1['CĐKT. TỔNG CỘNG TÀI SẢN'], name='Tài sản (tỷ)', marker_color='skyblue'))
            fig.add_trace(
                go.Bar(x=df1['Năm '], y=df1['CĐKT. VỐN CHỦ SỞ HỮU'], name='Vốn CSH (tỷ)', marker_color='#C70039'))
            fig.add_trace(
                go.Bar(x=df1['Năm '], y=df1['CĐKT. NỢ PHẢI TRẢ'], name='Nợ phải trả', marker_color='#F6AC48'))
            fig.add_trace(go.Scatter(
                x=df1['Năm '],
                y=df1['Nợ trên tài sản'],
                mode='lines+markers',
                name='Nợ trên tài sản(%)',
                line=dict(color='red'),
                hovertemplate='%{y:.2f}%',
                yaxis='y2'  # Sử dụng trục y phụ
            ))
            # Đặt trục y phụ cho giá trị 'Nợ trên tài sản'
            fig.update_layout(
                yaxis2=dict(
                    title='Nợ trên tài sản (%)',
                    overlaying='y',
                    side='right'
                )
            )
            fig.update_layout(
                title=dict(
                    text='Cân đối kế toán theo năm',
                    x=0.3, y=0.95,
                    font=dict(family="Tahoma", size=20)),
                xaxis_title='Năm ',
                yaxis_title='Doanh thu (đơn vị: tỷ đồng)'
            )

            # Hiển thị biểu đồ
            st.plotly_chart(fig, use_container_width=True)
            st.divider()
        elif "Dòng tiền theo năm" in option1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df1['Năm '],
                y=df1['LCTT. Lưu chuyển tiền tệ ròng từ các hoạt động sản xuất kinh doanh (TT)'],
                name='Lưu chuyển từ SXKD',
                line=dict(color='orange'),
                hovertemplate='%{y:.2f}%'
            ))
            fig.add_trace(go.Scatter(
                x=df1['Năm '],
                y=df1['LCTT. Lưu chuyển tiền tệ ròng từ hoạt động đầu tư (TT)'],
                name='Lưu chuyển từ đầu tư',
                line=dict(color='#3DF81F'),
                hovertemplate='%{y:.2f}%'
            ))
            fig.add_trace(go.Scatter(
                x=df1['Năm '],
                y=df1['LCTT. Lưu chuyển tiền tệ từ hoạt động tài chính (TT)'],
                name='Lưu chuyển từ tài chính',
                line=dict(color='#1D49AD'),
                hovertemplate='%{y:.2f}%'
            ))

            # Vẽ đường
            fig.add_trace(go.Scatter(
                x=df1['Năm '],
                y=df1['LCTT. Tiền và tương đương tiền cuối kỳ (TT)'],
                name='Tiền cuối kỳ',
                line=dict(color='#C70039')
            ))
            # Thiết lập tiêu đề và nhãn
            fig.update_layout(
                title=dict(
                    text='Dòng tiền theo năm',
                    x=0.3, y=0.95,
                    font=dict(family="Tahoma", size=20)),
                xaxis_title='Năm ',
                yaxis_title='Số tiền (tỷ đồng)',barmode='stack'
            )
            st.plotly_chart(fig, use_container_width=True)
            st.divider()
        elif "Hiệu suất tài chính" in option1:
            # Tính các chỉ số tài chính
            df1 = df1[pd.to_numeric(df1['Năm '], errors='coerce', downcast='integer').notnull()]

            # Chuyển đổi cột 'Năm\n' thành số nguyên
            df['Năm '] = df['Năm '].astype(int)

            # Tính lợi nhuận kế toán trước thuế và chi phí lãi vay
            df1['LNKT trước thuế và chi phí lãi vay'] = df1['KQKD. Tổng lợi nhuận kế toán trước thuế'] + df1[
                'KQKD. Trong đó: Chi phí lãi vay']
            # Phân tích khả năng sinh lời của doanh nghiệp sẽ tính các chỉ số như ROS, ROE, ROA
            df1['revenues'] = df1['KQKD. Doanh thu thuần'].tolist()
            df1['profit'] = df1['KQKD. Lợi nhuận sau thuế thu nhập doanh nghiệp'].tolist()
            df1['sumprofit'] = df1['CĐKT. TỔNG CỘNG TÀI SẢN'].tolist()
            df1['equity'] = df1['CĐKT. VỐN CHỦ SỞ HỮU'].tolist()
            # Tính tỉ suất lợi nhuận ròng ROS
            df1['ROA'] = (df1['profit'] / df1['sumprofit']) * 100
            df1['ROE'] = (df1['profit'] / df1['equity']) * 100
            df1['BEP'] = (df1['LNKT trước thuế và chi phí lãi vay'] / df1['CĐKT. TỔNG CỘNG TÀI SẢN']) * 100
            # Vẽ biểu đồ
            fig = go.Figure()
            # Biểu đồ đường cho tỉ lệ ROE
            fig.add_trace(go.Scatter(
                x=df1['Năm '],
                y=df1['ROE'],
                mode='lines+markers',
                name='ROE',
                line=dict(color='teal'),
                marker=dict(color='red', size=8),
                hovertemplate='%{y:.2f}%'
            ))
            # Biểu đồ đường cho tỉ lệ ROA
            fig.add_trace(go.Scatter(
                x=df1['Năm '],
                y=df1['ROA'],
                mode='lines+markers',
                name='ROA',
                line=dict(color='blue'),
                marker=dict(color='green', size=8),
                hovertemplate='%{y:.2f}%'
            ))
            # Biểu đồ đường cho tỉ lệ BEP
            fig.add_trace(go.Scatter(
                x=df1['Năm '],
                y=df1['BEP'],
                mode='lines+markers',
                name='BEP',
                line=dict(color='orange'),
                marker=dict(color='blue', size=8),
                hovertemplate='%{y:.2f}%'
            ))
            # Cài đặt layout
            fig.update_layout(
                title=dict(
                    text='Hiệu suất tài chính theo năm',
                    x=0.3, y=0.95,
                    font=dict(family="Tahoma", size=20)),
                xaxis_title='Năm ',
                yaxis_title='%'
            )
            # Hiển thị biểu đồ
            st.plotly_chart(fig, use_container_width=True)
            st.divider()
        elif "Chi phí" in option1:
            df1['Chi phí'] = -(df1['KQKD. Chi phí tài chính']+df1['KQKD. Chi phí bán hàng']+
                               df1['KQKD. Chi phí quản lý doanh  nghiệp'])
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['Chi phí'],
                name='Chi phí',
                marker_color='skyblue', width=0.5
            ))
            fig.update_layout(
                title=dict(
                    text=f'Chi phí của BCG từ {start_year} - {end_year}',
                    x=0.3, y=0.95,
                    font=dict(family="Tahoma", size=20)),
                xaxis=dict(title='Năm', tickmode='array', tickvals=df1['Năm '].tolist(),
                           ticktext=df1['Năm '].astype(str).tolist()),
                yaxis=dict(title='(Tỷ đồng)'),
            )
            st.plotly_chart(fig, use_container_width=True)
            st.divider()
        elif "Tài sản" in option1:
            st.markdown("&nbsp;")
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT. Tiền và tương đương tiền '],
                name='Tiền và tương đương tiền',
                marker_color='#43ECEF', width=0.4
            ))

            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT. Đầu tư tài chính ngắn hạn'],
                name='Đầu tư tài chính ngắn hạn',
                marker_color='#BF1ED1',
                base=df1['CĐKT. Tiền và tương đương tiền '], width=0.4
            ))

            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT. Các khoản phải thu ngắn hạn'],
                name='Các khoản phải thu ngắn hạn',
                marker_color='#73EFC1',
                base=df1['CĐKT. Đầu tư tài chính ngắn hạn'], width=0.4
            ))
            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT. Hàng tồn kho, ròng'],
                name='Hàng tồn kho',
                marker_color='#EE5C62',
                base=df1['CĐKT. Các khoản phải thu ngắn hạn'], width=0.4
            ))
            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT. Tài sản ngắn hạn khác'],
                name='Tài sản ngắn hạn khác',
                marker_color='#EE9F5C',
                base=df1['CĐKT. Hàng tồn kho, ròng'], width=0.4
            ))
            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT. Phải thu dài hạn'],
                name='Các khoản phải thu dài hạn',
                marker_color='#EEE85C',
                base=df1['CĐKT. Tài sản ngắn hạn khác'], width=0.4
            ))
            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT. Tài sản cố định'],
                name='Tài sản cố định',
                marker_color='#89EE5C',
                base=df1['CĐKT. Phải thu dài hạn'], width=0.4
            ))
            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT. Giá trị ròng tài sản đầu tư'],
                name='Bất động sản đầu tư',
                marker_color='#FFC300 ',
                base=df1['CĐKT. Tài sản cố định'], width=0.4
            ))
            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT. Đầu tư dài hạn'],
                name='Đầu tư tài chính dài hạn',
                marker_color='#0DF36E',
                base=df1['CĐKT. Giá trị ròng tài sản đầu tư'], width=0.4
            ))
            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT.Lợi thế thương mại'],
                name='Lợi thế thương mại',
                marker_color='#6E0DF3',
                base=df1['CĐKT. Đầu tư dài hạn'], width=0.4
            ))
            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT. Tài sản dài hạn khác'],
                name='Tài sản dài hạn khác',
                marker_color='#E10DF3',
                base=df1['CĐKT.Lợi thế thương mại'], width=0.4
            ))
            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT. Tài sản dở dang dài hạn'],
                name='Tài sản dở dang dài hạn',
                marker_color='#166FF2',
                base=df1['CĐKT. Tài sản dài hạn khác'], width=0.4
            ))
            fig.update_layout(
                title=dict(
                    text=f'Tài sản BCG {start_year} - {end_year}',
                    x=0.3, y=0.95,
                    font=dict(family="Tahoma", size=20)),
                xaxis_title='Năm ',
                yaxis_title='Số tiền (đơn vị: tỷ đồng)',
                barmode='stack'
            )
            st.plotly_chart(fig, use_container_width=True)
            st.divider()
        elif "Nguồn vốn" in option1:
            st.markdown("&nbsp;")
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT. Phải trả người bán ngắn hạn'],
                name='Phải trả người bán ngắn hạn',
                marker_color='#43ECEF', width=0.4
            ))
            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT. Người mua trả tiền trước ngắn hạn'],
                name='Người mua trả tiền trước ngắn hạn',
                marker_color='#BF1ED1',
                base=df1['CĐKT. Phải trả người bán ngắn hạn'], width=0.4
            ))
            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT. Phải trả nhà cung cấp dài hạn'],
                name='Phải trả nhà cung cấp dài hạn',
                marker_color='#73EFC1',
                base=df1['CĐKT. Người mua trả tiền trước ngắn hạn'], width=0.4
            ))
            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT. Vốn góp của chủ sở hữu'],
                name='Vốn góp của chủ sở hữu',
                marker_color='#EE5C62',
                base=df1['CĐKT. Phải trả nhà cung cấp dài hạn'], width=0.4
            ))
            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT. Thặng dư vốn cổ phần'],
                name='Thặng dư vốn cổ phần',
                marker_color='#EE9F5C',
                base=df1['CĐKT. Vốn góp của chủ sở hữu'], width=0.4
            ))
            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT.Vốn khác'],
                name='Vốn khác',
                marker_color='#EEE85C',
                base=df1['CĐKT. Thặng dư vốn cổ phần'], width=0.4
            ))
            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT. Lãi chưa phân phối'],
                name='Lãi chưa phân phối',
                marker_color='#89EE5C',
                base=df1['CĐKT.Vốn khác'], width=0.4
            ))
            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT. Vay và nợ thuê tài chính ngắn hạn'],
                name='Vay và nợ thuê tài chính ngắn hạn',
                marker_color='#FFC300 ',
                base=df1['CĐKT. Lãi chưa phân phối'], width=0.4
            ))
            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT. Vay và nợ thuê tài chính dài hạn'],
                name='Vay và nợ thuê tài chính dài hạn',
                marker_color='#0DF36E',
                base=df1['CĐKT. Vay và nợ thuê tài chính ngắn hạn'], width=0.4
            ))
            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT.Doanh thu chưa thực hiên dài hạn'],
                name='Doanh thu chưa thực hiên dài hạn',
                marker_color='#6E0DF3',
                base=df1['CĐKT. Vay và nợ thuê tài chính dài hạn'], width=0.4
            ))
            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT. Doanh thu chưa thực hiện ngắn hạn'],
                name='Doanh thu chưa thực hiện ngắn hạn',
                marker_color='#E10DF3',
                base=df1['CĐKT.Doanh thu chưa thực hiên dài hạn'], width=0.4
            ))
            fig.add_trace(go.Bar(
                x=df1['Năm '],
                y=df1['CĐKT. Người mua trả tiền trước dài hạn'],
                name='Người mua trả tiền trước dài hạn',
                marker_color='#166FF2',
                base=df1['CĐKT. Doanh thu chưa thực hiện ngắn hạn'], width=0.4
            ))
            fig.update_layout(
                title=dict(
                    text=f'Nguồn vốn BCG {start_year} - {end_year}',
                    x=0.3, y=0.95,
                    font=dict(family="Tahoma", size=20)),
                xaxis_title='Năm ',
                yaxis_title='Số tiền (đơn vị: tỷ đồng)',barmode='stack'
            )
            st.plotly_chart(fig, use_container_width=True)
            st.divider()
    with col4:
        if "Kết quả kinh doanh" in option1:
            st.markdown("<h4 style='text-align: center;'>Bảng dữ liệu</h4>", unsafe_allow_html=True)
            selected_columns1 = ['Năm ',
                                 'KQKD. Doanh thu thuần',
                                 'KQKD. Lợi nhuận gộp về bán hàng và cung cấp dịch vụ',
                                 'KQKD. Lợi nhuận thuần từ hoạt động kinh doanh',
                                 'KQKD. Lợi nhuận sau thuế thu nhập doanh nghiệp']
            selected_df = df1[selected_columns1]
            selected_df.columns = ['Năm', 'DT thuần', 'LN Gộp', 'LN từ HĐKD', 'NL sau Thuế']
            def shorten_value(x):
                if isinstance(x, (int, float)):
                    return f'{x / 1e9:.2f}B' if x >= 1e9 else f'{x / 1e6:.2f}M'
                else:
                    return x
            for column in selected_df.columns:
                if column != 'Năm':
                    selected_df[column] = selected_df[column].apply(shorten_value)
            selected_df = selected_df.reset_index(drop=True)
            st.table(selected_df)
        elif "Cân đối kế toán" in option1:
            def shorten_value(x):
                if isinstance(x, (int, float)):
                    if x >= 1e9:
                        return f'{x / 1e9:.2f}B'
                    elif x >= 1e6:
                        return f'{x / 1e6:.2f}M'
                    else:
                        return f'{x:.2f}'
                else:
                    return str(x)

            selected_columns2 = ['Năm ', 'CĐKT. TỔNG CỘNG TÀI SẢN', 'CĐKT. NỢ PHẢI TRẢ', 'CĐKT. VỐN CHỦ SỞ HỮU',
                                 'Nợ trên tài sản']
            selected_df1 = df1[selected_columns2]

            selected_df1.columns = ['Năm', 'Tài sản', 'Nợ phải trả', 'Vốn CSH', 'Nợ trên tài sản(%)']

            # Apply formatting to numerical columns
            for column in selected_df1.columns:
                if column != 'Năm' and column != 'Nợ trên tài sản':
                    selected_df1[column] = selected_df1[column].apply(shorten_value)
            # Reset index for display
            selected_df1 = selected_df1.reset_index(drop=True)
            # Display the formatted table
            st.markdown("<h4 style='text-align: center;'>Bảng dữ liệu</h4>", unsafe_allow_html=True)
            st.table(selected_df1)
        elif "Tăng trưởng doanh thu theo năm" in option1:
            st.markdown("<h4 style='text-align: center;'>Bảng dữ liệu</h4>", unsafe_allow_html=True)
            df1['Tăng trưởng']=df1['Tăng trưởng'].fillna(0)
            selected_columns3 = ['Năm ','KQKD. Doanh thu thuần',
                                 'Tăng trưởng']
            selected_df2 = df1[selected_columns3]
            selected_df2.columns = ['Năm','Doanh thu thuần', 'Tăng trưởng']
            def shorten_value(x):
                return f'{x / 1e9:.2f}B' if x >= 1e9 else f'{x / 1e6:.2f}M'
            selected_df2['Doanh thu thuần'] = selected_df2['Doanh thu thuần'].apply(shorten_value)
            selected_df2 = selected_df2.reset_index(drop=True)
            st.table(selected_df2)
        elif "Tăng trưởng lợi nhuận" in option1:
            st.markdown("<h4 style='text-align: center;'>Bảng dữ liệu</h4>", unsafe_allow_html=True)
            df1['Tăng trưởng lợi nhuận']=df1['Tăng trưởng lợi nhuận'].fillna(0)
            selected_columns3 = ['Năm ','KQKD. Cổ đông của Công ty mẹ',
                                 'Tăng trưởng lợi nhuận']
            selected_df2 = df1[selected_columns3]
            selected_df2.columns = ['Năm','Lợi nhuận sau thuế của cổ đông công ty mẹ', 'Tăng trưởng lợi nhuận']
            def shorten_value(x):
                return f'{x / 1e9:.2f}B' if x >= 1e9 else f'{x / 1e6:.2f}M'
            selected_df2['Lợi nhuận sau thuế của cổ đông công ty mẹ'] = selected_df2['Lợi nhuận sau thuế của cổ đông công ty mẹ'].apply(shorten_value)
            selected_df2 = selected_df2.reset_index(drop=True)
            st.table(selected_df2)
        elif "Chi phí" in option1:
            st.markdown("<h4 style='text-align: center;'>Bảng dữ liệu</h4>", unsafe_allow_html=True)
            selected_columns3 = ['Năm ',
                                 'Chi phí' ]
            selected_df2 = df1[selected_columns3]
            selected_df2.columns = ['Năm', 'Chi phí']
            def shorten_value(x):
                return f'{x / 1e9:.2f}B' if x >= 1e9 else f'{x / 1e6:.2f}M'
            selected_df2['Chi phí'] = selected_df2['Chi phí'].apply(shorten_value)
            selected_df2 = selected_df2.reset_index(drop=True)
            st.table(selected_df2)
        elif "Tài sản" in option1:
            col5, col6 = st.columns([1, 1])
            def DLTS():
                st.markdown("<h4 style='text-align: center;'>Bảng dữ liệu</h4>", unsafe_allow_html=True)
                selected_columns3 = ['Năm ',
                                     'CĐKT. Tiền và tương đương tiền ', 'CĐKT. Đầu tư tài chính ngắn hạn',
                                     'CĐKT. Các khoản phải thu ngắn hạn', 'CĐKT. Hàng tồn kho, ròng',
                                     'CĐKT. Tài sản ngắn hạn khác', 'CĐKT. Phải thu dài hạn',
                                     'CĐKT. Tài sản cố định', 'CĐKT. Giá trị ròng tài sản đầu tư',
                                     'CĐKT. Đầu tư dài hạn', 'CĐKT.Lợi thế thương mại',
                                     'CĐKT. Tài sản dài hạn khác', 'CĐKT. Tài sản dở dang dài hạn']
                selected_df2 = df1[selected_columns3]
                selected_df2.columns = ['Năm', 'Tiền và tương đương tiền', 'Đầu tư TC ngắn hạn',
                                        'Phải thu ngắn hạn', 'Hàng tồn kho', 'TS ngắn hạn khác',
                                        'Phải thu dài hạn', 'TS cố định', 'Bất động sản', 'Đầu tư dài hạn',
                                        'Lợi thế thương mại', 'TS dài hạn khác', 'TS dở dang dài hạn']

                def shorten_value(x):
                    if isinstance(x, (int, float)):
                        return f'{x / 1e9:.2f}B' if x >= 1e9 else f'{x / 1e6:.2f}M'
                    else:
                        return x

                for column in selected_df2.columns:
                    if column != 'Năm':
                        selected_df2[column] = selected_df2[column].apply(shorten_value)
                selected_df2 = selected_df2.reset_index(drop=True)
                st.table(selected_df2)
            with col6:
                on2 = st.toggle('Hiển thị Tài sản dài hạn')
            with col5:
                on1 = st.toggle('Hiển thị Tài sản ngắn hạn')
                if on1 and not on2:
                    with col4:
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT. Tiền và tương đương tiền '],
                            name='Tiền và tương đương tiền',
                            marker_color='#43ECEF', width=0.4
                        ))

                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT. Đầu tư tài chính ngắn hạn'],
                            name='Đầu tư tài chính ngắn hạn',
                            marker_color='#BF1ED1', width=0.4
                        ))

                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT. Các khoản phải thu ngắn hạn'],
                            name='Các khoản phải thu ngắn hạn',
                            marker_color='#73EFC1', width=0.4
                        ))
                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT. Hàng tồn kho, ròng'],
                            name='Hàng tồn kho',
                            marker_color='#EE5C62', width=0.4
                        ))
                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT. Tài sản ngắn hạn khác'],
                            name='Tài sản ngắn hạn khác',
                            marker_color='#EE9F5C', width=0.4
                        ))
                        fig.update_layout(
                            title=dict(
                                text=f'Tài sản ngắn hạn {start_year} - {end_year}',
                                x=0.3, y=0.95,
                                font=dict(family="Tahoma", size=20)),
                            xaxis_title='Năm ',
                            yaxis_title='Số tiền (đơn vị: tỷ đồng)',
                            barmode='stack'
                        )

                        st.plotly_chart(fig, use_container_width=True)
                        st.divider()
            with col6:
                if on2 and not on1:
                    with col4:
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT. Phải thu dài hạn'],
                            name='Các khoản phải thu dài hạn',
                            marker_color='#EEE85C', width=0.4
                        ))
                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT. Tài sản cố định'],
                            name='Tài sản cố định',
                            marker_color='#89EE5C', width=0.4
                        ))
                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT. Giá trị ròng tài sản đầu tư'],
                            name='Bất động sản đầu tư',
                            marker_color='#FFC300 ', width=0.4
                        ))
                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT. Đầu tư dài hạn'],
                            name='Đầu tư tài chính dài hạn',
                            marker_color='#0DF36E', width=0.4
                        ))
                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT.Lợi thế thương mại'],
                            name='Lợi thế thương mại',
                            marker_color='#6E0DF3', width=0.4
                        ))
                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT. Tài sản dài hạn khác'],
                            name='Tài sản dài hạn khác',
                            marker_color='#E10DF3', width=0.4
                        ))
                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT. Tài sản dở dang dài hạn'],
                            name='Tài sản dở dang dài hạn',
                            marker_color='#166FF2', width=0.4
                        ))
                        fig.update_layout(
                            title=dict(
                                text=f'Tài sản dài hạn {start_year} - {end_year}',
                                x=0.3, y=0.95,
                                font=dict(family="Tahoma", size=20)),
                            xaxis_title='Năm ',
                            yaxis_title='Số tiền (đơn vị: tỷ đồng)',
                            barmode='stack'
                        )

                        st.plotly_chart(fig, use_container_width=True)
                        st.divider()
            #Thiết lập hiển thị các bảng
            if not on1 and not on2:
                DLTS()
            if on1 and on2:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df1['Năm '],
                    y=df1['CĐKT. TÀI SẢN NGẮN HẠN'],
                    name='Tài sản ngắn hạn',
                    marker_color='#EEE85C', width=0.4
                ))
                fig.add_trace(go.Bar(
                    x=df1['Năm '],
                    y=df1['CĐKT. TÀI SẢN DÀI HẠN'],
                    name='Tài sản dài hạn',
                    marker_color='#166FF2', width=0.4
                ))
                fig.update_layout(
                    title=dict(
                        text=f'Tài sản ngắn và dài hạn {start_year} - {end_year}',
                        x=0.1, y=0.95,
                        font=dict(family="Tahoma", size=20)),
                    xaxis_title='Năm ',
                    yaxis_title='Số tiền (đơn vị: tỷ đồng)',
                    barmode='group'
                )

                st.plotly_chart(fig, use_container_width=True)
                st.divider()
        elif "Nguồn vốn" in option1:
            col5, col6 = st.columns([1, 1])
            def DLNV():
                # st.subheader("Bảng dữ liệu")
                st.markdown("<h4 style='text-align: center;'>Bảng dữ liệu</h4>", unsafe_allow_html=True)
                selected_columns5 = ['Năm ',
                                     'CĐKT. Phải trả người bán ngắn hạn','CĐKT. Người mua trả tiền trước ngắn hạn',
                                     'CĐKT. Phải trả nhà cung cấp dài hạn', 'CĐKT. Vốn góp của chủ sở hữu',
                                     'CĐKT. Thặng dư vốn cổ phần', 'CĐKT.Vốn khác', 'CĐKT. Lãi chưa phân phối',
                                     'CĐKT. Vay và nợ thuê tài chính ngắn hạn',
                                     'CĐKT. Vay và nợ thuê tài chính dài hạn',
                                     'CĐKT.Doanh thu chưa thực hiên dài hạn', 'CĐKT. Doanh thu chưa thực hiện ngắn hạn',
                                     'CĐKT. Người mua trả tiền trước dài hạn']

                selected_df3 = df1[selected_columns5]
                selected_df3.columns = ['Năm', 'Phải trả người bán ngắn hạn', 'Người mua trả tiền trước ngắn hạn',
                                        'Phải trả nhà cung cấp dài hạn', 'Vốn góp của chủ sở hữu', 'Thặng dư vốn cổ phần',
                                        'Vốn khác', 'Lãi chưa phân phối', 'Vay và nợ thuê tài chính ngắn hạn',
                                        'Vay và nợ thuê tài chính dài hạn',
                                        'Doanh thu chưa thực hiên dài hạn', 'Doanh thu chưa thực hiện ngắn hạn',
                                        'Người mua trả tiền trước dài hạn']

                def shorten_value(x):
                    if isinstance(x, (int, float)):
                        return f'{x / 1e9:.2f}B' if x >= 1e9 else f'{x / 1e6:.2f}M'
                    else:
                        return x

                for column in selected_df3.columns:
                    if column != 'Năm':
                        selected_df3[column] = selected_df3[column].apply(shorten_value)
                selected_df3 = selected_df3.reset_index(drop=True)
                st.table(selected_df3)
            with col6:
                on2 = st.toggle('Hiển thị Vốn chủ sở hữu')
            with col5:
                on1 = st.toggle('Hiển thị Nợ phải trả')
                if on1 and not on2:
                    with col4:
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT. Doanh thu chưa thực hiện ngắn hạn'],
                            name='Doanh thu chưa thực hiện ngắn hạn',
                            marker_color='#43ECEF', width=0.4
                        ))

                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT. Phải trả người bán ngắn hạn'],
                            name='Phải trả người bán ngắn hạn',
                            marker_color='#BF1ED1', width=0.4
                        ))

                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT. Người mua trả tiền trước ngắn hạn'],
                            name='Người mua trả tiền trước ngắn hạn',
                            marker_color='#73EFC1', width=0.4
                        ))
                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT. Vay và nợ thuê tài chính ngắn hạn'],
                            name='Vay và nợ thuê tài chính ngắn hạn',
                            marker_color='#EE5C62', width=0.4
                        ))
                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT. Phải trả nhà cung cấp dài hạn'],
                            name='Phải trả nhà cung cấp dài hạn',
                            marker_color='#EE9F5C', width=0.4
                        ))
                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT. Vay và nợ thuê tài chính dài hạn'],
                            name='Vay và nợ thuê tài chính dài hạn',
                            marker_color='#EEE85C', width=0.4
                        ))
                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT.Doanh thu chưa thực hiên dài hạn'],
                            name='Doanh thu chưa thực hiên dài hạn',
                            marker_color='#89EE5C', width=0.4
                        ))
                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT. Người mua trả tiền trước dài hạn'],
                            name='Người mua trả tiền trước dài hạn',
                            marker_color='#FFC300 ', width=0.4
                        ))

                        fig.update_layout(
                            title=dict(
                                text=f'Nợ phải trả {start_year} - {end_year}',
                                x=0.3, y=0.95,
                                font=dict(family="Tahoma", size=20)),
                            xaxis_title='Năm ',
                            yaxis_title='Số tiền (đơn vị: tỷ đồng)',
                            barmode='stack'
                        )

                        st.plotly_chart(fig, use_container_width=True)
                        st.divider()
            with col6:
                if on2 and not on1:
                    with col4:
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT. Vốn góp của chủ sở hữu'],
                            name='Vốn góp của chủ sở hữu',
                            marker_color='#6E0DF3', width=0.4
                        ))
                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT. Thặng dư vốn cổ phần'],
                            name='Thặng dư vốn cổ phần',
                            marker_color='#E10DF3', width=0.4
                        ))
                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT.Vốn khác'],
                            name='Vốn khác',
                            marker_color='#166FF2', width=0.4
                        ))
                        fig.add_trace(go.Bar(
                            x=df1['Năm '],
                            y=df1['CĐKT. Lãi chưa phân phối'],
                            name='Lãi chưa phân phối',
                            marker_color='skyblue', width=0.4
                        ))
                        fig.update_layout(
                            title=dict(
                                text=f'Vốn chủ sở hữu {start_year} - {end_year}',
                                x=0.3, y=0.95,
                                font=dict(family="Tahoma", size=20)),
                            xaxis_title='Năm ',
                            yaxis_title='Số tiền (đơn vị: tỷ đồng)',
                            barmode='stack'
                        )

                        st.plotly_chart(fig, use_container_width=True)
                        st.divider()
            #Thiết lập hiển thị các bảng
            if not on1 and not on2:
                DLNV()
            if on1 and on2:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df1['Năm '],
                    y=df1['CĐKT. VỐN CHỦ SỞ HỮU'],
                    name='Vốn chủ sở hữu',
                    marker_color='#EEE85C', width=0.4
                ))
                fig.add_trace(go.Bar(
                    x=df1['Năm '],
                    y=df1['CĐKT. NỢ PHẢI TRẢ'],
                    name='Nợ phải trả',
                    marker_color='#166FF2', width=0.4
                ))
                fig.update_layout(
                    title=dict(
                        text=f'Vốn chủ sở hữu và Nợ phải trả {start_year} - {end_year}',
                        x=0.1, y=0.95,
                        font=dict(family="Tahoma", size=20)),
                    xaxis_title='Năm ',
                    yaxis_title='Số tiền (đơn vị: tỷ đồng)',
                    barmode='group'
                )

                st.plotly_chart(fig, use_container_width=True)
                st.divider()
        elif "Biên lợi nhuận năm" in option1:
            st.markdown("<h4 style='text-align: center;'>Bảng dữ liệu</h4>", unsafe_allow_html=True)
            selected_columns4 = ['Năm ',
                                 'Tỷ suất lợi nhuận gộp biên (%)','Tỷ lệ lãi EBITDA (%)',
                                 'Tỷ suất sinh lợi trên doanh thu thuần (%)']
            selected_df2 = df1[selected_columns4]
            selected_df2.columns = ['Năm', 'Lợi nhuận gộp (%)', 'Lãi EBITDA (%)', 'Lợi nhuận sau thuế (%)']
            selected_df2 = selected_df2.reset_index(drop=True)
            st.table(selected_df2)
        elif "Hiệu suất tài chính" in option1:
            st.markdown("<h4 style='text-align: center;'>Bảng dữ liệu</h4>", unsafe_allow_html=True)
            selected_columns4 = ['Năm ',
                                 'ROA', 'ROE',
                                 'BEP']
            selected_df2 = df1[selected_columns4]
            selected_df2.columns = ['Năm', 'ROA (%)', 'BEP (%)', 'ROE (%)']
            selected_df2 = selected_df2.reset_index(drop=True)
            st.table(selected_df2)
        elif "Dòng tiền theo năm" in option1:
            st.markdown("<h4 style='text-align: center;'>Bảng dữ liệu</h4>", unsafe_allow_html=True)
            selected_columns3 = ['Năm ', 'LCTT. Lưu chuyển tiền tệ ròng từ các hoạt động sản xuất kinh doanh (TT)',
                                 'LCTT. Lưu chuyển tiền tệ ròng từ hoạt động đầu tư (TT)',
                                 'LCTT. Lưu chuyển tiền tệ từ hoạt động tài chính (TT)',
                                 'LCTT. Tiền và tương đương tiền cuối kỳ (TT)']
            selected_df2 = df1[selected_columns3]
            selected_df2.columns = ['Năm', 'Lưu chuyển từ SXKD', 'Lưu chuyển từ đầu tư','Lưu chuyển từ tài chính','Tiền cuối kỳ']
            def shorten_value(x):
                if isinstance(x, (int, float)):
                    return f'{x / 1e9:.2f}B' if x >= 1e9 else f'{x / 1e6:.2f}M'
                else:
                    return x
            for column in selected_df2.columns:
                if column != 'Năm':
                    selected_df2[column] = selected_df2[column].apply(shorten_value)
            selected_df2 = selected_df2.reset_index(drop=True)
            st.table(selected_df2)
    st.subheader("So sánh giữa hai năm")
    ss3, ss4, ss5 = st.columns([1, 0.5, 0.5])
    with ss3:
        compare1 = st.selectbox(
            "So sánh về:",
            ("Tỷ trọng Chi phí so với Doanh thu thuần",
             "Tỷ trọng Tài sản ngắn hạn và dài hạn trong Tổng tài sản"),
            label_visibility="visible")
    with ss4:
        compare2 = st.selectbox(
            "Lựa chọn năm thứ 1",
            df['Năm '],
            label_visibility="visible")
        df3 = df
        df3 = df3[df3["Năm "] == compare2].copy()
    with ss5:
        compare3 = st.selectbox(
            "Lựa chọn năm thứ 2",
            df['Năm '],
            label_visibility="visible")
        df4 = df
        df4 = df4[df4["Năm "] == compare3].copy()
    ss6, ss7 = st.columns([1, 1])
    with ss6:
        df3 = df3.fillna(0)
        if "Tỷ trọng Chi phí so với Doanh thu thuần" in compare1:
            # Tính tỷ trọng của 'KQKD. Chi phí quản lý doanh nghiệp' và 'KQKD. Chi phí bán hàng'
            df3['Chi phí quản lý'] = (-df3['KQKD. Chi phí quản lý doanh  nghiệp']) / df3['KQKD. Doanh thu thuần'] * 100
            df3['Chi phí bán hàng'] = (-df3['KQKD. Chi phí bán hàng']) / df3['KQKD. Doanh thu thuần'] * 100
            df3['Chi phí khác'] = 100 - df3['Chi phí quản lý'].astype(float) - df3['Chi phí bán hàng'].astype(float)
            # Thiết lập biểu đồ Pie Chart
            labels = ['Chi phí quản lý', 'Chi phí bán hàng', 'Chi phí khác']
            sizes = [df3['Chi phí quản lý'].iloc[0], df3['Chi phí bán hàng'].iloc[0], df3['Chi phí khác'].iloc[0]]
            explode = (0, 0.0, 0)  # chỉ "nổ" phần thứ 2 (tức là 'Tỷ trọng CP bán hàng')

            # Vẽ biểu đồ Pie Chart
            fig1, ax1 = plt.subplots(figsize=(4, 4))
            ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                    shadow=True, startangle=90)
            ax1.axis('equal')  # Đảm bảo tỷ lệ khía cạnh giống nhau để biểu đồ tròn
            plt.title(f"Biểu đồ tỷ trọng chi phí so với Doanh thu thuần năm {compare2}", y=1.08, fontsize=16,
                      fontstyle='oblique')

            # Hiển thị biểu đồ trong ứng dụng Streamlit
            st.pyplot(fig1)
        if "Tỷ trọng Tài sản ngắn hạn và dài hạn trong Tổng tài sản" in compare1:
            df3['Tài sản ngắn hạn'] = (df3['CĐKT. TÀI SẢN NGẮN HẠN']) / df3['CĐKT. TỔNG CỘNG TÀI SẢN'] * 100
            df3['Tài sản dài hạn'] = 100 - df3['Tài sản ngắn hạn']

            # Thiết lập biểu đồ Pie Chart
            labels = ['Tài sản ngắn hạn', 'Tài sản dài hạn']
            sizes = [df3['Tài sản ngắn hạn'].iloc[0], df3['Tài sản dài hạn'].iloc[0]]
            explode = (0, 0)  # chỉ "nổ" phần thứ 2 (tức là 'Tỷ trọng CP bán hàng')

            # Vẽ biểu đồ Pie Chart
            fig1, ax1 = plt.subplots(figsize=(4, 4))
            ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                    shadow=True, startangle=90)
            ax1.axis('equal')  # Đảm bảo tỷ lệ khía cạnh giống nhau để biểu đồ tròn
            plt.title(f"Tỷ trọng Tài sản ngắn hạn và dài hạn trong Tổng tài sản {compare2}", y=1.08, fontsize=16,
                      fontstyle='oblique')

            # Hiển thị biểu đồ trong ứng dụng Streamlit
            st.pyplot(fig1)
    with ss7:
        if "Tỷ trọng Chi phí so với Doanh thu thuần" in compare1:
            df4['Chi phí quản lý'] = (-df4['KQKD. Chi phí quản lý doanh  nghiệp']) / df4['KQKD. Doanh thu thuần'] * 100
            df4['Chi phí bán hàng'] = (-df4['KQKD. Chi phí bán hàng']) / df4['KQKD. Doanh thu thuần'] * 100
            df4['Chi phí khác'] = 100 - df4['Chi phí quản lý'].astype(float) - df4['Chi phí bán hàng'].astype(float)
            labels = ['Chi phí quản lý', 'Chi phí bán hàng', 'Chi phí khác']
            sizes = [df4['Chi phí quản lý'].iloc[0], df4['Chi phí bán hàng'].iloc[0], df4['Chi phí khác'].iloc[0]]
            explode = (0, 0.0, 0)  # chỉ "nổ" phần thứ 2 (tức là 'Chi phí bán hàng')

            # Vẽ biểu đồ Pie Chart với kích thước nhỏ
            fig1, ax1 = plt.subplots(figsize=(4, 4))
            ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                    shadow=True, startangle=90)
            ax1.axis('equal')  # Đảm bảo tỷ lệ khía cạnh giống nhau để biểu đồ tròn
            plt.title(f"Biểu đồ tỷ trọng chi phí so với Doanh thu thuần năm {compare3}", y=1.08, fontsize=16,
                      fontstyle='oblique')

            # Hiển thị biểu đồ trong ứng dụng Streamlit
            st.pyplot(fig1)
        if "Tỷ trọng Tài sản ngắn hạn và dài hạn trong Tổng tài sản" in compare1:
            df4['Tài sản ngắn hạn'] = (df4['CĐKT. TÀI SẢN NGẮN HẠN']) / df4['CĐKT. TỔNG CỘNG TÀI SẢN'] * 100
            df4['Tài sản dài hạn'] = 100 - df4['Tài sản ngắn hạn']

            # Thiết lập biểu đồ Pie Chart
            labels = ['Tài sản ngắn hạn', 'Tài sản dài hạn']
            sizes = [df4['Tài sản ngắn hạn'].iloc[0], df4['Tài sản dài hạn'].iloc[0]]
            explode = (0, 0)  # chỉ "nổ" phần thứ 2 (tức là 'Tỷ trọng CP bán hàng')

            # Vẽ biểu đồ Pie Chart
            fig1, ax1 = plt.subplots(figsize=(4, 4))
            ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                    shadow=True, startangle=90)
            ax1.axis('equal')  # Đảm bảo tỷ lệ khía cạnh giống nhau để biểu đồ tròn
            plt.title(f"Tỷ trọng Tài sản ngắn hạn và dài hạn trong Tổng tài sản {compare3}", y=1.08, fontsize=16,
                      fontstyle='oblique')

            # Hiển thị biểu đồ trong ứng dụng Streamlit
            st.pyplot(fig1)








