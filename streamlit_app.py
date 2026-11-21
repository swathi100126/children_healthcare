import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv(Path(__file__).resolve().parent / ".env")

SYSTEM_PROMPT = """
You are a helpful children's healthcare information assistant.

Your role:
- Provide simple and understandable child health information.
- Help parents understand common symptoms, nutrition, hygiene,
  sleep and general child wellness.
- Use friendly and easy-to-understand language.
- Ask for the child's age when it is important to answer.
- Never claim to diagnose a disease.
- Never prescribe medicines or dosages.
- Do not assume symptoms are harmless.
- If the child has difficulty breathing, seizures, is unresponsive,
  or another emergency symptom, advise seeking emergency medical care.
- For concerning symptoms, recommend consulting a pediatrician.
- Make clear that you are an AI assistant, not a doctor.
"""

st.set_page_config(page_title="Children's healthcare assistant")
st.title("Children's healthcare assistant")
st.caption(
    "I am an AI assistant, not a doctor. I do not diagnose illnesses "
    "or prescribe medicine."
)

if not os.getenv("GROQ_API_KEY"):
    st.error("Missing GROQ_API_KEY. Add it to the .env file and restart the app.")
    st.stop()


@st.cache_resource
def get_client() -> Groq:
    return Groq(api_key=os.environ["GROQ_API_KEY"])


def reply(messages: list[dict[str, str]]) -> str:
    completion = get_client().chat.completions.create(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, *messages],
    )
    content = completion.choices[0].message.content
    return content or ""


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("Ask about your child's health"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            answer = reply(st.session_state.messages)
        except Exception as exc:
            if type(exc).__name__ in {"APIConnectionError", "APITimeoutError"}:
                st.error(
                    "Could not reach Groq. Check your internet connection, then try again."
                )
            else:
                st.error(
                    "Could not get a reply. Check your Groq key and model, then try again."
                )
            st.stop()
        st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
