import json

from django.core.urlresolvers import reverse
from django.http import HttpResponse

from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.test import APITestCase

# Create your tests here.

##########################################################
#                      HELPER CLASS                      #
##########################################################


class JSONResponse(HttpResponse):
    """
    A HttpResponse that renders content into JSON
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


##########################################################
#                   USER CREATION TEST                   #
##########################################################


class UserTests(APITestCase):
    def setUp(self):
        self.create_data = {"username": "krasus", "password": "krasus", "email": "krasus@wow.com"}

    def test_create_account(self):
        response = self.client.post(reverse('create_user'), json.dumps(self.create_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

