# # # import argparse
# # # import json
# # # import openai
# # # import re
# # # import time
# # # import sys
# # # from collections import defaultdict

# # # def main():
# # #     # Create the parser
# # #     parser = argparse.ArgumentParser(description='Process OpenAI API key and JSONL file path.')
# # #     parser.add_argument('--openai_api_key', required=True, help='Your OpenAI API key')
# # #     parser.add_argument('--answer_file', default="answer.jsonl", help='Path to the JSONL file')
# # #     parser.add_argument('--output_file', default="evaluation_results.json", help='Path to save detailed results')
# # #     parser.add_argument('--debug', action='store_true', help='Enable debug mode to see problematic text')
    
# # #     # Parse arguments
# # #     args = parser.parse_args()
    
# # #     # Set up OpenAI client (updated API)
# # #     client = openai.OpenAI(api_key=args.openai_api_key)
    
# # #     NUM_SECONDS_TO_SLEEP = 10
    
# # #     def clean_text_for_api(text):
# # #         """Clean text for API consumption"""
# # #         if not isinstance(text, str):
# # #             text = str(text)
        
# # #         # Remove markdown formatting
# # #         text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold **text**
# # #         text = re.sub(r'\*(.*?)\*', r'\1', text)      # Remove italic *text*
# # #         text = text.replace('`', '')                   # Remove backticks
        
# # #         # Replace smart quotes and special characters
# # #         replacements = {
# # #             '\u201c': '"', '\u201d': '"',  # Smart quotes
# # #             '\u2018': "'", '\u2019': "'",  # Smart apostrophes
# # #             '\u2013': '-', '\u2014': '--', # Dashes
# # #             '\u2026': '...',               # Ellipsis
# # #             '\u00a0': ' ',                 # Non-breaking space
# # #         }
        
# # #         for old, new in replacements.items():
# # #             text = text.replace(old, new)
        
# # #         # Clean up whitespace
# # #         text = ' '.join(text.split())
        
# # #         # Keep only printable ASCII characters
# # #         text = ''.join(char for char in text if ord(char) < 128 and (char.isprintable() or char.isspace()))
        
# # #         return text.strip()
    
# # #     def get_yes_no_answer(question):
# # #         if args.debug:
# # #             print(f"DEBUG: Sending question to GPT: {repr(question[:100])}...")
        
# # #         while True:
# # #             try:
# # #                 response = client.chat.completions.create(
# # #                     model='gpt-4',
# # #                     messages=[
# # #                         {
# # #                             'role': 'system',
# # #                             'content': 'You are a helpful and precise assistant for checking the quality of the answer. Please answer in only yes or no.'
# # #                         },
# # #                         {
# # #                             'role': 'user',
# # #                             'content': question,
# # #                         }
# # #                     ],
# # #                     temperature=0.2,
# # #                 )
# # #                 break
# # #             except openai.RateLimitError:
# # #                 print("Rate limit exceeded. Waiting...")
# # #                 time.sleep(NUM_SECONDS_TO_SLEEP)
# # #             except Exception as e:
# # #                 print(f"Error: {e}")
# # #                 if args.debug:
# # #                     print(f"DEBUG: Error occurred with question: {repr(question[:200])}")
# # #                 time.sleep(NUM_SECONDS_TO_SLEEP)
        
# # #         answer = response.choices[0].message.content
# # #         yes_no_regex = re.compile(r"^(yes|no)$", re.IGNORECASE)
# # #         if yes_no_regex.match(answer):
# # #             return answer.lower()
# # #         else:
# # #             return "Could not determine yes or no."
    
# # #     # Initialize counters
# # #     num_correct_pairs = 0
# # #     num_total_pairs = 0
# # #     individual_correct = 0
# # #     individual_total = 0
    
# # #     # Category tracking
# # #     category_stats = defaultdict(lambda: {'correct_pairs': 0, 'total_pairs': 0, 'individual_correct': 0, 'individual_total': 0})
    
# # #     # Detailed results storage
# # #     detailed_results = []
    
# # #     # Process the JSONL file
# # #     print(f"Reading file: {args.answer_file}")
# # #     try:
# # #         with open(args.answer_file, 'r', encoding='utf-8') as file:
# # #             lines = file.readlines()
# # #     except Exception as e:
# # #         print(f"Error reading file: {e}")
# # #         sys.exit(1)
    
# # #     print(f"Found {len(lines)} lines in file")
    
