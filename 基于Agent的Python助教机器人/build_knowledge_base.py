from langchain_community.document_loaders import (PyPDFLoader, CSVLoader, TextLoader, UnstructuredWordDocumentLoader, UnstructuredMarkdownLoader)
from unstructured.file_utils.filetype import FileType, detect_filetype
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma
import os


def load_file(file_path: str):
    """
    根据文件类型加载文档
    """
    file_type = {
        FileType.CSV: (CSVLoader, {'autodetect_encoding': True}),
        FileType.TXT: (TextLoader, {'autodetect_encoding': True}),
        FileType.DOC: (UnstructuredWordDocumentLoader, {}),
        FileType.DOCX: (UnstructuredWordDocumentLoader, {}),
        FileType.PDF: (PyPDFLoader, {}),
        FileType.MD: (UnstructuredMarkdownLoader, {})
    }
    try:
        file_type_detected = detect_filetype(file_path)
        loader_class, params = file_type[file_type_detected]
        loader = loader_class(file_path, **params)
        return loader.load()
    except Exception as e:
        raise ValueError(f"文件加载失败: {e}")

def split_documents(documents, chunk_size=150, chunk_overlap=10):
    """
    将文档切割成块
    """
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n"],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return text_splitter.split_documents(documents)

def create_vector_store(documents, embedding_model, persist_directory):
    """
    创建向量数据库存储
    """
    embeddings = HuggingFaceBgeEmbeddings(model_name=embedding_model)
    db = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    return db


if __name__ == "__main__":

    file_path = "chromadb/knowledge/Python_concept.docx"
    documents = load_file(file_path)
        
    # 分割文档
    split_docs = split_documents(documents)
    for i, chunk in enumerate(split_docs):
        print(f"分块 {i+1}: {chunk.page_content}\n")

    
    # 创建向量数据库存储
    embedding_model = "/home/yumi/model/bge-large-zh-v1.5"
    persist_directory = "chromadb"
    db = create_vector_store(split_docs, embedding_model, persist_directory)
    
    # 测试RAG检索
    # retriever = db.as_retriever(search_kwargs={"k": 2})
    # query = "列表和集合的定义是什么？"  
    # docs = retriever.invoke(query)
    # for doc in docs:
    #     print(doc.page_content)
    