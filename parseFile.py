import re
import changeName
import sys

reAttribute = re.compile("\s*__attribute__\s*")
qualifiers = [re.compile("\sstatic\s"), re.compile("\svolatile\s"), re.compile('\stypedef\s'), re.compile("\sconst\s"), re.compile("\s__extension__\s"), re.compile("\s__inline__\s"), re.compile("\sinline\s"), re.compile("\s__volatile__\s"), re.compile("\sextern\s")]
reStructUnion = [re.compile("\sstruct\s"), re.compile("\sunion\s"), re.compile("\senum\s")]

# Unsigned is a problem. Mainly because it can act like a qualifier OR a type. So are "signed", "long", "int", and "short"
# For this reason there are enumerated cases where they are problematic and what should be removed in each case
unsignedProblem = [re.compile('\sunsigned\s(int\s|long\s|char\s|short\s)'), re.compile('\ssigned\s(int\s|long\s|char\s|short\s)'), re.compile('\slong\s(int\s|unsigned\s|signed\s|long\s)'), re.compile('\sshort\s(int\s|unsigned\s|signed\s)'), re.compile('\sint\s(unsigned\s|signed\s)')]
unsignedRemove = [re.compile('\sunsigned\s'), re.compile('\ssigned\s'), re.compile('\slong\s'), re.compile("\sshort\s"), re.compile("\sint\s")]

reNamespace = re.compile('\snamespace\s\S+\s*\{')

reInQuotes = re.compile('(\".*;.*\")|(\'.*;.*\')')

# All of the namespaces
namespaces = {}