# # #     # Process in pairs (questions come in pairs with same image but different correct answers)
# # #     for i in range(0, len(lines), 2):
# # #         if i + 1 >= len(lines):
# # #             print(f"Warning: Odd number of lines, skipping last line")
# # #             break
        
# # #         try:
# # #             # Parse both questions in the pair
# # #             data1 = json.loads(lines[i].strip())
# # #             data2 = json.loads(lines[i + 1].strip())
# # #         except json.JSONDecodeError as e:
# # #             print(f"Error parsing JSON at lines {i}-{i+1}: {e}")
# # #             if args.debug:
# # #                 print(f"DEBUG: Line {i}: {repr(lines[i][:100])}")
# # #                 print(f"DEBUG: Line {i+1}: {repr(lines[i+1][:100])}")
# # #             continue
        
# # #         pair_correct = 0
        
# # #         # Process each question in the pair
# # #         for j, data in enumerate([data1, data2]):
# # #             try:
# # #                 question = str(data["prompt"])
# # #                 correct_answer = str(data["answer"])
# # #                 model_response = str(data["response"])
# # #                 category = data.get("category", "unknown")
# # #                 question_id = data["question_id"]
                
# # #                 if args.debug:
# # #                     print(f"Processing question {question_id}")
# # #                     print(f"  Original response: {repr(model_response[:100])}")
                
# # #                 # Clean all text
# # #                 question = clean_text_for_api(question)
# # #                 correct_answer = clean_text_for_api(correct_answer)
# # #                 model_response = clean_text_for_api(model_response)
                
# # #                 if args.debug:
# # #                     print(f"  Cleaned response: {repr(model_response[:100])}")
                
# # #                 # Grade the response
# # #                 question4gpt = f"Given the following question '{question}', the correct answer is '{correct_answer}'. Does the following answer correctly answer the question? Answer: '{model_response}'"
                
# # #                 gpt_grade = get_yes_no_answer(question4gpt)
                
# # #                 is_correct = (gpt_grade == "yes")
                
# # #                 # Individual question tracking
# # #                 individual_total += 1
# # #                 category_stats[category]['individual_total'] += 1
                
# # #                 if is_correct:
# # #                     individual_correct += 1
# # #                     pair_correct += 1
# # #                     category_stats[category]['individual_correct'] += 1
                
# # #                 # Store detailed result
# # #                 detailed_results.append({
# # #                     "question_id": question_id,
# # #                     "category": category,
# # #                     "question": question,
# # #                     "correct_answer": correct_answer,
# # #                     "model_response": model_response,
# # #                     "is_correct": is_correct,
# # #                     "gpt_grade": gpt_grade
# # #                 })
                
# # #                 print(f"Question {question_id}: {gpt_grade}")
                
# # #             except Exception as e:
# # #                 print(f"Error processing question at line {i+j}: {e}")
# # #                 if args.debug:
# # #                     print(f"DEBUG: Data: {data}")
# # #                 continue
        
# # #         # Pair tracking (both questions must be correct)
# # #         num_total_pairs += 1
# # #         category = data1.get("category", "unknown")
# # #         category_stats[category]['total_pairs'] += 1
        
# # #         if pair_correct == 2:
# # #             num_correct_pairs += 1
# # #             category_stats[category]['correct_pairs'] += 1
    
# # #     # Calculate accuracies
# # #     pair_accuracy = num_correct_pairs / num_total_pairs if num_total_pairs > 0 else 0
# # #     individual_accuracy = individual_correct / individual_total if individual_total > 0 else 0
    
# # #     # Prepare category results
# # #     category_results = {}
# # #     for category, stats in category_stats.items():
# # #         category_results[category] = {
# # #             'pair_accuracy': stats['correct_pairs'] / stats['total_pairs'] if stats['total_pairs'] > 0 else 0,
# # #             'individual_accuracy': stats['individual_correct'] / stats['individual_total'] if stats['individual_total'] > 0 else 0,
# # #             'correct_pairs': stats['correct_pairs'],
# # #             'total_pairs': stats['total_pairs'],
# # #             'correct_individual': stats['individual_correct'],
# # #             'total_individual': stats['individual_total']
# # #         }
    
