import re

class WordSplitter:
    def __init__(self):
        # Expresión regular para CamelCase
        self.camel_regex = re.compile(r'.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)')

    def split_to_natural_language(self, identifier_list):
        natural_words = []
        for identifier in identifier_list:
            clean_id = re.sub(r'[^a-zA-Z0-9_]', '', identifier)
            
            # Dividir por guiones bajos (snake_case)
            parts = clean_id.split('_')
            
            for part in parts:
                if not part:
                    continue
                
                # Dividir por CamelCase/PascalCase
                words = [m.group(0) for m in self.camel_regex.finditer(part)]
                
                for word in words:
                    low_word = word.lower()
                    if len(low_word) > 1:
                        natural_words.append(low_word)
                        
        return natural_words