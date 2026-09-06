# Adobe ExtendScript (JSX) Quick Reference for Illustrator & Photoshop

## Adobe Illustrator DOM

### Document Initialization:
```javascript
#target illustrator

var docPreset = new DocumentPreset();
docPreset.colorMode = DocumentColorMode.CMYK; // For print prepress
var doc = app.documents.addDocument(DocumentPresetType.Print, docPreset);
```

### Artboard Manipulation:
```javascript
// Adding artboards: rect = [left, top, right, bottom]
var ab = doc.artboards.add([1300, 0, 2100, -800]);
ab.name = "02_Stacked_Vertical";
```

### Spot Color Swatches:
```javascript
var spot = doc.spots.add();
spot.name = "Brand/Primary";
var cmyk = new CMYKColor();
cmyk.cyan = 75; cmyk.magenta = 68; cmyk.yellow = 0; cmyk.black = 0;
spot.color = cmyk;
spot.colorType = ColorModel.SPOT;
```

---

## Adobe Photoshop DOM

### Replacing Smart Object Content:
```javascript
#target photoshop

var targetLayer = doc.layers.getByName("REPLACE_LOGO");
doc.activeLayer = targetLayer;

// Edit contents
executeAction(stringIDToTypeID("placedLayerEditContents"), new ActionDescriptor(), DialogModes.NO);
var smartDoc = app.activeDocument;

// Place replacement file
var placedDesc = new ActionDescriptor();
placedDesc.putPath(stringIDToTypeID("null"), new File("/path/to/mark.png"));
executeAction(stringIDToTypeID("placeEvent"), placedDesc, DialogModes.NO);

smartDoc.save();
smartDoc.close(SaveOptions.DONOTSAVECHANGES);
```

### Exporting Save-For-Web PNG:
```javascript
var exportOpts = new ExportOptionsSaveForWeb();
exportOpts.format = SaveDocumentType.PNG;
exportOpts.PNG8 = false;
exportOpts.quality = 100;
doc.exportDocument(new File("/path/to/render.png"), ExportType.SAVEFORWEB, exportOpts);
```
