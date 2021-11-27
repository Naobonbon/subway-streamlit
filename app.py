import pandas as pd
import altair as alt
import streamlit as st
import folium
from streamlit_folium import folium_static

# アプリタイトル
st.title('仙台市地下鉄乗客数見える化アプリ')

# サイドバー部分
st.sidebar.write("""
# 仙台市地下鉄乗客数
  以下のオプションから路線・地図に表示する年度を指定できます。
""")

st.sidebar.write("""
## 表示路線選択
""")

line_name = st.sidebar.radio(
    "表示する路線を選んでください：",
    ('南北線', '東西線'))

fy_list = {
    '南北線': ['2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019',
            '2020'], '東西線': ['2015', '2016', '2017', '2018', '2019', '2020']}

selected_fy = st.sidebar.selectbox(
    '地図に表示する年度を選んでください：',
    fy_list[line_name]
)

# CSVデータの読み込み
df = pd.read_csv('sendaysubway_passengers.csv', encoding='Shift-JIS')
mapdf = df[df['Line'] == line_name]

# Foliumで地図作成
sendai_map = folium.Map(location=[38.2677554, 140.8691498], zoom_start=12)

# CircleMarkerのマーカーの大きさ調整の重みづけ
weight = 0.000004

# 地図上にCircleMarkerを配置。乗客数10000000以上の場合は特別な表示（サークルが大きくなりすぎるので）
for index, r in mapdf.iterrows():
    folium.CircleMarker(location=[r['Lat'], r['Lon']],
                        radius=r[selected_fy] * weight if r[selected_fy] < 10000000 else 18,
                        popup=[r['Station'], str(r[selected_fy]) + '人'],
                        color='#3186cc' if r[selected_fy] < 10000000 else '#ff4d4d',
                        fill_color='#3186cc' if r[selected_fy] < 10000000 else '#ff4d4d',
                        ).add_to(sendai_map)

# 表・グラフとして表示するため、単年度のデータを取り出す
data = mapdf.loc[:,
       ['Station'] + fy_list[line_name]]

# 表データを表示
st.write(f'### {line_name} 年度別乗客数')
st.dataframe(data, height=550)

# 折れ線グラフを表示

melted_data = pd.melt(data, id_vars=['Station'], var_name='FY').rename(
    columns={'value': 'Passengers'}
)

ymin = 0
ymax = 16000000 if line_name == '南北線' else 7000000

chart = (
    alt.Chart(melted_data)
        .mark_line(opacity=0.8, clip=True)
        .encode(
        x="FY:O",
        y=alt.Y("Passengers:Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
        color='Station:N'
    )
)

st.altair_chart(chart, use_container_width=True)

# マッピングした地図を表示
st.write(f'### {line_name} {selected_fy}年度乗客数')
folium_static(sendai_map)
