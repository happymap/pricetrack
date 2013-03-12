from bottle import route, run, template
import urllib2
import pymongo
import bottle
import json
import datetime

connection_string = "mongodb://localhost"

# search google shopping API
@bottle.route('/:key')
def index(key=''):
    connection = pymongo.Connection(connection_string, safe=True)
    db = connection.blog
    posts = db.posts
    print "the num of posts: " + str(posts.count())
    
    api = 'AIzaSyDz2oQ85knuniOtuUbu8p7GFZKdhIjaJN4'
    url = 'https://www.googleapis.com/shopping/search/v1/public/products?key='+api+'&country=US&q='+key+'&alt=JSON'
    data = urllib2.urlopen(url).read()
    return template('{{name}}',name=data)

# insert a new user
@bottle.post('/newuser')
def post_newuser():
    name = bottle.request.forms.get("newUser")
    #password = bottle.request.forms.get("newPwd")
    email = bottle.request.forms.get("newEmail")

    #print "name:"+name

    connection = pymongo.Connection(connection_string, safe=True)
    db = connection.pricetrack
    users = db.users

    user = {"name":name,
            "email":email,
            "list":[]}

    try:
        users.insert(user)
        print "Add new user"

    except:
        print "Error inserting user"
        print "Unexpected error:", sys.exc_info()[0]

# insert a new item into wishing list
@bottle.post('/newitem')
def post_newitem():
    email = bottle.request.forms.get("email")
    productId = bottle.request.forms.get("productid")
    merchantId = bottle.request.forms.get("merchantid")

    connection = pymongo.Connection(connection_string, safe=True)
    db = connection.pricetrack
    users = db.users

    try:
        users.update({"email":email},{"$push":{"list":{"pid":productId, "mid":merchantId}}})
        print "Add new productId"

    except:
        print "Error add productId"
        print "Unexpected error:", sys.exc_info()[0]
        
# insert a price record
@bottle.post('/newprice')
def add_newprice():
    pid = bottle.request.forms.get("pid")
    mid = bottle.request.forms.get("mid")
    
    connection = pymongo.Connection(connection_string, safe=True)
    db = connection.pricetrack
    items = db.items

    price = fetch_newprice(pid, mid)

    try:
        items.insert({"pid":pid,"mid":mid,"price":price,"date":datetime.datetime.utcnow()})
        print "Add new price"

    except:
        print "Error add price"
        print "Unexpected error:", sys.exc_info()[0]
        

# get a new price
def fetch_newprice(pid, mid):
    #pid = '11972006473052128578'
    #mid = '428871'
    key = 'AIzaSyDz2oQ85knuniOtuUbu8p7GFZKdhIjaJN4'
    url = 'https://www.googleapis.com/shopping/search/v1/public/products/'+mid+'/gid/'+pid+'?key='+key+'&country=US&alt=JSON'
    data = urllib2.urlopen(url)
    json_data = json.load(data)
    return json_data['product']['inventories'][0]['price']


run(host='0.0.0.0',port=8080)
