import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
from datetime import timedelta


tree_icons=["🌲","🌳","🌴","🪴"]

impact = {"rode a public transport":85,"used my own tumbler":40,"recycled":1,"rode a car":-65, "rode a motorbike":-95,"used disposable paper items":-40,"used disposable plastic items":-20}
#edit the impact

st.sidebar.title("navigation")
view=st.sidebar.radio("select",("tracker","about global warming"))
goal=st.sidebar.number_input("set final goal", min_value=1000,step=100)


if view=="tracker":
    st.title("Eco Tracker")
    st.header("Your eco friendly tracker to help you save the planet")

    tab1,tab2,tab3=st.tabs(["record","analysis","garden"])

    with tab1:
        date=st.date_input("today's date")
        activity=st.selectbox("what did you do today?",["rode a public transport", "used my own tumbler","recycled","rode a car","rode a motorbike","used disposable paper items","used disposable plastic items"])
        count=st.number_input("how many times? (unit in g, km, number of times)", min_value=1, step=1)
        if st.button("save"):
            newdata= pd.DataFrame({"date":[date],"activity":[activity],"count":[count]})
            try:
                existing=pd.read_csv("activity_log.csv")
                df=pd.concat([existing,newdata],ignore_index=True)
            except:
                df = newdata

            df.to_csv("activity_log.csv",index=False)
            st.success("Activity saved")

    with tab2:
        try:
            df= pd.read_csv("activity_log.csv")
            df["impact(g)"]=df["activity"].map(impact)*df["count"]
            df["date"]=pd.to_datetime(df["date"])
            rpositive= df[df["impact(g)"]>0]
            rnegative= df[df["impact(g)"]<0]

            realtotal_saved=rpositive["impact(g)"].sum()
            realtotal_emitted=rnegative["impact(g)"].sum()

            st.markdown("progress challenge")
            progress=realtotal_saved/goal if goal>0 else 0
            progress=min(progress,1.0)
            st.progress(progress)
            st.markdown(f"{realtotal_saved}g / {goal}g saved")

            today=pd.to_datetime(date.today())
            today_df=df[(df["date"] == today)]
            yesterday=today-timedelta(days=1)
            yesterday_df=df[(df["date"]==yesterday)]
            todaypositive= today_df[today_df["impact(g)"]>0]
            todaynegative= today_df[today_df["impact(g)"]<0]
            yesterdaypositive= yesterday_df[yesterday_df["impact(g)"]>0]
            yesterdaynegative= yesterday_df[yesterday_df["impact(g)"]<0]

            totalsavedtoday=todaypositive["impact(g)"].sum()
            totalemittedtoday=todaynegative["impact(g)"].sum()
            totalsavedyesterday=yesterdaypositive["impact(g)"].sum()
            totalemittedyesterday=yesterdaynegative["impact(g)"].sum()

            if totalsavedtoday>=totalsavedtoday:
                st.metric("CO2 saved today:",f"{totalsavedtoday}",f"+{totalsavedtoday-totalsavedyesterday}g from yesterday")
            else:
                st.metric("CO2 saved today:",f"{totalsavedtoday}",f"-{totalsavedyesterday-totalsavedtoday}g from yesterday")
            if totalemittedtoday>totalemittedyesterday:
                st.metric("CO2 emitted today:",f"{totalemittedtoday}",f"+{totalemittedtoday-totalemittedyesterday}g from yesterday",delta_color="inverse")
            else:
                st.metric("CO2 emitted today:",f"{totalemittedtoday}",f"-{totalemittedyesterday-totalemittedtoday}g from yesterday",delta_color="inverse")
            st.markdown("___")

            st.markdown("set time range")
            startdate=st.date_input("start date",value=df["date"].min())
            enddate=st.date_input("end date",value=df["date"].max())

            filtered_df=df[(df["date"] >= pd.to_datetime(startdate)) & (df["date"]<=pd.to_datetime(enddate))]

            fpositive= filtered_df[filtered_df["impact(g)"]>0]
            fnegative= filtered_df[filtered_df["impact(g)"]<0]

            total_saved=fpositive["impact(g)"].sum()
            total_emitted=fnegative["impact(g)"].sum()

            col1,col2=st.columns(2)
            with col1:
                st.subheader(f"saved: {total_saved:.0f}g")
            with col2:
                st.subheader(f"emitted: {abs(total_emitted):.0f}g")
            
            st.markdown("CO2 saved by activity")
            if not fpositive.empty:
                pos_summary=fpositive.groupby("activity")["impact(g)"].sum()
                #st.bar_chart(pos_summary)
                fig_pos=go.Figure(go.Bar(
                    x=pos_summary.index,
                    y=pos_summary.values,
                    marker_color='DarkSeaGreen'
                ))
                fig_pos.update_layout(title="CO2 saved by activity")
                st.plotly_chart(fig_pos,use_container_width=True)
            else:
                st.write("no positive actions logged yet")

            st.markdown("CO2 emitted by activity")
            if not fnegative.empty:
                neg_summary=fnegative.groupby("activity")["impact(g)"].sum().abs()
                #st.bar_chart(neg_summary)
                fig_neg=go.Figure(go.Bar(
                    x=neg_summary.index,
                    y=neg_summary.values,
                    marker_color='LightCoral'
                ))
                fig_neg.update_layout(title="CO2 emitted by activity")
                st.plotly_chart(fig_neg,use_container_width=True)
            else:
                st.write("no negative actions logged yet")
            
            col3,col4=st.columns(2)
            with col3:
                if not fpositive.empty:
                    st.markdown("CO2 Saved daily")
                    pos_perday=fpositive.groupby("date")["impact(g)"].sum()
                    st.line_chart(pos_perday)
                else:
                    st.write("no positive actions logged yet")
            with col4:
                if not fnegative.empty:
                    st.markdown("CO2 Emitted daily")
                    neg_perday=fnegative.groupby("date")["impact(g)"].sum().abs()
                    st.line_chart(neg_perday)
                else:
                    st.write("no negative actions logged yet")


        except FileNotFoundError:
            col1,col2=st.columns(2)
            with col1:
                st.subheader(f"saved: 0g")
            with col2:
                st.subheader(f"emitted: 0g")  
            st.markdown("CO2 saved by activity")
            st.write("no positive actions logged yet")
            st.markdown("CO2 emitted by activity")
            st.write("no negative actions logged yet")
            col3,col4=st.columns(2)
            with col3:
                st.markdown("CO2 Saved daily")
                st.write("no positive actions logged yet")
            with col4:
                st.markdown("CO2 Emitted daily")
                st.write("no negative actions logged yet")
    
    with tab3:
        try:
            st.markdown("your impact visualisation")
            trees=int(total_saved//200)
            st.write(f"you've planted {trees} virtual trees! 🌳")

            if trees>0:
                trees_row=""
                for i in range(trees):
                    trees_row+=random.choice(tree_icons)+" "
                st.markdown(f"<div style='font-size:30px'>{trees_row}</div>",unsafe_allow_html=True)
            else:
                st.write("no trees yet - keep logging to grow your own forest")
            
            if total_saved >= 1000:
                st.image("forest.png",caption="you restored a forest!")
            elif total_saved>=500:
                st.image("grove.png",caption="you planted a grove!")
            elif total_saved>=200:
                st.image("tree.png",caption="you planted a tree!")
        
        except:
            st.markdown("your impact visualisation")
            st.write("no trees yet - keep logging to grow your own forest")

elif view=="about global warming":
    st.write("Global warming refers to the long-term increase in Earth's average surface temperature due to human activities, primarily the emission of greenhouse gases like carbon dioxide and methane. These gases trap heat in the atmosphere, leading to a range of environmental impacts. As global temperatures rise, we experience more frequent and severe weather events, such as hurricanes, droughts, and heatwaves. Additionally, the melting of polar ice caps and glaciers contributes to rising sea levels, threatening coastal communities and ecosystems.\n\nPreventing and reducing global warming is crucial for several reasons. Firstly, it directly affects biodiversity and the health of ecosystems. Many species face extinction as their habitats change or disappear due to climate shifts. Secondly, the economic implications are significant; industries reliant on stable weather patterns, such as agriculture and tourism, can suffer devastating losses. Moreover, addressing global warming promotes public health by reducing air pollution, which is linked to respiratory diseases. Ultimately, taking action against global warming is not only vital for the planet's future but also for ensuring a sustainable and healthy world for future generations.\n\nTogether, we have the power to create a sustainable future; every small action counts, and by working collectively, we can protect our planet for generations to come.")