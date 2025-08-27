import streamlit as st
from datetime import datetime

from tools import get_weather, get_forecast,plot_forecast_graph

from reactagent import reactagent
from tts import text_to_speech


# Set page config
st.set_page_config(page_title="Weather Assistant", page_icon="🌤️", layout="wide")

# Title and description
st.markdown("""
    <h1 style='text-align: center; color: #4f8bf9;'>🌤️ Weather Assistant</h1>
    <p style='text-align: center; font-size: 18px;'>Your AI-powered weather sidekick ☁️</p>
    """, unsafe_allow_html=True)

# Initialize agent in session state
if "agent" not in st.session_state:
    st.session_state.agent = reactagent           #select agent    

# Initialize session state for play audio
# Ensure session state for TTS
if "last_ai_response" not in st.session_state:
    st.session_state.last_ai_response = None
if "last_voice_id" not in st.session_state:
    st.session_state.last_voice_id = None


# Define layout columns
col1, col2 = st.columns([ 1, 1], gap="medium")


with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1779/1779940.png", width=100)
    st.header("🔧 Voice Settings")
    voice_option = st.selectbox("🗣️ Choose Voice", ("Scott", "Rachel", "Bella", "Antoni", "Daniel"))
    voice_map = {
        "Scott": "scott",
        "Rachel": "21m00Tcm4TlvDq8ikWAM",  # Backward compatibility
        "Bella": "EXAVITQu4vr4xnSDxMaL",   # Backward compatibility
        "Antoni": "AZnzlk1XvdvUeBnXmlld",  # Backward compatibility
        "Daniel": "IKne3meq5aSn9XLyUdCD"   # Backward compatibility
    }
    selected_voice_id = voice_map[voice_option]
    st.session_state.last_voice_id = selected_voice_id
    st.caption("🌍 Powered by Speechify")

# --------------------------
# 🧾 Current Weather Section
# --------------------------
with col1:
    st.markdown("---")
    st.markdown("<h3 style='text-align: center; color: #6BB9F0;'>🧾 Get Current Weather Report</h3>", unsafe_allow_html=True)

    with st.form('current_weather_form'):
        city = st.text_input('Enter city name:')
        if st.form_submit_button("Get Current Weather"):
            if city.strip():
                data = get_weather(city.strip())["report"]
                if data == 'error getting current weather':
                    st.error("❌ Error fetching weather data. Please try again.")
                else:
                    st.success(f"Current weather for {city.title()}:")
                    lines = data.split('\n')
                    for line in lines:
                        st.markdown(f"- {line}")
            else:
                st.warning("Please enter a city name.")

# --------------------------
# 📅 Forecast Section
# --------------------------

st.markdown("---")
st.markdown("<h3 style='text-align: center; color: #6BB9F0;'>📅 Get Weather Forecast</h3>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center; color: #BCC6CC;'>5-day forecast (3-hour intervals)</h5>", unsafe_allow_html=True)

with st.form('forecast_form'):
    forecast_city = st.text_input('Enter city name for forecast:')
    interval_count = st.slider("Select number of intervals to display", min_value=1, max_value=40, value=10)
    submitted = st.form_submit_button("Get Forecast")

    if submitted:
        if forecast_city.strip():
            forecast_data = get_forecast(forecast_city.strip())
            if "parsed" in forecast_data:
                # Save to session state to persist after rerun
                st.session_state.forecast_city = forecast_city.strip()
                st.session_state.interval_count = interval_count
                st.session_state.forecast_data = forecast_data
                st.session_state.forecast_key = f"forecast_plot_{forecast_city.strip()}_{interval_count}"
            else:
                st.error("❌ Could not retrieve forecast data.")
        else:
            st.warning("Please enter a city name.")

# 🔁 Persist and display after rerun
if "forecast_data" in st.session_state:
    forecast_data = st.session_state.forecast_data
    interval_count = st.session_state.interval_count
    forecast_city = st.session_state.forecast_city
    plot_key = st.session_state.forecast_key

    st.success(f"Weather forecast for {forecast_city.title()}:")
    for item in forecast_data["parsed"][:interval_count]:
        st.markdown(f"📌 **{item['datetime']}**: {item['description']}, **{item['temp']}°C**, humidity - **{item['humidity']}%**")

    # Plot below the list
    plot_forecast_graph(forecast_data["parsed"], limit=interval_count, key=plot_key)


# --------------------------
# 🤖 Weather Assistant Chat
# --------------------------
with col2:
    st.markdown("---")
    st.markdown("<h3 style='text-align: center; color: #6BB9F0;'>🤖 Ask Weather Assistant</h3>", unsafe_allow_html=True)

    user_input = st.chat_input("Ask about weather, forecast ⛅")
    if user_input:
        st.chat_message("user").markdown(user_input)
        st.session_state.last_user_input = user_input 
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.agent.invoke({"input": user_input})
                ai_response = response.get("output", "Sorry, I couldn't understand that.")
                st.session_state.last_ai_response = ai_response
                st.chat_message("assistant").markdown(ai_response)

                
            except Exception as e:
                st.error(f"⚠️ Error: {str(e)}")
                st.session_state.last_ai_response = f"⚠️ Error: {str(e)}"
    
    if st.session_state.last_ai_response and st.session_state.last_voice_id:
        
        if st.button("🔊 Speak the Response"):
            st.chat_message("user").markdown(st.session_state.last_user_input)
            st.chat_message("assistant").markdown(st.session_state.last_ai_response)
            with st.spinner("🎧 Generating voice..."):
                audio = text_to_speech(
                    st.session_state.last_ai_response,
                    st.session_state.last_voice_id
                )
                if audio:
                    st.audio(audio, format="audio/mp3")
                else:
                    st.markdown("couldn't generate audio")
    
                