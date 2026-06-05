import anthropic
import json
import pandas as pd
import time

client = anthropic.Anthropic(api_key=XXXXXXX)
total_input_tokens=0
total_output_tokens=0

emails = [
    "Hi, I'm Sarah. My order #101 never arrived. Very unhappy!",
    "Hello, this is Tom. Love your product, works perfectly!",
    "I'm Priya. Order #103 arrived damaged. Please help.",
    "Hey it's Mike. Just checking status of order #104.",
    "This is Lisa. Wrong item delivered for order #105!",
]

def safe_parse_json(reply):
    reply = reply.strip()
    if reply.startswith("```"):
        reply = reply.split("```")[1]
        if reply.startswith("json"):
            reply = reply[4:]
        reply = reply.strip()
    return json.loads(reply)

#retry logic
def extract_with_retry(email_text, max_tries=3):
    global total_input_tokens, total_output_tokens
    
    for attempt in range(max_tries):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=300,
                temperature=0,
                system="""Reply ONLY with valid JSON, no markdown.
                        Use exactly: {"name":"...","issue":"...","sentiment":"..."}""",
                messages=[{"role": "user",
                            "content": f"Extract info from: {email_text}"}]
            )
            
            total_input_tokens += response.usage.input_tokens
            total_output_tokens += response.usage.output_tokens
            
            return safe_parse_json(response.content[0].text)
            
        except Exception as e:
            print(f"Attempts {attempt+1} failed : {e}")
            if attempt < max_tries-1:
                time.sleep(2)
            else:
                return {"name":"Error","Issue":str(e),"sentiment":"Unknown"}
               

results = []

for i,email in enumerate(emails):
    print(f"Processing email {i+1} of {len(emails)}.....")
    data = extract_with_retry(email)
    results.append(data)
    
df = pd.DataFrame(results)
print("\n--Results--\n")
print(df)
df.to_csv("pipeline_costtracking.csv",index=False)

#Cost
total_tokens = total_input_tokens + total_output_tokens
cost = ((total_input_tokens/1_000_000)*3) + ((total_output_tokens/1_000_000)*15)

print("\n -------Cost Report-----------")
print(f"Input Tokens : {total_input_tokens}")
print(f"Output Tokens : {total_output_tokens}")
print(f"Total Tokens : {total_tokens}")
print(f"Estimated Cost : {cost}")

#--- Calculating monthly Cost and Scaling Up the emails---------

emails_per_day = 1000

cost_per_email = cost / len(emails)
daily_cost     = cost_per_email * emails_per_day
monthly_cost   = daily_cost * 30

print(f"Cost per email:  ${cost_per_email:.6f}")
print(f"Daily cost:      ${daily_cost:.2f}")
print(f"Monthly cost:    ${monthly_cost:.2f}")




