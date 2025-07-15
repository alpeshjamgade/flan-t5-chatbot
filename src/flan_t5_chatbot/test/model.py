from sympy.printing.numpy import const
from transformers import T5ForConditionalGeneration, T5Tokenizer, AutoTokenizer, AutoModelForSeq2SeqLM

llm_model = "google/flan-t5-large"

model = AutoModelForSeq2SeqLM.from_pretrained(llm_model)

tokenizer = AutoTokenizer.from_pretrained(llm_model)

print(model.config)

import torch

device = "cpu"
if  torch.cuda.is_available():
    device = "cuda"
elif torch.backends.mps.is_available():
    device = "mps"

model.to(device)

sentence = "Explain dividend in stock market"

input_ids = tokenizer(sentence, return_tensors="pt").input_ids.to(device)

print(input_ids)

outputs = model.generate(input_ids,
                         min_length=256,
                         max_new_tokens=1024,
                         length_penalty=1.4,
                         num_beams=16,
                         no_repeat_ngram_size=2,
                         temperature=0.7,
                         top_k=150,
                         top_p=0.92,
                         repetition_penalty=2.1,
                         early_stopping=True
                         )

output_text_flan_t5 = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]

print(output_text_flan_t5)