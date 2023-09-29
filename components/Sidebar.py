import streamlit as st
import requests
import json
from shared import constants, utils

# Get available models from the API
def get_available_models():
    try:
        response = requests.get(constants.OPENROUTER_API_BASE + "/models")
        response.raise_for_status()
        models = json.loads(response.text)["data"]
        return [model["id"] for model in models]
    except requests.exceptions.RequestException as e:
        st.error(f"Error getting models from API: {e}")
        return []


# Handle the model selection process
def handle_model_selection(available_models, selected_model, default_model):
    # Determine the index of the selected model
    if selected_model and selected_model in available_models:
        selected_index = available_models.index(selected_model)
    else:
        selected_index = available_models.index(default_model)
    selected_model = st.selectbox(
        "Select a model", available_models, index=selected_index
    )
    return selected_model


def exchange_code_for_api_key(code: str):
    print(f"Exchanging code for API key: {code}")
    try:
        response = requests.post(
            constants.OPENROUTER_API_BASE + "/auth/keys",
            json={"code": code},
        )
        response.raise_for_status()
        st.experimental_set_query_params()
        api_key = json.loads(response.text)["key"]
        st.session_state["api_key"] = api_key
        st.experimental_rerun()
    except requests.exceptions.RequestException as e:
        st.error(f"Error exchanging code for API key: {e}")


def sidebar(default_model):
    with st.sidebar:
        params = st.experimental_get_query_params()
        code = params.get("code", [""])[0]
        if code:
            exchange_code_for_api_key(code)
        # not storing sensitive api_key in query params
        api_key = st.session_state.get("api_key")
        selected_model = params.get("model", [None])[0] or st.session_state.get(
            "model", None
        )
        url = utils.url_to_hostname(utils.get_url())
        if not api_key:
            st.button(
                "Connect OpenRouter",
                on_click=utils.open_page,
                args=(f"{constants.OPENROUTER_BASE}/auth?callback_url={url}",),
            )
        available_models = get_available_models()
        selected_model = handle_model_selection(
            available_models, selected_model, default_model
        )
        st.session_state["model"] = selected_model
        st.experimental_set_query_params(model=selected_model)

            temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
            top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
            max_length = st.sidebar.slider('max_length', min_value=64, max_value=4096, value=512, step=8)


# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)


        if api_key:
            st.text("Connected to OpenRouter")
            if st.button("Log out"):
                del st.session_state["api_key"]
                st.experimental_rerun()
        st.markdown(
            "[View the source code](https://github.com/alexanderatallah/openrouter-streamlit)"
        )
        # st.markdown(
        #     "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/alexanderatallah/openrouter-streamlit?quickstart=1)"
        # )

    return api_key, selected_model