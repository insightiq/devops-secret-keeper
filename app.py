from pywebio.input import input, select, textarea
from pywebio.output import put_text, put_image, put_html, put_code, put_buttons, popup,put_processbar
import redis,time
import secrets
from flask import Flask
from pywebio.platform.flask import webio_view
import argparse
from pywebio import start_server
from pywebio.session import run_js, set_env

app = Flask(__name__)

# Connect to the Redis server
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Define a Redis key for storing the data-to-code mapping
REDIS_MAPPING_KEY = "data_to_code_mapping"

def save_mapping_to_redis(data_to_code):
    # Save the data-to-code mapping to Redis
    redis_client.hmset(REDIS_MAPPING_KEY, data_to_code)

def btn_click(btn_val):
            if btn_val == 'Home':
                run_js('window.location.reload()')
            elif btn_val == "About":
                popup("About",
                      [put_html('<h2>Created by InsightIQ</h2>'),                   
                       
                       ]

                      )

def retrieve_mapping_from_redis():
    # Retrieve the data-to-code mapping from Redis
    data = redis_client.hgetall(REDIS_MAPPING_KEY)
    return {code.decode('utf-8'): data.decode('utf-8') for code, data in data.items()}

def generate_code_and_store_data(data, data_to_code):
    # Generate a random code and store the data-to-code mapping in Redis
    code = secrets.token_hex(4)  # Generate an 8-character hexadecimal code
    data_to_code[code] = data
    save_mapping_to_redis(data_to_code)
    return code

def insert_data():

    # Input form to insert data and generate a code
    data = textarea("Enter your Secret✨:", rows=5, placeholder="Don't share your secrets...", required=True)

    data_to_code = retrieve_mapping_from_redis()
    code = generate_code_and_store_data(data, data_to_code)

    put_text(f"Secret Created 🔒 ")
    put_text(f"Your secret code is:")
    
    larger_text = f'<span style="font-size: 20px; color: green;">{code}</span>'
    put_html(larger_text)
    
    put_buttons(['Home', 'About', 'Copy'], onclick=btn_click)

def retrieve_data():
    # Input form to retrieve data using a code
    code = input("Enter the secret code to retrieve your data:", type='text',required=True)
    data_to_code = retrieve_mapping_from_redis()
    data = data_to_code.get(code)

   
    
    if data:
        
        put_text("Secret retrieved Successfully 🔓")
        larger_text = f'<span style="font-size: 20px; color: black;">{data}</span>'
        put_html(larger_text)
        #put_text(data)
        put_buttons(['Home', 'About'], onclick=btn_click)
        

    else:
        #put_text("Invalid code. Secret not found.")
        larger_text = f'<span style="font-size: 20px; color: black;">Invalid Code. Please try again</span>'
        put_html(larger_text)
        put_buttons(['Home', 'About'], onclick=btn_click)


def home():
    put_html(r"""<h1  align="center"><strong> SECRET KEEPER 🔐 </strong></h1>""")
    img = open('logo.png', 'rb').read()
    put_image(img, width='100px')  # size of image

    put_code("Secret Keeper is an online web app to create and share secrets.", 'python')

    option = select('Select an Option!', ['Insert Secret', 'Retrieve Secret'])
    
    if option == 'Insert Secret':
        insert_data()
    elif option == 'Retrieve Secret':
        retrieve_data()

# To allow reloading of the web browser and specifying the port
app.add_url_rule('/home', 'webio_view', webio_view(home), methods=['GET', 'POST', 'OPTIONS'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8085)
    args = parser.parse_args()

    start_server(home, port=args.port, debug=True)

