"""
Interactive Chatbot using Gemini API with LangChain
Features: Conversation memory, streaming responses, chat history
"""
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Load API key from environment variable
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("ERROR: GOOGLE_API_KEY environment variable not set!")
    print("Set it with: $env:GOOGLE_API_KEY='your_api_key_here'")
    exit()

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # stable model
    temperature=0.7,
    max_output_tokens=2048
)

# Create chat prompt with conversation history
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant. Be friendly, informative, and concise."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

# Create the chain
chain = prompt | llm

# Store for chat histories (keyed by session_id)
chat_histories = {}

def get_session_history(session_id: str):
    """Retrieve or create chat history for a session"""
    if session_id not in chat_histories:
        chat_histories[session_id] = InMemoryChatMessageHistory()
    return chat_histories[session_id]

# Create conversational chain with memory
conversational_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)

def chat(user_input: str, session_id: str = "default") -> str:
    """Send a message and get a response with conversation context"""
    config = {"configurable": {"session_id": session_id}}
    response = conversational_chain.invoke(
        {"input": user_input},
        config=config
    )
    return response.content

def clear_history(session_id: str = "default"):
    """Clear chat history for a session"""
    if session_id in chat_histories:
        chat_histories[session_id].clear()
        print("✓ Chat history cleared!")

def print_separator():
    print("\n" + "="*60 + "\n")

def main():
    """Interactive chatbot loop"""
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "GEMINI CHATBOT WITH LANGCHAIN" + " "*14 + "║")
    print("╚" + "="*58 + "╝")
    print("\nCommands:")
    print("  • Type your message to chat")
    print("  • 'clear' - Clear conversation history")
    print("  • 'quit' or 'exit' - Exit chatbot")
    print_separator()
    
    session_id = "main_session"
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Check for commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye! Thanks for chatting!")
                break
            
            if user_input.lower() == 'clear':
                clear_history(session_id)
                continue
            
            # Get bot response
            print("\n🤖 Gemini: ", end="", flush=True)
            response = chat(user_input, session_id)
            print(response)
            print_separator()
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for chatting!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'quit' to exit.")
            print_separator()

if __name__ == "__main__":
    main()