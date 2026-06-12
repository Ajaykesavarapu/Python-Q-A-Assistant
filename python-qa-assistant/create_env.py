import os

def main():
    api_key = os.environ.get("OPENAI_API_KEY", "")
    print(f"Detected OPENAI_API_KEY: {bool(api_key)}")
    
    with open(".env", "w") as f:
        f.write("LLM_PROVIDER=openai\n")
        f.write(f"OPENAI_API_KEY={api_key}\n")
        f.write("EMBEDDING_MODEL=text-embedding-3-small\n")
        f.write("CHROMA_DB_PATH=./chroma_db\n")
        f.write("COLLECTION_NAME=stackoverflow_python\n")
        f.write("TOP_K_RETRIEVAL=5\n")
        f.write("APP_ENV=development\n")
        f.write("LOG_LEVEL=INFO\n")
        f.write("MAX_TOKENS=1024\n")
        f.write("TEMPERATURE=0.2\n")
    print("[✓] .env file created successfully!")

if __name__ == "__main__":
    main()
