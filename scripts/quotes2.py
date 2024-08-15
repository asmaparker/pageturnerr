import re
import glob

def convert_single_to_double_quotes(json_str):
    pattern = re.compile(r"'(.*?)':\s*'(.*?)'")
    
    def replacer(match):
        return f'"{match.group(1)}": "{match.group(2)}"'
    
    json_str = pattern.sub(replacer, json_str)
    json_str = re.sub(r"'(.*?)':", r'"\1":', json_str)
    json_str = re.sub(r':\s*\'(.*?)\'', r': "\1"', json_str)
    
    return json_str

def process_files(file_list):
    for file_name in file_list:
        with open(file_name, 'r', encoding='utf-8') as file:
            content = file.read()
        
        updated_content = convert_single_to_double_quotes(content)
        
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(updated_content)

# Example usage
file_list = glob.glob(pathname="D:\\Downloads\\asmaaa\\jsons\\*.txt")
process_files(file_list)