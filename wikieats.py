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

class Restaurant(ndb.Model):
	name = ndb.StringProperty(required=True)
	cuisine = ndb.StringProperty(required=True)
	city = ndb.StringProperty(required=True)
	postcode = ndb.StringProperty(required=False)
	phone = ndb.StringProperty(required=False)
	created = ndb.DateTimeProperty(auto_now_add=True)







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

class photo(ndb.Model):
    rating = ndb.IntegerProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add = True)
    review = ndb.StringProperty(required=False)
    blob_key = ndb.BlobKeyProperty(required=False)

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        self.response.out.write('<html><body>')
        # 'file' is file upload field in the form
        upload_files = self.get_uploads()
        blob_info = upload_files[0]
        r = photo()
        r.rating = int(self.request.get('rating'))
        r.review = self.request.get('review')
        r.blob_key = blob_info.key()
        r.put()
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
    ('/uploadPhotoPage', uploadPhotoPage),
    ('/upload', UploadHandler),
    ('/serve/([^/]+)?', ServeHandler),
], debug=True)