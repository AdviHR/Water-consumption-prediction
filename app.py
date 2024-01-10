from flask import Flask,request,render_template,make_response
import mysql.connector
from mysql.connector import Error
import json
import csv
import os
from werkzeug.utils import secure_filename

from flask_cors import CORS, cross_origin


app=Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS']='Content-Type'

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')
@app.route('/register')
def register():
    return render_template('register.html')
@app.route('/login')
def login():
    return render_template('login.html')
    
@app.route('/dashboard')


def dashboard():
    connection = mysql.connector.connect(host='localhost',database='waterdb',user='root',password='')
    sqlquery="SELECT TU AS value1, COUNT(*) AS count1 FROM dataset GROUP BY TU UNION SELECT USO2013 AS value2, COUNT(*) AS count2 FROM dataset GROUP BY USO2013"

    print(sqlquery)
    cursor = connection.cursor()
    cursor.execute(sqlquery)
    data=cursor.fetchall()
    print(data)
   
    connection.close()
    cursor.close()
    return render_template('dashboard.html',drcount=data[3][1],dmcount=data[2][1],scount=data[6][1],h3count=data[7][1],mxcount=data[9][1],icount=data[8][1])



@app.route('/regdata', methods =  ['GET','POST'])
def regdata():
    #Data gathering
    nm=request.args['uname']
    em=request.args['email']
    ph=request.args['phone']
    gen=request.args['gender']
    pswd=request.args['pswd']
    addr=request.args['addr']

    
    #Data transmission to db
    connection = mysql.connector.connect(host='localhost',database='waterdb',user='root',password='')
    sqlquery="insert into userdata(uname,email,phone,gender,pswd,addr) values('"+nm+"','"+em+"','"+ph+"','"+gen+"','"+pswd+"','"+addr+"')"
    print(sqlquery)
    cursor = connection.cursor()
    cursor.execute(sqlquery)
    connection.commit() 
    connection.close()
    cursor.close()
    msg="Data Saved Successfully"
    #return render_template('register.html')
    resp = make_response(json.dumps(msg))
    
    print(msg, flush=True)
    #return render_template('register.html',data=msg)
    return resp



@app.route('/logdata', methods =  ['GET','POST'])
def logdata():
    #Data gathering
    em=request.args['email']
    pswd=request.args['pswd']

    
    #Data transmission to db
    connection = mysql.connector.connect(host='localhost',database='waterdb',user='root',password='')
    sqlquery="select count(*) from  userdata where email='"+em+"' and pswd='"+pswd+"'"
    print(sqlquery)
    cursor = connection.cursor()
    cursor.execute(sqlquery)
    data=cursor.fetchall()
    print(data) 
    connection.close()
    cursor.close()
    msg=""
    if data[0][0]==0:
        msg="Failure"
    else:
        msg="Success"
    #return render_template('register.html')
    resp = make_response(json.dumps(msg))
    
    print(msg, flush=True)
    #return render_template('register.html',data=msg)
    return resp

    
@app.route('/savedataset', methods = ['POST'])
def savedataset():
    print("request :"+str(request), flush=True)
    if request.method == 'POST':
        connection = mysql.connector.connect(host='localhost',database='waterdb',user='root',password='')
        cursor = connection.cursor()
    
        prod_mas = request.files['dt_file']
        filename = secure_filename(prod_mas.filename)
        prod_mas.save(os.path.join("./static/Uploads/", filename))

        #csv reader
        fn = os.path.join("./static/Uploads/", filename)

        # initializing the titles and rows list 
        fields = [] 
        rows = []
        
        with open(fn, 'r') as csvfile:
            # creating a csv reader object 
            csvreader = csv.reader(csvfile)  
  
            # extracting each data row one by one 
            for row in csvreader:
                rows.append(row)
                print(row)

        try:     
            #print(rows[1][1])       
            for row in rows[1:]: 
                # parsing each column of a row
                if row[0][0]!="":                
                    query="";
                    query="insert into dataset values (";
                    for col in row: 
                        query =query+"'"+col+"',"
                    query =query[:-1]
                    query=query+");"
                print("query :"+str(query), flush=True)
                cursor.execute(query)
                connection.commit()
        except:
            print("An exception occurred")
        csvfile.close()
        
        print("Filename :"+str(prod_mas), flush=True)       
        
        
        connection.close()
        cursor.close()
        return render_template('dataloader.html',data="Data loaded successfully")

    
@app.route('/cleardataset', methods = ['POST'])
def cleardataset():
    print("request :"+str(request), flush=True)
    if request.method == 'POST':
        connection = mysql.connector.connect(host='localhost',database='waterdb',user='root',password='')
        sqlquery="delete from dataset"
        print(sqlquery)
        cursor = connection.cursor()
        cursor.execute(sqlquery)
        connection.commit() 
        connection.close()
        cursor.close()
        return render_template('dataloader.html',data="Data cleared successfully")

@app.route('/planning')
def planning():
    connection = mysql.connector.connect(host='localhost',database='waterdb',user='root',password='')
    sqlquery="select * from dataset limit 100"
    print(sqlquery)
    cursor = connection.cursor()
    cursor.execute(sqlquery)
    data=cursor.fetchall()
    print(data) 
    connection.close()
    cursor.close()    
    return render_template('planning.html',patdata=data)
@app.route('/dataloader')
def dataloader():
    return render_template('dataloader.html')
@app.route('/predict')
def predict():
    return render_template('prediction.html')

@app.route('/predictdata', methods =  ['GET','POST'])
def predictdata():
    #Data gathering
    tu=request.args['tu']
    sep=request.args['sep']
    oct=request.args['oct']
    nov=request.args['nov']


    
    #Data transmission to db
    connection = mysql.connector.connect(host='localhost',database='waterdb',user='root',password='')
    sqlquery="select DIC from dataset where TU='"+tu+"' and SEP='"+sep+"' and OCT='"+oct+"' and NOV='"+nov+"' limit 1 "
    print(sqlquery)
    cursor = connection.cursor()
    cursor.execute(sqlquery)
    data=cursor.fetchall()
    connection.commit()    
    connection.close()
    cursor.close()
    #dataset creation    
    import pandas as pd
    dataset=pd.read_csv("./static/Uploads/water_c.csv")
    res=''
    from sklearn.model_selection import train_test_split

    predictors = dataset.drop("DIC",axis=1)
    target = dataset["DIC"]

    X_train,X_test,Y_train,Y_test = train_test_split(predictors,target,test_size=0.20,random_state=0)
    res=data[0][0]
      
    msg="December water consumption is "+res+"units"
   
    resp = make_response(json.dumps(msg))
    
    print(msg, flush=True)
  
    return resp



@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/contactdata', methods =  ['GET','POST'])
def contactdata():
    #Data gathering
    nm=request.args['name']
    em=request.args['email']
    msg=request.args['message']

    
    #Data transmission to db
    connection = mysql.connector.connect(host='localhost',database='waterdb',user='root',password='')
    sqlquery="insert into contactdata(name,email,message) values('"+nm+"','"+em+"','"+msg+"')"
    print(sqlquery)
    cursor = connection.cursor()
    cursor.execute(sqlquery)
    connection.commit() 
    connection.close()
    cursor.close()
    msg="Contact Saved Successfully"
    #return render_template('register.html')
    resp = make_response(json.dumps(msg))
    
    print(msg, flush=True)
    #return render_template('register.html',data=msg)
    return resp

if __name__=="__main__":
    app.run(debug=True)
