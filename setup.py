from plotly.graph_objs import *
import streamlit as st
import numpy as np
import pandas as pd
import pandas.plotting as pdplt
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
import seaborn as sns
import plotly.express as pl
from plotly.subplots import make_subplots
from sklearn.metrics import confusion_matrix, auc, roc_auc_score, roc_curve
import matplotlib.pyplot as plt
import webbrowser
import time
from bokeh.models.widgets import Div
import time
import pickle

# Global Variables

pickled_df = pd.DataFrame(pd.read_csv("esp8266_readings - Sheet1.csv")).to_pickle("./uncleaned_df")
unpickled_df = pd.read_pickle("./uncleaned_df")

# convert from 12 hr to 24 hr time


def storeCleanData():
    raw_df = unpickled_df.rename(columns={
    'Event Name': 'Event_Name', 
    'Value1': 'Digital_Button', 
    'Value2':'Photoresistor', 
    'Value3':'Temp; Humidity'
    })

    #clean date column
    times = []
    date_df = pd.DataFrame(raw_df['Date'])
    date_df = date_df['Date'].str.split('at', expand = True)
    for val in date_df[1].iteritems():
        if str(val[1][-2:]) == 'AM':
            times.append(int(val[1][0:3]))
        elif str(val[1][-2:]) == 'PM':
            times.append(int(val[1][0:3]) + 12)
    
    

    # drop rows where humidity sensor was not activated
    

    #clean temp: humidity column
    raw_df[['Temp', 'Humidity']] = raw_df['Temp; Humidity'].str.split(';', expand=True)
    time_df = pd.DataFrame(times)
    time_df = time_df.rename(columns={0: 'Hour'})
    # OHE hours
    time_df = pd.get_dummies(time_df.astype(str))
    cols = time_df.columns.tolist() # get name of columns in a list
    # now, reorganize those names 
    cols = ['Hour_1', 'Hour_2', 'Hour_3', 'Hour_4', 'Hour_5', 'Hour_6', 'Hour_7', 'Hour_8', 'Hour_9', 'Hour_10', 'Hour_11', 'Hour_12', 'Hour_13', 'Hour_14', 'Hour_15', 'Hour_16', 'Hour_17', 'Hour_18', 'Hour_19', 'Hour_20', 'Hour_21', 'Hour_22', 'Hour_23', 'Hour_24']
    # now, use the reorganized column names to reorganize your columns
    time_df = time_df[cols]
    #rearrange indeces and concat time to initial df
    raw_df.index = np.arange(0, len(raw_df))
    df = pd.concat([raw_df, time_df], axis =1)
    #drop unnecessary columns
    df = df.drop(columns=['Date', 'Temp; Humidity', 'Event_Name'])
    df = df.drop([0, 1, 2, 3, 4, 5, 6, 7, 8],axis = 0)
    #normalization
    df['Photoresistor'] = df['Photoresistor'].astype(int)/df['Photoresistor'].max().astype(int)
    df['Temp'] = df['Temp'].astype(float)/df['Temp'].astype(float).max()
    df['Humidity'] = df['Humidity'].astype(float)/df['Humidity'].astype(float).max()
    r, c = df.shape
    pickle_data = df.to_pickle("./cleaned_df")
storeCleanData()

unpickled_clean = pd.read_pickle('./cleaned_df')




st.title("Classification Models with Data Collected from an ESP8266 Board, Photoresistor, Digital Button, and dht Sensor")

part_selector = st.sidebar.selectbox(label= "Project Outline", options= ["Part I. Data Analysis, Cleaning, and Viz", "Part II. Implementing Models", "Part III. Try Out Your Own Data"])

