import streamlit as st
import pandas as pd
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import sqlite3
load_dotenv()

def get_sql_query_from_text(user_query):
    groq_prompt = ChatPromptTemplate.from_template(
        """
                    You are an expert in converting English questions to SQL query!
                    The SQL database has the name STUDENT and has the following columns - NAME, COURSE, 
                    SECTION and MARKS. For example, 
                    Example 1 - How many entries of records are present?, 
                        the SQL command will be something like this SELECT COUNT(*) FROM STUDENT;
                    Example 2 - Tell me all the students studying in Data Science COURSE?, 
                        the SQL command will be something like this SELECT * FROM STUDENT 
                        where COURSE="Data Science"; 
                    also the sql code should not have ``` in beginning or end and sql word in output.
                    Now convert the following question in English to a valid SQL Query: {user_query}. 
                    No preamble, only valid SQL please
                                                       """
    )
    model="llama3-8b-8192"
    llm = ChatGroq(
        model_name = model
    )
    chain = groq_prompt | llm | StrOutputParser()
    sql_query = chain.invoke({"user_query": user_query})
    return sql_query

def get_data_from_sql(sql_query):
    database = 'student.db'
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.execute(sql_query)
        columns = [desc[0] for desc in cursor.description]  # Get column names
        data = cursor.fetchall()
        return pd.DataFrame(data, columns=columns)  # Return as DataFrame

def get_full_database():
    database = 'student.db'
    with sqlite3.connect(database) as conn:
        query = "SELECT * FROM STUDENT"
        df = pd.read_sql_query(query, conn)
    return df

def main():
    st.set_page_config(page_title='Text-to-SQL', page_icon='📊', layout='centered')
    
    st.markdown("""
        <style>
            .main-title {text-align: center; color: #4CAF50; font-size: 36px; font-weight: bold;}
            .query-text {color: #FF5733; font-size: 20px;}
            .stButton>button {background-color: #008CBA; color: white; font-size: 18px; padding: 10px;}
            .stTextInput>div>div>input {font-size: 18px;}
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="main-title">Talk to Your Database 📊</p>', unsafe_allow_html=True)
    
    st.markdown('<p class="query-text">Current Database:</p>', unsafe_allow_html=True)
    st.dataframe(get_full_database())
    
    user_query = st.text_input('Enter your query:', placeholder='E.g., Show all students with marks above 80')
    submit = st.button('Generate SQL & Fetch Data')
    
    if submit:
        sql_query = get_sql_query_from_text(user_query)
        data = get_data_from_sql(sql_query)
        
        st.markdown('<p class="query-text">Query to fetch data is:</p>', unsafe_allow_html=True)
        st.code(sql_query, language='sql')
        
        st.markdown('<p class="query-text">Results:</p>', unsafe_allow_html=True)
        st.dataframe(data)  # Display results in a table

if __name__ == '__main__':
    main()
