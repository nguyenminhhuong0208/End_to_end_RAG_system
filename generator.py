from transformers import LlamaForCausalLM, LlamaTokenizer, LlamaConfig
import torch

class Generator:
    def __init__(self, model_id: str = "phongnp2010/vietrag-finetuning"):
        self.tokenizer = LlamaTokenizer.from_pretrained(model_id)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"

        self.model = LlamaForCausalLM.from_pretrained(
            model_id,
            config=LlamaConfig.from_pretrained(model_id),
            torch_dtype=torch.bfloat16,
            device_map='auto',
        )
        self.model.eval()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def format_prompt(self, question, context):
        instruction = 'You are now a dedicated assistant for TLU. Provide a detailed answer so user don’t need to search outside to understand the answer.'
        input = f"Dựa vào một số Tài liệu được cho dưới đây, trả lời câu hỏi ở cuối. bạn phải trả lời câu hỏi thật ngắn gọn. nếu câu hỏi có nhiều câu trả lời, ngăn cách các câu trả lời bằng ';'. nếu bạn thấy Tài liệu không liên quan đến câu hỏi thì phải giải thích tại sao lại không thể trả lời.\n\n{context}\n\nQuestion: {question}"
        prompt_template = (
            "### System:\n"
            "Below is an instruction that describes a task, paired with an input that provides further context. "
            "Write a response that appropriately completes the request.\n\n\n\n"
            "### Instruction:\n{instruction}\n\n"
            "### Input:\n{input}\n\n"
            "### Response:\n{output}"
        )
        return prompt_template.format(instruction=instruction, input=input, output='')
    
    def generate_answer(self, query: str, context: str, max_new_tokens: int = 620) -> str:
        prompt = self.format_prompt(question=query, context=context)
        input_ids = self.tokenizer(prompt, return_tensors="pt")["input_ids"].to(self.device)
        attention_mask = (input_ids != self.tokenizer.pad_token_id).long()

        with torch.no_grad():
            generated = self.model.generate(
                inputs=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=max_new_tokens,
                repetition_penalty=1.13,
                pad_token_id=self.tokenizer.pad_token_id,
                do_sample=False,
                use_cache=True
            )
        gen_tokens = generated[:, len(input_ids[0]):]
        output = self.tokenizer.batch_decode(gen_tokens)[0]
        return output.strip().replace('</s>', '')
    
def test():
    generator= Generator()
    query = "Trường Đại Học Công Nghệ ở đâu?"
    context = "Trường đại học công nghệ thuộc đại học quốc gia hà nội nằm ở 144 Xuân Thủy, Cầu Giấy, Hà Nội."
    answer = generator.generate_answer(query, context)
    print(answer)

if __name__ == "__main__":
    test()