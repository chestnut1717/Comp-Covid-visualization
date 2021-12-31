import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import json


plt.rcParams['font.family'] = 'Malgun Gothic'
sns.set(font="Malgun Gothic", 
rc={"axes.unicode_minus":False}, style='whitegrid')

# 필요한 함수 정의
## top, down value 반환 함수
def value_make(values, top):
    val_name = []
    val_value = []
    
    if top:
        for val, index in zip(values, values.index):
            if val <= 0 or val == float("inf"):
                break
            else:
                val_name.append(index)
                val_value.append(round(val, 1))
    
    else:
        for val, index in zip(values, values.index):
            if val > 0 or type(val) == -float("inf"):
                break
            else:
                val_name.append(index)
                val_value.append(round(val, 2))
    
    return val_name, val_value


# 첫번째 추천 function
def custom_dashboard(data_b, age='B', job='A.전문직', sole='O'):
    garbage = data_b.columns[8:9]
    
    data_selected = data_b[(data_b['연령성별'] == age) & (data_b['직업'] == job) & (data_b['일인가구여부'] == sole)]
    data_selected = data_selected.drop(garbage, axis=1)

    data_selected_melt = data_selected.melt(id_vars=list(data_selected.columns[:8]) + ['id'], 
                    var_name="업종", 
                    value_name="이용횟수")



    data_selected_before = data_selected_melt[data_selected_melt['소비년월'] < 202011]
    data_selected_after = data_selected_melt[data_selected_melt['소비년월'] > 202011]

    groupby_before = data_selected_before.groupby(['업종']).sum()['이용횟수']
    groupby_after = data_selected_after.groupby(['업종']).sum()['이용횟수']

    # 업종별 ranking
    ranking = ( (groupby_after - groupby_before) / (groupby_before) * 100 ).sort_values()
    ranking.dropna(inplace=True)

    top_3 = ranking[-3:].sort_values(ascending=False)
    down_3 = ranking[:3]
    
    # st.write(ranking)
    
    top_3_name, top_3_value = value_make(top_3, top=True)
    down_3_name, down_3_value = value_make(down_3, top=False)

    
    return top_3_name, top_3_value, down_3_name, down_3_value

def color_selector(values, top):
    colors_blues = ["#70c4ff", "#8cd0ff", "#a1d8ff", "#b5e0ff", "#bfe4ff", "#cce9ff" ]
    colors_reds = ["#ff4136", "#ff5d54", "#ff7870", "#ff958f", "#ffada8", "#ffc5c2"]
    colors = []
    
    if top == True:
        colors_original = colors_blues
    else:
        colors_original = colors_reds
        
    for val in values:
        tmp = abs(val)
        if tmp >= 60:
            colors.append(colors_original[0])
        elif tmp >= 35 and tmp <60:
            colors.append(colors_original[1])

        elif tmp >= 20 and tmp <35:
            colors.append(colors_original[2])

        elif tmp >= 10 and tmp <20:
            colors.append(colors_original[3])

        elif tmp >= 5 and tmp <10:
            colors.append(colors_original[4])

        else:
            colors.append(colors_original[5])
    
    return colors

