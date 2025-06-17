 # Install system deps (Tesseract, tzdata for zoneinfo, etc.)
 RUN apt-get update \
  && apt-get install -y --no-install-recommends \
       git \
      tesseract-ocr \
      libtesseract-dev \
   libleptonica-dev \
      pkg-config \
      poppler-utils \
    tzdata \
 && apt-get install -y --no-install-recommends \
     git \
   ca-certificates \
   tesseract-ocr \
   libtesseract-dev \
   libleptonica-dev \
   pkg-config \
  poppler-utils \
  tzdata \
   && rm -rf /var/lib/apt/lists/*