# # #     # Prepare final results
# # #     results = {
# # #         'overall_statistics': {
# # #             'pair_accuracy': pair_accuracy,
# # #             'individual_accuracy': individual_accuracy,
# # #             'correct_pairs': num_correct_pairs,
# # #             'total_pairs': num_total_pairs,
# # #             'correct_individual': individual_correct,
# # #             'total_individual': individual_total
# # #         },
# # #         'category_statistics': category_results,
# # #         'detailed_results': detailed_results
# # #     }
    
# # #     # Save detailed results to JSON file
# # #     with open(args.output_file, 'w', encoding='utf-8') as f:
# # #         json.dump(results, f, indent=2, ensure_ascii=True)
    
# # #     # Print summary
# # #     print(f"\n{'='*60}")
# # #     print(f"EVALUATION RESULTS")
# # #     print(f"{'='*60}")
# # #     print(f"Overall Pair Accuracy: {pair_accuracy:.3f} ({num_correct_pairs}/{num_total_pairs})")
# # #     print(f"Overall Individual Accuracy: {individual_accuracy:.3f} ({individual_correct}/{individual_total})")
# # #     print(f"\nCategory Breakdown:")
# # #     print(f"{'Category':<12} {'Pair Acc':<10} {'Ind Acc':<10} {'Pair':<15} {'Individual':<15}")
# # #     print(f"{'-'*60}")
    
# # #     for category, stats in sorted(category_results.items()):
# # #         pair_str = f"{stats['correct_pairs']}/{stats['total_pairs']}"
# # #         ind_str = f"{stats['correct_individual']}/{stats['total_individual']}"
# # #         print(f"{category:<12} {stats['pair_accuracy']:<10.3f} {stats['individual_accuracy']:<10.3f} {pair_str:<15} {ind_str:<15}")
    
# # #     print(f"\nDetailed results saved to: {args.output_file}")

# # # if __name__ == "__main__":
# # #     main()

# # import argparse
# # import json
# # import openai
# # import re
# # import time
# # import sys
# # from collections import defaultdict

# # def main():
# #     # Create the parser
# #     parser = argparse.ArgumentParser(description='Process OpenAI API key and JSONL file path.')
# #     parser.add_argument('--openai_api_key', required=True, help='Your OpenAI API key')
# #     parser.add_argument('--answer_file', default="answer.jsonl", help='Path to the JSONL file')
# #     parser.add_argument('--output_file', default="evaluation_results.json", help='Path to save detailed results')
# #     parser.add_argument('--debug', action='store_true', help='Enable debug mode to see problematic text')
    
# #     # Parse arguments
# #     args = parser.parse_args()
    
# #     # Set up OpenAI client (updated API)
# #     client = openai.OpenAI(api_key=args.openai_api_key)
    
# #     NUM_SECONDS_TO_SLEEP = 10
    
# #     def clean_text_for_api(text):
# #         """Clean text for API consumption"""
# #         if not isinstance(text, str):
# #             text = str(text)
        
# #         # Remove markdown formatting
# #         text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold **text**
# #         text = re.sub(r'\*(.*?)\*', r'\1', text)      # Remove italic *text*
# #         text = text.replace('`', '')                   # Remove backticks
        
# #         # Replace smart quotes and special characters - be more aggressive
# #         replacements = {
# #             '\u201c': '"', '\u201d': '"',  # Smart quotes
# #             '\u2018': "'", '\u2019': "'",  # Smart apostrophes
# #             '\u2013': '-', '\u2014': '--', # Dashes
# #             '\u2026': '...',               # Ellipsis
# #             '\u00a0': ' ',                 # Non-breaking space
# #             '"': '"', '"': '"',            # More smart quotes
# #             ''': "'", ''': "'",            # More smart apostrophes
# #         }
        
# #         for old, new in replacements.items():
# #             text = text.replace(old, new)
        
# #         # Clean up whitespace
# #         text = ' '.join(text.split())
        
# #         # More aggressive ASCII filtering - remove ANY non-ASCII characters
# #         ascii_text = ''
# #         for char in text:
# #             if ord(char) < 128:
# #                 ascii_text += char
# #             else:
# #                 if char in ' \t\n':
# #                     ascii_text += ' '
# #                 else:
# #                     ascii_text += '?'  # Replace with question mark temporarily
        
# #         # Remove the question marks we added
# #         ascii_text = ascii_text.replace('?', ' ')
        
# #         # Clean up multiple spaces
# #         ascii_text = ' '.join(ascii_text.split())
        
# #         return ascii_text.strip()
    
