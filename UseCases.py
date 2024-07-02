import streamlit as st
import pdfplumber
from utils import *


# App title
st.set_page_config(page_title="📑 Use Cases")
st.title('👩‍🔬🔬💬 BioRAG Analyser')
st.header('📑 Your Use Cases')

if "user" not in st.session_state.keys():
    st.session_state["user"] = "Testing" # os.environ['DOMINO_STARTING_USERNAME']

use_case_df = get_use_case_dataframe(st.session_state.user)

if "use_cases" not in st.session_state.keys():
    st.session_state['use_cases'] = use_case_df['Use Case Name'].tolist()

if "new_use_case_creation" not in st.session_state.keys():
    st.session_state['new_use_case_creation'] = False

if "use_case_deletion" not in st.session_state.keys():
    st.session_state['use_case_deletion'] = False

if len(use_case_df) > 0:
    st.table(use_case_df)
    
    if st.button("Create New Use Case"):
        st.session_state['new_use_case_creation'] = True

    if st.button("Delete Use Case"):
        st.session_state['use_case_deletion'] = True

    if st.session_state['new_use_case_creation']:
        with st.form("new_use_case_form"):
            st.header("Add new Use Case")
            # Input for the use case name
            new_use_case_name = st.text_input("Enter Use Case Name")
            # File uploader for documents
            new_file_upload = st.file_uploader("Upload your pdf documents for analysis 👇",
                                            accept_multiple_files=True,
                                            type=['pdf'])
            # Submit button
            new_submit_button = st.form_submit_button(label="Submit")

            if new_submit_button:
                if not new_use_case_name:
                    st.error("Please enter a use case name.")
                elif new_use_case_name in use_case_df["Use Case Name"].tolist():
                    st.error("Use case already exists. Please select a new use case name.")
                elif not new_file_upload:
                    st.error("Please upload at least one document.")
                else:
                    with st.spinner("Creating Use Case"):
                        docs = []
                        for uploaded_file in new_file_upload:
                            if uploaded_file.type == "application/pdf":
                                with pdfplumber.open(uploaded_file) as pdf:
                                    document_text = extract_text_from_pdf(pdf)
                                    documents = text_splitter.create_documents([document_text])
                                    for page in documents:
                                        page.metadata = {'source':f"{uploaded_file.name}"}
                                    docs += documents
                            else:
                                pass
                        try:
                            docs = remove_duplicate_documents(docs)
                            docs_to_vectordb(docs, f"{st.session_state.user}_{new_use_case_name}")
                        except Exception as e:
                            st.sidebar.error(f"Something went wrong: {e}")

                        add_use_case(st.session_state.user, new_use_case_name, list(set([uploaded_file.name for uploaded_file in new_file_upload])))
                        st.session_state['use_cases'] = use_case_df['Use Case Name'].tolist()
                        use_case_df = get_use_case_dataframe(st.session_state.user)
                        st.session_state['new_use_case_creation'] = False
                    st.success("Use Case Created!")
        st.button("Clear new use case form")

    if st.session_state['use_case_deletion']:
        with st.form("delete_use_case_form"):
            st.header("Delete Existing Use Case")
            # Input for the use case name
            deletion_use_case_name = st.text_input("Enter Use Case Name you want to be deleted")
            st.warning("⚠️ This action cannot be undone")
            delete_button = st.form_submit_button(label="Submit")

            if delete_button:
                if not deletion_use_case_name:
                    st.error("Please enter a use case name.")
                elif deletion_use_case_name not in use_case_df["Use Case Name"].tolist():
                    st.error(f"Cannot find {deletion_use_case_name} in use cases. Current use cases are: {use_case_df['Use Case Name'].tolist()}")
                else:
                    with st.spinner("Deleting Use Case"):
                        
                        delete_use_case(st.session_state.user, deletion_use_case_name)
                        use_case_df = get_use_case_dataframe(st.session_state.user)
                        st.session_state['use_cases'] = use_case_df['Use Case Name'].tolist()
                        st.session_state['use_case_deletion'] = False
                    st.success("Use Case Deleted!")
        st.button("Clear delete use case form")


else:
    st.warning("⚠️You have no use cases! Please create one below 👇")
    # Create a form
    with st.form("first_use_case_form"):
        # Input for the use case name
        use_case_name = st.text_input("Enter Use Case Name")
        # File uploader for documents
        file_upload = st.file_uploader("Upload your pdf documents for analysis 👇",
                                          accept_multiple_files=True,
                                          type=['pdf'])
        # Submit button
        submit_button = st.form_submit_button(label="Submit")

    if submit_button:
        if not use_case_name:
            st.error("Please enter a use case name.")
        elif use_case_name in use_case_df["Use Case Name"].tolist():
            st.error("Use case already exists. Please select a new use case name.")
        elif not file_upload:
            st.error("Please upload at least one document.")
        
        else:
            with st.spinner("Creating Use Case"):
                docs = []
                for uploaded_file in file_upload:
                    if uploaded_file.type == "application/pdf":
                        with pdfplumber.open(uploaded_file) as pdf:
                            document_text = extract_text_from_pdf(pdf)
                            documents = text_splitter.create_documents([document_text])
                            for page in documents:
                                page.metadata = {'source':f"{uploaded_file.name}"}
                            docs += documents
                    else:
                        pass
                try:
                    docs = remove_duplicate_documents(docs)
                    docs_to_vectordb(docs, f"{st.session_state.user}_{use_case_name}")
                except Exception as e:
                    st.sidebar.error(f"Something went wrong: {e}")

                add_use_case(st.session_state.user, use_case_name, list(set([uploaded_file.name for uploaded_file in file_upload])))
                use_case_df = get_use_case_dataframe(st.session_state.user)
                st.session_state['use_cases'] = use_case_df['Use Case Name'].tolist()
                st.success("Use Case Created!")
                st.button("View Use Cases")