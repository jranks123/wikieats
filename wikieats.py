import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app
import webapp2

HEADER_TEMPLATE = """<html><body><div style="position: absolute; width: 99%; height: 100px; background: cyan;">Header</div>
<div style="position: absolute; box-sizing:border-box; -moz-box-sizing:border-box; padding-top: 100px; padding-bottom: 50px; width: 99%; height: 99%;">"""

FOOTER_TEMPLATE = """</div><div style="position: absolute; bottom: 0; background: lightgreen; width: 99%; height: 50px;">Footer</div></body></html>"""

MAIN_PAGE_TEMPLATE = """\
		</p></p>
		<a href="addNew">Add new photo</a>
        <p></p>
        <a href="browse">Browse</a>
"""




SEARCH_RESTAURANT_TEMPLATE = """\
	<form action="/submitSearchRestaurant/%s" method="post">
		Restaurant Name:<br>
		<input type="text" name="rest_name" value="">
		<br>
		<input type="submit" value="Submit">
	</form>
"""




ADD_RESTAURANT_TEMPLATE = """\
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
"""


ADD_NEW_RESTAURANT_TEMPLATE = """\
	<form action="/postrestaurant2/%s" method="post">
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
		Postcode:<div><input name="rest_postcode"></div>
		Phone Number:<div><input name="rest_phone"></div>
		<div><input type="submit" value="ADD RESTAURANT"></div>
	</form>
"""

ADD_DISH_TEMPLATE = """\
	<form action="/postdish/%s/%s" method="post">
		Name Of Dish:<div><input name="dish_name"></div>
		Price (&pound):<div><input name="dish_price"></div>
		</p>
		<div><input type="submit" value="Add Dish"></div>
	</form>
"""

ADD_NEW_DISH_TEMPLATE = """\
	<form action="/postdish2/%s/%s" method="post">
		Name Of Dish:<div><input name="dish_name"></div>
		Price (&pound):<div><input name="dish_price"></div>
		</p>
		<div><input type="submit" value="Add Dish"></div>
	</form>
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
"""


#####################################
########## DATABASE MODELS ##########
#####################################
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

class Photo(ndb.Model):
    rating = ndb.IntegerProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add = True)
    review = ndb.StringProperty(required=False)
    blob_key = ndb.BlobKeyProperty(required=False)  


######################################
########## REQUEST HANDLERS ##########
######################################
class MainPage(webapp2.RequestHandler):
	def get(self):
		self.response.write(HEADER_TEMPLATE)
		#restaurants = Restaurant.query()
		
		#for r in restaurants:
		#	self.response.write(r.name)
		#	self.response.write('<form action="/displayrestaurant" method="get"><input type="submit" value="View"></form>')
			
		#	self.response.write('<form action="/editrestaurant" method="get"><input type="submit" value="Edit"></form>')
		#	self.response.write('</p>')
		
		self.response.write(MAIN_PAGE_TEMPLATE)
		self.response.write(FOOTER_TEMPLATE)

class AddRestaurant(webapp2.RequestHandler):
	def get(self, resource, name):
		self.response.write(ADD_RESTAURANT_TEMPLATE % (resource, name))

class searchRestaurant(webapp2.RequestHandler):
    def get(self):
        self.response.write(SEARCH_RESTAURANT_TEMPLATE)

class searchCity(webapp2.RequestHandler):
	def get(self):
		self.response.write(HEADER_TEMPLATE)
		cities = City.query().order(City.city)
		
		self.response.write('<form action="/selectcity2" method="post"><div><select name="city_link">')
		for c in cities:
			self.response.write('<option value="%s">%s</option>' % (c.key.id(), c.city))
		self.response.write('</select><input type="submit" value="SUBMIT"></div></form>');
		self.response.write('<a href="/"><< BACK</a>')
		self.response.write(FOOTER_TEMPLATE)
		
class SelectCity2(webapp2.RequestHandler):
    def post(self):
		city_link = self.request.get('city_link')
		self.redirect('/city/%s' % (city_link))

