import re

class Namespace:
    def __init__(self, name, vars):
        self.name = name
        self.vars = vars
        self.brace_counter = 1

def create_namespace_pattern(namespaces):
    # Join all namespace names with '|' to create a pattern that matches any of them
    namespace_names = '|'.join(map(re.escape, namespaces.keys()))
    # Pattern to match 'namespace::'
    pattern = r'\b({})::'.format(namespace_names)
    return pattern


def replace_var_names(c_code, namespaces):
    lines = c_code.split('\n')
    modified_lines = [] 


    namespace_stack = [] # Stack to keep track of nested namespace
    current_namespace = None
    namespace_map = {}

    # Regular expression for namespace usage
    namespace_usage_pattern = create_namespace_pattern(namespaces)


    for i, line in enumerate(lines):
        
        # Replace 'namespace::' with 'namespace__'
        match = re.search(namespace_usage_pattern, line)
        if match:
            match = namespace_map[match.group(1)]
            line = re.sub(namespace_usage_pattern, match+'__', line) 
            
        namespace_match = re.match(r'\s*namespace\s+((\w|\$)+)\s*\{', line) # Assuming 'namespace XYZ {' format
        if namespace_match:
            # Extract namespace name from the regex match
            namespace_name = namespace_match.group(1)
            namespace_vars = set(namespaces.get(namespace_name, []))
            current_namespace = Namespace(namespace_name, namespace_vars)
            if namespace_stack:
                # add all outer namespace names to this inner one before appending
                for outer_name in namespace_stack:
                    current_namespace.name = outer_name.name + '__' + current_namespace.name
            namespace_stack.append(current_namespace)
            namespace_map[namespace_name] = current_namespace.name
            continue

        elif namespace_stack:
            used = []
            # Replace variable names with "TEST" using regex for whole word matching
            for namespace in reversed(namespace_stack):
                for var in namespace.vars:
                    if var not in used:
                        pattern = r'\b' + re.escape(var) + r'\b'  # Word boundary regex
                        used.append(var)    # should it be 'used.append(pattern)' ??
                        # Go through the stack to find nested names of namespaces
                        replacement = namespace.name + '__' + var
                        line = re.sub(pattern, replacement, line)  # Replace with regex
            lines[i] = line
            
            # Update brace counters
            if '{' in line:
                current_namespace.brace_counter += 1
            if '}' in line:
                if current_namespace.brace_counter == 1:
                    namespace_stack.pop()  # Leave the current namespace
                    # Update current_namespace and current_vars after popping
                    if namespace_stack:
                        current_namespace = namespace_stack[-1]
                    else:
                        current_namespace = None
                    continue
                else:
                    current_namespace.brace_counter -= 1


        modified_lines.append(line)

    return '\n'.join(modified_lines)

    
if __name__ == "__main__":
    with open("test.c", "r") as file:
        c_code = file.read()

    namespaces = {
    'outerNamespace': ['var1', 'var2', 'testFunction', 'var5'],
    'innerNamespace': ['var1', 'function1', 'var3'],
    'veryInnerNamespace': ['var6', 'function2', 'var7'],
    'adjacentNamespace': ['var8', 'function3', 'var9', 'var1']
}

    modified_c_code = replace_var_names(c_code, namespaces)
    print(modified_c_code)