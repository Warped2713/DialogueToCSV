# coding: utf-8
import os
import sys
import string
import codecs

def main():
    
    with codecs.open('SpriteFont_Input.txt', 'rb', 'utf-8') as infile, codecs.open('SpriteFont_Output_JSON.txt', 'w+b', 'utf-8') as outfile:
        for line in infile:
            fontstyle = line.strip()            
            sizeA = float( next(infile).strip() )
            sizeB = next(infile).strip()
            fontname = fontstyle + " " + sizeB
            sizeB = float(sizeB)
            ratioBA = sizeB / sizeA
            xShift = float( next(infile).strip() )
            charList = next(infile).strip()
            widthList = next(infile).strip().split()
            addList = next(infile).strip().split()
            subList = next(infile).strip().split()
            next(infile) # empty line
            
            newWidthList = []
            newCharList = []
            print(fontstyle)
            print(charList.encode('utf-8'))
            print(len(charList))
            print(len(widthList))
            for i in range(0, len(charList)):
                c = charList[i]
                if c == u'"':
                    c = u'\\""'
                w = int( ratioBA * ( float( widthList[i] ) + xShift ) )                
                
                # Optionally, adjust widths +/-
                #w = w + int(addList[i]) - int(subList[i])
                
                # Group characters by size
                if w in newWidthList:
                    x = newWidthList.index(w)
                    newCharList[x] += c
                else:
                    newWidthList.append(w)
                    newCharList.append(c)
                
                # Alternative: List each character and width separately
                #newWidthList.append(w)
                #newCharList.append(c)
            
            # Print in c2array format
            text = u'{""c2array"":true,""size"":[2,' + unicode(str(len(newWidthList)), encoding='utf-8') + u',1],""data"":[ [ '
            text += u','.join(u'[' + unicode(str(e), encoding='utf-8') + u']' for e in newWidthList) + u' ], [ '
            text += u','.join(u'[""' + f + u'""]' for f in newCharList) + u' ] ]}'
            
            outfile.write( fontname + u'\n' + text + u'\n\n')
            
if __name__ == "__main__": main()
