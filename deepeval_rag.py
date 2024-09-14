import json
import os
from typing import List, Tuple

from deepeval import evaluate
from deepeval.metrics import GEval, FaithfulnessMetric, ContextualRelevancyMetric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain import PromptTemplate
from deepeval.models.base_model import DeepEvalBaseLLM
import asyncio


from dotenv import load_dotenv

from embeddings import *
from llms import *
# from query_simple_rag import *

load_dotenv()

from query_simple_rag import *
def create_deep_eval_test_cases(
    questions: List[str],
    gt_answers: List[str],
    generated_answers: List[str],
    retrieved_documents: List[str]
) -> List[LLMTestCase]:
    """
    Create a list of LLMTestCase objects for evaluation.

    Args:
        questions (List[str]): List of input questions.
        gt_answers (List[str]): List of ground truth answers.
        generated_answers (List[str]): List of generated answers.
        retrieved_documents (List[str]): List of retrieved documents.

    Returns:
        List[LLMTestCase]: List of LLMTestCase objects.
    """
    return [
        LLMTestCase(
            input=question,
            expected_output=gt_answer,
            actual_output=generated_answer,
            retrieval_context=retrieved_document
        )
        for question, gt_answer, generated_answer, retrieved_document in zip(
            questions, gt_answers, generated_answers, retrieved_documents
        )
    ]


# Define evaluation metrics
correctness_metric = GEval(
    name="Correctness",
    model="gpt-3.5-turbo",
    evaluation_params=[
        LLMTestCaseParams.EXPECTED_OUTPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT
    ],
    evaluation_steps=[
        "Determine whether the actual output is factually correct based on the expected output."
    ],
)

faithfulness_metric = FaithfulnessMetric(
    threshold=0.7,
    model="gpt-3.5-turbo",
    include_reason=False
)

relevance_metric = ContextualRelevancyMetric(
    threshold=1,
    model="gpt-3.5-turbo",
    include_reason=True
)

def evaluate_rag(chunks_query_retriever, num_questions: int = 5) -> None:
    mistral_model, llama_model = initialize_models()
    
    # Load questions and answers from JSON file
    q_a_file_name = os.path.join('data', 'json', 'q_a.json')
    with open(q_a_file_name, "r", encoding="utf-8") as json_file:
        q_a = json.load(json_file)

    questions = [qa["question"] for qa in q_a][:num_questions]
    ground_truth_answers = [qa["answer"] for qa in q_a][:num_questions]
    generated_answers = []
    retrieved_documents = []
    
    # Generate answers and retrieve documents for each question
    for question in questions:
        collection_name='document_embeddings_v20'
        persist_directory='chroma_db_v4'
        
        context = get_similar_documents_from_chroma(collection_name, persist_directory, question)
        filter_context = create_context_for_llm(context)
        retrieved_documents.append([filter_context])
      
        result = ask_llm_with_ollama(question, filter_context, mistral_model)
        print(result)  # Fügen Sie dies hinzu, um zu sehen, was zurückgegeben wird
        # Füge den String in ein Dictionary-ähnliches Format um
        # modified_result = {"answer": result}
        generated_answers.append(result)
        
            # Create test cases and evaluate
    test_cases = create_deep_eval_test_cases(questions, ground_truth_answers, generated_answers, retrieved_documents)
    evaluate(
        test_cases=test_cases,
        metrics=[correctness_metric, faithfulness_metric, relevance_metric]
    )
    
evaluate_rag("hallo")
        