def dashboard_draw(top_3_name, top_3_value, top):
    if top == True:
        hover_text = '상승'
    else:
        hover_text = '하락'
        
    x_coor = [0.5, 2, 3]
    y_coor = [3, 2.9, 2.8]

    color = color_selector(top_3_value, top=top)
    size=[val**2 for val in top_3_value]
    # layout 그리기
    layout = go.Layout(
    plot_bgcolor="#FFF",  # Sets background color to white
    xaxis=dict(
        linecolor="#BCCCDC",  # Sets color of X-axis line
        showgrid=False,  # Removes X-axis grid lines
        visible= False,  # numbers below
        ),
    yaxis=dict( 
        linecolor="#BCCCDC",  # Sets color of Y-axis line
        showgrid=False,  # Removes Y-axis grid lines
        visible= False,  # numbers below
        ),
    hoverlabel=dict(
        font_size=16,
        font_family="Rockwell"
        )
    )

    fig = go.Figure(
        layout=layout,
        data=[go.Scatter(
        
        # text 및 원 위치할 좌표
        x = [x_coor[idx] for idx in range(len(top_3_value))],
        y = [y_coor[idx] for idx in range(len(top_3_value))],
        text = [round(val, 1) for val in top_3_value],
        # x=[0.5, 2, 3], y=[3, 2.9, 2.8], text=[round(val, 1) for val in top_3_value],
        
        mode='markers',
        marker=dict(
            # ['rgb(255, 65, 54)', 'rgb(255, 144, 14)', 'rgb(93, 164, 214)'],
            color=color,
            size=size,
            sizemode='area',
            sizeref=2.* max(size)/(180.**2),
            sizemin=20
        )
    )])
    
    for idx in range(len(top_3_value)):
        fig.add_annotation(
                    x=x_coor[idx], y=y_coor[idx],
                    text=f'<b>{top_3_name[idx]}</b> <br>({top_3_value[idx]}%)',
                    showarrow=False,

                    font=dict(
                    size=20 -(2*idx),
                    color="black"
                    ),
            )

        

    fig.update_traces(
        hovertemplate="<br>".join([
            f"{hover_text}" + ": %{text}%",
        ]),
    )

    return fig



# Streampli page

st.set_page_config(page_title="Dashboard for COVID 19", page_icon="🍎", layout="wide")

# layout
row_1, _ = st.columns(2)
row_2_1, row_2_2 = st.columns(2)
row_3_1, row_3_2 = st.columns(2)
    

with row_1:
    
    # 데이터 업로드
    data_b = pd.read_csv('./data/data_for_geo.csv')
    with open('./data/geo_korea.json', encoding='utf8') as f:
        geo_korea = json.load(f)
    
    business = sorted(data_b.columns[9:-1].unique())

    st.sidebar.title('지역/업종별 매출 분석')
    option_business= st.sidebar.selectbox('업종을 선택해주세요', tuple(business))
    
    st.title("지역/업종별 매출 분석")
    fig_map = px.choropleth_mapbox(data_b, geojson=geo_korea, locations='id', color=option_business,
                               color_continuous_scale="Blues",
                               range_color = (0,max(data_b[option_business])),
                               mapbox_style="carto-positron",
                               zoom=5.5, center={"lat": 36.0402, "lon": 127.4899},
                               opacity=1,
                               labels={'CNT':'CNT'},
                               animation_frame= '소비년월',
                               animation_group = 'id',
                               width=800,
                               height=600,
                              )
    fig_map.update_geos(fitbounds="locations", visible=False)
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map)    
    
        
        

    
data = pd.read_csv('./data/data_for_business.csv')

ages = sorted(data['연령성별'].unique())
jobs = sorted(data['직업'].unique())
ones = sorted(data['일인가구여부'].unique())



st.sidebar.title('맞춤형 매출 변화 분석')
st.sidebar.empty()
option_age= st.sidebar.selectbox('연령/성별을 선택해주세요', tuple(ages))
option_job= st.sidebar.selectbox('직업을 선택해주세요', tuple(jobs))
option_sole= st.sidebar.selectbox('1인가구 여부를 선택해주세요', tuple(ones))
       
with row_2_1:
    st.empty()
    st.title("맞춤형 매출 변화 분석")
top_3_name, top_3_value, down_3_name, down_3_value = custom_dashboard(data, option_age, option_job, option_sole)







with row_3_1:
    st.subheader('TOP 3 매출 상승 업종')
    if len(top_3_name) < 1:
        st.error("선택하신 조건에 만족하는 결과가 나오질 않습니다")

    else:
        fig = dashboard_draw(top_3_name, top_3_value, top=True)
        st.plotly_chart(fig, top=True)

with row_3_2:
    st.subheader('TOP 3 매출 하락 업종', )
    if len(down_3_name) < 1:
        st.error("선택하신 조건에 만족하는 결과가 나오질 않습니다")

    else:
        fig = dashboard_draw(down_3_name, down_3_value, top=False)
        st.plotly_chart(fig)


