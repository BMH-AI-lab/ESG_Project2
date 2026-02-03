/****************************************************
 * Solar Panel Detection - Arduino Controller (DEBUG)
 *
 * Commands from Python (LINE based):
 *  - "N\n" : Normal
 *  - "A\n" : Any Anomaly
 *  - "O\n" : Off
 *
 * Hardware:
 *  - Blue LED  : D12
 *  - Red LED   : D13
 *  - Buzzer    : D8 (PASSIVE)
 ****************************************************/

#define LED_BLUE  12
#define LED_RED   13
#define BUZZER    8

char currentMode = 'O';

void setup() {
  Serial.begin(9600);

  pinMode(LED_BLUE, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  allOff();

  // 🔥 Python에서 기다리는 Ready 메시지
  Serial.println("ARDUINO READY");
}

void loop() {
  if (Serial.available() > 0) {

    char incoming = Serial.read();

    // 개행 / 공백 무시
    if (incoming == '\n' || incoming == '\r') return;

    currentMode = incoming;

    // ✅ 수신 로그 (핵심)
    Serial.print("[RECV] ");
    Serial.println(currentMode);

    applyMode();
  }
}

void applyMode() {

  switch (currentMode) {

    case 'N':  // Normal
      Serial.println("[MODE] NORMAL");
      digitalWrite(LED_BLUE, HIGH);
      digitalWrite(LED_RED, LOW);
      noTone(BUZZER);
      break;

    case 'A':  // Any anomaly
      Serial.println("[MODE] ANOMALY");
      digitalWrite(LED_BLUE, LOW);
      digitalWrite(LED_RED, HIGH);
      tone(BUZZER, 2000);
      break;

    case 'O':  // Off
    default:
      Serial.println("[MODE] OFF");
      allOff();
      break;
  }
}

void allOff() {
  digitalWrite(LED_BLUE, LOW);
  digitalWrite(LED_RED, LOW);
  noTone(BUZZER);
}
