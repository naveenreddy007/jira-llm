import os
import requests
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class DeepSeekLLM:
    """Service for interacting with DeepSeek LLM API."""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            print("WARNING: DeepSeek API key not found. Please add it to your .env file.")
            raise ValueError("DeepSeek API key not found. Please add it to your .env file.")
        else:
            print("INFO: DeepSeek API key loaded successfully.")
        
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Test connection to verify API works
        self.test_connection()
    
    def test_connection(self):
        """Test the connection to DeepSeek API."""
        try:
            response = self.generate_response("Hello, this is a test message.")
            print(f"INFO: Successfully connected to DeepSeek API. Response: {response[:30]}...")
            return True
        except Exception as e:
            print(f"ERROR: Failed to connect to DeepSeek API: {str(e)}")
            return False
    
    def generate_response(self, prompt, system_prompt=None, temperature=0.7, max_tokens=1000):
        """Generate a response from DeepSeek LLM."""
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add user prompt
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": "deepseek-chat",  # Adjust based on which DeepSeek model you're using
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        print(f"DEBUG: Sending request to DeepSeek API with payload: {json.dumps(payload)[:100]}...")
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
            print(f"DEBUG: Received response with status code {response.status_code}")
            
            # Print full response for debugging
            print(f"DEBUG: Raw response: {response.text[:200]}...")
            
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Request exception when calling DeepSeek API: {str(e)}")
            return f"Error calling DeepSeek API: {str(e)}"
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"ERROR: Error parsing DeepSeek response: {str(e)}")
            return f"Error parsing DeepSeek response: {str(e)}"
        except Exception as e:
            print(f"ERROR: Unexpected error with DeepSeek API: {str(e)}")
            return f"Unexpected error with DeepSeek API: {str(e)}"

# Simple fallback class that can be used if the main LLM service fails
class MockLLM:
    """A mock LLM service that returns pre-defined responses."""
    
    def generate_response(self, prompt, system_prompt=None, temperature=0.7, max_tokens=1000):
        """Generate a mock response."""
        print(f"DEBUG: Using MockLLM since DeepSeek is not available.")
        return "This is a mock response as the LLM service is not properly configured. Please check your API key and connection."

# Helper functions for Jira + LLM integration
def get_llm_service():
    """Get an LLM service instance, falling back to a mock if needed."""
    try:
        return DeepSeekLLM()
    except Exception as e:
        print(f"WARNING: Using MockLLM due to error: {str(e)}")
        return MockLLM()

def summarize_ticket(llm, ticket_data):
    """Generate a summary of a Jira ticket using LLM."""
    prompt = f"""
    Please provide a concise summary of this Jira ticket:
    
    Title: {ticket_data.get('summary', 'No title')}
    Description: {ticket_data.get('description', 'No description')}
    Status: {ticket_data.get('status', 'Unknown')}
    Priority: {ticket_data.get('priority', 'Unknown')}
    Reporter: {ticket_data.get('reporter', 'Unknown')}
    
    Provide a 2-3 sentence summary that captures the key points.
    """
    
    return llm.generate_response(prompt)

def categorize_ticket(llm, ticket_data):
    """Categorize a Jira ticket using LLM."""
    prompt = f"""
    Based on the information below, categorize this Jira ticket into one of the following:
    - Bug
    - Feature Request
    - Documentation
    - Support Request
    - Infrastructure
    - Security Issue
    
    Title: {ticket_data.get('summary', 'No title')}
    Description: {ticket_data.get('description', 'No description')}
    
    Reply ONLY with the category name, nothing else.
    """
    
    return llm.generate_response(prompt)

def generate_response_suggestion(llm, ticket_data):
    """Generate a suggested response for a ticket."""
    prompt = f"""
    Please draft a helpful, professional response to this Jira ticket:
    
    Title: {ticket_data.get('summary', 'No title')}
    Description: {ticket_data.get('description', 'No description')}
    Status: {ticket_data.get('status', 'Unknown')}
    Priority: {ticket_data.get('priority', 'Unknown')}
    
    The response should acknowledge the issue, provide next steps if possible, and maintain a helpful tone.
    """
    
    return llm.generate_response(prompt)

def analyze_project_tickets(llm, project_stats):
    """Generate insights about a project based on ticket data."""
    prompt = f"""
    Based on the following Jira project statistics, provide 3-5 key insights and recommendations:
    
    Project: {project_stats.get('name', 'Unknown')}
    Total Tickets: {project_stats.get('total_tickets', 0)}
    Open Tickets: {project_stats.get('open_tickets', 0)}
    Tickets by Priority:
    {project_stats.get('priority_breakdown', 'No data')}
    Average Resolution Time: {project_stats.get('avg_resolution_time', 'Unknown')}
    
    Focus on identifying patterns, bottlenecks, and suggestions for improving project health.
    """
    
    return llm.generate_response(prompt)