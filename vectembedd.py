from ollama import embeddings

response = embeddings(
    model='nomic-embed-text:latest',
    prompt='What is Artificial Intelligence?'
)

print(response ['embedding'])