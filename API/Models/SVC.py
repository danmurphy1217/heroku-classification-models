from sklearn import svm
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix
from Models.Data import X_train, X_test, y_train, y_test

class SVC:
    def __init__(self, params):
        self.params = params
    
    def buildModel(self, train_x, test_x, train_y, test_y, params = {"kernel" : "linear", "gamma" : "auto"}):
        """
        Builds a Support Vector Classification model and returns the following metrics:
            1. The models accuracy : percent correctly predicted divided by the total predictions made
            2. The models precision : TP / (TP + FP) where (TP + FP) -> The number of Positive guesses
            3. The models recall : TP / (TP + FN) where (TP + FN) -> True number of positives
            4. The models f1-score : 
            5. The models FP-rate : FP / (FP + TN) where (FP+FN) -> True number of negatives
            6. The models FN-rate : FN / (FN + TP) where (FN+TP) -> True number of positives

        Parameters
        ----------
        train_x : ( pandas dataframe )
            the training set of feature vectors
        test_x : ( pandas dataframe )
            the testing set of feature vectors
        train_y : ( pandas dataframe )
            the training set of target vectors
        test_y : ( pandas dataframe )
            the testing set of target vectors
        params : (dictionary)
            the parameters passed to the model.

        Returns
        ----------
        The metrics outlined in the summary above: Accuracy, Precision, Recall, F1-score, FP-Rate, and FN-Rate.        
        """
        def metrics(y_preds, y_true):
            """
            Compute and return the metrics for the model.

            Parameters
            ----------
            y_preds : (list / series / numpy array)
                the predicted values of the model
            y_true : (list / series / numpy array)
                the true values for the model

            Return
            ----------
            The accuracy, precision, recall, f1 score, FP-rate, and FN-rate
            """
            accuracy = clf.score(X_test, y_test)
            precision = precision_score(y_test, y_preds)
            recall = recall_score(y_test, y_preds)
            f1 = f1_score(y_test, y_preds)
            tn, fp, fn, tp = confusion_matrix(y_test, y_preds).ravel()
            FPR = fp/(fp+tn)
            FNR = fn/(fn+tp)
            return round(accuracy, 3), round(precision, 3), round(recall, 3), round(f1, 3), round(FPR, 3), round(FNR, 3) # recall + FNR = 1

        accepted_params = ["kernel", "gamma"]
        passed_params = [params.get(param) for param in accepted_params]
        if len(passed_params) == len(accepted_params):
            clf = svm.SVC(kernel = params.get("kernel"), gamma = params.get("gamma"))
            clf.fit(X_train, y_train)
            y_preds = clf.predict(X_test)
            #return the metrics
            accuracy, precision, recall, f1, fpr, fnr = metrics(y_preds, y_test)
            return {
                "accuracy" : accuracy,
                "precision" : precision,
                "recall" : recall,
                "f1" : f1,
                "False Positive Rate" : fpr,
                "False Negative Rate" : fnr
            }
        
        clf = svm.SVC() # no params specified
        clf.fit(X_train, y_train)
        y_preds = clf.predict(X_test)
        #return the metrics
        return metrics(y_preds, y_test)        

