# ✅ Unified Streamlit App with Multiple Tools
# Original scripts: streamlit6.py and FINAL_MENU_BASED_PROJECT.py
# Version 2.0: Added Home Page and Custom Styling

# 📦 Auto-install required packages
import subprocess
import sys

# Combined list of required packages from both scripts
required = [
    "streamlit", "langchain", "langchain-google-genai", "langchain-community",
    "fpdf", "requests", "pypdf", "protobuf==4.25.1", "proto-plus==1.23.0",
    "beautifulsoup4", "pywhatkit", "smtplib-shim", "openai", "tweepy",
    "instagrapi", "pandas", "scikit-learn", "mysql-connector-python",
    "google-search-results", "pyautogui"
]

for pkg in required:
    try:
        # Try importing the package to see if it's installed
        __import__(pkg.split("==")[0].replace("-", "_"))
    except ImportError:
        # If not installed, use pip to install it
        package_to_install = pkg
        if pkg == "smtplib-shim": # smtplib is built-in
             continue
        if pkg == "google-search-results":
            package_to_install = "google"

        subprocess.check_call([sys.executable, "-m", "pip", "install", package_to_install])


# 🧠 Main Imports
import streamlit as st
import os
import re
import tempfile
import time
import json
import requests
from fpdf import FPDF
from bs4 import BeautifulSoup
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import HumanMessage
import pywhatkit
import smtplib
from openai import OpenAI
import tweepy
from instagrapi import Client as InstaClient
import pandas
from sklearn.linear_model import LinearRegression
import mysql.connector
from mysql.connector import Error
from googlesearch import search
import pyautogui


# Dummy Password file for functions that require it
class Password:
    twilio_sid = "YOUR_TWILIO_SID"
    twilio_auth_token = "YOUR_TWILIO_AUTH_TOKEN"
    my_phone = "YOUR_PHONE_NUMBER"
    twilio_number = "YOUR_TWILIO_NUMBER"
    email = "YOUR_EMAIL"
    mail_pass = "YOUR_EMAIL_PASSWORD"
    insta_pass = "YOUR_INSTAGRAM_PASSWORD"
    twitter_consumer_key = "YOUR_TWITTER_CONSUMER_KEY"
    twitter_consumer_secret = "YOUR_TWITTER_CONSUMER_SECRET"
    twitter_access_token = "YOUR_TWITTER_ACCESS_TOKEN"
    twitter_access_token_secret = "YOUR_TWITTER_ACCESS_TOKEN_SECRET"

# 🧠 Gemini Setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "YOUR_GEMINI_API_KEY" # Replace with your key
GEMINI_MODEL = "gemini-1.5-pro"
FALLBACK_MODEL = "gemini-1.5-flash"
MAX_RETRIES = 3

# Initialize the Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GEMINI_API_KEY,
    convert_system_message_to_human=True,
    temperature=0.7,
    stream=False
)

# ========== Streamlit Layout & Styling ==========
st.set_page_config(page_title="AI Automation Hub", layout="wide", page_icon="🚀")

