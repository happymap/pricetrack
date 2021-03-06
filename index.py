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

#insert a new item into wishing list
@bottle.post('/newitem')
def post_newitem():
    email = bottle.request.forms.get("email")
    productId = bottle.request.forms.get("productid")
    merchantId = bottle.request.forms.get("merchantid")
    link = bottle.request.forms.get("link")
    image_link = bottle.request.forms.get("imagelink")
    title = bottle.request.forms.get("title")
    description = bottle.request.forms.get("description")
    condition = bottle.request.forms.get("condition")
    merchant_name = bottle.request.forms.get("merchantname")
    status = bottle.request.forms.get("status")
    price = bottle.request.forms.get("price")

    print "merchant_name:"+image_link

    connection = pymongo.Connection(connection_string, safe=True)
    db = connection.pricetrack
    users = db.users
    items = db.items

    try:
        users.update({"email":email},{"$push":{"list":{"pid":productId, "mid":merchantId}}})

        item = items.find_one({"mid":merchantId, "pid":productId})
        if item == None:
            items.insert({"pid":productId,
                          "mid":merchantId,
                          "link":link,
                          "imagelink":image_link,
                          "title":title,
                          "description":description,
                          "condition":condition,
                          "merchantname":merchant_name,
                          "status":status,
                          "price":[]})

        print "Add new productId"

    except:
        print "Error add productId"
        print "Unexpected error:", sys.exc_info()[0]
        
# insert a price record
@bottle.post('/newprice')
def add_newprice():
    pid = bottle.request.forms.get("pid")
    mid = bottle.request.forms.get("mid")
    
    merchant_name = bottle.request.forms.get("merchantname")
    title = bottle.request.forms.get("title")
    description = bottle.request.forms.get("description")
    link = bottle.request.forms.get("link")
    condition = bottle.request.forms.get("condition")
    price = bottle.request.forms.get("price")
    image_link = bottle.request.forms.get("imagelink")
    status = bottle.request.forms.get("status")
    
    connection = pymongo.Connection(connection_string, safe=True)
    db = connection.pricetrack
    items = db.items

    price = fetch_newprice(pid, mid)

    item = items.find_one({"pid":pid,"mid":mid})
    if item == None:
        print "No such item"
        try:
            items.insert({"pid":pid,
                          "mid":mid,
                          "merchant_name":merchant_name,
                          "title":title,
                          "description":description,
                          "link":link,
                          "condition":condition,
                          "records":[],
                          "image_link":image_link,
                          "status":status})
            print "insert an item"

        except:
            print "Error and item"
            print "Unexpected error:", sys.exc_info()[0]

    try:
        items.update({"pid":pid,"mid":mid},{"$push":{"records":{"price":price,"date":datetime.datetime.utcnow()}}})
        print "Add new price"

    except:
        print "Error add price"
        print "Unexpected error:", sys.exc_info()[0]
        

# fecth a user's wishing list
@bottle.route('/wishlist/:email')
def fetch_list(email=''):
    connection = pymongo.Connection(connection_string, safe=True)
    db = connection.pricetrack
    users = db.users
    items = db.items

    user = users.find_one({"email":email})

    if user == None:
        print "No such a user exists"

    wishlist = []
    list = user['list']

    
    for item in list:
        pid  = item['pid']
        mid = item['mid']
        product = fetch_item(pid,mid)
        if product != None:
            pro = {'link':product['link'],
                   'pid': pid,
                   'mid': mid,
                   'image_link':product['imagelink'],
                   'status':product['status'],
                   'price':product['price'],
                   'title':product['title'],
                   'merchant_name':product['merchantname'],
                   'description':product['description'],
                   'condition':product['condition']}
            wishlist.append(pro)

    return json.dumps({"items":wishlist})
   


# get a new price
def fetch_newprice(pid, mid):
    #pid = '11972006473052128578'
    #mid = '428871'
    key = 'AIzaSyDz2oQ85knuniOtuUbu8p7GFZKdhIjaJN4'
    url = 'https://www.googleapis.com/shopping/search/v1/public/products/'+mid+'/gid/'+pid+'?key='+key+'&country=US&alt=JSON'
    data = urllib2.urlopen(url)
    json_data = json.load(data)
    return json_data['product']['inventories'][0]['price']

# get a product item
def fetch_item(pid, mid):
    connection = pymongo.Connection(connection_string, safe=True)
    db = connection.pricetrack
    items = db.items

    product = items.find_one({"pid":pid,"mid":mid})

    if product == None:
        print "no such a product"
    
    return product

run(host='0.0.0.0',port=8080)
