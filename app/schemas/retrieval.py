from pydantic import BaseModel, Field
from typing import Optional, List

class SearchIntent(BaseModel):
    optimized_query: str = Field(
        description="""The rewritten user query optimized for vector database search. 
        Rules:
        1. Resolve all aliases, nicknames, or titles to their full names (e.g., 'Padfoot' -> 'Sirius Black', 'He-Who-Must-Not-Be-Named' -> 'Lord Voldemort', 'Moony' -> 'Remus Lupin').
        2. Fix spelling errors of magical terms.
        3. Add implicit context keywords to make the search richer."""
    )
    book_titles: Optional[List[str]] = Field(
        default_factory=list,
        description="""A list of exact Harry Potter book titles mentioned or implied in the user's query. 
        Valid options are exactly: 
        'Harry Potter and the Sorcerer's Stone', 
        'Harry Potter and the Chamber of Secrets', 
        'Harry Potter and the Prisoner of Azkaban', 
        'Harry Potter and the Goblet of Fire', 
        'Harry Potter and the Order of the Phoenix', 
        'Harry Potter and the Half-Blood Prince', 
        'Harry Potter and the Deathly Hallows'.
        Return an empty list if no specific books are mentioned."""
    )