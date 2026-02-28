


from crewai import Agent, Task, Crew, Process,LLM
from crewai.tools import tool
import agentops
from google.colab import userdata
import os
import json
from pydantic import BaseModel,Field
from typing import List
from tavily import TavilyClient
from scrapegraph_py import Client
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource

import os

os.environ["AGENTOPS_API_KEY"] =AGENTOPS_API_KEY 
os.environ["GROQ_API_KEY"]=AGENTOPS_API_KEY

session = agentops.init(
    api_key=os.environ["AGENTOPS_API_KEY"],
    skip_auto_end_session=True
)

import os
from crewai import LLM

output_dir = './ai-agent-output'
os.makedirs(output_dir, exist_ok=True)

basic_llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    temperature=0,
    rpm=10
)
search_client=TavilyClient(api_key=TAVILY_API_KEY)

scrape_client=Client(api_key=SCRAPE_API_KEY)

no_keywords=10
about_company="Rankyx is a company that provides AI solutions to help websites refine their search and recommendation systems."
company_context=StringKnowledgeSource(
    content=about_company
)

"""## **Setup Agents**"""

# class SearchQuery(BaseModel):
#     query: str = Field(..., title="Search query text")
#     url: str = Field(..., title="Search URL for the query")

# class SuggestedSearchQueries(BaseModel):
#     queries: List[SearchQuery] = Field(
#         ...,
#         title="Suggested search queries with URLs",
#         min_items=1,
#         max_items=no_keywords
#     )
class SuggestedSearchQueries(BaseModel):
    queries: List[str] = Field(..., title="Suggested search queries to be passed to the search engine",
                               min_items=1, max_items=no_keywords)
search_queries_recommendations_agent=Agent(
    role="Search Queries Recommendation Agent",
    goal="\n".join([
        #use join because not wait list so i convert to lines of string
            "To provide a list of suggested search queries to passed to the search engine.",
            "the quries must be varied and looking for specific items."
        ]),

    backstory="the agent is  designed to help in looking for products by prividing list of suggested search quries to be passed to the search engine  based on the  context provided",

    llm=basic_llm,
    verbose=True
)
search_queries_recommendations_task=Task(
    description="\n".join(
        [
        "Rankyx is looking to buy {product_name} at the best prices (value for a price strategy)",
        "The campany target any of these websites to buy from: {websites_list}",
        "The company wants to reach all available proucts on the internet to be compared later in another stage.",
        "The stores must sell the product in {country_name}",
        "Generate at maximum {no_keywords} queries.",
        "The search keywords must be in {language} language.",
        "Search keywords must contains specific brands, types or technologies. Avoid general keywords.",
        "The search query must reach an ecommerce webpage for product, and not a blog or listing page."
        ]
    ),

    expected_output="A JSON object containing a list of suggested search queries",
    output_json=SuggestedSearchQueries,
    output_file=os.path.join(output_dir,"step_1_suggested_search_queries.json"),
    agent=search_queries_recommendations_agent
)

"""##Agent B"""

class SingleSearchResult(BaseModel):
  title:str
  url:str
  content:str
  score:float
  search_query:str

class AllSearchResult(BaseModel):
  results:List[SingleSearchResult]
@tool
def search_engin_tool(query:str):
  """Useful for search-based queries. Use this to find current information about any query related pages using search engine. """
  return search_client.search(query)
search_engin_agent=Agent(
    role="Search Engine Agent",
    goal="To search for products based on suggested search query",
    backstory="The agent is designed to help in looking for products by searching for products based on the suggested search queries.",
    llm=basic_llm,
    verbose=True,
    tools=[search_engin_tool]
)
search_engin_task=Task(
    description="\n".join([
         "The task is to search for products based on the suggested search queries.",
        "You have to collect results from multiple search queries.",
        "Ignore any susbicious links or not an ecommerce single product website link.",
        "Ignore any search results with confidence score less than ({score_th}) .",
        "The search results will be used to compare prices of products from different websites.",
    ]),
    expected_output="A JSON object containing the search results",
    output_json=AllSearchResult,
    output_file=os.path.join(output_dir,"step_2_search_result_engin.json"),
    agent=search_engin_agent

)

"""##Agent C"""

def web_scraping_tool(page_url:str,required_fields:list):

  details=scrape_client.smartscraper(
      website_url=page_url,
      user_prompt="Extract"+json.dumps(required_fields,ensure_ascii=False)+" From the web page"
  )

  return {
      "page_url":page_url,
      "details":details
  }

# page_url=""
# required_fields=["product_title","current_price","old_price"]

# page_details=web_scraping_tool(page_url=page_url,required_fields=required_fields)

class ProductSpec(BaseModel):
  specifaction_name:str
  specifaction_value:str


