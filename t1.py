from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import pandas as pd

# Load the dataset to examine its structure and content
file_path = 'scrappingNewDf.csv'
data = pd.read_csv(file_path)

# Display the first few rows of the dataset to understand its structure
data.head()

# Selecting relevant numeric columns with sufficient non-null values
selected_columns = [
    'Year Of Publication', 'Frontal Offset Deformable Barrier', 'Whiplash Rear Impact', 
    'Lateral Impact', '18 months old child', '36 months old child', 'VRU Impact Protection', 
    'Crash Test Performance', 'Safety Features', 'CRS Installation Check', 'Speed Assistance', 
    'Electronic Stability Control', 'Seatbelt Reminder', 'Lane Support', 'AEB Inter-Urban', 
    'Head Impact', 'Pelvis Impact', 'Leg Impact'
]

# Extracting features (X) and target (y)
X = data[selected_columns]
y = data['rating']

# Handling missing values by imputing with the mean value for simplicity
imputer = SimpleImputer(strategy='mean')
X_imputed = imputer.fit_transform(X)

# Standardizing the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_imputed)

# Splitting data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Using Random Forest Classifier as a baseline model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Predicting on the test set
y_pred = model.predict(X_test)

# Calculating accuracy and generating classification report
accuracy = accuracy_score(y_test, y_pred)
classification_report_output = classification_report(y_test, y_pred)

print(f"Accuracy: {accuracy}")
print(classification_report_output)