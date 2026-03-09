import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain.embeddings import HuggingFaceEmbeddings
from few_shots import few_shots
from langchain.vectorstores import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import FewShotPromptTemplate
from langchain_experimental.sql import SQLDatabaseChain

load_dotenv()

def get_few_shot_db_chain():
    from langchain_community.utilities import SQLDatabase

    db_user = "root"
    db_password = "root"
    db_host = "localhost"
    db_name = "atliq_tshirts"

    db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}",sample_rows_in_table_info=3)

    llm = ChatOpenAI(
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    model_name="openai/gpt-4o-mini",
    temperature=0.1,
    )

    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    to_vectorize = [
    " ".join(str(v) for v in example.values())
    for example in few_shots
    ]
    clean_metadata = [
    {
        "Question": item["Question"],
        "SQLQuery": item["SQLQuery"],
        "SQLResult": item["SQLResult"],
        "Answer": item["Answer"]
    }
    for item in few_shots
    ]
    vectorstore = Chroma.from_texts(to_vectorize, embedding, metadatas=clean_metadata)
    example_selector = SemanticSimilarityExampleSelector(vectorstore=vectorstore, k=2)

    example_prompt = PromptTemplate(
    input_variables=["Question", "SQLQuery", "SQLResult", "Answer"],
    template="""
    Question: {Question}
    SQLQuery: {SQLQuery}
    SQLResult: {SQLResult}
    Answer: {Answer}
    """
    )
    mysql_prompt = """You are a MySQL expert. Given an input question, first create a syntactically correct MySQL query to run, then look at the results of the query and return the answer in English.

    Never use Markdown backticks (```) or the word 'sql' in your response. 

    Target Database Tables and Columns:
    {table_info}

    Question: {input}"""	

    prompt_suffix = """
    Only use following tables:
    {table_info}

    Question: {input}
    """

    few_short_templete = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=example_prompt,
        prefix=mysql_prompt,
        suffix=prompt_suffix,
        input_variables=["input", "table_info", "top_k"],
    )

    new_chain = SQLDatabaseChain.from_llm(
    llm,
    db,
    prompt=few_short_templete,
    verbose=False,
    return_intermediate_steps=False,
    return_sql=False
    )

    return new_chain