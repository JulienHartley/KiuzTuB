
import streamlit as st
import pandas as pd
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
participant_file = "participant.txt"
with open(participant_file, "r", encoding="utf-8") as in_f:
    try:
        participant = int(in_f.readline())
    except ValueError:
        participant = 1

    if participant % 2 == 0:
        testtype = "Original"
    else:
        testtype = "Updated"
# === now update the participant number ===
participant = participant + 1
with open("participant.txt", "w") as out_f:
    out_f.write(str(participant))

st.session_state["testtype"] = testtype
st.success(f"🧪 You have been assigned to the **{testtype}** condition.")

st.markdown("---")
st.write("""
Welcome to our experiment!  
You’ll view a sequence of comic panels and answer two questions.  
All responses are anonymous.  
""")
st.button("Continue")

# === Load Images ===
image_dir = "Images"
image_files1 = [f"panel{i}.png" for i in range(1, 8)]
image_files2 = ["panel8.png", "panel9.png"]
image_files3 = ["panel8_manipulated.png", "panel9_manipulated.png"]
final_images = image_files1 + (image_files2 if testtype == "Original" else image_files3)

responses = []

st.markdown("---")
# st.write("### Please view each panel and answer the question")

# === Loop through each image ===
for image_file in final_images:
    st.image(os.path.join(image_dir, image_file))
    st.button("Continue")

answer = st.radio(f"What do you think happens next?")
confidence = st.radio(f"How confident do you feel about this on a scale of 1(low) to 10(certain)?")
responses.append({"participant":participant, "response": answer, "confidence": confidence})

# === Submit and Save ===
if st.button("Submit All Responses"):
    df = pd.DataFrame(responses)
    df["participant"] = participant
    df["age"] = age
    df["gender"] = gender
    df["testtype"] = testtype
    df["timestamp"] = datetime.now().isoformat()

    # Save CSV
    filename = f"response_{participant}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)

    st.success("✅ Thank you! Your responses have been recorded.")
    st.download_button("Download your CSV", data=df.to_csv(index=False).encode(), file_name=filename, mime="text/csv")