class submitSearchRestaurant(webapp2.RequestHandler):
    def post(self, resource):
        name = self.request.get('rest_name')
        check = False
        #need to add in check for right city
        result = Restaurant.query(ancestor = ndb.Key('City', int(resource))).filter(Restaurant.name == name)
        try:
            for r in result:
                check = True
                self.redirect('/viewDish/%s/%s' % (resource, r.key.id()))
            if check == False:
				self.response.write(HEADER_TEMPLATE)
				self.response.write(ADD_RESTAURANT_TEMPLATE % (resource, name))
				self.response.write(FOOTER_TEMPLATE)
                
        except:
			self.response.write(HEADER_TEMPLATE)
			self.response.write(ADD_RESTAURANT_TEMPLATE % (resource, name))
			self.response.write(FOOTER_TEMPLATE)

class cityHandler(webapp2.RequestHandler):
    def get(self, resource):
        self.response.write(SEARCH_RESTAURANT_TEMPLATE % resource)

class viewDish(webapp2.RequestHandler):
	def get(self, city, rest):
		rkey = ndb.Key('City', int(city), 'Restaurant', int(rest))
		self.response.write(HEADER_TEMPLATE)
		self.response.out.write('<a>Please select from the dishes below<br>')
		result = Dish.query(ancestor = rkey)
		check = False
		for r in result:
			check = True
			self.response.write('<a href=/uploadPhotoPage/%s/%s/%s>%s</a><br>' % (city, rest, r.key.id(), r.name))
		if check == False:
			self.redirect('/addDish/%s/%s' % (city, rest))
		self.response.out.write('<button><a href="/addDish/%s/%s">Cant see what your looking for/ Click here to add a new dish</a></button>' % (city, rest))
		self.response.write(FOOTER_TEMPLATE)
		
class addDish(webapp2.RequestHandler):
    def get(self, city, rest):
        self.response.out.write(ADD_DISH_TEMPLATE % (city,rest))

class postdish(webapp2.RequestHandler):
	def post(self, city, rest):
		rkey = ndb.Key('City', int(city), 'Restaurant', int(rest))
		#this ensures that an adversay cannot inject dishes to restaurants that do not exist in the database
		if rkey.get() == None:
			self.redirect('/')
		else:
			r = Dish(parent=rkey)
			r.name = self.request.get('dish_name')
			r.price = self.request.get('dish_price')
			r.put()
			check = False
			while check == False:
				result = Dish.query(ancestor = rkey).filter(Dish.name == r.name)
				for r in result:
					check = True
					self.redirect('/uploadPhotoPage/%s/%s/%s' % (city, rest, r.key.id()))

class PostRestaurant(webapp2.RequestHandler):
    def post(self, resource):
        rkey = ndb.Key('City', int(resource))
        #this makes sure that adversary cannot insert restaurant into non-existing City in the database
        if rkey.get() == None:
            self.redirect('/')
        else:
            r = Restaurant(parent= rkey)
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
		
		
##############################
########## BROWSING ##########
##############################		
class BrowseCities(webapp2.RequestHandler):
	def get(self):
		self.response.write(HEADER_TEMPLATE)
		cities = City.query().order(City.city)
		
		self.response.write('<form action="/selectcity" method="post"><div><select name="city_link">')
		for c in cities:
			#self.response.write('<a href="/browse/%s">%s</a></p>' % (c.key.id(),c.city))
			self.response.write('<option value="%s">%s</option>' % (c.key.id(), c.city))
		self.response.write('</select><input type="submit" value="GO"></div></form>');
		self.response.write('<a href="/"><< BACK</a>')
		self.response.write(FOOTER_TEMPLATE)
		
class SelectCity(webapp2.RequestHandler):
    def post(self):
		city_link = self.request.get('city_link')
		self.redirect('/browse/%s' % (city_link))
		
class BrowseRestaurants(webapp2.RequestHandler):
	def get(self, city):
		city_key = ndb.Key('City', int(city))
		result = Restaurant.query(ancestor = city_key).order(Restaurant.name)
		check = False
		self.response.write(HEADER_TEMPLATE)
		for r in result:
			check = True
			self.response.write('<a href="/browse/%s/%s">%s</a></p></p>' % (city, r.key.id(), r.name))
			
		if check == False:
			self.response.write('No restaurants in this city.')
		
		self.response.write('</p><a href="/addnewrestaurant/%s"><input type="submit" value="ADD NEW RESTAURANT"></a>' % (city))
		self.response.write('</p><a href="/browse"><< BACK</a>')
		self.response.write(FOOTER_TEMPLATE)
		
