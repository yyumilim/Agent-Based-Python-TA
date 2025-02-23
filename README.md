# Agent-Based-Python-TA   基于Agent的Python助教机器人

一个基于 LangChain Agent 和 OpenAI GPT-3.5 的 Python 助教机器人，支持代码检查、报错解释、Python 知识点问答和数学计算功能。

### 项目特点
- **Agent 调用 Tools**：通过 LangChain Agent 动态调用自定义 Tools，实现多任务处理。
- **多轮对话**：支持上下文感知的多轮对话，提升用户体验。
- **知识库检索**：使用 LangChain RAG 和 Chroma 实现知识库问答，确保回答的准确性和相关性。
- **易于扩展**：模块化设计，支持快速添加新的 Tools 或功能。

### 技术栈
- **大模型**：OpenAI GPT-3.5-turbo
- **Agent 框架**：LangChain Agent
- **知识库检索**：LangChain RAG + Chroma
- **后端框架**：FastAPI
- **前端**：HTML + JavaScript

### 功能列表
1. **代码检查**：检查 Python 代码的语法错误并提供修复建议。
   ![代码检查功能](images/test_check_code.png)
   ![代码检查功能agent调用](images/agent_function_call_check_code.png)
3. **报错解释**：用中文解释 Python 报错信息，并提供修复建议。
   ![报错解释功能](images/test_explain_error.png)
   ![报错解释功能agent调用](images/agent_function_call_explain_error.png)
5. **Python 知识点问答**：基于知识库检索，回答 Python 相关问题。
   ![知识点问答功能](images/test_ask_python_knowledge.png)
   ![知识点问答功能agent调用](images/agent_function_call_ask_python_knowledge.png)
7. **数学计算**：支持简单的数学表达式计算。
   ![数学计算功能](images/test_calculate.png)
   ![数学计算功能agent调用](images/agent_function_call_calculate.png)


