/* *************************************************************************
    An Illustrator Script
    Exports a list of object widths for each object, grouped by layer    
    For example:
        "
        Layer Name
        30.0
        156.43
        234.05
        "
************************************************************************** */  

// Get the destination folder to save the text file in
var destFolder = Folder.selectDialog('Select a folder to export the text file to:');

if (destFolder) {

    // Access text file for (over)writing
    var doc = app.activeDocument;
    var textFile = File(destFolder + '/' + doc.name.split(".")[0] + '_info.txt');
    
    // Collect data from current Illustrator document
    var textInfo = "";
    for( var x = 0; x < doc.layers.length; x++ ) {
        
        if(doc.layers[x].visible) {
            textInfo += "Layer: " + doc.layers[x].name + "\n";
            
            for( var y = doc.layers[x].groupItems.length - 1; y >= 0; y-- ) {
                if(!doc.layers[x].groupItems[y].hidden) {
                    bounds = doc.layers[x].groupItems[y].visibleBounds;
                    textInfo += (bounds[2] - bounds[0]) + " ";
                }
            }
            
            textInfo += "\n";
        }
    }
    
    // Open the text file, write to it, and close it
    textFile.open('e');
    textFile.write(textInfo);
    textFile.close();
}