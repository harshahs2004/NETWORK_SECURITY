import pickle
import numpy as np

from sklearn.metrics import precision_score, recall_score, f1_score


# 1. Load already-trained Random Forest
model = pickle.load(
    open("final_model/model.pkl", "rb")
)

print("Model loaded successfully!")


# 2. Load your existing transformed test data
test_arr = np.load(
    "/Users/hemanthhs/Documents/NETWORK SECURITY/Artifacts/08_08_2026_01_26_10/data_transformation/transformed/test.npy"
)

# Separate X and y
X_test = test_arr[:, :-1]
y_test = test_arr[:, -1]


# 3. Get probability of phishing (class 1)
y_prob = model.predict_proba(X_test)[:, 1]


# 4. Try different thresholds
for threshold in [0.5, 0.6, 0.7, 0.8, 0.9]:

    y_pred = (y_prob >= threshold).astype(int)

    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print(
        f"Threshold: {threshold} | "
        f"Precision: {precision:.4f} | "
        f"Recall: {recall:.4f} | "
        f"F1: {f1:.4f}"
    )