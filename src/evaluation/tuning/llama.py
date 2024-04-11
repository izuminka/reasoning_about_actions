import argparse
import json
import os
from torch.utils.data import DataLoader
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import Trainer, TrainingArguments

DEFAULT_EPOCHS = 3

class Llama:
    def __init__(
            self,
            model,
            input_file_path,
            model_save_path,
            context_length,
            huggingface_token,
            huggingface_cache_dir = None,
            epochs = DEFAULT_EPOCHS
        ):
        self.model_name = model
        self.train_file_path = os.path.join(input_file_path, 'train.jsonl')
        self.eval_file_path = os.path.join(input_file_path, 'eval.jsonl')
        self.test_file_path = os.path.join(input_file_path, 'test.jsonl')
        self.model_save_path = model_save_path
        self.context_length = context_length
        self.huggingface_cache_dir = huggingface_cache_dir
        self.huggingface_token = huggingface_token
        self.epochs = epochs
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            cache_dir = self.huggingface_cache_dir,
            token = self.huggingface_token
        )
        self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            # device_map = 'auto',
            cache_dir = self.huggingface_cache_dir,
            token = self.huggingface_token
        )
    
    def tokenize_function(self, text):
        return self.tokenizer(
            text,
            padding = "max_length",
            truncation = True,
            max_length = self.context_length,
            add_special_tokens = False
        )
        # .to('cuda')
    
    def prepare_data(self, file_path, is_test=False):
        with open(file_path, 'r') as f:
            data = [json.loads(jline) for jline in f.readlines()]
        
        dataset = []
        for instance in data:
            if is_test:
                dataset.append(self.tokenize_function(instance['prompt']))
            else:
                prompt = self.tokenize_function(self.tokenizer.bos_token + instance['prompt'])['input_ids']
                answer = self.tokenize_function(instance['answer'] + self.tokenizer.eos_token)['input_ids']
                print(len(prompt), len(answer))
                print(len(prompt+answer))
                dataset.append({
                    'input_ids': prompt + answer,
                    'attention_mask': [1]*len(prompt) + [1]*len(answer),
                    'labels': [-100]*len(prompt) + answer
                })
        return dataset

    def train(self):
        training_data = self.prepare_data(self.train_file_path)
        validation_data = self.prepare_data(self.eval_file_path)
        
        training_args = TrainingArguments(
            output_dir = self.model_save_path,
            num_train_epochs = self.epochs,
            bf16 = True,
            per_device_train_batch_size = 4,
            per_device_eval_batch_size = 4,
            warmup_steps = 500,
            weight_decay = 0.01,
            logging_steps = 10,
            evaluation_strategy = "epoch",
            # torch_compile = True
        )
        trainer = Trainer(
            model = self.model,
            args = training_args,
            train_dataset = training_data,
            eval_dataset = validation_data,
        )
        trainer.train()
    
    def test(self):
        testing_data = self.prepare_data(self.test_file_path, is_test=True)
        model_outputs = []

        for instance in testing_data:
            model_outputs.append(self.tokenizer.decode(self.model.generate(**instance)[0], skip_special_tokens=True))
        
        with open(os.path.join(self.model_save_path, 'test_results.json'), 'w') as f:
            for output in model_outputs:
                f.write(json.dumps(output)+'\n')


def parse_args():
    '''
    Parse the arguments for the script
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', type=str, required=True, help='Model name')
    parser.add_argument('-f', '--file', type=str, required=True, help='Input data path')
    parser.add_argument('-o', '--output', type=str, required=True, help='Model save path')
    parser.add_argument('-c', '--context', type=int, required=True, help='Context length')
    parser.add_argument('-d', '--huggingface_cache_dir', type=str, required=False, help='Huggingface cache directory')
    parser.add_argument('-t', '--huggingface_token', type=str, required=True, help='Huggingface token')
    parser.add_argument('-e', '--epochs', type=int, required=False, default=DEFAULT_EPOCHS, help='Number of epochs')
    return parser.parse_args()


if __name__ == '__main__':
    # Getting arguments
    args = parse_args()

    llama_model = Llama(
        args.model,
        args.file,
        args.output,
        args.context,
        args.huggingface_token,
        args.huggingface_cache_dir,
        args.epochs
    )
    llama_model.train()
    # llama_model.test()