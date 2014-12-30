####THINGS TO DO#####

#. change it so we don't have duplicate functions
#. stop double submit when you upload a photo
#. Add sort filter to restaurant and dish pages
#. parse any entered text to protect against XSS


import cgi
import urllib
import json
import urllib2
import urlparse
import webapp2
import logging
import time
import webapp2_extras.appengine.auth.models

from google.appengine.ext import ndb
from google.appengine.api import mail
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app

from webapp2_extras import auth
from webapp2_extras import sessions
from webapp2_extras import security
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError


###################################
####### USER AUTHENTICATION #######
###################################

PASSWORD_RESET_EMAIL = """
%s,
Your password can be reset by clicking the following link:

%s

Thanks,
The WikiEats Team
"""

ACCOUNT_CONFIRM = """
%s,
Please confirm your account by clicking the following link:

%s

Thanks,
The WikiEats Team
"""

SIGNUP_TEMPLATE = """
	<div class="input_form">
		<h1>Register</h1>
		<form action="/signup" method="POST">
			<input type="text" name="username" placeholder="Username" required/>
			<input type="text" name="email" placeholder="Email address" required/>
			<input type="password" name="password" placeholder="Password" required/>
			<input type="submit" value="Register" />
		</form>
	</div>
"""

LOGIN_TEMPLATE = """
		<form action="/login" method="POST">
			<input type="text" value="%s" name="username" placeholder="Username"/>
			<input type="password" name="password" placeholder="Password"/>
			<input type="submit" value="Login" />
		</form> 
		<ul>
			<li><a href="/forgot">Forgotten your password?</a></li>
			<li><a href="/signup" id="register">Register</a></li>
		</ul>
	</div> 
"""

RESET_PASSWORD_TEMPLATE = """
	<div class="input_form">
		<h1>Reset password</h1>
		<form action="/password" method="post">
			<input type="password" name="password" placeholder="New Password"/>
			<input type="password" name="confirm_password" placeholder="Confirm Password"/>
			<input type="hidden" name="t" value="%s" />
			<input type="submit" value="Update Password" />
		</form>
	</div>
"""

FORGOT_TEMPLATE = """
	<form class="form" action= "/forgot" method="POST">
		<input type="text" value="%s" name="username" placeholder="Username"/>
		<input type="submit" value="Send password reset link"/>
	</form>
"""

class User(webapp2_extras.appengine.auth.models.User):
	def set_password(self, raw_password):
		self.password = security.generate_password_hash(raw_password, length=12)

	@classmethod
	def get_by_auth_token(cls, user_id, token, subject='auth'):
		token_key = cls.token_model.get_key(user_id, subject, token)
		user_key = ndb.Key(cls, user_id)
		# Use get_multi() to save a RPC call.
		valid_token, user = ndb.get_multi([token_key, user_key])
		if valid_token and user:
			timestamp = int(time.mktime(valid_token.created.timetuple()))
			return user, timestamp

		return None, None

def user_required(handler):
  """
    Decorator that checks if there's a user associated with the current session.
    Will also fail if there's no session present.
  """
  def check_login(self, *args, **kwargs):
    auth = self.auth
    if not auth.get_user_by_session():
      self.redirect('/login', abort=True)
    else:
      return handler(self, *args, **kwargs)

  return check_login

