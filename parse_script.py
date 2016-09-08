# coding: utf-8
import os
import re
import sys
import csv
import string
import logging
import codecs

class RowObject:
    """
    A row of dialogue
    """
    def __init__(self, section, ID, chara, rowtype, tag="", linetxt="", optxt="", cond=[], trig1=[], trig2=[], next=[], score="", setname=""):
        self.rowID = ID
        self.section = section
        self.chara = chara
        self.rowtype = rowtype
        self.tag = tag
        self.line = linetxt
        self.optxt = optxt
        self.cond = cond
        self.trig1 = trig1
        self.trig2 = trig2
        self.next = next
        self.score = score
        self.setname = setname
    def __str__(self):
        return "\n{ ID:" + str(self.rowID) + ", Sect:" + self.section + ", Char:" + self.chara + ", Type:" + self.rowtype + ", Tag:" + self.tag + ", Line:" + self.line + ", Opt:" + self.optxt + ", Condition:" + str(self.cond) + ", PreTriggers:" + str(self.trig1) + ", PostTriggers:" + str(self.trig2) + ", Next:" + str(self.next) + ", Score:" + str(self.score) + ", SetName: " + self.setname + " }\n"
        
class Chapter:    
    def __init__(self, ID, story, section, deli):
        self.ID = ID+1
        self.story = story
        self.section = section
        self.deli = deli
        self.rowSet = []
        self.cDict = {}
        self.rDict = {}
        self.paired = {}
        self.pairableC = {}
        self.pairableRC = {}
        self.pairableR = {}
        self.cPreTrig = {}
        self.cPostTrig = {}
        self.rPreTrig = {}
        self.rPostTrig = {}
        
        self.filename = story.replace(" ", "_") + "_" + section.replace(" ", "_")
        self.outfile = open(self.filename + '.csv', 'w+b')
        self.writer = csv.DictWriter(self.outfile, delimiter=self.deli, fieldnames=['Line ID', 'Story', 'Section', 'Character', 'Line', 'Option Text', 'Condition', 'Triggers Before Line', 'Triggers After Line', 'NextID1', 'NextID2', 'NextID3', 'NextID4', 'Score Modification'], quotechar='"', quoting=csv.QUOTE_MINIMAL)
        self.writer.writeheader()
                

def clean_script(script, outscript, v_names):
    # Open the script.txt file for cleaning
    with open(script, 'rb') as original, open(outscript, 'w+b') as script:
        for line in original:
            # Remove unnecessary white space
            line = line.strip()
            # Replace weird 'single quote' encodings
            #line = line.replace('’', '\'')
            # Replace weird "double quote" encodings
            #line = line.replace('“', '"')
            #line = line.replace('”', '"')
            if line != '':
                line = line.decode("utf-8-sig")
                line = line.encode("utf-8")
                script.write( line + "\n")
            for m in re.finditer(r"(%\w+%)", line):
                word = line[m.start():m.end()]
                if word not in v_names:
                    v_names.append( word.strip('%') )

def parse_emoticons(emotefile):
    emotes = []
    with open(emotefile, 'rb') as all_emotes:
        for line in all_emotes:
            line = line.split(" ")
            if line[0] != "Unset":
                emotes.append(line)
    return emotes

def replace_emotes(emotes, line):
    for emo in emotes:
        line = line.replace(emo[1],emo[2])
    return line
    
INITIALIZED = 0
CHOICE = 1
RESPONSE = 2 
SIMPLE = 3

