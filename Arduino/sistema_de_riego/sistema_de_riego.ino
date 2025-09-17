const int AirValue = 550;   
const int WaterValue = 250;  
int soilMoistureValue = 0;
int soilmoisturepercent=0;
void setup() {
  pinMode(9, OUTPUT); 
  Serial.begin(9600); 
}
void loop() {
soilMoistureValue = analogRead(A0); 
Serial.println(soilMoistureValue);
soilmoisturepercent = map(soilMoistureValue, AirValue, WaterValue, 0, 100);

if (soilmoisturepercent < 40) 
  {
    Serial.println("seco, Pump turning on");
    digitalWrite(9, HIGH); 
  }
  else if (soilmoisturepercent > 50)
    Serial.println("mojado, Pump turning off");
    digitalWrite(9, LOW); 
  }



if(soilmoisturepercent >= 100)
{
  Serial.println("100 %");
}
else if(soilmoisturepercent <=0)
{
  Serial.println("0 %");
}
else if(soilmoisturepercent >0 && soilmoisturepercent < 100)
{
  Serial.print(soilmoisturepercent);
  Serial.println("%");
  
}
  delay(250);
}
