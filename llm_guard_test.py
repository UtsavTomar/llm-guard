"""
LLM Guard - Focused on features beyond OpenAI moderation API
Key features: Prompt Injection, Secrets Detection, Token Limits, Relevance, No Refusal
"""

import os
# from openai import OpenAI
from llm_guard import scan_output, scan_prompt
from llm_guard.input_scanners import PromptInjection, TokenLimit, Secrets
from llm_guard.output_scanners import NoRefusal, Relevance

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Focus on features OpenAI moderation doesn't provide
input_scanners = [
    PromptInjection(),  # Detect prompt injection and jailbreak attempts (built-in)
    # TokenLimit(max_tokens=1000),  # Control input length
    Secrets()  # Detect API keys, passwords, tokens
]

output_scanners = [
    NoRefusal(),  # Check if AI refuses to answer appropriately
    Relevance()  # Ensure response stays on topic
]

# Test prompt with potential security concerns
prompt = """
Here is my OpenAI API key: sk-ABC1234567890abcdefg1234567890abc
"""

print("=== INPUT SCANNING ===")
sanitized_prompt, results_valid, results_score = scan_prompt(input_scanners, prompt)

print(f"Original prompt: {prompt}")
print(f"Sanitized prompt: {sanitized_prompt}")
print(f"Scanner results: {results_score}")
print(f"All valid: {results_valid}")

if not all(results_valid.values()):
    print("❌ Input blocked by LLM Guard")
    exit(1)

print("✅ Input passed LLM Guard checks")

# # Get response from OpenAI
# response = client.chat.completions.create(
#     model="gpt-4o-mini",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": sanitized_prompt},
#     ],
#     temperature=0,
#     max_tokens=200,
# )

# response_text = response.choices[0].message.content

# print("\n=== OUTPUT SCANNING ===")
# sanitized_response, results_valid, results_score = scan_output(
#     output_scanners, sanitized_prompt, response_text
# )

# print(f"Original response: {response_text}")
# print(f"Sanitized response: {sanitized_response}")
# print(f"Scanner results: {results_score}")
# print(f"All valid: {results_valid}")

# if not all(results_valid.values()):
#     print("❌ Output blocked by LLM Guard")
#     exit(1)

# print("✅ Output passed LLM Guard checks")
# print(f"\nFinal safe response: {sanitized_response}")