class BrowseDishes(webapp2.RequestHandler):
	def get(self, city, rest):
		rest_key = ndb.Key('City', int(city), 'Restaurant', int(rest))
		result = Dish.query(ancestor = rest_key).order(Dish.name)
		check = False
		self.response.write(HEADER_TEMPLATE)
		for d in result:
			check = True
			self.response.write('<a href="/browse/%s/%s/%s">%s</a></p></p>' % (city, rest, d.key.id(), d.name))
		if check == False:
			self.response.write('No dishes in this restaurant.')
		self.response.write('</p><a href="/addnewdish/%s/%s"><input type="submit" value="ADD NEW DISH"></a>' % (city, rest))
		self.response.write('</p><a href="/browse/%s"><< BACK</a>' % (city))
		self.response.write(FOOTER_TEMPLATE)
		
class DisplayDish(webapp2.RequestHandler):
	def get(self, city, rest, dish):
		photo_key = ndb.Key('City', int(city), 'Restaurant', int(rest), 'Dish' , int(dish))
		result = Photo.query(ancestor = photo_key).order(-Photo.created).fetch(10)
		check = False
		self.response.write(HEADER_TEMPLATE)
		
		for p in result:
			check = True
			blob_info = blobstore.BlobInfo.get(p.blob_key)
			self.response.write('<img src="/serve/%s" height="500" width="500">' % (p.blob_key))
				
		if check == False:
			self.response.write('No photos of this dish.')
			
		self.response.write('</p><a href="/uploadPhotoPage/%s/%s/%s"><input type="submit" value="Upload"></a>' % (city, rest, dish))
		self.response.write('</p><a href="/browse/%s/%s"><< BACK</a>' % (city, rest))
		self.response.write(FOOTER_TEMPLATE)
		

#########################################
########## ADD WHILST BROWSING ##########
#########################################
class AddNewRestaurant(webapp2.RequestHandler):
	def get(self, city):
		self.response.out.write(ADD_NEW_RESTAURANT_TEMPLATE % (city))
		
class PostRestaurant2(webapp2.RequestHandler):
    def post(self, city):
        rkey = ndb.Key('City', int(city))
        #this makes sure that adversary cannot insert restaurant into non-existing City in the database
        if rkey.get() == None:
            self.redirect('/')
        else:
            r = Restaurant(parent= rkey)
            r.name = self.request.get('rest_name')
            r.cuisine = self.request.get('rest_type')
            r.postcode = self.request.get('rest_postcode')
            r.phone = self.request.get('rest_phone')
            r.put()
            check2 = False
            while check2 == False:
                result = Restaurant.query(ancestor = ndb.Key('City', int(city))).filter(Restaurant.name == r.name)
                for r in result:
                    check2 = True
                    self.redirect('/browse/%s' % (city))
		
class AddNewDish(webapp2.RequestHandler):
	def get(self, city, rest):
		self.response.out.write(ADD_NEW_DISH_TEMPLATE % (city, rest))

class PostDish2(webapp2.RequestHandler):
	def post(self, city, rest):
		rkey = ndb.Key('City', int(city), 'Restaurant', int(rest))
		#this ensures that an adversay cannot inject dishes to restaurants that do not exist in the database
		if rkey.get() == None:
			self.redirect('/browse/%s/%s' % (city, rest))
		else:
			r = Dish(parent=rkey)
			r.name = self.request.get('dish_name')
			r.price = self.request.get('dish_price')
			r.put()
			check = False
			while check == False:
				result = Dish.query(ancestor = rkey).filter(Dish.name == r.name)
				for r in result:
					check = True
					self.redirect('/browse/%s/%s' % (city, rest))

					
