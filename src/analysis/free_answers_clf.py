
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from torch.utils.data import DataLoader
import os

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

def preprocess_function(batch):
    responses = [str(response) if response else "" for response in batch["response"]]
    labels = [str(label) if label else "" for label in batch["label"]]
    return tokenizer(responses, labels, padding="max_length", max_length=512, truncation=False)

if __name__ == '__main__':
    device = torch.device("cpu") #"cuda:0" if torch.cuda.is_available() else
    model_name = 'roberta-base'
    path_to_fine_tuned_model = './roberta_finetuned_models/checkpoint-2500_roberta'
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(path_to_fine_tuned_model).to(device)

    # test_data = [{'s1': 'sdfsdf', 's2:': 'sdfsdf'}]
    # # test_data = test_data.map(preprocess_function, batched=True)
    #
    # # Set the format for PyTorch tensors
    # test_data.set_format(type='torch', columns=['input_ids', 'attention_mask'])
    #
    # # Initialize DataLoader for test dataset
    # batch_size = 128  # Define the batch size for inference
    # test_dataloader = DataLoader(test_data, batch_size=batch_size)
    #
    # # get the predictions and probabilities
    # predictions = []
    # probabilities = []
    # model.eval()
    # for batch in test_dataloader:
    #     with torch.no_grad():
    #         input_ids = batch['input_ids'].to(device)
    #         attention_mask = batch['attention_mask'].to(device)
    #         outputs = model(input_ids, attention_mask=attention_mask)
    #         logits = outputs.logits
    #         probs = torch.softmax(logits, dim=-1)
    #         predictions.extend(torch.argmax(probs, dim=-1).cpu().numpy())
    #         probabilities.extend(probs.cpu().numpy())