from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score
import xgboost as xgb

class ModelManager:
    """
    데이터를 바탕으로 머신러닝 모델을 관리하고 평가하는 클래스입니다.

    Attributes:
        data_df (DataFrame): 학습에 사용될 데이터 프레임.
        models (dict): 훈련된 모델들을 저장하는 딕셔너리.
        predictions (dict): 모델별 예측 결과를 저장하는 딕셔너리.
    """
    
    def __init__(self, data_df):
        """
        모델 관리자를 초기화하고, 주어진 데이터 프레임을 바탕으로 모델 훈련 준비를 합니다.

        Args:
            data_df (DataFrame): 모델 훈련에 사용될 데이터.
        """
        self.data_df = data_df
        self.data_df['air_conditional'] = self.data_df['air_conditional'].map({'close': 0, 'open': 1}) # air_conditional의 값이 close면 0, open이면 1로 변경
        self.models = {}
        self.predictions = {}

    def train_test_split(self):
        """
        데이터를 학습용과 테스트용으로 분할합니다. 테스트 셋은 전체 데이터의 20%로 설정됩니다.
        """
        X = self.data_df[['outdoor_temperature', 'outdoor_humidity', 'temperature', 'humidity', 'people_count', 'time_in_minutes']]
        y = self.data_df['air_conditional']
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    def train_logistic_regression(self):
        """
        로지스틱 회귀 모델을 훈련합니다. 데이터는 표준화 후 로지스틱 회귀 알고리즘으로 학습시킵니다.
        """
        model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
        # model = LogisticRegression()
        model.fit(self.X_train, self.y_train)
        self.models['LogisticRegression'] = model
        self.predictions['LogisticRegression'] = model.predict(self.X_test)

    def train_random_forest(self):
        """
        랜덤 포레스트 모델을 훈련합니다. 트리의 개수는 100개로 설정되며, 랜덤 시드는 42입니다.
        """
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(self.X_train, self.y_train)
        self.models['RandomForest'] = model
        self.predictions['RandomForest'] = model.predict(self.X_test)

    def train_xgboost(self):
        """
        XGBoost 모델을 훈련합니다. 라벨 인코더는 사용하지 않으며, 평가 메트릭으로 'logloss'를 사용합니다.
        """
        model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
        model.fit(self.X_train, self.y_train)
        self.models['XGBoost'] = model
        self.predictions['XGBoost'] = model.predict(self.X_test)

    def evaluate_models(self):
        """
        저장된 모델들을 평가하여 각 모델의 정확도를 계산합니다.

        Returns:
            dict: 모델 이름을 키로 하고 정확도를 값으로 하는 딕셔너리.
        """
        accuracies = {}
        for name, prediction in self.predictions.items():
            accuracies[name] = accuracy_score(self.y_test, prediction)
        return accuracies
