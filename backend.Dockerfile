FROM python:3.8-slim
WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       curl \
       poppler-utils \
       tesseract-ocr \
       libxml2-dev libxslt1-dev \
       default-jdk \
       git \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir torch==2.2.0+cpu torchvision==0.17.0+cpu torchaudio==2.2.0+cpu \
        -f https://download.pytorch.org/whl/cpu/torch_stable.html \
 && pip install --no-cache-dir -r requirements.txt
# NLP models
# spaCy
RUN python -m spacy download en_core_web_sm
# NLTK stopwords
RUN python -m nltk.downloader stopwords
# Copy Hugging Face model into container cache
COPY all-MiniLM-L6-v2 /root/.cache/huggingface/sentence-transformers/all-MiniLM-L6-v2
RUN mkdir -p /data
VOLUME ["/data"]
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app", "--timeout", "120"]
