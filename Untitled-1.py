from openai import OpenAI

client = OpenAI(
  api_key="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"
)

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": "write a haiku about ai"}
  ]
)

print(completion.choices[0].message);
