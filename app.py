import streamlit as st
import requests
from typing import Optional, List

# Configuration
API_BASE_URL = "http://localhost:8000"

# Enum options
GENDER_OPTIONS = ["Male", "Female", "Other"]
FITNESS_LEVEL_OPTIONS = ["Beginner", "Intermediate", "Advanced"]
GOAL_OPTIONS = ["Weight Loss", "Weight Gain", "Maintenance", "Muscle Building"]
DIET_PREFERENCE_OPTIONS = ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian", "Pescatarian", "No Preference"]
CUISINE_OPTIONS = ["Indian", "Mexican", "Spanish", "Italian", "Chinese", "American", "Japanese", "Korean", "Thai", "Middle Eastern"]
MEAL_TYPE_OPTIONS = ["Breakfast", "Lunch", "Dinner", "Snack", "Main Course", "Dessert", "Soup", "Salad"]
BUDGET_TYPE_OPTIONS = ["Daily", "Weekly", "Monthly"]

st.set_page_config(
    page_title="Nutri-AI",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: Orange;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: Light Orange;
        margin-top: 1rem;
    }
    .info-box {
        background-color: Black;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .result-box {
        background-color: grey;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def check_api_health():
    """Check if the backend API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health-check", timeout=5)
        return response.status_code == 200
    except:
        return False

def build_user_profile():
    """Build user profile from sidebar inputs"""
    st.sidebar.header("Your Profile")

    col1, col2 = st.sidebar.columns(2)
    with col1:
        age = st.number_input("Age", min_value=10, max_value=100, value=25)
        weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=70.0, step=0.5)
    with col2:
        gender = st.selectbox("Gender", GENDER_OPTIONS)
        height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.5)

    fitness_level = st.sidebar.selectbox("Fitness Level", FITNESS_LEVEL_OPTIONS)
    goal = st.sidebar.selectbox("Goal", GOAL_OPTIONS)
    diet_preference = st.sidebar.selectbox("Diet Preference", DIET_PREFERENCE_OPTIONS)

    st.sidebar.subheader("Schedule")
    work_hours = st.sidebar.text_input("Work Hours", "9 AM - 5 PM")
    free_time = st.sidebar.text_input("Free Time", "6 PM - 10 PM")

    st.sidebar.subheader("Budget")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        budget_amount = st.number_input("Amount ($)", min_value=1.0, value=50.0, step=5.0)
    with col2:
        budget_type = st.selectbox("Type", BUDGET_TYPE_OPTIONS)

    gym_access = st.sidebar.checkbox("Gym Access", value=True)

    st.sidebar.subheader("Additional Info")
    allergies = st.sidebar.text_input("Allergies (comma-separated)", "")
    health_conditions = st.sidebar.text_input("Health Conditions (comma-separated)", "")
    cuisine_preferences = st.sidebar.multiselect("Cuisine Preferences", CUISINE_OPTIONS, default=["Indian"])
    available_ingredients = st.sidebar.text_area("Available Ingredients (comma-separated)", "")

    st.sidebar.subheader("Caffeine & Sleep")
    caffeine_sensitive = st.sidebar.checkbox("Caffeine Sensitive")
    sleep_hours = st.sidebar.slider("Sleep Hours", 4, 12, 7)

    # Menstrual cycle (for females)
    menstrual_cycle_day = None
    if gender == "Female":
        st.sidebar.subheader("Menstrual Cycle")
        track_cycle = st.sidebar.checkbox("Track Menstrual Cycle")
        if track_cycle:
            menstrual_cycle_day = st.sidebar.slider("Current Cycle Day", 1, 28, 14)

    return {
        "age": age,
        "gender": gender,
        "weight_kg": weight,
        "height_cm": height,
        "work_hours": work_hours,
        "free_time": free_time,
        "fitness_level": fitness_level,
        "goal": goal,
        "gym_access": gym_access,
        "diet_preference": diet_preference,
        "budget_amount": budget_amount,
        "budget_type": budget_type,
        "allergies": [a.strip() for a in allergies.split(",") if a.strip()],
        "health_conditions": [h.strip() for h in health_conditions.split(",") if h.strip()],
        "cuisine_preferences": cuisine_preferences,
        "menstrual_cycle_day": menstrual_cycle_day,
        "available_ingredients": [i.strip() for i in available_ingredients.split(",") if i.strip()],
        "caffeine_sensitive": caffeine_sensitive,
        "sleep_hours": sleep_hours
    }

def nutrition_analysis_page(user_profile):
    """Nutrition Analysis Page"""
    st.header("Nutrition Analysis")
    st.write("Get a complete nutrition analysis including BMI, calorie needs, macros, and caffeine guidance.")

    if st.button("Analyze My Nutrition", type="primary"):
        with st.spinner("Analyzing your nutrition profile..."):
            try:
                response = requests.post(f"{API_BASE_URL}/nutrition-analysis", json=user_profile)
                if response.status_code == 200:
                    data = response.json()

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("BMI", f"{data['bmi']}", data['bmi_category'])
                    with col2:
                        st.metric("Daily Calories", f"{data['daily_calories']} kcal")
                    with col3:
                        st.metric("Hydration", f"{data['hydration_liters']} L/day")

                    st.subheader("Macro Breakdown")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Protein", f"{data['macro_breakdown']['protein_g']}g")
                    with col2:
                        st.metric("Carbs", f"{data['macro_breakdown']['carbs_g']}g")
                    with col3:
                        st.metric("Fats", f"{data['macro_breakdown']['fats_g']}g")

                    st.subheader("Caffeine Guidance")
                    caffeine = data['caffeine_guidance']
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Max Caffeine", f"{caffeine['max_caffeine_mg']} mg/day")
                    with col2:
                        st.metric("Max Coffee", f"{caffeine['max_coffee_cups']} cups/day")
                    with col3:
                        st.metric("Max Tea", f"{caffeine['max_tea_cups']} cups/day")

                    with st.expander("Coffee Preparation Tips"):
                        for key, value in caffeine['coffee_preparation'].items():
                            st.write(f"**{key.replace('_', ' ').title()}:** {value}")

                    with st.expander("Tea Preparation Tips"):
                        for key, value in caffeine['tea_preparation'].items():
                            st.write(f"**{key.replace('_', ' ').title()}:** {value}")

                    if caffeine['warnings']:
                        st.warning("**Warnings:** " + " | ".join(caffeine['warnings']))
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to API: {str(e)}")

def fitness_plan_page(user_profile):
    """Fitness Plan Page"""
    st.header("Personalized Fitness Plan")
    st.write("Generate a comprehensive workout plan tailored to your goals and fitness level.")

    if st.button("Generate Fitness Plan", type="primary"):
        with st.spinner("Creating your personalized fitness plan..."):
            try:
                response = requests.post(f"{API_BASE_URL}/fitness-plan", json=user_profile, timeout=120)
                if response.status_code == 200:
                    data = response.json()

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Your BMI", data['user_bmi'])
                    with col2:
                        st.metric("Category", data['bmi_category'])

                    st.subheader("Your Fitness Plan")
                    st.markdown(data['fitness_plan'])
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to API: {str(e)}")

def meal_plan_page(user_profile):
    """Meal Plan Page"""
    st.header("Personalized Meal Plan")
    st.write("Get a detailed meal plan based on your dietary preferences and budget.")

    if st.button("Generate Meal Plan", type="primary"):
        with st.spinner("Creating your personalized meal plan..."):
            try:
                response = requests.post(f"{API_BASE_URL}/meal-plan", json=user_profile, timeout=120)
                if response.status_code == 200:
                    data = response.json()

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Daily Calories", f"{data['daily_calories']} kcal")
                    with col2:
                        st.metric("Daily Budget", f"${data['daily_budget']}")
                    with col3:
                        st.metric("Cuisines", data['cuisine_preferences'])

                    st.subheader("Your Meal Plan")
                    st.markdown(data['meal_plan'])
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to API: {str(e)}")

def recipe_generator_page(user_profile):
    """Recipe Generator Page"""
    st.header("Recipe Generator")
    st.write("Generate recipes based on ingredients you have available.")

    col1, col2 = st.columns(2)
    with col1:
        ingredients = st.text_area("Available Ingredients (comma-separated)",
                                    "chicken, rice, onion, garlic, tomato")
        meal_type = st.selectbox("Meal Type", MEAL_TYPE_OPTIONS)
        servings = st.slider("Servings", 1, 10, 2)

    with col2:
        cuisine_type = st.selectbox("Cuisine Type (optional)", ["Any"] + CUISINE_OPTIONS)
        prep_time_max = st.slider("Max Prep Time (minutes)", 5, 180, 45)
        budget_per_serving = st.number_input("Budget per Serving ($)", min_value=0.0, value=5.0, step=0.5)

    if st.button("Generate Recipe", type="primary"):
        with st.spinner("Creating your recipe..."):
            recipe_request = {
                "available_ingredients": [i.strip() for i in ingredients.split(",") if i.strip()],
                "cuisine_type": cuisine_type if cuisine_type != "Any" else None,
                "meal_type": meal_type,
                "servings": servings,
                "prep_time_max": prep_time_max,
                "diet_preference": user_profile['diet_preference'],
                "allergies": user_profile['allergies'],
                "budget_per_serving": budget_per_serving if budget_per_serving > 0 else None
            }

            try:
                response = requests.post(f"{API_BASE_URL}/recipe-generator", json=recipe_request, timeout=120)
                if response.status_code == 200:
                    data = response.json()
                    st.subheader(f"Recipe for {data['meal_type']}")
                    st.markdown(data['recipe'])
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to API: {str(e)}")

def period_nutrition_page(user_profile):
    """Period Nutrition Page"""
    st.header("Period Nutrition Guide")

    if user_profile['gender'] != "Female":
        st.info("This feature is designed for female users to get nutrition guidance based on their menstrual cycle.")
        return

    if not user_profile.get('menstrual_cycle_day'):
        st.warning("Please enable menstrual cycle tracking in the sidebar and set your current cycle day.")
        return

    st.write(f"Current Cycle Day: **{user_profile['menstrual_cycle_day']}**")

    if st.button("Get Period Nutrition Guide", type="primary"):
        with st.spinner("Creating your period-specific nutrition guide..."):
            try:
                response = requests.post(f"{API_BASE_URL}/period-nutrition", json=user_profile, timeout=120)
                if response.status_code == 200:
                    data = response.json()

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Cycle Day", data['cycle_day'])
                    with col2:
                        st.metric("Current Phase", data['current_phase'])

                    st.subheader("Your Period Nutrition Guide")
                    st.markdown(data['period_nutrition_guide'])
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to API: {str(e)}")

def caffeine_guidance_page(user_profile):
    """Caffeine Guidance Page"""
    st.header("Caffeine Guidance")
    st.write("Get personalized recommendations for coffee and tea consumption.")

    if st.button("Get Caffeine Guidance", type="primary"):
        with st.spinner("Analyzing your caffeine needs..."):
            try:
                response = requests.post(f"{API_BASE_URL}/caffeine-guidance", json=user_profile, timeout=120)
                if response.status_code == 200:
                    data = response.json()

                    limits = data['caffeine_limits']

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Max Caffeine", f"{limits['max_caffeine_mg']} mg/day")
                    with col2:
                        st.metric("Max Coffee", f"{limits['max_coffee_cups']} cups/day")
                    with col3:
                        st.metric("Max Tea", f"{limits['max_tea_cups']} cups/day")

                    with st.expander("Timing Recommendations", expanded=True):
                        for rec in limits['timing_recommendations']:
                            st.write(f"• {rec}")

                    if limits['warnings']:
                        st.warning("**Warnings:** " + " | ".join(limits['warnings']))

                    st.subheader("Detailed Recommendations")
                    st.markdown(data['detailed_recommendations'])
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to API: {str(e)}")

def chatbot_page(user_profile):
    """Chatbot Page"""
    st.header("Fitness & Nutrition Chatbot")
    st.write("Ask any questions about fitness, nutrition, meal planning, and more!")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything about fitness and nutrition..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    chat_request = {
                        "message": prompt,
                        "user_profile": user_profile,
                        "conversation_history": st.session_state.messages[:-1]
                    }

                    response = requests.post(f"{API_BASE_URL}/chatbot", json=chat_request, timeout=120)
                    if response.status_code == 200:
                        data = response.json()
                        assistant_response = data['response']
                        st.markdown(assistant_response)
                        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Failed to connect to API: {str(e)}")

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

def progress_tracking_page(user_profile):
    """Progress Tracking Page"""
    st.header("Progress Tracking System")
    st.write("Get a comprehensive system for tracking your fitness progress.")

    if st.button("Generate Progress Tracking Plan", type="primary"):
        with st.spinner("Creating your progress tracking system..."):
            try:
                response = requests.post(f"{API_BASE_URL}/progress-tracking", json=user_profile, timeout=120)
                if response.status_code == 200:
                    data = response.json()

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Current BMI", data['current_bmi'])
                    with col2:
                        st.metric("Goal", data['goal'])

                    st.subheader("Your Progress Tracking System")
                    st.markdown(data['progress_tracking_system'])
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to API: {str(e)}")

def main():
    st.markdown('<h1 class="main-header">Fitness & Diet Management</h1>', unsafe_allow_html=True)

    # Check API health
    api_status = check_api_health()
    if api_status:
        st.sidebar.success("API Connected")
    else:
        st.sidebar.error("API Disconnected - Start the backend server")
        st.error("Cannot connect to the backend API. Please ensure the FastAPI server is running on http://localhost:8000")
        st.code("python -m uvicorn main:app --reload", language="bash")
        return

    # Build user profile from sidebar
    user_profile = build_user_profile()

    # Navigation
    st.sidebar.markdown("---")
    st.sidebar.header("Navigation")
    page = st.sidebar.radio(
        "Select Feature",
        [
            "Nutrition Analysis",
            "Fitness Plan",
            "Meal Plan",
            "Recipe Generator",
            "Period Nutrition",
            "Caffeine Guidance",
            "Chatbot",
            "Progress Tracking"
        ]
    )

    # Page routing
    if page == "Nutrition Analysis":
        nutrition_analysis_page(user_profile)
    elif page == "Fitness Plan":
        fitness_plan_page(user_profile)
    elif page == "Meal Plan":
        meal_plan_page(user_profile)
    elif page == "Recipe Generator":
        recipe_generator_page(user_profile)
    elif page == "Period Nutrition":
        period_nutrition_page(user_profile)
    elif page == "Caffeine Guidance":
        caffeine_guidance_page(user_profile)
    elif page == "Chatbot":
        chatbot_page(user_profile)
    elif page == "Progress Tracking":
        progress_tracking_page(user_profile)

if __name__ == "__main__":
    main()
