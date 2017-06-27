from django.conf.urls import include, url
from .views import SSCrowdBotView
urlpatterns = [
url(r'^fe7ab42bf9d6ffc453130fe6ffa3598987dadeaa04d05c8a91/?$', SSCrowdBotView.as_view())
]