def main():
    logging.basicConfig(filename='parse_script_errorlog.txt', filemode='w', level=logging.DEBUG, format='\n%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    
    infile = "script_formatted.txt"
    emotefile = "emoticon_dict.txt"
    delimiter = ""
    
    # Check if given a file
    if len(sys.argv) > 1:
        infile = sys.argv[1]
    
    # Check if our infile doesn't exist
    while not infile or not os.path.isfile(infile): 
        # Prompt user for a filename
        infile = raw_input('\n> Please enter the filename of your script file.\nThe file must be a .txt file in the SAME DIRECTORY as this program and formatted correctly\n\n>>> Input Filename: ')
    
    outscript = infile.split(".")[0] + "_cleaned.txt"
    
    # Check if our emotefile doesn't exist
    while not emotefile or not os.path.isfile(emotefile): 
        # Prompt user for a filename
        emotefile = raw_input('\n> Please enter the filename of your emoticon dictionary file.\nThe file must be a .txt file in the SAME DIRECTORY as this program\n\n>>> Input Emoticon Filename: ')
        
    # Check if our emotefile doesn't exist
    while not delimiter or len(delimiter) != 1: 
        # Prompt user for a filename
        delimiter = raw_input('\n> Choose a delimiter character for your CSV, such as a comma, semi-colon, or pipe.\n\n>>> Input Delimiter: ')
    
    print('\n>Reading in emoticon dictionary from ' + emotefile)
    logging.debug('\n>Reading in emoticon dictionary from ' + emotefile)
    
    # Prepare Emoticon List
    emotes = parse_emoticons(emotefile)
    
    print('\n>Cleaning the script file '+ infile +'.\n>Cleaned script file will be saved in '+ outscript)
    logging.debug('\n>Cleaning the script file '+ infile +'.\n>Cleaned script file will be saved in '+ outscript)
    
    variable_names = []
    
    # Clean file
    clean_script(infile, outscript, variable_names)
    
    print('\n>Analyzing script...')
    logging.debug('\n>Analyzing script...')
    
    # Process script file
    with open(outscript, 'rb') as script:
    
        line = script.readline().strip()
        parse_mode = INITIALIZED
        rowtype = ["INITIALIZED", "CHOICE", "RESPONSE", "SIMPLE", "ENDING"]
        
        title = ""
        chapter = -1
        chapterSet = []
        section = ""
        chara_names = []
        chara = ""
        condition = []
        
        default_values = {
        }
        
        currentTag = "" # to help organize rows into dictionaries
        current_triggers = []
        incomplete = {
            "INITIALIZED" : "",
            "SIMPLE" : "",
            "CHOICE" : "",
            "RESPONSE" : ""
            }
        
        while line:
            nextline = script.readline().strip()
            
            logging.debug("Current Line: " + line)
                
            # Process comments
            if line[:2] == "//":
                # Get title
                if "[Title]" in line:
                    title = line.strip("//").strip()[len("[Title]"):].strip()
                    logging.debug("Title: " + title )
                # Get character
                elif "[Characters]" in line:
                    chara_names = line.strip("//").strip()[len("[Characters]"):].strip().upper().split(", ")
                    logging.debug("Names: " + str(chara_names) )
                # Get chapter
                elif "[Section]" in line:
                    section = line.strip("//").strip()[len("[Section]"):].strip()
                    logging.debug("Section: " + section)
                    chapter += 1;
                    chapterSet.append( Chapter(chapter, title, section, delimiter) )
                    parse_mode = INITIALIZED
                # Get Default Vars
                elif "[Default]" in line:
                    varval = line.split()
                    if varval[1] not in variable_names:
                        variable_names.append(varval[1])
                    default_values[varval[1]] = line[line.find("=")+1:].strip()
                # Get condition
                elif "[Condition]" in line:
                    condition.append( 
                        "if " + 
                        line.strip("//").strip()[len("[Condition]"):].strip()
                        )
                elif "[EndCondition]" in line:
                    condition = []
                # Get event
                elif "[Event Trigger]" in line:
                    trigs = line.strip("//").strip()[len("[Event Trigger]"):].strip()
                    
                    # Collect variables
                    if "Set" in trigs:
                        s = trigs[trigs.index("Set")+3:].split()[0]
                        if s not in variable_names:
                            variable_names.append( s )
                    elif "Request" in trigs:
                        s = trigs[trigs.index("Request")+7:].split()[0]
                        if s not in variable_names:
                            variable_names.append( s )
                    
                    # If in the middle of a row creation, set the row's PreTriggers
                    row = incomplete[ rowtype[parse_mode] ]                    
                    if row:
                        row.trig1.append(trigs)
                    
                    # Put it aside for post-processing Choice rows
                    elif parse_mode == CHOICE:
                        if chapterSet[chapter].cDict[ currentTag ]:
                            chapterSet[chapter].cPostTrig[ currentTag ].append(trigs)
                        else:
                            chapterSet[chapter].cPreTrig[ currentTag ].append(trigs)
                    
                    # Put it aside for post-processing Response rows
                    elif parse_mode == RESPONSE:
                        if chapterSet[chapter].rDict[ currentTag ]:
                            chapterSet[chapter].rPostTrig[ currentTag ].append(trigs)
                        else:
                            chapterSet[chapter].rPreTrig[ currentTag ].append(trigs)
                    
                    # Save it for the first row's PreTriggers
                    elif parse_mode == INITIALIZED:
                        current_triggers.append(trigs)
                        
                    else: # Append to the end of the last row's PostTriggers
                        chapterSet[chapter].rowSet[-1].trig2 = list(chapterSet[chapter].rowSet[-1].trig2 + [trigs])
                
                # Special case for Ending Text: A row without a character
                elif "[EndingText]" in line:
                    row = RowObject( section, len(chapterSet[chapter].rowSet), "", rowtype="ENDING", linetxt=line.strip("//").strip()[len("[EndingText]"):].strip(), cond=list(condition), setname="EndingText" )
                    chapterSet[chapter].rowSet.append(row)
                    row.trig1 = current_triggers
                    current_triggers = []
                
                # Otherwise ignore
                else:
                    pass
                
            # Process names and decide parse_mode
            elif line.strip(":").upper() in chara_names:
                chara = string.capwords( line.strip(":") )
                # Check if next is Choice Set
                if nextline[0] != "#":
                    parse_mode = SIMPLE
                    currentTag = ""
            
            elif line[0] == "#":
                # Check if next is Choice Set
                if "Choice Set" in line:
                    parse_mode = CHOICE
                    # Set current tag
                    currentTag = line.split()[0]
                    chapterSet[chapter].cDict[currentTag] = []
                    chapterSet[chapter].paired[currentTag] = []
                    chapterSet[chapter].pairableRC[currentTag] = []
                    chapterSet[chapter].pairableC[currentTag] = []
                    chapterSet[chapter].cPreTrig[currentTag] = []
                    chapterSet[chapter].cPostTrig[currentTag] = []
                # Check if next is Response Set
                elif "Response Set" in line:
                    parse_mode = RESPONSE
                    # Set current tag
                    currentTag = line.split()[0]
                    chapterSet[chapter].rDict[currentTag] = []
                    chapterSet[chapter].pairableR[currentTag] = []
                    resetR = 0
                    chapterSet[chapter].rPreTrig[currentTag] = []
                    chapterSet[chapter].rPostTrig[currentTag] = []
            
            # Must be parsed further for row data
            else:
                logging.debug("MODE: " + rowtype[parse_mode] )
                
                # SIMPLE mode
                if parse_mode == SIMPLE:
                    
                    if "{{" in line:
                        
                        # Check if an incomplete row exists
                        if incomplete[ rowtype[parse_mode] ]:
                            row = incomplete[ rowtype[parse_mode] ]
                        
                        # Else must be a new line of text
                        else:
                            row = RowObject( section, len(chapterSet[chapter].rowSet), chara, rowtype[parse_mode], linetxt="", cond=list(condition), setname="Normal" )
                            chapterSet[chapter].rowSet.append(row)
                            row.trig1 = current_triggers
                            current_triggers = []
                    
                    # Else it must be a continuation line
                    else:
                        # Set row to previously incomplete row
                        row = incomplete[ rowtype[parse_mode] ]
                        
                    # ===Now check for line endings===
                    if row:
                        if "}}" in line:
                            # Append message text
                            row.line += line[:line.index("}}")].strip("{{").strip()
                            # Get and set tag
                            # If [[Next]]
                            if "[[" in line and "]]" in line:
                                tag = line[line.index("[[")+2:line.index("]]")].strip()
                                # set the tag
                                row.tag = tag
                            # Clear Incomplete holder
                            incomplete[ rowtype[parse_mode] ] = ""
                        else:
                            # There must be another line of message text to add
                            # Append message text
                            row.line += line.strip("{{").strip()
                            # Set incomplete = row
                            incomplete[ rowtype[parse_mode] ] = row
                            row.line += "\n"
                    else:
                        logging.debug("Expected a continuation of a previous normal line text, but no previous line could be found!")
                        raise ValueError("Expected a continuation of a previous normal line text, but no previous line could be found!")
                        
                # CHOICE mode
                if parse_mode == CHOICE:
                    
                    firstWord = line.split()[0].strip()
                    skipline = 0
                    # Check if this line has a score marker in front
                    if "[" in firstWord and "]" in firstWord:
                        
                        # Create new row with score, optxt, without any linetext
                        smod = firstWord.strip("[").strip("]")
                        opt = line[ line.index("]")+1: ].strip()
                        row = RowObject(section, len(chapterSet[chapter].rowSet), chara, rowtype[parse_mode], linetxt="", optxt=opt, cond=list(condition), score=smod, setname=currentTag)
                        
                        # Add row to sets and dictionary
                        chapterSet[chapter].rowSet.append(row)
                        chapterSet[chapter].cDict[ currentTag ].append(row.rowID)
                        chapterSet[chapter].pairableRC[ currentTag ].append(row.rowID)
                        row.trig1 = current_triggers
                        current_triggers = []
                        
                        # Set Incomplete to this row
                        incomplete[ rowtype[parse_mode] ] = row
                        
                        # Set skip line true
                        skipline = 1
                        
                    # Otherwise if starting line text
                    elif "{{" == firstWord:
                        
                        # Check if an incomplete row exists
                        if incomplete[ rowtype[parse_mode] ]:
                            row = incomplete[ rowtype[parse_mode] ]
                        
                        # Else must be a non-choice additional text
                        else:
                            row = RowObject( section, len(chapterSet[chapter].rowSet), chara, rowtype[parse_mode], linetxt="", cond=list(condition), setname=currentTag )
                            chapterSet[chapter].rowSet.append(row)
                            chapterSet[chapter].cDict[ currentTag ].append(row.rowID)
                            row.trig1 = current_triggers
                            current_triggers = []
                            if len(chapterSet[chapter].pairableRC[ currentTag ]) == 0:
                                chapterSet[chapter].pairableRC[ currentTag ].append(row.rowID)
                    
                    # Else it must be a continuation line
                    else:
                        # Set row to previously incomplete row
                        row = incomplete[ rowtype[parse_mode] ]
                        
                    # ===Now check for line endings===
                    if row:
                        if "}}" in line:
                            # Append message text
                            row.line += line[:line.index("}}")].strip("{{").strip()
                            # Get and set tag
                            if "[[" in line and "]]" in line:
                                tag = line[line.index("[[")+2:line.index("]]")].strip()
                                # set the tag
                                row.tag = tag
                                if "#" in tag:
                                    chapterSet[chapter].pairableC[ currentTag ].append(row.rowID)
                                # Clear Incomplete holder
                                #incomplete[ rowtype[parse_mode] ] = ""
                            
                            # Clear Incomplete holder
                            incomplete[ rowtype[parse_mode] ] = ""
                            
                            #else:
                            #    # There must be another line of message text to add
                            #    # Set incomplete = row
                            #    incomplete[ rowtype[parse_mode] ] = row
                            #    row.line += "\n"
                        elif skipline:
                            logging.debug("Skipping append")
                            pass
                        else:
                            # Append message text
                            row.line += line.strip("{{").strip()
                            # Set incomplete = row
                            incomplete[ rowtype[parse_mode] ] = row
                            row.line += "\n"
                    
                    else:
                        logging.debug("Expected a continuation of a previous choice line text, but no previous choice line could be found!")
                        raise ValueError("Expected a continuation of a previous choice line text, but no previous choice line could be found!")
                    
                # RESPONSE mode
                if parse_mode == RESPONSE:
                    
                    # Check if starting line
                    if "{{" == line.split()[0].strip():
                        # Create new row and add to set and dictionary
                        row = RowObject( section, len(chapterSet[chapter].rowSet), chara, rowtype[parse_mode], linetxt="", cond=list(condition), setname=currentTag )
                        chapterSet[chapter].rowSet.append(row)
                        chapterSet[chapter].rDict[ currentTag ].append(row.rowID)
                        row.trig1 = current_triggers
                        current_triggers = []
                        
                        if len(chapterSet[chapter].rDict[ currentTag ]) == 1 or resetR:
                            chapterSet[chapter].pairableR[ currentTag ].append(row.rowID)
                            resetR = 0
                        logging.debug("Created a new row " + str(row))
                    # Else it must be a continuation line
                    else:
                        # Set row to previously incomplete row
                        row = incomplete[ rowtype[parse_mode] ]
                        logging.debug("Using a previous row " + str(row))
                        
                    # ===Now check for line endings===
                    if row:
                        if "}}" in line: 
                            # Append message text
                            row.line += line[:line.index("}}")].strip("{{").strip()
                            # Get and set tag
                            # If [[#Tag]]
                            if "[[" in line and "]]" in line:
                                tag = line[line.index("[[")+2:line.index("]]")].strip()
                                # set the tag
                                row.tag = tag
                                resetR = 1
                            # Clear Incomplete holder
                            incomplete[ rowtype[parse_mode] ] = ""
                        else:
                            # Append message text
                            row.line += line.strip("{{").strip()
                            # Set incomplete = row
                            incomplete[ rowtype[parse_mode] ] = row
                            row.line += "\n"
                    else:
                        logging.debug("Expected a continuation of a previous response line text, but no previous line could be found!")
                        raise ValueError("Expected a continuation of a previous response line text, but no previous line could be found!")
            
            # Proceed through file
            line = nextline
    
    for chap in chapterSet:
        
        print("\n>Writing to CSV file " + chap.filename + ".csv")
        logging.debug("\n>Writing to CSV file " + chap.filename + ".csv")
        logging.debug( "========== Choices =========" )
        logging.debug( str(chap.cDict) )
        logging.debug( "========== Pairable Choices =========" )
        logging.debug( str(chap.pairableC) )
        logging.debug( "========== Responses =========" )
        logging.debug( str(chap.rDict) )
        logging.debug( "========== Pairable Responses =========" )
        logging.debug( str(chap.pairableR) )
        logging.debug( "========== Pairable Response-Choices =========" )
        logging.debug( str(chap.pairableRC) )
        #logging.debug( "========== Current Row Data w/o NextID =========" )
        #for row in chap.rowSet:
        #    logging.debug( str(row) )
        
        # ========= Now go through rowSet and update Next data =========
        for row in chap.rowSet:
            #logging.debug("Type: " + row.rowtype)
            #logging.debug("Tag: " + row.tag)
            #logging.debug("Set: " + row.setname)
            
            # Simple Row NextID
            if row.rowtype == "SIMPLE":
                if "#" in row.tag:
                    set = chap.pairableRC[row.tag]
                    if type(set) is list:
                        row.next = set
                    else: 
                        row.next = [ set ]
                elif row.rowID != chap.rowSet[-1].rowID:
                    row.next = [ row.rowID+1 ]
                else:
                    row.next = [ ]
            
            # Choice Row NextID and Triggers
            elif row.rowtype == "CHOICE":
                if row.tag != "":
                    if chap.cPreTrig[row.setname]:
                        row.trig1 = list(row.trig1 + chap.cPreTrig[row.setname])
                    if chap.cPostTrig[row.setname]:
                        row.trig2 = list(row.trig2 + chap.cPostTrig[row.setname])
                    
                if "#" in row.tag:
                    if chap.rowSet[row.rowID-1].tag == "Next":
                        row.next = [ chap.pairableR[row.tag][0] ]
                    
                    elif row.optxt == "" and row.rowID not in chap.rowSet[row.rowID-1].next:
                        set = chap.pairableR[row.tag]
                        if type(set) is list:
                            row.next = set
                        else: 
                            row.next = [ set ]
                    
                    else:
                        if not chap.pairableR[row.tag]:
                            logging.debug("Could not find a response row for given choice")
                            raise ValueError("Could not find a response row for given choice")
                        elif len(chap.pairableR[row.tag]) > 1:
                            i = chap.pairableC[row.setname].index(row.rowID)
                            row.next = [ chap.pairableR[row.tag][i] ]
                        else:
                            row.next = [ chap.pairableR[row.tag][0] ]
                            
                elif row.tag == "Next":
                    # Find first occurence of a line in pairableC without a NEXT tag
                    for c in chap.pairableC[row.setname]:
                        if chap.rowSet[c].tag != "Next":
                            row.next = [c]
                    if not row.next:
                        logging.debug("Could not find a shared message row for given [[Next]] choice")
                        raise ValueError("Could not find a shared message row for given [[Next]] choice")
                elif row.tag == "End":
                    row.next = [ chap.rowSet[-1].rowID ]
                else:
                    logging.debug("Found a choice line without a tag. Assigning it to line immediately below.")
                    logging.debug(row.rowID)
                    if row.rowID != chap.rowSet[-1].rowID:
                        row.next = [ row.rowID+1 ]
                    else:
                        row.next = [  ]
            # Response Row NextID and Triggers
            elif row.rowtype == "RESPONSE":
                if row.tag != "":
                    if chap.rPreTrig[row.setname]:
                        row.trig1 = list(row.trig1 + chap.rPreTrig[row.setname])
                    if chap.rPostTrig[row.setname]:
                        row.trig2 = list(row.trig2 + chap.rPostTrig[row.setname])
                
                if "#" in row.tag:
                    set = chap.pairableRC[row.tag]
                    if type(set) is list:
                        row.next = set
                    else: 
                        row.next = [ set ]
                elif row.tag == "Next":
                    # Search for the next line in pairableR that is non-next
                    for r in chap.pairableR[row.setname]:
                        if chap.rowSet[r].tag != "Next":
                            row.next = [r]
                    if not row.next:
                        logging.debug("Could not find a shared message row for given [[Next]] response")
                        raise ValueError("Could not find a shared message row for given [[Next]] response")
                elif row.tag == "End":
                    row.next = [ chap.rowSet[-1].rowID ]
                else:
                    # If unrecognized tag, link it to the next line
                    logging.debug("Found a response line without a recognized tag. Assigning this line's nextID to the line immediately below")
                    logging.debug(row.rowID)
                    if row.rowID != chap.rowSet[-1].rowID:
                        row.next = [ row.rowID+1 ]
                    else:
                        row.next = [  ]
            elif row.rowtype == "INITIALIZED" or row.rowtype == "ENDING":
                pass
            else:
                logging.debug("Unable to identify rowtype of this message row")
                raise ValueError("Unable to identify rowtype of this message row")
            
            logging.debug("\n>Writing row: " + str(row))
            # Add row data to table
            chap.writer.writerow( {
                'Line ID' : chap.ID * 100 + row.rowID+1, 
                'Story' : chap.story, 
                'Section' : row.section, 
                'Character' : row.chara, 
                'Line' : replace_emotes(emotes,row.line), 
                'Option Text' : replace_emotes(emotes,row.optxt), 
                'Condition' : "\n".join(row.cond), 
                'Triggers Before Line' : "\n".join(row.trig1), 
                'Triggers After Line' : "\n".join(row.trig2), 
                'NextID1' : "" if len(row.next) < 1 else row.next[0]+1+chap.ID*100,
                'NextID2' : "" if len(row.next) < 2 else row.next[1]+1+chap.ID*100,
                'NextID3' : "" if len(row.next) < 3 else row.next[2]+1+chap.ID*100,
                'NextID4' : "" if len(row.next) < 4 else row.next[3]+1+chap.ID*100,
                'Score Modification' : row.score
                } )
    
    print('\n>Creating default variable CSV...')
    logging.debug('\n>Creating default variable CSV...')
    
    with open(title.replace(" ","_") + "_default_variables.csv", 'w+b') as vfile:
        var_writer = csv.DictWriter(vfile, delimiter=delimiter, fieldnames=['Variable Name', 'Default Values'], quotechar='"', quoting=csv.QUOTE_MINIMAL)
        var_writer.writeheader()
        
        for v in variable_names:
            var_writer.writerow( {
                'Variable Name' : v, 
                'Default Values' : "" if not default_values[v] else default_values[v]
                } )
    
    raw_input('\n>Program complete.  Press ENTER to exit.\n')
    
if __name__ == "__main__": main()