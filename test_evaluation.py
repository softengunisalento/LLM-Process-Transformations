import os
import csv
from docx import Document
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams
from deepeval.test_case import LLMTestCase

base_dir = "Transformed_Sustainable_Descriptions"

processes = ["Credit Scoring", "Dispatch of Goods", "Recourse", "Self-Service Restaurant"]
models = ["GPT-4o (ChatGPT)", "Claude 3.5 Haiku", "GPT-4 Turbo (Copilot)", "GPT-3.5 Turbo (Perplexity AI)", "DeepAI"]

def read_outputs_from_directory(process, model):
    model_dir = os.path.join(base_dir, process, model)
    if not os.path.exists(model_dir):
        print(f"Directory non trovata per {process}, {model}")
        return ["Nessun output"]

    outputs = []
    for i in range(1, 6):
        file_path = os.path.join(model_dir, f"Output {i}.txt")
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                outputs.append(file.read().strip())
        else:
            print(f"File {file_path} non trovato")
    return outputs

def calculate_average_score(process, outputs):
    process_dir = os.path.join(base_dir, process)

    try:
        with open(os.path.join(process_dir, "Input.txt"), "r") as input_file:
            process_input = input_file.read().strip()
    except FileNotFoundError:
        print(f"File Input.txt non trovato per {process}")
        return "Input mancante"

    try:
        docx_file_path = os.path.join(process_dir, "Expected Output.docx")
        document = Document(docx_file_path)

        expected_output = "\n".join([paragraph.text for paragraph in document.paragraphs]).strip()
    except FileNotFoundError:
        print(f"File Expected Output.txt non trovato per {process}")
        return "Output desiderato mancante"

    if not outputs:
        return "Output mancante"

    scores = []
    for output in outputs:
        test_case = LLMTestCase(input=process_input, actual_output=output, expected_output=expected_output)
        coherence_metric = GEval(
            name="Sustainability Compliance",
            criteria="Evaluate how well the output meets sustainability criteria",
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
        )
        coherence_metric.measure(test_case)
        scores.append(coherence_metric.score)

    return round(sum(scores) / len(scores), 4) if scores else 0

results = []

for process in processes:
    row = []
    for model in models:
        outputs = read_outputs_from_directory(process, model)
        avg_score = calculate_average_score(process, outputs)
        row.append(avg_score)
    results.append(row)

csv_filename = "evaluation_results.csv"

with open(csv_filename, mode="w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow(["Process"] + models)

    for process, row in zip(processes, results):
        writer.writerow([process] + row)