README: Editing Fonts

1.  Create a SpriteSheet for your Font
Use the SpriteFontTemplate.AI Adobe Illustrator file to create your sprite sheet.  Default setup has sprite frames of 64x64 pixels with fontsize 60, using the following character set:
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,;:¿?¡!@#$€£%^<>&*()[]{}-_+=/¢|¤~“”"‘’'`´¸¨ºª©°¶¦§‡†…

Each layer contains a different font (except the first two layers that serve as emoticon replacements for ¶¦§‡†). These layers contain text objects that have been converted to paths and offset by 1px from the left.

To use a new font, make visible to bottom two locked layers and copy the locked layer "Regular" into a new layer.  Select the new layer and change the font to what you want.  Then do Type > Create Outlines to convert the text objects to paths. 

2. Export your "SpriteSheet.PNG" and a "CharacterWidths.txt" from Illustrator
Export the spritesheet by doing File > Save for Web and resize it as you see fit.
Export a text file containing the individual character widths by doing File > Scripts > Other Scripts... and selecting "ExportObjectInfoToText.jsx" from this directory.

3. Convert "CharacterWidths.txt" to "JSON.txt" and add to the Construct 2 CAPX or Project
To get the JSON strings you need, edit the "SpriteFont_Input.txt" according to the "py_template.txt".  Then run the Python script "gen_spritefont_json.py" to get your JSON strings in the "SpriteFont_Output_JSON.txt".  Copypaste the individual JSON strings into the appropriate part of the "Format Spritefonts" event sheet (in Construct 2).

4. Update the SpriteFont objects with "SpriteSheet.PNG"
To update the spritesheets for your fonts, go to the FontTest layout in Construct 2.  Double click on the appropriate Font_XXX object in the Objects panel.  In the animation editor, open the image file you exported from Adobe Illustrator.