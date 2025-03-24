from code_library import CodeIndexer, CodeChatbot

def main():
    indexer = CodeIndexer()
    chatbot = CodeChatbot(indexer)
    
    repositories = [
        "https://github.com/example/repo1.git",
        "https://github.com/example/repo2.git"
    ]
    
    indexer.add_repositories(repositories)
    question = "Generate unit test for the User class"
    response = chatbot.chatbot_rag(question)
    print(response)

if __name__ == "__main__":
    main()
