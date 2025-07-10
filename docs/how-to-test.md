Improve @examples/extract/ppt_extractor.py and @examples/extract/ppt_generator.py to match slide1.xml of input and output powerpoint open xml file for
  the first slide.

1. Run "python ppt_extractor.py sample1-2.pptx" in examples/extract directory.
2. Run "python ppt_generator.py \
sample1-2_shapes.json \
sample1-2_layouts.json \
sample1-2_theme.json \
--media-file sample1-2_media.json \
--properties-file sample1-2_properties.json \
--output sample1-2_enhanced.pptx"
3. Unzip @examples/extract/sample1-2.pptx and @examples/extract/sample1-2_enhanced.pptx to the implicit directory.
4. Compare the slide1.xml file inside each output directory in ppt/slides directory.
5. Find the different part and analyze why this different parts exist.
6. Modify ppt_extractor.py and ppt_generator.py for recover these differences.
7. Iterate this process until there's no different part.
8. You should use python-pptx library to extract and generate the powerpoint open xml file.
9. If needed, read @docs/python-pptx-reference.md to understand the python-pptx library.