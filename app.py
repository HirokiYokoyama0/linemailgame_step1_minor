from worddata_Excel import create_word,check_genre
from flask import Flask, render_template, redirect, url_for,request,g

#from models.models import db, MemberList #class名
import random
from flask_sqlalchemy import SQLAlchemy ###
from flask.globals import session
import worddata_Excel #自作関数

app = Flask(__name__)
app.secret_key = 'yokoyama' # secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db_memberlist.sqlite' ###
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False ###

db = SQLAlchemy(app) ###
db2 = SQLAlchemy(app) ###
db3 = SQLAlchemy(app) ### for worddata

class MemberList(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False)
    comment = db.Column(db.String(128), nullable=False)
    vote_num = db.Column(db.Integer, nullable=False)
    ulf_flg = db.Column(db.Integer, nullable=False)
    to_vote_minor = db.Column(db.Integer, nullable=False)
    to_vote_major = db.Column(db.Integer, nullable=False)
    prepare_flg = db.Column(db.Integer, nullable=False)

    def __init__(self, username=None, comment=None, vote_num = 0 , ulf_flg = 0 ,to_vote_minor = 0,to_vote_major = 0,prepare_flg = 0):
        self.username = username
        self.comment = comment
        self.vote_num = vote_num
        self.ulf_flg = ulf_flg
        self.to_vote_minor = to_vote_minor
        self.to_vote_major = to_vote_major
        self.prepare_flg = prepare_flg

    def __repr__(self):
        #return '<UserName: %r  ' % (self.username)
        return f"id = {self.id}, username={self.username}"


class OtherVar(db2.Model):
    __tablename__ = 'OtherVariable'
    id = db.Column(db.Integer, primary_key=True)
    word_num = db.Column(db.Integer, nullable=False)
    global_ulfnum = db.Column(db.Integer, nullable=False)
    wolf_number = db.Column(db.Integer, nullable=False)
    genre_number = db.Column(db.Integer, nullable=False)
    mainmail = db.Column(db.String(128), nullable=False)
    ans1 = db.Column(db.String(128), nullable=False)
    ans2 = db.Column(db.String(128), nullable=False)
    ans3 = db.Column(db.String(128), nullable=False)
    ans4 = db.Column(db.String(128), nullable=False)
    ans5 = db.Column(db.String(128), nullable=False)

    def __init__(self, word_num = 0 , global_ulfnum = 0 ,wolf_number = 0 ,genre_number = 0 ,mainmail = '' ,ans1 = '',ans2 = '',ans3 = '',ans4 = '',ans5 = ''):
        self.word_num = word_num
        self.global_ulfnum = global_ulfnum
        self.wolf_number = wolf_number
        self.genre_number = genre_number
        self.mainmail = mainmail
        self.ans1 = ans1
        self.ans2 = ans2
        self.ans3 = ans3
        self.ans4 = ans4
        self.ans5 = ans5
        
    def __repr__(self):
        return f"id = {self.id},mainmail = {self.mainmail}"

class OrignalGenreData(db3.Model):
    __tablename__ = 'OrignalGenreData'
    id = db3.Column(db.Integer, primary_key=True)
    GenreData = db.Column(db.String(128), nullable=True)

    def __init__(self, GenreData=None):
        self.GenreData = GenreData

    def __repr__(self):
        return f"{self.GenreData}"

word_data = [] #wordデータ格納用
word_num = 0 #wordを選択番号

global_ulfnum = 0
genre_number = 0

@app.route('/') # メインページ
def main():
    myname = session.get('username')

    if myname  is None:
        checkflg = 0
    else:
        checkflg = 1


    return render_template('main.html',checkflg = checkflg)


@app.route("/index",methods=["post"])
def post():

    if "username" not in session:
        session["username"] = request.form["username"]

    
    myname = session.get('username')

    new_member = MemberList(username=request.form["username"],comment="",vote_num = 0 , ulf_flg = 0, to_vote_minor = 0,to_vote_major=0,prepare_flg=0)
    db.session.add(new_member)
    db.session.commit()

    MemberList_DB = db.session.query(MemberList).all() #デバッグ用
   
  
    #### この処理は一回しかやらない（最初にとおったときのみ実施） ####
    if len(MemberList_DB) == 1: #最初のひとりだけ？ちょっと不安処理
        word_Genre_p = check_genre()

        for data in word_Genre_p:
            new_data = OrignalGenreData(GenreData=data)
            db3.session.add(new_data)
    
        db3.session.commit()
     #### この処理は一回しかやらない ####

    word_Genre = db3.session.query(OrignalGenreData).all()
    return render_template('member_list.html',MemberList_DB = MemberList_DB, val = 0 , myname = myname  ,word_Genre = word_Genre, flg_start=0)

