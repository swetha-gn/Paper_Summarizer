# Research Paper Summarizer and Assistant

## Overview

The Research Paper Summarizer and Assistant is an AI-driven system designed to automate the process of literature reviews. By combining cutting-edge **Natural Language Processing (NLP)** techniques with **Large Language Models (LLMs)**, the tool retrieves, summarizes, and synthesizes academic papers into concise and insightful reports. 

The system accelerates research workflows by helping users query topics, locate relevant academic articles, generate section-wise summaries, and build a reusable knowledge base for future exploration.


## Project Goals

- Automate academic paper retrieval from repositories like **arXiv**.
- Extract structured sections (abstract, introduction, methods, results) from PDFs.
- Generate concise, accurate section-wise summaries using **LLMs** (e.g., GPT-4).
- Evaluate summary quality using **BERTScore**.
- Store processed summaries and metadata as vector embeddings for future queries.
- Deliver structured responses synthesizing key findings, methodologies, and research gaps.
- Build a scalable and adaptable system for future academic search and summarization.


## Technologies and Tools Used

| Category                 | Tools and Libraries                           |
|---------------------------|------------------------------------------------|
| Programming Language      | Python 3.x                                    |
| NLP & Summarization       | OpenAI API (text-davinci, GPT-4)              |
| Vector Storage            | FAISS (Facebook AI Similarity Search)         |
| PDF Text Extraction       | PyMuPDF (fitz)                                |
| Embedding Models          | OpenAI Embedding API (text-embedding-ada-002) |
| Data Processing           | NumPy, Pandas                                 |
| Evaluation Metrics        | BERTScore                                     |
| Web Scraping & API Access  | aiohttp, arXiv API                            |
| Code Management           | Modular Python classes and async pipelines    |

## Dataset Description

- **Primary Source:** [arXiv.org](https://arxiv.org/)
- **Type:** Academic research papers in PDF format
- **Sections Processed:** Title, Abstract, Introduction, Methodology, Results, Conclusion
- **Storage:** PDF content, summaries, and vector embeddings are stored locally.


## Methodology

1. **Query Input and Search**  
   - User submits a topic or question.
   - Query is embedded and matched semantically against academic repositories via the arXiv API.

2. **Paper Retrieval and Processing**  
   - Asynchronous download of academic papers.
   - Text extraction and section segmentation using PyMuPDF.

3. **Summarization**  
   - Section-wise summarization using OpenAI's LLMs.
   - Custom prompt engineering ensures focus on contributions, findings, and methodologies.

4. **Evaluation of Summaries**  
   - BERTScore used to evaluate semantic similarity against reference abstracts.

5. **Embedding and Storage**  
   - Summaries are converted into vector embeddings and stored using FAISS for future retrieval.

6. **Structured Response Generation**  
   - System synthesizes findings across multiple papers into a cohesive narrative.


## Key Features

- **Automated Literature Review:** Rapidly locate, summarize, and synthesize papers relevant to a user’s query.
- **High-Quality Summaries:** Section-wise focus ensures critical information is retained.
- **Reusable Knowledge Base:** Embeddings allow fast retrieval of processed papers for future queries.
- **Scalable Architecture:** Easily extensible to multiple languages, richer sources, and improved models.



## User Interface

A simple console-based interaction is provided for:
- Entering queries
- Triggering paper search and summarization
- Reviewing structured outputs

*(GUI extensions planned for future versions.)*

## Sample Output

- **Main Findings:** Summarized across relevant papers.
- **Methods Overview:** Highlights experimental designs and approaches.
- **Research Gaps:** Points out limitations and areas needing future work.
- **Future Directions:** Synthesizes suggestions for further study.

## Future Enhancements

- Extend source support beyond arXiv (Google Scholar, PubMed).
- Integrate multi-lingual summarization capabilities.
- Develop a full-fledged web-based UI using Streamlit or Gradio.
- Apply reinforcement learning techniques to fine-tune summary generation.

## Co-Author
- **Swetha Gendlur Nagarajan**

*(Project submitted as part of academic coursework, 2025.)*

