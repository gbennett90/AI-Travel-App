import streamlit as st
import pandas as pd
import json
import requests
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up API key for Google Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Currency and timezone data for some cities
CURRENCY_DATA = {
    "Paris, France": "EUR (Euro)",
    "New York, USA": "USD (US Dollar)",
    "Tokyo, Japan": "JPY (Japanese Yen)",
    "Curacao": "ANG (Netherlands Antillean Guilder)",
    "London, UK": "GBP (British Pound Sterling)",
    "Sydney, Australia": "AUD (Australian Dollar)",
    "Dubai, UAE": "AED (United Arab Emirates Dirham)",
    "Rio de Janeiro, Brazil": "BRL (Brazilian Real)",
    "Cancun, Mexico": "MXN (Mexican Peso)"
}

TIMEZONE_DATA = {
    "Paris, France": "CET (Central European Time)",
    "New York, USA": "EST (Eastern Standard Time)",
    "Tokyo, Japan": "JST (Japan Standard Time)",
    "Curacao": "AST (Atlantic Standard Time)",
    "London, UK": "GMT (Greenwich Mean Time)",
    "Sydney, Australia": "AEST (Australian Eastern Standard Time)",
    "Dubai, UAE": "GST (Gulf Standard Time)",
    "Rio de Janeiro, Brazil": "BRT (Brasilia Time)",
    "Cancun, Mexico": "EST (Eastern Standard Time)"
}

def get_international_info(city):
    # Return currency and timezone for the city
    currency = CURRENCY_DATA.get(city, "Currency data not available.")
    timezone = TIMEZONE_DATA.get(city, "Time zone not available.")
    return currency, timezone


def get_ai_itinerary(city, interests, weather_data, budget, occasion, hotel_style, num_days, currency, timezone):
    st.info("Generating a personalized itinerary... please wait.")
    try:
        prompt = f"""
        Create a detailed {num_days}-day travel itinerary for a trip to {city}.
        The traveler is interested in {interests}.
        The budget for this trip is {budget}.
        The occasion for the trip is a {occasion}.
        They are looking for a {hotel_style} style of accommodation.
        The current weather forecast for {city} is {weather_data}.
        The local currency is {currency} and the time zone is {timezone}.

        The itinerary should be fun, creative, and take the weather, budget, and occasion into account.
        Please also include a small section at the end with a few basic phrases in the local language and a cultural tip.
        Return the response in Markdown format with clear headings for each day, and for morning, afternoon, and evening within each day.
        """

        model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
        response = model.generate_content(prompt)

        if response and response.text:
            return response.text
        else:
            return "Sorry, unable to generate itinerary right now."

    except Exception as e:
        st.error(f"AI integration error: {e}")
        return "Sorry, unable to generate itinerary right now."


def get_ai_image(city, interests):
    # Return a placeholder image URL
    return f"https://placehold.co/1024x576/1e88e5/ffffff?text=Travel+is+Calling!"


def fetch_external_data(city):
    st.info(f"Fetching weather data for {city}...")
    try:
        api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        if not api_key:
            st.error("OpenWeatherMap API key missing in .env file.")
            return "Weather data not available."

        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        return f"{temperature}°C with {weather_description}."
    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return "Weather data not available."


def generate_hotel_link(city):
    # Create Google Hotels search URL
    search_query = f"{city} hotels"
    url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}&tbm=lcl&tbs=lrf:!1m4!1u3!2m2!3m1!1e1!2m1!1e3!3sIAE,lf:1,lf_ui:6"
    return url


def generate_flight_link(city):
    # Create Google Flights search URL
    url = f"https://www.google.com/flights?q=Flights to {city.replace(' ', '+')}"
    return url


# Streamlit page setup
st.set_page_config(page_title="AI Travel Itinerary", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1e88e5;'>✨ Your Personal AI Travel Planner 🌍</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Tell me about your trip, and I’ll help plan it.</p>", unsafe_allow_html=True)
st.markdown("---")
st.write("Enter your destination, interests, and budget to get a custom itinerary.")

with st.sidebar:
    st.subheader("Your Travel Details")

    city_name = st.text_input("Destination City, State, or Country", placeholder="e.g., Paris, France")
    user_interests = st.text_input("Your Hobbies and Interests (comma-separated)", placeholder="e.g., Museums, Food Tours, Shopping")
    user_budget = st.text_input("Your Budget", placeholder="e.g., Mid-Range")
    user_occasion = st.text_input("Occasion for the Trip", placeholder="e.g., Family Vacation")
    user_hotel_style = st.text_input("Hotel Style", placeholder="e.g., Boutique Hotel")
    num_days = st.number_input("Number of Days", min_value=1, value=3)

    submitted = st.button("Generate Itinerary")

if submitted and city_name and user_interests and user_budget and user_occasion and user_hotel_style and num_days:
    with st.spinner('Creating your itinerary...'):
        external_data = fetch_external_data(city_name)
        currency, timezone = get_international_info(city_name)
        generated_image_url = get_ai_image(city_name, user_interests)
        itinerary = get_ai_itinerary(city_name, user_interests, external_data, user_budget, user_occasion, user_hotel_style, num_days, currency, timezone)

    st.subheader("Your Personalized Itinerary")
    if generated_image_url:
        st.image(generated_image_url, caption="Ready for your trip!")

    st.markdown(f"**Currency:** {currency}")
    st.markdown(f"**Time Zone:** {timezone}")
    st.markdown("---")

    st.markdown(itinerary)

    st.subheader("Booking Information")
    hotel_link = generate_hotel_link(city_name)
    flight_link = generate_flight_link(city_name)

    st.markdown(f"**Find Hotels:** [Search Hotels in {city_name}]({hotel_link})")
    st.markdown(f"**Find Flights:** [Search Flights to {city_name}]({flight_link})")

elif submitted:
    st.error("Please fill in all the details to generate an itinerary.")