@app.route('/reset2',methods=["post"]) # リセット
def reset2():
   

   if "username" in session:  # セッション情報があれば削除
        session.pop('username', None)

   session.clear
 
    
   return render_template('main.html')


@app.route('/reset1',methods=["post"]) # リセット
def reset1():
   
   if "username" in session:  # セッション情報があれば削除
        session.pop('username', None)

   session.clear

   #リセット処理のため
   db.session.query(MemberList).delete() #メンバーリストを削除 
   db.session.commit()

   db2.session.query(OtherVar).delete() #OtherVarを削除 
   db2.session.commit()

   db3.session.query(OrignalGenreData).delete() #OtherVarを削除 
   db3.session.commit()

   return render_template('main.html')

## ユーザーチェック
@app.route('/memberlist_check',methods=['POST'])
def memberlist_check():

    btnid = request.form['BtnID']
    myname = session.get('username')

    content2 = db.session.query(MemberList).filter_by(id = btnid).first()
    content2.prepare_flg = 1
    db.session.commit()

    MemberList_DB = db.session.query(MemberList).all()

    flg_start = 1
    for member in MemberList_DB:
        if member.prepare_flg == 0 :
            flg_start = 0 #まだ準備できていない人がいる
            break

    word_Genre = db.session.query(OrignalGenreData).all()

    return render_template('member_list.html',MemberList_DB=MemberList_DB,myname = myname, word_Genre = word_Genre ,flg_start = flg_start)
    

@app.route("/prepare",methods=["post"]) # 開始準備確認/＊＊親だけが実行する処理
def odai_warifuri(): 
    #お題割り振り処理
    global global_ulfnum
    global word_data
    global word_num

    myname = session.get('username')
    MemberList_DB = db.session.query(MemberList).all()

    if myname is None:
        print("ユーザ名がNoneになってしまっています")
        flg_none = '1'
    else:
        flg_none = '0'

    ulfnum = int(request.form.get('number_wolf')) #ウルフの数を取得する
    print("ulfnum-->",ulfnum) 

    listsize  = len(MemberList_DB) #全体人数を取得する
   
    OtherVari = db2.session.query(OtherVar).all()

    if len(OtherVari) == 0: #この処理は一回しかできないようにする
        new1 = OtherVar()
        db2.session.add(new1)
        db2.session.commit()

        if ulfnum == 1 : #ウルフが一人の場合

            global_ulfnum = random.randint(1,listsize) #ここでウルフを決定する.
            MemberList_DB[global_ulfnum-1].ulf_flg = 1
        
        else :

            global_ulfnumh = random.sample(list(range(1,listsize + 1)),ulfnum) #ここでウルフを決定する.
            MemberList_DB[global_ulfnumh[0]-1].ulf_flg = 1
            MemberList_DB[global_ulfnumh[1]-1].ulf_flg = 1
           

        db.session.commit()
        
         #### エクセルファイルからワードを引っ張ってくる処理（これも親だけ実施する処理）
        #genre_number = int(request.form.get('genre_num'))
        [word_data,word_max_row_num] = create_word(1) #wordデータをエクセルから生成
      
        word_num = random.randint(0,len(word_data)-1) #ランダムにワードデータを一つ選択

        print("word_data,word_num---->",word_data,word_num)

        OtherVari = db2.session.query(OtherVar).all()
        OtherVari[0].word_num = word_num
        OtherVari[0].global_ulfnum = global_ulfnum ####危険なくすべき
        OtherVari[0].wolf_number = ulfnum
        OtherVari[0].mainmail = word_data[word_num][0] #　メール内容

        if word_data[word_num][1] is None: #回答例1
            OtherVari[0].ans1 = "" 
        else:
            OtherVari[0].ans1 = word_data[word_num][1] 

        if word_data[word_num][2] is None:
            OtherVari[0].ans2 = "" 
        else:
            OtherVari[0].ans2 = word_data[word_num][2] 

        if word_data[word_num][3] is None:
            OtherVari[0].ans3 = "" 
        else:
            OtherVari[0].ans3 = word_data[word_num][3]

        if word_data[word_num][4] is None:
            OtherVari[0].ans4 = "" 
        else:
            OtherVari[0].ans4 = word_data[word_num][4]
        
        if word_data[word_num][5] is None:
            OtherVari[0].ans5 = "" 
        else:
            OtherVari[0].ans5 = word_data[word_num][5] 
   
        db2.session.commit()
    
    else:
        print("子が実施ボタンを押してしまったのでは---->",OtherVari) 
    
    return render_template('member_list_prepare.html', MemberList_DB = MemberList_DB, myname = myname , flg_none = flg_none )


 ## お題配信する
