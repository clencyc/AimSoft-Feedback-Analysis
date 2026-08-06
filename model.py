from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

app = FastAPI(
    title="Sentiment Analysis API", 
    version="1.0.0", 
    description="API for sentiment analysis using a pre-trained model."
)

# # 1. Corrected case sensitivity to match your Hugging Face account profile
# REPO_ID = "Christy123/CustomerFeedbackSentimentAnalysis"

# print("Loading model and tokenizer from Hugging Face...")
# tokenizer = AutoTokenizer.from_pretrained(REPO_ID, subfolder="sentiment_model")
# model = AutoModelForSequenceClassification.from_pretrained(REPO_ID, subfolder="sentiment_model")
# print("Model loaded successfully!")


model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# 2. Correctly feed your loaded remote model and tokenizer into the transformers pipeline
classifier = pipeline("sentiment-analysis", model=model_name)

print(classifier("This product is amazing, I love it!"))
print(classifier("Terrible experience, never buying again."))

class TextPayload(BaseModel):
    text: str

# 3. Changed method to POST and added the leading forward slash
@app.post("/sentiment/")
async def predict_sentiment(payload: TextPayload):
    # Pass the text to your configured pipeline
    prediction = classifier(payload.text)[0]
    
    label_mapping = {
        "LABEL_0": "positive",
        "LABEL_1": "negative"
    }

    return {
        "text": payload.text,
        "sentiment": label_mapping.get(prediction['label'], "unknown"),
        "confidence_level": round(prediction['score'], 4)
    }
