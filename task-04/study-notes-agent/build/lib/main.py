import os
from dotenv import load_dotenv
import asyncio
from agent_config import create_study_agent
from agents import RunConfig

async def main():
    load_dotenv()  # Load environment variables from .env

    print("Initializing Study Helper Agent...")
    try:
        agent = create_study_agent()
        print("Study Helper Agent initialized.")
    except ValueError as e:
        print(f"Error initializing agent: {e}")
        print("Please ensure GEMINI_API_KEY is set in your .env file.")
        return

    while True:
        file_path = input("\nEnter the path to a PDF document (or 'q' to quit): ")
        if file_path.lower() == 'q':
            break

        if not os.path.exists(file_path):
            print("File not found. Please enter a valid path.")
            continue

        print(f"Processing PDF: {file_path}")

        # The agent's instructions handle calling read_pdf_document when a file path is provided.
        # We just need to give the agent the instruction with the file path.
        agent_response = await agent.run(f"Please process this PDF file: {file_path}", run_config=RunConfig(max_tool_iterations=50, max_iterations=50))
        print("\nAgent Response:")
        print(agent_response.output)

        while True:
            action = input("\nDo you want a 'summary', a 'quiz', or 'new' PDF (or 'q' to quit)? ").lower()
            if action == 'q':
                return
            elif action == 'new':
                break
            elif action == 'summary':
                summary_response = await agent.run("Please provide a summary of the document.", run_config=RunConfig(max_tool_iterations=50, max_iterations=50))
                print("\nSummary:")
                print(summary_response.output)
            elif action == 'quiz':
                quiz_response = await agent.run("Please generate a quiz (MCQs and open-ended questions) from the document.", run_config=RunConfig(max_tool_iterations=50, max_iterations=50))
                print("\nQuiz:")
                print(quiz_response.output)
            else:
                print("Invalid action. Please choose 'summary', 'quiz', 'new', or 'q'.")

if __name__ == "__main__":
    asyncio.run(main())