if part_selector == "Part I. Data Analysis, Cleaning, and Viz":
    url = "https://docs.google.com/spreadsheets/d/1F-UPZf3je1x4M8ryp34OCe29E-CagCrUn9mFzsyfmJE/edit?usp=sharing"
    st.write("A sample of the data can be found here: \n")
    st.markdown("[Link To Dataset](https://docs.google.com/spreadsheets/d/1F-UPZf3je1x4M8ryp34OCe29E-CagCrUn9mFzsyfmJE/edit?usp=sharing)")
    st.write("A previous write-up on this experiment can be found here: \n")
    st.markdown("[Link to Article](https://medium.com/@danielmurph8/esp8266-nodemcu-weekend-project-4812d7636ad)")




    st.header("**Part 1. Data Pre-Clean vs. Post-Clean**")
    """
    The data used to predict whether I am in my room or not includes: 
    """
    """
    1. **_Photoresistor_** data that reports the amount of light in the surrounding area (the higher the luminosity, the lower the resistance)
    """
    """
    2. **_DHT-sensor_** data that reports the temperature and humidity in the room
    """
    """
    3. **_Digital sensor_** data (1's and 0's... 1 = im in my room, 0 = im not in my room) and 
    """
    """
    4. **_Dates_** (used to incorporate time series into the model)
    """
    st.subheader("**_Part A. Pre-Clean_**")
    st.dataframe(unpickled_df.head(15))
    r, c = unpickled_df.shape
    st.text("Shape of Initial Data: {}".format(unpickled_df.shape) + ". There are " + str(r) + " rows and " + str(c) + " columns.")
    """
    We will need to: \n
    1. Rename Columns. What are Value1? Value2? etc... \n
    2. By taking a look at Value3, we see that the first 9 rows are different from the following 5382. We'll want to remove these or determine a representative placeholder for the missing values. \n
    3. Normalize columns 3 (Value1), 4 (Value2), and 5 (Value3) \n
    3. Split the "Date" column at 'at' and retrieve the hour for each row. Then, we will one-hot-encode the hours.
    """
    r, c = unpickled_clean.shape
    st.subheader("**_Part B. Post-Clean_**")
    bar = st.progress(0)
    iters = st.empty()
    action_list = ['Cleaning Data', 'Building KNN Model', 'Building SVC Model', 'Creating Visualizations']
    for i in np.arange(1, 5):
        iters.text("Building Task #{0} : {1}".format(i, action_list[i-1]))
        bar.progress(int(i)*25)
        time.sleep(.75)


    st.dataframe(unpickled_clean.head(15))
    st.text("Shape of Cleaned Data: {}".format(unpickled_clean.shape) + ". There are " + str(r) + " rows and " + str(c) + " columns.")


