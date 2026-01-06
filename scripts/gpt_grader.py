# import argparse
# import json
# import openai
# import re
# import time
# # Create the parser
# parser = argparse.ArgumentParser(description='Process OpenAI API key and JSONL file path.')

# # Add arguments
# parser.add_argument('--openai_api_key', default = "", help='Your OpenAI API key')
# parser.add_argument('--answer_file', default = "answer.jsonl",help='Path to the JSONL file')

# # Parse arguments
# args = parser.parse_args()

# openai.api_key = args.openai_api_key
# NUM_SECONDS_TO_SLEEP = 10
# # Define a function to query the OpenAI API and evaluate the answer
# def get_yes_no_answer(question):
#     while True:
#         try:
#             response = openai.ChatCompletion.create(
#                 model='gpt-4-0314',
#                 messages=[{
#                     'role': 'system',
#                     'content': 'You are a helpful and precise assistant for checking the quality of the answer. Please answer in only yes or no.'
#                 }, {
#                     'role': 'user',
#                     'content': question,
#                 }],
#                 temperature=0.2,  # TODO: figure out which temperature is best for evaluation
#             )
#             break
#         except openai.error.RateLimitError:
#             pass
#         except Exception as e:
#             print(e)
#         time.sleep(NUM_SECONDS_TO_SLEEP)

#     answer = response['choices'][0]['message']['content']
#     yes_no_regex = re.compile(r"^(yes|no)$", re.IGNORECASE)

#     if yes_no_regex.match(answer):
#         return answer.lower()
#     else:
#         return "Could not determine yes or no."


# num_correct, num_total = 0, 0
# # Continue with the processing of the JSONL file
# with open(args.answer_file, 'r') as file:
#     index, round_correct = 0, 0
#     for line in file:
#         data = json.loads(line)
#         question, correct_answer, model_response = data["prompt"], data["answer"], data["response"]
#         question4gpt = f"Given the following question {question}, the correct answer is {correct_answer}. Does the following answer correctly answers the question, answer:{model_response}?"
#         gpt_grade = get_yes_no_answer(question4gpt)

#         index += 1

#         if gpt_grade=="yes":
#             round_correct += 1
#         if index == 2:
#             index = 0
#             if round_correct == 2:
#                 num_correct += 1
#             round_correct = 0

#             num_total += 1
# print(f"The accuracy is {num_correct/num_total}")

