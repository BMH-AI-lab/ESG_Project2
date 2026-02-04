## AI 기반 태양광 패널 이상 탐지 시스템 

**1. 소개**
- 태양광 패널에 대한 이상 상태를 탐지하기 위한 시스템 
- 객체 탐지 모델, 아두이노, Gemini 기술을 활용 
- Flask를 통해 만들어진 웹페이지를 통해 시스템을 구현

<p align="center">
  <img
  src="https://github.com/user-attachments/assets/fa77ac9f-d432-4a7c-861f-1152fb3af9c0"
    width="2522"
    height="1350"
    alt="Image"
  />
  <br>
  <sub><b><h3>Solar AI</b></sub>
</p>


**2.모델 학습** 
- Google Colab에서 모델 학습을 하였음 
- 객체 탐지 모델에는 YOLO26 nano를 사용(YOLO12 모델 학습도 했음)
- 하이퍼 파라미터는 YOLO26에서 주는 기본 파라미터를 사용 
- 모델 학습 코드 
```python

from ultralytics import YOLO

# Load a pretrained YOLO26n model
model = YOLO("/content/ultralytics/ultralytics/cfg/models/26/yolo26n.yaml")
#model = YOLO("C:/ESG_Project2/yolov26n_train_result/weights/last.pt")

# Train the model on the COCO8 dataset for 100 epochs
train_results = model.train(
    data="C:/ESG_Project2/SP_dataset/data.yaml",  # Path to dataset configuration file
    epochs=100,  # Number of training epochs
    imgsz=640,  # Image size for training
    device=0,
    # 학습이 중단 되면 써야 되는 코드
    # resume=True,

    # 학습 결과 저장
    project="C:/ESG_Project2/yolov26n_train_result/",
    name="yolov26n_train_result",
    exist_ok=True
)


```

**3. 이미지 및 실시간 탐지 모듈** 
- 아두이노 기술 활용 
- 객체 탐지 모델에서 나오는 탐지 결과에 따라 반응
    - 정상 태양광 패널이면 LED가 파랑색 불빛을 냄 
    - 이상 탐지 관련 정상 태양광 패널이면 LED가 빨간색 불빛을 내며 부저가 울림 

<p align="center">
<img width="646" height="324" alt="Image" src="https://github.com/user-attachments/assets/0247f35e-5cee-4db2-ab0a-9517b21c513a" />
</p>

<p align="center">
<img width="646" height="324" alt="Image" src="https://github.com/user-attachments/assets/47168521-fe2d-4c96-a398-e9183df04945" />
</p>

**4.  태양광 패널 이상 탐지 시스템 기능** 
- 이미지 탐지 
    * 태양광 패널에 대한 이미지를 한장 또는 여러 장으로 업로드(폴더 째로도 가능)
    * 업로드를 하면 객체 탐지 모델이 자동으로 태양광 패널의 상태를 탐지
        * 정상 태양광 패널이면 LED가 파랑색 불빛을 냄 
        * 이상 탐지 관련 정상 태양광 패널이면 LED가 빨간색 불빛을 내며 부저가 울림 
    * 탐지된 이미지 중에 분석을 하고 싶을 때 Gemini 분석을 통해 분석이 가능
        * 분석 결과에는 탐지 결과에 대한 상세 설명과 문제점, 대응방안, 중 • 장기 관리 및 예방 전략을 알려줌 

<p align="center">
<img width="640" height="640" alt="Image" src="https://github.com/user-attachments/assets/face4815-91a2-471e-8ddc-13ed9944c414" />
</p>

- 실시간 탐지 
    * 카메라 웹캠을 통해 실시간으로 탐지 
    * 탐지한 결과에 따라 아두이노가 반응하며 정상이면 LED가 파랑색 불빛을 냄    
        * 이상 탐지 클래스이면 LED가 빨간색 불빛을 내며 부저가 울림
    * 24시간 아두이노 부저가 울리면 밤 환경시 소음으로 번질 수 있음 
        * 키보드 기능을 통해 아두이노 기능을 정지 하거나 재개할 수 있음 (S: STOP, R: RESUME)

<p align="center">
<img width="709" height="239" alt="Image" src="https://github.com/user-attachments/assets/6cec956d-d9a9-46f1-a8d3-cf1d2b76bd49" />
</p>