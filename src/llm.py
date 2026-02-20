import aiohttp
import asyncio
import os
import uuid
import time
import re
from google import genai
from google.auth.transport.requests import Request
from src.auth import AuthManager
from src.config.settings import GEMINI_MODEL, GEMINI_API_KEY
from src.skills.registry import SkillRegistry
import src.skills  # noqa: F401 # Import the package to trigger __init__.py and load all skills

class CodeAssistTransport:
    """A custom transport to hit the Google Code Assist (GCA) 'free' endpoint."""
    
    BASE_URL = "https://cloudcode-pa.googleapis.com/v1internal"

    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        self.session_id = str(uuid.uuid4())
        self.cli_version = "0.30.0-nightly.20260210.a2174751d"

    async def _onboard(self, token):
        """Discover the cloudaicompanionProject ID used by this account."""
        url = f"{self.BASE_URL}:loadCodeAssist"
        payload = {
            "cloudaicompanionProject": self.project_id,
            "metadata": {
                "ideType": "IDE_UNSPECIFIED",
                "platform": "PLATFORM_UNSPECIFIED",
                "pluginType": "GEMINI"
            }
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": f"GeminiCLI/{self.cli_version}/gemini-3-flash-preview (linux; aarch64)"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        discovered = data.get("cloudaicompanionProject")
                        if discovered:
                            if isinstance(discovered, dict):
                                discovered = discovered.get("id")
                            if discovered:
                                print(f"Discovered GCA Project ID: {discovered}")
                                self.project_id = discovered
                                return discovered
            except Exception as e:
                print(f"Onboarding network error: {str(e)}")
        return self.project_id

    async def generate_content(self, model, prompt, system_instruction=None, tools=None):
        """Send a request to the cloudcode-pa endpoint with recursive tool-calling support."""
        creds = self.auth_manager.get_credentials()
        if not creds.valid:
            creds.refresh(Request())
        
        token = creds.token
        if not self.project_id:
            await self._onboard(token)
        
        # Support list-based prompts (turns) or string prompts
        if isinstance(prompt, list):
            messages = list(prompt)
        else:
            messages = [{"role": "user", "parts": [{"text": prompt}]}]
        
        for turn in range(10): # Increased recursion limit
            # QUOTA PROTECTION: Truncate tool history if it gets too long
            if len(messages) > 10:
                # Keep the original prompt [0] and the 6 most recent messages
                messages = [messages[0]] + messages[-6:]
                print(f"Truncated tool history to stay under quota (Turn {turn})")

            current_model = os.getenv("GEMINI_MODEL", model)
            
            payload = {
                "model": current_model,
                "user_prompt_id": str(uuid.uuid4()),
                "request": {
                    "contents": messages,
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 4096
                    },
                    "session_id": self.session_id
                }
            }
            
            if self.project_id:
                payload["project"] = self.project_id
            if system_instruction:
                payload["request"]["systemInstruction"] = {
                    "role": "system",
                    "parts": [{"text": system_instruction}]
                }
            
            # Tools logic: only add if tools is provided and not empty
            if tools:
                gca_tools = []
                for t in tools:
                    gca_tools.extend(t.get("function_declarations", []))
                if gca_tools:
                    payload["request"]["tools"] = [{"function_declarations": gca_tools}]

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": f"GeminiCLI/{self.cli_version}/{current_model.replace('models/', '')} (linux; aarch64)"
            }

            async with aiohttp.ClientSession() as session:
                endpoint = f"{self.BASE_URL}:generateContent"
                try:
                    async with session.post(endpoint, json=payload, headers=headers) as resp:
                        if resp.status != 200:
                            error_text = await resp.text()
                            raise RuntimeError(f"GCA Error {resp.status}: {error_text}")
                        
                        data = await resp.json()
                        res_data = data.get("response", {})
                        candidates = res_data.get("candidates", [])
                        if not candidates:
                            # Instead of a hard error, try to return whatever text we have or fallback
                            raise RuntimeError(f"Error: No candidates in GCA response. Prompt tokens: {res_data.get('usageMetadata', {}).get('promptTokenCount')}")
                        
                        candidate = candidates[0]
                        content = candidate.get("content", {})
                        parts = content.get("parts", [])
                        messages.append(content)
                        
                        tool_calls = [p.get("functionCall") for p in parts if p.get("functionCall")]
                        if not tool_calls:
                            text_parts = [p.get("text") for p in parts if p.get("text")]
                            return "".join(text_parts) if text_parts else "No text returned."
                        
                        # Only execute if tools were actually allowed
                        if not tools:
                            return "Error: AI attempted tool call but tools are disabled."

                        registry = SkillRegistry()
                        responses_parts = []
                        for tc in tool_calls:
                            name = tc.get("name")
                            args = tc.get("args", {})
                            print(f"Executing tool: {name}({args})")
                            try:
                                result = await registry.execute(name, args)
                            except Exception as te:
                                result = f"Tool Error: {str(te)}"
                            
                            responses_parts.append({
                                "functionResponse": {
                                    "name": name,
                                    "response": {"result": str(result)[:3000]}
                                }
                            })
                        
                        messages.append({"role": "function", "parts": responses_parts})
                        # QUOTA PROTECTION: 3 second delay between turns
                        await asyncio.sleep(3.0)
                except aiohttp.ClientError as ce:
                    raise RuntimeError(f"Network error connecting to GCA: {str(ce)}")
        
        return "Error: Maximum tool-call recursion reached."

