from flask import Flask, request, Response
from flask_cors import CORS
import dbcreds
import mariadb
import json
import secrets


app = Flask(__name__)
CORS(app)


@app.route("/api/users", methods=["GET","POST","PATCH","DELETE"])
def users():
    if request.method =="GET":
        user_id = request.args.get("userId")
        conn = None
        cursor = None 
        users_data = None
        try:
            conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
            cursor = conn.cursor()
            #if there is user id 
            if user_id:
                cursor.execute("SELECT * FROM users where id =?", [user_id])
                users_data = cursor.fetchall()
            #if no user id
            else:
                cursor.execute("SELECT * FROM users")
                users_data = cursor.fetchall()
        except Exception as e:
            print(e)
        finally:
            if(cursor !=None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
                #if there is user data or if it is empty
        if users_data or users_data ==[]:
            users_info =[]
            #create for loop
            for user in users_data:
                user_dic={
                    #user 0 is the user id in db, 1 is email ...
                    "userId": user[0],
                    "email": user [1],
                    "bio": user [2],
                    "username": user[5],
                    "birthdate": user [4]
                }
                users_info.append(user_dic)
            return Response(json.dumps(users_info, default = str), mimetype="application/json", status=200)
        else:
            return Response("failure", mimetype="html/text", status=400)
    if request.method =="POST":
        conn = None
        cursor = None 
        user_info = request.json
        username = user_info.get("username")
        password = user_info.get("password")
        email = user_info.get("email")
        birthdate = user_info.get("birthdate")
        bio = user_info.get("bio")
        user_session_id = None
        #should not be empty 
        if email!=None and email !="" and username!=None and username !="" and password!=None and password !="" and birthdate!=None and birthdate !="" and bio!=None and bio !="":
            try:
                conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, password, email, birthdate, bio)  VALUES  (?,?,?,?,?)", [username, password, email, birthdate,bio])
                conn.commit()
                user_id = cursor.lastrowid
                #make login token(random 20 charachters)
                login_token= secrets.token_urlsafe(20)
                #usersession is where login token is
                cursor.execute("INSERT INTO user_session (user_id, loginToken) VALUES (?,?)", [user_id, login_token])
                conn.commit()
                #make sure everything is inserted and fine
                user_session_id = cursor.lastrowid
            except Exception as e:
                print(e)
            finally:
                if(cursor !=None):
                    cursor.close()
                if(conn != None):
                    conn.rollback()
                    conn.close()
                    #if there is user data or if it is empty
                if user_session_id != None:
                    user_dic={
                        "userId": user_id,
                        "email": email,
                        "bio": bio,
                        "username": username,
                        "birthdate": birthdate,
                        "loginToken": login_token
                    }
                    return Response(json.dumps(user_dic, default = str), mimetype="application/json", status=200)
                else:
                    return Response("failure", mimetype="html/text", status=400)
    if request.method == "PATCH":
    #must have ownership/login token
        user_info = request.json
        conn = None
        cursor = None
        username = user_info.get("username")
        password = user_info.get("password")
        email = user_info.get("email")
        birthdate = user_info.get("birthdate")
        bio = user_info.get("bio")
        login_token = user_info.get("loginToken")
        user= None
        try:
            conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
            cursor = conn.cursor()
            #not equal none or empty string
            if email != None and email !="" and login_token != None and login_token !="":
                #get userid based on login token
                cursor.execute("SELECT user_id FROM user_session where loginToken = ?",[login_token])
                user_id = cursor.fetchone()[0]
                #can update user table based on user id
                cursor.execute("UPDATE users SET email = ? where id = ?", [email, user_id])
            if username != None and username !="" and login_token != None and login_token !="":
                cursor.execute("SELECT user_id FROM user_session where loginToken = ?",[login_token])
                user_id = cursor.fetchone()[0]
                cursor.execute("UPDATE users SET username = ? where id = ?", [username, user_id])
            if password != None and password !="" and login_token != None and login_token !="":
                cursor.execute("SELECT user_id FROM user_session where loginToken = ?",[login_token])
                user_id = cursor.fetchone()[0]
                cursor.execute("UPDATE users SET password = ? where id = ?", [password, user_id])
            if bio != None and bio !="" and login_token != None and login_token !="":
                cursor.execute("SELECT user_id FROM user_session where loginToken = ?",[login_token])
                user_id = cursor.fetchone()[0]
                cursor.execute("UPDATE users SET bio = ? where id = ?", [bio, user_id])
            if birthdate != None and birthdate !="" and login_token != None and login_token !="":
                cursor.execute("SELECT user_id FROM user_session where loginToken = ?",[login_token])
                user_id = cursor.fetchone()[0]
                cursor.execute("UPDATE users SET birthdate = ? where id = ?", [birthdate, user_id])
            conn.commit()
            row=cursor.rowcount
            #return only data, no login token
            cursor.execute("SELECT * FROM users where id = ?", [user_id])
            user = cursor.fetchone()
        except Exception as e:
            print (e)
        finally:
            if(cursor !=None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
                #if there is user data or if it is empty
            if user != None:
                user_dic={
                    #user 0 is the user id in db, 1 is email ...
                    "userId": user[0],
                    "email": user [1],
                    "bio": user [2],
                    "username": user[5],
                    "birthdate": user [4]
                }
                return Response(json.dumps(user_dic, default = str), mimetype="application/json", status=200)
            else:
                return Response("failure", mimetype="html/text", status=400)
    if request.method == "DELETE":
    #must have ownership/login token
        user_info = request.json
        conn = None
        cursor = None
        password = user_info.get("password")
        login_token = user_info.get("loginToken")
        user= None
        try:
            conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
            cursor = conn.cursor()
            #get userid based on login token
            cursor.execute("SELECT user_id FROM user_session WHERE loginToken = ?",[login_token])
            user_id = cursor.fetchone()[0]
            if password != None and password !="" and login_token != None and login_token !="":
                cursor.execute("DELETE FROM users WHERE id = ?",[user_id])
                conn.commit()
                row=cursor.rowcount
        except Exception as e:
            print (e)
        finally:
            if(cursor !=None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
        if user == None:
            return Response("Delete successful", mimetype="application/json", status=200)
        else:
            return Response("failure", mimetype="html/text", status=400)



@app.route("/api/login", methods=["POST", "DELETE"])
def login():
    if request.method == "POST":
        conn = None
        cursor = None 
        users_data = None
        user_info = request.json
        password = user_info.get("password")
        email = user_info.get("email")
        login_rows = None
        user_data = None
        if email !="" and email !=None and password !="" and password !=None:
            try:
                conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users where email =? AND password =?", [email, password])
                user_data = cursor.fetchone()
                #did we get a row from the select stament 
                rows = cursor.rowcount
                #to login need user id, can get from fetch one(which hold all user data)
                if (user_data != None):
                    #user id is first row in db-0
                    user_id = user_data[0]
                    login_token = secrets.token_urlsafe(20)
                    cursor.execute("INSERT INTO user_session (user_id, loginToken) VALUES (?,?)",[user_id, login_token])
                    conn.commit()
                    #login_rows check if inseration is done correclt
                    login_rows = cursor.rowcount
            except Exception as e:
                print(e)
            finally: 
                if(cursor !=None):
                    cursor.close()
                if(conn != None):
                    conn.rollback()
                    conn.close()
                #determine if login is working or not
                if(login_rows != None):
                    #return user date
                    user_dic = {
                        "userId": user_data[0],
                        "email": user_data [1],
                        "bio": user_data [2],
                        "username": user_data[5],
                        "birthdate": user_data [4],
                        "loginToken": login_token
                    }
                    return Response(json.dumps(user_dic, default = str), mimetype="application/json", status=200)
                else:
                    return Response("failure", mimetype="html/text", status=400)
    if request.method =="DELETE":
        login_token = request.json.get("loginToken")
        rows = None
        if login_token != None and login_token !="":
            try: 
                conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
                cursor = conn.cursor()
                #delete token
                cursor.execute("DELETE FROM user_session where loginToken = ?", [login_token])
                conn.commit()
                rows = cursor.rowcount
            except Exception as e:
                print(e)
            finally:
                if(cursor !=None):
                    cursor.close()
                if(conn != None):
                    conn.rollback()
                    conn.close()
                if (rows == 1):
                    return Response("logout success", mimetype="text/html", status =204)
                else:
                    return Response ("logout failed",  mimetype="text/html", status =404)

@app.route("/api/follows", methods=["GET", "POST", "DELETE"])
def user_follows():
    if request.method == "GET":
        #get all users i am following
        user_id = request.args.get("userId")
        conn = None
        cursor = None
        users_data = None
        if user_id != None and user_id !="":
            try:
                conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
                cursor = conn.cursor()
                cursor.execute ("SELECT id, email, username, bio, birthdate FROM users u1 INNER JOIN follow f on u1.id = f.followed_id WHERE f.following_id = ?", [user_id])
                users_data = cursor.fetchall()
            except Exception as e:
                print(e)
            finally: 
                if(cursor !=None):
                    cursor.close()
                if(conn != None):
                    conn.rollback()
                    conn.close()
                    #or if users isnt following anyone- empty array
                if users_data != None or users_data == []:
                    users_list =[]
                    for user in users_data:
                        #reference select statment order above
                        user_dic = {
                            "userId": user[0],
                            "email": user[1],
                            "username": user[2],
                            "bio": user[3],
                            "birthdate": user[4]
                        }
                        #add dictionary to user list
                        users_list.append(user_dic)
                    return Response(json.dumps(users_list, default=str), mimetype="application/json", status=200)
                else:   
                    return Response("Failed", mimetype="text/html", status=400)
    if request.method == "POST":
        #the one making follow request must have logged in successfully
        login_token = request.json.get("loginToken")
        #my id
        followId = request.json.get("followId")
        rows = None
        #check for logintoken, userid
        if login_token !=None and login_token !="" and followId != None and followId !="":
            try:
                conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
                cursor = conn.cursor()
                #get my id first- the one making request
                cursor.execute("SELECT user_id from user_session where loginToken =?", [login_token])
                user_id = cursor.fetchone()[0]
                #userid of other user
                cursor.execute("INSERT INTO follow (following_id, followed_id) VALUES (?,?)", [user_id, followId])
                conn.commit()
                rows = cursor.rowcount
            except Exception as e:
                print(e)
            finally: 
                if(cursor !=None):
                    cursor.close()
                if(conn != None):
                    conn.rollback()
                    conn.close()
                if(rows != None and rows==1):
                    return Response("success", mimetype="text/html", status =204)
                else:
                    return Response ("Failed", mimetype="text/html", status= 400)
    if request.method == "DELETE":
        login_token = request.json.get("loginToken")
        #my id
        followId = request.json.get("followId")
        rows = None
        try:
            conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
            cursor = conn.cursor()
            #get my id first- the one making request
            cursor.execute("SELECT user_id from user_session where loginToken =?", [login_token])
            user_id = cursor.fetchone()[0]
            #userid of other user
            cursor.execute("DELETE FROM follow where following_id =? and followed_id =?", [user_id, followId])
            conn.commit()
            rows = cursor.rowcount
        except Exception as e:
            print(e)
        finally: 
            if(cursor !=None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows != None and rows==1):
                return Response("success", mimetype="text/html", status =204)
            else:
                return Response ("Failed", mimetype="text/html", status= 400)

@app.route("/api/followers", methods=["GET"])
def user_followers():
    if request.method == "GET":
        user_id = request.args.get("userId")
        conn = None
        cursor = None
        users_data = None
        if user_id != None and user_id !="":
            try:
                conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
                cursor = conn.cursor()
                #vis-versa following
                cursor.execute ("SELECT id, email, username, bio, birthdate FROM users u1 INNER JOIN follow f on u1.id = f.following_id WHERE f.followed_id = ?", [user_id])
                users_data = cursor.fetchall()
            except Exception as e:
                print(e)
            finally: 
                if(cursor !=None):
                    cursor.close()
                if(conn != None):
                    conn.rollback()
                    conn.close()
                if users_data != None or users_data == []:
                    users_list =[]
                    for user in users_data:
                        user_dic = {
                            "userId": user[0],
                            "email": user[1],
                            "username": user[2],
                            "bio": user[3],
                            "birthdate": user[4]
                        }
                        users_list.append(user_dic)
                    return Response(json.dumps(users_list, default=str), mimetype="application/json", status=200)
                else:   
                    return Response("Failed", mimetype="text/html", status=400)

@app.route("/api/tweets", methods=["GET","POST","PATCH","DELETE"])
def tweet():
    if request.method == "GET":
        #get all users i am following
        user_id = request.args.get("userId")
        conn = None
        cursor = None 
        tweet_data = None 
        try:
            conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
            cursor = conn.cursor()
            #if there is specific userid
            if user_id:
                cursor.execute("SELECT * FROM users u INNER JOIN tweet t ON u.id = t.user_id WHERE u.id = ?", [user_id])
                tweet_data = cursor.fetchall()
            else:
                #if you want all tweets
                cursor.execute("SELECT * FROM users u INNER JOIN tweet t ON u.id = t.user_id")
                tweet_data = cursor.fetchall()
        except Exception as e:
            print(e)
        finally:
            if(cursor !=None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
                #if there is tweet data or if it is empty
        if tweet_data or tweet_data ==[]:
            tweet_info =[]
            #create for loop
            for tweet in tweet_data:
                tweet_dic={
                    "tweetId": tweet[6],
                    "userId": tweet [0],
                    "username": tweet[5],
                    "content": tweet [8],
                    "createdAt": tweet [9]
                }
                tweet_info.append(tweet_dic)
            return Response(json.dumps(tweet_info, default = str), mimetype="application/json", status=200)
        else:
            return Response("failure", mimetype="html/text", status=400)
    if request.method == "POST":
        login_token = request.json.get("loginToken")
        content = request.json.get("content")
        conn = None
        cursor = None 
        tweet = None 
        user_id = None
        tweet_id = None
        try:
            conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE loginToken = ?", [login_token])
            user_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO tweet(user_id, content) VALUES (?,?)", [user_id, content])
            conn.commit() 
            tweet_id = cursor.lastrowid
            cursor.execute("SELECT * FROM users u INNER JOIN tweet t ON u.id = t.user_id where t.id = ?", [tweet_id])
            tweet = cursor.fetchone()
        except Exception as e:
            print(e)
        finally:
            if(cursor !=None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if tweet or tweet ==[]:
                tweet_dic={
                    "tweetId": tweet[6],
                    "userId": tweet [0],
                    "username": tweet[5],
                    "content": tweet [8],
                    "createdAt": tweet [9]
                }
                return Response(json.dumps(tweet_dic, default = str), mimetype="application/json", status=201)
            else:
                return Response("failure", mimetype="html/text", status=400)
    if request.method == "PATCH":
        login_token = request.json.get("loginToken")
        tweet_id = request.json.get("tweetId")
        content = request.json.get("content")
        conn = None
        cursor = None 
        user_id = None
        rows= None
        try:
            conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE loginToken = ?", [login_token])
            user_id = cursor.fetchone()[0]
            cursor.execute("UPDATE tweet SET content = ? WHERE id=? AND user_id =?", [content, tweet_id, user_id])
            conn.commit() 
            rows = cursor.rowcount
        except Exception as e:
            print(e)
        finally:
            if(cursor !=None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
                #tweetid and content come with request
            if rows != None:
                response_dic={
                    "tweetId": tweet_id,
                    "content": content,
                }
                return Response(json.dumps(response_dic, default = str), mimetype="application/json", status=200)
            else:
                return Response("failure", mimetype="html/text", status=400)
    if request.method == "DELETE":
        login_token = request.json.get("loginToken")
        tweet_id = request.json.get("tweetId")
        conn = None
        cursor = None 
        user_id = None
        rows= None
        try:
            conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE loginToken = ?", [login_token])
            user_id = cursor.fetchone()[0]
            cursor.execute("DELETE FROM tweet WHERE id=? AND user_id =?", [tweet_id, user_id])
            conn.commit() 
            rows = cursor.rowcount
        except Exception as e:
            print(e)
        finally:
            if(cursor !=None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if rows != None:
                return Response("Delete success", mimetype="html/text", status=204)
            else:
                return Response("failure", mimetype="html/text", status=400)
    


@app.route("/api/comments", methods=["GET","POST","PATCH","DELETE"])
def comment():
    if request.method == "GET":
        tweet_id = request.args.get("tweetId")
        conn = None
        cursor = None 
        comments_data = None 
        try:
            conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
            cursor = conn.cursor()
            if tweet_id:
                cursor.execute("SELECT c.id, t.id, u.id, u.username, c.content, c.createdAt FROM tweet t INNER JOIN comment c INNER JOIN users u ON t.id = c.tweet_id and u.id = c.user_id WHERE t.id = ?", [tweet_id])
                comments_data = cursor.fetchall()
            else:
                cursor.execute("SELECT * FROM users u INNER JOIN tweet t ON u.id = t.user_id")
                tweet_data = cursor.fetchall()
        except Exception as e:
            print(e)
        finally:
            if(cursor !=None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
        if comments_data or comments_data ==[]:
            comments_info =[]
            for comment in comments_data:
                comment_dic={
                    "commentId": comment[0],
                    "tweetId": comment [1],
                    "userId": comment[2],
                    "username": comment[3],
                    "content": comment [4],
                    "createdAt": comment [5]
                }
                comments_info.append(comment_dic)
            return Response(json.dumps(comments_info, default = str), mimetype="application/json", status=200)
        else:
            return Response("failure", mimetype="html/text", status=400)
    if request.method == "POST":
        login_token = request.json.get("loginToken")
        content = request.json.get("content")
        tweet_id = request.json.get("tweetId")
        if (len(content) > 150):
            return Response("exceeds 150 character limit", mimetype="html/text", status=400)
        conn = None
        cursor = None 
        comment = None
        user_id = None
        comment_id = None
        try:
            conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE loginToken = ?", [login_token])
            user_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO comment(user_id,tweet_id, content) VALUES (?,?,?)", [user_id, tweet_id, content])
            conn.commit() 
            comment_id = cursor.lastrowid
            cursor.execute("SELECT c.id, t.id, u.id, u.username, c.content, c.createdAt FROM tweet t INNER JOIN comment c INNER JOIN users u ON t.id = c.tweet_id and u.id = c.user_id WHERE c.id = ?", [comment_id])
            comment= cursor.fetchone()
        except Exception as e:
            print(e)
        finally:
            if(cursor !=None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if comment or comment ==[]:
                comment_dic={
                    "commentId": comment[0],
                    "tweetId": comment [1],
                    "userId": comment[2],
                    "username": comment[3],
                    "content": comment[4],
                    "createdAt": comment [5]
                }
                return Response(json.dumps(comment_dic, default = str), mimetype="application/json", status=201)
            else:
                return Response("failure", mimetype="html/text", status=400)

    if request.method == "PATCH":
        login_token = request.json.get("loginToken")
        comment_id = request.json.get("commentId")
        content = request.json.get("content")
        if (len(content) > 150):
            return Response("comment too long: 150 character limit", mimetype="html/text", status=400)
        conn = None
        cursor = None 
        user_id = None
        rows= None
        comment_data = None
        try:
            conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE loginToken = ?", [login_token])
            user = cursor.fetchone()[0]
            cursor.execute("SELECT * FROM users u INNER JOIN comment c ON u.id = c.user_id WHERE c.id = ?", [comment_id])
            comment_id = cursor.lastrowid
            cursor.execute("UPDATE comment SET content = ? WHERE id=? AND user_id =?", [content, commentId, userId])
            conn.commit() 
            rows = cursor.rowcount
        except Exception as e:
            print(e)
        finally:
            if(cursor !=None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if comment_data or comment_data ==[]:
                comment_dic={
                    "commentId": comment[6],
                    "tweetId": comment[10],
                    "userId": comment [0],
                    "username": comment [5],
                    "content": comment [8],
                    "createdAt": comment [9]
                }
                return Response(json.dumps(comment_dic, default = str), mimetype="application/json", status=200)
            else:
                return Response("failure", mimetype="html/text", status=400)
    if request.method == "DELETE":
        login_token = request.json.get("loginToken")
        comment_id = request.json.get("commentId")
        conn = None
        cursor = None 
        user_id = None
        rows= None
        try:
            conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE loginToken = ?", [login_token])
            user_id = cursor.fetchone()[0]
            cursor.execute("DELETE FROM comment WHERE id=? AND user_id =?", [comment_id, user_id])
            conn.commit() 
            rows = cursor.rowcount
        except Exception as e:
            print(e)
        finally:
            if(cursor !=None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if rows != None:
                return Response("Delete success", mimetype="html/text", status=204)
            else:
                return Response("failure", mimetype="html/text", status=400)


@app.route("/api/tweet_likes", methods=["GET","POST","DELETE"])
def tweet_like():
    if request.method =="GET":
        tweet_id = request.args.get("tweetId")
        conn = None
        cursor = None
        try:
            conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
            cursor = conn.cursor()
            if user_id:
                cursor.execute("SELECT * FROM users u INNER JOIN tweet_like tl ON u.id = tl.user_id WHERE u.id = ?", [user_id])
                tweetlike_data = cursor.fetchall()
            else:
                cursor.execute("SELECT * FROM users u INNER JOIN tweet_like tl ON u.id = tl.user_id")
                tweetlike_data = cursor.fetchall()
        except Exception as e:
            print(e)
        finally:
            if(cursor !=None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
        if tweetlike_data or tweetlike_data ==[]:
            tweetlike_info =[]
            for tweetlike in tweetlike_data:
                tweetlike_dic={
                    "tweetId": tweetlike[8],
                    "userId": tweetlike [0],
                    "username": tweetlike[5]
                }
                tweetlike_info.append(tweetlike_dic)
            return Response(json.dumps(tweetlike_info, default = str), mimetype="application/json", status=200)
        else:
            return Response("failure", mimetype="html/text", status=400)
    if request.method == "POST":
    # An error will be returned if the loginToken or tweetId is invalid. 
    # An error will also be sent if the user has already 'liked' the tweet
        login_token = request.json.get("loginToken")
        tweet_id = request.json.get("tweedId")
        rows = None
        if login_token !=None and login_token !=""
            try:
                conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("SELECT user_id from user_session where loginToken =?", [login_token])
                user_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO tweet_like (user_id, tweet.id) VALUES (?,?)", [user_id, tweet_likeId])
                conn.commit()
                rows = cursor.rowcount
            except Exception as e:
                print(e)
            finally: 
                if(cursor !=None):
                    cursor.close()
                if(conn != None):
                    conn.rollback()
                    conn.close()
                if(rows != None and rows==1):
                    return Response("liked", mimetype="text/html", status =204)
                else:
                    return Response ("Failed", mimetype="text/html", status= 400)
    if request.method == "DELETE":
        # An error will be returned if the loginToken and tweetId combo are 
        # not valid (the user has not liked that tweet or that tweet does not exist).
            login_token = request.json.get("loginToken")
            tweetId = request.json.get("tweetId")
            rows = None
            try:
                conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
                cursor = conn.cursor()       
                cursor.execute("SELECT user_id from user_session where loginToken =?", [login_token])
                user_id = cursor.fetchone()[0]
                cursor.execute("DELETE FROM tweet_like WHERE id=? AND user_id =?", [tweet_like_id, user_id])
                conn.commit() 
                rows = cursor.rowcount
        except Exception as e:
            print(e)
        finally:
            if(cursor !=None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if rows != None:
                return Response("Delete success", mimetype="html/text", status=204)
            else:
                return Response("failure", mimetype="html/text", status=400)

@app.route("/api/comment_likes", methods=["GET","POST","DELETE"])
def comment_like():
    if request.method =="GET":
        comment_id request.args.get("commentId")
        conn = None
        cursor = None
        comment_like = None
        try:
            conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
            cursor = conn.cursor()
            if comment_like_id:
                cursor.execute("SELECT * FROM users u INNER JOIN comment_like cl ON u.id = cl.user_id WHERE u.id = ?", [user_id])
                comment_like_data = cursor.fetchall()
            else:
                cursor.execute("SELECT * FROM users u INNER JOIN comment_like ON u.id = cl.user_id")
                tweet_data = cursor.fetchall()
        except Exception as e:
            print(e)
        finally:
            if(cursor !=None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
        if comment_like_data or comment_like_data ==[]:
            comment_like_info =[]
            for comment_like in comment_like_data:
                tweet_dic={
                    "commentId": comment_like[8],
                    "userId": tweet [0],
                    "username": tweet[5]
                }
                tweet_info.append(tweet_dic)
            return Response(json.dumps(comment_like_info, default = str), mimetype="application/json", status=200)
        else:
            return Response("failure", mimetype="html/text", status=400)
    if request.method == "POST":
        login_token = request.json.get("loginToken")
        comment_id = request.json.get("commentId")
        conn = None
        cursor = None
        comment_like = None
        comment_id = None
        user_id = None
        try:
            conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE loginToken = ?", [login_token])
            user_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO comment_like(id, user_id) VALUES (?,?)", [comment_like_id, user_id])
            conn.commit() 
            comment_like_id = cursor.lastrowid
            cursor.execute("SELECT * FROM users u INNER JOIN comment_like cl ON u.id = cl.user_id where cl.id = ?", [comment_like_id])
            comment_like = cursor.fetchone()
        except Exception as e:
            print(e)
        finally:
            if(cursor !=None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if comment_like or comment_like ==[]:
                comment_like_dic={
                    "commentId": tweet[8],
                    "userId": tweet [0],
                    "username": tweet[5]
                }
                return Response(json.dumps(comment_like_dic, default = str), mimetype="application/json", status=201)
            else:
                return Response("failure", mimetype="html/text", status=400)
    if request.method == "DELETE":
        login_token = request.json.get("loginToken")
        comment_id = request.json.get("commentId")







            