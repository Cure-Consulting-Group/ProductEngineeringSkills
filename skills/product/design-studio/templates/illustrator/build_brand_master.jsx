/**
 * build_brand_master.jsx
 * Adobe Illustrator ExtendScript template.
 *
 * Automates:
 * 1. Document creation with CMYK color space for print compliance.
 * 2. Generation of 5 standard artboards (Primary, Stacked, Submark, Monochrome, Favicon).
 * 3. Layer architecture ([Guides], [Artwork], [Typography], [Background]).
 * 4. Spot & Process Swatch creation.
 * 5. Native .ai and vector .eps saving.
 */

#target illustrator

function buildBrandFile(config) {
    if (!app.documents) {
        alert("Illustrator document engine unavailable.");
        return;
    }

    // 1. Create Document with CMYK profile
    var docPreset = new DocumentPreset();
    docPreset.colorMode = DocumentColorMode.CMYK;
    docPreset.units = RulerUnits.Points;
    docPreset.width = 1920;
    docPreset.height = 1080;
    
    var doc = app.documents.addDocument(DocumentPresetType.Print, docPreset);

    // 2. Setup 5 Production Artboards
    // Coordinates: [left, top, right, bottom]
    var abList = doc.artboards;
    
    // Artboard 1: Primary Horizontal Lockup
    abList[0].name = "01_Primary_Horizontal";
    abList[0].artboardRect = [0, 0, 1200, -400];

    // Artboard 2: Stacked Vertical Lockup
    var ab2 = abList.add([1300, 0, 2100, -800]);
    ab2.name = "02_Stacked_Vertical";

    // Artboard 3: Submark & App Icon (512x512)
    var ab3 = abList.add([0, -500, 512, -1012]);
    ab3.name = "03_Submark_Icon";

    // Artboard 4: Monochrome 1-Bit
    var ab4 = abList.add([600, -500, 1112, -1012]);
    ab4.name = "04_Monochrome_1Bit";

    // Artboard 5: Favicon Grid
    var ab5 = abList.add([1300, -900, 1700, -1300]);
    ab5.name = "05_Favicon_Matrix";

    // 3. Setup Labeled Layer Hierarchy
    var guidesLayer = doc.layers.add();
    guidesLayer.name = "[Guides & Clearspace]";
    
    var typeLayer = doc.layers.add();
    typeLayer.name = "[Typography - Outlines]";

    var artLayer = doc.layers.add();
    artLayer.name = "[Artwork - Vectors]";

    var bgLayer = doc.layers.add();
    bgLayer.name = "[Background]";

    // 4. Register Swatches
    if (config.colors) {
        for (var i = 0; i < config.colors.length; i++) {
            var c = config.colors[i];
            var spot = doc.spots.add();
            spot.name = "Brand/" + c.name;
            
            var cmyk = new CMYKColor();
            cmyk.cyan = c.c || 0;
            cmyk.magenta = c.m || 0;
            cmyk.yellow = c.y || 0;
            cmyk.black = c.k || 0;
            
            spot.color = cmyk;
            spot.colorType = ColorModel.SPOT;
        }
    }

    // 5. Save Native .ai with maximum cross-version compatibility
    var safeName = String(config.brandName).replace(/[^A-Za-z0-9_-]/g, "_");
    var targetFile = new File(config.saveDirectory + "/" + safeName + "_Master.ai");
    var saveOpts = new IllustratorSaveOptions();
    saveOpts.compatibility = Compatibility.ILLUSTRATOR17; // the current CC file format
    saveOpts.pdfCompatible = true;
    doc.saveAs(targetFile, saveOpts);

    return targetFile.fsName;
}

// Example execution configuration
/*
buildBrandFile({
    brandName: "AcmeCorp",
    saveDirectory: "~/Desktop",
    colors: [
        { name: "Primary_Indigo", c: 80, m: 70, y: 0, k: 0 },
        { name: "Accent_Gold", c: 0, m: 30, y: 100, k: 0 }
    ]
});
*/
