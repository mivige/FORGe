# Text to tiket
### Input: text file(or multiple ones to concat)
### Output: JSON file

---

### General idea of workflow
raw text (from speech) 
   ↓
cleaning / normalization (optional)
   ↓
structured field extraction (your defined fields)
   ↓
validation + enrichment (sentiment/rage detection)
   ↓
ticket object or JSON
   ↓
store / display / send to API

### Step 1: define fields for ticket (discuss together)
What info do we actually need for our system to assign the caller to the carrect human agent?
What questions are we asking to get the info?

### Step 2: Prompt Engineering for Extraction
This part would be really hard to implement ourself, we can probably use structured prompt with gpt-4o-mini(or similar) to exctract the fields

### Step 3: Validation & Post-Processing
This were we actually code ourself, make sure info in the ticket is consistent with what we expect(right stucture, and basic checks) and were we add the rage detector

### Step 4: Save the ticket
Create the JSON file our classification model will take in input
Es:     {
        "name": "John",
        "issue": "Printer keeps jamming",
        "location": "Third floor",
        "priority": "medium",
        "summary": "Printer malfunction on third floor"
        }