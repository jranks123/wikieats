import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app
import webapp2

HEADER_TEMPLATE = """
<html>
	<head>
		<link rel="stylesheet" type="text/css" href="/styles/image_grid.css">
		<link rel="stylesheet" type="text/css" href="/styles/star_rating.css">
	</head>
	<body>
		<div style="position:fixed; left:0px; top:0px; height:100px; width:100%; background:lightgreen; z-index:10;">
			<div style="padding:10px;">
				<a href="/"><img src="/images/wikieats_logo.png" width="99px" height="99px"></a>
			</div>
		</div>
		<div style="padding-top:110px; width:99%; height:99%;">"""

FOOTER_TEMPLATE = """
		</div>
		<div style="position:fixed; left:0px; bottom:0px; height:30px; width:100%; background:lightgreen;">Footer</div>
	</body>
</html>"""

MAIN_PAGE_TEMPLATE = """\
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
############### ADMIN ###############
#####################################
class admin(webapp2.RequestHandler):
	def get(self):
		self.response.write(HEADER_TEMPLATE)
		self.response.write('<form action="/addAllCities" method="post">')
		self.response.write('<input type = "submit" value = "Add All Cities From File"></form>')
		self.response.write('<form action="/clearDatabase" method="post">')
		self.response.write('<input type = "submit" value = "Clear Database"></form>')
		self.response.write(FOOTER_TEMPLATE)

class addAllCities(webapp2.RequestHandler):
	def post(self):
		lines = [line.strip() for line in open('cities.text')]
		for line in lines:
			r = City()
			r.city = line
			r.put()
		self.redirect('/')

class clearDatabase(webapp2.RequestHandler):
	def post(self):
		ndb.delete_multi(
			City.query().fetch(keys_only=True)
			)
		ndb.delete_multi(
			Restaurant.query().fetch(keys_only=True)
			)
		ndb.delete_multi(
			Dish.query().fetch(keys_only=True)
			)
		ndb.delete_multi(
			Photo.query().fetch(keys_only=True)
			)
		self.redirect('/')





#ndb.delete_multi(
  #  Game.query().fetch(keys_only=True)
#)

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
	price = ndb.StringProperty(required=True)
	averageRating = ndb.FloatProperty(required=True)

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
    	self.response.write(HEADER_TEMPLATE)
        self.response.out.write(ADD_DISH_TEMPLATE % (city,rest))
        self.response.write(FOOTER_TEMPLATE)

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
			r.averageRating = 0.0
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
			self.response.write('<a href="/browse/%s/%s/%s">%s (&pound%s)</a></p></p>' % (city, rest, d.key.id(), d.name, d.price))
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
		
		d = Dish.get_by_id(photo_key.id(), photo_key.parent())
		self.response.write('<div style="display: inline-block; ">')
		self.response.write('<div style="margin: auto; float: left; display: inline-block; width: 600px;"><p style=" padding-left: 40px; font-size: 40px; font-family: \'Lucida Console\', \'Lucida Sans Typewriter\', monaco, \'Bitstream Vera Sans Mono\', monospace;"><b>%s </b>&pound%s</p></div>' % (d.name, d.price))
		

		avg_rating = d.averageRating	
		self.response.write('<div style="float:left;display: inline-block; width: 200px;margin: auto; top: 0; bottom: 0;vertical-align: middle; padding:40px 0px;">')
		self.response.write('<a>%.2f</a>' % avg_rating)
		i=0
		while i <= avg_rating and i < 5:
			if i  > 0 and i.is_integer():
				self.response.write('<img src="/images/star.png" style="display:inline;" height="40px" width="40px">')
			i = i + 0.5
				
		j = 5 - i
		if j > 0:
			if j.is_integer() == False:
				self.response.write('<img src="/images/half_star.png" style="display:inline;" height="40px" width="40px">')
				j = j - 0.5
			for k in range(int(j)):
				self.response.write('<img src="/images/star_off2.png" style="display:inline;" height="40px" width="40px">')
		
		self.response.write('</div></div>')
			
		
		
		self.response.write('<ul class="rig">')
		for p in result:
			check = True
			blob_info = blobstore.BlobInfo.get(p.blob_key)
			self.response.write('<li><img src="/serve/%s" /><p>%s/5<p><p>%s</p></li>' % (p.blob_key, p.rating, p.review))
		self.response.write('</ul>')
		
		if check == False:
			self.response.write('No photos of this dish.')
			
		self.response.write('</p><a href="/uploadPhotoPage/%s/%s/%s"><input type="submit" value="Upload"></a>' % (city, rest, dish))
		self.response.write('</p><a href="/browse/%s/%s"><< BACK</a><br><br><br>' % (city, rest))
		self.response.write(FOOTER_TEMPLATE)
		

#########################################
########## ADD WHILST BROWSING ##########
#########################################
class AddNewRestaurant(webapp2.RequestHandler):
	def get(self, city):
		self.response.write(HEADER_TEMPLATE)
		self.response.out.write(ADD_NEW_RESTAURANT_TEMPLATE % (city))
		self.response.write(HEADER_TEMPLATE)
		
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
			r.averageRating = 0.0
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
                <input type="file" name="file" required><br> 
                Review<div><textarea name="review" rows="3" cols="60"></textarea></div>
                Rating:
				<div class="rating">     
					<input type="radio" name="stars" id="5_stars" value="5" >
					<label class="stars" for="5_stars">5</label>
					<input type="radio" name="stars" id="4_stars" value="4" >
					<label class="stars" for="4_stars">4</label>
					<input type="radio" name="stars" id="3_stars" value="3" >
					<label class="stars" for="3_stars"></label>
					<input type="radio" name="stars" id="2_stars" value="2" >
					<label class="stars" for="2_stars"></label>
					<input type="radio" name="stars" id="1_stars" value="1" >
					<label class="stars" for="1_stars"></label>
					<input type="radio" name="stars" id="0_stars" value="0" selected="selected">
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
			r.review = self.request.get('review')
			r.blob_key = blob_info.key()
			r.rating = int(self.request.get('stars'))
			r.put()
			q = rkey.get()
			# Calculate average rating
			photos = Photo.query(ancestor=rkey)
			n = 0.0
			avg_rating = 0
			for p in photos:
				if p.rating:
					n = n + p.rating
			if photos.count() > 0:
				avg_rating = n / (photos.count())
			q.averageRating = avg_rating
			q.put()
			self.redirect('/browse/%s/%s/%s' % (city, rest, dish))
		except:
			#this is when there is no rating. Need to implement some verification here
			self.redirect('/uploadPhotoPage/%s/%s/%s' % (city, rest, dish))
			

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
	

	###### ADMIN#####
	('/admin', admin),
	('/addAllCities', addAllCities),
	('/clearDatabase', clearDatabase),

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