if part_selector == "Part II. Implementing Models":
    st.header("**Part 2. Learn About, Use and Analyze Two ML Models:**")
    x = unpickled_clean.drop(columns=["Digital_Button"])
    y = unpickled_clean['Digital_Button']
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = .3, random_state = 42)

    st.subheader("First, Choose Your Model: ")
    model = st.selectbox(
        "Model Selection:",
        ["K-Nearest Neighbors", "Support Vector Classifier"]
        )

    if model == "K-Nearest Neighbors":
        st.write("KNN is a supervised machine learning algorithm that can be used for both classification and regression tasks. In this example, we will be using it for classification (to answer the question 'am I in my room (1) or not (0)?'). Simply put, KNN uses feature similarity to predict the values of new data points. The intuition behind this model is that things with **similar** feature values tend to be **similar**.")
        st.write('The distance between points is calculated using the following equation: ')
        st.latex("d(x,y) = d(y,x) = (\sum_{i=1}^{n} \\big|{x_i - y_i}\\big|^p)^\\frac{1}{p}")
        st.write("We can change p to calculate the distance in different ways:")
        st.subheader("1. Manhattan Distance (p = 1)")
        st.write("This is useful for calculating the distance between two points on a grid-like path (like city blocks)")
        st.latex('d(x, y) = d(y, x) = \sum_{i=1}^{n} \\big|{x_i - y_i}\\big|')
        st.subheader("2. Euclidean Distance (p = 2)")
        st.write("This is useful for calculating the distance between points in a plane (Pythagorean Theorem)")
        st.latex('d(x, y) = d(y, x) = \sum_{i=1}^{n} \sqrt{(x_i + y_i)^2}')
        st.subheader("3. Chebychev Distance (p = ∞)")
        st.write("This is useful for finding where the difference between two vectors is the maximum")
        st.latex('d(x, y) = d(y, x) = \max(\\big|x_i - y_i\\big|)')
    elif model == "Support Vector Classifier":
        st.write("Support Vector Machine is an algorithm that finds a hyperplane in an n-dimensional space (with n being the number of features in your dataset). This hyperplane acts as a decision boundary that distinctly classifies data points. In Linear Regression models, the model is optimized when **w*** and **b*** create a line with a *minimized* loss function (typically MSE or RMSE). In contrast, SVM models are optimized once the distance between the decision boundary and the closest data point (the **margin**) is *maximized*.")
        st.write("The margin can be represented in functional and geometric terms: ")
        st.subheader("1. Functional Margin")
        st.write('Returns a number that tells us whether a data point, x, is properly classified or not. If the prediction is the same as the actual, the formula will return +1. If the predicted is different from the actual, the formula will return -1.')
        st.latex("\gamma_i = y_i(\omega^T x_i +  b)")
        st.subheader("2. Geometric Margin")
        st.write("This is the euclidean distance between a data point, x, and the hyperplane.")
        st.latex("\hat{\gamma_i} = \\frac{\gamma_i}{\\big|\\big|\omega\\big|\\big|}")
    st.subheader("Second, Choose Your Parameters:")
    st.text("If you need help, click here: ")
    btn = st.button("Run a Grid Search")
    # @st.cache(show_spinner=True, suppress_st_warning=True, hash_funcs={st.DeltaGenerator.DeltaGenerator: lambda _ : None})
    if btn & (model == "K-Nearest Neighbors"):
        param_grid = {
                "n_neighbors" : [5, 10, 15],
                "weights" : ['uniform', 'distance'],
                'algorithm' : ['auto', 'ball_tree', 'kd_tree', 'brue']
            }
        gs_KNN = GridSearchCV(estimator=KNeighborsClassifier(), param_grid=param_grid, scoring='accuracy', cv=5, n_jobs=-1)
        gs_KNN.fit(x_train, y_train)
        best_parameters = gs_KNN.best_params_
        df_for_pickling = pd.DataFrame(best_parameters, index=[0])
        pickled_gs = df_for_pickling.to_pickle("./gridSearchDataKNN")
        st.write("The parameters that lead to the highest accuracy are: ")
        st.table(pd.read_pickle("./gridSearchDataKNN"))
        
    elif btn & (model == "Support Vector Classifier"):
        param_grid = {
                'kernel':['linear', 'poly', 'rbf', 'sigmoid'],
                'degree': [2, 3, 4],
                'gamma': ['scale', 'auto']

            }
        gs_SVC = GridSearchCV(estimator=SVC(), param_grid=param_grid, scoring="accuracy", cv=3, n_jobs=-1)
        gs_SVC.fit(x_train, y_train)
        best_parameters = gs_SVC.best_params_
        df_for_pickling = pd.DataFrame(best_parameters, index=[0])
        pickled_gs = df_for_pickling.to_pickle("./gridSearchDataSVC")            
        st.write("The parameters that lead to the highest accuracy are: ")
        st.table(pd.read_pickle("./gridSearchDataSVC"))


    if model == "K-Nearest Neighbors":        
        algo = st.selectbox(
            "Algorithm to computer nearest neighbor: ",
            ["ball_tree", "kd_tree", "brute", "auto"]
        )
        neighbors = st.selectbox(
            "Number of Neighbors to use:",
            [5, 10, 15, 20, 25]
        )
        w = st.selectbox(
            "Weight function",
            ["uniform", "distance"]
        )
        knn_clf = KNeighborsClassifier(n_neighbors=neighbors, algorithm=algo, n_jobs=-1, weights=w)
        knn_clf.fit(x_train, y_train)
        preds_knn = knn_clf.predict(x_test)
        results = pd.DataFrame(
        { "Actual": y_test,
            "Predicted": preds_knn
        }
        )
        score = knn_clf.score(x_test, y_test)
        st.write(score)
    elif model == "Support Vector Classifier":
        deg = st.selectbox(
            "Degree of Polynomial: ",
            ["2","3", "4"]
        )
        gam = st.selectbox(
            "Gamma, the Kernel Coefficient",
            ["scale", "auto"]
        )
        kern = st.selectbox(
            "Kernel Type used in Algorithm:",
            ["linear", "poly", "rbf", "sigmoid"]
        )

        svc_clf = SVC(kernel= kern, degree = int(deg), random_state= 42, gamma=gam)
        svc_clf.fit(x_train, y_train)
        y_preds_svm = svc_clf.predict(x_test)
        results = pd.DataFrame({
            "Actual": y_test,
            "Predicted": y_preds_svm
        })
        score = svc_clf.score(x_test, y_test)
        st.write(score)
    else:
        unknown_input = []
        unknown_input.append(model)
        st.write("{}".format(model) + " is not available yet, coming soon (:")

    st.subheader("Lastly, choose the visualizations to build:")


    def return_visualization():
        if model == "K-Nearest Neighbors":
            viz_selector = st.selectbox(
                "Choose your visualization:",
                ["Confusion Matrix", "Test Accuracy Vs. # of Neighbors", "ROC Curve"]
            )
            # if viz_selector == "Boxplot":
            #     fig, ([ax1, ax2], [ax3, ax4]) = plt.subplots(2, 2, figsize=[8, 6])
            #     plt1 = sns.boxplot(data= df, y="Photoresistor", ax = ax1)
            #     plt2 = sns.boxplot(data= df, y="Temp", ax=ax2)
            #     plt3 = sns.boxplot(data= df, y="Humidity", ax=ax3)
            #     plt4 = sns.boxplot(data=df, y="Digital_Button", ax=ax4)

            #     return st.plotly_chart(fig)
            if viz_selector=="Test Accuracy Vs. # of Neighbors":
                num_neighbors = st.selectbox(
                    "Choose Range for Number of Neighbors",
                    [[5, 10, 15, 20, 25], [10, 20,30, 40, 50]]
                )
                accuracy_scores = []
                for i in num_neighbors:
                    knn_clf2 = KNeighborsClassifier(n_neighbors=i, n_jobs=-1)
                    knn_clf2.fit(x_train, y_train)
                    preds = knn_clf2.predict(x_test)
                    score = knn_clf2.score(x_test, y_test)
                    accuracy_scores.append(score)
                
                fig = pl.line(x=num_neighbors, y=accuracy_scores, hover_name = accuracy_scores)
                fig.update_layout(title="Accuracy for {} Neighbors".format(num_neighbors), xaxis_title = "Number of Neighbors", yaxis_title = "Accuracy (0 - 1.0)")
                return st.plotly_chart(fig)
            elif viz_selector=="Confusion Matrix":
                c_mat = pd.crosstab(preds_knn, y_test, rownames=["True"], colnames=["False"])
                st.write(c_mat)
                fig = pl.imshow(c_mat, labels=dict(
                    x = 'Testing Data',
                    y = 'Predicted Data'
                ), x= ["False", "True"], y=["False", "True"])
                fig.update_xaxes(side = "top")
                return st.plotly_chart(fig)
            elif viz_selector == "ROC Curve":
                fp_rate, tp_rate, _ = roc_curve(y_test, preds_knn)
                plt.plot(fp_rate, tp_rate, color = "navy")
                plt.plot([0, 1], [0, 1], linestyle='-', color = "lightblue")
                plt.xlim=[0.0, 1.0]
                plt.ylim=[0.0, 1.25]
                plt.xlabel("False Positive Rate")
                plt.ylabel("True Positive Rate")
                plt.title("ROC Curve for KNN Model")
                plt.legend(["ROC Curve", "Line with slope 1"], loc = "lower right")
                st.pyplot()

        if model == "Support Vector Classifier":
            viz_selector = st.selectbox(
                "Choose your visualization for {}: ".format(model),
                ["Confusion Matrix", "Test Accuracy Vs. Kernel", "ROC Curve"]
            )
            if viz_selector == "Confusion Matrix":
                c_mat = pd.crosstab(y_preds_svm, y_test, colnames= ['False'], rownames=['True'])
                st.write(c_mat)
                fig = pl.imshow(c_mat, 
                labels=dict(x="Testing Data", y="Predicted Data"),
                        x=['False', 'True'],
                        y=['False', 'True']
                )
                fig.update_xaxes(side = "top")

                return st.plotly_chart(fig) 
            elif viz_selector == "Test Accuracy Vs. Kernel":
                svc_kern1 = SVC(kernel='linear')
                svc_kern2 = SVC(kernel='poly')
                svc_kern3 = SVC(kernel='rbf')
                svc_kern4 = SVC(kernel='sigmoid')


                fit_m1 = svc_kern1.fit(x_train, y_train)
                fit_m2 = svc_kern2.fit(x_train, y_train)
                fit_m3 = svc_kern3.fit(x_train, y_train)
                fit_m4 = svc_kern4.fit(x_train, y_train)

                data_for_chart = dict(
                    {
                        'linear': svc_kern1.score(x_test, y_test),
                        'poly': svc_kern2.score(x_test, y_test),
                        'rbf': svc_kern3.score(x_test, y_test),
                        'sigmoid': svc_kern4.score(x_test, y_test)
                    }
                )
                df = pd.DataFrame(data_for_chart, index=[0], columns= ['linear', 'poly', 'rbf', 'sigmoid'])
                fig = pl.bar(df, x = ['linear', 'rbf', 'sigmoid', 'poly'], y = [svc_kern1.score(x_test, y_test), 
                svc_kern3.score(x_test, y_test), svc_kern4.score(x_test, y_test), svc_kern2.score(x_test, y_test)], 
                color=[svc_kern1.score(x_test, y_test), svc_kern3.score(x_test, y_test), svc_kern4.score(x_test, y_test), svc_kern2.score(x_test, y_test)],
                labels={
                    'x':'Kernel Type',
                    'y': 'Accuray (estimator.score())'
                })
                fig.update_layout(title="Accuracy Score vs. Kernel Type")
                return st.plotly_chart(fig)
            elif viz_selector == "ROC Curve":
                fp_rate, tp_rate,  _ = roc_curve(y_test, y_preds_svm)
                plt.plot(fp_rate, tp_rate, color = "navy")
                plt.plot([0, 1], [0, 1], color = "lightblue", linestyle="-")
                plt.legend(["ROC Curve", "Line with slope 1"])
                plt.xlabel("False Positive Rate")
                plt.ylabel("True Positive Rate")
                plt.title("ROC Curve for SVC Model")
                st.pyplot()



    return_visualization()

