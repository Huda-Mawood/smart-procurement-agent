from crewai import Crew, Process
from crew import (
    search_queries_recommendations_agent,
    search_engine_agent,
    scraping_agent,
    procurement_report_author_agent,
    search_queries_recommendations_task,
    search_engine_task,
    scraping_task,
    procurement_report_author_task,
    company_context
)

rankyx_crew = Crew(
    agents=[
        search_queries_recommendations_agent,
        search_engine_agent,
        scraping_agent,
        procurement_report_author_agent,
    ],
    tasks=[
        search_queries_recommendations_task,
        search_engine_task,
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

crew_results = rankyx_crew.kickoff(
    inputs={
        "product_name": "coffee machine for the office",
        "websites_list": ["www.amazon.eg", "www.jumia.com.eg", "www.noon.com/egypt-en"],
        "country_name": "Egypt",
        "no_keywords": 10,
        "language": "English",
        "score_th": 0.10,
        "top_recommendations_no": 10,
    }
)