@app.route("/odaihaishin",methods=["post"])
def odai_haishin():
     global word_data
     global global_ulfnum
     global word_num

     myname = session.get('username')
     MemberList_DB = db.session.query(MemberList).all() #DBからメンバーリストを割り当てる
     OtherVari = db2.session.query(OtherVar).all()

     content2 = db.session.query(MemberList).filter_by(username = myname).first()

     print("/odaihaishinnai ウルフNo→→　　",OtherVari[0].global_ulfnum)

     return render_template('odai_mail.html',MemberList_DB = MemberList_DB,myname = myname,mainmail = OtherVari[0].mainmail,ans1 =  OtherVari[0].ans1,ans2 =  OtherVari[0].ans2,ans3 =  OtherVari[0].ans3,ans4 =  OtherVari[0].ans4,ans5 =  OtherVari[0].ans5)

## 投票結果 
@app.route('/vote', methods=['POST']) 
def vote_result():
 
    myname = session.get('username')
    MemberList_DB = db.session.query(MemberList).all() #DBからメンバーリストを割り当てる
    
    #content = db.session.query(MemberList).filter_by(id=int(request.form.get('sel'))).first()
    #content.vote_num = content.vote_num + 1

    content2 = db.session.query(MemberList).filter_by(username = myname).first()
    #print("content---->",content)
    #print("content2---->",content2)
    
    content2.to_vote_minor = int(request.form.get('sel')) #マイノリティ選択肢の投票入力
    content2.to_vote_major = int(request.form.get('sel2')) #メジャー選択肢の投票入力

    db.session.commit()
    #print("content[0].vote_num コミット後",content.vote_num)  #デバッグモード

    OtherVari = db2.session.query(OtherVar).all()
    
    return render_template('vote_result.html',MemberList_DB = MemberList_DB,OtherVari=OtherVari,myname = myname)


## ゲーム継続　→　メンバー一覧ページ　
@app.route('/repeat')
def game_repeat():

    #リセット処理のため（継続のため）
    
    myname = session.get('username')
    MemberList_DB = db.session.query(MemberList).all()
    
    for member in MemberList_DB:
        member.vote_num=0
        member.ulf_flg=0
        member.to_vote_minor=0
        member.to_vote_major=0
        member.prepare_flg=0

    db.session.commit()
    
    db2.session.query(OtherVar).delete() #OtherVarを削除 
    db2.session.commit()

    word_Genre = db3.session.query(OrignalGenreData).all() 
    
    return render_template('member_list.html',MemberList_DB=MemberList_DB,myname = myname, word_Genre = word_Genre,flg_start = 0)


## メンバー一覧ページ　
@app.route('/memberlist')
def load_member_list():

    myname = session.get('username')
    MemberList_DB = db.session.query(MemberList).all()

    flg_start = 1
    for member in MemberList_DB:
        if member.prepare_flg == 0 :
            flg_start = 0 #まだ準備できていない人がいる
            break

    word_Genre = db3.session.query(OrignalGenreData).all()
    
    return render_template('member_list.html',MemberList_DB=MemberList_DB,myname = myname, word_Genre = word_Genre, flg_start=flg_start)

## お題割り振りページ　（親以外のリンク用）
@app.route('/memberlist_prepare')
def memberlist_prepare():
    
    myname = session.get('username')
    MemberList_DB = db.session.query(MemberList).all()

    OtherVari = db2.session.query(OtherVar).all()
    
    if myname is None:
        print("ユーザ名がNoneになってしまっています")
        flg_none = '1'
    else:
        flg_none = '0'


    if len(OtherVari) == 0:
        print("まだ親の人が開始ボタンを教えていません")
        return redirect(url_for('load_member_list'))
    else:
        return render_template('member_list_prepare.html',MemberList_DB = MemberList_DB,myname = myname,flg_none = flg_none)
   

## 投票結果　
@app.route('/result')
def result():
    myname = session.get('username')
    MemberList_DB = db.session.query(MemberList).all() #DBからメンバーリストを割り当てる

    OtherVari = db2.session.query(OtherVar).all()

    return render_template('vote_result.html',MemberList_DB =MemberList_DB,OtherVari=OtherVari,myname = myname)

## 利用規約
@app.route('/terms') 
def terms_of_service():
    return render_template('terms.html')

## ページが間違うとmain
@app.errorhandler(404) 
def redirect_main_page(error):
    return redirect(url_for('main'))

if __name__ == '__main__':
    #db.create_all()
    #db2.create_all()
    #db3.create_all()
    app.run(debug=True)