# Extracts global symbols from a braceless block
def getNamesFromBracelessBlock(text: str, wasStructUnionEnum = False, onlyWithBraces = False, currentNameSpaceName = ""):

    # Store a copy of text for comparison and debugging purposes
    # textCpy = text
    
    # Track if we've ended on a struct, union, or enum depth (will be a returned value)
    endedOnStructUnionEnumDef = False

    # True only on the first iteration
    firstIt = True

    # Tracks whether there's another semicolon in the braceless block
    hasSem = True

    # Track the name of a namespace if we've entered one (at the end of the braceless block)
    # will be a returned value
    nameSpaceNameParsed = ""

    # Track if we've ended on a namespace
    endsOnNamespace = False

    # While there was a semicolon in the last block of code (or first iteration) keep going
    while hasSem:

        # Update hasSem for next iteration
        firstSemInd = text.find(";")
        hasSem = firstSemInd != -1

        # toNextSem tracks the block of code till the next semicolon or end of braceless block
        toNextSem = text
        if hasSem:
            toNextSem = text[:firstSemInd + 1]

        # Move text forward
        text = text[firstSemInd + 1:]

        # Commas act similarly to sems
        hasComma = True
        while hasComma:

            # curText tracks the block to the next comma
            curText = toNextSem

            # Find the next comma not in parens
            i = 0
            parenDepth = 0
            commaInd = -1
            while i < len(curText):
                if curText[i] == '(':
                    parenDepth += 1
                elif curText[i] == ')':
                    parenDepth -= 1
                elif curText[i] == ',' and parenDepth == 0:
                    commaInd = i
                    break
                i += 1

            hasComma = commaInd != -1

            # As mentioned, curText tracks to the next comma
            if hasComma:
                curText = curText[:commaInd]

            # If there's an equals sign then we can chop off anything after it (can't be a new lvalue)
            assgnmtOpInd = curText.find("=")
            if assgnmtOpInd != -1:
                curText = curText[:assgnmtOpInd]

            #==================================#
            #===========NAME PARSING===========#
            #==================================#

            # Remove any whitespace, semicolons, and asterixes on the ends and add spaces
            # Name and left is named thusly because we work our way towards the name from the left
            nameAndLeft = " " + curText.strip('\n \t*;') + " "

            # Check for a namespace (should only happen at end of braceless block)
            if re.search(reNamespace, nameAndLeft):
                if hasSem or hasComma:
                    print("BUG or bad test code")
                endsOnNamespace = True

            # While "__attribute__" is in nameAndLeft (ugh)
            while re.search(reAttribute, nameAndLeft):

                # Find "__attribute__" starting index
                attributeIndex = nameAndLeft.find(re.search(reAttribute, nameAndLeft).group())

                # Find the start and end parents of the __attribute__ block
                parenInd = nameAndLeft[attributeIndex:].find('(')
                i = parenInd + attributeIndex + 1
                parenDepth = 1
                lastInd = 0
                while lastInd == 0 and i < len(nameAndLeft) - 1:
                    if nameAndLeft[i] == '(':
                        parenDepth += 1
                    elif nameAndLeft[i] == ')':
                        parenDepth -= 1
                    if parenDepth == 0:
                        lastInd = i
                    i += 1

                # Remove the attribute block
                nameAndLeft = nameAndLeft[:attributeIndex] + nameAndLeft[lastInd + 1:]
                
            # Replace any and all whitespace, brackets, parents, asterisks, braces... with a space
            nameAndLeft = re.sub('(\(|\)|\*|\s|\[.*\]|\{|\})+', ' ', nameAndLeft)

            # Check through the qualifiers and remove them if they are present
            for s in qualifiers:
                while re.search(s, nameAndLeft):
                    nameAndLeft = re.sub(s, ' ', nameAndLeft)

            # Check through the qualifiers matching the 'unsigned' problem (See top of file)
            # Remove them in the correct cases
            for (sprob, sfix) in zip(unsignedProblem, unsignedRemove):
                if re.search(sprob, nameAndLeft):
                    nameAndLeft = re.sub(sfix, ' ', nameAndLeft)
            
            # Check if the struct or union or enum keyword is present
            for s in reStructUnion:
                if not hasSem and s.match(nameAndLeft):
                    endedOnStructUnionEnumDef = True
                nameAndLeft = re.sub(s, ' ', nameAndLeft)

            # Remove the spaces on the ends
            nameAndLeft = nameAndLeft.strip(' ')

            # Split by whitespaces
            words = nameAndLeft.split()

            name = None

            # If we're coming from a struct, enum, or union we take the first word
            if len(words) >= 2 and firstIt and wasStructUnionEnum:
                name = words[0]
            # Else if there are more than 1 word take the second
            elif len(words) >= 2:
                name = words[1]
            # Else take the only word
            elif len(words) == 1:
                name = words[0]
            
            # Once we're here firstIt can be set to false
            firstIt = False

            # If we only want names before open braces, then we should check if there's an open brace in the toNextSem block
            if onlyWithBraces and toNextSem.find('{') == -1:
                if name != None and currentNameSpaceName != "":
                    print(currentNameSpaceName + '__' + name)
                    namespaces.get(currentNameSpaceName).append(name)
                name = None

            # If name isn't None then we have a valid name
            if name != None:
                if endsOnNamespace:
                    if '.' not in currentNameSpaceName:
                        nameSpaceNameParsed = (currentNameSpaceName + '__' + name).strip('_')
                elif currentNameSpaceName != "":
                    if endedOnStructUnionEnumDef:
                        nameSpaceNameParsed = currentNameSpaceName + "." + name
                    currentNameSpaceNameAdj = currentNameSpaceName
                    if currentNameSpaceName.find('.') != -1:
                        currentNameSpaceNameAdj = currentNameSpaceName[:currentNameSpaceName.find('.')]
                    print(currentNameSpaceNameAdj + '__' + name)
                    namespaces.get(currentNameSpaceNameAdj).append(name)

            # If there's a comma then we need to move toNextSem forward
            if hasComma:
                toNextSem = words[0] + toNextSem[commaInd + 1:]

    # If we ended on a namespace then we need to make sure it has a valid name
    if endsOnNamespace:
        # Technically, and strangely, dollar signs are allowed in identifier names
        # (at least for GCC which is what we're using)
        if not nameSpaceNameParsed.replace("_","").replace("$", "").isalnum():
            print("Invalid namespace name, invalid character(s): ", nameSpaceNameParsed)
        
        # The first character cannot be numeric in a valid c identifier
        if nameSpaceNameParsed[0].isnumeric():
            print("Invalid namespace name, starts with number: ", nameSpaceNameParsed)
        print("Found namespace: ", nameSpaceNameParsed)


    return (endedOnStructUnionEnumDef, nameSpaceNameParsed)


