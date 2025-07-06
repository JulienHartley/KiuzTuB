import streamlit as st
# import pandas as pd
import csv
import os
import base64 # to enable writing to Github repo
import requests # ditto

from datetime import datetime

st.set_page_config(page_title="Comic Panel Experiment", layout="centered")
st.title("🧠 Comic Panel Experiment")

# === Participant Info Form ===
if "age" not in st.session_state:
    with st.form("participant_form"):
        st.write("### Tell us about yourself")
        age = st.text_input("Your age:", key="age")
        gender = st.selectbox("Gender:", ["Prefer not to say", "Female", "Male", "Other"], key="gender")
        submit = st.form_submit_button(label="Start", on_click=form_callback)
        if not submit:
            st.stop()
        st.write(st.session_state.age, st.session_state.gender)

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
    st.write("this participant", participant)
    st.session_state.participant = participant
    st.session_state.testtype = testtype
    st.success(f"🧪 You are participant **{participant}** and have been assigned to the **{testtype}** condition.")

if "proceed" not in st.session_state:
    with st.form("instructions_form"):
        st.write("""
        Welcome to our experiment!  
        You’ll view a sequence of comic panels and will then be asked to answer two questions.  
        All responses are anonymous.  
        """)
        st.session_state.proceed = st.form_submit_button("Continue")
        st.write("participant after instructions ", st.session_state.participant)
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
st.session_state.img_index = 0

# Show first image
if "image1" not in st.session_state:
    with st.form("first_image"):
        current_image = st.session_state.final_images[st.session_state.img_index]
        st.image(os.path.join("Images", current_image), caption=current_image)
        st.session_state.image1 = current_image
        next_image = st.form_submit_button("Next")
        if not next_image:
            st.stop()

# if next:
#   if img_index < len(image_files) - 1:
#       img_index += 1
#       current_image = final_images[img_index]
#       form_key = "image" + str(img_index)
#       with st.form(form_key):
#           st.image(os.path.join(image_folder, current_image), caption=current_image)
#           next = st.form_submit_button("Next")

if "answer" not in st.session_state:
    with st.form("response_form"):
        st.write("### Please type your responses to the questions below ")
        st.session_state.answer = st.text_input("What do you think happens next?")
        st.session_state.confidence = st.radio(
            "How confident do you feel about this on a scale of 1(low) to 10(certain)?",
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        submit = st.form_submit_button("Submit")
        st.write(st.session_state.answer, st.session_state.confidence)
        if not submit:
            st.stop()

# -----------------
st.write("participant ", st.session_state.participant, "age ", st.session_state.age)
st.write("gender ", st.session_state.gender, "type ", st.session_state.testtype)
st.write("answer ", st.session_state.answer, "confidence ", st.session_state.confidence)
# ------------------
# === Now need to write to Github files
if "answer" in st.session_status:

    # My GitHub info
    token = "YOUR_GITHUB_TOKEN"
    repo = "JulienHartley/KiuzTuB"
    branch = "main"

    # === Save CSV
    filename = f"response_{st.session_state.participant}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    path = f"{filename}"
# ........
    api_url = f"https://api.github.com/repos/{repo}/contents/{path}"
    encoded_content = base64.b64encode(content.encode()).decode()

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
# ..........




    with open(filename, "w", encoding="utf-8") as out_f:
        writer = csv.writer(out_f)
        writer.writerow([
            'Participant',
            'Age',
            'Gender',
            'Test type',
            'Answer',
            'Confidence'])
        writer.writerow([st.session_state.participant, st.session_state.age,
                         st.session_state.gender, st.session_state.testtype,
                         st.session_state.answer, st.session_state.confidence])
    # === update participant number in participant.txt
    with open("participant.txt", "w", encoding="utf-8") as out_f:
        out_f.write(str(st.session_state.participant))

st.success("✅ Thank you! Your responses have been recorded. You may close this browser window")
# st.download_button("Download your CSV", data=df.to_csv(index=False).encode(), file_name=filename, mime="text/csv")
