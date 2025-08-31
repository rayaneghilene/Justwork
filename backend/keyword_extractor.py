import json, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = AutoModelForCausalLM.from_pretrained("numind/NuExtract-tiny", trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained("numind/NuExtract-tiny", trust_remote_code=True)
model.to(device).eval()

def predict_keywords(text: str, schema: str, examples=None):
    if examples is None:
        examples = ["", "", ""]
    schema = json.dumps(json.loads(schema), indent=4)

    input_llm = "<|input|>\n### Template:\n" + schema + "\n"
    for i in examples:
        if i != "":
            input_llm += "### Example:\n" + json.dumps(json.loads(i), indent=4) + "\n"

    input_llm += "### Text:\n" + text + "\n<|output|>\n"
    input_ids = tokenizer(input_llm, return_tensors="pt", truncation=True, max_length=4000).to(device)

    output = tokenizer.decode(model.generate(**input_ids)[0], skip_special_tokens=True)
    return output.split("<|output|>")[1].split("<|end-output|>")[0]