/*
Control relee
*/

int action = -1;
int relay = -1;
int state = -1;
int relay_state[9] = {0,0,0,0,0,0,0,0,0};
int RXLED = 17;

void setup() {
  for (int i=2; i<10; i++){
    pinMode(i, OUTPUT);
    digitalWrite(i, HIGH);
  }
  pinMode(RXLED, OUTPUT);
  Serial.begin(9600); 
  
}

void loop() {

  while (Serial.available() > 0) {
    action = Serial.parseInt();
    relay = Serial.parseInt();
    if (Serial.peek()==44){state = Serial.parseInt();}
    
    if (Serial.read() == '\n'){
      switch(action){
        case 1:
          if (relay>0 && relay<9){
            if (state == 0 || state == 1){
              bool b_state = state;
              digitalWrite(relay+1, !b_state);
              relay_state[relay] = b_state;
              Serial.println(String(action+100) + ',' + String(relay) + ',' + String(b_state));
            }
            else {
              Serial.println(String(0) + ',' + String(action) + ',' + String(11));
            }
          }
          else {
            Serial.println(String(0) + ',' + String(action) + ',' + String(31));
          }
        break;

        case 2:
          if (relay == 0){
            for (int i=1; i<9; i++){
              Serial.println(String(action+100) + ',' + String(i) + ',' + String(relay_state[i]));
            }
          }
          else if (relay>0 && relay<9){
            Serial.println(String(action+100) + ',' + String(relay) + ',' + String(relay_state[relay]));
          }
          else {
            Serial.println(String(0) + ',' + String(action) + ',' + String(31));
          }
        break;
        case 99:
          for(int i=0; i<=relay; i++){
            digitalWrite(RXLED, 1);   
            TXLED1; 
            delay(500);
            digitalWrite(RXLED, 0);  
            TXLED0; 
            delay(500);
          }

        break;
        
      }
    }
    action = -1;
    relay = -1;
    state = -1;
  }
}
