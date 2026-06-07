import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="Privacy Policy Analyzer",
    page_icon="🔍",
    layout="wide"
)

API_URL = "http://localhost:8000"

tab1, tab2, tab3 = st.tabs(["🔍 Analyzer", "📂 History", "📈 Monitoring"])

# TAB 1 — ANALYZER

with tab1:
    st.title("🔍 Privacy Policy Analyzer")
    st.subheader("Know exactly what apps do with your personal data")
    st.markdown("---")

    def display_results(result):
        score = result['risk_score']
        risk_label = result['risk_label']

        if result.get('cached'):
            st.info("⚡ Returned from cache — this URL was analyzed before.")

        st.subheader("📊 Overall Risk")
        st.progress(min(score / 10, 1.0))
        st.markdown(f"**Risk Score:** {score:.2f}/10 — {risk_label}")

        if result.get('processing_time_ms'):
            st.caption(f"Processing time: {result['processing_time_ms']} ms")

        st.markdown("---")
        st.subheader("📋 Summary")
        st.write(result['summary'])

        if not result['top_risky_clauses']:
            st.success("✅ No major privacy risks detected")
            return

        st.subheader("🚨 Top Risky Clauses")
        for clause in result['top_risky_clauses']:
            risk_level = clause.get('risk_level', 'low')
            expander_label = f"⚠️ {clause['risk_type']} — {clause['confidence']}% [{risk_level.upper()}]"
            with st.expander(expander_label):
                st.markdown(f"**Clause:**\n{clause['clause']}")
                explanation = clause.get('explanation', 'No explanation provided')
                st.markdown(f"**Explanation:**\n{explanation}")

    option = st.radio(
        "Choose input method:",
        ["🌐 Paste URL", "📄 Upload PDF", "📝 Paste Text"]
    )

    if option == "🌐 Paste URL":
        url = st.text_input("Enter Privacy Policy URL:")
        top_n = st.slider("Number of top risky clauses to display:", 1, 10, 5)
        if st.button("Analyze Policy"):
            if not url:
                st.warning("Please enter a URL")
            else:
                with st.spinner("Analyzing... please wait"):
                    try:
                        response = requests.post(
                            f"{API_URL}/analyze-url",
                            json={"url": url},
                            params={"top_n": top_n}
                        )
                        result = response.json()
                        if 'detail' in result:
                            st.error(result['detail'])
                        else:
                            display_results(result)
                    except:
                        st.error("❌ Cannot connect to backend API")

    elif option == "📄 Upload PDF":
        pdf_file = st.file_uploader("Upload Privacy Policy PDF:", type=["pdf"])
        top_n = st.slider("Number of top risky clauses to display:", 1, 10, 5)
        if st.button("Analyze PDF"):
            if not pdf_file:
                st.warning("Please upload a PDF file")
            else:
                with st.spinner("Analyzing... please wait"):
                    try:
                        response = requests.post(
                            f"{API_URL}/analyze-pdf",
                            files={"file": pdf_file},
                            params={"top_n": top_n}
                        )
                        result = response.json()
                        if 'detail' in result:
                            st.error(result['detail'])
                        else:
                            display_results(result)
                    except:
                        st.error("❌ Cannot connect to backend API")

    elif option == "📝 Paste Text":
        text_input = st.text_area("Paste Privacy Policy Text:", height=200)
        top_n = st.slider("Number of top risky clauses to display:", 1, 10, 5)
        if st.button("Analyze Text"):
            if not text_input.strip():
                st.warning("Please enter some text")
            else:
                with st.spinner("Analyzing... please wait"):
                    try:
                        response = requests.post(
                            f"{API_URL}/analyze-text",
                            json={"text": text_input},
                            params={"top_n": top_n}
                        )
                        result = response.json()
                        if 'detail' in result:
                            st.error(result['detail'])
                        else:
                            display_results(result)
                    except:
                        st.error("❌ Cannot connect to backend API")

# TAB 2 — History

with tab2:
    st.title("📂 Analysis History")
    st.markdown("All previously analyzed privacy policies.")
    st.markdown("---")

    limit = st.slider("Number of records to load:", 5, 50, 20)

    if st.button("Load History"):
        try:
            response = requests.get(f"{API_URL}/history", params={"limit": limit})
            records = response.json()

            if not records:
                st.info("No analyses yet. Run your first analysis in the Analyzer tab.")
            else:
                df = pd.DataFrame(records)
                df = df[[
                    "id", "input_type", "source_url",
                    "filename", "risk_score", "risk_label",
                    "total_risky_clauses", "processing_time_ms", "created_at"
                ]]
                df.columns = [
                    "ID", "Type", "URL", "File",
                    "Risk Score", "Risk Label",
                    "Risky Clauses", "Latency (ms)", "Analyzed At"
                ]

                def color_risk(val):
                    if val == "HIGH RISK":
                        return "background-color: #FCEBEB; color: #791F1F"
                    elif val == "MEDIUM RISK":
                        return "background-color: #FAEEDA; color: #633806"
                    return "background-color: #EAF3DE; color: #27500A"

                st.dataframe(
                    df.style.applymap(color_risk, subset=["Risk Label"]),
                    use_container_width=True
                )
                st.caption(f"Showing {len(records)} most recent analyses.")

        except:
            st.error("❌ Cannot connect to backend API")

# TAB 3 — MONITORING

with tab3:
    st.title("📈 Monitoring Dashboard")
    st.markdown("System usage, performance, and error tracking.")
    st.markdown("---")

    if st.button("Load Analytics"):
        try:
            response = requests.get(f"{API_URL}/analytics")
            data = response.json()

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Analyses", data["total_analyses"])
            col2.metric("Avg Risk Score", f"{data['avg_risk_score']}/10")
            col3.metric("Avg Latency", f"{data['avg_latency_ms']} ms")
            col4.metric("Total Errors", data["total_errors"])

            st.markdown("---")
            col_left, col_right = st.columns(2)

            with col_left:
                st.subheader("Analyses by Input Type")
                if data["by_input_type"]:
                    type_df = pd.DataFrame(
                        list(data["by_input_type"].items()),
                        columns=["Input Type", "Count"]
                    )
                    st.bar_chart(type_df.set_index("Input Type"))
                else:
                    st.info("No data yet.")

            with col_right:
                st.subheader("Analyses by Risk Level")
                if data["by_risk_label"]:
                    risk_df = pd.DataFrame(
                        list(data["by_risk_label"].items()),
                        columns=["Risk Level", "Count"]
                    )
                    st.bar_chart(risk_df.set_index("Risk Level"))
                else:
                    st.info("No data yet.")

        except:
            st.error("❌ Cannot connect to backend API")