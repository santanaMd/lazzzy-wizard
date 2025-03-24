from openai import OpenAI

client = OpenAI()

class RefactChat:
    def __init__(self, model="gpt-4o-mini", temperature=0.7):
        self.model = model
        self.temperature = temperature

    def ask(self, prompt):
        response = client.chat.completions.create(model=self.model,
        messages=[
            {"role": "system", "content": "You are a programming assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=self.temperature)
        return response.choices[0].message.content
