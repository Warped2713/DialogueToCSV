parse_script.exe
parse_script.py
__________________________________
Input Requirements:

1. "script_formatted.txt" which is a script written in the correct format (see Script_Format_Guide.txt), and if the program cannot find this file, you must enter the name of your file in the console window.

2. "emoticon_dict.txt" which contains a list of emoticons and their replacement symbols, separated by a space. If this file cannot be found, you must enter the name of your own file in the console window.

__________________________________
Output:

1. CSV files of the form "Title_Section.csv" encoded as UTF-8 without BOM. Note these may look funny in Excel, but are encoded correctly for use with Construct 2 SpriteFonts. You can also import these into Google Spreadsheets with your custom delimiter (if not a comma).

2. "script_cleaned.txt" which is a version of the input script file without empty lines, and with corrected UTF-8 encoding symbols, and replaced emoticon symbols

3. "parse_script_errorlog.txt" which is a log of any chronological debugging messages created while running parse_script.exe

4. A CSV file of any default variables mentioned at the top of the script.


___________________________________
Also included:

Sample script from Sphere 9's A Casual Chat https://www.sphere-9.com/product/a-casual-chat/

Run the parse_script.exe to test it on "script_formatted.txt" (which includes all of Chapter 1 of A Casual Chat if you haven't changed it yet).