class BaseHandler(webapp2.RequestHandler):
  @webapp2.cached_property
  def auth(self):
    """Shortcut to access the auth instance as a property."""
    return auth.get_auth()

  @webapp2.cached_property
  def user_info(self):
    """Shortcut to access a subset of the user attributes that are stored
    in the session.

    The list of attributes to store in the session is specified in
      config['webapp2_extras.auth']['user_attributes'].
    :returns
      A dictionary with most user information
    """
    return self.auth.get_user_by_session()

  @webapp2.cached_property
  def user(self):
    """Shortcut to access the current logged in user.

    Unlike user_info, it fetches information from the persistence layer and
    returns an instance of the underlying model.

    :returns
      The instance of the user model associated to the logged in user.
    """
    u = self.user_info
    return self.user_model.get_by_id(u['user_id']) if u else None

  @webapp2.cached_property
  def user_model(self):
    """Returns the implementation of the user model.

    It is consistent with config['webapp2_extras.auth']['user_model'], if set.
    """    
    return self.auth.store.user_model

  @webapp2.cached_property
  def session(self):
      """Shortcut to access the current session."""
      return self.session_store.get_session(backend="datastore")
      
      
  def display_message(self, message):
    """Utility function to display a template with a simple message."""
    self.response.write(message)

  # this is needed for webapp2 sessions to work
  def dispatch(self):
      # Get a session store for this request.
      self.session_store = sessions.get_store(request=self.request)

      try:
          # Dispatch the request.
          webapp2.RequestHandler.dispatch(self)
      finally:
          # Save all sessions.
          self.session_store.save_sessions(self.response)

class MainHandler(BaseHandler):
  def get(self):
    user = self.auth.get_user_by_session()
    self.response.write('<ul>')
    if user:
      self.response.write('<a href="/logout">Logout</a>')
    else:
      self.response.write('<li><a href="/signup">Register</a></li><li><a href="/login">Login</a></li>')
    self.response.write('<li><a href="/authenticated">Authenticated</a></li></ul>')

class SignupHandler(BaseHandler):
  def get(self):
    active = "register"
    writeNav(self, active)
    self.response.write(SIGNUP_TEMPLATE)
    self.response.write(FOOTER_TEMPLATE)
    
  def post(self):
    user_name = self.request.get('username')
    email = self.request.get('email')
    password = self.request.get('password')

    unique_properties = ['email_address']
    user_data = self.user_model.create_user(user_name,
      unique_properties,
      email_address=email, name=user_name, password_raw=password,
      verified=False)
    if not user_data[0]: #user_data is a tuple
      self.display_message('Unable to create user for email %s because of \
        duplicate keys %s' % (user_name, user_data[1]))
      return
    
    user = user_data[1]
    user_id = user.get_id()

    token = self.user_model.create_signup_token(user_id)

    verification_url = self.uri_for('verification', type='v', user_id=user_id,
      signup_token=token, _full=True)
	  
    mail.send_mail(sender="WikiEats Support <support@wikieats.com>",to = user.email_address,subject="WikiEats Account Confirmation",body = ACCOUNT_CONFIRM % (user.name,verification_url))

    msg = 'Send an email to user in order to verify their address. \
          They will be able to do so by visiting <a href="{url}">{url}</a>'

    self.display_message(msg.format(url=verification_url))

class ForgotPasswordHandler(BaseHandler):
  def get(self):
    self._serve_page()

  def post(self):
    username = self.request.get('username')

    user = self.user_model.get_by_auth_id(username)
    if not user:
      logging.info('Could not find any user entry for username %s', username)
      self._serve_page(not_found=True)
      return

    user_id = user.get_id()
    token = self.user_model.create_signup_token(user_id)

    verification_url = self.uri_for('verification', type='p', user_id=user_id,
      signup_token=token, _full=True)

    mail.send_mail(sender="WikiEats Support <support@wikieats.com>",to = user.email_address,subject="WikiEats Password Reset",body = PASSWORD_RESET_EMAIL % (user.name,verification_url))
	
    msg = 'Send an email to user in order to reset their password. \
          They will be able to do so by visiting <a href="{url}">{url}</a>'

    self.display_message(msg.format(url=verification_url))
  
  def _serve_page(self, not_found=False):
    username = self.request.get('username')
    active = "forgot"
    writeNav(self, active)
    self.response.write('<div class="input_form"><h1>Recover password</h1><p>Forgot your password? Click the link below to receive a link to recover your password.</p>')
    if not_found:
	  self.response.write('<strong>Not found!</strong> We could not found any user with the given username.')
    self.response.write(FORGOT_TEMPLATE % username)
    self.response.write('</div>')
    self.response.write(FOOTER_TEMPLATE)


