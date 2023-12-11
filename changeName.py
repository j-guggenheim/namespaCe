import re

class Namespace:
    def __init__(self, name, vars):
        self.name = name
        self.vars = vars
        self.brace_counter = 0

def create_scope_pattern(namespaces):
    # Join all namespace names with '|' to create a pattern that matches any of them
    namespace_names = '|'.join(map(re.escape, namespaces.keys()))
    # Pattern to match 'namespace::'
    namespace_names = namespace_names.strip("|")
    pattern = r'\b({})::'.format(namespace_names)
    return pattern

def extract_string_literals(text):
    string_literals = []
    modified_text = text
    pattern = r'(?<!\\)(["\'])(.*?)(?<!\\)\1'
    matches = list(re.finditer(pattern, text))
    for i, match in enumerate(reversed(matches)):
        literal = match.group(0)
        string_literals.append(literal)
        placeholder = f"__STRING_LITERAL_{i}__"
        start, end = match.span()
        modified_text = modified_text[:start] + placeholder + modified_text[end:]
    return modified_text, string_literals

def reinsert_string_literals(text, string_literals):
    for i, literal in enumerate(string_literals):
        placeholder = f"__STRING_LITERAL_{i}__"
        text = text.replace(placeholder, literal)
    return text



def replace_var_names(c_code, namespaces):

    modified_c_code, string_literals = extract_string_literals(c_code)

    # Regular expression for namespace usage
    scope_usage_pattern = create_scope_pattern(namespaces)

    # Tracks the current curly brace depth
    curlyBraceDepth = 0

    # Tracks the text left to examine
    curText = modified_c_code

    # Tracks which curly brace depth we entered into each namespace
    # as well as the names of the namespaces
    namespaceByDepth = [""]

    toRemove = []

    # Tracks whether or not we are in the last block (no close bracket)
    inLastBlock = False

    retText = ""

    while not inLastBlock:
        

        # Find the end of the current braceless block (endIndex)
        # Find whether we are going shallower or deeper at the end (depthChange)
        # Find whether or not we are in the last block in text (inLastBlock)
        closeCurlyBraceInd = curText.find('}')
        openCurlyBraceInd = curText.find('{')

        depthChange = 1
        endIndex = openCurlyBraceInd
        if closeCurlyBraceInd < openCurlyBraceInd or openCurlyBraceInd == -1:
            depthChange = -1
            endIndex = closeCurlyBraceInd

        if closeCurlyBraceInd == -1 and openCurlyBraceInd == -1:
            inLastBlock = True

        # newTextToSend contains the current braceless block
        newTextToSend = curText[:endIndex + 1]
        curText = curText[endIndex + 1:]


        newTextToSend = newTextToSend.replace("::", "__")
        
        curNamespaceTracker = namespaceByDepth[-1]
        used = []
        while curNamespaceTracker != "":
            for var in namespaces.get(curNamespaceTracker, set()):
                if var not in used:
                    pattern = r'\b' + re.escape(var) + r'\b'

                    used.append(var)

                    if ('.' not in curNamespaceTracker):
                        replacement = curNamespaceTracker + '__' + var
                        newTextToSend = re.sub(pattern, replacement, newTextToSend)
            indToRemove = max(curNamespaceTracker.rfind('.'), curNamespaceTracker.rfind('__'))
            if indToRemove == -1:
                curNamespaceTracker = ""
            else:
                curNamespaceTracker = curNamespaceTracker[:indToRemove]
                
        if depthChange > 0:
            namespace_match = re.search(r'\snamespace\s', newTextToSend)

            semInd = newTextToSend.rfind(";")
            lastStatement = newTextToSend
            if semInd != -1:
                lastStatement = newTextToSend[semInd:]
            structUnionEnum_match = re.search(r'\s(struct|union|enum)\s', lastStatement)

            if namespace_match:
                namespaceInd = newTextToSend.find("namespace")
                name = newTextToSend[namespaceInd:].split()[1].strip("{}")
                if len(namespaceByDepth) == 0:
                    namespaceByDepth.append(name)
                else:
                    namespaceByDepth.append((namespaceByDepth[-1] + '__' + name).strip("_"))
                newTextToSend = re.sub((r'\s*namespace\s*' + name + r'\s*{'),'', newTextToSend)
                toRemove.append(curlyBraceDepth)

            elif structUnionEnum_match:
                structUnionEnum_ind = structUnionEnum_match.start()
                name = lastStatement[structUnionEnum_ind:].split()[1].split('__')[-1].strip("{}")
                if len(namespaceByDepth) == 0:
                    namespaceByDepth.append('.' + name)
                else:
                    namespaceByDepth.append((namespaceByDepth[-1] + '.' + name).strip("_"))
            else:
                namespaceByDepth.append(namespaceByDepth[-1])


        curlyBraceDepth += depthChange
        if depthChange < 0:
            namespaceByDepth.pop()
            if curlyBraceDepth in toRemove:
                newTextToSend = newTextToSend.replace('}', '')
                toRemove.remove(curlyBraceDepth)
        
        retText = retText + newTextToSend
    
    retTextWithStrings = reinsert_string_literals(retText, string_literals)
    return retTextWithStrings
        


if __name__ == "__main__":
    with open("test.c", "r") as file:
        c_code = file.read()

    namespaces = {
    'outerNamespace': ['var1', 'var2', 'testFunction', 'var5'],
    'outerNamespace__innerNamespace': ['var1', 'function1', 'var3'],
    'outerNamespace__veryInnerNamespace': ['var6', 'function2', 'var7'],
    'adjacentNamespace': ['var8', 'function3', 'var9', 'var1']
}
    modified_c_code = replace_var_names(c_code, namespaces)
    print(modified_c_code)