# Custom CSS for a modern dark theme
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# You can create a style.css file or embed the CSS directly
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Roboto', sans-serif;
    }

    .stApp {
        background-color: #0f1116;
        color: #e6e6e6;
    }

    .st-emotion-cache-16txtl3 {
        padding: 2rem 2rem 1rem;
    }

    .stSidebar {
        background-color: #1a1c23;
    }

    .st-emotion-cache-16txtl3 h1 {
        color: #00aaff;
        font-weight: 700;
    }

    .st-emotion-cache-16txtl3 h2, .st-emotion-cache-16txtl3 h3 {
        color: #00aaff;
    }

    .stButton>button {
        background-color: #007bff;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: 500;
        transition: background-color 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #0056b3;
    }

    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #1a1c23;
        color: #e6e6e6;
        border-radius: 8px;
        border: 1px solid #333;
    }

    .stSelectbox>div>div {
        background-color: #1a1c23;
        border-radius: 8px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


st.sidebar.title("🚀 AI Automation Hub")
st.sidebar.markdown("---")

# Combined list of tools with icons
page = st.sidebar.radio("Select a Tool", [
    "🏠 Home",
    "📄 PDF Summarizer",
    "🐧 Remote Linux",
    "🐳 Docker Manager",
    "🌐 Website Q&A",
    "🐍 Python Error Fixer",
    "📘 Blog Explorer",
    "📱 Social & Comms",
    "🤖 AI/ML Models",
    "🏦 Bank Management System",
    "🔍 Google Search"
])
st.sidebar.markdown("---")
st.sidebar.info("This app combines multiple AI and automation tools into a single interface.")


# 🔁 Reusable Functions
def remove_emojis(text):
    return re.sub(r'[\U00010000-\U0010ffff]', '', text)

def save_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in remove_emojis(content).split("\n"):
        pdf.multi_cell(0, 10, line if line.strip() else " ")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        return tmp.name

def save_txt(content):
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".txt", encoding="utf-8") as tmp:
        tmp.write(content)
        return tmp.name

def run_ssh_command(user, ip, command):
    full_cmd = f'ssh {user}@{ip} "{command}"'
    try:
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return str(e)

# === Tool Pages ===

