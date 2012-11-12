from django.utils import simplejson

from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (OAuthAdapter,
                                                         OAuthLoginView,
                                                         OAuthCallbackView)
from allauth.socialaccount.models import SocialLogin, SocialAccount
from allauth.utils import get_user_model

from provider import TwitterProvider

User = get_user_model()

class TwitterAPI(OAuth):
    """
    Verifying twitter credentials
    """
    url = 'https://api.twitter.com/1.1/account/verify_credentials.json'

    def get_user_info(self):
        user = simplejson.loads(self.query(self.url))
        return user


class TwitterOAuthAdapter(OAuthAdapter):
    provider_id = TwitterProvider.id
    request_token_url = 'https://api.twitter.com/oauth/request_token'
    access_token_url = 'https://api.twitter.com/oauth/access_token'
    # Issue #42 -- this one authenticates over and over again...
    # authorize_url = 'https://api.twitter.com/oauth/authorize'
    authorize_url = 'https://api.twitter.com/oauth/authenticate'

    def complete_login(self, request, app, token):
        client = TwitterAPI(request, app.key, app.secret,
                            self.request_token_url)
        extra_data = client.get_user_info()
        uid = extra_data['id']
        name = extra_data['name'].split(" ", 1)
        first_name = if len(name) > 0 name[0] else ''
        last_name if len(name) > 1 name[1] else ''
        user = User(username=extra_data['screen_name'], first_name=first_name, last_name=last_name)
        account = SocialAccount(user=user,
                                uid=uid,
                                provider=TwitterProvider.id,
                                extra_data=extra_data)
        return SocialLogin(account)


oauth_login = OAuthLoginView.adapter_view(TwitterOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(TwitterOAuthAdapter)

