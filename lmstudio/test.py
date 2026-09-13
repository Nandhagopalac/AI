from langchain_openai import ChatOpenAI
import time

# Initialize model
chat_model = ChatOpenAI(
    model_name="prism-ml/bonsai-27b",
    temperature=0.7,
    base_url="http://localhost:1234/v1"
)

def chat_with_formatting(prompt):
    """
    Chat with the model and return formatted results.
    Returns a dictionary with response text and timing info.
    """
    
    start_time = time.time()
    
    # Get raw response
    raw_response = chat_model.invoke(prompt)
    
    elapsed_time = time.time() - start_time
    
    # Format as bullet points (clean up the response)
    lines = [line.strip() for line in str(raw_response).split("\n") if line.strip()]
    formatted_lines = ["• " + line for line in lines]
    formatted_text = "\n".join(formatted_lines)
    
    return {
        "response": formatted_text,
        "time_seconds": elapsed_time,
        "raw_response": raw_response  # Keep original if needed
    }

# Usage example
result = chat_with_formatting("Tell me who is Chinnaswamy?")

print("=" * 50)
print("📋 RESPONSE:")
print("-" * 30)
print(result["response"])
print("-" * 30)
print(f"⏱️ Response time: {result['time_seconds']:.2f} seconds")
print("=" * 50)
