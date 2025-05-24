from generator import Generator
from retrieval import Retrieval
import os

class RAGSystem:
    def __init__(self, retrievel: Retrieval, generator: Generator):
        self.retrievel = retrievel
        self.generator = generator

    def answer_query(self, query: str, max_new_tokens: int = 620) -> str:
        """
        Retrievel document and generate answer based on question and context.
        Args:
            query: Question.
            max_new_tokens: Maximum number of tokens generated.
        Returns:
            String answer.
        """
        try:
            context = self.retrievel.top_retrieval(query)
            answer = self.generator.generate_answer(query, context, max_new_tokens=max_new_tokens)
            return answer
        except Exception as e:
            return f"Lỗi khi xử lý truy vấn: {str(e)}"
        


def main():
    retrieval = Retrieval()
    generator = Generator()

    rag_system = RAGSystem(retrieval=retrieval, generator=generator)

    input_path = "./test-data/question.txt"
    output_folder = "./output"
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, "output.txt")

    with open(input_path, "r", encoding="utf-8") as f_in:
        questions = [line.strip() for line in f_in if line.strip()]

    with open(output_path, "w", encoding="utf-8") as f_out:
        for question in questions:
            answer = rag_system.answer_query(question)
            f_out.write(answer + "\n")

if __name__ == "__main__":
    main()