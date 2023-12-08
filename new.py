import streamlit as st
import json
import requests
from datetime import datetime
import time
import math
from streamlit_extras.tags import tagger_component
import webcolors

# pip install streamlit-extras
# pip install webcolors

# Remove Burger and Footer
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 


footer = """
<style>
a:link , a:visited{
color: white;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: black;
color: white;
text-align: center;
}

</style>
<div class="footer">
<p>Developed by <a href="mailto:kaidtheinternetuser@gmail.com">Kaid</a>
</div>
"""

# <p>Developed by <a style='display: block; text-align: center;' href="https://www.heflin.dev/" target="_blank">Heflin Stephen Raj S</a></p>
st.markdown(footer, unsafe_allow_html=True) 

def hex_to_color_name(hex_code):
    try:
        color_name = webcolors.hex_to_name(hex_code)
        return color_name
    except ValueError:
        return "white"

st.title("Twitch Chat Log Check")

def layout_expander(streamername, data, username):
    with st.expander(streamername):
        if data:
            for item in data:
                timestamp = datetime.fromisoformat(item["timestamp"])
                formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                color = item['tags']['color']
                color_name = hex_to_color_name(color)
                st.write(f":grey[{formatted_timestamp}] :{color_name}[{username}]: {item['text']}")

def test(tagsliste):
    tagger_component("User Tags: ", tagsliste)

username = st.text_input("Enter Twitch User Name", value="")

website = "https://logs.ivr.fi/channel/"

data = {}
progressbarcount = 0
done = 0
tagsliste = []
found = 0

ph = st.empty()
with ph.container():
    test(tagsliste)
ph.empty()

if username:
    with open('streamers.json', 'r') as file:
        streamerliste = json.load(file)

    my_bar = st.progress(0, text="Search ...")
    index = 0
    for streamer in streamerliste["channels"]:
        index += 1

        # Progress Bar
        anteil = 1 / len(streamerliste["channels"]) * 100
        anteil = math.floor(anteil)
        progressbarcount = progressbarcount + anteil
        if index == (len(streamerliste["channels"])):
            progressbarcount = 100
        my_bar.progress(int(progressbarcount), text="Search ("+streamer["name"]+")...")

        try:
            # Führe get request durch
            response = requests.get(website + streamer["name"] + '/user/' + username, params={'json': 'json'})
            time.sleep(0.5)
            data = json.loads(response.text)

            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # TAG Searcher

            if data["messages"][0]["channel"] == "pokimane":
                if data["messages"][0]["tags"]["subscriber"] == "1":
                    tagsliste.append("pokimane sub")
                    found = 1
                if data["messages"][0]["tags"]["mod"] == "1":
                    tagsliste.append("pokimane mod")
                    found = 1
            
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if data:
                # Erstelle output.json
                
                #file_path = 'output'+str(index)+'.json'
                #with open(file_path, 'w') as json_file:
                #    json.dump(data, json_file, indent=4)
                #print(f'JSON data has been written to {file_path}')
                

                # Erstelle Layout
                layout_expander(streamer["name"],data["messages"], username)

        # Error Handling GET
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP-Fehler: {http_err}')
        except json.JSONDecodeError as json_err:
            print(username+": "+"Kein Chat gefunden bei: "+streamer["name"])
        except Exception as err:
            print(f'Allgemeiner Fehler: {err}')

    done = 1
    if done == 1:
        my_bar.empty()
        if found == 1:
            with ph.container():
                test(tagsliste)
        