# Gets all nqmes in namespaces in the text
# Assumes text starts at global scope
def getGlobalNames(text: str):
    print("Get Global Names")
    print()

    # Tracks the current curly brace depth
    curlyBraceDepth = 0

    # Tracks the text left to examine
    curText = text

    # Tracks whether or not we are in a location where globally scoped symbols can be made
    depthToTake = 0 

    # Tracks whether or not we are in a struct union or enum.
    # If so, then only new struct, enum, and union defs are global
    endedOnStructUnionEnum = {-1:False, 0:False}

    # Tracks which curly brace depth we entered into each namespace
    # as well as the names of the namespaces
    namespaceByDepth = [""]

    # Tracks whether or not we are in the last block (no close bracket)
    inLastBlock = False
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

        # If we are not in a globally scoped section then we don't need to check inside
        if curlyBraceDepth > depthToTake:
            curlyBraceDepth += depthChange
            curText = curText[endIndex + 1:]
            continue

        # We should only consider vars followed by braces as global if we are in an enum, struct, or union
        onlyWithBraces = endedOnStructUnionEnum[curlyBraceDepth - 1]

        # newTextToSend contains the current braceless block
        newTextToSend = curText[:endIndex + 1]

        # Calculate the current namespace name from namespaceByDepth
        curNamespaceName = namespaceByDepth[curlyBraceDepth - 1]
        # for s in namespaceByDepth:
        #     if s == "":
        #         break
        #     curNamespaceName = curNamespaceName + '__' + s
        #     curNamespaceName = curNamespaceName.lstrip('_')
        if namespaces.get(curNamespaceName) == None:
            namespaces[curNamespaceName] = []


        # Extract global names from newTextToSend (the braceless block)
        (endedOnStructUnionEnum[curlyBraceDepth], newNameSpaceName) = getNamesFromBracelessBlock(newTextToSend, endedOnStructUnionEnum.get(curlyBraceDepth), onlyWithBraces, curNamespaceName)

        # If newTextToSend ended on a struct, union or enum, or if we entered a new namespace
        # then the depth of global symbols has increased by one 
        if endedOnStructUnionEnum[curlyBraceDepth] or newNameSpaceName:
            depthToTake += 1

        # The namespace returned will be the new namespace at the given depth
        namespaceByDepth.insert(curlyBraceDepth, newNameSpaceName)

        # Get the current braceless block out of curText
        curText = curText[endIndex + 1:]
        
        # Modify the curly brace depth and shrink depth to take to match if necessary
        curlyBraceDepth += depthChange
        if depthToTake > curlyBraceDepth:
                depthToTake = curlyBraceDepth

if __name__ == "__main__":

    firstIt = True;
    for name in sys.argv:
        if firstIt:
            firstIt = False
            continue
        fileName = str(name)
        cFile = open(fileName, 'r')

        fileText = cFile.read()
        reMoveAnnoyingLines = re.compile("\#.*\n")
        fileTextMod = reMoveAnnoyingLines.sub("", fileText)

        fileTextMod = re.sub(reInQuotes, ' ', fileTextMod, count=0)
        
        outFile = open(fileName.split('.')[0] + 'post.' + fileName.split('.')[1], 'w')

        getGlobalNames(fileTextMod)
        print(namespaces)
        outFile.write(changeName.replace_var_names(fileText, namespaces))
    