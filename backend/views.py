from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from rest_framework import status, renderers
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.authtoken import views as auth_views
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.models import Token

from serializers import *
from models import Food, Message, Preference
from permissions import IsOwnerOrReadOnly

##########################################################
#                      HEADER CONTROL                    #
##########################################################


def _acao_response(response):
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET'


def _options_allow_access():
    response = HttpResponse()
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, PUT, POST, DELETE, OPTIONS'
    response['Access-Control-Max-Age'] = 1000
    # note that '*' is not valid for Access-Control-Allow-Headers
    response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, ' \
                                               'X-Requested-With, origin, x-csrftoken, ' \
                                               'content-type, accept'
    return response


#########################################################
#               AUTHENTICATION METHOD                   #
#########################################################

# Takes the place of the login mechanism
# Extends parent class to produce token cookies
class ObtainAuthToken(auth_views.ObtainAuthToken):
    parser_classes = (FormParser, MultiPartParser, JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def options(self, request, *args, **kwargs):
        return _options_allow_access()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        response = JSONResponse({'token': token.key})
        _acao_response(response)
        response.set_cookie('auth-token', token.key)
        return response

obtain_auth_token = ObtainAuthToken.as_view()


#########################################################
#                USER-RELATED QUERIES                   #
#########################################################


@csrf_exempt
@api_view(['GET', 'OPTIONS', 'POST'])
# Create user through POST request
def createUser(request):
    if request.method == 'OPTIONS':
        return _options_allow_access()
    elif request.method == 'POST':
        serializer = UserCreationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = JSONResponse({'username': serializer.data['username'], 'email': serializer.data['email']},
                                    status=status.HTTP_201_CREATED)
            _acao_response(response)
            return response
        response = JSONResponse({'error': 'information given invalid'}, status=status.HTTP_400_BAD_REQUEST)
        _acao_response(response)
        return response
    response = HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    _acao_response(response)
    return response


# Gets the username from the URL as a param
def findUser(request, username):
    # Get particular user from db based on param
    # Returns username and email
    try:
        user = User.objects.get(username=username)
        serializer = UserSerializer(user)
        response = JSONResponse(serializer.data)
        _acao_response(response)
        return response
    except User.DoesNotExist:
        response = JSONResponse({'error': 'user does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        _acao_response(response)
        return response


@csrf_exempt
def historyHandler(request):
    if request.method == 'OPTIONS':
        return _options_allow_access()
    else:
        return getHistory(request)


@csrf_exempt
@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def getHistory(request):
    user = request.user
    if user.is_authenticated():
        foodHistory = Food.objects.filter(user=user.id)
        serializer = FoodListSerializer(foodHistory, many=True)
        response = JSONResponse(serializer.data)
        _acao_response(response)
        return response
    response = JSONResponse({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    _acao_response(response)
    return response


@csrf_exempt
def profileHandler(request):
    if request.method == 'OPTIONS':
        return _options_allow_access()
    else:
        return getProfile(request)


@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def getProfile(request):
    user = request.user
    if not user.is_authenticated():
        response = JSONResponse({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        _acao_response(response)
        return response

    if request.method == 'GET':
        serializer = UserSerializer(user)
        response = JSONResponse(serializer.data)
        _acao_response(response)
        return response

    if request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = JSONResponse(serializer.data, status=status.HTTP_202_ACCEPTED)
            _acao_response(response)
            return response
        response = JSONResponse({'error': 'invalid information provided'}, status=status.HTTP_400_BAD_REQUEST)
        _acao_response(response)
        return response

    elif request.method == 'DELETE':
        user.delete()
        response = HttpResponse(status=status.HTTP_204_NO_CONTENT)
        _acao_response(response)
        return response


@csrf_exempt
def preferenceHandler(request):
    if request.method == 'OPTIONS':
        return _options_allow_access()
    else:
        return getPreferences(request)


@csrf_exempt
@api_view(['GET', 'POST', 'DELETE'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def getPreferences(request):
    user = request.user
    if not user.is_authenticated():
        response = JSONResponse({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        _acao_response(response)
        return response

    if request.method == 'GET':
        preferences = Preference.objects.filter(preference_user=user.id)
        serializer = PreferenceSerializer(preferences, many=True)
        response = JSONResponse(serializer.data)
        _acao_response(response)
        return response

    elif request.method == 'POST':
        serializer = PreferenceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(preference_user=user)
            response = JSONResponse(serializer.data, status=status.HTTP_201_CREATED)
            _acao_response(response)
            return response
        response = JSONResponse(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        _acao_response(response)
        return response

    elif request.method == 'DELETE':
        data = JSONParser().parse(request)
        try:
            preference = Preference.objects.get(preference_user=user, preference=data['preference'])
            preference.delete()
            response = HttpResponse(status=status.HTTP_204_NO_CONTENT)
            _acao_response(response)
            return response
        except Preference.DoesNotExist:
            response = HttpResponse(status=status.HTTP_400_BAD_REQUEST)
            _acao_response(response)
            return response


def identify(request, user_id):
    try:
        user=User.objects.get(id=user_id)
        serializer = UserSerializer(user)
        response = JSONResponse(serializer.data)
        _acao_response(response)
        return response
    except:
        response = HttpResponse('User not found')
        _acao_response(response)
        return response


#########################################################
#                FOOD-RELATED QUERIES                   #
#########################################################


@csrf_exempt
def foodListHandler(request, latitude, longitude):
    """
    Deals with incoming OPTIONS for FOODLIST functions
    """
    if request.method == 'OPTIONS':
        return _options_allow_access()
    else:
        return foodList(request, latitude, longitude)


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def foodList(request, latitude, longitude):
    latitude = float(latitude)
    longitude = float(longitude)

    if request.method == 'GET':
        allFoods = Food.objects.filter(Q(latitude__range=(latitude - 0.1, latitude + 0.1)),
                                       Q(longitude__range=(longitude - 0.1, longitude + 0.1)))
        serializer = FoodListSerializer(allFoods, many=True)
        response = JSONResponse(serializer.data)
        _acao_response(response)
        return response

    elif request.method == 'POST':
        if request.user.is_authenticated():
            username = request.user.username
            currentUser = User.objects.get(username=username)
            data = JSONParser().parse(request)
            serializer = FoodListSerializer(data=data, partial=True)
            if serializer.is_valid():
                serializer.save(user=currentUser)
                response = JSONResponse(serializer.data, status=status.HTTP_201_CREATED)
                _acao_response(response)
                return response
            response = JSONResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            _acao_response(response)
            return response
        response = JSONResponse({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        _acao_response(response)
        return response

    else:
        response = HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        _acao_response(response)
        return response


# UNUSED FUNCTION: Searching is handled in the front-end
# Searches based on keyword, food_type, and location
def search(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        try:
            searchItems = Food.objects.filter(Q(food_name__icontains=data['keyword']) |
                                              Q(food_type__exact=data['food_type']) |
                                              (Q(latitude__range=(data['latitude'] - 10, data['latitude'] + 10)),
                                               Q(longitude__range=(data['longitude'] - 10, data['longitude'] + 10))))
            serializer = FoodListSerializer(searchItems, many=True)
            response = JSONResponse(serializer.data)
            _acao_response(response)
            return response
        except Food.DoesNotExist:
            response = JSONResponse({'error': 'food not found'}, status=status.HTTP_400_BAD_REQUEST)
            _acao_response(response)
            return response
    else:
        response = HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        _acao_response(response)
        return response


@csrf_exempt
def updateHandler(request, id):
    """
    Deals with incoming OPTIONS for UPDATE functions
    """
    if request.method == 'OPTIONS':
        return _options_allow_access()
    else:
        return update(request, id)


@csrf_exempt
@api_view(['PUT', 'DELETE'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def update(request, id):
    try:
        foodItem = Food.objects.get(id=id)
        authorized = IsOwnerOrReadOnly().has_object_permission(request, foodItem)
        if not authorized:
            response = JSONResponse({'error': 'not authorized'}, status=status.HTTP_401_UNAUTHORIZED)
            _acao_response(response)
            return response

    except Food.DoesNotExist:
        response = JSONResponse({'error': 'food does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        _acao_response(response)
        return response

    if request.method == 'PUT':
        if request.user.is_authenticated():
            serializer = FoodListSerializer(foodItem, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                response = JSONResponse(serializer.data, status=status.HTTP_202_ACCEPTED)
                _acao_response(response)
                return response
            response = JSONResponse({'error': 'invalid information provided'}, status=status.HTTP_400_BAD_REQUEST)
            _acao_response(response)
            return response

    elif request.method == 'DELETE':
        if request.user.is_authenticated():
            foodItem.delete()
            response = HttpResponse(status=status.HTTP_204_NO_CONTENT)
            _acao_response(response)
            return response

    else:
        response = HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        _acao_response(response)
        return response


#########################################################
#               MESSAGE-RELATED QUERIES                 #
#########################################################


# Returns number of unread messages
def unreadMessages(request, username):
    try:
        unreadMessages = Message.objects.filter(receiver=username, read=False).count()
        serialized = JSONRenderer().render(unreadMessages)
        response = JSONResponse(serialized)
        _acao_response(response)
        return response
    except:
        return HttpResponse('User not found')


# Gets all the messages for current user and returns it
def getMessages(request, username):
    try:
        user = User.objects.filter(username=username)
        uID = user[0].id
        messageList = Message.objects.filter(Q(receiver_id=uID) | Q(sender_id=uID))
        serializer = MessageSerializer(messageList, many=True)
        response = JSONResponse(serializer.data)
        _acao_response(response)
        return response
    except Message.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    except IndexError:
        response = HttpResponse('User not found')
        _acao_response(response)
        return response


@csrf_exempt
def getMessagesBetween(request):
    try:
        if request.method == "POST":
            data= request.POST
            userA=data['userA']
            userB = data['userB']
            print userA,userB
            messageList = Message.objects.filter((Q(receiver_id=userA) & Q(sender_id=userB)) | (Q(receiver_id=userB) & Q(sender_id=userA)))
            serializer = MessageSerializer(messageList, many=True)
            response = JSONResponse(serializer.data)
            response['Access-Control-Allow-Origin'] = '*'
            return response
        else:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    except Message.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)


def getContacts(request, username):
    try:
        user=User.objects.filter(username=username)
        uID=user[0].id
        messageList = Message.objects.filter(Q(receiver_id=uID) | Q(sender_id=uID))
        contacts={}
        contactList=[]
        counter=0
        for x in messageList:
            if x.receiver_id==uID:
                if not x.sender_id in contactList:
                    contactList.append(x.sender_id)
                    contacts[counter] = (x.sender_id)
                    counter=counter+1
            elif x.sender_id==uID:
                if not x.receiver_id in contactList:
                    contactList.append(x.receiver_id)
                    contacts[counter] = (x.receiver_id)
                    counter=counter+1
        response = JSONResponse(contacts)
        _acao_response(response)
        return response
    except Message.DoesNotExist:
        response = HttpResponse(status=status.HTTP_404_NOT_FOUND)
        _acao_response(response)
        return response
    except IndexError:
        response = HttpResponse('User not found')
        _acao_response(response)
        return response

@csrf_exempt
def addMessage(request):
    try:
        if request.method == "POST":#TODO make robust i.e. deal with post request that don't contain thr right data
            data =request.POST
            sender_id=data['sender_id']
            receiver_id = data['receiver_id']
            msg_content=data['msg_content']
            # user=User.objects.filter(username=sender_username)
            # sender_id=user[0].id
            # user=User.objects.filter(username=receiver_username)
            # receiver_id=user[0].id
            message= Message(sender_id=sender_id,receiver_id=receiver_id,msg_content=msg_content)
            response = JSONResponse("{'done:done'}")
            _acao_response(response)
            message.save()
            return response
    except Message.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)


##########################################################
#               DJANGO REST UTILITIES                    #
##########################################################

class JSONResponse(HttpResponse):
    """
    A HttpResponse that renders content into JSON
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)
