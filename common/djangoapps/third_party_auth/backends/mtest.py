from django.conf import settings
from social.backends.oauth import BaseOAuth2


class TestBackend(BaseOAuth2):
    name = 'test'
    ID_KEY = 'user_id'
    AUTHORIZATION_URL = 'https://rnoep.raccoongang.com/oauth2/authorize'
    ACCESS_TOKEN_URL = 'https://rnoep.raccoongang.com/oauth2/token'
    DEFAULT_SCOPE = []
    REDIRECT_STATE = False
    ACCESS_TOKEN_METHOD = 'POST'

    def get_user_details(self, response):
        """ Return user details from MIPT account. """
        email = response.get('email', '')
        firstname = response.get('firstname', '')
        lastname = response.get('lastname', '')
        fullname = ' '.join([firstname, lastname])
        return {'username': email.split('@', 1)[0],
                'email': email,
                'fullname': fullname,
                'first_name': firstname,
                'last_name': lastname}

    def user_data(self, access_token, *args, **kwargs):
        """ Grab user profile information from MIPT. """
        userinfo = self.get_json('https://rnoep.raccoongang.com/api/user/v1/preferences/admin/',
                                 params={'access_token': access_token})
        email = userinfo['email']
        return {
            'user_id': userinfo['id'],
            'username': email.split('@', 1)[0],
            'email': email,
            'firstname': userinfo['name'],
            'lastname': userinfo['surname'],
        }

    def do_auth(self, access_token, *args, **kwargs):
        """Finish the auth process once the access_token was retrieved"""
        data = self.user_data(access_token)
        data['access_token'] = access_token
        kwargs.update({'response': data, 'backend': self})
        return self.strategy.authenticate(*args, **kwargs)

    def get_key_and_secret(self):
        return (
            settings.SOCIAL_AUTH_TEST_OAUTH2_KEY,
            settings.SOCIAL_AUTH_TEST_OAUTH2_SECRET,
        )
