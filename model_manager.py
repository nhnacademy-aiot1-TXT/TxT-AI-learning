from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

from sklearn.metrics import accuracy_score
import xgboost as xgb

class ModelManager:
    def __init__(self, data_df):
        self.data_df = data_df
        self.data_df['air_conditional'] = self.data_df['air_conditional'].map({'close': 0, 'open': 1}) # air_conditional의 값이 close면 0, open이면 1로 변경
        self.models = {}
        self.predictions = {}

    def train_test_split(self):
        X = self.data_df[['outdoor_temperature', 'outdoor_humidity', 'temperature', 'humidity', 'people_count', 'time_in_minutes']]
        y = self.data_df['air_conditional']
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    def train_logistic_regression(self):
        model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
        # model = LogisticRegression()
        model.fit(self.X_train, self.y_train)
        self.models['LogisticRegression'] = model
        self.predictions['LogisticRegression'] = model.predict(self.X_test)

    def train_random_forest(self):
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(self.X_train, self.y_train)
        self.models['RandomForest'] = model
        self.predictions['RandomForest'] = model.predict(self.X_test)

    def train_xgboost(self):
        model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
        model.fit(self.X_train, self.y_train)
        self.models['XGBoost'] = model
        self.predictions['XGBoost'] = model.predict(self.X_test)

    def evaluate_models(self):
        accuracies = {}
        for name, prediction in self.predictions.items():
            accuracies[name] = accuracy_score(self.y_test, prediction)
        return accuracies
