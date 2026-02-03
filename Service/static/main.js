const video = document.getElementById("webcam");

if (video) {
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      video.srcObject = stream;
    })
    .catch(err => {
      alert("웹캠 접근 실패");
      console.error(err);
    });
}
