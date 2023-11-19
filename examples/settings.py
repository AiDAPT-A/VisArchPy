# format of settings for the pipelineS


layout_settings = {
        "caption": {
            "offset": [4, "mm"],
            "direction": "down",
            "keywords": ['figure', 'caption', 'figuur']
            },
        "image": {
            "width": 120,
            "height": 120,
        }
    }

# OCR ANALYSIS SETTINGS
ocr_settings = {
        "caption": {
            "offset": [50, "px"],
            "direction": "down",
            "keywords": ['figure', 'caption', 'figuur']
            },
        "image": {
            "width": 120,
            "height": 120,
        },
        "resolution": 250,  # dpi, default for ocr analysis,
        "resize": 30000,  # px, if image is larger than this, it will be
        # resized before performing OCR,
        # this affect the quality of output images
    }