import argparse
import json
import openai
import re
import time
from collections import defaultdict

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description='Process OpenAI API key and JSONL file path.')
    parser.add_argument('--openai_api_key', required=True, help='Your OpenAI API key')
    parser.add_argument('--answer_file', default="answer.jsonl", help='Path to the JSONL file')
    parser.add_argument('--output_file', default="evaluation_results.json", help='Path to save detailed results')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set up OpenAI client (updated API)
    client = openai.OpenAI(api_key=args.openai_api_key)
    
    NUM_SECONDS_TO_SLEEP = 10
    
    def get_yes_no_answer(question):
        while True:
            try:
                response = client.chat.completions.create(
                    model='gpt-4',
                    messages=[
                        {
                            'role': 'system',
                            'content': 'You are a helpful and precise assistant for checking the quality of the answer. Please answer in only yes or no.'
                        },
                        {
                            'role': 'user',
                            'content': question,
                        }
                    ],
                    temperature=0.2,
                )
                break
            except openai.RateLimitError:
                print("Rate limit exceeded. Waiting...")
                time.sleep(NUM_SECONDS_TO_SLEEP)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(NUM_SECONDS_TO_SLEEP)
        
        answer = response.choices[0].message.content
        yes_no_regex = re.compile(r"^(yes|no)$", re.IGNORECASE)
        if yes_no_regex.match(answer):
            return answer.lower()
        else:
            return "Could not determine yes or no."
    
    # Initialize counters
    num_correct_pairs = 0
    num_total_pairs = 0
    individual_correct = 0
    individual_total = 0
    
    # Category tracking
    category_stats = defaultdict(lambda: {'correct_pairs': 0, 'total_pairs': 0, 'individual_correct': 0, 'individual_total': 0})
    
    # Detailed results storage
    detailed_results = []
    
    # Process the JSONL file
    with open(args.answer_file, 'r') as file:
        lines = list(file)
        
        # Process in pairs (questions come in pairs with same image but different correct answers)
        for i in range(0, len(lines), 2):
            if i + 1 >= len(lines):
                break
                
            # Parse both questions in the pair
            data1 = json.loads(lines[i])
            data2 = json.loads(lines[i + 1])
            
            pair_correct = 0
            
            # Process each question in the pair
            for data in [data1, data2]:
                question = data["prompt"]
                correct_answer = data["answer"]
                model_response = data["response"]
                category = data.get("category", "unknown")  # Handle missing category
                question_id = data["question_id"]
                
                # Grade the response
                question4gpt = f"Given the following question '{question}', the correct answer is '{correct_answer}'. Does the following answer correctly answer the question? Answer: '{model_response}'"
                gpt_grade = get_yes_no_answer(question4gpt)
                
                is_correct = (gpt_grade == "yes")
                
                # Individual question tracking
                individual_total += 1
                category_stats[category]['individual_total'] += 1
                
                if is_correct:
                    individual_correct += 1
                    pair_correct += 1
                    category_stats[category]['individual_correct'] += 1
                
                # Store detailed result
                detailed_results.append({
                    "question_id": question_id,
                    "category": category,
                    "question": question,
                    "correct_answer": correct_answer,
                    "model_response": model_response,
                    "is_correct": is_correct,
                    "gpt_grade": gpt_grade
                })
            
            # Pair tracking (both questions must be correct)
            num_total_pairs += 1
            category = data1.get("category", "unknown")
            category_stats[category]['total_pairs'] += 1
            
            if pair_correct == 2:
                num_correct_pairs += 1
                category_stats[category]['correct_pairs'] += 1
    
    # Calculate accuracies
    pair_accuracy = num_correct_pairs / num_total_pairs if num_total_pairs > 0 else 0
    individual_accuracy = individual_correct / individual_total if individual_total > 0 else 0
    
    # Prepare category results
    category_results = {}
    for category, stats in category_stats.items():
        category_results[category] = {
            'pair_accuracy': stats['correct_pairs'] / stats['total_pairs'] if stats['total_pairs'] > 0 else 0,
            'individual_accuracy': stats['individual_correct'] / stats['individual_total'] if stats['individual_total'] > 0 else 0,
            'correct_pairs': stats['correct_pairs'],
            'total_pairs': stats['total_pairs'],
            'correct_individual': stats['individual_correct'],
            'total_individual': stats['individual_total']
        }
    
    # Prepare final results
    results = {
        'overall_statistics': {
            'pair_accuracy': pair_accuracy,
            'individual_accuracy': individual_accuracy,
            'correct_pairs': num_correct_pairs,
            'total_pairs': num_total_pairs,
            'correct_individual': individual_correct,
            'total_individual': individual_total
        },
        'category_statistics': category_results,
        'detailed_results': detailed_results
    }
    
    # Save detailed results to JSON file
    with open(args.output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"EVALUATION RESULTS")
    print(f"{'='*60}")
    print(f"Overall Pair Accuracy: {pair_accuracy:.3f} ({num_correct_pairs}/{num_total_pairs})")
    print(f"Overall Individual Accuracy: {individual_accuracy:.3f} ({individual_correct}/{individual_total})")
    print(f"\nCategory Breakdown:")
    print(f"{'Category':<12} {'Pair Acc':<10} {'Ind Acc':<10} {'Pair':<15} {'Individual':<15}")
    print(f"{'-'*60}")
    
    for category, stats in sorted(category_results.items()):
        pair_str = f"{stats['correct_pairs']}/{stats['total_pairs']}"
        ind_str = f"{stats['correct_individual']}/{stats['total_individual']}"
        print(f"{category:<12} {stats['pair_accuracy']:<10.3f} {stats['individual_accuracy']:<10.3f} {pair_str:<15} {ind_str:<15}")
    
    print(f"\nDetailed results saved to: {args.output_file}")

if __name__ == "__main__":
    main()
