"""
Configuration file for the Multi-Agent Medical Chatbot

This file contains all the configuration parameters for the project.

If you want to change the LLM and Embedding model:

you can do it by changing all 'llm' and 'embedding_model' variables present in multiple classes below.

Each llm definition has unique temperature value relevant to the specific class. 
"""

import os
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI

# Load environment variables from .env file
load_dotenv()

class AgentDecisoinConfig:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            deployment_name = os.getenv("deployment_name"),  # Replace with your Azure deployment name
            model_name = os.getenv("model_name"),  # Replace with your Azure model name
            azure_endpoint = os.getenv("azure_endpoint"),  # Replace with your Azure endpoint
            openai_api_key = os.getenv("openai_api_key"),  # Replace with your Azure OpenAI API key
            openai_api_version = os.getenv("openai_api_version"),  # Ensure this matches your API version
            temperature = 0.1  # Deterministic
        )

class ConversationConfig:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            deployment_name = os.getenv("deployment_name"),  # Replace with your Azure deployment name
            model_name = os.getenv("model_name"),  # Replace with your Azure model name
            azure_endpoint = os.getenv("azure_endpoint"),  # Replace with your Azure endpoint
            openai_api_key = os.getenv("openai_api_key"),  # Replace with your Azure OpenAI API key
            openai_api_version = os.getenv("openai_api_version"),  # Ensure this matches your API version
            temperature = 0.7  # Creative but factual
        )

class WebSearchConfig:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            deployment_name = os.getenv("deployment_name"),  # Replace with your Azure deployment name
            model_name = os.getenv("model_name"),  # Replace with your Azure model name
            azure_endpoint = os.getenv("azure_endpoint"),  # Replace with your Azure endpoint
            openai_api_key = os.getenv("openai_api_key"),  # Replace with your Azure OpenAI API key
            openai_api_version = os.getenv("openai_api_version"),  # Ensure this matches your API version
            temperature = 0.3  # Slightly creative but factual
        )
        self.context_limit = 20     # include last 20 messsages (10 Q&A pairs) in history

class RAGConfig:
    def __init__(self):
        self.vector_db_type = "qdrant"
        self.embedding_dim = 1536  # Add the embedding dimension here
        self.distance_metric = "Cosine"  # Add this with a default value
        self.use_local = True  # Add this with a default value
        self.vector_local_path = "./data/qdrant_db"  # Add this with a default value
        self.doc_local_path = "./data/docs_db"
        self.parsed_content_dir = "./data/parsed_docs"
        self.url = os.getenv("QDRANT_URL")
        self.api_key = os.getenv("QDRANT_API_KEY")
        self.collection_name = "medical_assistance_rag"  # Ensure a valid name
        self.chunk_size = 512  # Modify based on documents and performance
        self.chunk_overlap = 50  # Modify based on documents and performance
        # self.embedding_model = "text-embedding-3-large"
        # Initialize Azure OpenAI Embeddings
        self.embedding_model = AzureOpenAIEmbeddings(
            deployment = os.getenv("embedding_deployment_name"),  # Replace with your Azure deployment name
            model = os.getenv("embedding_model_name"),  # Replace with your Azure model name
            azure_endpoint = os.getenv("embedding_azure_endpoint"),  # Replace with your Azure endpoint
            openai_api_key = os.getenv("embedding_openai_api_key"),  # Replace with your Azure OpenAI API key
            openai_api_version = os.getenv("embedding_openai_api_version")  # Ensure this matches your API version
        )
        self.llm = AzureChatOpenAI(
            deployment_name = os.getenv("deployment_name"),  # Replace with your Azure deployment name
            model_name = os.getenv("model_name"),  # Replace with your Azure model name
            azure_endpoint = os.getenv("azure_endpoint"),  # Replace with your Azure endpoint
            openai_api_key = os.getenv("openai_api_key"),  # Replace with your Azure OpenAI API key
            openai_api_version = os.getenv("openai_api_version"),  # Ensure this matches your API version
            temperature = 0.3  # Slightly creative but factual
        )
        self.summarizer_model = AzureChatOpenAI(
            deployment_name = os.getenv("deployment_name"),  # Replace with your Azure deployment name
            model_name = os.getenv("model_name"),  # Replace with your Azure model name
            azure_endpoint = os.getenv("azure_endpoint"),  # Replace with your Azure endpoint
            openai_api_key = os.getenv("openai_api_key"),  # Replace with your Azure OpenAI API key
            openai_api_version = os.getenv("openai_api_version"),  # Ensure this matches your API version
            temperature = 0.5  # Slightly creative but factual
        )
        self.chunker_model = AzureChatOpenAI(
            deployment_name = os.getenv("deployment_name"),  # Replace with your Azure deployment name
            model_name = os.getenv("model_name"),  # Replace with your Azure model name
            azure_endpoint = os.getenv("azure_endpoint"),  # Replace with your Azure endpoint
            openai_api_key = os.getenv("openai_api_key"),  # Replace with your Azure OpenAI API key
            openai_api_version = os.getenv("openai_api_version"),  # Ensure this matches your API version
            temperature = 0.0  # factual
        )
        self.response_generator_model = AzureChatOpenAI(
            deployment_name = os.getenv("deployment_name"),  # Replace with your Azure deployment name
            model_name = os.getenv("model_name"),  # Replace with your Azure model name
            azure_endpoint = os.getenv("azure_endpoint"),  # Replace with your Azure endpoint
            openai_api_key = os.getenv("openai_api_key"),  # Replace with your Azure OpenAI API key
            openai_api_version = os.getenv("openai_api_version"),  # Ensure this matches your API version
            temperature = 0.3  # Slightly creative but factual
        )
        self.top_k = 5
        self.vector_search_type = 'similarity'  # or 'mmr'

        self.huggingface_token = os.getenv("HUGGINGFACE_TOKEN")

        self.reranker_model = "cross-encoder/ms-marco-TinyBERT-L-6"
        self.reranker_top_k = 3

        self.max_context_length = 8192  # (Change based on your need) # 1024 proved to be too low (retrieved content length > context length = no context added) in formatting context in response_generator code

        self.include_sources = True  # Show links to reference documents and images along with corresponding query response

        # ADJUST ACCORDING TO ASSISTANT'S BEHAVIOUR BASED ON THE DATA INGESTED:
        self.min_retrieval_confidence = 0.40  # The auto routing from RAG agent to WEB_SEARCH agent is dependent on this value

        self.context_limit = 20     # include last 20 messsages (10 Q&A pairs) in history