if page == "🏠 Home":
    st.title("Welcome to the All-in-One AI Automation Hub")
    st.markdown("### A Menu-Based Project by **Nitin Singh**")
    st.markdown("---")
    
    st.info("""
        This application integrates a variety of powerful tools, from AI-powered document summarization and code fixing to remote server management and social media automation. 
        
        **Select a tool from the sidebar on the left to get started!**
    """)
    
    st.subheader("Featured Tools:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("- **📄 PDF Summarizer**")
        st.markdown("- **🐧 Remote Linux**")
        st.markdown("- **🐳 Docker Manager**")
    with col2:
        st.markdown("- **🌐 Website Q&A**")
        st.markdown("- **🐍 Python Error Fixer**")
        st.markdown("- **🤖 AI/ML Models**")
    with col3:
        st.markdown("- **📱 Social & Comms**")
        st.markdown("- **🏦 Bank Management**")
        st.markdown("- **🔍 Google Search**")

elif page == "📄 PDF Summarizer":
    st.title("📄 PDF Summarizer (Gemini)")
    url = st.text_input("Paste PDF URL:")
    pages_to_analyze = st.slider("Pages to analyze", 1, 20, 5)

    def read_pdf_pages(pdf_url, max_pages):
        r = requests.get(pdf_url)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(r.content)
            loader = PyPDFLoader(f.name)
            pages = loader.load()
        os.remove(f.name)
        return pages[:max_pages]

    def safe_generate(text, is_final_summary=False):
        prompt = (
            'Summarize the objective, methods, and key findings from the following text:\n\n'
            if is_final_summary else
            'Summarize the following page content into 3–5 concise bullet points:\n\n'
        ) + text[:2000]

        for attempt in range(MAX_RETRIES):
            try:
                response = llm.invoke([HumanMessage(content=prompt)])
                return response.content
            except Exception as e:
                if "stream has ended" in str(e).lower() and attempt < MAX_RETRIES - 1:
                    time.sleep(2)
                    continue
                st.error(f"Error generating summary: {e}")
                return "❌ Failed to generate summary."
        return "❌ Failed after multiple retries."

    if st.button("Summarize"):
        if not url:
            st.warning("Please enter a PDF URL.")
        else:
            try:
                with st.spinner("Processing PDF..."):
                    extracted_pages = read_pdf_pages(url, pages_to_analyze)
                    all_text = ""
                    output_lines = []
                    for i, p in enumerate(extracted_pages):
                        page_text = p.page_content
                        all_text += page_text + "\n\n"
                        summary = safe_generate(page_text)
                        st.subheader(f"📄 Page {i+1} Summary")
                        st.markdown(summary)
                        output_lines.append(f"📄 Page {i+1}:\n{summary}\n")

                    if extracted_pages:
                        final_summary = safe_generate(all_text, is_final_summary=True)
                        st.subheader("🧠 Overall Document Summary")
                        st.markdown(final_summary)
                        output_lines.append("🧠 Overall Summary:\n" + final_summary)
                        full_content = "\n".join(output_lines)
                        
                        txt_path = save_txt(full_content)
                        with open(txt_path, "rb") as f:
                            st.download_button("📥 Download TXT Summary", f, file_name="summary.txt")
                        
                        pdf_path = save_pdf(full_content)
                        with open(pdf_path, "rb") as f:
                            st.download_button("📥 Download PDF Summary", f, file_name="summary.pdf")

            except Exception as e:
                st.error(f"❌ An error occurred: {e}")

elif page == "🐧 Remote Linux":
    st.title("🐧 Remote Linux Shell")
    user = st.text_input("Enter SSH Username")
    ip = st.text_input("Enter Remote IP Address")
    if "linux_path" not in st.session_state:
        st.session_state.linux_path = "~"

    st.info(f"Current remote directory: `{st.session_state.linux_path}`")

    options = [
        "Know Current Directory", "List Files & Directories", "Change Directory",
        "Create Directory", "Create File", "Edit File", "Read File",
        "Remove File", "Remove Directory"
    ]
    choice = st.selectbox("Choose Operation", options)
    extra_input = ""
    if choice in ["Change Directory", "Create Directory", "Edit File", "Create File", "Remove File", "Read File", "Remove Directory"]:
        extra_input = st.text_input("Enter Name/Path:")

    if st.button("Execute"):
        if not user or not ip:
            st.warning("Please provide SSH username and IP address.")
        else:
            current_path = st.session_state.linux_path
            command = ""
            if choice == "Know Current Directory":
                command = f"cd {current_path} && pwd"
            elif choice == "List Files & Directories":
                command = f"cd {current_path} && ls -l"
            elif choice == "Read File":
                command = f"cat {current_path}/{extra_input}"
            elif choice == "Change Directory":
                test_cmd = f"cd {current_path}/{extra_input}"
                test_output = run_ssh_command(user, ip, test_cmd)
                if "No such file or directory" in test_output:
                     st.error("Directory does not exist.")
                else:
                    st.session_state.linux_path = os.path.join(current_path, extra_input).replace("\\", "/")
                    st.success(f"Changed directory to: {st.session_state.linux_path}")
                    st.experimental_rerun()
            elif choice == "Create Directory":
                command = f"cd {current_path} && mkdir {extra_input}"
            elif choice == "Create File":
                command = f"cd {current_path} && touch {extra_input}"
            elif choice == "Remove File":
                command = f"cd {current_path} && rm -f {extra_input}"
            elif choice == "Remove Directory":
                command = f"cd {current_path} && rmdir {extra_input}"

            if command:
                with st.spinner(f"Executing: {command}"):
                    output = run_ssh_command(user, ip, command)
                    st.text_area("📤 Command Output:", output, height=300)

    if choice == "Edit File" and user and ip and extra_input:
        current_path = st.session_state.linux_path
        file_path = f"{current_path}/{extra_input}"
        with st.spinner(f"Fetching content of {file_path}..."):
            out = run_ssh_command(user, ip, f"cat {file_path}")
        
        data = st.text_area("Edit File Content:", out, height=300, key="edit_area")
        
        if st.button("Save Changes to File"):
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
                tmp.write(data)
                tmp_path = tmp.name
            
            scp_cmd = f"scp {tmp_path} {user}@{ip}:{file_path}"
            with st.spinner("Uploading file..."):
                result = subprocess.run(scp_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                st.success("✅ File updated successfully.")
            else:
                st.error(f"❌ Error while uploading: {result.stderr}")
            os.remove(tmp_path)

elif page == "🐳 Docker Manager":
    st.title("🐳 Docker Control Panel")
    user = st.text_input("Enter SSH Username")
    ip = st.text_input("Enter Remote IP Address")
    
    docker_options = [
        "List All Containers", "List Images", "Pull Image", "Launch New Container", 
        "Start Container", "Stop Container", "Remove Container"
    ]
    choice = st.selectbox("Choose Docker Operation", docker_options)
    
    name = st.text_input("Container/Image Name or ID (if needed)")
    image = st.text_input("Image Name (for launching a new container)")
    
    if st.button("Execute Docker Command"):
        if not user or not ip:
            st.warning("Please provide SSH username and IP address.")
        else:
            command = ""
            if choice == "Launch New Container":
                if not name or not image:
                    st.warning("Please provide both a container name and an image name.")
                else:
                    command = f"docker run -dit --name {name} {image}"
            elif choice == "Stop Container":
                command = f"docker stop {name}"
            elif choice == "Remove Container":
                command = f"docker rm -f {name}"
            elif choice == "Start Container":
                command = f"docker start {name}"
            elif choice == "List Images":
                command = "docker images"
            elif choice == "List All Containers":
                command = "docker ps -a"
            elif choice == "Pull Image":
                if not name:
                    st.warning("Please provide an image name to pull.")
                else:
                    command = f"docker pull {name}"
            
            if command:
                with st.spinner(f"Executing: {command}"):
                    output = run_ssh_command(user, ip, command)
                    st.text_area("📤 Docker Output:", output, height=300)

elif page == "🌐 Website Q&A":
    st.title("🌐 Ask Questions from Any Website")
    if "chat_history" not in st.session_state: st.session_state.chat_history = []

    def scrape_website(url):
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            content = "\n".join(el.get_text(strip=True) for el in soup.find_all(['h1','h2','h3','p','li','span']) if el.get_text(strip=True))
            return content[:15000] if content else "No text content found."
        except requests.exceptions.RequestException as e:
            return f"❌ Error scraping website: {e}"

    def website_agent(question, context, history):
        prompt = f"Based ONLY on the following text, answer the question. Do not use outside knowledge.\n\nCONTEXT:\n{context}\n\n---\n\nChat History:\n"
        for msg in history:
            prompt += f"{msg['role']}: {msg['text']}\n"
        prompt += f"user: {question}"
        
        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            reply = response.content
            history.append({"role": "user", "text": question})
            history.append({"role": "model", "text": reply})
            return reply, history
        except Exception as e:
            return f"❌ Gemini API error: {e}", history

    url_input = st.text_input("🔗 Enter Website URL", value="https://www.w3schools.com/python/")
    if st.button("Scrape and Load Website"):
        with st.spinner("Scraping website..."):
            ctx = scrape_website(url_input)
            if ctx.startswith("❌"):
                st.error(ctx)
            else:
                st.session_state.scraped_context = ctx
                st.session_state.chat_history = []
                st.success("✅ Website content loaded!")

    if "scraped_context" in st.session_state:
        question = st.text_input("💬 Ask a question about the website content")
        if st.button("Get Answer") and question.strip():
            with st.spinner("🤖 Getting answer from Gemini..."):
                answer, st.session_state.chat_history = website_agent(question, st.session_state.scraped_context, st.session_state.chat_history)
                st.text_area("📘 Answer", value=answer, height=200)

    with st.expander("📜 View Chat History"):
        if not st.session_state.chat_history:
            st.write("No history yet.")
        for msg in st.session_state.chat_history:
            st.markdown(f"**{msg['role'].capitalize()}**: {msg['text']}")

elif page == "🐍 Python Error Fixer":
    st.title("🐍 Gemini Python Error Fixer")
    code_input = st.text_area("Paste your Python code or error message here", height=300)
    if st.button("Fix with Gemini") and code_input.strip():
        with st.spinner("Analyzing and fixing with Gemini..."):
            try:
                error_prompt = f"""
As an expert Python programmer, please analyze the following code or error message.
Provide a step-by-step explanation of the issue and the corrected code.

CODE/ERROR:
```python
{code_input}
```
"""
                response = llm.invoke([HumanMessage(content=error_prompt)])
                st.success("✅ Gemini's Suggestion:")
                st.markdown(response.content)
            except Exception as e:
                st.error(f"❌ An error occurred with the Gemini API: {e}")

elif page == "📘 Blog Explorer":
    st.title("📘 My Tech Blog Explorer")
    st.markdown("Explore my Linux, Docker, AWS, and Kubernetes blog posts from LinkedIn.")
    blogs = [
        {"title": "Why the World’s Top Tech Companies Use Linux", "link": "https://www.linkedin.com/posts/nitin-singh-tanwar-133419371_title-why-the-worlds-top-tech-companies-activity-7348600415724163072-4u7q", "category": "Linux"},
        {"title": "5 GUI Programs in Linux and the Commands Behind Them", "link": "https://www.linkedin.com/posts/nitin-singh-tanwar-133419371_5-gui-programs-in-linux-and-the-commands-activity-7348607634125619201-BzK1", "category": "Linux"},
        {"title": "Case Study: Why Companies Use Docker", "link": "https://www.linkedin.com/posts/nitin-singh-tanwar-133419371_docker-in-the-real-world-case-studies-activity-7348627852080185344-uGzJ", "category": "Docker"},
        {"title": "AWS Case Studies: How Big Brands Use the Cloud", "link": "https://www.linkedin.com/posts/nitin-singh-tanwar-133419371_aws-case-studies-how-leading-companies-activity-7351824573782294529-jE1D", "category": "AWS"},
        {"title": "Kubernetes Case Study: How Amazon Uses It", "link": "https://www.linkedin.com/posts/nitin-singh-tanwar-133419371_case-study-amazons-strategic-use-of-kubernetes-activity-7351081767530868737-tVok", "category": "Kubernetes"},
    ]
    categories = ["All"] + sorted(list(set(b["category"] for b in blogs)))
    selected_category = st.selectbox("📂 Filter by Category", categories)
    filtered_blogs = blogs if selected_category == "All" else [b for b in blogs if b["category"] == selected_category]
    for blog in filtered_blogs:
        st.subheader(blog["title"])
        st.markdown(f"**Category**: `{blog['category']}`")
        st.markdown(f"[🔗 Read on LinkedIn]({blog['link']})")
        st.markdown("---")

elif page == "📱 Social & Comms":
    st.title("📱 Social Media & Communications")
    task = st.selectbox("Choose a task", ["WhatsApp Message", "Email", "Instagram Post", "Twitter Post", "LinkedIn Post (Automated)", "Twilio SMS", "Twilio Call"])

    if task == "WhatsApp Message":
        st.subheader("WhatsApp Message Sender")
        mob = st.text_input("Enter Receiver's Mob. Number (with country code)", "+91")
        msg = st.text_input("Enter Your Message")
        hour = st.number_input("Hour (24-hour format)", min_value=0, max_value=23, step=1)
        minute = st.number_input("Minute", min_value=0, max_value=59, step=1)
        if st.button("Send WhatsApp Message"):
            pywhatkit.sendwhatmsg(mob, msg, int(hour), int(minute))
            st.success("WhatsApp message scheduled!")

    elif task == "Email":
        st.subheader("Send an Email")
        rec = st.text_input("Enter Receiver's E-Mail")
        sub = st.text_input("Enter Subject")
        body = st.text_area("Enter Body Content")
        if st.button("Send Email"):
            message = f"Subject: {sub}\n\n{body}"
            try:
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(Password.email, Password.mail_pass)
                server.sendmail(Password.email, rec, message)
                server.quit()
                st.success("Email sent successfully!")
            except Exception as e:
                st.error(f"Failed to send email: {e}")

    elif task == "Instagram Post":
        st.subheader("Instagram Photo Uploader")
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])
        caption = st.text_input("Enter Caption for the Photo:")
        if st.button("Upload to Instagram"):
            if uploaded_file is not None and caption:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    image_path = tmp.name
                
                try:
                    cl = InstaClient()
                    cl.login("YOUR_INSTA_USERNAME", Password.insta_pass)
                    cl.photo_upload(path=image_path, caption=caption)
                    st.success("Photo uploaded to Instagram successfully!")
                except Exception as e:
                    st.error(f"Failed to upload to Instagram: {e}")
                finally:
                    os.remove(image_path)
            else:
                st.warning("Please upload an image and provide a caption.")

    elif task == "Twitter Post":
        st.subheader("Twitter Bulk Tweet Poster")
        n = st.number_input("How many tweets?", min_value=1, max_value=10, step=1)
        tweets = [st.text_input(f"Tweet #{i+1}:") for i in range(n)]
        if st.button("Post Tweets"):
            try:
                client = tweepy.Client(
                    consumer_key=Password.twitter_consumer_key,
                    consumer_secret=Password.twitter_consumer_secret,
                    access_token=Password.twitter_access_token,
                    access_token_secret=Password.twitter_access_token_secret
                )
                for i, tweet in enumerate(tweets):
                    if tweet.strip():
                        client.create_tweet(text=tweet)
                        st.success(f"Tweet #{i+1} posted.")
            except Exception as e:
                st.error(f"Failed to post tweets: {e}")

    elif task == "LinkedIn Post (Automated)":
        st.subheader("LinkedIn Auto Poster (via PyAutoGUI)")
        st.warning("This is an automation script. Please ensure the LinkedIn window is ready and do not move your mouse during execution.")
        message = st.text_area("Enter your LinkedIn post message:", "Hello LinkedIn! 🚀")
        if st.button("Post to LinkedIn"):
            st.info("Starting automation in 5 seconds...")
            time.sleep(5)
            try:
                pyautogui.click(x=581, y=127) # Click on 'Start a post'
                time.sleep(3)
                pyautogui.write(message, interval=0.05)
                time.sleep(2)
                pyautogui.click(x=1006, y=620) # Click on 'Post' button
                st.success("Post published on LinkedIn!")
            except Exception as e:
                st.error(f"Automation failed: {e}")

    elif task == "Twilio SMS":
        st.subheader("Twilio SMS Sender")
        msg = st.text_area("Enter the message:")
        if st.button("Send SMS"):
            try:
                from twilio.rest import Client as TwilioClient
                client = TwilioClient(Password.twilio_sid, Password.twilio_auth_token)
                message = client.messages.create(from_=Password.twilio_number, body=msg, to=Password.my_phone)
                st.success(f"Message sent! SID: {message.sid}")
            except Exception as e:
                st.error(f"Failed to send SMS: {e}")

    elif task == "Twilio Call":
        st.subheader("Twilio Auto Call")
        if st.button("Make Test Call"):
            try:
                from twilio.rest import Client as TwilioClient
                client = TwilioClient(Password.twilio_sid, Password.twilio_auth_token)
                call = client.calls.create(twiml='<Response><Say>Hello, this is a test call!</Say></Response>', to=Password.my_phone, from_=Password.twilio_number)
                st.success(f"Call initiated! SID: {call.sid}")
            except Exception as e:
                st.error(f"Failed to make call: {e}")

