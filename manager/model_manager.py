from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import xgboost as xgb

class ModelManager:
    """
    데이터를 바탕으로 머신러닝 모델을 관리하고 평가하는 클래스입니다.

    Attributes:
        data_df (DataFrame): 학습에 사용될 데이터 프레임.
        model (xgb.XGBClassifier): 훈련된 모델들을 저장하는 딕셔너리.
        prediction (array): 모델의 예측 결과.
    """
    
    def __init__(self, data_df):
        """
        모델 관리자를 초기화하고, 주어진 데이터 프레임을 바탕으로 모델 훈련 준비를 합니다.

        Args:
            data_df (DataFrame): 모델 훈련에 사용될 데이터.
        """
        self.data_df = data_df.copy()
        self.model = None
        self.prediction = None

    def train_test_split(self):
        """
        데이터를 학습용과 테스트용으로 분할합니다. 테스트 셋은 전체 데이터의 20%로 설정됩니다.
        """
        X = self.data_df[['outdoor_temperature', 'outdoor_humidity', 'temperature', 'humidity', 'people_count', 'time_in_minutes']]
        y = self.data_df['air_conditioner']
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    def train_xgboost(self):
        """
        XGBoost 모델을 훈련합니다. 튜닝된 하이퍼파라미터를 사용합니다.
        """
        self.model = xgb.XGBClassifier(
            use_label_encoder=False,
            eval_metric='logloss',
            n_estimators=300,
            max_depth=5,
            learning_rate=0.1,
            colsample_bytree=0.5
        )
        self.model.fit(self.X_train, self.y_train)
        self.prediction = self.model.predict(self.X_test)

    def evaluate_model(self):
        """
        모델을 평가하여 모델의 정확도를 계산합니다.

        Returns:
            float: 모델의 정확도.
        """
        return accuracy_score(self.y_test, self.prediction)
