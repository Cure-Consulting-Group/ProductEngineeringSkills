/**
 * update_mockup.jsx
 * Adobe Photoshop ExtendScript template.
 *
 * Automates:
 * 1. Opening a master mockup PSD template.
 * 2. Locating designated Smart Object layers (e.g. "REPLACE_LOGO").
 * 3. Editing Smart Object contents with the new brand vector/mark.
 * 4. Saving high-resolution rendered presentation mockups.
 */

#target photoshop

function replaceSmartObject(psdTemplatePath, newLogoImagePath, outputRenderPath) {
    if (!app.documents) {
        alert("Photoshop document engine unavailable.");
        return;
    }

    // 1. Open the PSD Mockup Template
    var mockupFile = new File(psdTemplatePath);
    if (!mockupFile.exists) {
        alert("Mockup file not found: " + psdTemplatePath);
        return;
    }

    var doc = app.open(mockupFile);

    // 2. Recursive search for Smart Object layer
    function findSmartObjectLayer(parent) {
        for (var i = 0; i < parent.layers.length; i++) {
            var layer = parent.layers[i];
            if (layer.typename === "LayerSet") {
                var found = findSmartObjectLayer(layer);
                if (found) return found;
            } else if (layer.kind === LayerKind.SMARTOBJECT) {
                // If layer is named REPLACE or SMART_OBJECT
                if (layer.name.toUpperCase().indexOf("REPLACE") !== -1 || layer.name.toUpperCase().indexOf("LOGO") !== -1) {
                    return layer;
                }
            }
        }
        return null;
    }

    var targetLayer = findSmartObjectLayer(doc);
    if (targetLayer) {
        doc.activeLayer = targetLayer;
        // A linked Smart Object saves back into its source file on disk; only embedded ones are safe to replace.
        try {
            if (targetLayer.smartObject && targetLayer.smartObject.linked) {
                throw new Error("Smart Object '" + targetLayer.name + "' is linked; embed it (Layer > Smart Objects > Embed Linked) before running this script.");
            }
        } catch (guardErr) {
            if (String(guardErr.message).indexOf("is linked") !== -1) { throw guardErr; }
        }
        
        // Open the smart object for editing
        executeAction(stringIDToTypeID("placedLayerEditContents"), new ActionDescriptor(), DialogModes.NO);
        var smartDoc = app.activeDocument;

        // Place new artwork
        var placedDesc = new ActionDescriptor();
        placedDesc.putPath(stringIDToTypeID("null"), new File(newLogoImagePath));
        executeAction(stringIDToTypeID("placeEvent"), placedDesc, DialogModes.NO);

        // Save and close Smart Object
        smartDoc.save();
        smartDoc.close(SaveOptions.DONOTSAVECHANGES);
    }

    // 3. Export Rendered Mockup to PNG
    var exportOpts = new ExportOptionsSaveForWeb();
    exportOpts.format = SaveDocumentType.PNG;
    exportOpts.PNG8 = false;
    exportOpts.quality = 100;

    var outFile = new File(outputRenderPath);
    doc.exportDocument(outFile, ExportType.SAVEFORWEB, exportOpts);

    // Close template without overwriting original PSD
    doc.close(SaveOptions.DONOTSAVECHANGES);

    return outFile.fsName;
}
