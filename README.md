## AI 기반 태양광 패널 이상 탐지 시스템 

**1. 소개**
- 태양광 패널에 대한 이상 상태를 탐지하기 위한 시스템 
- 객체 탐지 모델, 아두이노, Gemini 기술을 활용 
- Flask를 통해 만들어진 웹페이지를 통해 시스템을 구현
- 객체 탐지 모델에는 YOLO26 nano를 사용


<img width="2522" height="1350" alt="Image" src="https://github.com/user-attachments/assets/1d4ce90b-5077-4bed-b724-f07aa0dbd542" />

**2. 기능** 
- 이미지 탐지 
    * 태양광 패널에 대한 이미지를 한장 또는 여러 장으로 업로드(폴더 째로도 가능)
    * 업로드를 하면 객체 탐지 모델이 자동으로 태양광 패널의 상태를 탐지
    * 탐지한 결과에 따라 아두이노가 반응하며 정상이면 LED가 파랑색 불빛을 냄 
        * 이상 탐지 클래스이면 LED가 빨간색 불빛을 내며 부저가 울림 
    * 탐지된 이미지 중에 분석을 하고 싶을 때 Gemini 분석을 통해 분석이 가능
        * 분석 결과에는 탐지 결과에 대한 상세 설명과 문제점, 대응방안, 중 • 장기 관리 및 예방 전략을 알려줌 

<p align="center">
<img width="635" height="260" alt="Image" src="https://github.com/user-attachments/assets/fce8fda1-2de8-4266-999c-b7bafc5e8331" />

<img width="664" height="271" alt="Image" src="https://github.com/user-attachments/assets/3ebdc7c5-6bf2-43cd-8a33-3d152a67fd76" />
</p>

- 실시간 탐지 
    * 카메라 웹캠을 통해 실시간으로 탐지 
    * 탐지한 결과에 따라 아두이노가 반응하며 정상이면 LED가 파랑색 불빛을 냄    
        * 이상 탐지 클래스이면 LED가 빨간색 불빛을 내며 부저가 울림
    * 24시간 아두이노 부저가 울리면 밤 환경시 소음으로 번질 수 있음 
        * 키보드 기능을 통해 아두이노 기능을 정지 밀 재개할 수 있음 (S: STOP, R: RESUME)

<p align="center">
<img width="709" height="239" alt="Image" src="https://github.com/user-attachments/assets/6cec956d-d9a9-46f1-a8d3-cf1d2b76bd49" />
</p>