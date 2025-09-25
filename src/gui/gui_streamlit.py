import streamlit as st

def create_gui():
    st.title("My Streamlit App")
    st.write("Welcome to my app!")
    if st.button("押す"):
        st.success("こんにちは！Streamlitへようこそ。")
    return

if __name__ == "__main__":
    create_gui()