# #     def get_yes_no_answer(question):
# #         if args.debug:
# #             print(f"DEBUG: Sending question to GPT: {repr(question[:100])}...")
        
# #         while True:
# #             try:
# #                 response = client.chat.completions.create(
# #                     model='gpt-4',
# #                     messages=[
# #                         {
# #                             'role': 'system',
# #                             'content': 'You are a helpful and precise assistant for checking the quality of the answer. Please answer in only yes or no.'
# #                         },
# #                         {
# #                             'role': 'user',
# #                             'content': question,
# #                         }
# #                     ],
# #                     temperature=0.2,
# #                 )
# #                 break
# #             except openai.RateLimitError:
# #                 print("Rate limit exceeded. Waiting...")
# #                 time.sleep(NUM_SECONDS_TO_SLEEP)
# #             except Exception as e:
# #                 print(f"Error: {e}")
# #                 if args.debug:
# #                     print(f"DEBUG: Error occurred with question: {repr(question[:200])}")
# #                 time.sleep(NUM_SECONDS_TO_SLEEP)
        
# #         answer = response.choices[0].message.content
# #         yes_no_regex = re.compile(r"^(yes|no)$", re.IGNORECASE)
# #         if yes_no_regex.match(answer):
# #             return answer.lower()
# #         else:
# #             return "Could not determine yes or no."
    
# #     # Initialize counters
# #     num_correct_pairs = 0
# #     num_total_pairs = 0
# #     individual_correct = 0
# #     individual_total = 0
    
# #     # Category tracking
# #     category_stats = defaultdict(lambda: {'correct_pairs': 0, 'total_pairs': 0, 'individual_correct': 0, 'individual_total': 0})
    
# #     # Detailed results storage
# #     detailed_results = []
    
# #     # Process the JSONL file
# #     print(f"Reading file: {args.answer_file}")
# #     try:
# #         with open(args.answer_file, 'r', encoding='utf-8') as file:
# #             lines = file.readlines()
# #     except Exception as e:
# #         print(f"Error reading file: {e}")
# #         sys.exit(1)
    
# #     print(f"Found {len(lines)} lines in file")
    
# #     # Process in pairs (questions come in pairs with same image but different correct answers)
# #     for i in range(0, len(lines), 2):
# #         if i + 1 >= len(lines):
# #             print(f"Warning: Odd number of lines, skipping last line")
# #             break
        
# #         try:
# #             # Parse both questions in the pair
# #             data1 = json.loads(lines[i].strip())
# #             data2 = json.loads(lines[i + 1].strip())
# #         except json.JSONDecodeError as e:
# #             print(f"Error parsing JSON at lines {i}-{i+1}: {e}")
# #             if args.debug:
# #                 print(f"DEBUG: Line {i}: {repr(lines[i][:100])}")
# #                 print(f"DEBUG: Line {i+1}: {repr(lines[i+1][:100])}")
# #             continue
        
# #         pair_correct = 0
        
# #         # Process each question in the pair
# #         for j, data in enumerate([data1, data2]):
# #             try:
# #                 question = str(data["prompt"])
# #                 correct_answer = str(data["answer"])
# #                 model_response = str(data["response"])
# #                 category = data.get("category", "unknown")
# #                 question_id = data["question_id"]
                
# #                 if args.debug:
# #                     print(f"Processing question {question_id}")
# #                     print(f"  Original response: {repr(model_response[:100])}")
                
# #                 # Clean all text
# #                 question = clean_text_for_api(question)
# #                 correct_answer = clean_text_for_api(correct_answer)
# #                 model_response = clean_text_for_api(model_response)
                
# #                 if args.debug:
# #                     print(f"  Cleaned response: {repr(model_response[:100])}")
                
# #                 # Grade the response
# #                 question4gpt = f"Given the following question '{question}', the correct answer is '{correct_answer}'. Does the following answer correctly answer the question? Answer: '{model_response}'"
                
# #                 # Clean the final question string too
# #                 question4gpt = clean_text_for_api(question4gpt)
                
# #                 gpt_grade = get_yes_no_answer(question4gpt)
                
# #                 is_correct = (gpt_grade == "yes")
                
# #                 # Individual question tracking
# #                 individual_total += 1
# #                 category_stats[category]['individual_total'] += 1
                
# #                 if is_correct:
# #                     individual_correct += 1
# #                     pair_correct += 1
# #                     category_stats[category]['individual_correct'] += 1
                
