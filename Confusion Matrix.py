# Generate and Evaluate Confusion Matrix
import numpy as np
from sklearn.metrics import confusion_matrix
import random
import pandas as pd

def sample_dataframe(df, column_name):
    # Get indices of positive and negative samples
    pos_indices = df.index[df[column_name] == 'Positive'].tolist()
    neg_indices = df.index[df[column_name] == 'Negative'].tolist()

    # Sample equal number of positive and negative samples
    num_samples = min(len(pos_indices), len(neg_indices))
    pos_sample_indices = random.sample(pos_indices, num_samples)
    neg_sample_indices = random.sample(neg_indices, num_samples)

    # Combine positive and negative sample indices
    sample_indices = pos_sample_indices + neg_sample_indices

    # Get predicted and true labels as numpy arrays
    predicted_labels = np.array(df.loc[sample_indices, 'predicted']) #you will need to adjust this for predicted
    true_labels = np.array(df.loc[sample_indices, 'actual']) #you will need to adjust this for annotated

    # Return predicted and true label arrays
    return predicted_labels, true_labels

def calculate_confusion_matrix(true_labels, predicted_labels):
    # Get the unique class labels
    classes = np.unique(true_labels)

    # Calculate the confusion matrix
    conf_matrix = confusion_matrix(true_labels,predicted_labels, labels=classes)

    # Return the confusion matrix as a NumPy array
    return conf_matrix

def evaluate_confusion_matrix(conf_matrix):
    # Calculate metrics from the confusion matrix
    tn = conf_matrix[0, 0]
    fp = conf_matrix[0, 1:].sum()
    fn = conf_matrix[1:, 0].sum()
    tp = conf_matrix[1:, 1:].sum()
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1_score = 2 * precision * recall / (precision + recall)

    # Print the metrics
    print("True positives: {}".format(tp))
    print("True negatives: {}".format(tn))
    print("False positives: {}".format(fp))
    print("False negatives: {}".format(fn))
    print("Accuracy: {:.2f}".format(accuracy))
    print("Precision: {:.2f}".format(precision))
    print("Recall: {:.2f}".format(recall))
    print("F1 score: {:.2f}".format(f1_score))
    return {"accuracy": float(accuracy), "precision": float(precision),"recall" : float(recall),"f1 score" :float(f1_score)}


#Note: the model is a unweighted confusion matrix, user should have already sampled x number of postive and negative accordingly, slicing them and thus retrieving the labels
    
# Example true and predicted labels
cmdf = pd.read_csv("Labelled Human Confusion Matrix Labelling.csv")
cmdf.dropna(inplace=True)
cmdf["Human Sentiment Labelling"].dropna(axis=0,inplace=True)
true_labels = list(cmdf["Human Sentiment Labelling"]) #(annotated sentiment), numpy array input
predicted_labels = list(cmdf["Sentiment"]) #t(predicted sentiment), numpy array input
true_labels = np.array(true_labels)
predicted_labels =np.array(predicted_labels)
true_labels[true_labels=="p"] = "POSITIVE"
true_labels[true_labels=="n"] = "NEGATIVE"
print(true_labels)
print(predicted_labels)
# Calculate the confusion matrix
conf_matrix = calculate_confusion_matrix(true_labels=true_labels , predicted_labels=predicted_labels)
# Print the confusion matrix
print(conf_matrix)
outdict = evaluate_confusion_matrix(conf_matrix)
outdf = pd.DataFrame([outdict])


cmdf["Human Specification Labelling"].dropna(axis=0,inplace=True)
a = cmdf["Human Specification Labelling"].value_counts()
classification_accuracy = a["YES"]/sum(a)
outdf = pd.concat([outdf,pd.DataFrame([classification_accuracy],columns=["classification accuracy"])] , axis=1)
outdf.to_csv("evaluation scores.csv")
accuracydf = pd.read_csv("evaluation scores.csv")
class_acc ={"Classification Accuracy" :accuracydf["classification accuracy"][0]}
sent_acc = {"Sentiment Accuracy" : accuracydf["accuracy"][0]}
print(class_acc,sent_acc)
class_acc.update(sent_acc)
accuracy = class_acc
print(accuracy)