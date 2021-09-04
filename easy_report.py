#python3

# Import general modules
import logging
import pickle
import os.path
from os import environ as environ
import time
import datetime as dt
import json

# Pandas
import pandas as pd

# Plotly
import plotly.graph_objects as go

from random import randint

# Web server
import streamlit as st
import stSplashScreen as st_SS # use SessionState


###############################################################################################################
##################             MAIN             ###############################################################
###############################################################################################################

def main(filepath=None, cost_file=None):

    # StreamLit configuration
    st.set_page_config(
        page_title="Daily reports",
        page_icon="🦈", # "📯📦🧊🦈",
        layout="wide", #"centered",
        initial_sidebar_state="collapsed",)

    hide_streamlit_style = """
            <style>
            /* MainMenu {visibility: hidden;} */
            footer {visibility: hidden;}
            title  {
                visibility: hidden;
                position: relative;
                }
            title:after {
                visibility: visible;
                position: absolute;
                top: 0;
                left: 0;
                content: "New title";
                }
            footer:after {
                content:'Newtryton'; 
                visibility: visible;
                display: block;
                position: relative;
                #background-color: red;
                padding: 5px;
                top: 2px;
                }
            .rotate {
                animation: rotation 8s infinite linear;
                }
            .rotate2 {
                animation: rotation 1.81s infinite linear;
                }
            @keyframes rotation {
              from { transform: rotate(0deg); }
              to { transform: rotate(359deg); }
              }
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

    #### ————–—— check password  —————————————
    if not st_SS.ask_password(  password_text='Quick Report',
                                logo_file='report_visual.png',
                                logo_width='150px',
                                logo_text='Opertational report', 
                                logo_shadow=False):
        return # if password wrong

    ## Logout feature
    logout_button = st.empty()
    if logout_button.button('Logout'):  
        # st.write('Thank you!')
        result_ap = st_SS.ask_password(reset=True) # Reset typed password
        # logout_button = st.empty()
        logout_button.button('Start over')
        return
    #### ————————————————————————————————————

    #### ——————————— SELECT ANALYSIS TYPE
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

    ## Select what is working on
    selected_genre = None 
    index_store_file = "genre_index.idx"
    genres = [
            'Montly report', # 0
            'Weekly report', # 0
            'Daily report', # 0
        ]
    
    if os.path.isfile(index_store_file):
        with open(index_store_file,"r") as f:
            selected_genre = f.read() # update from file
    # st.write(f"BEFORE: {selected_genre}")
    
    genre_index = genres.index(selected_genre) if selected_genre else 0    

    genre = st.sidebar.radio( "Select Field of Analysis", genres, index=int(genre_index))


    ## save selected to a file.
    with open(index_store_file,"w") as f:
        f.write(genre)
    # st.write(f"AFTER: {genre}")
    
    ########## ——— WHAT WE ARE DOING NOW? 
    # st.sidebar.markdown("""---""", unsafe_allow_html=True)
    st.sidebar.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#0510F4A;" /> """, unsafe_allow_html=True)
    # st.sidebar.markdown(f"<H1>{genre}</H1>", unsafe_allow_html=True)
    st.sidebar.subheader(f'{genre}')
  
    ### Create a cashflow report
    cf_fields = ['Продажи', 'Прочие доходы', 'Комиссии', 'Расходы поставщикам', 'Зарплаты', 'Уплаченные проценты', 'Налоги', 'Прочие расходы',
                'Чистые денежные средства от основной деятельности',
                'Инвестиционные доходы', 'Инвестиционные расходы',
                'Чистые денежные средства от инветиционной деятельности',
                # 'Продажа долей/акций',
                'Поступлений по кредитам/займам',
                'Прочие денежные поступления (в т.ч. гранты)',
                'Уплаченные дивиденды',
                'Выплаченные  кредиты/займы',
                'Чистые денежные средства от финансовой деятельности',
                'Чистое изменение денежных средств',
                'Чистые денежные средства на начало периода',
                'Чистые денежные средства на конец периода',
                ]
    cf = pd.DataFrame(columns=['field', 'Week 1', 'Week 2', 'Week 3','Week 4'])
    cf['field'] = cf_fields
    cf.set_index(['field'], inplace=True)    

    ################### SELECTOR 
    if genre == 'Weekly report':
        ###################  ——————————————  ANALYSIS ————————————————  #############
        st.header("Weekly report")
        st.subheader('Отчет о движении средств')

        columns = st.beta_columns(3)
        for key in cf_fields:
            cf.loc[key,:] = [randint(128,1024) for x in range(len(cf.columns))] 

        # color = (cf[['Чистые денежные средства от финансовой деятельности']]).map({True: 'background-color: yellow', False: ''})
    
        colormap = {
            'Продажи': 'green',
            'Чистые денежные средства от основной деятельности' : 'gray',
            'Чистые денежные средства от инветиционной деятельности': 'gray',
            'Чистые денежные средства от инветиционной деятельности': 'gray',
            'Чистое изменение денежных средств': 'orange',
            }

        def custom_style(row):
            color = None
            if row.name in colormap.keys():
                color = colormap[row.name]
            return ['background-color: %s' % color]*len(row.values)

        columns[0].table(cf.style
                        .apply(custom_style, axis=1)
                        # .bar(subset=['Week 1',], color='lightgreen')
                        # .bar(subset=['Week 2',], color='orange')
                        )
        
        # for key in data:
        fig = go.Figure()
        # columns[1].write(cf.loc[['Продажи']].values.tolist()[0])
        fig.add_trace(go.Bar(
                # name=key,
                y=cf.loc[['Продажи']].values.tolist()[0],
                x=cf.columns,
                # width=widths,
                # offset=0,
                # customdata=np.transpose([labels, data[key]]),
                texttemplate="$%{y}"    ,#"%{y} x %{width} =<br>%{customdata[1]}",
                textposition="inside",
                textangle=0,
                textfont_color="white",
                # hovertemplate="<br>".join([
                    # "year: %{customdata[0]}",
                    # "total: $%{width:0,.0d}",
                    # "service: $%{y}",
                    # "area: %{customdata[1]}",
                # ])
            ))
        fig.update_traces(marker_color='green', marker_line_color='rgb(8,48,107)',
                  marker_line_width=1.5, opacity=0.9)

        fig.update_layout(
            title_text="Продажи",
            barmode="stack",
            uniformtext=dict(mode="hide", minsize=10),
        )
        columns[1].plotly_chart(fig)        

        return

        ###################  ——————————————  ANALYSIS ————————————————  #############
    elif genre == "Montly report":
        st.header("Montly report")
        st.write('Пока не реализован')
        return

    elif genre == "Daily report":
        st.header("Daily report")
        st.write('Пока не реализован')
        return


    return


if __name__ == '__main__':
    main()
    