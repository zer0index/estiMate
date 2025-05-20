import os
from typing import Optional
import openai
import yaml

def call_llm(
    prompt: str,
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.0,
    max_tokens: int = 1024,
    system_message: Optional[str] = None,
    **kwargs
) -> str:
    """
    Calls OpenAI's ChatCompletion API (openai>=1.0.0) with the given prompt and configuration.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set in environment.")
    client = openai.OpenAI(api_key=api_key)
    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )
    return response.choices[0].message.content 

def call_llm_with_yaml_prompt(prompt_path, context, model="gpt-4", temperature=0.2, max_tokens=2048):
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_yaml = yaml.safe_load(f)
    system_message = prompt_yaml.get("system_message", "")
    user_template = prompt_yaml["user_template"]
    # Render user prompt with context (using .format)
    user_message = user_template.format(**context)
    return call_llm(
        prompt=user_message,
        model=model,
        temperature=temperature,
        system_message=system_message,
        max_tokens=max_tokens,
    ) 