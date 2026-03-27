from pydantic import BaseModel, Field
from typing import List

class ResearchOutput(BaseModel):
    """Schema for the Researcher Agent's output."""
    company_summary: str = Field(description="A concise summary of the company's business and tech stack")
    recent_news: List[str] = Field(description="A list of recent business news items from the last 6-12 months")

class AnalysisOutput(BaseModel):
    """Schema for the Analyst Agent's output."""
    pain_points: List[str] = Field(description="A list of up to 3 specific pain points identified for the company", max_length=3)

class EmailOutput(BaseModel):
    """Schema for the Copywriter Agent's output."""
    subject_line: str = Field(description="A catchy but professional subject line")
    email_body: str = Field(description="The full body of the personalized cold email")