class VerificationHandler(BaseHandler):
  def get(self, *args, **kwargs):
    user = None
    user_id = kwargs['user_id']
    signup_token = kwargs['signup_token']
    verification_type = kwargs['type']

    # it should be something more concise like
    # self.auth.get_user_by_token(user_id, signup_token)
    # unfortunately the auth interface does not (yet) allow to manipulate
    # signup tokens concisely
    user, ts = self.user_model.get_by_auth_token(int(user_id), signup_token,
      'signup')

    if not user:
      logging.info('Could not find any user with id "%s" signup token "%s"',
        user_id, signup_token)
      self.abort(404)
    
    # store user data in the session
    self.auth.set_session(self.auth.store.user_to_dict(user), remember=True)

    if verification_type == 'v':
      # remove signup token, we don't want users to come back with an old link
      self.user_model.delete_signup_token(user.get_id(), signup_token)

      if not user.verified:
        user.verified = True
        user.put()

      self.display_message('User email address has been verified.')
      return
    elif verification_type == 'p':
      # supply user to the page
      active = "verify"
      writeNav(self, active)
      self.response.write(RESET_PASSWORD_TEMPLATE %(signup_token))
      self.response.write(FOOTER_TEMPLATE)
    else:
      logging.info('verification type not supported')
      self.abort(404)

class SetPasswordHandler(BaseHandler):
  @user_required
  def post(self):
    password = self.request.get('password')
    old_token = self.request.get('t')

    if not password or password != self.request.get('confirm_password'):
      self.display_message('passwords do not match')
      return

    user = self.user
    user.set_password(password)
    user.put()

    # remove signup token, we don't want users to come back with an old link
    self.user_model.delete_signup_token(user.get_id(), old_token)
    
    self.display_message('Password updated')

class LoginHandler(BaseHandler):
  def get(self):
    self._serve_page()

  def post(self):
    username = self.request.get('username')
    password = self.request.get('password')
    try:
      u = self.auth.get_user_by_password(username, password, remember=True,
        save_session=True)
      self.redirect('/')
    except (InvalidAuthIdError, InvalidPasswordError) as e:
      logging.info('Login failed for user %s because of %s', username, type(e))
      self._serve_page(True)

  def _serve_page(self, failed=False):
    username = self.request.get('username')
    active = "login"
    writeNav(self, active)
    self.response.write('<div class="input_form"><h1>Login</h1>')

    if failed:
      self.response.write('<p><strong>Login failed!</strong> Check your credentials and try again.</p>')

    self.response.write(LOGIN_TEMPLATE % (username))
    self.response.write(FOOTER_TEMPLATE)

class LogoutHandler(BaseHandler):
  def get(self):
    self.auth.unset_session()
    self.redirect('/')

class AuthenticatedHandler(BaseHandler):
  @user_required
  def get(self):
    self.response.write('<h1>Congratulations %s!</h1><p>If you see this page, it means that you managed to log in successfully.</p>' % self.user.name)

config = {
  'webapp2_extras.auth': {
    'user_model': 'wikieats.User',
    'user_attributes': ['name','email_address']
  },
  'webapp2_extras.sessions': {
    'secret_key': 'YOUR_SECRET_KEY'
  }
}

HEADER_TEMPLATE = """
<html>
	<head>
		<link rel="stylesheet" type="text/css" href="/styles/image_grid.css">
		<link rel="stylesheet" type="text/css" href="/styles/star_rating.css">
		<link rel="stylesheet" type="text/css" href="/styles/navbar.css">
		<link rel="stylesheet" type="text/css" href="/styles/login.css">
		<link rel="stylesheet" type="text/css" href="/styles/list.css">
	</head>
	<body>
		<div style="position:fixed; left:0px; top:0px; height:110px; width:100%; background:#15967E; z-index:100;">
			<div style="padding:5px;">
				<a href="/"><img src="/images/wikieats_logo.png" width="99px" height="99px"></a>
			</div>	
		</div>
"""

