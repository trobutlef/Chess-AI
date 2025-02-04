# backend/model/train_model.py
import numpy as np
from tensorflow.keras.utils import to_categorical
from data_preprocessing import extract_features_labels, save_move_labels_dict
from model import create_chess_model
from sklearn.model_selection import train_test_split
import os

# Directory containing PGN files
pgn_directory = '../data/'  # Adjust the path if necessary

# Initialize lists to collect features and labels from all files
features_list = []
labels_list = []

# Maximum number of samples to extract from each PGN file
max_samples_per_file = 10000  # Adjust based on your requirements

# Iterate over all files in the data directory
for filename in os.listdir(pgn_directory):
    if filename.endswith('.pgn'):
        pgn_file_path = os.path.join(pgn_directory, filename)
        print(f'Processing file: {pgn_file_path}')
        # Extract features and labels from the current PGN file
        features, labels = extract_features_labels(pgn_file_path, max_samples=max_samples_per_file)
        if features.size == 0 or labels.size == 0:
            print(f"No data extracted from file: {pgn_file_path}")
            continue
        features_list.append(features)
        labels_list.append(labels)

# Check if any data was collected
if not features_list or not labels_list:
    print("No data was extracted from any PGN files.")
    exit()

# Concatenate all features and labels from the list
features = np.concatenate(features_list, axis=0)
labels = np.concatenate(labels_list, axis=0)

# Convert labels to categorical
num_classes = len(set(labels))
labels_categorical = to_categorical(labels, num_classes=num_classes)

# Shuffle and split data into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(features, labels_categorical, test_size=0.1, random_state=42)

# Create the model
model = create_chess_model(num_classes)

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=5, batch_size=64)

# Save the trained model
model.save('chess_model.h5')

# Save the move labels dictionary
save_move_labels_dict('move_labels_dict.pkl')
