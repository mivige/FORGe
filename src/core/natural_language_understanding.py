"""
Real-time Natural Language Understanding for insurance call handling.

This module processes speech transcriptions in real-time, performing:
1. Sentiment analysis (panic/injury detection, frustration scoring)
2. Claim report extraction following text_to_ticket schema
3. Conversational response generation
4. All in a single OpenAI API call for efficiency
"""

import json
from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import Dict, Any, List
from enum import Enum
import requests
from requests.exceptions import RequestException
import re

load_dotenv()


class ConversationState(Enum):
    """Track the current stage of the conversation."""
    GREETING = "greeting"
    GATHERING_POLICY_INFO = "gathering_policy_info"
    GATHERING_INCIDENT_DETAILS = "gathering_incident_details"
    GATHERING_DAMAGE_INFO = "gathering_damage_info"
    CONFIRMING = "confirming"
    TO_REVIEW = "to_review"
    COMPLETE = "complete"
    EMERGENCY_TRANSFER = "emergency_transfer"


class ConversationalNLU:
    """
    Real-time NLU processing for insurance call handling.
    Receives transcribed text, maintains context, analyzes sentiment,
    extracts claim data, and generates appropriate responses.
    """
    
    def __init__(self):
        """Initialize the NLU with OpenAI client and conversation state."""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.conversation_history: List[str] = []  # Context window
        self.state = ConversationState.GREETING
        self.claim_data = {
            "policyId": None,
            "customerName": None,
            "incidentType": None,
            "description": None,
            "location": None,
            "estimatedDamage": None,
            "incidentDate": None
        }
        self.frustration_score = 0.0
        self.base_system_prompt = self._build_base_system_prompt()  # Build once at start
        
    def process_input(self, user_text: str) -> Dict[str, Any]:
        """
        Process user input in real-time using a single OpenAI API call.
        
        Args:
            user_text: Transcribed text from speech_to_text.py
            
        Returns:
            Dictionary containing:
                - response: Text to send to text_to_speech.py
                - should_transfer: Boolean for emergency transfer
                - transfer_reason: Reason for transfer (panic/injury)
                - frustration_score: Float 0-10 indicating anger/frustration
                - claim_data: Updated claim report following text_to_ticket schema
                - state: Current conversation state
                - is_complete: Boolean indicating if claim is ready
        """
        # Add user input to context window
        self.conversation_history.append(f"CALLER: {user_text}")
        # canonical is_complete flag for returns (keeps pipeline checks consistent)
        is_complete = False
        
        # --- existing local TO_REVIEW handling and other logic happen below ---
        # Local handling for the "to_review" confirmation flow (robust detection)
        if self.state == ConversationState.TO_REVIEW:
            lc = user_text.lower().strip()

            def is_affirmative(s: str) -> bool:
                return bool(re.search(r'\b(yes|yep|yeah|y|correct|confirm|that\'s correct|all set|looks good|right|thanks|thank you|bye|goodbye)\b', s))

            def is_negative(s: str) -> bool:
                return bool(re.search(r'\b(no|not|change|incorrect|wrong|edit|update|needs|nope)\b', s))

            if is_affirmative(lc):
                self.state = ConversationState.COMPLETE
                is_complete = True
                self.confirm_attempts = 0
                self.conversation_history.append("ASSISTANT: Claim confirmed by caller.")
                return {
                    "response": "Thank you! Your claim has been created successfully. Now you have to speak to a human operator to finish the report. I can either put you in line to speak with an agent now, the estimated waiting time is 5 minutes, or you can ask to be called back later. Which would you prefer?",
                    "should_transfer": False,
                    "transfer_reason": "",
                    "frustration_score": self.frustration_score,
                    "claim_data": self.claim_data,
                    "state": self.state.value,
                    "is_complete": True
                }

            # Negative / change requests -> go back to collecting details
            if is_negative(lc):
                self.state = ConversationState.GATHERING_INCIDENT_DETAILS
                self.conversation_history.append("ASSISTANT: Caller requested changes; returning to information collection.")
                return {
                    "response": "I understand you'd like to make changes. Which detail would you like to update?",
                    "should_transfer": False,
                    "transfer_reason": "",
                    "frustration_score": self.frustration_score,
                    "claim_data": self.claim_data,
                    "state": self.state.value,
                    "is_complete": False
                }

            # Unclear -> ask for a clear yes/no or specify change
            return {
                "response": "Could you please confirm: is the information I summarized correct? Say 'yes' to confirm or tell me what to change.",
                "should_transfer": False,
                "transfer_reason": "",
                "frustration_score": self.frustration_score,
                "claim_data": self.claim_data,
                "state": self.state.value,
                "is_complete": False
            }
        # end TO_REVIEW handling
         
        # Build dynamic context (only what changes)
        dynamic_context = f"""
 CURRENT STATE: {self.state.value}
 CURRENT CLAIM DATA: {json.dumps(self.claim_data, indent=2)}

 CONVERSATION:
{chr(10).join(self.conversation_history[-6:])}
"""
        
        # Single API call with structured output request
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.base_system_prompt},
                    {"role": "user", "content": dynamic_context}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Extract all information from single response
            assistant_response = result.get("response", "I'm sorry, could you repeat that?")
            emergency_detected = result.get("emergency_detected", False)
            emergency_reason = result.get("emergency_reason", "")
            self.frustration_score = float(result.get("frustration_score", 0.0))
            
            # Update claim data with any newly extracted information
            extracted_claim = result.get("claim_data", {})
            for key, value in extracted_claim.items():
                if value and value != "null" and key in self.claim_data:
                    # Prepend frustration score to description
                    if key == "description" and value:
                        value = f"[Frustration Score: {self.frustration_score}/10] {value}"
                    self.claim_data[key] = value
            
            # Update conversation state
            self.state = ConversationState[result.get("conversation_state", "GATHERING_POLICY_INFO")]
            
            # Add assistant response to context window
            self.conversation_history.append(f"ASSISTANT: {assistant_response}")
            
            # Check if emergency transfer needed
            if emergency_detected:
                self.state = ConversationState.EMERGENCY_TRANSFER
                return {
                    "response": "I understand this is urgent. I'm connecting you with the emergency team who can better assist you. Please hold in line!",
                    "should_transfer": True,
                    "transfer_reason": emergency_reason,
                    "frustration_score": self.frustration_score,
                    "claim_data": self.claim_data,
                    "state": self.state.value,
                    "is_complete": False
                }
            
            # Check if frustration score is too high
            if self.frustration_score > 5.0:
                self.state = ConversationState.EMERGENCY_TRANSFER
                return {
                    "response": "I can understand that there is a bit of frustration. Let me connect you with a specialist who can better help you right away. Please hold.",
                    "should_transfer": True,
                    "transfer_reason": f"high_frustration_{self.frustration_score}",
                    "frustration_score": self.frustration_score,
                    "claim_data": self.claim_data,
                    "state": self.state.value,
                    "is_complete": False
                }
            
            # Check if claim is complete -> switch to TO_REVIEW and ask caller to confirm summary
            is_complete = self._check_claim_completion()
            if is_complete and self.state not in (ConversationState.TO_REVIEW, ConversationState.COMPLETE):
                # Move to TO_REVIEW and ask the caller to verify the extracted claim
                self.state = ConversationState.TO_REVIEW
                
                # Create a brief natural summary instead of dumping JSON
                summary_parts = []
                if self.claim_data.get("policyId"):
                    summary_parts.append(f"policy number {self.claim_data['policyId']}")
                if self.claim_data.get("customerName"):
                    summary_parts.append(f"under the name {self.claim_data['customerName']}")
                if self.claim_data.get("incidentType"):
                    summary_parts.append(f"for a {self.claim_data['incidentType']}")
                if self.claim_data.get("location"):
                    summary_parts.append(f"at {self.claim_data['location']}")
                if self.claim_data.get("incidentDate"):
                    summary_parts.append(f"on {self.claim_data['incidentDate']}")
                
                summary = ", ".join(summary_parts)
                confirm_text = f"Let me confirm: I have {summary}. Is this correct?"
                
                # Add assistant confirmation prompt to history
                self.conversation_history.append(f"ASSISTANT: {confirm_text}")
                return {
                    "response": confirm_text,
                    "should_transfer": False,
                    "transfer_reason": "",
                    "frustration_score": self.frustration_score,
                    "claim_data": self.claim_data,
                    "state": self.state.value,
                    "is_complete": False
                }

            # final normalized return — ensure is_complete reflects the ConversationState
            final_is_complete = bool(is_complete or (self.state == ConversationState.COMPLETE))
            
            return {
                 "response": assistant_response,
                 "should_transfer": False,
                 "transfer_reason": "",
                 "frustration_score": self.frustration_score,
                 "claim_data": self.claim_data,
                 "state": self.state.value,
                 "is_complete": final_is_complete
             }
            
        except Exception as e:
            print(f"[NLU Error] {e}")
            return {
                "response": "I apologize, I'm having technical difficulties. Let me connect you with an agent.",
                "should_transfer": True,
                "transfer_reason": "technical_error",
                "frustration_score": self.frustration_score,
                "claim_data": self.claim_data,
                "state": self.state.value,
                "is_complete": False
            }
    
    def _build_base_system_prompt(self) -> str:
        """
        Build base system prompt once at initialization.
        Dynamic context (state, claim data, conversation) is passed separately.
        
        Returns:
            Base system prompt string with all instructions
        """
        return """You are an AI assistant for an insurance company call center. Process the conversation and return a JSON response.

YOUR TASKS (in priority order):

1. EMERGENCY DETECTION (highest priority):
   - Detect ANY mention of: injuries, bleeding, pain, emergency, ambulance, hospital, hurt, unconscious
   - Detect panic indicators: help, scared, dying, can't breathe
   - If detected, set "emergency_detected": true and "emergency_reason": "<reason>"

2. SENTIMENT ANALYSIS:
   - Score frustration/anger from 0-10 based on:
     * Tone indicators: angry, frustrated, upset, ridiculous, unacceptable
     * Repeated questions or complaints
     * Escalation language
   - Return as "frustration_score": <float>

3. CLAIM DATA EXTRACTION (follow this schema exactly):
   {{
       "policyId": "string or null",
       "customerName": "string or null",
       "incidentType": "string or null",
       "description": "string or null (detailed description of incident)",
       "location": "string or null",
       "estimatedDamage": "float or null (in USD)",
       "incidentDate": "YYYY-MM-DD or null"
   }}
   - Extract ANY new information from current input
   - Keep existing data, only update with new information
   - Return as "claim_data": {{...}}

4. CONVERSATION STATE MANAGEMENT:
   Progress through these states:
   - GREETING → GATHERING_POLICY_INFO → GATHERING_INCIDENT_DETAILS → GATHERING_DAMAGE_INFO → CONFIRMING → COMPLETE
   - Return as "conversation_state": "<STATE>"
   
5. RESPONSE GENERATION:
   - Generate natural, empathetic response (under 30 words)
   - Guide conversation based on current state and missing data
   - If state is GATHERING_POLICY_INFO: ask for policy number and name
   - If state is GATHERING_INCIDENT_DETAILS: ask about what happened, where, when
   - If state is GATHERING_DAMAGE_INFO: ask about damage extent and costs
   - If state is CONFIRMING: summarize and confirm details
   - Keep tone professional but warm
   - Return as "response": "<text>"

REQUIRED JSON OUTPUT FORMAT:
{{
    "emergency_detected": <boolean>,
    "emergency_reason": "<string or empty>",
    "frustration_score": <float 0-10>,
    "claim_data": {{
        "policyId": <string or null>,
        "customerName": <string or null>,
        "incidentType": <string or null>,
        "description": <string or null>,
        "location": <string or null>,
        "estimatedDamage": <float or null>,
        "incidentDate": <string or null>
    }},
    "conversation_state": "<STATE_NAME>",
    "response": "<your natural language response>"
}}

Remember: Return ONLY valid JSON. Be empathetic and guide the conversation naturally."""
    
    def _check_claim_completion(self) -> bool:
        """
        Check if all required claim fields are collected.
        
        Returns:
            Boolean indicating if claim is complete and ready for submission
        """
        required_fields = ["policyId", "customerName", "incidentType", "description", "location"]
        return all(
            self.claim_data.get(field) and self.claim_data.get(field) != "null"
            for field in required_fields
        )
    
    def get_greeting(self) -> str:
        """
        Get initial greeting message.
        
        Returns:
            Greeting text for text_to_speech.py
        """
        greeting = "Hello! Thank you for calling InsurTech. How may I assist you today?"
        self.conversation_history.append(f"ASSISTANT: {greeting}")
        return greeting
    
    def reset(self):
        """Reset conversation for new call."""
        self.conversation_history = []
        self.state = ConversationState.GREETING
        self.claim_data = {
            "policyId": None,
            "customerName": None,
            "incidentType": None,
            "description": None,
            "location": None,
            "estimatedDamage": None,
            "incidentDate": None
        }
        self.frustration_score = 0.0