# #                 # Store detailed result
# #                 detailed_results.append({
# #                     "question_id": question_id,
# #                     "category": category,
# #                     "question": question,
# #                     "correct_answer": correct_answer,
# #                     "model_response": model_response,
# #                     "is_correct": is_correct,
# #                     "gpt_grade": gpt_grade
# #                 })
                
# #                 print(f"Question {question_id}: {gpt_grade}")
                
# #             except Exception as e:
# #                 print(f"Error processing question at line {i+j}: {e}")
# #                 if args.debug:
# #                     print(f"DEBUG: Data: {data}")
# #                 continue
        
# #         # Pair tracking (both questions must be correct)
# #         num_total_pairs += 1
# #         category = data1.get("category", "unknown")
# #         category_stats[category]['total_pairs'] += 1
        
# #         if pair_correct == 2:
# #             num_correct_pairs += 1
# #             category_stats[category]['correct_pairs'] += 1
    
# #     # Calculate accuracies
# #     pair_accuracy = num_correct_pairs / num_total_pairs if num_total_pairs > 0 else 0
# #     individual_accuracy = individual_correct / individual_total if individual_total > 0 else 0
    
# #     # Prepare category results
# #     category_results = {}
# #     for category, stats in category_stats.items():
# #         category_results[category] = {
# #             'pair_accuracy': stats['correct_pairs'] / stats['total_pairs'] if stats['total_pairs'] > 0 else 0,
# #             'individual_accuracy': stats['individual_correct'] / stats['individual_total'] if stats['individual_total'] > 0 else 0,
# #             'correct_pairs': stats['correct_pairs'],
# #             'total_pairs': stats['total_pairs'],
# #             'correct_individual': stats['individual_correct'],
# #             'total_individual': stats['individual_total']
# #         }
    
# #     # Prepare final results
# #     results = {
# #         'overall_statistics': {
# #             'pair_accuracy': pair_accuracy,
# #             'individual_accuracy': individual_accuracy,
# #             'correct_pairs': num_correct_pairs,
# #             'total_pairs': num_total_pairs,
# #             'correct_individual': individual_correct,
# #             'total_individual': individual_total
# #         },
# #         'category_statistics': category_results,
# #         'detailed_results': detailed_results
# #     }
    
# #     # Save detailed results to JSON file
# #     with open(args.output_file, 'w', encoding='utf-8') as f:
# #         json.dump(results, f, indent=2, ensure_ascii=True)
    
# #     # Print summary
# #     print(f"\n{'='*60}")
# #     print(f"EVALUATION RESULTS")
# #     print(f"{'='*60}")
# #     print(f"Overall Pair Accuracy: {pair_accuracy:.3f} ({num_correct_pairs}/{num_total_pairs})")
# #     print(f"Overall Individual Accuracy: {individual_accuracy:.3f} ({individual_correct}/{individual_total})")
# #     print(f"\nCategory Breakdown:")
# #     print(f"{'Category':<12} {'Pair Acc':<10} {'Ind Acc':<10} {'Pair':<15} {'Individual':<15}")
# #     print(f"{'-'*60}")
    
# #     for category, stats in sorted(category_results.items()):
# #         pair_str = f"{stats['correct_pairs']}/{stats['total_pairs']}"
# #         ind_str = f"{stats['correct_individual']}/{stats['total_individual']}"
# #         print(f"{category:<12} {stats['pair_accuracy']:<10.3f} {stats['individual_accuracy']:<10.3f} {pair_str:<15} {ind_str:<15}")
    
# #     print(f"\nDetailed results saved to: {args.output_file}")

# # if __name__ == "__main__":
# #     main()

# import argparse
# import json
# import openai
# import re
# import time
# from collections import defaultdict

# def force_ascii(text):
#     """Force text to pure ASCII by any means necessary"""
#     if not isinstance(text, str):
#         text = str(text)
    
#     # Remove all non-ASCII characters completely
#     ascii_only = ''.join(char for char in text if 0 <= ord(char) <= 127)
    
#     # Clean up any remaining problematic characters
#     ascii_only = ascii_only.replace('"', '"').replace('"', '"')  # Smart quotes to regular
#     ascii_only = ascii_only.replace(''', "'").replace(''', "'")  # Smart apostrophes
    
#     # Remove markdown
#     ascii_only = re.sub(r'\*\*(.*?)\*\*', r'\1', ascii_only)
#     ascii_only = re.sub(r'\*(.*?)\*', r'\1', ascii_only)
    
