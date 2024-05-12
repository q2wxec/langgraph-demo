
from langchain_community.utilities import SearchApiAPIWrapper
import os
os.environ["SEARCHAPI_API_KEY"] = ""
search_tool = SearchApiAPIWrapper()