if part_selector == "Part III. Try Out Your Own Data":
    st.header("**Part 3. Input your own data and check out the results:**")
    st.write("It is recommended you look at the values in the cleaned dataframe to aid in helping you select your inputs.")

    st.subheader("First, Input your data:")


    photo_val = st.text_input("Photoresistor Value: ", value="Example: .4541")
    temp_val = st.text_input("Temperature Value: ", value='Example: .7368')
    humid_val = st.text_input("Humidity Value: ", value='Example: .8923')
    hour_num = st.selectbox(
        "Hour Value: ",
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    )
    hour_timeframe = st.selectbox(
        "AM or PM?",
        ["AM", "PM"]
    )
    st.subheader("Now, select your model:")
    model_selector = st.selectbox(
        "Model Selector:",
        ["K-Nearest Neighbors", "Support Vector Classifier"]
    )
    def hourConverterTwo(timeframe, hour):
        if timeframe == "PM":
            final_time = int(hour) + 12
            return int(final_time)
        else:
            return int(hour)

    @st.cache(show_spinner=True)
    def transform_user_input(photo, temp, humidity, hour):
        hour_val = [0 if i!= hourConverterTwo(hour_timeframe, hour_num) else 1 for i in range(1, 25)]
        input_data_array = np.array([float(photo_val), float(temp_val), float(humid_val)]+[i for i in hour_val])
        return input_data_array

    confirmation_button = st.button("Run Model and Predict")

    @st.cache(show_spinner=True, hash_funcs={st.DeltaGenerator.DeltaGenerator: lambda _: None})
    def buildModel(model_name, input_data):
        x = unpickled_clean.drop(columns=["Digital_Button"])
        y = unpickled_clean['Digital_Button']
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = .3, random_state = 42)
        if model_name == "K-Nearest Neighbors":
            knn_clf = KNeighborsClassifier(algorithm='auto', n_neighbors=5, weights='distance', n_jobs=-1)
            knn_clf.fit(x_train, y_train)
            preds = knn_clf.predict(input_data.reshape(1, -1))
        elif model_name == "Support Vector Classifier":
            svc_clf = SVC(degree=4, gamma='scale', kernel='poly')
            svc_clf.fit(x_train, y_train)
            preds = svc_clf.predict(input_data.reshape(1, -1))
        return st.dataframe(preds)
    if confirmation_button:
        buildModel(model_selector, transform_user_input(photo= photo_val, temp=temp_val, humidity= humid_val, hour=hour_num))

