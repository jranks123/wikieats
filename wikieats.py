import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app
import webapp2

MAIN_PAGE_TEMPLATE = """\
		</p></p>
		<a href="addNew">Add new photo</a>
        <p></p>
        <a href="browse">Browse resteraunts</a>
	</body>
</html>
"""

SEARCH_CITY_TEMPLATE = """\
    <html>
        <body>
            <form action="/submitSearchCity" method="post">
                City:<br>
                <input type="text" name="city_name" value="">
                <br>
                <input type="submit" value="Submit">
            </form>  
        </body>
    </html>
    """


SEARCH_RESTAURANT_TEMPLATE = """\
    <html>
        <body>
            <form action="/submitSearchRestaurant/%s" method="post">
                Restaurant Name:<br>
                <input type="text" name="rest_name" value="">
                <br>
                <input type="submit" value="Submit">
            </form>  
        </body>
    </html>
    """




ADD_RESTAURANT_TEMPLATE = """\
<html>
	<body>
        <a>Sorry we could not find that Restaurant. Please fill in the form below to add it</a>
		<form action="/postrestaurant/%s" method="post">
			Name:<div><input name="rest_name" value="%s"></div>
			Cuisine:
			<div>
				<select name="rest_type">
					<option value="indian">Indian</option>
					<option value="pizza">Pizza</option>
					<option value="chinese">Chinese</option>
					<option value="kebab">Kebab</option>
					<option value="italian">Italian</option>
					<option value="fishandchips">Fish & Chips</option>
					<option value="america">American</option>
					<option value="chicken">Chicken</option>
					<option value="carribean">Carribean</option>
				</select>
			</div>
			Postcode:<div><input name="rest_postcode"></div>
			Phone Number:<div><input name="rest_phone"></div>
			<div><input type="submit" value="ADD RESTAURANT"></div>
		</form>
	</body>
</html>
"""


ADD_DISH_TEMPLATE = """\
<html>
    <body>
        <form action="/postdish/%s/%s" method="post">
            Name Of Dish:<div><input name="dish_name"></div>
            <div><input type="submit" value="Add Dish"></div>
        </form>
    </body>
</html>
"""

EDIT_RESTAURANT_TEMPLATE = """\
		<form action="/postrestaurant" method="post">
			Name:<div><input value="%s" name="rest_name"></div>
			Cuisine:
			<div>
				<select name="rest_type">
					<option value="indian">Indian</option>
					<option value="pizza">Pizza</option>
					<option value="chinese">Chinese</option>
					<option value="kebab">Kebab</option>
					<option value="italian">Italian</option>
					<option value="fishandchips">Fish & Chips</option>
					<option value="america">American</option>
					<option value="chicken">Chicken</option>
					<option value="carribean">Carribean</option>
				</select>
			</div>
			City:<div><input value="%s" name="rest_city"></div>
			Postcode:<div><input value="%s" name="rest_postcode"></div>
			Phone Number:<div><input value="%s" name="rest_phone"></div>
			<div><input type="submit" value="ADD RESTAURANT"></div>
		</form>
	</body>
</html>
"""

class City(ndb.Model):
    city = ndb.StringProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)



class Restaurant(ndb.Model):
	name = ndb.StringProperty(required=True)
	cuisine = ndb.StringProperty(required=True)
	postcode = ndb.StringProperty(required=False)
	phone = ndb.StringProperty(required=False)
	created = ndb.DateTimeProperty(auto_now_add=True)


class Dish(ndb.Model):
    name = ndb.StringProperty(required=True)
    price = ndb.StringProperty(required=False)


class photo(ndb.Model):
    rating = ndb.IntegerProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add = True)
    review = ndb.StringProperty(required=False)
    blob_key = ndb.BlobKeyProperty(required=False)  




class MainPage(webapp2.RequestHandler):
	def get(self):
		self.response.write('<html><body>')
		#restaurants = Restaurant.query()
		
		#for r in restaurants:
		#	self.response.write(r.name)
		#	self.response.write('<form action="/displayrestaurant" method="get"><input type="submit" value="View"></form>')
			
		#	self.response.write('<form action="/editrestaurant" method="get"><input type="submit" value="Edit"></form>')
		#	self.response.write('</p>')
		
		self.response.write(MAIN_PAGE_TEMPLATE) 

class AddRestaurant(webapp2.RequestHandler):
	def get(self, resource, name):
		self.response.write(ADD_RESTAURANT_TEMPLATE % (resource, name))

class searchRestaurant(webapp2.RequestHandler):
    def get(self):
        self.response.write(SEARCH_RESTAURANT_TEMPLATE)

class searchCity(webapp2.RequestHandler):
    def get(self):
        self.response.write(SEARCH_CITY_TEMPLATE)



