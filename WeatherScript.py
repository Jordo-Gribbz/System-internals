#import required modules
#Reference, paho
#based on: https://pypi.org/project/paho-mqtt/#client
import requests, json
import RPi.GPIO as GPIO
from time import sleep 
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import paho.mqtt.client as mqtt

GPIO.setmode(GPIO.BCM)
GPIO.setup(14, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)

broker = "*insert IP"

def Draw(text, textW, textH, textD):
    #Reference, Adafruit
    #based on: https://learn.adafruit.com/monochrome-oled-breakouts/python-usage-2
    
    # Define the Reset Pin
    oled_reset = digitalio.DigitalInOut(board.D4)

    # Change these
    # to the right size for your display!
    WIDTH = 128
    HEIGHT = 64 
    BORDER = 5

    # Use for I2C.
    i2c = board.I2C()
    oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=oled_reset)

    # Clear display.
    oled.fill(0)
    oled.show()
    
    font_size = 14 

    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    image = Image.new("1", (oled.width, oled.height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)    
    # Load default font.
    font = ImageFont.load_default()
    
    (font_width, font_height) = font.getsize(text)
       
    draw.text(
        (oled.width//2 - font_width//2, 0),
        text,
        font=font,
        fill=255,
    )
    
    (font_width, font_height) = font.getsize(textW)
       
    draw.text(
        (oled.width//2 - font_width//2, 0 + font_size),
        textW,
        font=font,
        fill=255,
    )
    
    (font_width, font_height) = font.getsize(textH)
       
    draw.text(
        (oled.width//2 - font_width//2, 0 + font_size*2),
        textH,
        font=font,
        fill=255,
    )
    
    (font_width, font_height) = font.getsize(textD)
       
    draw.text(
        (oled.width//2 - font_width//2, 0 + font_size*3),
        textD,
        font=font,
        fill=255,
    )
    
    # Display image
    oled.image(image)
    oled.show()
    GPIO.output(15, GPIO.HIGH)
    sleep(1)
    GPIO.output(15, GPIO.LOW)
    sleep(1)
    GPIO.output(15, GPIO.HIGH)
    sleep(1)
    GPIO.output(15, GPIO.LOW)

def Weather(client, userdata, message):

    GPIO.output(14, GPIO.LOW) #Once message reciveced light off
    
    AWScity = str(message.payload.decode("utf-8","ignore"))
    
    #Reference, Weather API code
    #based on: https://www.geeksforgeeks.org/python-find-current-weather-of-anycity-using-openweathermap-api/

    # Enter your API key here
    api_key = "85540bda151e89fc35d48ac7d5e2056b"

    # base_url variable to store url
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    # Give city name
    city_name = AWScity
    # complete_url variable to store
    # complete url address
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name

    # get method of requests module
    # return response object
    response = requests.get(complete_url)

    # json method of response object
    # convert json format data into
    # python format data
    x = response.json()

    # Now x contains list of nested dictionaries
    # Check the value of "cod" key is equal to
    # "404", means city is found otherwise,
    # city is not found
    if x["cod"] != "404":
        
        # store the value of "main"
        # key in variable y
        y = x["main"]

        # store the value corresponding
        # to the "temp" key of y
        current_temperature = y["temp"]

        # store the value corresponding
        # to the "humidity" key of y
        current_humidity = y["humidity"]

        # store the value of "weather"
        # key in variable z
        z = x["weather"]

        # store the value corresponding
        # to the "description" key at
        # the 0th index of z
        weather_description = z[0]["description"]
        
        current_temperature = round(current_temperature - 273.15, 2)
            
        # print following values
        print( city_name + " Weather" +
            "\n Temperature (in Celcius) = " +
                        str(current_temperature) +
            "\n humidity (in percentage) = " +
                        str(current_humidity) +
            "\n description = " +
                        str(weather_description))
                        
        text = (city_name + " Weather" )
        textW =("Temperature: " + str(current_temperature))
        textH = ("Humidity: " +  str(current_humidity)) 
        textD = (str(weather_description))
        
        Draw(text, textW, textH, textD)
        
    else:
        print(" City Not Found ")
        GPIO.output(18, GPIO.HIGH) #if city cannot be found flash red led
        sleep(1)
        GPIO.output(18, GPIO.LOW) 
        sleep(1)
        GPIO.output(18, GPIO.HIGH) 
        sleep(1)
        GPIO.output(18, GPIO.LOW) 


GPIO.output(14, GPIO.HIGH) 

client = mqtt.Client()

client.username_pw_set("user", password="test")

client.on_message=Weather

client.connect(broker)
client.subscribe("Citydata")
client.loop_forever()
