import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import webapp2

MAIN_PAGE_TEMPLATE = """\
		</p></p>
		<a href="addNew">Add new photo</a>
        <p></p>
        <a href="Browse">Browse resteraunts</a>
        <p></p>
        <a href="/adddish">Add New Dish</a>
	</body>
</html>
"""



SEARCH_RESTAURANT_TEMPLATE = """\
    <html>
        <body>
            <form action="/submitSearchRestaurant" method="post">
                Restaurant Name:<br>
                <input type="text" name="rest_name" value="">
                <br>
                <input type="submit" value="Submit">
            </form>  
        </body>
    </html>
    """

#<a href="/addrestaurant">Add a Restaurant to the datastore</a>


ADD_RESTAURANT_TEMPLATE = """\
<html>
	<body>
		<form action="/postrestaurant" method="post">
			Name:<div><input name="rest_name"></div>
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
			City:<div><input name="rest_city"></div>
			Postcode:<div><input name="rest_postcode"></div>
			Phone Number:<div><input name="rest_phone"></div>
			<div><input type="submit" value="ADD RESTAURANT"></div>
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

ADD_DISH_TEMPLATE = """\
<html>
	<body>
		<form action="/postdish" method="post">
			Name:<div><input name="dish_name"></div>
			Price (&pound): <div><input name="dish_price"></div>
			Average Rating:<div><input name="avg_rate"></div>
			Restaurant:<div><input name="rest_name"></div>
			<div><input type="submit" value="ADD DISH"></div>
		</form>
	</body>
</html>
"""

class Restaurant(ndb.Model):
	name = ndb.StringProperty(required=True)
	cuisine = ndb.StringProperty(required=True)
	city = ndb.StringProperty(required=True)
	postcode = ndb.StringProperty(required=False)
	phone = ndb.StringProperty(required=False)
	created = ndb.DateTimeProperty(auto_now_add=True)

class Dish(ndb.Model):
	name = ndb.StringProperty(required=True)
	price = ndb.StringProperty(required=False)
	rating = ndb.StringProperty(required=False)

class MainPage(webapp2.RequestHandler):
	def get(self):
		self.response.write('<html><body>')
		restaurants = Restaurant.query()
		
		for r in restaurants:
			self.response.write(r.name)
			self.response.write('<form action="/displayrestaurant" method="get"><input type="submit" value="View"></form>')
			
			self.response.write('<form action="/editrestaurant" method="get"><input type="submit" value="Edit"></form>')
			self.response.write('</p>')
		
		self.response.write(MAIN_PAGE_TEMPLATE) 

class AddRestaurant(webapp2.RequestHandler):
	def get(self):
		self.response.write(ADD_RESTAURANT_TEMPLATE)
	
class PostRestaurant(webapp2.RequestHandler):
	def post(self):
		r = Restaurant()
		r.name = self.request.get('rest_name')
		r.cuisine = self.request.get('rest_type')
		r.city = self.request.get('rest_city')
		r.postcode = self.request.get('rest_postcode')
		r.phone = self.request.get('rest_phone')
		r.put()
		self.redirect('/')
		
class searchRestaurant(webapp2.RequestHandler):
    def get(self):
        self.response.write(SEARCH_RESTAURANT_TEMPLATE)

class submitSearchRestaurant(webapp2.RequestHandler):
    def post(self):
        name = self.request.get('rest_name')
        check = False
        result = Restaurant.query(Restaurant.name == name)
        self.response.out.write('<html><body>')
        for r in result:
            check = True
            self.response.write(r.name)
        if check == False:
            self.response.write('<a href="/addrestaurant">Sorry we could not find your restaurant, click here to add a new restaurant</a>')

class DisplayRestaurant(webapp2.RequestHandler):
	def get(self):
		self.response.write('<html><body><b>')
		self.response.write(r.name)
		self.response.write('</b>')
		
class EditRestaurant(webapp2.RequestHandler):
	def get(self):
		self.response.write('<html><body>')
		self.response.write(EDIT_RESTAURANT_TEMPLATE)
		
class AddDish(webapp2.RequestHandler):
	def get(self):
		self.response.write(ADD_DISH_TEMPLATE)
		
class PostDish(webapp2.RequestHandler):
	def post(self):
	
		#qry = Restaurant.query(Restaurant.name == 'rest_name')
		#r = qry.fetch(1)
		#d = Dish(parent = r.id())
		
		d = Dish()
		d.name = self.request.get('dish_name')
		d.price = self.request.get('dish_price')
		d.rating = self.request.get('avg_rate')
		
		d.put()
		self.redirect('/')

class uploadPhotoPage(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload')
        self.response.out.write('<html><body>')
        self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
        self.response.out.write("""Upload File: 
                <input type="file" name="file"><br> <input type="submit"
                name="submit" value="Submit"> </form></body></html>""")

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        # 'file' is file upload field in the form
        upload_files = self.get_uploads('file')
        blob_info = upload_files[0]
        self.redirect('/serve/%s' % blob_info.key())

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)


application = webapp2.WSGIApplication([
	('/', MainPage),
	('/addNew', searchRestaurant),
	('/submitSearchRestaurant', submitSearchRestaurant),
	('/addrestaurant', AddRestaurant),
	('/postrestaurant', PostRestaurant),
	('/displayrestaurant', MainPage),
	('/editrestaurant', MainPage),
	('/adddish', AddDish),
	('/postdish', PostDish),
	('/uploadPhotoPage', uploadPhotoPage),
	('/upload', UploadHandler),
	('/serve/([^/]+)?', ServeHandler),
], debug=True)