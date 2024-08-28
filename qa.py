import os
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chat_models import ChatOpenAI
from transformers import GPT2TokenizerFast
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain.chains import create_citation_fuzzy_match_chain
import chromadb


load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

class QA:

    folder_path = "embeddings/"

    def __init__(self,year):
        self.db_path=f"{self.folder_path}{year}.db"
        self.client_settings = chromadb.config.Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=self.db_path,
            anonymized_telemetry=False
        )

    def get_chunks(self,folder_path):
        docs=[]

        for dirpath, dirnames, filenames in os.walk(folder_path):
            for file in filenames:
                try: 
                    loader = PyPDFLoader(os.path.join(dirpath, file))
                    docs.extend(loader.load_and_split())
                except Exception as e: 
                    pass

        tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
        
        def count_tokens(text: str) -> int:
            return len(tokenizer.encode(text))
    
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=24,length_function = count_tokens)
        return text_splitter.split_documents(docs)


    def init_chromadb(self,folder_path):
        
        if os.path.exists(self.db_path):
            print(f"Database file already exists at {self.db_path}. \nLoading existing database...")
            self.vectorstore = Chroma(
                collection_name="langchain_store",
                embedding_function=embeddings,
                client_settings=self.client_settings,
                persist_directory=self.db_path,
            )
            return
        
        print(f"Creating new database at {self.db_path}...")

        chunks=self.get_chunks(folder_path)
        
        self.vectorstore = Chroma(
            collection_name="langchain_store",
            embedding_function=embeddings,
            client_settings=self.client_settings,
            persist_directory=self.db_path,
        )

        self.vectorstore.add_documents(documents=chunks, embedding=embeddings)
        self.vectorstore.persist()

    def format_context(self,docs):
        context=""
        for doc in docs:
            context = context + doc.metadata["source"] + "-" + str(doc.metadata["page"])+"\n"+doc.page_content+"\n\n"
        return context
    
    def get_metadata(self,docs):
        if(len(docs)>0):
            return docs[0].metadata["source"] + "-" + str(docs[0].metadata["page"])
        return ""
    
    def get_citation(self,context,query):
        model = ChatOpenAI(model='gpt-3.5-turbo')    
        citation_chain = create_citation_fuzzy_match_chain(model)
        result = citation_chain.run(question=query, context=context)
        citation=""
        for fact in result.answer:
            for span in fact.get_spans(context):
                citation+= self.highlight(context, span) + "\t"
        return citation
    
    def highlight(self,text, span):
        return (
            "..."
            + text[span[0] - 20 : span[0]]
            + "*"
            + text[span[0] : span[1]]
            + "*"
            + text[span[1] : span[1] + 20]
            + "..."
        )
    
    def get_answer(self,docs,query,response_options):
        model = ChatOpenAI(model='gpt-3.5-turbo')
        answer_chain = load_qa_chain(llm=model, chain_type="stuff")
        question_with_response_options=f"{query} Response Options: {response_options}"
        answer = answer_chain.run(input_documents=docs, question=question_with_response_options)
        return answer
      

    def query(self,query,response_options=""):
        retriever=self.vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})
        docs=retriever.get_relevant_documents(query)
        context=self.format_context(docs)
        metadata=self.get_metadata(docs)
        return self.get_citation(context,query),self.get_answer(docs,query,response_options),metadata
