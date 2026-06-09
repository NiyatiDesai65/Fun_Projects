import anthropic

client = anthropic.Anthropic(api_key="XXXXXXX")

SYSTEM = """You are friendly data engineering coach. You help people learn data engineering.
            Keep answers short and encouraging. Remember everything user tells you 
            about themselves"""
        
history =[]

print("Data Career Chatbot - Type quit to exit\n")

while True:
    user_input= input("You: ")
    if user_input.lower()=="quit":
        break
    
    history.append({"role":"user","content":user_input})
    
    response = client.messages.create(
        model= "claude-sonnet-4-5",
        max_tokens= 500,
        temperature=0.3,
        system = SYSTEM,
        messages=history
    )        
    
    reply = response.content[0].text
    
    print(f"\nAI: {reply}\n")
    
    history.append({"role":"assistant","content": reply})
    print(f"Memory size: {len(history)} messages")