class submitSearchRestaurant(webapp2.RequestHandler):
    def post(self, resource):
        name = self.request.get('rest_name')
        check = False
        #need to add in check for right city
        result = Restaurant.query(ancestor = ndb.Key('City', int(resource))).filter(Restaurant.name == name)
        self.response.out.write('<html><body>')
        try:
            for r in result:
                check = True
                self.redirect('/viewDish/%s/%s' % (resource, r.key.id()))
            if check == False:
                self.response.write(ADD_RESTAURANT_TEMPLATE % (resource, name))
                
        except:
            self.response.write(ADD_RESTAURANT_TEMPLATE % (resource, name))


class submitSearchCity(webapp2.RequestHandler):
    def post(self):
        city = self.request.get('city_name')
        check = False
        result = City.query(City.city == city)
        self.response.out.write('<html><body>')
        for r in result:
            check = True
            self.redirect('/city/%s' % r.key.id())
        if check == False:
            q = City()
            q.city = self.request.get('city_name')
            q.put()
            check2 = False
            while check2 == False:
                result = City.query(City.city == city)
                for r in result:
                    check2 = True
                    self.redirect('/city/%s' % r.key.id())
                


class cityHandler(webapp2.RequestHandler):
    def get(self, resource):
        self.response.write(SEARCH_RESTAURANT_TEMPLATE % resource)

        
class viewDish(webapp2.RequestHandler):
    def get(self, city, rest):
        self.response.out.write('<html><body>')
        self.response.out.write('<a href="/addDish/%s/%s">Add Dish</a>' % (city, rest))

class addDish(webapp2.RequestHandler):
    def get(self, city, rest):
        self.response.out.write(ADD_DISH_TEMPLATE % (city,rest))

class postdish(webapp2.RequestHandler):
    def post(self, city, rest):
        rkey = ndb.Key('City', int(city), 'Restaurant', int(rest))
        r = Dish(parent=rkey)
        r.name = self.request.get('dish_name')
        r.put()
        self.redirect('/');


class viewRestaurant(webapp2.RequestHandler):
    def get(self, resource):
        self.response.out.write('<html><body>')
        self.response.write(r.name)

	
class PostRestaurant(webapp2.RequestHandler):
	def post(self, resource):
		r = Restaurant(parent=ndb.Key('City', int(resource)))
		r.name = self.request.get('rest_name')
		r.cuisine = self.request.get('rest_type')
		r.postcode = self.request.get('rest_postcode')
		r.phone = self.request.get('rest_phone')
		r.put()
                check2 = False
                while check2 == False:
                    result = Restaurant.query(ancestor = ndb.Key('City', int(resource))).filter(Restaurant.name == r.name)
                    for r in result:
                        check2 = True
                        self.redirect('/viewDish/%s/%s' % (resource, r.key.id()))

		
class DisplayRestaurant(webapp2.RequestHandler):
	def get(self):
		self.response.write('<html><body><b>')
		self.response.write(r.name)
		self.response.write('</b>')
		
class EditRestaurant(webapp2.RequestHandler):
	def get(self):
		self.response.write('<html><body>')
		self.response.write(EDIT_RESTAURANT_TEMPLATE)


class uploadPhotoPage(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload')
        self.response.out.write('<html><body>')
        self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
        self.response.out.write("""Upload File: 
                <input type="file" name="file"><br> 
                Review<div><textarea name="review" rows="3" cols="60"></textarea></div>
                Rating:
                <div>
                    <select name="rating">
                        <option value="1">1</option>
                        <option value="2">2</option>
                        <option value="3">3</option>
                        <option value="4">4</option>
                        <option value="5">5</option>
                    </select>
                </div>
                <input type="submit"name="submit" value="Submit"> 
                </form></body></html>""")



class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
         try:
            # 'file' is file upload field in the form
            upload_files = self.get_uploads()
            blob_info = upload_files[0]
            r = photo()
            r.rating = int(self.request.get('rating'))
            r.review = self.request.get('review')
            r.blob_key = blob_info.key()
            r.put()
            self.redirect('/serve/%s' % blob_info.key())
         except:
            self.redirect('/')

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/addNew', searchCity),
    ('/submitSearchRestaurant', submitSearchRestaurant),
    ('/viewRestaurant', viewRestaurant),
    ('/submitSearchCity', submitSearchCity),
    ('/addrestaurant/([^/]+)?/([^/]+)?', AddRestaurant),
	('/postrestaurant/([^/]+)?', PostRestaurant),
	('/displayrestaurant', MainPage),
	('/editrestaurant', MainPage),
    ('/uploadPhotoPage', uploadPhotoPage),
    ('/upload', UploadHandler),
    ('/serve/([^/]+)?', ServeHandler),
    ('/city/([^/]+)?', cityHandler),
    ('/viewDish/([^/]+)?/([^/]+)?', viewDish),
    ('/addDish/([^/]+)?/([^/]+)?', addDish),
    ('/postdish/([^/]+)?/([^/]+)?', postdish),
    ('/submitSearchRestaurant/([^/]+)?', submitSearchRestaurant)
], debug=True)