from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

MODEL_NAME = "sshleifer/tiny-gpt2"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

def generate_local(prompt):
    inputs = tokenizer.encode(prompt, return_tensors="pt")

    outputs = model.generate(
        inputs,
        max_length=100,
        do_sample=True,
        temperature=0.7
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)