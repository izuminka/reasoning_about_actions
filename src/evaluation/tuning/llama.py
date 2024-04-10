import argparse
import json
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import Trainer, TrainingArguments


class Llama:
    def __init__(
            self,
            model,
            input_file_path,
            model_save_path,
            context_length,
            huggingface_token,
            huggingface_cache_dir=None,
            epochs = 3
        ):
        self.model_name = model
        self.train_file_path = os.path.join(input_file_path, 'train.json')
        self.eval_file_path = os.path.join(input_file_path, 'eval.json')
        self.test_file_path = os.path.join(input_file_path, 'test.json')
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
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map = 'auto',
            cache_dir = self.huggingface_cache_dir,
            token = self.huggingface_token
        )
    
    def tokenize_function(self, text):
        return self.tokenizer(
            text,
            padding = "max_length",
            truncation = True,
            max_length = self.context_length,
            return_tensors = "pt"
        ).to('cuda')
    
    def prepare_data(self, file_path):
        with open(file_path, 'r') as f:
            data = [json.loads(jline) for jline in f.readlines()]
        
        dataset = []
        for instance in data:
            dataset.append(self.tokenize_function(instance['prompt']))
        return dataset

    def train(self):
        training_data = self.prepare_data(self.train_file_path)
        validation_data = self.prepare_data(self.eval_file_path)
        
        training_args = TrainingArguments(
            output_dir = self.model_save_path,
            num_train_epochs = self.epochs,
            per_device_train_batch_size = 4,
            per_device_eval_batch_size = 4,
            warmup_steps = 500,
            weight_decay = 0.01,
            logging_dir = "./logs",
            logging_steps = 10,
            evaluation_strategy = "epoch",
        )
        trainer = Trainer(
            model = self.model,
            args = training_args,
            train_dataset = training_data,
            eval_dataset = validation_data,
        )
        trainer.train()
    
    def test(self):
        testing_data = self.prepare_data(self.test_file_path)
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
        args.huggingface_cache_dir
    )
    llama_model.train()
    llama_model.test()