elif page == "🤖 AI/ML Models":
    st.title("🤖 AI & Machine Learning Models")
    model_choice = st.selectbox("Choose a model", ["Code Explainer (Gemini)", "Marks Predictor"])

    if model_choice == "Code Explainer (Gemini)":
        st.subheader("Code Explainer Using Gemini")
        code_input = st.text_area("Paste your code snippet here:", height=250)
        if st.button("Explain Code"):
            if code_input.strip():
                prompt = f"Explain this code in 4-5 simple lines, specify the programming language, and detect if it’s AI-written or human-written.\n\nCODE:\n```\n{code_input}\n```"
                with st.spinner("Generating explanation..."):
                    response = llm.invoke([HumanMessage(content=prompt)])
                    st.markdown(response.content)
            else:
                st.warning("Please enter a code snippet.")

    elif model_choice == "Marks Predictor":
        st.subheader("Marks Predictor based on Study Hours")
        try:
            if not os.path.exists("marks.csv"):
                dummy_data = {'hrs': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 'marks': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]}
                df = pandas.DataFrame(dummy_data)
                df.to_csv("marks.csv", index=False)
                
            data = pandas.read_csv("marks.csv")
            x = data["hrs"].values.reshape(-1, 1)
            y = data["marks"].values.reshape(-1, 1)
            model = LinearRegression()
            model.fit(x, y)
            hours = st.number_input("Enter hours of study:", min_value=0.0, max_value=10.0, step=0.5)
            if st.button("Predict Marks"):
                prediction = model.predict([[hours]])
                st.success(f"Predicted Marks for {hours} hours: {prediction[0][0]:.2f}%")
        except Exception as e:
            st.error(f"Could not load or process marks.csv: {e}")

