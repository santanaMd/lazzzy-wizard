from code_library import CodeIndexer, CodeChatbot

def main():
    indexer = CodeIndexer()
    chatbot = CodeChatbot(indexer)
    
    repositories = [
        "https://github.com/santanaMd/lazzzy-wizard.git"
    ]
    
    indexer.add_repositories(repositories)
    question = "Generate unit test for the code_library classes"
    response = chatbot.chatbot_rag(question)
    print(response)

if __name__ == "__main__":
    main()