FOOTER_TEMPLATE = """
			</div>
			<div style="position:fixed; left:0px; bottom:0px; height:30px; width:100%; background:#15967E; z-index:100; "></div>
		</body>
	</html>
"""

NAV_1 = """
	<div id='cssmenu'>
		<form action="/selectcity" method="post">
			<span class="dropdown">
				<select name="city_link">
					<option value="none" class="noselect">Select City</option>
	"""

NAV_2 = """
				</select>
			</span>
			<span class="dropdown">
			<select name="rest_type"> <option value="all">All Cuisines</option>
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
			</span>
			<input type="submit" value="GO">
		</form>
		
		<ul>
"""

ADD_NEW_RESTAURANT_TEMPLATE = """
	<div class="input_form">
		<h1>Add Restaurant</h1>
		<form action="/postrestaurant2/%s?cuisine=%s" method="POST">
			<input type="text" name="rest_name" placeholder="Restaurant Name" required/>
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
			<input type="text" name="rest_postcode" placeholder="Postcode"/>
			<input type="text" name="rest_phone" placeholder="Phone Number"/>
			<input type="submit" value="Submit" />
		</form>
	</div>
"""

ADD_NEW_DISH_TEMPLATE = """
	<div class="input_form">
		<h1>Add Dish</h1>
		<form action="/postdish2/%s/%s?cuisine=%s" method="POST">
			<input type="text" name="dish_name" placeholder="Name of Dish" required/>
			<input type="text" name="dish_price" placeholder="Price (&pound)"/>
			<input type="submit" value="Submit" />
		</form>
	</div>
"""

