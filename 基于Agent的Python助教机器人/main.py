
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType, tool
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from langchain.schema import StrOutputParser
from datetime import datetime
import logging
import os
import ast

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

chat_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)


embedding_model = "BAAI/bge-large-zh-v1.5"
persist_directory = "chromadb"
embeddings = HuggingFaceBgeEmbeddings(model_name=embedding_model)
db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
retriever = db.as_retriever(search_kwargs={"k": 1})

def initialize_rag_chain(retriever, chat_model):
    """
    初始化 RAG 链
    """
    SYSTEMPL = """你是一名Python助教机器人，负责根据所提供的知识内容回答问题。注意，不在知识库里面的内容回答。
    以下是知识内容：
    {context}
    请回答以下问题：
    {input}
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEMPL),
        ("human", "{input}"),
    ])
    question_answer_chain = create_stuff_documents_chain(chat_model, prompt)
    return create_retrieval_chain(retriever, question_answer_chain)

rag_chain = initialize_rag_chain(retriever, chat_model)



@tool
def check_code(code: str):
    """
    检查学生代码并提供建议
    """
    try:
        ast.parse(code)
        return "代码语法正确，没有发现明显问题。"
    except SyntaxError as e:
        return f"代码存在语法错误：{e.msg}\n建议修复：{e.text}"

@tool
def explain_error(error_message: str):
    """
    解释报错信息
    """
    prompt = f"""你是一名Python助教机器人，负责用中文解释报错信息。
    以下是报错信息：
    {error_message}
    请用简单易懂的中文解释这个报错信息，并提供修复建议。"""
    chain = ChatPromptTemplate.from_template(prompt) | chat_model | StrOutputParser()
    return chain.invoke({"error_message": error_message})

@tool
def calculate(expression: str):
    """
    计算数学表达式
    """
    try:
        result = eval(expression)
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算错误: {e}"

@tool
def ask_python_knowledge(query: str):
    """
    咨询 Python 知识点
    """
    try:
        retrieved_docs = retriever.invoke(query)
        context = "\n".join([doc.page_content for doc in retrieved_docs])
        print(f"RAG召回的知识：{context}")
        # 调用 RAG 链回答问题
        response = rag_chain.invoke({"context": context, "input": query})
        return response["answer"]
    except Exception as e:
        return f"查询失败: {e}"

tools = [check_code, explain_error, calculate, ask_python_knowledge]

agent = initialize_agent(
    tools=tools,
    llm=chat_model,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
)

conversation_history = ChatMessageHistory()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r") as file:
        return HTMLResponse(content=file.read())

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    query = data.get("query")

    try:
        logger.info("开始调用 Agent 处理用户输入...")

        context = "\n".join([msg.content for msg in conversation_history.messages])
        print(f"对话历史：\n{context}\n当前问题：{query}")

        SYSTEM_PROMPT = """
        你是一名 Python 助教机器人，名字叫小林，负责帮助学生解决 Python 相关问题。
        回答应尽量简洁。
        如果学生的问题涉及 Python 知识点，请调用 "ask_python_knowledge" 工具，从知识库中获取知识再回答。
        以下是之前的对话历史：{context}
        当前学生的问题是：{query}
        """
        response = agent.run(SYSTEM_PROMPT.format(context=context, query=query))
   
        conversation_history.add_user_message(query) 
        conversation_history.add_ai_message(response) 

        logger.info(f"Agent 返回结果: {response}")
        return {
            "response": response
        }
    except Exception as e:
        logger.error(f"处理查询时出错: {e}")
        return {"error": "内部服务器错误"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
