from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import Trainer, TrainingArguments
from transformers import pipeline
from src.evaluation.prompting.llama import *

dataset = load_dataset("text", data_files={"train": "path_to_your_train_file.txt",
                                           "validation": "path_to_your_validation_file.txt"})


model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=128)

def train():
    tokenized_datasets = dataset.map(tokenize_function, batched=True)
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir="./logs",
        logging_steps=10,
        evaluation_strategy="epoch",
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
    )
    trainer.train()


def evaluate_on_action_bench(model_path, data_file_path,):
    model = AutoModelForCausalLM.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    text_generator = pipeline("text-generation", model=model, tokenizer=tokenizer, device_map='auto', max_length=4096, truncation=True)
    evaluate(data_file_path, text_generator)
