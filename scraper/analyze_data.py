#!/usr/bin/env python3
"""
Westpac Scholars Data Analysis

This script analyzes the scraped scholar data, performs sentiment analysis,
and extracts themes from the text.
"""

import os
import json
import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("analysis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
INPUT_DIR = "data"
OUTPUT_DIR = "analysis"
SCHOLARS_JSON = os.path.join(INPUT_DIR, "westpac_scholars.json")
ANALYSIS_JSON = os.path.join(OUTPUT_DIR, "analysis_results.json")

def download_nltk_resources():
    """Download required NLTK resources."""
    resources = [
        'punkt', 
        'stopwords', 
        'wordnet', 
        'vader_lexicon'
    ]
    
    for resource in resources:
        try:
            nltk.download(resource, quiet=True)
            logger.info(f"Downloaded NLTK resource: {resource}")
        except Exception as e:
            logger.error(f"Error downloading NLTK resource {resource}: {e}")

def load_data(filename):
    """Load scholar data from JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
        logger.info(f"Loaded {len(data)} scholar records from {filename}")
        return data
    except Exception as e:
        logger.error(f"Error loading data from {filename}: {e}")
        return []

def preprocess_text(text):
    """Preprocess text for analysis."""
    if not text or not isinstance(text, str):
        return ""
    
    # Tokenize
    tokens = word_tokenize(text.lower())
    
    # Remove stopwords and non-alphabetic tokens
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
    
    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
    return " ".join(tokens)

def perform_sentiment_analysis(scholars):
    """
    Perform sentiment analysis on scholar bios and descriptions.
    
    Args:
        scholars: List of scholar dictionaries
        
    Returns:
        List of scholar dictionaries with sentiment scores added
    """
    sia = SentimentIntensityAnalyzer()
    
    for scholar in scholars:
        # Combine all text fields for sentiment analysis
        text_fields = []
        
        if scholar.get('bio'):
            text_fields.append(scholar['bio'])
        
        if scholar.get('full_bio'):
            text_fields.append(scholar['full_bio'])
            
        if scholar.get('project_description'):
            text_fields.append(scholar['project_description'])
        
        combined_text = " ".join(text_fields)
        
        if combined_text:
            sentiment = sia.polarity_scores(combined_text)
            scholar['sentiment'] = {
                'compound': sentiment['compound'],
                'positive': sentiment['pos'],
                'negative': sentiment['neg'],
                'neutral': sentiment['neu']
            }
    
    logger.info(f"Performed sentiment analysis on {len(scholars)} scholar records")
    return scholars

def extract_themes(scholars, num_topics=5, num_words=10):
    """
    Extract themes from scholar bios and descriptions using LDA.
    
    Args:
        scholars: List of scholar dictionaries
        num_topics: Number of topics to extract
        num_words: Number of words per topic
        
    Returns:
        Dictionary with theme information
    """
    # Combine and preprocess text from all scholars
    texts = []
    
    for scholar in scholars:
        text_fields = []
        
        if scholar.get('bio'):
            text_fields.append(scholar['bio'])
        
        if scholar.get('full_bio'):
            text_fields.append(scholar['full_bio'])
            
        if scholar.get('project_description'):
            text_fields.append(scholar['project_description'])
        
        combined_text = " ".join(text_fields)
        
        if combined_text:
            preprocessed_text = preprocess_text(combined_text)
            texts.append(preprocessed_text)
    
    if not texts:
        logger.warning("No text data available for theme extraction")
        return {"themes": []}
    
    # Create TF-IDF features
    vectorizer = TfidfVectorizer(
        max_features=1000,
        min_df=2,
        max_df=0.8
    )
    
    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()
    
    # Apply LDA for topic modeling
    lda = LatentDirichletAllocation(
        n_components=num_topics,
        random_state=42,
        max_iter=10
    )
    
    lda.fit(tfidf_matrix)
    
    # Extract topics
    themes = []
    for topic_idx, topic in enumerate(lda.components_):
        top_words_idx = topic.argsort()[:-num_words-1:-1]
        top_words = [feature_names[i] for i in top_words_idx]
        
        themes.append({
            "id": topic_idx,
            "name": f"Theme {topic_idx + 1}",
            "keywords": top_words,
            "weight": float(topic.sum())
        })
    
    # Assign themes to scholars
    scholar_themes = lda.transform(tfidf_matrix)
    
    for i, scholar in enumerate(scholars):
        if i < len(scholar_themes):
            # Get the top 2 themes for this scholar
            top_theme_indices = scholar_themes[i].argsort()[-2:][::-1]
            scholar_theme_scores = [
                {"theme_id": int(idx), "score": float(scholar_themes[i][idx])}
                for idx in top_theme_indices
                if scholar_themes[i][idx] > 0.1  # Only include significant themes
            ]
            scholar['themes'] = scholar_theme_scores
    
    logger.info(f"Extracted {num_topics} themes from scholar data")
    return {"themes": themes}

def analyze_scholarship_distribution(scholars):
    """
    Analyze the distribution of scholarship types.
    
    Args:
        scholars: List of scholar dictionaries
        
    Returns:
        Dictionary with scholarship distribution information
    """
    scholarship_counts = {}
    
    for scholar in scholars:
        scholarship_type = scholar.get('scholarship_type')
        if scholarship_type:
            scholarship_counts[scholarship_type] = scholarship_counts.get(scholarship_type, 0) + 1
    
    # Convert to list of dictionaries for easier use in frontend
    distribution = [
        {"name": scholarship_type, "count": count}
        for scholarship_type, count in scholarship_counts.items()
    ]
    
    logger.info(f"Analyzed distribution of {len(distribution)} scholarship types")
    return {"scholarship_distribution": distribution}

def analyze_institution_distribution(scholars):
    """
    Analyze the distribution of institutions.
    
    Args:
        scholars: List of scholar dictionaries
        
    Returns:
        Dictionary with institution distribution information
    """
    institution_counts = {}
    
    for scholar in scholars:
        institution = scholar.get('institution')
        if institution:
            institution_counts[institution] = institution_counts.get(institution, 0) + 1
    
    # Convert to list of dictionaries for easier use in frontend
    distribution = [
        {"name": institution, "count": count}
        for institution, count in institution_counts.items()
    ]
    
    # Sort by count in descending order
    distribution.sort(key=lambda x: x["count"], reverse=True)
    
    logger.info(f"Analyzed distribution of {len(distribution)} institutions")
    return {"institution_distribution": distribution}

def analyze_year_distribution(scholars):
    """
    Analyze the distribution of scholars by year.
    
    Args:
        scholars: List of scholar dictionaries
        
    Returns:
        Dictionary with year distribution information
    """
    year_counts = {}
    
    for scholar in scholars:
        year = scholar.get('year')
        if year:
            # Extract just the year if it's in a format like "2020 Cohort"
            import re
            year_match = re.search(r'\d{4}', year)
            if year_match:
                year = year_match.group(0)
            
            year_counts[year] = year_counts.get(year, 0) + 1
    
    # Convert to list of dictionaries for easier use in frontend
    distribution = [
        {"year": year, "count": count}
        for year, count in year_counts.items()
    ]
    
    # Sort by year
    distribution.sort(key=lambda x: x["year"])
    
    logger.info(f"Analyzed distribution of scholars across {len(distribution)} years")
    return {"year_distribution": distribution}

def save_analysis_results(results, filename):
    """Save analysis results to a JSON file."""
    # Ensure output directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(results, file, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved analysis results to {filename}")

def main():
    """Main function to run the analysis."""
    logger.info("Starting Westpac Scholars data analysis")
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Download NLTK resources
    download_nltk_resources()
    
    # Load scholar data
    scholars = load_data(SCHOLARS_JSON)
    
    if not scholars:
        logger.error("No scholar data available for analysis")
        return
    
    # Perform sentiment analysis
    scholars_with_sentiment = perform_sentiment_analysis(scholars)
    
    # Extract themes
    themes = extract_themes(scholars_with_sentiment)
    
    # Analyze distributions
    scholarship_distribution = analyze_scholarship_distribution(scholars_with_sentiment)
    institution_distribution = analyze_institution_distribution(scholars_with_sentiment)
    year_distribution = analyze_year_distribution(scholars_with_sentiment)
    
    # Combine all analysis results
    analysis_results = {
        "scholars": scholars_with_sentiment,
        **themes,
        **scholarship_distribution,
        **institution_distribution,
        **year_distribution
    }
    
    # Save analysis results
    save_analysis_results(analysis_results, ANALYSIS_JSON)
    
    logger.info("Data analysis completed")

if __name__ == "__main__":
    main() 