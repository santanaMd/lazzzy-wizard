import subprocess
from refact_ai import RefactChat

class CodeChatbot:
    """Chatbot that utilizes indexed code to answer questions and generate unit tests."""

    def __init__(self, indexer):
        self.chat = RefactChat()
        self.indexer = indexer

    def chatbot_rag(self, question):
        """
        Processes the user's query, retrieves relevant code, and generates a response.
        If the question contains 'generate unit test', it generates a unit test.

        Args:
            question (str): User's question or command.

        Returns:
            str: Chatbot-generated response or unit test.
        """
        related_code = self.indexer.retrieve_code(question)
        
        if "generate unit test" in question.lower():
            prompt = f"Generate a unit test for the following code:\n{related_code}\nAnswer:"
            generated_test = self.chat.ask(prompt)
            test_file = "generated_test.py"
            try:
                with open(test_file, "w", encoding="utf-8") as f:
                    f.write(generated_test)
                print(f"Test generated and saved in {test_file}")
                self.run_test(test_file)
            except Exception as e:
                print(f"Error writing the test file: {e}")
            return generated_test

        prompt = f"Context:\n{related_code}\n\nQuestion: {question}\nAnswer:"
        answer = self.chat.ask(prompt)
        return answer

    def run_test(self, test_file):
        """
        Runs unit tests using pytest.

        Args:
            test_file (str): Path to the test file.
        """
        print(f"Running tests in {test_file}...")
        result = subprocess.run(["pytest", test_file], capture_output=True, text=True)
        print(result.stdout)
