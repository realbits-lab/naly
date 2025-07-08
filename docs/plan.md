# PowerPoint Template Collection and Generation Plan

## Phase 1: Collect and Index PowerPoint Templates

1. **Collect PowerPoint Files**
   - Download or gather a set of PowerPoint (.pptx) files from the web or other sources.

2. **Extract Slides**
   - For each PowerPoint file, extract each slide as a separate entity.

3. **Describe Slides**
   - Generate a textual description for each slide, summarizing its content and intent.

4. **Store in Vector Database**
   - Save each slide’s description and its corresponding PowerPoint XML data in a vector database.
   - Use the description as the embedding/query key, and store the XML as the value.

---

## Phase 2: Generate New PowerPoint Files

1. **Receive User Prompt**
   - Accept a prompt from the user describing the desired presentation.

2. **Generate Slide Content List**
   - Based on the user prompt, generate a list of intended slide contents (one per slide).

3. **For Each Slide Content:**
   - a. **Search for Similar Slides**
      - Query the vector database using the generated slide content to find the most similar existing slide template.
   - b. **Prepare Generation Input**
      - Combine the user’s prompt and the retrieved slide’s XML data as input for generation.
   - c. **Generate Slide**
      - Use the combined input to generate a new slide (in PowerPoint XML format).

4. **Assemble PowerPoint File**
   - Combine all generated slides into a single PowerPoint (.pptx) file.