class GeminiBrain:
    MODEL_HIERARCHY = [
        "gemini-3-flash-preview",
        "gemini-3-pro-preview",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.5-flash-lite"
    ]

    def __init__(self):
        self.auth_manager = AuthManager()
        self.client = None
        self.gca_transport = None
        self.registry = SkillRegistry()
        self._current_model = os.getenv("GEMINI_MODEL", GEMINI_MODEL)
        self._last_request_time = 0
        self._throttle_delay = 3.5 
        self._cooldowns = {} 
        self._consecutive_failures = 0

    def initialize(self):
        """Initialize the Gemini Client or GCA Transport."""
        api_key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)
        if api_key:
            print("Initializing Gemini Client with API Key...")
            self.client = genai.Client(api_key=api_key)
        else:
            print("Initializing GCA Transport with OAuth...")
            self.gca_transport = CodeAssistTransport(self.auth_manager)

    async def _throttle(self):
        """Ensure independent requests don't happen too close together."""
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self._throttle_delay:
            wait = self._throttle_delay - elapsed
            print(f"Throttling: Waiting {wait:.1f}s...")
            await asyncio.sleep(wait)
        self._last_request_time = time.time()

    async def generate_response(self, prompt, system_instruction=None, retries=3, tools=None):
        """Generate a response with circuit-breaker and intelligent fallback."""
        if not self.client and not self.gca_transport:
            self.initialize()
        
        if self._consecutive_failures >= len(self.MODEL_HIERARCHY):
            print("CIRCUIT BREAKER: API exhaustion. Sleeping 5 mins...")
            self._consecutive_failures = 0
            await asyncio.sleep(300) 
            return "Error: System-wide API exhaustion. Pausing for 5 minutes."

        await self._throttle()
        self._current_model = os.getenv("GEMINI_MODEL", self._current_model)
        
        # Tools decision: None means use registry, empty list means no tools
        final_tools = self.registry.get_tool_schemas() if tools is None else tools

        for attempt in range(retries):
            if self._current_model in self._cooldowns:
                if time.time() < self._cooldowns[self._current_model]:
                    if self._fallback_model():
                        continue
                    else:
                        break

            try:
                if self.client:
                    config = {"tools": final_tools} if final_tools else {}
                    if system_instruction:
                        config["system_instruction"] = system_instruction
                    response = await self.client.aio.models.generate_content(
                        model=self._current_model, contents=prompt, config=config
                    )
                    self._consecutive_failures = 0
                    
                    # NEW SDK HANDLING: Access the first candidate's content
                    if not response.candidates:
                        return "Error: No candidates in response."
                    
                    candidate = response.candidates[0]
                    content = candidate.content
                    
                    # Handle tool calls if they exist in the response
                    parts = content.parts
                    tool_calls = [p.function_call for p in parts if p.function_call]
                    
                    if tool_calls:
                        # Recursive tool execution (simplified for this context)
                        # The client handles most of this if we use a Chat session, 
                        # but here we are using generate_content directly.
                        # For now, let's extract the text and execute tools if needed.
                        # Or ideally, use the same logic as GCA transport for consistency.
                        return await self._handle_client_tool_calls(prompt, system_instruction, final_tools, content)
                    
                    # Return concatenated text from all text parts
                    text_parts = [p.text for p in parts if p.text]
                    return "".join(text_parts) if text_parts else "No text returned."
                else:
                    result = await self.gca_transport.generate_content(
                        model=self._current_model, prompt=prompt, system_instruction=system_instruction, tools=final_tools
                    )
                    self._consecutive_failures = 0
                    return result
            except Exception as e:
                error_msg = str(e)
                self._consecutive_failures += 1
                
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    print(f"Model {self._current_model} exhausted (429).")
                    self._cooldowns[self._current_model] = time.time() + 60 
                    wait_time = 5.0 
                    match = re.search(r"quotaResetDelay\": \"([\d.]+)s", error_msg)
                    if match:
                        wait_time = float(match.group(1)) + 1.0
                        print(f"Waiting {wait_time}s...")
                    if attempt < retries - 1:
                        await asyncio.sleep(wait_time)
                        if self._fallback_model():
                            continue
                    else:
                        return f"Quota reached. (Error: {error_msg})"
                
                if "404" in error_msg or "400" in error_msg:
                    print(f"Model {self._current_model} rejected by server. Error: {error_msg[:100]}...")
                    self._cooldowns[self._current_model] = time.time() + 7200 
                    if self._fallback_model():
                        continue
                    break

                if "Network error" in error_msg or "hostname" in error_msg:
                    print(f"Connection issue: {error_msg}. Retrying in 10s...")
                    await asyncio.sleep(10)
                    continue

                print(f"Model error: {error_msg}. Retrying...")
                await asyncio.sleep(2)
        
        return "Error: Failed to generate response after model scaling."

    def _fallback_model(self):
        """Switch to the next model in the hierarchy."""
        try:
            current_index = self.MODEL_HIERARCHY.index(self._current_model)
            if current_index + 1 < len(self.MODEL_HIERARCHY):
                self._current_model = self.MODEL_HIERARCHY[current_index + 1]
                os.environ["GEMINI_MODEL"] = self._current_model
                print(f"Switched to fallback model: {self._current_model}")
                return True
        except ValueError:
            self._current_model = self.MODEL_HIERARCHY[0]
            os.environ["GEMINI_MODEL"] = self._current_model
            return True
        return False

    async def _handle_client_tool_calls(self, prompt, system_instruction, tools, initial_content):
        """Handle recursive tool calling for the native Gemini Client."""
        if isinstance(prompt, list):
            messages = list(prompt)
        else:
            messages = [{"role": "user", "parts": [{"text": prompt}]}]
        
        messages.append(initial_content)
        
        for turn in range(10):
            # Extract tool calls from the last message
            last_content = messages[-1]
            # Handle both object-based (native SDK) and dict-based (GCA) content
            parts = last_content.parts if hasattr(last_content, "parts") else last_content.get("parts", [])
            
            tool_calls = []
            for p in parts:
                if hasattr(p, "function_call") and p.function_call:
                    tool_calls.append(p.function_call)
                elif isinstance(p, dict) and p.get("functionCall"):
                    tool_calls.append(p.get("functionCall"))

            if not tool_calls:
                text_parts = []
                for p in parts:
                    if hasattr(p, "text") and p.text:
                        text_parts.append(p.text)
                    elif isinstance(p, dict) and p.get("text"):
                        text_parts.append(p.get("text"))
                return "".join(text_parts) if text_parts else "No text returned."

            # Execute tools
            responses_parts = []
            for tc in tool_calls:
                name = tc.name if hasattr(tc, "name") else tc.get("name")
                args = tc.args if hasattr(tc, "args") else tc.get("args", {})
                print(f"Executing tool: {name}({args})")
                try:
                    result = await self.registry.execute(name, args)
                except Exception as te:
                    result = f"Tool Error: {str(te)}"
                
                responses_parts.append({
                    "function_response": {
                        "name": name,
                        "response": {"result": str(result)[:3000]}
                    }
                })
            
            messages.append({"role": "tool", "parts": responses_parts})
            
            # Send back to Gemini
            config = {"tools": tools} if tools else {}
            if system_instruction:
                config["system_instruction"] = system_instruction
            
            # Quota delay
            await asyncio.sleep(3.0)
            
            response = await self.client.aio.models.generate_content(
                model=self._current_model, contents=messages, config=config
            )
            
            if not response.candidates:
                return "Error: No candidates in tool-call follow-up."
            
            messages.append(response.candidates[0].content)

        return "Error: Maximum tool-call recursion reached."
