import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def configure_llm():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("Google API Key not found. Please add it to the .env file.")
    genai.configure(api_key=api_key)

def get_ats_score(resume_text: str, job_description: str) -> dict:
    """
    Uses Google Gemini API to act as an ATS system, 
    evaluate the resume against the job description, 
    and return a score and feedback in JSON format.
    """
    configure_llm()
    
    # We use gemini-2.5-flash for fast, high-quality responses
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are an expert Applicant Tracking System (ATS) with deep knowledge of tech and non-tech industries, software engineering, data science, and product management.
    Your task is to evaluate the provided resume against the provided job description.
    
    Resume Text:
    {resume_text}
    
    Job Description:
    {job_description}
    
    Provide your evaluation strictly as a valid JSON object with the following keys:
    1. "Match_Percentage": A string representing the matching percentage (e.g., "85%").
    2. "Matching_Keywords": A list of strings containing keywords from the JD that were found in the resume.
    3. "Missing_Keywords": A list of strings containing important keywords from the JD that are missing in the resume.
    4. "Profile_Summary": A brief 2-3 sentence summary of the candidate's fit for the role.
    5. "Recommendation": A brief recommendation on what the candidate should improve or add to increase their chances.

    Ensure the response is ONLY a raw JSON object and nothing else. No markdown formatting like ```json.
    """
    
    response = model.generate_content(prompt)
    
    try:
        # Attempt to parse the response as JSON
        response_text = response.text.strip()
        # Remove any potential markdown formatting if the model still includes it
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        result_dict = json.loads(response_text.strip())
        return result_dict
    except Exception as e:
        # Fallback if parsing fails
        print(f"Error parsing JSON: {e}\nResponse text: {response.text}")
        return {
            "Match_Percentage": "N/A",
            "Matching_Keywords": [],
            "Missing_Keywords": [],
            "Profile_Summary": "Error parsing the LLM response.",
            "Recommendation": "Try again or check the console logs."
        }
