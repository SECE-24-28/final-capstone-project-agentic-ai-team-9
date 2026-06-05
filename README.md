# 🎬 Movie Recommendation and Summarization System using Custom RAG Pipeline

## 📌 Project Overview

The Movie Recommendation and Summarization System is an AI-powered application that helps users discover movies based on their interests and provides concise movie summaries. The system leverages a Custom Retrieval-Augmented Generation (RAG) pipeline to retrieve relevant movie information and generate intelligent recommendations and summaries using Large Language Models (LLMs).

The project combines Information Retrieval, Natural Language Processing (NLP), Vector Databases, and Generative AI to enhance user experience in movie exploration and decision-making.

---

## 🎯 Problem Statement

With thousands of movies available across multiple platforms, users often struggle to find movies that match their preferences. Additionally, reading lengthy movie descriptions can be time-consuming.

This project addresses these challenges by:

- Providing personalized movie recommendations.
- Generating concise and meaningful movie summaries.
- Enabling semantic search based on movie plots, genres, actors, and user queries.

---

## 🚀 Objectives

- Develop an intelligent movie recommendation system.
- Generate accurate and concise movie summaries.
- Implement a Custom RAG Pipeline for efficient information retrieval.
- Improve user experience through semantic movie search.
- Reduce the time required for users to explore and select movies.

---

## ✨ Features

- Movie Recommendation Engine
- AI-Powered Movie Summarization
- Semantic Search using Vector Embeddings
- Custom Retrieval-Augmented Generation (RAG) Pipeline
- Genre-Based Recommendations
- Similar Movie Discovery
- Fast Information Retrieval
- Interactive User Interface

---

## 🏗️ System Architecture

```text
User Query
     │
     ▼
Embedding Model
     │
     ▼
Vector Database
     │
     ▼
Retriever
     │
     ▼
Relevant Movie Documents
     │
     ▼
Large Language Model (LLM)
     │
     ▼
Recommendations + Summary
```

---

## 🛠️ Technology Stack

### Frontend
- React.js / Streamlit (Choose the one you used)
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- FastAPI / Flask

### AI & Machine Learning
- Large Language Models (LLMs)
- Sentence Transformers
- LangChain (if used)

### Database
- Vector Database (FAISS / ChromaDB)

### Data Processing
- Pandas
- NumPy

---

## 🔍 Working of Custom RAG Pipeline

1. User enters a movie-related query.
2. The query is converted into vector embeddings.
3. Relevant movie documents are retrieved from the vector database.
4. Retrieved context is passed to the Large Language Model.
5. The LLM generates:
   - Personalized movie recommendations.
   - Concise movie summaries.
6. Results are displayed to the user.

---

## 📂 Project Structure

```text
Movie-Recommendation-RAG/
│
├── data/
│   ├── movies_dataset.csv
│
├── embeddings/
│
├── vector_store/
│
├── backend/
│   ├── app.py
│   ├── rag_pipeline.py
│
├── frontend/
│
├── models/
│
├── screenshots/
│
├── requirements.txt
│
└── README.md
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone <repository-url>
cd Movie-Recommendation-RAG
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
python app.py
```

---

## 📖 Usage

1. Launch the application.
2. Enter a movie name or preference.
3. The system retrieves relevant movie information.
4. AI generates personalized recommendations.
5. View summarized movie descriptions and suggested movies.

---

## 📊 Dataset

The project uses a movie dataset containing:

- Movie Title
- Genre
- Cast
- Director
- Plot Summary
- Ratings
- Release Year

---

## 🎯 Expected Outcomes

- Accurate movie recommendations.
- Fast semantic search.
- High-quality AI-generated summaries.
- Improved movie discovery experience.

---

## 🔮 Future Enhancements

- Multi-language movie summaries.
- Sentiment-based recommendations.
- User profile personalization.
- Voice-based movie search.
- Integration with OTT platforms.
- Real-time trending movie recommendations.

---

## 👨‍💻 Team Members

- VISHAL M K
- NIVAASH M
- RITISH BHARATH S R

---

## 📜 License

This project is developed for academic and educational purposes.

---

## 🙏 Acknowledgements

- OpenAI
- Hugging Face
- LangChain
- FAISS / ChromaDB
- Movie Dataset Providers
