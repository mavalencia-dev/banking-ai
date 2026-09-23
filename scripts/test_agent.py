from app.ai.agent import BankingAgent


def main():
    agent = BankingAgent()

    questions = [
        "What is my account balance?",
        "Show me my account transactions.",
        "What is a bank account?",
        "Where am I spending the most money?",
        
    ]

    for question in questions:
        print()
        print("=" * 60)
        print(f"USER: {question}")

        response = agent.run(question)

        print(f"AGENT: {response}")


if __name__ == "__main__":
    main()