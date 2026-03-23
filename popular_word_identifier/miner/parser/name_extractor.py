import ast
import re
import os

class NameExtractor:
    def __init__(self, storage_path="../../temp_data"):
        self.storage_path = storage_path

    def extract_from_storage(self):
        all_names = []
        files = [f for f in os.listdir(self.storage_path) if os.path.isfile(os.path.join(self.storage_path, f))]
        for filename in files:
            file_path = os.path.join(self.storage_path, filename)
            
            if filename.endswith('.py'):
                all_names.extend(self._parse_python(file_path))
            elif filename.endswith('.java'):
                all_names.extend(self._parse_java(file_path))
            
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error al eliminar {filename}: {e}")
                
        return all_names

    def _parse_python(self, path):
        names = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        names.append(node.name)
        except Exception as e:
            print(f"Error parseando Python {path}: {e}")
        return names

    def _parse_java(self, path):
        names = []
        method_regex = re.compile(r'(?:public|protected|private|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *\{')
        var_regex = re.compile(r'(?:[A-Z]\w+|int|double|float|char|boolean|long|byte)\s+(\w+)\s*(?:=|;)')
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                names.extend(method_regex.findall(content))
                names.extend(var_regex.findall(content))
        except Exception as e:
            print(f"Error parseando Java {path}: {e}")
        return names