ENTER_POSTCODE_TEMPLATE = """
	<form action="/getPostcodeDistance" method="post">
		Postcode1:<div><input name="postcode1" value = "RH2 7BS"></div>
		Postcode2:<div><input name="postcode2" value = "BS6 5DQ"></div>
		</p>
		<div><input type="submit" value="Get Distance"></div>
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


class postcode(webapp2.RequestHandler):
	def get(self):
		self.response.write(HEADER_TEMPLATE)
		self.response.write(ENTER_POSTCODE_TEMPLATE)
		self.response.write(FOOTER_TEMPLATE)


class getPostcodeDistance(webapp2.RequestHandler):
	def post(self):
		post1 = urllib.quote_plus(self.request.get('postcode1'))
		post2 = urllib.quote_plus(self.request.get('postcode2'))
		data = json.load(urllib2.urlopen('http://maps.googleapis.com/maps/api/distancematrix/json?origins='+post1+'&destinations='+post2+'&mode=driving&language=en-EN&sensor=false"'))
		self.response.write(HEADER_TEMPLATE)
		if(data["rows"][0]["elements"][0]["status"] == 'OK'):
		#self.response.write(data)
			self.response.write(data["rows"][0]["elements"][0]["distance"]["value"] * 0.000621371)
		else:
			self.response.write('invalid postcode')
		self.response.write(FOOTER_TEMPLATE)



#####################################
########## DATABASE MODELS ##########
#####################################
class City(ndb.Model):
    city = ndb.StringProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)

class Restaurant(ndb.Model):
	name = ndb.StringProperty(required=True)
	cuisine = ndb.StringProperty(required=True)
	postcode = ndb.StringProperty(required=True)
	phone = ndb.StringProperty(required=False)
	created = ndb.DateTimeProperty(auto_now_add=True)

class Dish(ndb.Model):
	name = ndb.StringProperty(required=True)
	price = ndb.StringProperty(required=True)
	averageRating = ndb.FloatProperty(required=True)
	numberOfPhotos = ndb.IntegerProperty(required=True)

class Photo(ndb.Model):
    rating = ndb.IntegerProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add = True)
    review = ndb.StringProperty(required=False)
    blob_key = ndb.BlobKeyProperty(required=False)

######################################
############# FUNCTIONS ##############
######################################

def starRating(self, rating):
	if rating == 1:
		self.response.write('<img src="/images/1_star.png" style="display:inline;" height="40px" width="200px">')
	elif  rating == 1.5:
		self.response.write('<img src="/images/1-5_star.png" style="display:inline;" height="40px" width="200px">')
	elif  rating == 2:
		self.response.write('<img src="/images/2_star.png" style="display:inline;" height="40px" width="200px">')
	elif  rating == 2.5:
		self.response.write('<img src="/images/2-5_star.png" style="display:inline;" height="40px" width="200px">')
	elif  rating == 3:
		self.response.write('<img src="/images/3_star.png" style="display:inline;" height="40px" width="200px">')
	elif  rating == 3.5:
		self.response.write('<img src="/images/3-5_star.png" style="display:inline;" height="40px" width="200px">')
	elif  rating == 4:
		self.response.write('<img src="/images/4_star.png" style="display:inline;" height="40px" width="200px">')
	elif  rating == 4.5:
		self.response.write('<img src="/images/4-5_star.png" style="display:inline;" height="40px" width="200px">')
	elif  rating == 5:
		self.response.write('<img src="/images/5_star.png" style="display:inline;" height="40px" width="200px">')



def writeNav(self, active):
		self.response.write(HEADER_TEMPLATE)
		self.response.write(NAV_1)
		cities = City.query().order(City.city)
		for c in cities:
			#self.response.write('<a href="/browse/%s">%s</a></p>' % (c.key.id(),c.city))
			self.response.write('<option value="%s">%s</option>' % (c.key.id(), c.city))
		self.response.write(NAV_2)
		
		u = self.auth.get_user_by_session()
		if u:
			greeting = ('<li class="last"><a href="/logout"><span>Logout</span></a></li>')
		elif active == "login":
			greeting = ('<li class="active"><a href="/login"><span>Sign In</span></a></li><li class="last"><a href="/signup"><span>Register</span></a></li>')
		elif active == "register":
			greeting = ('<li><a href="/login"><span>Sign In</span></a></li><li class="active last"><a href="/signup"><span>Register</span></a></li>')
		else:
			greeting = ('<li><a href="/login"><span>Sign In</span></a></li><li class="last"><a href="/signup"><span>Register</span></a></li>')
		self.response.write(greeting)
		
		self.response.write('</ul></div>')
		
		self.response.write('<div style="position:relative; top:175px; margin-bottom:50px;">')

		
##############################
########## BROWSING ##########
##############################		
class BrowseCities(BaseHandler):
	def get(self):
		active = "browse"
		writeNav(self, active)
		self.response.write('DISPLAY MOST RECENT UPLOADS???')
		self.response.write(FOOTER_TEMPLATE)


class SelectCity(webapp2.RequestHandler):
    def post(self):
		city_link = self.request.get('city_link')
		cuisine = self.request.get('rest_type')
		if(city_link == "none"):
			self.redirect('/browse')
		else:
			self.redirect('/browse/%s?cuisine=%s' % (city_link, cuisine))
		
class BrowseRestaurants(BaseHandler):
	def get(self, city):
		cuisine = self.request.get('cuisine')
		sorted = self.request.get('order')
		#parsed = urlparse.urlparse(url) 
		#print urlparse.parse_qs(parsed.query)['param']
		city_key = ndb.Key('City', int(city))
		if sorted == "zyx":
			result = Restaurant.query(ancestor = city_key).order(-Restaurant.name)
		else:
			result = Restaurant.query(ancestor = city_key).order(Restaurant.name)
		check = False
		active = "browse"
		writeNav(self, active)
		self.response.write('<div class="liststatus">Showing ' + cuisine + " restaurants in " + city_key.get().city + ':')
		self.response.write('<form action="/browse/%s" method="GET" class="sortorder"><select name="order" onchange="this.form.submit()">'% (city))
		
		self.response.write('<option value="abc"')
		if sorted == "abc":
			self.response.write('selected')
		self.response.write('>Alphabetical (A-Z)</option>')
		
		
		self.response.write('<option value="zyx"')
		if sorted == "zyx":
			self.response.write('selected')
		self.response.write('>Alphabetical (Z-A)</option>')
		
		self.response.write('<input type="hidden" value="%s" name="cuisine"' % (cuisine))
		self.response.write('</select></div><div class="listdisplay">')
		for r in result:
			if(r.cuisine == cuisine or cuisine == 'all'):
				check = True
				self.response.write('<a href="/browse/%s/%s?cuisine=%s">%s</a>' % (city, r.key.id(), cuisine, r.name))
			
		if check == False:
			self.response.write('<p class="noitems">No restaurants in this city.</p>')
		
		self.response.write('</div>')
		
		u = self.auth.get_user_by_session()
		if u:
			self.response.write('<a href="/addnewrestaurant/%s?cuisine=%s"><input class="addtolist" type="submit" value="ADD NEW RESTAURANT"></a></p>' % (city, cuisine))
			
		self.response.write('<a class="backbutton "href="/browse">BACK</a></div>')
		self.response.write(FOOTER_TEMPLATE)
		
class BrowseDishes(BaseHandler):
	def get(self, city, rest):
		cuisine = self.request.get('cuisine')
		sorted = self.request.get('order')
		rest_key = ndb.Key('City', int(city), 'Restaurant', int(rest))
		
		if sorted == "zyx":
			ordering = -Dish.name
		elif sorted == "top":
			ordering = -Dish.averageRating
		elif sorted == "bottom":
			ordering = Dish.averageRating
		elif sorted == "high":
			ordering = -Dish.price
		elif sorted == "low":
			ordering = Dish.price
		else:
			ordering = Dish.name
		
		result = Dish.query(ancestor = rest_key).order(ordering)
		check = False
		active = "browse"
		writeNav(self, active)
  
		self.response.write('<div class="liststatus">Showing meals from the ' + rest_key.get().name + ' menu:')
		self.response.write('<form action="/browse/%s/%s?cuisine=%s" method="GET" class="sortorder"><select name="order" onchange="this.form.submit()">'% (city, rest, cuisine))
		
		self.response.write('<option value="abc"')
		if sorted == "abc":
			self.response.write('selected')
		self.response.write('>Alphabetical (A-Z)</option>')
		
		
		self.response.write('<option value="zyx"')
		if sorted == "zyx":
			self.response.write('selected')
		self.response.write('>Alphabetical (Z-A)</option>')
		
		
		self.response.write('<option value="top"')
		if sorted == "top":
			self.response.write('selected')
		self.response.write('>Rating (High-Low)</option>')
		
		
		self.response.write('<option value="bottom"')
		if sorted == "bottom":
			self.response.write('selected')
		self.response.write('>Rating (Low-High)</option>')
		
		
		self.response.write('<option value="high"')
		if sorted == "high":
			self.response.write('selected')
		self.response.write('>Price (High-Low)</option>')
		
		
		self.response.write('<option value="low"')
		if sorted == "low":
			self.response.write('selected')
		self.response.write('>Price (Low-High)</option>')
		
		self.response.write('<input type="hidden" value="%s" name="cuisine"' % (cuisine))
		self.response.write('</select></form></div><div class="listdisplay">')
		for d in result:
			check = True
			#Here we need to make it display stars instead of the number
			d = Dish.get_by_id(d.key.id(), d.key.parent())
			self.response.write('<a href="/browse/%s/%s/%s?cuisine=%s">%s (&pound%s) <div style="display:inline-block; float:right"><div style="display:table-cell; vertical-align;">' % (city, rest, d.key.id(), cuisine, d.name, d.price))
			
			avg_rating = d.averageRating
			if avg_rating:
				rounded = round(avg_rating* 2) / 2
				starRating(self, rounded)
				
			self.response.write('</div></div></a>')
		if check == False:
			self.response.write('<p class="noitems">No dishes in this restaurant.</p>')
		
		self.response.write('</div>')
		
		u = self.auth.get_user_by_session()
		if u:
			self.response.write('<a  href="/addnewdish/%s/%s?cuisine=%s"><input class="addtolist" type="submit" value="ADD NEW DISH"></a></p>' % (city, rest, cuisine))
		
		self.response.write('<a class="backbutton" href="/browse/%s?cuisine=%s">BACK</a></div>' % (city, cuisine))
		self.response.write(FOOTER_TEMPLATE)
		
class DisplayDish(BaseHandler):
	def get(self, city, rest, dish):
		cuisine = self.request.get('cuisine')
		photo_key = ndb.Key('City', int(city), 'Restaurant', int(rest), 'Dish' , int(dish))
		result = Photo.query(ancestor = photo_key).order(-Photo.created).fetch(10)
		check = False
		active = "display"
		writeNav(self, active)
		d = Dish.get_by_id(photo_key.id(), photo_key.parent())
		self.response.write('<div style="display: inline-block; ">')
		self.response.write('<div style="margin: auto; float: left; display: inline-block; width: 600px;"><p style=" padding-left: 40px; font-size: 40px; font-family: \'Lucida Console\', \'Lucida Sans Typewriter\', monaco, \'Bitstream Vera Sans Mono\', monospace;"><b>%s </b>&pound%s</p></div>' % (d.name, d.price))

		avg_rating = d.averageRating
		if avg_rating:
			rounded = round(avg_rating* 2) / 2
			self.response.write('<div style="float:left; display: inline-block; width: 430px; margin: auto; top: 0; bottom: 0; vertical-align: middle; padding:40px 0px; font-size:13px; font-family:Arial;">')
			starRating(self, rounded)
			self.response.write('(Rating of %.2f based on %d ratings)</div></div>' % (avg_rating,d.numberOfPhotos))
		
		self.response.write('<ul class="rig">')
		for p in result:
			check = True
			blob_info = blobstore.BlobInfo.get(p.blob_key)
			self.response.write('<li><img src="/serve/%s" class="photo"/></br><div style="display: inline-block; "><div style="float:left; width: 100px; "><img src="/images/%s_star.png" style="display:inline;" height="20px" width="100px"></div></div><p>%s</p></li>' % (p.blob_key, p.rating, p.review))
		self.response.write('</ul>')
		
		if check == False:
			self.response.write('<p class="noitems">No photos of this dish.</p>')
		
		
		u = self.auth.get_user_by_session()
		if u:
			self.response.write('<a href="/uploadPhotoPage/%s/%s/%s?cuisine=%s"><input class="addtolist" type="submit" value="Upload"></a></p>' % (city, rest, dish, cuisine))
		
		self.response.write('<a class="backbutton" href="/browse/%s/%s?cuisine=%s">BACK</a></div>' % (city, rest, cuisine))
		self.response.write(FOOTER_TEMPLATE)

#####################################
########## LIST SORT ORDER ##########
#####################################
class AddNewRestaurant(BaseHandler):
	def post(self):
		order = self.request.get('order')
	
	
#########################################
########## ADD WHILST BROWSING ##########
#########################################
class AddNewRestaurant(BaseHandler):
	def get(self, city):
		cuisine = self.request.get('cuisine')
		active = "restaurant"
		writeNav(self, active)
		self.response.out.write(ADD_NEW_RESTAURANT_TEMPLATE % (city, cuisine))
		self.response.write('</p><a href="/browse/%s?cuisine=%s"><< BACK</a>' % (city, cuisine))
		self.response.write('</div>')
		self.response.write(FOOTER_TEMPLATE)
		
class PostRestaurant2(webapp2.RequestHandler):
    def post(self, city):
    	cuisine = self.request.get('cuisine')
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
                    self.redirect('/browse/%s?cuisine=%s' % (city, cuisine))
	


class AddNewDish(BaseHandler):
	def get(self, city, rest):
		cuisine = self.request.get('cuisine')
		active = "dish"
		writeNav(self, active)
		self.response.out.write(ADD_NEW_DISH_TEMPLATE % (city, rest, cuisine))
		self.response.write('</p><a href="/browse/%s/%s?cuisine=%s"><< BACK</a>' % (city, rest, cuisine))
		self.response.write('</div>')
		self.response.write(FOOTER_TEMPLATE)


class PostDish2(webapp2.RequestHandler):
	def post(self, city, rest):
		cuisine = self.request.get('cuisine')
		rkey = ndb.Key('City', int(city), 'Restaurant', int(rest))
		#this ensures that an adversay cannot inject dishes to restaurants that do not exist in the database
		if rkey.get() == None:
			self.redirect('/browse/%s/%s?cuisine=%s' % (city, rest, cuisine))
		else:
			r = Dish(parent=rkey)
			r.name = self.request.get('dish_name')
			r.price = self.request.get('dish_price')
			r.averageRating = 0.0
			r.numberOfPhotos = 0
			r.put()
			check = False
			while check == False:
				result = Dish.query(ancestor = rkey).filter(Dish.name == r.name)
				for r in result:
					check = True
					self.redirect('/browse/%s/%s?cuisine=%s' % (city, rest,cuisine))

					
##################################
########## PHOTO UPLOAD ##########
##################################
class uploadPhotoPage(BaseHandler):
    def get(self, city, rest, dish):
		cuisine = self.request.get('cuisine')
		upload_url = blobstore.create_upload_url('/upload/%s/%s/%s?cuisine=%s' % (city, rest, dish, cuisine))
		active = "upload"
		writeNav(self, active)
		self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
		self.response.out.write("""
				<div class="input_form">
					<h1>Upload Photo</h1>
					<form action="/postdish2/%s/%s?cuisine=%s" method="POST">
						<input type="file" name="file" placeholder="Browse..." required/>
						<textarea name="review" rows="3" cols="60" placeholder="Write a Review"></textarea>
									
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
					</form>
				</div>

                 
            """)
		self.response.write('</p><a href="/browse/%s/%s/%s?cuisine=%s"><< BACK</a>' % (city, rest, dish, cuisine))
		self.response.write('</div>')
		self.response.write(FOOTER_TEMPLATE)



class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, city, rest, dish):
		try:
		# 'file' is file upload field in the form
			cuisine = self.request.get('cuisine')
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
			numberOfPhotos = 0
			n = 0.0
			avg_rating = 0
			for p in photos:
				if p.rating:
					numberOfPhotos += 1
					n = n + p.rating
			if photos.count() > 0:
				avg_rating = n / (photos.count())
			q.averageRating = avg_rating
			q.numberOfPhotos = numberOfPhotos
			q.put()
			self.redirect('/browse/%s/%s/%s?cuisine=%s' % (city, rest, dish, cuisine))
		except:
			#this is when there is no rating. Need to implement some verification here
			self.redirect('/uploadPhotoPage/%s/%s/%s?cuisine=%s' % (city, rest, dish, cuisine))
			

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
	def get(self, resource):
		resource = str(urllib.unquote(resource))
		blob_info = blobstore.BlobInfo.get(resource)
		self.send_blob(blob_info)
		

application = webapp2.WSGIApplication([

	('/', BrowseCities),
	###### ADMIN#####
	('/admin', admin),
	('/addAllCities', addAllCities),
	('/clearDatabase', clearDatabase),
	('/postcode', postcode),
	('/getPostcodeDistance', getPostcodeDistance),

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
	
	
	##### USER AUTHENTICATION #####
    ('/signup', SignupHandler),
    webapp2.Route('/<type:v|p>/<user_id:\d+>-<signup_token:.+>',handler=VerificationHandler, name='verification'),
    ('/password', SetPasswordHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/forgot', ForgotPasswordHandler),
    ('/authenticated', AuthenticatedHandler),
	
    
	##### IMAGE UPLOAD AND SERVING #####
	('/uploadPhotoPage/([^/]+)?/([^/]+)?/([^/]+)?', uploadPhotoPage),
	('/upload/([^/]+)?/([^/]+)?/([^/]+)?', UploadHandler),
    ('/serve/([^/]+)?', ServeHandler),
	
], debug=True, config=config)

logging.getLogger().setLevel(logging.DEBUG)