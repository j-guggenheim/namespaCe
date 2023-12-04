import re
import changeName

reAttribute = re.compile("\s*__attribute__\s*")
qualifiers = [re.compile("\sstatic\s"), re.compile("\svolatile\s"), re.compile('\stypedef\s'), re.compile("\sconst\s"), re.compile("\s__extension__\s"), re.compile("\s__inline__\s"), re.compile("\sinline\s"), re.compile("\s__volatile__\s"), re.compile("\sextern\s")]
reStructUnion = [re.compile("\sstruct\s"), re.compile("\sunion\s"), re.compile("\senum\s")]

# Unsigned is a problem. Mainly because it can act like a qualifier OR a type
unsignedProblem = [re.compile('\sunsigned\s(int\s|long\s|char\s|short\s)'), re.compile('\ssigned\s(int\s|long\s|char\s|short\s)'), re.compile('\slong\s(int\s|unsigned\s|long\s)'), re.compile('\sshort\s(int\s|unsigned\s)')]
unsignedRemove = [re.compile('\sunsigned\s'), re.compile('\ssigned\s'), re.compile('\slong\s'), re.compile("\sshort\s")]

reNamespace = re.compile('\snamespace\s\S+\s*\{')

namespaces = {}

def getNamesFromBracelessBlock(text: str, wasStructUnionEnum = False, onlyWithBraces = False, currentNameSpaceName = ""):

    textCpy = text
    
    endedOnStructUnionEnumDef = False

    firstIt = True

    hasSem = True

    nameSpaceNameParsed = ""

    endsOnNamespace = False

    while hasSem:

        firstSemInd = text.find(";")
        hasSem = firstSemInd != -1

        toNextSem = text
        if hasSem:
            toNextSem = text[:firstSemInd + 1]
        text = text[firstSemInd + 1:]

        hasComma = True
        while hasComma:

            curText = toNextSem



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

            # commaInd = curText.find(',')
            hasComma = commaInd != -1

            if hasComma:
                curText = curText[:commaInd]



            assgnmtOpInd = curText.find("=")
            if assgnmtOpInd != -1:
                curText = curText[:assgnmtOpInd]

            nameAndLeft = " " + curText.strip('\n \t*;') + " "



            if re.search(reNamespace, nameAndLeft):
                if hasSem or hasComma:
                    print("JACK YOU'VE GOT A BIG BUG CTRL F THIS TEXT 1")
                endsOnNamespace = True



            while re.search(reAttribute, nameAndLeft):
                attributeIndex = nameAndLeft.find(re.search(reAttribute, nameAndLeft).group())
                # print('\t\t' + nameAndLeft)

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
                nameAndLeft = nameAndLeft[:attributeIndex] + nameAndLeft[lastInd + 1:]
                

            nameAndLeft = re.sub('(\(|\)|\*|\s|\[.*\]|\{|\})+', ' ', nameAndLeft)

            

            for s in qualifiers:
                while re.search(s, nameAndLeft):
                    nameAndLeft = re.sub(s, ' ', nameAndLeft)
                    






            for (sprob, sfix) in zip(unsignedProblem, unsignedRemove):
                if re.search(sprob, nameAndLeft):
                    nameAndLeft = re.sub(sfix, ' ', nameAndLeft)
            


            for s in reStructUnion:
                if not hasSem and s.match(nameAndLeft):
                    endedOnStructUnionEnumDef = True
                nameAndLeft = re.sub(s, ' ', nameAndLeft)



            nameAndLeft = nameAndLeft.strip(' ')

            words = nameAndLeft.split()

            name = None
            if len(words) >= 2 and firstIt and wasStructUnionEnum:
                name = words[0]
            elif len(words) >= 2:
                name = words[1]
            elif len(words) == 1:
                name = words[0]
            
            firstIt = False

            if onlyWithBraces and toNextSem.find('{') == -1:
                name = None

            if name != None:
                if endsOnNamespace:
                    nameSpaceNameParsed = name
                elif currentNameSpaceName != "":
                    print(currentNameSpaceName + name)
                    namespaces.get(currentNameSpaceName).append(name)

            if hasComma:
                toNextSem = words[0] + toNextSem[commaInd + 1:]

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


# Gets all global names (including in namespaces) in the text
# Assumes text starts at global scope
def getGlobalNames(text: str):
    print("Get Global Names")
    print()

    curlyBraceDepth = 0
    curText = text

    endedOnStructUnionEnum = {-1:False, 0:False}
    depthToTake = 0 

    inLastBlock = False

    namespaceByDepth = [""]

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

        onlyWithBraces = endedOnStructUnionEnum[curlyBraceDepth - 1]
        newTextToSend = curText[:endIndex + 1]

        curNamespaceName = ""
        for s in namespaceByDepth:
            if s == "":
                break
            curNamespaceName = curNamespaceName + '__' + s
            curNamespaceName = curNamespaceName.lstrip('_')
        if namespaces.get(curNamespaceName) == None:
            namespaces[curNamespaceName] = []

        (endedOnStructUnionEnum[curlyBraceDepth], newNameSpaceName) = getNamesFromBracelessBlock(newTextToSend, endedOnStructUnionEnum.get(curlyBraceDepth), onlyWithBraces, curNamespaceName)

        if endedOnStructUnionEnum[curlyBraceDepth] or newNameSpaceName:
            depthToTake += 1

        namespaceByDepth.insert(curlyBraceDepth, newNameSpaceName)

        curText = curText[endIndex + 1:]
        
        curlyBraceDepth += depthChange
        if depthToTake > curlyBraceDepth:
                depthToTake = curlyBraceDepth

if __name__ == "__main__":
    cFile = open('test3pre.c', 'r')

    fileText = cFile.read()
    reMoveAnnoyingLines = re.compile("\#.*\n")
    fileTextMod = reMoveAnnoyingLines.sub("", fileText)
    
    outFile = open('test3post.c', 'w')

    getGlobalNames(fileTextMod)
    outFile.write(changeName.replace_var_names(fileText, namespaces))
    