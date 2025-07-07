import streamlit as st
# import pandas as pd
import os
import base64  # to enable writing to GitHub repo
import requests  # ditto

from datetime import datetime

st.set_page_config(page_title="Comic Panel Experiment", layout="centered")
st.title("🧠 Comic Panel Experiment")

# === Participant Info Form ===
if "age" not in st.session_state:
    with st.form("participant_form"):
        st.write("### Tell us about yourself")
        age = st.text_input("Your age:", key="age")
        gender = st.selectbox("Gender:", ["Prefer not to say", "Female", "Male", "Other"], key="gender")
        submit = st.form_submit_button(label="Start")
        if not submit:
            st.stop()

# === decide on test type - if even numbered participant then test type = original ===
if "participant" not in st.session_state:
    participant_file = "Participant.txt"
    with open(participant_file, "r", encoding="utf-8") as in_f:
        try:
            participant = int(in_f.readline())
            st.write("participant from file", participant)
        except ValueError:
            participant = 1
        if participant % 2 == 0:
            testtype = "Group A"
        else:
            testtype = "Group B"
    # === now update the participant number ===
    participant = participant + 1
    st.session_state.participant = participant
    st.session_state.testtype = testtype
    st.success(f"🧪 You are participant **{participant}**.")

if "proceed" not in st.session_state:
    with st.form("instructions_form"):
        st.write("""
        Welcome to our experiment!  
        You’ll view a sequence of comic panels and will then be asked to answer two questions.  
        Please read each panel and then press next to display the next one. You cannot go back.
        
        All responses are anonymous.  
        """)
        st.session_state.proceed = st.form_submit_button("Continue")
        if not st.session_state.proceed:
            st.stop()

# === Load Images ===
if "final_images" not in st.session_state:
    image_files1 = [f"panel{i}.png" for i in range(1, 8)]
    image_files2 = ["panel8.png", "panel9.png"]
    image_files3 = ["panel8_manipulated.png", "panel9_manipulated.png"]
    if st.session_state.testtype == "Group A":
        st.session_state.final_images = image_files1 + image_files2
    else:
        st.session_state.final_images = image_files1 + image_files3

# st.write("### Please view each panel and answer the question")

# === Loop through each image ===
# Initialize index in session state
if "img_index" not in st.session_state:
    st.session_state.img_index = 0

panel_number = st.session_state.img_index + 1
panel_number_str = str(panel_number)

# Show first image
if "img_index" in st.session_state:
    if st.session_state.img_index < 9:
        with st.form(f"image_{panel_number_str}"):
            current_image = st.session_state.final_images[st.session_state.img_index]
            st.image(os.path.join("Images", current_image), caption=current_image)
            st.session_state.img_index += 1
            next_image = st.form_submit_button("Next")
            if not next_image:
                st.stop()

if "answer" not in st.session_state:
    with st.form("response_form"):
        st.write("### Please type your responses to the questions below ")
        answer = st.text_input("What do you think happens next?", key="answer")
        submit = st.form_submit_button("Submit")
        if not submit:
            st.stop()

if "confidence" not in st.session_state:
    with st.form("response_form2"):
        confidence = st.selectbox(
            "How confident do you feel about this on a scale of 1(low) to 10(certain)?",
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], key="confidence")
        submit = st.form_submit_button("Submit")
        if not submit:
            st.stop()

# -----------------
# st.write("participant ", st.session_state.participant, "age ", st.session_state.age)
# st.write("gender ", st.session_state.gender, "type ", st.session_state.testtype)
# st.write("answer ", st.session_state.answer, "confidence ", st.session_state.confidence)
# ------------------
# === Now need to write to GitHub files
if "answer" in st.session_state:

    # My GitHub info
    token = st.secrets["github"]["token"]
    repo = "JulienHartley/KiuzTuB"
    branch = "main"

    # === Save CSV
    filename = "Results/" + f"response_{st.session_state.participant}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
# ........
    api_url = f"https://api.github.com/repos/{repo}/contents/{filename}"
    output_array = [str(st.session_state.participant),
                    str(st.session_state.age),
                    st.session_state.gender,
                    st.session_state.testtype,
                    st.session_state.answer,
                    str(st.session_state.confidence)]
    output_record = ",".join(output_array)
    encoded_content = base64.b64encode(output_record.encode("utf-8")).decode("utf-8")

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }

    data = {
        "message": f"Add {filename}",
        "content": encoded_content,
        "branch": branch
    }

    response = requests.put(api_url, headers=headers, json=data)

    if response.status_code == 201:
        st.success("File created successfully!")
    else:
        st.error(f"Error: {response.status_code} - {response.json()}")
# Now update participant.txt
if "participant" in st.session_state:
    filename = "Participant.txt"
    output_record = str(st.session_state.participant)
    encoded_content = base64.b64encode(output_record.encode("utf-8")).decode("utf-8")

    # My GitHub info
    token = st.secrets["github"]["token"]
    repo = "JulienHartley/KiuzTuB"
    branch = "main"

    api_url = f"https://api.github.com/repos/{repo}/contents/{filename}"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        file_info = response.json()
        sha = file_info["sha"]
    else:
        st.error(f"Failed to fetch file info: {response.status_code}")
        st.stop()

    update_payload = {
        "message": "Update file via Streamlit",
        "content": encoded_content,
        "sha": sha,
        "branch": branch
    }

    update_response = requests.put(api_url, headers=headers, json=update_payload)

    if update_response.status_code == 200:
        st.success("✅ File updated successfully!")
    else:
        st.error(f"❌ Update failed: {update_response.status_code}")
        st.json(update_response.json())

st.success("✅ Thank you! Your responses have been recorded. You may close this browser window")