class SingleExtractedProduct(BaseModel):
    page_url: str = Field(..., title="The original url of the product page")
    product_title: str = Field(..., title="The title of the product")
    product_image_url: str = Field(..., title="The url of the product image")
    product_url: str = Field(..., title="The url of the product")
    product_current_price: float = Field(..., title="The current price of the product")
    product_original_price: float = Field(title="The original price of the product before discount. Set to None if no discount", default=None)
    product_discount_percentage: float = Field(title="The discount percentage of the product. Set to None if no discount", default=None)

    product_specs: List[ProductSpec] = Field(..., title="The specifications of the product. Focus on the most important specs to compare.", min_items=1, max_items=5)

    agent_recommendation_rank: int = Field(..., title="The rank of the product to be considered in the final procurement report. (out of 5, Higher is Better) in the recommendation list ordering from the best to the worst")
    agent_recommendation_notes: List[str]  = Field(..., title="A set of notes why would you recommend or not recommend this product to the company, compared to other products.")


class AllExtractedProducts(BaseModel):
  products:List[SingleExtractedProduct]


@tool
def web_scraping_tool(page_url:str):

  """
    An AI Tool to help an agent to scrape a web page

    Example:
    web_scraping_tool(
        page_url="https://www.noon.com/egypt-en/15-bar-fully-automatic-espresso-machine-1-8-l-1500",

    )
    """
  details=scrape_client.smartscraper(
      website_url=page_url,
      user_prompt="Extract ```json \n"+SingleExtractedProduct.schema_json()+"```\n From the web page"
  )

  return {
      "page_url":page_url,
      "details":details
  }
scraping_agent=Agent(
    role="Web scraping agent",
    goal="To extract details from any website",
    backstory="The agent is designed to help in looking for required values from any website url. These details will be used to decide which best product to buy.",
    llm=basic_llm,
    tools=[web_scraping_tool],
    verbose=True,
)
scraping_task=Task(
    description="\n".join([
        "The task is to extract product details from any ecommerce store page url.",
        "The task has to collect results from multiple pages urls.",
        "Collect the best {top_recommendations_no} products from the search results.",
    ]),
    expected_output="A JSON containing products details",
    json_output=AllExtractedProducts,
    output_file=os.path.join(output_dir,"step_3_search_results.json"),
    agent=scraping_agent
)

"""##Agent D"""

procurement_report_author_agent=Agent(
    role="Procurement Report Author Agent",
    goal="To generate a professional HTML page for the procurement report",
    backstory="The agent is designed to assist in generating a professional HTML page for the procurement report after looking into a list of products.",
    llm=basic_llm,
    verbose=True
)
procurement_report_author_task=Task(
    description="\n".join([
        "The task is to generate a professional HTML page for the procurement report.",
        "You have to use Bootstrap CSS framework for a better UI.",
        "Use the provided context about the company to make a specialized report.",
        "The report will include the search results and prices of products from different websites.",
        "The report should be structured with the following sections:",
        "1. Executive Summary: A brief overview of the procurement process and key findings.",
        "2. Introduction: An introduction to the purpose and scope of the report.",
        "3. Methodology: A description of the methods used to gather and compare prices.",
        "4. Findings: Detailed comparison of prices from different websites, including tables and charts.",
        "5. Analysis: An analysis of the findings, highlighting any significant trends or observations.",
        "6. Recommendations: Suggestions for procurement based on the analysis.",
        "7. Conclusion: A summary of the report and final thoughts.",
        "8. Appendices: Any additional information, such as raw data or supplementary materials.",
    ]),
    expected_output=" A professional HTML page for procurement report .",
    output_file=os.path.join(output_dir,"step_4_procurement_report.html"),
    agent=procurement_report_author_agent
)

"""##Run the AI Crew"""


rankyx_crew=Crew(
    agents=[
        search_queries_recommendations_agent,
        search_engin_agent,
        scraping_agent,
        procurement_report_author_agent,
        ],
    tasks=[
        search_queries_recommendations_task,
        search_engin_task,
        scraping_task,
        procurement_report_author_task,

        ],
    process=Process.sequential,
    knowledge_sources=[company_context],
    embedder={
        "provider": "huggingface",
        "config": {
            "model": "sentence-transformers/all-MiniLM-L6-v2"
        }
    }
)

crew_results=rankyx_crew.kickoff(
   inputs= {
        "product_name": "coffee machine for the office",
        "websites_list": ["www.amazon.eg", "www.jumia.com.eg", "www.noon.com/egypt-en"],
        "country_name": "Egypt",
        "no_keywords": 10,
        "language":"English",
        "score_th":0.10,
        "top_recommendations_no":10,


    }
)

