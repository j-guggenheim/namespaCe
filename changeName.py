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

    # in_namespace = False
    # current_namespace_vars = None
    # open_braces_counter = 0

    namespace_stack = [] # Stack to keep track of nested namespace
    current_namespace = None
    # current_namespace_vars = None

    # Regular expression for namespace usage
    namespace_usage_pattern = create_namespace_pattern(namespaces)


    for i, line in enumerate(lines):
        # if 'namespace' in line:
            # # Extract namespace name
            # namespace_name = line.split()[1]  # Assuming 'namespace XYZ {' format
            # namespace_vars = set(namespaces.get(namespace_name, []))
            # current_namespace = Namespace(namespace_name, namespace_vars)
            # 
            # namespace_stack.append(current_namespace)
            # in_namespace = True

            # # NOTE: the below line of code has to change when nested namespace
            # # maybe seperate counters for each namespace?
            # # open_braces_counter = 1 CHANGED

            # continue
        
        # Replace 'namespace::' with 'namespace__'
        line = re.sub(namespace_usage_pattern, r'\1__', line)
            
        namespace_match = re.match(r'\s*namespace\s+((\w|\$)+)\s*\{', line)
        if namespace_match:
            # Extract namespace name from the regex match
            namespace_name = namespace_match.group(1)
            namespace_vars = set(namespaces.get(namespace_name, []))
            current_namespace = Namespace(namespace_name, namespace_vars)

            namespace_stack.append(current_namespace)
            continue

        # TO-DO: maybe a for-loop here iterating through namespace names to change namespace::var

        elif namespace_stack:
            used = []
            # Replace variable names with "TEST" using regex for whole word matching
            for namespace in reversed(namespace_stack):
                for var in namespace.vars:
                    if var not in used:
                        pattern = r'\b' + var + r'\b'  # Word boundary regex
                        used.append(var)    # should it be 'used.append(pattern)' ??
                        # Go through the stack to find nested names of namespaces
                        replacement = namespace.name + '__' + var
                        print(replacement)
                        line = re.sub(pattern, replacement, line)  # Replace with regex
            lines[i] = line
            print(line)

            #if '{' in line:  # End of namespace
            #    open_braces_counter += 1
            #

            #if '}' in line:  # End of namespace
            #    if open_braces_counter == 1:
            #        in_namespace = False
            #    else:
            #        open_braces_counter -= 1
            
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


# if __name__ == "__main__":
#     file = open("test.c", "r")
#     c_code = file.read()
#     # print(text)
#     # Example:
# #     namespaces = {
# #     'myNamespace': ['var1', 'function1', 'var2']
# # }
#     namespaces = {
#     'outerNamespace': ['var1', 'var2', 'testFunction'],
#     'innerNamespace': ['function1', 'var3', 'var2']
# }
#     # globalNames = []
#     # replace_var_names('test.c', namespaces)
#     modified_c_code = replace_var_names(c_code, namespaces)  # Changed to pass string
#     print(modified_c_code) 
    
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

# To change:
# 1. curly brace  DONE
# 2. nested namespaces
    # a. properly identify the namespace associated with each var/function DONE
    # b. change all instances of namespace_name::var_name DONE
    # c. Edge case: if there's an extent variable referenced in a nested namespace, but also a variable of 
    #   the same name for that namespace NOT DONE
# 3. what to set the variable names to  DONE
# 4. concerns with partial matching (ie var1 and var10) DONE