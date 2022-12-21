import openai
from flask import Flask, jsonify, render_template, request
import sqlite3 as sql
app = Flask(__name__)


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


openai.api_key = open_file('openaiapikey.txt')


def gpt3_completion(prompt, engine='text-davinci-002', temp=0.7, top_p=1.0, tokens=400, freq_pen=0.0, pres_pen=0.0, stop=['BOT:', 'USER:']):
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        temperature=temp,
        max_tokens=tokens,
        top_p=top_p,
        frequency_penalty=freq_pen,
        presence_penalty=pres_pen,
        stop=stop)
    text = response['choices'][0]['text'].strip()
    print(response)
    return text

@app.route('/')
def chatbot():
   return render_template('index1.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
    
    conversation = list()
    your_name="Abhishek"  #NAME INPUT
    dbname=your_name+".db"
    try:
        conn=sql.connect(dbname)
        print("Connected successfully")
        conn.execute('CREATE TABLE chatbot(usertext TEXT)')
        print("Table created successfully")
        conn.close()
    except:
        print("Database already created")
    if request.method == 'POST':
      user_input = request.form
      print("User input=",user_input)
    con=sql.connect(dbname)
    con.row_factory=sql.Row
    cur=con.cursor()
    cur.execute("select * from chatbot")
    rows=cur.fetchall()
    for i in rows:
        print("i=",i["usertext"])
        conversation.append(i["usertext"])
    conversation.append('\nUSER: %s' % user_input)
    text_block = '\n'.join(conversation)
    print(text_block)
    prompt = open_file('chat.txt').replace('<<BLOCK>>', text_block)
    prompt = prompt + '\nBOT:'
    response = gpt3_completion(prompt)
    print('BOT:', response)
    conversation.append('BOT: %s' % response)
    x="USER:"+user_input.get('user_input')
    y="BOT:"+response
    print("Prompt:",prompt)
    with sql.connect(dbname) as con:
                cur=con.cursor()
                cur.execute("INSERT INTO chatbot (usertext) VALUES (?)", (x,))
                cur.execute("INSERT INTO chatbot (usertext) VALUES (?)", (y,))
                con.commit()
                msg="SUCCESS"
    con.close()
    return jsonify({ 'var1': response , 'var2':user_input.get('user_input') })


if __name__ == '__main__':
    
    app.run(debug = True)
   
        