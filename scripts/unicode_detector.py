import json

# Read the first few lines of your JSONL file and check for Unicode characters
with open("results/gemini_evaluation.jsonl", 'r', encoding='utf-8') as file:
    lines = file.readlines()

for i, line in enumerate(lines[:4]):  # Check first 4 lines
    data = json.loads(line.strip())
    
    print(f"\nLine {i+1}:")
    print(f"Question ID: {data['question_id']}")
    
    # Check each field for Unicode characters
    for field_name, field_value in data.items():
        if isinstance(field_value, str):
            # Find Unicode characters
            unicode_chars = []
            for pos, char in enumerate(field_value):
                if ord(char) > 127:
                    unicode_chars.append((pos, char, ord(char), hex(ord(char))))
            
            if unicode_chars:
                print(f"  {field_name}: Found Unicode characters:")
                for pos, char, code, hex_code in unicode_chars[:5]:  # Show first 5
                    print(f"    Position {pos}: '{char}' (U+{hex_code[2:].upper().zfill(4)}, {code})")
            else:
                print(f"  {field_name}: No Unicode characters found")