class MedicalCVConfig:
    def __init__(self):
        self.brain_tumor_model_path = "./agents/image_analysis_agent/brain_tumor_agent/models/brain_tumor_segmentation.pth"
        self.chest_xray_model_path = "./agents/image_analysis_agent/chest_xray_agent/models/covid_chest_xray_model.pth"
        self.skin_lesion_model_path = "./agents/image_analysis_agent/skin_lesion_agent/models/checkpointN25_.pth.tar"
        self.skin_lesion_segmentation_output_path = "./uploads/skin_lesion_output/segmentation_plot.png"
        self.llm = AzureChatOpenAI(
            deployment_name = os.getenv("deployment_name"),  # Replace with your Azure deployment name
            model_name = os.getenv("model_name"),  # Replace with your Azure model name
            azure_endpoint = os.getenv("azure_endpoint"),  # Replace with your Azure endpoint
            openai_api_key = os.getenv("openai_api_key"),  # Replace with your Azure OpenAI API key
            openai_api_version = os.getenv("openai_api_version"),  # Ensure this matches your API version
            temperature = 0.1  # Keep deterministic for classification tasks
        )

class SpeechConfig:
    def __init__(self):
        self.eleven_labs_api_key = os.getenv("ELEVEN_LABS_API_KEY")  # Replace with your actual key
        self.eleven_labs_voice_id = "21m00Tcm4TlvDq8ikWAM"    # Default voice ID (Rachel)

class ValidationConfig:
    def __init__(self):
        self.require_validation = {
            "CONVERSATION_AGENT": False,
            "RAG_AGENT": False,
            "WEB_SEARCH_AGENT": False,
            "BRAIN_TUMOR_AGENT": True,
            "CHEST_XRAY_AGENT": True,
            "SKIN_LESION_AGENT": True
        }
        self.validation_timeout = 300
        self.default_action = "reject"

class APIConfig:
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = 8000
        self.debug = True
        self.rate_limit = 10
        self.max_image_upload_size = 5  # max upload size in MB

class UIConfig:
    def __init__(self):
        self.theme = "light"
        # self.max_chat_history = 50
        self.enable_speech = True
        self.enable_image_upload = True

class HealthcarePlatformConfig:
    """Environment-backed settings for the healthcare AI/ML workflow layer.

    The new healthcare platform package reads these values through its own
    lightweight settings module as well. Keeping this object here preserves the
    original project's single Config entry point for callers that already import
    config.py.
    """

    def __init__(self):
        self.app_env = os.getenv("APP_ENV", "local")
        self.curated_store_mode = os.getenv("CURATED_STORE_MODE", "local")
        self.local_curated_path = os.getenv("LOCAL_CURATED_PATH", "data/curated_store.json")
        self.vector_store_provider = os.getenv("VECTOR_STORE_PROVIDER", "qdrant")
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")

        self.llm_provider = os.getenv("LLM_PROVIDER", "azure_openai")
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", os.getenv("azure_endpoint"))
        self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY", os.getenv("openai_api_key"))
        self.azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION", os.getenv("openai_api_version"))
        self.azure_openai_deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", os.getenv("deployment_name"))

        self.google_cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.bigquery_project_id = os.getenv("BIGQUERY_PROJECT_ID", os.getenv("GOOGLE_CLOUD_PROJECT"))
        self.bigquery_dataset = os.getenv("BIGQUERY_DATASET")
        self.cloud_healthcare_dataset = os.getenv("CLOUD_HEALTHCARE_DATASET")
        self.fhir_store = os.getenv("FHIR_STORE")
        self.hl7v2_store = os.getenv("HL7V2_STORE")

        self.enable_phi_redaction = os.getenv("ENABLE_PHI_REDACTION", "true").lower() == "true"
        self.enable_rbac = os.getenv("ENABLE_RBAC", "true").lower() == "true"
        self.enable_audit_logging = os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true"
        self.enable_human_review = os.getenv("ENABLE_HUMAN_REVIEW", "true").lower() == "true"
        self.enable_rag_eval = os.getenv("ENABLE_RAG_EVAL", "true").lower() == "true"

        self.readmission_model_path = os.getenv("READMISSION_MODEL_PATH")
        self.audit_log_path = os.getenv("AUDIT_LOG_PATH", "logs/audit_log.jsonl")

class Config:
    def __init__(self):
        self.agent_decision = AgentDecisoinConfig()
        self.conversation = ConversationConfig()
        self.rag = RAGConfig()
        self.medical_cv = MedicalCVConfig()
        self.web_search = WebSearchConfig()
        self.api = APIConfig()
        self.speech = SpeechConfig()
        self.validation = ValidationConfig()
        self.ui = UIConfig()
        self.healthcare = HealthcarePlatformConfig()
        self.eleven_labs_api_key = os.getenv("ELEVEN_LABS_API_KEY")
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.max_conversation_history = 20  # Include last 20 messsages (10 Q&A pairs) in history

# # Example usage
# config = Config()