##################################
########## PHOTO UPLOAD ##########
##################################
class uploadPhotoPage(webapp2.RequestHandler):
    def get(self, city, rest, dish):
		upload_url = blobstore.create_upload_url('/upload/%s/%s/%s' % (city, rest, dish))
		self.response.write(HEADER_TEMPLATE)
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
                </form>""")
		self.response.write(FOOTER_TEMPLATE)



class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, city, rest, dish):
         try:
            # 'file' is file upload field in the form
            upload_files = self.get_uploads()
            blob_info = upload_files[0]
            rkey = ndb.Key('City', int(city), 'Restaurant', int(rest), 'Dish' , int(dish))
            r = Photo(parent = rkey)
            r.rating = int(self.request.get('rating'))
            r.review = self.request.get('review')
            r.blob_key = blob_info.key()
            r.put()
            #this will serve the photo on the whole page
            #self.redirect('/serve/%s' % blob_info.key())
            self.redirect('/browse/%s/%s/%s' % (city, rest, dish))
         except:
            self.redirect('/browse/%s/%s/%s' % (city, rest, dish))

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)

		
##### IGNORE THIS FOR NOW #####
#class UploadNewPhoto(webapp2.RequestHandler):
#	def get(self):
		
		# photo upload form
#		self.response.write(HEADER_TEMPLATE)
#		self.response.write('<form action="/postnewphoto" method="post">')
		
		# select city dropdown menu
#		cities = City.query().order(City.city)
#		self.response.write('<div>City:<select name="city_link">')
#		for c in cities:
#			self.response.write('<option value="%s">%s</option>' % (c.key.id(), c.city))
#		self.response.write('</select></div></p>')
		
		# input restaurant name
#		self.response.write('<div>Restaurant:<input type="text" name="rest_name"></div></p>')
		
		# input dish info
#		self.response.write('<div>Name Of Dish:<input name="dish_name"></div></p>')
#		self.response.write('<div>Price (&pound):<input name="dish_price"></div></p>')
		
		# input photo info
#		self.response.write('<div>Image:<input type="file" name="file"></div>')
#		self.response.write('<div>Review:<textarea name="review" rows="3" cols="60"></textarea></div>')
#		self.response.write('<div>Rating:<select name="rating">')
#		self.response.write('<option value="1">1</option>')
#		self.response.write('<option value="2">2</option>')
#		self.response.write('<option value="3">3</option>')
#		self.response.write('<option value="4">4</option>')
#		self.response.write('<option value="5">5</option>')
#		self.response.write('</select></div>')
		
#		self.response.write('<input type="submit" value="SUBMIT">')
#		self.response.write('</form><a href="/"><< BACK</a>')
#		self.response.write(FOOTER_TEMPLATE)
	
#class PostNewPhoto(webapp2.RequestHandler):
#	def post(self):
#		self.response.write('<html><body>hello</body></html>')
#		self.redirect('/')


application = webapp2.WSGIApplication([
    ('/', MainPage),
#    ('/unp', UploadNewPhoto),
#    ('/postnewphoto', PostNewPhoto),
	
	##### BROWSING #####
    ('/browse', BrowseCities),
    ('/selectcity', SelectCity),
    ('/browse/([^/]+)?', BrowseRestaurants),
    ('/browse/([^/]+)?/([^/]+)?', BrowseDishes),
    ('/browse/([^/]+)?/([^/]+)?/([^/]+)?', DisplayDish),
	
	##### ADD WHILST BROWSING #####
    ('/addnewrestaurant/([^/]+)?', AddNewRestaurant),
	('/postrestaurant2/([^/]+)?', PostRestaurant2),
    ('/addnewdish/([^/]+)?/([^/]+)?', AddNewDish),
    ('/postdish2/([^/]+)?/([^/]+)?', PostDish2),
	
    ('/submitSearchRestaurant', submitSearchRestaurant),

	##### ADD WHILST UPLOADING PHOTO #####
	('/addNew', searchCity),
	('/selectcity2', SelectCity2),
	('/city/([^/]+)?', cityHandler),
    ('/addrestaurant/([^/]+)?/([^/]+)?', AddRestaurant),
	('/postrestaurant/([^/]+)?', PostRestaurant),
	('/addDish/([^/]+)?/([^/]+)?', addDish),
    ('/postdish/([^/]+)?/([^/]+)?', postdish),

    ('/uploadPhotoPage/([^/]+)?/([^/]+)?/([^/]+)?', uploadPhotoPage),
	
	##### IMAGE UPLOAD AND SERVING #####
    ('/upload/([^/]+)?/([^/]+)?/([^/]+)?', UploadHandler),
    ('/serve/([^/]+)?', ServeHandler),
	
    ('/viewDish/([^/]+)?/([^/]+)?', viewDish),
    
    ('/submitSearchRestaurant/([^/]+)?', submitSearchRestaurant)
], debug=True)