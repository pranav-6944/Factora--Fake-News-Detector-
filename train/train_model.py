import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import os

# ========== CONFIG ==========
DATA_DIR = "datasets"  # make sure this is where your True.csv and Fake.csv live
MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

TRUE_PATH = os.path.join(DATA_DIR, "True.csv")
FAKE_PATH = os.path.join(DATA_DIR, "Fake.csv")
MODEL_FILE = os.path.join(MODEL_DIR, "finalized_model.pkl")
VECTORIZER_FILE = os.path.join(MODEL_DIR, "vectorizer.pkl")
# ============================

# 1. Load the data
df_true = pd.read_csv(TRUE_PATH)
df_fake = pd.read_csv(FAKE_PATH)

# 2. Add labels
df_true['label'] = 1
df_fake['label'] = 0

# 3. Combine datasets
df = pd.concat([df_true, df_fake], ignore_index=True)
df = df[['title', 'label']]  # Use 'title' column for classification

# 4. Drop NaN and clean text
df.dropna(inplace=True)
df['title'] = df['title'].str.strip()

# 5. Train-test split
X_train, X_test, y_train, y_test = train_test_split(df['title'], df['label'], test_size=0.2, random_state=42)

# 6. TF-IDF Vectorization
vectorizer = TfidfVectorizer(max_features=5000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# 7. Train model
model = LogisticRegression(max_iter=1000)
model.fit(X_train_vec, y_train)

# 8. Evaluate
y_pred = model.predict(X_test_vec)
print("✅ Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# 9. Save model + vectorizer
joblib.dump(model, MODEL_FILE)
joblib.dump(vectorizer, VECTORIZER_FILE)
print(f"📦 Model saved to: {MODEL_FILE}")
print(f"📦 Vectorizer saved to: {VECTORIZER_FILE}")
