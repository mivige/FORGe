### Workflow

1. Call Begins
Incoming call is received.
2. Callbot Introduction and Option
Callbot initiates script with an introduction.
Caller is given option to either:
Be transferred immediately to a person.
Stay on the line to continue the scripted interaction.
3. Speech to Text (STT) Transcribes Response
Caller's response is transcribed for decision:
If caller requests transfer, they are put in general queue on hold. End of process.
If caller speech indicates panic or stress, caller is informed of immediate transfer to emergency line, then transferred. End of process.
If caller confirms continuation, script proceeds.
4. Script Continues via Text to Speech (TTS)
Caller is asked about their request verbally.
Caller's spoken response is transcribed.
5. Summarize Request
An LLM summarizes transcribed request into a JSON file capturing essential information.
6. Move to Personal Information Collection
Script collects personal info from caller.
Responses transcribed and appended.
7. Read Back Summary and Department for Confirmation
Summarized info and determined department are read back to caller using TTS for confirmation.
8. Parallel Sentiment Monitoring
Second LLM continuously analyzes caller responses for sentiment/frustration level:
If frustration is low: continue script as usual.
If frustration is medium: skip re-verification of personal info, JSON ticket tagged with label "frustrated".
If frustration is high: assure caller of imminent transfer to next available agent, JSON ticket tagged with label "angry".
9. Ticket Submission and Call Transfer Logic
JSON ticket (with or without frustration label) sent by email or internal system to relevant department.
Check if a free agent is available:
If yes, transfer call to agent immediately.
If no, offer caller option to receive a version of the ticket without label and be called back later." "Stage 1: Request Capture
Caller’s spoken request is transcribed.
LLM 1 summarizes the request into a JSON file immediately at this point if frustration is detected (if high then the caller is assured that an agent from the required department is being located and a transfer is imminent; JSON file is created with summary of information so far and labelled angry and sent to the necessary department).
LLM 2 simultaneously monitors caller sentiment for frustration throughout all stages.
Stage 2: Personal Info Capture
If caller frustration remains low, the script proceeds to collect personal information.
If frustration is medium then the caller is assured that an agent from the required department is being located and a transfer is imminent; JSON file is created with summary of information so far and labelled angry and sent to the necessary department
Stage 3: Readback for Confirmation
The summarized request and department are read back to the caller for confirmation or correction (via TTS).
If corrections are necessary repeat step 3
if all information is correct send JSON file and attempt to connect to department
Stage 5: agent not found
-          if agent not found script continues with caller being informed that a ticket has been submitted and they can choose to stay on the line and wait or be called back"

Here is a detailed, internally consistent merged workflow for a callbot system, integrating both provided approaches with clear stage definitions and unified logic for handling caller requests, sentiment analysis, ticket creation, and agent transfer.

***

## Detailed Merged Callbot Workflow

### 1. Call Initiation and Introduction

- An incoming call is received by the callbot system.
- The callbot initiates with a scripted introduction and presents options:
    - Transfer immediately to a live agent.
    - Continue with the scripted process.


### 2. Immediate Decision Handling

- Speech-to-text (STT) transcribes the caller’s response for analysis.
    - If the caller requests a transfer:
        - Place in general queue/on hold; process ends here.
    - If speech indicates panic or urgent stress:
        - Caller is assured of immediate transfer to emergency line, then transferred.
    - If caller opts to continue:
        - Proceed to main scripted interaction.


### 3. Request Capture and Sentiment Monitoring (Parallel)

- Callbot verbally asks for caller’s request (using text-to-speech, TTS).
- STT transcribes caller’s spoken request.
- Two large language models (LLMs) operate in parallel:
    - **LLM 1:** Immediately summarizes the transcribed request into a JSON file, capturing essential info.
        - If high frustration is detected at this stage:
            - Caller is assured an agent is being located, transfer is imminent.
            - JSON file is labelled "angry" and sent to necessary department.
            - Attempt direct agent transfer, process ends here.
    - **LLM 2:** Continuously monitors caller sentiment throughout all scripted stages.


### 4. Personal Information Collection (Conditional by Sentiment)

- If caller frustration is **low**:
    - Script proceeds to collect personal information (name, contact, etc.).
    - Responses transcribed and appended to existing JSON file.
- If frustration rises to **medium** during this or a previous stage:
    - Caller is assured an agent from the needed department is being located.
    - Creates and sends a JSON ticket labelled "frustrated" to the department.
    - Skips redundant verification steps; attempts transfer.
- If frustration escalates to **high** at any point:
    - Caller is assured of imminent transfer.
    - JSON ticket is labelled "angry" and sent.
    - Immediate attempt to transfer to the next available agent.


### 5. Readback and Department Confirmation

- Summarized JSON file (request + personal info + department) is read back for caller confirmation (TTS).
    - If corrections are needed:
        - Repeat readback and info collection cycles.
    - If all details confirmed:
        - JSON file sent by email or internal system to relevant department.


### 6. Call Transfer and Ticket Submission Logic

- On confirmation or sentiment-triggered fast-track, check agent availability:
    - If a free agent is found:
        - Transfer caller immediately.
    - If no agent is found:
        - Inform caller a ticket has been submitted to the department:
            - Caller is offered choice to:
                - Stay on the line and wait for the next available agent.
                - Be called back later; caller receives a copy of the ticket (without frustration label unless appropriate).

***

### Workflow Logic Table

| Stage | Actions | Sentiment Handling |
| :-- | :-- | :-- |
| Call Initiation | Introduction \& option: transfer or continue scripted interaction | Immediate transfer if stress detected |
| Request + Sentiment | Capture request via STT \& TTS; LLM summarizes to JSON | Parallel LLM monitoring; high/medium frustration triggers labelled ticket \& agent transfer |
| Personal Info Collection | Collect personal info if frustration is low | Medium frustration triggers transfer and skips re-verification |
| Readback Confirmation | Read back summary and department via TTS | Repeat if info needs correction |
| Agent Transfer/Ticket | Send JSON ticket to department; attempt agent transfer | If no agent, offer wait or callback; ticket sent |


***



