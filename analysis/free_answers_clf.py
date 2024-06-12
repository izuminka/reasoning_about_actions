import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.utils.data import DataLoader
from datasets import load_dataset, Dataset

device = torch.device("cpu")  # "cuda:0" if torch.cuda.is_available() else
model_name = 'roberta-base'
path_to_fine_tuned_model = './roberta_finetuned_models/checkpoint-2500_roberta'
ROBERTA_MODEL_TOKENIZER = AutoTokenizer.from_pretrained(model_name)
ROBERTA_MODEL = AutoModelForSequenceClassification.from_pretrained(path_to_fine_tuned_model).to(device)
ROBERTA_MODEL_EVAL_BATCH_SIZE = 128  # Define the batch size for inference

def robeta_model_preprocess_function(batch):
    responses = [str(response) if response else "" for response in batch["s1"]]
    labels = [str(label) if label else "" for label in batch["s2"]]
    return ROBERTA_MODEL_TOKENIZER(responses, labels, padding="max_length", max_length=512, truncation=False)


if __name__ == '__main__':
    data_path = 'blocksworld_topn.jsonl'

    test_data = load_dataset('json', data_files={'test': data_path})
    test_data = test_data['test'].map(robeta_model_preprocess_function, batched=True)
    test_data.set_format(type='torch', columns=['input_ids', 'attention_mask'])

    # Initialize DataLoader for test dataset
    test_dataloader = DataLoader(test_data, batch_size=ROBERTA_MODEL_EVAL_BATCH_SIZE)

    # get the predictions and probabilities
    predictions = []
    probabilities = []
    ROBERTA_MODEL.eval()
    for batch in test_dataloader:
        with torch.no_grad():
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            outputs = ROBERTA_MODEL(input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)
            predictions.extend(torch.argmax(probs, dim=-1).cpu().numpy())
            probabilities.extend(probs.cpu().numpy())

            print(predictions)
            print(probabilities)