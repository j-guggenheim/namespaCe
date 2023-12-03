import re

def replace_var_names(c_code, namespaces):
    lines = c_code.split('\n')
    modified_lines = [] 

    in_namespace = False
    current_namespace_vars = None
    open_braces_counter = 0

    for i, line in enumerate(lines):
        if 'namespace' in line:
            # Extract namespace name
            namespace_name = line.split()[1]  # Assuming 'namespace XYZ {' format
            current_namespace_vars = set(namespaces.get(namespace_name, []))
            in_namespace = True

            # NOTE: the below line of code has to change when nested namespace
            # maybe seperate counters for each namespace?
            open_braces_counter = 1
            continue

        elif in_namespace:
            # Replace variable names with "TEST" using regex for whole word matching
            for var in current_namespace_vars:
                pattern = r'\b' + re.escape(var) + r'\b'  # Word boundary regex
                line = re.sub(pattern, "TEST", line)  # Replace with regex
            lines[i] = line

            if '{' in line:  # End of namespace
                open_braces_counter += 1
            

            if '}' in line:  # End of namespace
                if open_braces_counter == 1:
                    in_namespace = False
                else:
                    open_braces_counter -= 1
            
        modified_lines.append(line)

    return '\n'.join(modified_lines)


if __name__ == "__main__":
    file = open("test.c", "r")
    c_code = file.read()
    # print(text)
    # Example:
    namespaces = {
    'myNamespace': ['var1', 'function1', 'var2']
}
    # globalNames = []
    # replace_var_names('test.c', namespaces)
    modified_c_code = replace_var_names(c_code, namespaces)  # Changed to pass string
    print(modified_c_code) 
    


# To change:
# 1. curly brace 
# 2. nested namespaces
# 3. what to set the variable names to
# 4. concerns with partial matching (ie var1 and var10)