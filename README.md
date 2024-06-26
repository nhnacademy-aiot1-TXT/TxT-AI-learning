# TxT-AI-learning

## 프로젝트 개요
현재 온도, 습도, 재실 인원에 따른 에어컨 ON/OFF 여부를 판별하는 AI 모델을 구현합니다. 머신러닝의 지도학습 방식을 사용하며, XGBoost를 최종 모델로 선택하여 높은 예측 정확도와 일관적인 성능을 가진 모델을 구현하는 것을 목표로 합니다.

## 주요 기능
1. InfluxDB에서 센서 데이터를 수집하고 전처리합니다.
2. 결측치를 처리하고, 이상치를 제거합니다.
3. XGBoost 알고리즘을 사용하여 에어컨 ON/OFF 여부를 예측하는 모델을 훈련합니다.
4. 훈련된 모델을 NHN Object Storage에 업로드하여 저장합니다.

## 파일 설명
- data_analysis.ipynb : 모델 구현을 위한 데이터 분석 파일
- main.py : 전체 프로세스를 실행하는 메인 파일
- config.py : 환경 변수를 로드하는 설정 파일
- manager/data_manager.py : InfluxDB에 데이터를 쿼리하고 전처리하는 클래스
- manager/model_manager.py : 모델을 훈련하고 평가하는 클래스
- utils/object_service.py : NHN Cloud Object Storage에 접근하여 모델 객체를 업로드하는 클래스
- utils/issue_token.py : NHN Cloud Object Storage에 접근하기 위한 인증 토큰을 발급받는 유틸리티 파일
- requirements.txt : 필요한 패키지 목록
- environment.yml : Conda 환경 설정 파일

## 데이터 분석
프로젝트 초기 단계에서 다양한 분류기를 사용하여 성능을 비교했습니다. 로지스틱 회귀, 랜덤 포레스트, XGBoost를 사용하여 데이터의 특성과 모델 성능을 평가한 후, 최종적으로 XGBoost를 선택했습니다.

#### 가설
- 가설 1 : 실내 온도와 습도가 특정 임계값을 초과할 때 에어컨이 켜질 가능성이 높다.
- 가설 2 : 재실 인원이 많을수록 에어컨이 켜질 가능성이 높다.
- 가설 3 : 실외 온도와 습도가 실내 에어컨 작동 여부에 영향을 미친다.

#### 구현 방식 : 머신러닝의 지도학습 방식

- 머신러닝 : 데이터를 기반으로 패턴을 학습하고 예측을 수행하는 인공지능의 분야입니다. 주어진 데이터를 사용하여 기능을 수행하고, 시간이 지남에 따라 그 기능이 점차적으로 향상됩니다. 머신러닝의 유형으로 지도학습, 비지도학습, 강화학습이 있습니다.
- 머신러닝의 지도학습 방식 선택 이유 : 현재 사용하려는 데이터는 ‘시간', '온도', '습도', '에어컨 ON/OFF' 상태입니다. 이 데이터는 구조화된 형태이며, 명확한 입력(온도, 습도)과 출력(에어컨 ON/OFF)이 정의되어 있어 지도 학습 방식이 적합함.

#### 분석에 사용한 지도학습 알고리즘

1. 로지스틱 회귀
    - 개념 : 독립변수의 선형 결합을 이용하여 사건의 발생 가능성을 예측하는데 사용되는 기법입니다. 에어컨ON/OFF와 같은 이진 분류 문제에 널리 사용되는 알고리즘입니다.
    - 선택이유 : 데이터 유형에 적합하며, 단순성과 해석 용이성이 높습니다.
2. 랜덤 포레스트
    - 개념 : 결정 트리의 앙상블 학습 방법으로, 여러 개의 결정 트리를 생성하고 그 결과를 평균 내어 최종 예측을 도출합니다.
    - 선택이유 : 높은 예측 정확도를 제공하며, 과적합을 방지하고 특성 중요도를 평가할 수 있습니다.
3. XG 부스트
    - 개념 : 그라디언트 부스팅을 기반으로 하는 머신러닝 알고리즘입니다. 그라디언트 부스팅은 여러 개의 약한 학습기를 순차적으로 학습시켜 결합함으로써 강한 예측 모델을 만드는 방법입니다.
    - 선택이유 : 높은 예측 정확도, 과적합 방지, 결측치 처리 기능 등 다양한 장점을 제공합니다.

