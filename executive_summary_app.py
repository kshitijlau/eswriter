import streamlit as st
import pandas as pd
from openai import AzureOpenAI
from io import BytesIO

# --- Azure OpenAI Setup ---
client = AzureOpenAI(
    api_key=st.secrets["AZURE_OPENAI_API_KEY"],
    api_version="2024-08-01-preview",
    azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"]
)

DEPLOYMENT_NAME = st.secrets["AZURE_DEPLOYMENT_NAME"]

# --- Prompt Template (Initial Section) ---
base_prompt = """
You are an expert leadership coach and organizational psychologist. Your task is to synthesize structured Start-Stop-Continue thematic feedback into a concise, high-quality executive summary that can be presented to senior leadership.

🧠 Objective:
Your summary should capture the essence of the feedback, using a professional tone, strategic clarity, and developmental focus. It should feel insightful and tailored to executive-level development.

📌 What you will receive:
You will be provided Start, Stop, and Continue sections that each contain up to 3 themes. Each theme has 3 bullet points. This feedback is the result of an AI-processed multi-rater review.

✍️ How to write the summary:
- Do NOT use the candidate's name. Use "he", "she", or neutral phrasing as needed
- Write in the third person
- Focus on clarity, professionalism, and leadership tone
- Highlight key development areas and strengths without sounding repetitive
- The tone should be supportive, developmental, and suitable for coaching discussions
- Do not reference themes, bullets, or structure explicitly

📋 Output Format:
Write a short executive summary paragraph of 150–200 words that captures the core behavioral themes and opportunities for growth across Start, Stop, and Continue.

---

"""

# --- Generate Executive Summary ---
def generate_summary(thematic_feedback_text):
    prompt = base_prompt + f"Here is the structured feedback:\n\n{thematic_feedback_text}"

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "You are a professional leadership summary writer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=600
    )
    return response.choices[0].message.content

# --- Streamlit UI ---
st.set_page_config(page_title="Executive Summary Generator", layout="wide")
st.title("📝 Executive Summary Generator from SSC Feedback")

uploaded_file = st.file_uploader("Upload SSC Feedback Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if "Name" not in df.columns or "Summary" not in df.columns:
        st.error("The Excel must have columns: 'Name' and 'Summary'")
    else:
        if st.button("🧠 Generate Executive Summaries"):
            output_data = []
            progress = st.progress(0)
            total = len(df)

            for i, row in df.iterrows():
                name = row["Name"]
                summary_input = row["Summary"]
                exec_summary = generate_summary(summary_input)
                output_data.append({"Name": name, "Executive Summary": exec_summary})
                progress.progress((i + 1) / total)

            output_df = pd.DataFrame(output_data)
            st.success("✅ Executive summaries generated!")
            st.dataframe(output_df)

            buffer = BytesIO()
            output_df.to_excel(buffer, index=False, engine="openpyxl")
            buffer.seek(0)

            st.download_button(
                label="📥 Download Executive Summaries",
                data=buffer,
                file_name="executive_summaries.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
