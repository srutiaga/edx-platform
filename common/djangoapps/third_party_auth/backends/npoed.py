import logging

from django.conf import settings
from social.backends.oauth import BaseOAuth2

log = logging.getLogger(__name__)


class NpoedBackend(BaseOAuth2):

    name = 'sso_npoed-oauth2'
    ID_KEY = 'user_id'
    AUTHORIZATION_URL = 'http://sso.rnoep.raccoongang.com/oauth2/authorize'
    ACCESS_TOKEN_URL = 'http://sso.rnoep.raccoongang.com/oauth2/access_token'
    DEFAULT_SCOPE = []
    REDIRECT_STATE = False
    ACCESS_TOKEN_METHOD = 'POST'

    def get_user_details(self, response):
        """ Return user details from MIPT account. """

        log.info(str(response) + "-" * 80)

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
        return self.get_json(
            'http://sso.rnoep.raccoongang.com/oauth2/access_token/%s/' % access_token,
            params={'access_token': access_token}
        )

    def do_auth(self, access_token, *args, **kwargs):
        """Finish the auth process once the access_token was retrieved"""
        data = self.user_data(access_token)
        data['access_token'] = access_token
        kwargs.update(data)
        kwargs.update({'response': data, 'backend': self})
        return self.strategy.authenticate(*args, **kwargs)
