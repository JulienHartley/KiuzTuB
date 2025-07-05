
import streamlit as st
import pandas as pd
import csv
import os
from datetime import datetime

st.set_page_config(page_title="Comic Panel Experiment", layout="centered")
st.title("🧠 Comic Panel Experiment")

# === Participant Info Form ===
with st.form("participant_form"):
    st.write("### Tell us about yourself")
    age = st.text_input("Your age:")
    gender = st.selectbox("Gender:", ["Prefer not to say", "Female", "Male", "Other"])
    submit = st.form_submit_button("Start")

if not submit:
    st.stop()

# === decide on test type - if even numbered participant then test type = original ===
participant_file = "Participant.txt"
with open(participant_file, "r", encoding="utf-8") as in_f:
    try:
        participant = int(in_f.readline())
    except ValueError:
        participant = 1

    if participant % 2 == 0:
        testtype = "Group A"
    else:
        testtype = "Group B"
# === now update the participant number ===
participant = participant + 1
with open("participant.txt", "w") as out_f:
    out_f.write(str(participant))

st.session_state["testtype"] = testtype
st.success(f"🧪 You are participant **{participant}** and have been assigned to the **{testtype}** condition.")

with st.form("instructions_form"):
    st.write("""
    Welcome to our experiment!  
    You’ll view a sequence of comic panels and will then be asked to answer two questions.  
    All responses are anonymous.  
    """)
    proceed = st.form_submit_button("Continue")

if not proceed:
   st.stop()

# === Load Images ===
image_folder = "Images"
image_files1 = [f"panel{i}.png" for i in range(1, 8)]
image_files2 = ["panel8.png", "panel9.png"]
image_files3 = ["panel8_manipulated.png", "panel9_manipulated.png"]
final_images = image_files1 + (image_files2 if testtype == "Original" else image_files3)

responses = []

# st.write("### Please view each panel and answer the question")

# === Loop through each image ===
# Initialize index in session state
img_index = 0

# Show first image
with st.form("first_image"):
    current_image = final_images[img_index]
    st.image(os.path.join(image_folder, current_image), caption=current_image)
    next = st.form_submit_button("Next")

#if next:
#   if img_index < len(image_files) - 1:
#        img_index += 1
#       current_image = final_images[img_index]
#       form_key = "image" + str(img_index)
#       with st.form(form_key):
#           st.image(os.path.join(image_folder, current_image), caption=current_image)
#           next = st.form_submit_button("Next")


with st.form("response_form"):
    st.write("### Please type your responses to the questions below ")
    answer = st.text_input("What do you think happens next?")
    confidence = st.radio("How confident do you feel about this on a scale of 1(low) to 10(certain)?",
                          ["1","2","3","4","5","6","7","8","9","10"])
    submit = st.form_submit_button("Submit")

# === appends user's answers to responses array
#responses.append({"participant":participant, "response": answer, "confidence": confidence})

# === Save ===
#df = pd.DataFrame(responses)
#df["participant"] = participant
#df["age"] = age
#df["gender"] = gender
#df["testtype"] = testtype
#df["timestamp"] = datetime.now().isoformat()

# === Save CSV
filename = f"response_{participant}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
with open(filename, "w", encoding="utf-8") as out_f:
    writer = csv.writer(out_f)
    writer.writerow([
    'Participant',
    'Age',
    'Gender',
    'Test type',
    'Answer',
    'Confidence'
    ])
    writer.writerow([participant,age,gender,testtype,answer,confidence])
#    df.to_csv(filename, index=False)

st.success("✅ Thank you! Your responses have been recorded.")
st.download_button("Download your CSV", data=df.to_csv(index=False).encode(), file_name=filename, mime="text/csv")