#     # Clean whitespace
#     ascii_only = ' '.join(ascii_only.split())
    
#     return ascii_only.strip()

# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--openai_api_key', required=True)
#     parser.add_argument('--answer_file', default="answer.jsonl")
#     parser.add_argument('--output_file', default="evaluation_results.json")
#     args = parser.parse_args()
    
#     client = openai.OpenAI(api_key=args.openai_api_key)
    
#     def get_yes_no_answer(question):
#         # Absolutely force ASCII
#         #safe_question = force_ascii(question)
#         safe_question = question.encode('ascii', 'ignore').decode('ascii')
        
#         # Double-check by encoding/decoding
#         try:
#             safe_question = safe_question.encode('ascii').decode('ascii')
#         except UnicodeError:
#             # If it still fails, replace everything non-ASCII with spaces
#             safe_question = ''.join(c if ord(c) < 128 else ' ' for c in safe_question)
#             safe_question = ' '.join(safe_question.split())
        
#         print(f"Sending to API: {safe_question[:100]}...")
        
#         while True:
#             try:
#                 response = client.chat.completions.create(
#                     model='gpt-4',
#                     messages=[
#                         {
#                             'role': 'system',
#                             'content': 'You are a helpful assistant. Answer only yes or no.'
#                         },
#                         {
#                             'role': 'user',
#                             'content': safe_question,
#                         }
#                     ],
#                     temperature=0.2,
#                 )
#                 break
#             except openai.RateLimitError:
#                 print("Rate limit exceeded. Waiting...")
#                 time.sleep(10)
#             except Exception as e:
#                 print(f"API Error: {e}")
#                 print(question)
#                 time.sleep(10)
        
#         answer = response.choices[0].message.content.strip().lower()
#         if answer in ['yes', 'no']:
#             return answer
#         else:
#             return "unclear"
    
#     # Initialize counters
#     correct_pairs = 0
#     total_pairs = 0
#     correct_individual = 0
#     total_individual = 0
    
#     # Read file
#     with open(args.answer_file, 'r', encoding='utf-8') as file:
#         lines = file.readlines()
    
#     print(f"Processing {len(lines)} lines...")
    
#     # Process in pairs
#     for i in range(0, len(lines), 2):
#         if i + 1 >= len(lines):
#             break
        
#         try:
#             data1 = json.loads(lines[i])
#             data2 = json.loads(lines[i + 1])
#         except:
#             print(f"Error parsing lines {i}-{i+1}")
#             continue
        
#         pair_correct = 0
        
#         for data in [data1, data2]:
#             try:
#                 question = force_ascii(data["prompt"])
#                 correct_answer = force_ascii(data["answer"])
#                 model_response = force_ascii(data["response"])
                
#                 # Create evaluation question
#                 eval_question = f"Question: {question} Correct answer: {correct_answer} Model answer: {model_response} Is the model answer correct?"
                
#                 grade = get_yes_no_answer(eval_question)
                
#                 total_individual += 1
#                 if grade == "yes":
#                     correct_individual += 1
#                     pair_correct += 1
                
#                 print(f"Question {data['question_id']}: {grade}")
                
#             except Exception as e:
#                 print(f"Error processing question {data.get('question_id', '?')}: {e}")
#                 #print(question)
        
#         total_pairs += 1
#         if pair_correct == 2:
#             correct_pairs += 1
    
#     # Print results
#     pair_accuracy = correct_pairs / total_pairs if total_pairs > 0 else 0
#     individual_accuracy = correct_individual / total_individual if total_individual > 0 else 0
    
#     print(f"\nResults:")
#     print(f"Pair Accuracy: {pair_accuracy:.3f} ({correct_pairs}/{total_pairs})")
#     print(f"Individual Accuracy: {individual_accuracy:.3f} ({correct_individual}/{total_individual})")
    
#     # Save basic results
#     results = {
#         'pair_accuracy': pair_accuracy,
#         'individual_accuracy': individual_accuracy,
#         'correct_pairs': correct_pairs,
#         'total_pairs': total_pairs,
#         'correct_individual': correct_individual,
#         'total_individual': total_individual
#     }
    
#     with open(args.output_file, 'w') as f:
#         json.dump(results, f, indent=2)

# if __name__ == "__main__":
#     main()

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
    parser.add_argument('--output_file', default="evaluation_results_gemini.json", help='Path to save detailed results')
    
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