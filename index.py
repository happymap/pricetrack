from bottle import route, run, template
import urllib2

#@route('/hello/:name')
@route('/:key')
def index(key=''):
    api = 'AIzaSyDz2oQ85knuniOtuUbu8p7GFZKdhIjaJN4'
    url = 'https://www.googleapis.com/shopping/search/v1/public/products?key='+api+'&country=US&q='+key+'&alt=JSON'
    data = urllib2.urlopen(url).read()
    return template('{{name}}',name=data)

run(host='0.0.0.0',port=8080)
