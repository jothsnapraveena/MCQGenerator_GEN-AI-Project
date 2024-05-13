import os
import json
import pandas as pd
import traceback
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file,get_table_data
from src.mcqgenerator.logger import logging
import streamlit as st
from langchain.callbacks import get_openai_callback
from src.mcqgenerator.mcqgenerator import generate_evaluate_chain


# loading json file
with open(r'response.json', 'r') as file:
    RESPONSE_JSON=json.load(file)

# creating title for the app
st.title('MCQs Creator Application with Langchain')

#create a form using st.form
with st.form("user_inputs"):
    #file Upload
    uploaded_file=st.file_uploader("Upload a PDF or txt file")

    #Input Fields
    mcq_count=st.number_input("No.of MCQs",min_value=3,max_value=50)

    #Subject
    subject=st.text_input("Insert subject",max_chars=30)
    #Quiz-tone
    tone=st.text_input("Complexity level of questions",max_chars=20,placeholder="simple")

    #Add button
    submit_button=st.form_submit_button("Create MCQs")
    #check if the button is clicked and all filed have input

    if submit_button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("loading...."):
            try:
                text=read_file(uploaded_file)
                with get_openai_callback() as cb:
                    response=generate_evaluate_chain(
                        {"text":text,
                         "number":mcq_count,
                         "subject":subject,
                         "tone":tone,
                         "response_json":json.dumps(RESPONSE_JSON)


                        }
                    )
            except Exception as e:
                traceback.print_exception(type(e),e,e.__traceback__)
                st.error("Error")
            else: 
                print(f"Total Tokens:{cb.total_tokens}")
                print(f"Prompt Tokens:{cb.prompt_tokens}")
                print(f"Completion Tokens:{cb.completion_tokens}")
                print(f"Total Cost:{cb.total_cost}")
                if isinstance(response,dict):
                    quiz=response.get("quiz",None)
                    if quiz is not None:
                        table_data=get_table_data(quiz)
                        if table_data is not None:
                            df=pd.DataFrame(table_data)
                            df.index=df.index+1
                            st.table(df)
                            st.text_area(label="Review",value=response["review"])
                        else:
                            st.error("Error in the table data")
                else:
                    st.write(response)

                    