elif page == "🏦 Bank Management System":
    st.title("🏦 Banking Management System (MySQL)")
    st.warning("This requires a local MySQL server with a 'bms' database and 'users' and 'transactions' tables.")

    def create_connection():
        try:
            connection = mysql.connector.connect(host="localhost", user="root", password="YOUR_MYSQL_PASSWORD", database="bms")
            return connection
        except Error as e:
            st.error(f"MySQL connection error: {e}")
            return None

    connection = create_connection()
    if connection:
        menu = ["Create User", "View Users", "Deposit", "Withdraw", "View Transactions"]
        choice = st.sidebar.selectbox("BMS Menu", menu)

        if choice == "Create User":
            st.subheader("Create New User")
            with st.form("create_user_form"):
                name = st.text_input("Name")
                email = st.text_input("Email")
                balance = st.number_input("Initial Balance", min_value=0.0)
                if st.form_submit_button("Create"):
                    cursor = connection.cursor()
                    cursor.execute("INSERT INTO users (name, email, balance) VALUES (%s, %s, %s)", (name, email, balance))
                    connection.commit()
                    st.success(f"User {name} created successfully.")
        
        elif choice == "View Users":
            st.subheader("All Users")
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            st.table(users)

        elif choice == "Deposit":
            st.subheader("Deposit Money")
            user_id = st.number_input("User ID", min_value=1)
            amount = st.number_input("Amount", min_value=0.01)
            if st.button("Deposit"):
                cursor = connection.cursor()
                cursor.execute("UPDATE users SET balance = balance + %s WHERE id = %s", (amount, user_id))
                cursor.execute("INSERT INTO transactions (user_id, type, amount) VALUES (%s, 'deposit', %s)", (user_id, amount))
                connection.commit()
                st.success(f"Deposited {amount} to user ID {user_id}")

        elif choice == "Withdraw":
            st.subheader("Withdraw Money")
            user_id = st.number_input("User ID", min_value=1)
            amount = st.number_input("Amount", min_value=0.01)
            if st.button("Withdraw"):
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
                user = cursor.fetchone()
                if user and user['balance'] >= amount:
                    cursor.execute("UPDATE users SET balance = balance - %s WHERE id = %s", (amount, user_id))
                    cursor.execute("INSERT INTO transactions (user_id, type, amount) VALUES (%s, 'withdrawal', %s)", (user_id, amount))
                    connection.commit()
                    st.success(f"Withdrew {amount} from user ID {user_id}")
                else:
                    st.error("Insufficient balance or user not found.")
        
        elif choice == "View Transactions":
            st.subheader("User Transactions")
            user_id = st.number_input("User ID", min_value=1)
            if st.button("View"):
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM transactions WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
                transactions = cursor.fetchall()
                st.table(transactions)
        
        connection.close()

elif page == "🔍 Google Search":
    st.title("🔍 Google Search Using Python")
    query = st.text_input("Enter your search query")
    num_results = st.slider("Number of results", min_value=1, max_value=20, value=5)

    if st.button("Search"):
        if query.strip():
            with st.spinner(f"Searching Google for: '{query}'..."):
                try:
                    results = list(search(query, num_results=num_results))
                    if results:
                        st.success("Search complete!")
                        for i, url in enumerate(results, start=1):
                            st.write(f"{i}. [{url}]({url})")
                    else:
                        st.error("No results found.")
                except Exception as e:
                    st.error(f"An error occurred during search: {e}")
        else:
            st.warning("Please enter a search query.")
